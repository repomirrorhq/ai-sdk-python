"""Utility functions for Bedrock provider."""

import json
from typing import List, Dict, Any, Union

from ...providers.types import Message, Content, TextContent, ImageContent, ToolCallContent, ToolResultContent, FinishReason
from .types import BedrockMessage, BEDROCK_STOP_REASONS


def convert_to_bedrock_messages(messages: List[Message]) -> List[BedrockMessage]:
    """Convert AI SDK messages to Bedrock message format."""
    bedrock_messages = []
    
    for message in messages:
        bedrock_content = []
        
        # Handle string content
        if isinstance(message.content, str):
            bedrock_content.append({"text": message.content})
        
        # Handle list of content items
        elif isinstance(message.content, list):
            for content_item in message.content:
                if isinstance(content_item, TextContent):
                    bedrock_content.append({"text": content_item.text})
                elif isinstance(content_item, ImageContent):
                    # Handle image content
                    if content_item.image.startswith('data:'):
                        # Data URL format: data:image/jpeg;base64,<base64_data>
                        media_type, base64_data = content_item.image.split(',', 1)
                        format_part = media_type.split(';')[0].split('/')[1]  # Extract format (e.g., 'jpeg')
                        bedrock_content.append({
                            "image": {
                                "format": format_part,
                                "source": {"bytes": base64_data}
                            }
                        })
                    elif content_item.image.startswith('http'):
                        # URL format - Bedrock doesn't support URLs directly, would need to fetch and convert
                        raise ValueError("Bedrock does not support image URLs directly. Please convert to base64.")
                elif isinstance(content_item, ToolCallContent):
                    # Tool use content
                    try:
                        arguments = json.loads(content_item.args) if isinstance(content_item.args, str) else content_item.args
                    except (json.JSONDecodeError, TypeError):
                        arguments = {}
                        
                    bedrock_content.append({
                        "toolUse": {
                            "toolUseId": content_item.id,
                            "name": content_item.name,
                            "input": arguments
                        }
                    })
                elif isinstance(content_item, ToolResultContent):
                    # Tool result content
                    result_content = []
                    if isinstance(content_item.result, str):
                        result_content.append({"text": content_item.result})
                    elif isinstance(content_item.result, dict):
                        result_content.append({"json": content_item.result})
                    else:
                        result_content.append({"text": str(content_item.result)})
                        
                    bedrock_content.append({
                        "toolResult": {
                            "toolUseId": content_item.tool_call_id,
                            "content": result_content
                        }
                    })
        
        # Map role
        bedrock_role = message.role
        if bedrock_role == "system":
            # System messages are handled separately in Bedrock
            bedrock_role = "user"
            
        bedrock_message = BedrockMessage(
            role=bedrock_role,
            content=bedrock_content
        )
        bedrock_messages.append(bedrock_message)
    
    return bedrock_messages


def map_bedrock_finish_reason(bedrock_reason: str) -> FinishReason:
    """Map Bedrock stop reason to AI SDK finish reason."""
    mapping = {
        "end_turn": "stop",
        "tool_use": "tool_calls", 
        "max_tokens": "length",
        "stop_sequence": "stop",
        "content_filter": "content_filter",
    }
    return mapping.get(bedrock_reason, "stop")


def prepare_bedrock_tools(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert AI SDK tools to Bedrock tool format."""
    bedrock_tools = []
    
    for tool in tools:
        if tool.get("type") == "function":
            function = tool.get("function", {})
            bedrock_tool = {
                "toolSpec": {
                    "name": function.get("name", ""),
                    "description": function.get("description", ""),
                    "inputSchema": {
                        "json": function.get("parameters", {})
                    }
                }
            }
            bedrock_tools.append(bedrock_tool)
    
    return bedrock_tools


def extract_model_family(model_id: str) -> str:
    """Extract the model family from a Bedrock model ID."""
    if model_id.startswith("anthropic."):
        return "anthropic"
    elif model_id.startswith("amazon."):
        return "amazon"
    elif model_id.startswith("meta."):
        return "meta"
    elif model_id.startswith("cohere."):
        return "cohere"
    elif model_id.startswith("ai21."):
        return "ai21"
    elif model_id.startswith("mistral."):
        return "mistral"
    elif model_id.startswith("us.amazon."):
        return "nova"
    else:
        return "unknown"


def get_default_max_tokens(model_id: str) -> int:
    """Get default max tokens for a model."""
    model_family = extract_model_family(model_id)
    
    defaults = {
        "anthropic": 4096,
        "amazon": 8192,
        "meta": 2048,
        "cohere": 4096,
        "ai21": 8192,
        "mistral": 4096,
        "nova": 5000,
    }
    
    return defaults.get(model_family, 4096)