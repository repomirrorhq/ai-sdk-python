"""
Message conversion utilities for Groq provider.

Handles conversion between AI SDK message formats and Groq API formats.
"""

from __future__ import annotations

from typing import List, Dict, Any, Optional

from ..types import (
    Message,
    MessageRole,
    ToolCall,
    ToolResult,
    FinishReason,
    Usage,
    GenerateTextResult,
    ProviderMetadata
)
from .api_types import (
    GroqMessage,
    GroqChatCompletionResponse,
    GroqUsage,
)


def convert_to_groq_messages(messages: List[Message]) -> List[GroqMessage]:
    """Convert AI SDK messages to Groq format.
    
    Args:
        messages: List of AI SDK Message objects
        
    Returns:
        List of GroqMessage objects
    """
    groq_messages: List[GroqMessage] = []
    
    for message in messages:
        if message.role == MessageRole.SYSTEM:
            groq_messages.append(GroqMessage(
                role="system",
                content=message.content
            ))
        elif message.role == MessageRole.USER:
            # Handle multimodal content
            if isinstance(message.content, list):
                # Convert multimodal content (text + images)
                content_parts = []
                for part in message.content:
                    if isinstance(part, dict):
                        if part.get("type") == "text":
                            content_parts.append({
                                "type": "text",
                                "text": part.get("text", "")
                            })
                        elif part.get("type") == "image":
                            content_parts.append({
                                "type": "image_url",
                                "image_url": {
                                    "url": part.get("image", "")
                                }
                            })
                groq_messages.append(GroqMessage(
                    role="user", 
                    content=content_parts
                ))
            else:
                groq_messages.append(GroqMessage(
                    role="user",
                    content=str(message.content)
                ))
                
        elif message.role == MessageRole.ASSISTANT:
            groq_message = GroqMessage(
                role="assistant",
                content=message.content
            )
            
            # Add tool calls if present
            if message.tool_calls:
                tool_calls = []
                for tool_call in message.tool_calls:
                    tool_calls.append({
                        "id": tool_call.id,
                        "type": "function",
                        "function": {
                            "name": tool_call.name,
                            "arguments": tool_call.arguments
                        }
                    })
                groq_message.tool_calls = tool_calls
                
            groq_messages.append(groq_message)
            
        elif message.role == MessageRole.TOOL:
            # Tool result message
            groq_messages.append(GroqMessage(
                role="tool",
                content=str(message.content),
                tool_call_id=getattr(message, 'tool_call_id', None)
            ))
            
    return groq_messages


def convert_from_groq_response(
    response: GroqChatCompletionResponse,
    model_id: str
) -> GenerateTextResult:
    """Convert Groq response to AI SDK format.
    
    Args:
        response: Groq API response
        model_id: The model ID used for the request
        
    Returns:
        GenerateTextResult object
    """
    if not response.choices:
        raise ValueError("No choices in Groq response")
        
    choice = response.choices[0]
    message = choice.message
    
    # Extract content
    content = message.content or ""
    
    # Extract tool calls if present
    tool_calls: Optional[List[ToolCall]] = None
    if message.tool_calls:
        tool_calls = []
        for tool_call in message.tool_calls:
            tool_calls.append(ToolCall(
                id=tool_call["id"],
                name=tool_call["function"]["name"],
                arguments=tool_call["function"]["arguments"]
            ))
    
    # Map finish reason
    finish_reason = _map_finish_reason(choice.finish_reason)
    
    # Extract usage information
    usage = None
    if response.usage:
        usage = Usage(
            prompt_tokens=response.usage.prompt_tokens,
            completion_tokens=response.usage.completion_tokens,
            total_tokens=response.usage.total_tokens
        )
    
    # Build provider metadata
    metadata = ProviderMetadata(
        provider_id="groq",
        model_id=model_id,
        usage=usage,
        finish_reason=finish_reason,
        response_id=response.id,
        response_timestamp=response.created,
    )
    
    # Add Groq-specific metadata
    if response.usage and hasattr(response.usage, 'prompt_time'):
        metadata.extra = {
            "prompt_time": response.usage.prompt_time,
            "completion_time": response.usage.completion_time,
            "total_time": response.usage.total_time,
            "system_fingerprint": response.system_fingerprint
        }
    
    return GenerateTextResult(
        content=content,
        tool_calls=tool_calls,
        finish_reason=finish_reason,
        usage=usage,
        metadata=metadata
    )


def _map_finish_reason(groq_reason: Optional[str]) -> FinishReason:
    """Map Groq finish reason to AI SDK finish reason.
    
    Args:
        groq_reason: Finish reason from Groq API
        
    Returns:
        AI SDK FinishReason
    """
    if not groq_reason:
        return FinishReason.UNKNOWN
        
    mapping = {
        "stop": FinishReason.STOP,
        "length": FinishReason.LENGTH,
        "tool_calls": FinishReason.TOOL_CALLS,
        "content_filter": FinishReason.CONTENT_FILTER,
        "function_call": FinishReason.TOOL_CALLS,  # Legacy mapping
    }
    
    return mapping.get(groq_reason, FinishReason.UNKNOWN)