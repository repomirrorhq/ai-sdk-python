"""Agent implementation for multi-step reasoning and tool orchestration."""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Union, TypeVar, Generic, Callable, Awaitable
from pydantic import BaseModel, Field

from ..providers.base import LanguageModel
from ..providers.types import Message, ToolDefinition, ProviderMetadata
from ..core.generate_text import generate_text, stream_text, GenerateTextResult, StreamTextResult
from ..tools import Tool, ToolRegistry

# Type variable for tools
TOOLS = TypeVar('TOOLS')


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
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
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
        
        # Register tools if provided
        if self.settings.tools:
            for name, tool in self.settings.tools.items():
                self._tool_registry.register(name, tool)
    
    async def generate(
        self,
        prompt: Optional[str] = None,
        *,
        messages: Optional[List[Message]] = None,
        provider_metadata: Optional[ProviderMetadata] = None,
        provider_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ) -> GenerateTextResult:
        """Generate a response from the agent.
        
        This method combines the agent's settings with the provided prompt/messages
        and executes the generation process, potentially involving multiple steps
        with tool calls.
        
        Args:
            prompt: Text prompt (alternative to messages)
            messages: List of messages for conversation
            provider_metadata: Provider-specific metadata
            provider_options: Provider-specific options
            **kwargs: Additional generation parameters
            
        Returns:
            Result containing the agent's response and metadata
        """
        # Build the full options by combining agent settings and call-specific options
        generation_options = {
            "model": self.settings.model,
            "max_tokens": self.settings.max_tokens,
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
            "max_tokens": self.settings.max_tokens,
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