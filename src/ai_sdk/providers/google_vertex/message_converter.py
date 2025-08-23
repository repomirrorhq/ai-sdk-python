"""Message conversion utilities for Google Vertex AI."""

from typing import Any, Dict, List, Union, Optional

from ...providers.types import Message, Content


def convert_to_vertex_messages(messages: List[Message]) -> List[Dict[str, Any]]:
    """
    Convert AI SDK messages to Google Vertex AI format.
    
    Args:
        messages: List of AI SDK messages
        
    Returns:
        List of Vertex AI formatted messages
    """
    vertex_messages = []
    
    for message in messages:
        role = message.get("role")
        content = message.get("content", "")
        
        # Convert role to Vertex AI format
        if role == "system":
            # System messages are added as user messages with special prefix
            vertex_role = "user"
            vertex_content = f"System: {content}"
        elif role == "user":
            vertex_role = "user"
            vertex_content = content
        elif role == "assistant":
            vertex_role = "model"
            vertex_content = content
        else:
            # Default to user role for unknown roles
            vertex_role = "user"
            vertex_content = str(content)
        
        # Handle different content types
        parts = []
        
        if isinstance(content, str):
            # Simple text content
            parts.append({"text": vertex_content})
        elif isinstance(content, list):
            # Multi-part content (text + images, etc.)
            for part in content:
                if isinstance(part, dict):
                    if part.get("type") == "text":
                        parts.append({"text": part.get("text", "")})
                    elif part.get("type") == "image_url":
                        # Handle image content
                        image_url = part.get("image_url", {}).get("url", "")
                        if image_url.startswith("data:"):
                            # Data URL - extract mime type and data
                            try:
                                header, data = image_url.split(",", 1)
                                mime_type = header.split(":")[1].split(";")[0]
                                parts.append({
                                    "inline_data": {
                                        "mime_type": mime_type,
                                        "data": data
                                    }
                                })
                            except (ValueError, IndexError):
                                # Invalid data URL, skip
                                continue
                        else:
                            # Regular URL - use file_data format
                            parts.append({
                                "file_data": {
                                    "mime_type": "image/*",
                                    "file_uri": image_url
                                }
                            })
                    elif part.get("type") == "file":
                        # Handle file content
                        file_url = part.get("file_url", "")
                        mime_type = part.get("mime_type", "application/octet-stream")
                        parts.append({
                            "file_data": {
                                "mime_type": mime_type,
                                "file_uri": file_url
                            }
                        })
                else:
                    # String part
                    parts.append({"text": str(part)})
        else:
            # Convert other types to string
            parts.append({"text": str(content)})
        
        # Only add message if it has content parts
        if parts:
            vertex_messages.append({
                "role": vertex_role,
                "parts": parts
            })
    
    return vertex_messages


def convert_from_vertex_response(response: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert Google Vertex AI response to AI SDK format.
    
    Args:
        response: Vertex AI API response
        
    Returns:
        AI SDK formatted response
    """
    candidates = response.get("candidates", [])
    if not candidates:
        return {"text": "", "usage": {"total_tokens": 0}}
    
    candidate = candidates[0]
    content = candidate.get("content", {})
    parts = content.get("parts", [])
    
    # Extract text content
    text_parts = []
    for part in parts:
        if "text" in part:
            text_parts.append(part["text"])
    
    text = "".join(text_parts)
    
    # Extract usage information
    usage_metadata = response.get("usageMetadata", {})
    usage = {
        "prompt_tokens": usage_metadata.get("promptTokenCount", 0),
        "completion_tokens": usage_metadata.get("candidatesTokenCount", 0), 
        "total_tokens": usage_metadata.get("totalTokenCount", 0),
    }
    
    return {
        "text": text,
        "usage": usage,
        "finish_reason": candidate.get("finishReason", "STOP"),
        "response": response,
    }


def prepare_system_message(system_content: str) -> Dict[str, Any]:
    """
    Prepare system message for Vertex AI (converted to user message).
    
    Args:
        system_content: System message content
        
    Returns:
        Vertex AI formatted message
    """
    return {
        "role": "user",
        "parts": [{"text": f"System: {system_content}"}]
    }