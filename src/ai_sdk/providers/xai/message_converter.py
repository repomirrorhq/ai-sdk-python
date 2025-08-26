"""Message conversion utilities for xAI provider."""

import base64
from typing import Any, Dict, List, Union

from ...core.types import Message, MessageContent, TextContent, FileContent


def convert_to_xai_messages(messages: List[Message]) -> List[Dict[str, Any]]:
    """
    Convert AI SDK messages to xAI format.
    
    Args:
        messages: List of AI SDK messages
        
    Returns:
        List of messages in xAI format
    """
    xai_messages = []
    
    for message in messages:
        if message.role == "system":
            xai_messages.append({
                "role": "system",
                "content": message.content if isinstance(message.content, str) else _extract_text_content(message.content)
            })
        elif message.role == "user":
            xai_messages.append(_convert_user_message(message))
        elif message.role == "assistant":
            xai_messages.append(_convert_assistant_message(message))
        elif message.role == "tool":
            xai_messages.append({
                "role": "tool",
                "tool_call_id": message.tool_call_id,
                "content": message.content if isinstance(message.content, str) else _extract_text_content(message.content)
            })
    
    return xai_messages


def _convert_user_message(message: Message) -> Dict[str, Any]:
    """Convert a user message to xAI format."""
    if isinstance(message.content, str):
        return {
            "role": "user",
            "content": message.content
        }
    
    # Handle multimodal content
    if len(message.content) == 1 and isinstance(message.content[0], TextContent):
        return {
            "role": "user",
            "content": message.content[0].text
        }
    
    # Convert to multimodal format
    content_parts = []
    for part in message.content:
        if isinstance(part, TextContent):
            content_parts.append({
                "type": "text",
                "text": part.text
            })
        elif isinstance(part, FileContent):
            if part.media_type and part.media_type.startswith("image/"):
                # Handle image content
                if isinstance(part.data, str) and part.data.startswith("http"):
                    # URL image
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {"url": part.data}
                    })
                else:
                    # Base64 image data
                    media_type = part.media_type if part.media_type != "image/*" else "image/jpeg"
                    if isinstance(part.data, bytes):
                        data_url = f"data:{media_type};base64,{base64.b64encode(part.data).decode()}"
                    else:
                        data_url = f"data:{media_type};base64,{part.data}"
                    
                    content_parts.append({
                        "type": "image_url",
                        "image_url": {"url": data_url}
                    })
    
    return {
        "role": "user",
        "content": content_parts
    }


def _convert_assistant_message(message: Message) -> Dict[str, Any]:
    """Convert an assistant message to xAI format."""
    xai_message = {"role": "assistant"}
    
    if isinstance(message.content, str):
        xai_message["content"] = message.content
    else:
        # Extract text content and tool calls
        text_parts = []
        tool_calls = []
        
        for part in message.content:
            if isinstance(part, TextContent):
                text_parts.append(part.text)
            elif hasattr(part, 'tool_call_id') and hasattr(part, 'tool_name'):
                # Tool call content
                tool_calls.append({
                    "id": part.tool_call_id,
                    "type": "function",
                    "function": {
                        "name": part.tool_name,
                        "arguments": part.input if hasattr(part, 'input') else "{}"
                    }
                })
        
        if text_parts:
            xai_message["content"] = " ".join(text_parts)
        
        if tool_calls:
            xai_message["tool_calls"] = tool_calls
    
    # Add tool calls if present in message
    if hasattr(message, 'tool_calls') and message.tool_calls:
        xai_message["tool_calls"] = [
            {
                "id": tool_call.id,
                "type": "function",
                "function": {
                    "name": tool_call.function.name,
                    "arguments": tool_call.function.arguments
                }
            }
            for tool_call in message.tool_calls
        ]
    
    return xai_message


def _extract_text_content(content: Union[str, List[MessageContent]]) -> str:
    """Extract text content from mixed content."""
    if isinstance(content, str):
        return content
    
    text_parts = []
    for part in content:
        if isinstance(part, TextContent):
            text_parts.append(part.text)
    
    return " ".join(text_parts)


def map_finish_reason(xai_reason: str) -> str:
    """Map xAI finish reason to AI SDK format."""
    mapping = {
        "stop": "stop",
        "length": "length", 
        "tool_calls": "tool-calls",
        "content_filter": "content-filter",
        "function_call": "tool-calls",  # Legacy mapping
    }
    
    return mapping.get(xai_reason, "other")