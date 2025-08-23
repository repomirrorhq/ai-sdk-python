"""Message format conversion utilities for Google Generative AI."""

import base64
from typing import List, Optional, Tuple

from ...providers.types import Message, Content
from .api_types import GoogleContent, GoogleContentPart, GooglePromptRequest


def convert_to_google_messages(
    messages: List[Message],
) -> Tuple[List[GoogleContent], Optional[str]]:
    """
    Convert AI SDK messages to Google Generative AI format.
    
    Args:
        messages: List of AI SDK messages
        
    Returns:
        Tuple of (contents, system_instruction)
    """
    contents: List[GoogleContent] = []
    system_instruction: Optional[str] = None
    system_messages_allowed = True
    
    for message in messages:
        if message.role == "system":
            if not system_messages_allowed:
                raise ValueError(
                    "System messages are only supported at the beginning of the conversation"
                )
            
            # Extract text from system message content
            if isinstance(message.content, str):
                system_instruction = message.content
            elif isinstance(message.content, list):
                # Concatenate all text parts for system message
                text_parts = []
                for part in message.content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        text_parts.append(part["text"])
                    elif isinstance(part, str):
                        text_parts.append(part)
                system_instruction = "\n".join(text_parts)
            continue
            
        system_messages_allowed = False
        
        # Convert user/assistant messages
        if message.role == "user":
            google_role = "user"
        elif message.role == "assistant":
            google_role = "model"
        else:
            raise ValueError(f"Unsupported message role: {message.role}")
            
        parts = _convert_content_to_parts(message.content)
        
        contents.append(GoogleContent(
            role=google_role,
            parts=parts
        ))
    
    return contents, system_instruction


def _convert_content_to_parts(content: Content) -> List[GoogleContentPart]:
    """Convert content to Google content parts."""
    parts: List[GoogleContentPart] = []
    
    if isinstance(content, str):
        parts.append(GoogleContentPart(text=content))
    elif isinstance(content, list):
        for part in content:
            if isinstance(part, str):
                parts.append(GoogleContentPart(text=part))
            elif isinstance(part, dict):
                if part.get("type") == "text":
                    parts.append(GoogleContentPart(text=part["text"]))
                elif part.get("type") == "image":
                    # Handle image content
                    if "url" in part:
                        # Handle data URL or file URL
                        url = part["url"]
                        if url.startswith("data:"):
                            # Parse data URL: data:image/jpeg;base64,/9j/4AA...
                            header, data = url.split(",", 1)
                            mime_type = header.split(":")[1].split(";")[0]
                            
                            # Default to image/jpeg for unknown image/* types
                            if mime_type == "image/*":
                                mime_type = "image/jpeg"
                                
                            parts.append(GoogleContentPart(
                                inline_data={
                                    "mime_type": mime_type,
                                    "data": data  # Already base64 encoded
                                }
                            ))
                        else:
                            # For file URLs, we'll need to handle differently
                            # For now, we'll pass it as-is (Google supports some URL formats)
                            parts.append(GoogleContentPart(
                                file_data={
                                    "file_uri": url,
                                    "mime_type": "image/jpeg"  # Default mime type
                                }
                            ))
                    elif "data" in part:
                        # Handle raw image data
                        image_data = part["data"]
                        mime_type = part.get("mimeType", "image/jpeg")
                        
                        # Encode to base64 if not already encoded
                        if isinstance(image_data, bytes):
                            data = base64.b64encode(image_data).decode("utf-8")
                        else:
                            data = str(image_data)  # Assume already base64
                            
                        parts.append(GoogleContentPart(
                            inline_data={
                                "mime_type": mime_type,
                                "data": data
                            }
                        ))
                else:
                    # For other content types, convert to text if possible
                    text_content = str(part)
                    parts.append(GoogleContentPart(text=text_content))
    else:
        # Convert any other content to string
        parts.append(GoogleContentPart(text=str(content)))
    
    return parts


def convert_google_response_to_message(google_content: GoogleContent) -> Message:
    """Convert Google response content back to AI SDK message format."""
    
    # Convert Google role back to AI SDK role
    if google_content.role == "model":
        role = "assistant"
    elif google_content.role == "user":
        role = "user"
    else:
        role = google_content.role
    
    # Extract text content from parts
    content_parts = []
    for part in google_content.parts:
        if part.text:
            content_parts.append(part.text)
        elif part.inline_data:
            # For now, we'll represent images as text descriptions
            mime_type = part.inline_data.get("mime_type", "unknown")
            content_parts.append(f"[Image: {mime_type}]")
        elif part.file_data:
            # For file data, represent as text description
            file_uri = part.file_data.get("file_uri", "unknown")
            content_parts.append(f"[File: {file_uri}]")
    
    # Join all text parts
    content = "\n".join(content_parts) if len(content_parts) > 1 else content_parts[0] if content_parts else ""
    
    return Message(role=role, content=content)