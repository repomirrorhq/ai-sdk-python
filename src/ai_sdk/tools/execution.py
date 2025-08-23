"""Tool execution logic for AI SDK Python."""

import asyncio
import json
from typing import Any, Dict, List, Optional

from pydantic import ValidationError

from ..errors.base import AISDKError
from ..providers.types import Message, ToolCallContent
from .core import Tool, ToolCall, ToolResult, ToolCallOptions


async def execute_tools(
    tools: Dict[str, Tool],
    tool_calls: List[ToolCall],
    messages: List[Message],
    experimental_context: Optional[Any] = None,
) -> List[ToolResult]:
    """Execute multiple tool calls.
    
    Args:
        tools: Dictionary of available tools by name
        tool_calls: List of tool calls to execute
        messages: Messages context for the tool calls
        experimental_context: Additional context for tools
        
    Returns:
        List of tool results
        
    Raises:
        AISDKError: If tool execution fails
    """
    results = []
    
    # Execute all tool calls concurrently
    tasks = []
    for tool_call in tool_calls:
        task = execute_tool_call(
            tools=tools,
            tool_call=tool_call,
            messages=messages,
            experimental_context=experimental_context,
        )
        tasks.append(task)
    
    # Wait for all executions to complete
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        raise AISDKError(f"Failed to execute tools: {e}") from e
    
    # Convert exceptions to error results
    final_results = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            error_result = ToolResult(
                tool_call_id=tool_calls[i].tool_call_id,
                tool_name=tool_calls[i].tool_name,
                input=tool_calls[i].input,
                output=None,
                is_error=True,
                error=str(result),
            )
            final_results.append(error_result)
        else:
            final_results.append(result)
    
    return final_results


async def execute_tool_call(
    tools: Dict[str, Tool],
    tool_call: ToolCall,
    messages: List[Message],
    experimental_context: Optional[Any] = None,
) -> ToolResult:
    """Execute a single tool call.
    
    Args:
        tools: Dictionary of available tools by name
        tool_call: The tool call to execute
        messages: Messages context for the tool call
        experimental_context: Additional context for the tool
        
    Returns:
        Tool result containing the execution output
        
    Raises:
        AISDKError: If the tool is not found or execution fails
    """
    # Find the tool
    tool = tools.get(tool_call.tool_name)
    if not tool:
        return ToolResult(
            tool_call_id=tool_call.tool_call_id,
            tool_name=tool_call.tool_name,
            input=tool_call.input,
            output=None,
            is_error=True,
            error=f"Tool '{tool_call.tool_name}' not found",
        )
    
    # Check if tool has an execute function
    if not tool.execute:
        return ToolResult(
            tool_call_id=tool_call.tool_call_id,
            tool_name=tool_call.tool_name,
            input=tool_call.input,
            output=None,
            is_error=True,
            error=f"Tool '{tool_call.tool_name}' does not have an execute function",
        )
    
    # Create tool call options
    options = ToolCallOptions(
        tool_call_id=tool_call.tool_call_id,
        messages=messages,
        experimental_context=experimental_context,
    )
    
    # Call the on_input_available callback if it exists
    if tool.on_input_available:
        try:
            callback_result = tool.on_input_available(tool_call.input, options)
            if asyncio.iscoroutine(callback_result):
                await callback_result
        except Exception as e:
            # Log but don't fail the tool execution
            pass
    
    # Execute the tool
    try:
        output = await tool.execute_async(tool_call.input, options)
        
        return ToolResult(
            tool_call_id=tool_call.tool_call_id,
            tool_name=tool_call.tool_name,
            input=tool_call.input,
            output=output,
            provider_executed=tool_call.provider_executed,
            dynamic=tool_call.dynamic,
            is_error=False,
        )
        
    except Exception as e:
        return ToolResult(
            tool_call_id=tool_call.tool_call_id,
            tool_name=tool_call.tool_name,
            input=tool_call.input,
            output=None,
            is_error=True,
            error=str(e),
        )


def extract_tool_calls_from_messages(messages: List[Message]) -> List[ToolCall]:
    """Extract tool calls from message content.
    
    Args:
        messages: List of messages to extract tool calls from
        
    Returns:
        List of extracted tool calls
    """
    tool_calls = []
    
    for message in messages:
        if isinstance(message.content, list):
            for content in message.content:
                if isinstance(content, ToolCallContent):
                    tool_call = ToolCall(
                        tool_call_id=content.tool_call_id,
                        tool_name=content.tool_name,
                        input=content.args,
                    )
                    tool_calls.append(tool_call)
    
    return tool_calls


def create_tool_result_messages(tool_results: List[ToolResult]) -> List[Message]:
    """Create messages from tool results for continuation.
    
    Args:
        tool_results: List of tool results to convert
        
    Returns:
        List of messages containing tool results
    """
    messages = []
    
    for result in tool_results:
        # Create tool result content
        from ..providers.types import ToolResultContent
        
        content = ToolResultContent(
            tool_call_id=result.tool_call_id,
            result=result.output if not result.is_error else result.error,
            is_error=result.is_error,
        )
        
        # Create message
        message = Message(
            role="tool",
            content=[content],
            tool_call_id=result.tool_call_id,
        )
        messages.append(message)
    
    return messages


async def execute_tools_from_messages(
    tools: Dict[str, Tool],
    messages: List[Message],
    experimental_context: Optional[Any] = None,
) -> List[Message]:
    """Extract tool calls from messages and execute them, returning result messages.
    
    Args:
        tools: Dictionary of available tools by name
        messages: Messages containing tool calls
        experimental_context: Additional context for tools
        
    Returns:
        List of messages containing tool results
        
    Raises:
        AISDKError: If tool execution fails
    """
    # Extract tool calls from messages
    tool_calls = extract_tool_calls_from_messages(messages)
    
    if not tool_calls:
        return []
    
    # Execute the tool calls
    tool_results = await execute_tools(
        tools=tools,
        tool_calls=tool_calls,
        messages=messages,
        experimental_context=experimental_context,
    )
    
    # Convert results to messages
    return create_tool_result_messages(tool_results)