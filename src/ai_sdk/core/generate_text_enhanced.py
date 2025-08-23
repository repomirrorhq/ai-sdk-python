"""Enhanced text generation with multi-step tool calling support."""

from __future__ import annotations

import asyncio
import uuid
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, Union

from ..errors import InvalidArgumentError
from ..providers.base import LanguageModel
from ..providers.types import (
    Content,
    FinishReason,
    GenerateOptions,
    GenerateResult,
    Message,
    StreamOptions,
    StreamPart,
    ToolDefinition,
    Usage,
)
from ..tools.core import Tool, ToolCall, ToolResult
from .step import (
    GeneratedFile,
    PrepareStepArgs,
    PrepareStepFunction,
    PrepareStepResult,
    StepResult,
    StopCondition,
    is_stop_condition_met,
    step_count_is,
)
from .tool_execution import (
    create_tool_response_messages,
    execute_tools,
    parse_tool_calls_from_content,
)


class EnhancedGenerateTextResult:
    """Enhanced result from text generation with multi-step support."""
    
    def __init__(self, steps: List[StepResult]) -> None:
        """Initialize result with steps.
        
        Args:
            steps: List of generation steps
        """
        self.steps = steps
    
    @property
    def final_step(self) -> StepResult:
        """Get the final step in the generation."""
        return self.steps[-1]
    
    @property
    def content(self) -> List[Content]:
        """Get content from the final step."""
        return self.final_step.content
    
    @property
    def text(self) -> str:
        """Get text from the final step."""
        return self.final_step.text
    
    @property
    def files(self) -> List[GeneratedFile]:
        """Get files from the final step."""
        return self.final_step.files
    
    @property
    def reasoning_text(self) -> Optional[str]:
        """Get reasoning text from the final step."""
        return self.final_step.reasoning_text
    
    @property
    def reasoning(self) -> Optional[List[Dict[str, Any]]]:
        """Get structured reasoning from the final step."""
        return self.final_step.reasoning
    
    @property
    def tool_calls(self) -> List[ToolCall]:
        """Get tool calls from the final step."""
        return self.final_step.tool_calls
    
    @property
    def static_tool_calls(self) -> List[ToolCall]:
        """Get static tool calls from the final step."""
        return self.final_step.static_tool_calls
    
    @property
    def dynamic_tool_calls(self) -> List[ToolCall]:
        """Get dynamic tool calls from the final step."""
        return self.final_step.dynamic_tool_calls
    
    @property
    def tool_results(self) -> List[ToolResult]:
        """Get tool results from the final step."""
        return self.final_step.tool_results
    
    @property
    def static_tool_results(self) -> List[ToolResult]:
        """Get static tool results from the final step."""
        return self.final_step.static_tool_results
    
    @property
    def dynamic_tool_results(self) -> List[ToolResult]:
        """Get dynamic tool results from the final step."""
        return self.final_step.dynamic_tool_results
    
    @property
    def sources(self) -> Optional[List[Dict[str, Any]]]:
        """Get sources from the final step."""
        return self.final_step.sources
    
    @property
    def finish_reason(self) -> FinishReason:
        """Get finish reason from the final step."""
        return self.final_step.finish_reason
    
    @property
    def warnings(self) -> Optional[List[str]]:
        """Get warnings from the final step."""
        return self.final_step.warnings
    
    @property
    def provider_metadata(self) -> Optional[Dict[str, Any]]:
        """Get provider metadata from the final step."""
        return self.final_step.provider_metadata
    
    @property
    def response(self) -> Optional[Dict[str, Any]]:
        """Get response metadata from the final step."""
        return self.final_step.response
    
    @property
    def request(self) -> Optional[Dict[str, Any]]:
        """Get request metadata from the final step."""
        return self.final_step.request
    
    @property
    def usage(self) -> Usage:
        """Get usage from the final step."""
        return self.final_step.usage
    
    @property
    def total_usage(self) -> Usage:
        """Get total usage across all steps."""
        total_input_tokens = 0
        total_output_tokens = 0
        total_total_tokens = 0
        
        for step in self.steps:
            if step.usage.input_tokens:
                total_input_tokens += step.usage.input_tokens
            if step.usage.output_tokens:
                total_output_tokens += step.usage.output_tokens
            if step.usage.total_tokens:
                total_total_tokens += step.usage.total_tokens
        
        return Usage(
            input_tokens=total_input_tokens if total_input_tokens > 0 else None,
            output_tokens=total_output_tokens if total_output_tokens > 0 else None,
            total_tokens=total_total_tokens if total_total_tokens > 0 else None,
        )


async def generate_text_enhanced(
    model: LanguageModel,
    *,
    system: Optional[str] = None,
    prompt: Optional[str] = None,
    messages: Optional[List[Message]] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    top_k: Optional[int] = None,
    frequency_penalty: Optional[float] = None,
    presence_penalty: Optional[float] = None,
    stop: Optional[Union[str, List[str]]] = None,
    seed: Optional[int] = None,
    tools: Optional[Dict[str, Tool]] = None,
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
    active_tools: Optional[List[str]] = None,
    stop_when: Union[StopCondition, List[StopCondition]] = step_count_is(1),
    prepare_step: Optional[PrepareStepFunction] = None,
    repair_tool_call: Optional[Callable] = None,
    context: Optional[Any] = None,
    max_retries: int = 2,
    headers: Optional[Dict[str, str]] = None,
    extra_body: Optional[Dict[str, Any]] = None,
    on_step_finish: Optional[Callable[[StepResult], None]] = None,
) -> EnhancedGenerateTextResult:
    """Generate text with enhanced multi-step tool calling support.
    
    Args:
        model: Language model to use for generation
        system: System message that will be part of the prompt
        prompt: Simple text prompt (mutually exclusive with messages)
        messages: List of messages (mutually exclusive with prompt)
        max_tokens: Maximum number of tokens to generate
        temperature: Temperature setting for randomness (0.0 to 2.0)
        top_p: Nucleus sampling parameter (0.0 to 1.0)
        top_k: Top-k sampling parameter
        frequency_penalty: Frequency penalty (-2.0 to 2.0)
        presence_penalty: Presence penalty (-2.0 to 2.0)
        stop: Stop sequences (string or list of strings)
        seed: Random seed for deterministic output
        tools: Available tools for the model to call
        tool_choice: How the model should choose tools ("auto", "none", or specific tool)
        active_tools: Subset of tools that are available for this generation
        stop_when: Conditions for stopping multi-step generation
        prepare_step: Function to prepare each step dynamically
        repair_tool_call: Function to repair invalid tool calls
        context: Context passed to tool executions
        max_retries: Maximum number of retries on failure
        headers: Additional HTTP headers
        extra_body: Additional request body parameters
        on_step_finish: Callback called after each step completes
        
    Returns:
        EnhancedGenerateTextResult containing all steps and aggregated results
        
    Raises:
        InvalidArgumentError: If arguments are invalid
        APIError: If the API call fails
        NetworkError: If there are network issues
    """
    # Validate arguments
    if prompt is not None and messages is not None:
        raise InvalidArgumentError(
            "Cannot specify both 'prompt' and 'messages'. Use one or the other."
        )
    
    if prompt is None and messages is None:
        raise InvalidArgumentError(
            "Must specify either 'prompt' or 'messages'."
        )
    
    # Build initial messages
    initial_messages = []
    if system:
        initial_messages.append(Message(role="system", content=system))
    
    if prompt:
        initial_messages.append(Message(role="user", content=prompt))
    elif messages:
        initial_messages.extend(messages)
    
    # Convert stop_when to list if needed
    stop_conditions = stop_when if isinstance(stop_when, list) else [stop_when]
    
    # Initialize state
    steps: List[StepResult] = []
    current_messages = initial_messages.copy()
    
    # Multi-step generation loop
    while True:
        step_number = len(steps)
        
        # Prepare step if function provided
        step_args = PrepareStepArgs(
            model=model,
            steps=steps,
            step_number=step_number,
            messages=current_messages
        )
        
        step_config = None
        if prepare_step:
            step_config = await prepare_step(step_args)
        
        # Use step configuration or defaults
        step_model = (step_config.model if step_config and step_config.model else model)
        step_system = (step_config.system if step_config and step_config.system else system)
        step_messages = (step_config.messages if step_config and step_config.messages else current_messages)
        step_tools = (step_config.tools if step_config and step_config.tools else tools)
        step_tool_choice = (step_config.tool_choice if step_config and step_config.tool_choice else tool_choice)
        step_active_tools = (step_config.active_tools if step_config and step_config.active_tools else active_tools)
        
        # Filter tools if active_tools is specified
        if step_tools and step_active_tools:
            filtered_tools = {k: v for k, v in step_tools.items() if k in step_active_tools}
        else:
            filtered_tools = step_tools
        
        # Convert tools to ToolDefinition format for provider
        tool_definitions = None
        if filtered_tools:
            tool_definitions = []
            for tool_name, tool in filtered_tools.items():
                if hasattr(tool, 'definition'):
                    tool_definitions.append(tool.definition)
                else:
                    # Create basic definition
                    tool_definitions.append(ToolDefinition(
                        name=tool_name,
                        description=getattr(tool, 'description', f'Tool: {tool_name}'),
                        parameters=getattr(tool, 'parameters', {})
                    ))
        
        # Build provider options
        provider_options = GenerateOptions(
            messages=step_messages,
            max_tokens=step_config.max_tokens if step_config and step_config.max_tokens else max_tokens,
            temperature=step_config.temperature if step_config and step_config.temperature else temperature,
            top_p=step_config.top_p if step_config and step_config.top_p else top_p,
            top_k=step_config.top_k if step_config and step_config.top_k else top_k,
            frequency_penalty=step_config.frequency_penalty if step_config and step_config.frequency_penalty else frequency_penalty,
            presence_penalty=step_config.presence_penalty if step_config and step_config.presence_penalty else presence_penalty,
            stop=step_config.stop if step_config and step_config.stop else stop,
            seed=step_config.seed if step_config and step_config.seed else seed,
            tools=tool_definitions,
            tool_choice=step_tool_choice,
            headers=headers,
            extra_body=extra_body,
        )
        
        # Call the model
        result = await step_model.generate(provider_options)
        
        # Parse tool calls from the result
        tool_calls = []
        tool_results = []
        
        if filtered_tools and result.content:
            tool_calls = parse_tool_calls_from_content(
                result.content,
                filtered_tools,
                repair_tool_call
            )
            
            # Execute tool calls
            if tool_calls:
                # Filter out invalid tool calls for execution
                valid_tool_calls = [tc for tc in tool_calls if not tc.invalid]
                
                if valid_tool_calls:
                    tool_results = await execute_tools(
                        tool_calls=valid_tool_calls,
                        tools=filtered_tools,
                        messages=step_messages,
                        context=context
                    )
                
                # Add error results for invalid tool calls
                for tc in tool_calls:
                    if tc.invalid:
                        tool_results.append(ToolResult(
                            type="error",
                            tool_call_id=tc.tool_call_id,
                            tool_name=tc.tool_name,
                            input=tc.input,
                            error=str(getattr(tc, 'error', 'Invalid tool call')),
                            dynamic=tc.dynamic
                        ))
        
        # Extract text from content
        text_parts = []
        files = []
        reasoning_parts = []
        sources = []
        
        for content_item in result.content:
            if hasattr(content_item, 'text') and content_item.text:
                text_parts.append(content_item.text)
            elif hasattr(content_item, 'type'):
                if content_item.type == 'file':
                    # Convert to GeneratedFile
                    file = GeneratedFile(
                        name=getattr(content_item, 'name', 'generated_file'),
                        content_type=getattr(content_item, 'content_type', 'application/octet-stream'),
                        content=getattr(content_item, 'content', b''),
                        url=getattr(content_item, 'url', None)
                    )
                    files.append(file)
                elif content_item.type == 'reasoning':
                    reasoning_parts.append(getattr(content_item, 'text', ''))
                elif content_item.type == 'source':
                    sources.append({
                        'type': 'source',
                        'text': getattr(content_item, 'text', ''),
                        'metadata': getattr(content_item, 'metadata', {})
                    })
        
        text = ''.join(text_parts)
        reasoning_text = '\n'.join(reasoning_parts) if reasoning_parts else None
        
        # Create step result
        step_result = StepResult(
            content=result.content,
            text=text,
            finish_reason=result.finish_reason,
            usage=result.usage,
            tool_calls=tool_calls,
            tool_results=tool_results,
            files=files,
            reasoning_text=reasoning_text,
            reasoning=[{'text': reasoning_text}] if reasoning_text else None,
            sources=sources if sources else None,
            warnings=getattr(result, 'warnings', None),
            provider_metadata=result.provider_metadata.data if result.provider_metadata else None,
            request={
                'model': step_model.__class__.__name__,
                'messages': step_messages,
                'tools': list(filtered_tools.keys()) if filtered_tools else None,
                'tool_choice': step_tool_choice,
            },
            response={
                'id': str(uuid.uuid4()),  # Generate response ID
                'model': getattr(step_model, 'model_name', 'unknown'),
                'created': None,  # Could add timestamp
            },
            step_number=step_number
        )
        
        steps.append(step_result)
        
        # Call step finish callback if provided
        if on_step_finish:
            if asyncio.iscoroutinefunction(on_step_finish):
                await on_step_finish(step_result)
            else:
                on_step_finish(step_result)
        
        # Check if we should continue
        should_stop = await is_stop_condition_met(stop_conditions, steps)
        
        # Also stop if there are no tool calls or all tool calls failed
        has_successful_tool_calls = any(
            tc for tc in tool_calls if not tc.invalid
        ) and any(
            tr for tr in tool_results if tr.type == "result"
        )
        
        if should_stop or not has_successful_tool_calls:
            break
        
        # Add tool messages to conversation for next step
        if tool_calls and tool_results:
            tool_messages = create_tool_response_messages(tool_calls, tool_results)
            current_messages.extend(tool_messages)
    
    return EnhancedGenerateTextResult(steps)