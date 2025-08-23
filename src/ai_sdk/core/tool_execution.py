"""Tool execution engine for multi-step AI workflows."""

from __future__ import annotations

import asyncio
import traceback
from typing import Any, Dict, List, Optional, Union

from ..errors import AISDKError
from ..providers.types import Message
from ..tools.core import Tool, ToolCall, ToolResult


class ToolExecutionError(AISDKError):
    """Error during tool execution."""
    
    def __init__(self, tool_name: str, tool_call_id: str, error: Exception) -> None:
        self.tool_name = tool_name
        self.tool_call_id = tool_call_id
        self.original_error = error
        super().__init__(f"Tool execution failed for {tool_name} (call {tool_call_id}): {error}")


class ToolCallRepairError(AISDKError):
    """Error during tool call repair."""
    
    def __init__(self, tool_call_id: str, error: Exception) -> None:
        self.tool_call_id = tool_call_id
        self.original_error = error
        super().__init__(f"Tool call repair failed for call {tool_call_id}: {error}")


async def execute_tools(
    tool_calls: List[ToolCall],
    tools: Dict[str, Tool],
    messages: List[Message],
    context: Optional[Any] = None,
    abort_signal: Optional[Any] = None,
) -> List[ToolResult]:
    """Execute a list of tool calls and return their results.
    
    Args:
        tool_calls: List of tool calls to execute
        tools: Dictionary of available tools
        messages: Current message history
        context: Optional context passed to tools
        abort_signal: Optional abort signal for cancellation
        
    Returns:
        List of tool results
    """
    if not tool_calls:
        return []
    
    # Execute all tool calls in parallel
    tasks = []
    for tool_call in tool_calls:
        if tool_call.invalid:
            # Create error result for invalid tool calls
            error_result = ToolResult(
                type="error",
                tool_call_id=tool_call.tool_call_id,
                tool_name=tool_call.tool_name,
                input=tool_call.input,
                error=getattr(tool_call, 'error', 'Invalid tool call'),
                dynamic=tool_call.dynamic
            )
            tasks.append(asyncio.create_task(_return_result(error_result)))
        else:
            task = asyncio.create_task(
                _execute_single_tool(
                    tool_call=tool_call,
                    tools=tools,
                    messages=messages,
                    context=context,
                    abort_signal=abort_signal
                )
            )
            tasks.append(task)
    
    # Wait for all executions to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Convert exceptions to error results
    final_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            tool_call = tool_calls[i]
            error_result = ToolResult(
                type="error",
                tool_call_id=tool_call.tool_call_id,
                tool_name=tool_call.tool_name,
                input=tool_call.input,
                error=str(result),
                dynamic=tool_call.dynamic
            )
            final_results.append(error_result)
        else:
            final_results.append(result)
    
    return final_results


async def _return_result(result: ToolResult) -> ToolResult:
    """Helper to return a result as an awaitable."""
    return result


async def _execute_single_tool(
    tool_call: ToolCall,
    tools: Dict[str, Tool],
    messages: List[Message],
    context: Optional[Any] = None,
    abort_signal: Optional[Any] = None,
) -> ToolResult:
    """Execute a single tool call."""
    tool = tools.get(tool_call.tool_name)
    
    if tool is None:
        return ToolResult(
            type="error",
            tool_call_id=tool_call.tool_call_id,
            tool_name=tool_call.tool_name,
            input=tool_call.input,
            error=f"Tool '{tool_call.tool_name}' not found",
            dynamic=tool_call.dynamic
        )
    
    if not hasattr(tool, 'execute') or tool.execute is None:
        return ToolResult(
            type="error",
            tool_call_id=tool_call.tool_call_id,
            tool_name=tool_call.tool_name,
            input=tool_call.input,
            error=f"Tool '{tool_call.tool_name}' has no execute method",
            dynamic=tool_call.dynamic
        )
    
    try:
        # Prepare execution context
        execution_context = {
            'tool_call_id': tool_call.tool_call_id,
            'messages': messages,
            'abort_signal': abort_signal,
            'context': context,
        }
        
        # Call onInputAvailable if the tool has it
        if hasattr(tool, 'on_input_available') and tool.on_input_available:
            await tool.on_input_available(
                input=tool_call.input,
                tool_call_id=tool_call.tool_call_id,
                messages=messages,
                abort_signal=abort_signal,
                context=context
            )
        
        # Execute the tool
        if asyncio.iscoroutinefunction(tool.execute):
            output = await tool.execute(tool_call.input, **execution_context)
        else:
            output = tool.execute(tool_call.input, **execution_context)
        
        return ToolResult(
            type="result",
            tool_call_id=tool_call.tool_call_id,
            tool_name=tool_call.tool_name,
            input=tool_call.input,
            output=output,
            dynamic=tool_call.dynamic
        )
        
    except Exception as e:
        # Create detailed error information
        error_message = str(e)
        if hasattr(e, '__traceback__'):
            error_message += f"\n\nTraceback:\n{''.join(traceback.format_tb(e.__traceback__))}"
        
        return ToolResult(
            type="error",
            tool_call_id=tool_call.tool_call_id,
            tool_name=tool_call.tool_name,
            input=tool_call.input,
            error=error_message,
            dynamic=tool_call.dynamic
        )


def parse_tool_calls_from_content(
    content: List[Any],  # List[Content] - avoiding circular import
    tools: Dict[str, Tool],
    repair_function: Optional[Any] = None  # ToolCallRepairFunction
) -> List[ToolCall]:
    """Parse tool calls from model content.
    
    Args:
        content: Content from model response
        tools: Available tools for validation
        repair_function: Optional function to repair invalid tool calls
        
    Returns:
        List of parsed tool calls
    """
    tool_calls = []
    
    for item in content:
        if not hasattr(item, 'type') or item.type != 'tool_call':
            continue
        
        tool_name = getattr(item, 'tool_name', None)
        tool_call_id = getattr(item, 'tool_call_id', None)
        tool_input = getattr(item, 'input', {})
        
        if not tool_name or not tool_call_id:
            continue
        
        # Check if tool exists
        tool = tools.get(tool_name)
        is_dynamic = tool is not None and getattr(tool, 'type', 'static') == 'dynamic'
        
        try:
            # Validate tool input if tool exists
            if tool and hasattr(tool, 'validate_input'):
                validated_input = tool.validate_input(tool_input)
            else:
                validated_input = tool_input
            
            tool_call = ToolCall(
                type="call",
                tool_call_id=tool_call_id,
                tool_name=tool_name,
                input=validated_input,
                dynamic=is_dynamic,
                invalid=False
            )
            
        except Exception as e:
            # Try to repair the tool call if repair function is provided
            if repair_function:
                try:
                    invalid_call = ToolCall(
                        type="call",
                        tool_call_id=tool_call_id,
                        tool_name=tool_name,
                        input=tool_input,
                        dynamic=is_dynamic,
                        invalid=True,
                        error=e
                    )
                    
                    repaired_call = await repair_function(invalid_call)
                    if repaired_call:
                        tool_call = repaired_call
                    else:
                        tool_call = invalid_call
                        
                except Exception as repair_error:
                    tool_call = ToolCall(
                        type="call",
                        tool_call_id=tool_call_id,
                        tool_name=tool_name,
                        input=tool_input,
                        dynamic=is_dynamic,
                        invalid=True,
                        error=ToolCallRepairError(tool_call_id, repair_error)
                    )
            else:
                tool_call = ToolCall(
                    type="call",
                    tool_call_id=tool_call_id,
                    tool_name=tool_name,
                    input=tool_input,
                    dynamic=is_dynamic,
                    invalid=True,
                    error=e
                )
        
        tool_calls.append(tool_call)
    
    return tool_calls


def create_tool_response_messages(
    tool_calls: List[ToolCall],
    tool_results: List[ToolResult]
) -> List[Message]:
    """Create response messages for tool calls and results.
    
    Args:
        tool_calls: List of tool calls
        tool_results: List of tool results
        
    Returns:
        List of messages to add to conversation
    """
    messages = []
    
    # Create tool call message if there are tool calls
    if tool_calls:
        # Group tool calls by type and create appropriate message content
        tool_call_content = []
        for tool_call in tool_calls:
            if not tool_call.invalid:
                tool_call_content.append({
                    'type': 'tool_call',
                    'tool_call_id': tool_call.tool_call_id,
                    'tool_name': tool_call.tool_name,
                    'input': tool_call.input
                })
        
        if tool_call_content:
            messages.append(Message(
                role='assistant',
                content=tool_call_content
            ))
    
    # Create tool result messages
    for result in tool_results:
        content = {
            'type': 'tool_result',
            'tool_call_id': result.tool_call_id,
            'tool_name': result.tool_name,
        }
        
        if result.type == "result":
            content['result'] = result.output
        else:  # error
            content['error'] = result.error
        
        messages.append(Message(
            role='tool',
            content=[content]
        ))
    
    return messages