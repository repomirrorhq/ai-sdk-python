"""Agent implementation for multi-step reasoning and tool orchestration."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union, TypeVar, Generic, Callable, Awaitable
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
import asyncio
import logging

from ..providers.base import LanguageModel
from ..providers.types import Message, ToolDefinition, ProviderMetadata
from ..core.generate_text import generate_text, stream_text, GenerateTextResult, StreamTextResult
from ..tools import Tool, ToolRegistry
from ..errors.base import AISDKError

# Type variable for tools
TOOLS = TypeVar('TOOLS')


class StepResult(BaseModel):
    """Result of a single agent step."""
    
    step_number: int = Field(description="The step number")
    messages: List[Message] = Field(description="Messages generated in this step")
    result: Optional[GenerateTextResult] = Field(None, description="Generation result")
    tool_calls: List[Any] = Field(default_factory=list, description="Tool calls made in this step")
    tool_results: List[Any] = Field(default_factory=list, description="Tool results from this step")
    
    class Config:
        arbitrary_types_allowed = True


class PrepareStepResult(BaseModel):
    """Result from a prepare step function."""
    
    model: Optional[LanguageModel] = Field(None, description="Override model for this step")
    tool_choice: Optional[Union[str, Dict[str, Any]]] = Field(None, description="Override tool choice")
    active_tools: Optional[List[str]] = Field(None, description="Limit tools to these names")
    system: Optional[str] = Field(None, description="Override system message")
    messages: Optional[List[Message]] = Field(None, description="Override messages")
    
    class Config:
        arbitrary_types_allowed = True


# Type alias for prepare step function
PrepareStepFunction = Callable[
    [Dict[str, Any]],  # Context with steps, step_number, model, messages
    Union[PrepareStepResult, None, Awaitable[Union[PrepareStepResult, None]]]
]

# Type alias for tool call repair function
ToolCallRepairFunction = Callable[
    [Dict[str, Any]],  # Context with toolCall, tools, error, etc.
    Awaitable[Optional[Dict[str, Any]]]  # Returns repaired tool call or None
]

# Type alias for step finish callback
OnStepFinishCallback = Callable[
    [StepResult],  # Step result
    Union[None, Awaitable[None]]
]


class StopCondition:
    """Condition for stopping agent execution."""
    
    def __init__(self, condition: Callable[[int, List[Message]], bool]):
        self.condition = condition
    
    def __call__(self, step_count: int, messages: List[Message]) -> bool:
        """Check if the stop condition is met."""
        return self.condition(step_count, messages)


def step_count_is(count: int) -> StopCondition:
    """Stop condition based on step count."""
    return StopCondition(lambda step_count, messages: step_count >= count)


def has_tool_call(tool_name: Optional[str] = None) -> StopCondition:
    """Stop condition based on tool call presence."""
    def condition(step_count: int, messages: List[Message]) -> bool:
        if not messages:
            return False
        
        last_message = messages[-1]
        if last_message.role != "assistant":
            return False
            
        if isinstance(last_message.content, list):
            for content in last_message.content:
                if hasattr(content, 'type') and content.type == "tool-call":
                    if tool_name is None or content.tool_name == tool_name:
                        return True
        return False
    
    return StopCondition(condition)


class AgentSettings(BaseModel):
    """Settings for configuring an AI Agent."""
    
    model: LanguageModel = Field(description="The language model to use")
    system: Optional[str] = Field(None, description="System message for the agent")
    tools: Optional[Dict[str, Tool]] = Field(None, description="Available tools for the agent")
    tool_choice: Optional[Union[str, Dict[str, Any]]] = Field("auto", description="Tool choice strategy")
    max_output_tokens: Optional[int] = Field(None, description="Maximum tokens to generate (preferred)")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate (deprecated, use max_output_tokens)")
    temperature: Optional[float] = Field(None, description="Temperature for generation")
    top_p: Optional[float] = Field(None, description="Top-p for nucleus sampling") 
    top_k: Optional[int] = Field(None, description="Top-k for top-k sampling")
    frequency_penalty: Optional[float] = Field(None, description="Frequency penalty")
    presence_penalty: Optional[float] = Field(None, description="Presence penalty")
    stop: Optional[Union[str, List[str]]] = Field(None, description="Stop sequences")
    seed: Optional[int] = Field(None, description="Random seed")
    max_retries: int = Field(2, description="Maximum number of retries")
    headers: Optional[Dict[str, str]] = Field(None, description="Custom headers")
    extra_body: Optional[Dict[str, Any]] = Field(None, description="Extra body parameters")
    
    # Agent-specific settings
    stop_when: Union[StopCondition, List[StopCondition]] = Field(
        default_factory=lambda: step_count_is(1),
        description="Condition(s) for stopping the agent"
    )
    max_steps: int = Field(10, description="Maximum number of steps the agent can take")
    context: Any = Field(None, description="Shared context for tool executions")
    
    # Advanced agent settings
    active_tools: Optional[List[str]] = Field(
        None, 
        description="Limit tools to these names without changing types"
    )
    prepare_step: Optional[PrepareStepFunction] = Field(
        None,
        description="Function to provide different settings for each step"
    )
    tool_call_repair: Optional[ToolCallRepairFunction] = Field(
        None,
        description="Function to repair failed tool calls"
    )
    on_step_finish: Optional[OnStepFinishCallback] = Field(
        None,
        description="Callback called when each step finishes"
    )
    experimental_context: Any = Field(
        None,
        description="Experimental context passed to tool calls"
    )
    
    @property
    def resolved_max_tokens(self) -> Optional[int]:
        """Resolve max_tokens parameter, preferring max_output_tokens."""
        if self.max_output_tokens is not None and self.max_tokens is not None:
            raise ValueError("Cannot specify both max_output_tokens and max_tokens. Use max_output_tokens (preferred).")
        return self.max_output_tokens if self.max_output_tokens is not None else self.max_tokens
    
    class Config:
        arbitrary_types_allowed = True


class Agent:
    """AI Agent for multi-step reasoning and tool orchestration.
    
    The Agent class provides a high-level interface for building AI agents that can:
    - Perform multi-step reasoning with language models
    - Execute tools and process their results
    - Maintain conversation context across multiple interactions
    - Handle complex workflows with stopping conditions
    
    Example:
        ```python
        from ai_sdk import create_openai, tool
        from ai_sdk.agent import Agent
        
        @tool("calculator", "Perform arithmetic")
        def calculator(expression: str) -> float:
            return eval(expression)  # In real use, use a safe evaluator
            
        agent = Agent(
            model=create_openai().chat("gpt-4"),
            tools={"calculator": calculator},
            system="You are a math tutor."
        )
        
        result = await agent.generate("What is 15 * 24 + 7?")
        ```
    """
    
    def __init__(self, **settings: Any):
        """Initialize the agent with the given settings.
        
        Args:
            **settings: Agent configuration settings (see AgentSettings)
        """
        self.settings = AgentSettings(**settings)
        self._tool_registry = ToolRegistry()
        self._logger = logging.getLogger("ai_sdk.agent")
        
        # Register tools if provided
        if self.settings.tools:
            for name, tool in self.settings.tools.items():
                self._tool_registry.register(name, tool)
    
    async def multi_step_generate(
        self,
        prompt: Optional[str] = None,
        *,
        messages: Optional[List[Message]] = None,
        provider_metadata: Optional[ProviderMetadata] = None,
        provider_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Generate a response using multi-step reasoning.
        
        This method implements the full agent loop with tool execution,
        step preparation, and stop conditions. It performs multiple
        generation steps until a stop condition is met.
        
        Args:
            prompt: Text prompt (alternative to messages)
            messages: List of messages for conversation
            provider_metadata: Provider-specific metadata
            provider_options: Provider-specific options
            **kwargs: Additional generation parameters
            
        Returns:
            Dict containing final result, steps, and metadata
        """
        # Initialize conversation
        if messages:
            conversation = list(messages)
        elif prompt:
            conversation = [Message(role="user", content=prompt)]
        else:
            raise ValueError("Either 'prompt' or 'messages' must be provided")
        
        # Add system message if configured
        if self.settings.system:
            conversation.insert(0, Message(role="system", content=self.settings.system))
        
        steps: List[StepResult] = []
        step_number = 0
        
        while step_number < self.settings.max_steps:
            self._logger.debug(f"Starting step {step_number}")
            
            # Prepare step settings
            step_settings = await self._prepare_step(
                steps=steps,
                step_number=step_number,
                messages=conversation,
                **kwargs
            )
            
            # Execute generation step
            try:
                result = await self._execute_step(
                    messages=conversation,
                    step_settings=step_settings,
                    provider_metadata=provider_metadata,
                    provider_options=provider_options,
                    **kwargs
                )
                
                # Create step result
                step_result = StepResult(
                    step_number=step_number,
                    messages=conversation.copy(),
                    result=result,
                    tool_calls=getattr(result, 'tool_calls', []),
                    tool_results=getattr(result, 'tool_results', [])
                )
                
                steps.append(step_result)
                
                # Call step finish callback
                if self.settings.on_step_finish:
                    try:
                        callback_result = self.settings.on_step_finish(step_result)
                        if asyncio.iscoroutine(callback_result):
                            await callback_result
                    except Exception as e:
                        self._logger.warning(f"Step finish callback failed: {e}")
                
                # Check stop conditions
                if self._should_stop(step_number, conversation):
                    break
                
                # Execute tools if present
                if hasattr(result, 'tool_calls') and result.tool_calls:
                    await self._execute_tools(result.tool_calls, conversation)
                
                step_number += 1
                
            except Exception as e:
                self._logger.error(f"Step {step_number} failed: {e}")
                break
        
        return {
            "final_result": steps[-1].result if steps else None,
            "steps": steps,
            "conversation": conversation,
            "total_steps": len(steps)
        }
    
    async def _prepare_step(
        self,
        steps: List[StepResult],
        step_number: int,
        messages: List[Message],
        **kwargs: Any
    ) -> Dict[str, Any]:
        """Prepare settings for a specific step."""
        base_settings = {
            "model": self.settings.model,
            "max_output_tokens": self.settings.resolved_max_tokens,
            "temperature": self.settings.temperature,
            "top_p": self.settings.top_p,
            "top_k": self.settings.top_k,
            "frequency_penalty": self.settings.frequency_penalty,
            "presence_penalty": self.settings.presence_penalty,
            "stop": self.settings.stop,
            "seed": self.settings.seed,
            "max_retries": self.settings.max_retries,
            "headers": self.settings.headers,
            "extra_body": self.settings.extra_body,
            **kwargs
        }
        
        # Apply prepare step function if provided
        if self.settings.prepare_step:
            try:
                context = {
                    "steps": steps,
                    "step_number": step_number,
                    "model": self.settings.model,
                    "messages": messages
                }
                
                step_override = self.settings.prepare_step(context)
                if asyncio.iscoroutine(step_override):
                    step_override = await step_override
                
                if step_override:
                    if step_override.model:
                        base_settings["model"] = step_override.model
                    if step_override.tool_choice is not None:
                        base_settings["tool_choice"] = step_override.tool_choice
                    if step_override.system:
                        base_settings["system"] = step_override.system
                    if step_override.messages:
                        messages[:] = step_override.messages
                    
                    # Handle active_tools filtering
                    if step_override.active_tools and self.settings.tools:
                        filtered_tools = {
                            name: tool for name, tool in self.settings.tools.items()
                            if name in step_override.active_tools
                        }
                        base_settings["active_tools"] = filtered_tools
                        
            except Exception as e:
                self._logger.warning(f"Prepare step function failed: {e}")
        
        return base_settings
    
    async def _execute_step(
        self,
        messages: List[Message],
        step_settings: Dict[str, Any],
        provider_metadata: Optional[ProviderMetadata] = None,
        provider_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> GenerateTextResult:
        """Execute a single generation step."""
        generation_options = {
            **step_settings,
            "messages": messages
        }
        
        # Add tools if available
        tools_to_use = step_settings.get("active_tools", self.settings.tools)
        if tools_to_use:
            tool_definitions = []
            for name, tool in tools_to_use.items():
                tool_definitions.append(ToolDefinition(
                    name=name,
                    description=tool.description,
                    parameters=tool.parameters
                ))
            generation_options["tools"] = tool_definitions
            generation_options["tool_choice"] = step_settings.get("tool_choice", self.settings.tool_choice)
        
        # Add provider options
        if provider_metadata:
            generation_options["provider_metadata"] = provider_metadata
        if provider_options:
            generation_options["provider_options"] = provider_options
        
        return await generate_text(**generation_options)
    
    async def _execute_tools(self, tool_calls: List[Any], conversation: List[Message]) -> None:
        """Execute tool calls and add results to conversation."""
        for tool_call in tool_calls:
            try:
                # Get the tool
                tool_name = tool_call.get("name") or tool_call.get("function", {}).get("name")
                if not tool_name or not self.settings.tools or tool_name not in self.settings.tools:
                    continue
                
                tool = self.settings.tools[tool_name]
                args = tool_call.get("arguments") or tool_call.get("function", {}).get("arguments", {})
                
                # Execute tool with context
                if self.settings.experimental_context:
                    result = await tool.execute(args, context=self.settings.experimental_context)
                else:
                    result = await tool.execute(args)
                
                # Add tool result to conversation
                conversation.append(Message(
                    role="tool",
                    content=str(result),
                    tool_call_id=tool_call.get("id")
                ))
                
            except Exception as e:
                self._logger.error(f"Tool execution failed for {tool_name}: {e}")
                
                # Try tool repair if configured
                if self.settings.tool_call_repair:
                    try:
                        repair_context = {
                            "toolCall": tool_call,
                            "tools": self.settings.tools,
                            "error": e,
                            "system": self.settings.system,
                            "messages": conversation
                        }
                        
                        repaired_call = await self.settings.tool_call_repair(repair_context)
                        if repaired_call:
                            # Retry with repaired call
                            await self._execute_tools([repaired_call], conversation)
                            continue
                    except Exception as repair_error:
                        self._logger.error(f"Tool repair failed: {repair_error}")
                
                # Add error result to conversation
                conversation.append(Message(
                    role="tool",
                    content=f"Error: {str(e)}",
                    tool_call_id=tool_call.get("id")
                ))
    
    def _should_stop(self, step_number: int, messages: List[Message]) -> bool:
        """Check if any stop condition is met."""
        stop_conditions = self.settings.stop_when
        if not isinstance(stop_conditions, list):
            stop_conditions = [stop_conditions]
        
        for condition in stop_conditions:
            if condition(step_number + 1, messages):
                return True
        
        return False
    
    async def generate(
        self,
        prompt: Optional[str] = None,
        *,
        messages: Optional[List[Message]] = None,
        provider_metadata: Optional[ProviderMetadata] = None,
        provider_options: Optional[Dict[str, Any]] = None,
        use_multi_step: bool = True,
        **kwargs: Any
    ) -> GenerateTextResult:
        """Generate a response from the agent.
        
        This method can use either simple generation or multi-step reasoning
        depending on the agent configuration and use_multi_step parameter.
        
        Args:
            prompt: Text prompt (alternative to messages)
            messages: List of messages for conversation
            provider_metadata: Provider-specific metadata
            provider_options: Provider-specific options
            use_multi_step: Whether to use multi-step reasoning (default: True)
            **kwargs: Additional generation parameters
            
        Returns:
            Result containing the agent's response and metadata
        """
        # Use multi-step generation if enabled and tools are available
        if (use_multi_step and 
            (self.settings.tools or 
             self.settings.prepare_step or
             self.settings.tool_call_repair or
             self.settings.max_steps > 1)):
            
            result = await self.multi_step_generate(
                prompt=prompt,
                messages=messages,
                provider_metadata=provider_metadata,
                provider_options=provider_options,
                **kwargs
            )
            return result["final_result"]
        
        # Fall back to simple generation
        return await self._simple_generate(
            prompt=prompt,
            messages=messages,
            provider_metadata=provider_metadata,
            provider_options=provider_options,
            **kwargs
        )
    
    async def _simple_generate(
        self,
        prompt: Optional[str] = None,
        *,
        messages: Optional[List[Message]] = None,
        provider_metadata: Optional[ProviderMetadata] = None,
        provider_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> GenerateTextResult:
        """Simple single-step generation without multi-step reasoning."""
        # Build the full options by combining agent settings and call-specific options
        generation_options = {
            "model": self.settings.model,
            "max_output_tokens": self.settings.resolved_max_tokens,
            "temperature": self.settings.temperature,
            "top_p": self.settings.top_p,
            "top_k": self.settings.top_k,
            "frequency_penalty": self.settings.frequency_penalty,
            "presence_penalty": self.settings.presence_penalty,
            "stop": self.settings.stop,
            "seed": self.settings.seed,
            "max_retries": self.settings.max_retries,
            "headers": self.settings.headers,
            "extra_body": self.settings.extra_body,
            **kwargs
        }
        
        # Add system message if configured
        if self.settings.system:
            if messages:
                messages = [Message(role="system", content=self.settings.system)] + messages
            elif prompt:
                generation_options["system"] = self.settings.system
        
        # Filter tools if active_tools is set
        tools_to_use = self.settings.tools
        if self.settings.active_tools and self.settings.tools:
            tools_to_use = {
                name: tool for name, tool in self.settings.tools.items()
                if name in self.settings.active_tools
            }
        
        # Add tools if available
        if tools_to_use:
            tool_definitions = []
            for name, tool in tools_to_use.items():
                tool_definitions.append(ToolDefinition(
                    name=name,
                    description=tool.description,
                    parameters=tool.parameters
                ))
            generation_options["tools"] = tool_definitions
            generation_options["tool_choice"] = self.settings.tool_choice
        
        # Set prompt or messages
        if messages:
            generation_options["messages"] = messages
        elif prompt:
            generation_options["prompt"] = prompt
        else:
            raise ValueError("Either 'prompt' or 'messages' must be provided")
            
        # Add provider options
        if provider_metadata:
            generation_options["provider_metadata"] = provider_metadata
        if provider_options:
            generation_options["provider_options"] = provider_options
        
        return await generate_text(**generation_options)
    
    def stream(
        self,
        prompt: Optional[str] = None,
        *,
        messages: Optional[List[Message]] = None,
        provider_metadata: Optional[ProviderMetadata] = None,
        provider_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> StreamTextResult:
        """Stream a response from the agent.
        
        Similar to generate() but returns a streaming result for real-time
        response processing.
        
        Args:
            prompt: Text prompt (alternative to messages)
            messages: List of messages for conversation
            provider_metadata: Provider-specific metadata
            provider_options: Provider-specific options
            **kwargs: Additional generation parameters
            
        Returns:
            Streaming result for real-time processing
        """
        # Build the full options (same logic as generate)
        generation_options = {
            "model": self.settings.model,
            "max_output_tokens": self.settings.resolved_max_tokens,
            "temperature": self.settings.temperature,
            "top_p": self.settings.top_p,
            "top_k": self.settings.top_k,
            "frequency_penalty": self.settings.frequency_penalty,
            "presence_penalty": self.settings.presence_penalty,
            "stop": self.settings.stop,
            "seed": self.settings.seed,
            "max_retries": self.settings.max_retries,
            "headers": self.settings.headers,
            "extra_body": self.settings.extra_body,
            **kwargs
        }
        
        # Add system message if configured
        if self.settings.system:
            if messages:
                messages = [Message(role="system", content=self.settings.system)] + messages
            elif prompt:
                generation_options["system"] = self.settings.system
        
        # Add tools if available
        if self.settings.tools:
            tool_definitions = []
            for name, tool in self.settings.tools.items():
                tool_definitions.append(ToolDefinition(
                    name=name,
                    description=tool.description,
                    parameters=tool.parameters
                ))
            generation_options["tools"] = tool_definitions
            generation_options["tool_choice"] = self.settings.tool_choice
        
        # Set prompt or messages
        if messages:
            generation_options["messages"] = messages
        elif prompt:
            generation_options["prompt"] = prompt
        else:
            raise ValueError("Either 'prompt' or 'messages' must be provided")
            
        # Add provider options
        if provider_metadata:
            generation_options["provider_metadata"] = provider_metadata
        if provider_options:
            generation_options["provider_options"] = provider_options
        
        return stream_text(**generation_options)
    
    def add_tool(self, name: str, tool: Tool) -> None:
        """Add a tool to the agent.
        
        Args:
            name: Name of the tool
            tool: Tool implementation
        """
        if self.settings.tools is None:
            self.settings.tools = {}
        self.settings.tools[name] = tool
        self._tool_registry.register(name, tool)
    
    def remove_tool(self, name: str) -> None:
        """Remove a tool from the agent.
        
        Args:
            name: Name of the tool to remove
        """
        if self.settings.tools and name in self.settings.tools:
            del self.settings.tools[name]
            self._tool_registry.unregister(name)
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name.
        
        Args:
            name: Name of the tool
            
        Returns:
            Tool instance or None if not found
        """
        if self.settings.tools:
            return self.settings.tools.get(name)
        return None
    
    def list_tools(self) -> List[str]:
        """Get a list of all available tool names.
        
        Returns:
            List of tool names
        """
        if self.settings.tools:
            return list(self.settings.tools.keys())
        return []
    
    def update_settings(self, **kwargs: Any) -> None:
        """Update agent settings.
        
        Args:
            **kwargs: Settings to update
        """
        for key, value in kwargs.items():
            if hasattr(self.settings, key):
                setattr(self.settings, key, value)
            else:
                raise ValueError(f"Unknown setting: {key}")