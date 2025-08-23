"""
Message conversion utilities for Cohere provider.
Converts AI SDK messages to Cohere-compatible format.
"""

from typing import Any, Dict, List, Tuple, Optional
from ai_sdk.core.types import (
    ChatPrompt, 
    SystemMessage, 
    UserMessage, 
    AssistantMessage,
    ToolMessage,
    Message,
    ContentPart,
    TextContentPart,
    ImageContentPart,
    AudioContentPart
)
from .types import CohereMessage, CohereDocument


def convert_to_cohere_messages(
    prompt: ChatPrompt,
) -> Tuple[List[CohereMessage], List[CohereDocument], List[str]]:
    """
    Convert AI SDK ChatPrompt to Cohere messages format.
    
    Returns:
        - messages: List of Cohere-formatted messages
        - documents: List of documents extracted from the conversation
        - warnings: List of conversion warnings
    """
    messages: List[CohereMessage] = []
    documents: List[CohereDocument] = []
    warnings: List[str] = []
    
    for message in prompt.messages:
        if isinstance(message, SystemMessage):
            # Cohere handles system messages as the first message with role "system"
            cohere_msg = CohereMessage(
                role="system",
                content=message.content
            )
            messages.append(cohere_msg)
            
        elif isinstance(message, UserMessage):
            content = _convert_content_parts(message.content, warnings, documents)
            cohere_msg = CohereMessage(
                role="user", 
                content=content
            )
            messages.append(cohere_msg)
            
        elif isinstance(message, AssistantMessage):
            # Handle tool calls in assistant messages
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
                
                cohere_msg = CohereMessage(
                    role="assistant",
                    content=message.content or "",
                    tool_calls=tool_calls
                )
            else:
                cohere_msg = CohereMessage(
                    role="assistant",
                    content=message.content or ""
                )
            messages.append(cohere_msg)
            
        elif isinstance(message, ToolMessage):
            # Cohere expects tool results in a specific format
            cohere_msg = CohereMessage(
                role="tool",
                content=str(message.content)
            )
            messages.append(cohere_msg)
            
        else:
            warnings.append(f"Unknown message type: {type(message)}")
    
    return messages, documents, warnings


def _convert_content_parts(
    content: str | List[ContentPart], 
    warnings: List[str],
    documents: List[CohereDocument]
) -> str:
    """
    Convert content parts to string format for Cohere.
    Cohere primarily uses text content, so we convert other types accordingly.
    """
    if isinstance(content, str):
        return content
        
    text_parts = []
    
    for part in content:
        if isinstance(part, TextContentPart):
            text_parts.append(part.text)
            
        elif isinstance(part, ImageContentPart):
            # Cohere doesn't support direct image content in chat
            # We'll add a warning and skip the image
            warnings.append("Image content is not supported in Cohere chat messages. Image content was skipped.")
            
        elif isinstance(part, AudioContentPart):
            # Cohere doesn't support audio content in chat
            warnings.append("Audio content is not supported in Cohere chat messages. Audio content was skipped.")
            
        else:
            warnings.append(f"Unknown content part type: {type(part)}")
    
    return " ".join(text_parts) if text_parts else ""


def extract_documents_from_content(content: Any) -> List[CohereDocument]:
    """
    Extract documents from content for Cohere's document-aware chat.
    This is a placeholder for future document extraction functionality.
    """
    # TODO: Implement document extraction logic when needed
    return []


def prepare_cohere_tools(tools: List[Dict[str, Any]] | None) -> Tuple[List[Dict[str, Any]] | None, Dict[str, Any] | None, List[str]]:
    """
    Prepare tools for Cohere API format.
    
    Returns:
        - tools: Cohere-formatted tools
        - tool_choice: Cohere tool choice configuration  
        - warnings: List of conversion warnings
    """
    if not tools:
        return None, None, []
        
    cohere_tools = []
    warnings = []
    
    for tool in tools:
        if tool.get("type") != "function":
            warnings.append(f"Tool type '{tool.get('type')}' is not supported. Only 'function' tools are supported.")
            continue
            
        function = tool.get("function", {})
        
        # Convert OpenAI-style tool to Cohere format
        cohere_tool = {
            "name": function.get("name"),
            "description": function.get("description", ""),
            "parameter_definitions": {}
        }
        
        # Convert JSON Schema parameters to Cohere parameter definitions
        parameters = function.get("parameters", {})
        properties = parameters.get("properties", {})
        required = parameters.get("required", [])
        
        for param_name, param_schema in properties.items():
            cohere_tool["parameter_definitions"][param_name] = {
                "description": param_schema.get("description", ""),
                "type": _convert_json_schema_type_to_cohere(param_schema.get("type", "string")),
                "required": param_name in required
            }
            
        cohere_tools.append(cohere_tool)
    
    # Default tool choice is "auto"
    tool_choice = {"type": "auto"}
    
    return cohere_tools, tool_choice, warnings


def _convert_json_schema_type_to_cohere(json_type: str) -> str:
    """Convert JSON Schema type to Cohere parameter type."""
    type_mapping = {
        "string": "str",
        "number": "float", 
        "integer": "int",
        "boolean": "bool",
        "array": "list",
        "object": "dict"
    }
    return type_mapping.get(json_type, "str")


def map_cohere_finish_reason(cohere_reason: str | None) -> str:
    """Map Cohere finish reason to AI SDK finish reason."""
    if not cohere_reason:
        return "unknown"
        
    mapping = {
        "COMPLETE": "stop",
        "MAX_TOKENS": "length", 
        "ERROR_LIMIT": "error",
        "ERROR_TOXIC": "content-filter",
        "ERROR": "error",
        "USER_CANCEL": "stop",
    }
    
    return mapping.get(cohere_reason, "unknown")