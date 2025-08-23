"""
Message conversion utilities for Anthropic API.

This module handles converting between AI SDK message format and Anthropic's message format.
"""

from typing import List, Dict, Any, Optional
from ...core.types import Message, Content, GenerateTextResult, Usage, FinishReason
from .api_types import AnthropicMessage, AnthropicPrompt, AnthropicResponse


def convert_messages_to_anthropic(messages: List[Message]) -> Dict[str, Any]:
    """
    Convert AI SDK messages to Anthropic message format.
    
    Anthropic API expects:
    - A separate 'system' parameter for system messages
    - Messages alternating between 'user' and 'assistant' roles
    - Content can be string or list of content blocks
    
    Args:
        messages: List of AI SDK messages
        
    Returns:
        Dictionary with 'system' (optional) and 'messages' keys
    """
    system_message = None
    anthropic_messages = []
    
    # Process each message
    for message in messages:
        if message.role == "system":
            # Anthropic handles system messages separately
            if system_message is None:
                system_message = ""
            
            # Extract text content from system message
            for content in message.content:
                if content.type == "text":
                    if system_message:
                        system_message += "\n\n"
                    system_message += content.text
        
        elif message.role in ["user", "assistant"]:
            # Convert content to Anthropic format
            if len(message.content) == 1 and message.content[0].type == "text":
                # Simple text message
                content_value = message.content[0].text
            else:
                # Complex content with multiple parts
                content_blocks = []
                for content in message.content:
                    if content.type == "text":
                        content_blocks.append({
                            "type": "text",
                            "text": content.text,
                        })
                    elif content.type == "image":
                        # Anthropic supports image content
                        if hasattr(content, 'image_url') and content.image_url:
                            content_blocks.append({
                                "type": "image",
                                "source": {
                                    "type": "url",
                                    "url": content.image_url.url,
                                }
                            })
                        elif hasattr(content, 'data') and content.data:
                            # Base64 image data
                            content_blocks.append({
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": getattr(content, 'media_type', 'image/jpeg'),
                                    "data": content.data,
                                }
                            })
                    elif content.type == "tool-call":
                        # Tool calls in assistant messages
                        content_blocks.append({
                            "type": "tool_use",
                            "id": content.tool_call_id,
                            "name": content.tool_name,
                            "input": content.input if isinstance(content.input, dict) else {},
                        })
                    elif content.type == "tool-result":
                        # Tool results in user messages (converted from tool role)
                        result_content = content.result
                        if isinstance(result_content, str):
                            result_value = result_content
                        else:
                            result_value = str(result_content)
                        
                        content_blocks.append({
                            "type": "tool_result",
                            "tool_use_id": content.tool_call_id,
                            "content": result_value,
                        })
                
                content_value = content_blocks if content_blocks else "..."
            
            anthropic_messages.append(AnthropicMessage(
                role=message.role,
                content=content_value,
            ))
        
        elif message.role == "tool":
            # Convert tool messages to user messages with tool_result content
            for content in message.content:
                if content.type == "tool-result":
                    result_content = content.result
                    if isinstance(result_content, str):
                        result_value = result_content
                    else:
                        result_value = str(result_content)
                    
                    # Add as user message with tool result
                    anthropic_messages.append(AnthropicMessage(
                        role="user",
                        content=[{
                            "type": "tool_result",
                            "tool_use_id": content.tool_call_id,
                            "content": result_value,
                        }]
                    ))
    
    result = {
        "messages": [msg.dict() for msg in anthropic_messages]
    }
    
    if system_message:
        result["system"] = system_message
    
    return result


def convert_anthropic_response(response_data: Dict[str, Any]) -> GenerateTextResult:
    """
    Convert Anthropic API response to AI SDK format.
    
    Args:
        response_data: Response from Anthropic API
        
    Returns:
        GenerateTextResult with converted data
    """
    # Extract text content
    text_content = ""
    tool_calls = []
    
    for content_block in response_data.get("content", []):
        if content_block.get("type") == "text":
            text_content += content_block.get("text", "")
        elif content_block.get("type") == "tool_use":
            # Convert tool use to tool call
            tool_calls.append({
                "type": "tool-call",
                "tool_call_id": content_block.get("id", ""),
                "tool_name": content_block.get("name", ""),
                "input": content_block.get("input", {}),
            })
    
    # Build content list
    content = []
    if text_content:
        content.append(Content(type="text", text=text_content))
    
    for tool_call in tool_calls:
        content.append(Content(
            type="tool-call",
            tool_call_id=tool_call["tool_call_id"],
            tool_name=tool_call["tool_name"],
            input=tool_call["input"],
        ))
    
    # Convert finish reason
    stop_reason = response_data.get("stop_reason")
    if stop_reason == "end_turn":
        finish_reason = "stop"
    elif stop_reason == "max_tokens":
        finish_reason = "length"
    elif stop_reason == "stop_sequence":
        finish_reason = "stop"
    elif stop_reason == "tool_use":
        finish_reason = "tool-calls"
    else:
        finish_reason = "unknown"
    
    # Extract usage
    usage_data = response_data.get("usage", {})
    usage = Usage(
        input_tokens=usage_data.get("input_tokens", 0),
        output_tokens=usage_data.get("output_tokens", 0),
        total_tokens=usage_data.get("input_tokens", 0) + usage_data.get("output_tokens", 0),
    )
    
    return GenerateTextResult(
        text=text_content,
        content=content,
        finish_reason=finish_reason,
        usage=usage,
        raw_response=response_data,
    )