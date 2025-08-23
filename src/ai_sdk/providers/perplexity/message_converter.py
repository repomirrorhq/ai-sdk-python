"""
Message conversion utilities for Perplexity provider.
Converts AI SDK messages to Perplexity-compatible format.
"""

from typing import List, Tuple
from ai_sdk.core.types import (
    ChatPrompt, 
    SystemMessage, 
    UserMessage, 
    AssistantMessage,
    ToolMessage,
    ContentPart,
    TextContentPart,
    ImageContentPart,
    AudioContentPart
)
from .types import PerplexityMessage


def convert_to_perplexity_messages(
    prompt: ChatPrompt,
) -> Tuple[List[PerplexityMessage], List[str]]:
    """
    Convert AI SDK ChatPrompt to Perplexity messages format.
    
    Returns:
        - messages: List of Perplexity-formatted messages
        - warnings: List of conversion warnings
    """
    messages: List[PerplexityMessage] = []
    warnings: List[str] = []
    
    for message in prompt.messages:
        if isinstance(message, SystemMessage):
            perplexity_msg = PerplexityMessage(
                role="system",
                content=message.content
            )
            messages.append(perplexity_msg)
            
        elif isinstance(message, UserMessage):
            content = _convert_content_parts(message.content, warnings)
            perplexity_msg = PerplexityMessage(
                role="user", 
                content=content
            )
            messages.append(perplexity_msg)
            
        elif isinstance(message, AssistantMessage):
            # Perplexity doesn't support tool calls in the same way as OpenAI
            # We'll include tool call information in the content if present
            content = message.content or ""
            
            if message.tool_calls:
                warnings.append("Tool calls in assistant messages are not directly supported by Perplexity. Tool call information was added to message content.")
                
                for tool_call in message.tool_calls:
                    content += f"\n[Tool Call: {tool_call.name}({tool_call.arguments})]"
            
            perplexity_msg = PerplexityMessage(
                role="assistant",
                content=content
            )
            messages.append(perplexity_msg)
            
        elif isinstance(message, ToolMessage):
            # Perplexity handles tool results differently - they're integrated into search
            # We'll convert tool results to user messages with context
            warnings.append("Tool messages are not directly supported by Perplexity. Tool result was converted to user message.")
            
            content = f"[Tool Result from {message.tool_call_id}]: {message.content}"
            perplexity_msg = PerplexityMessage(
                role="user",
                content=str(content)
            )
            messages.append(perplexity_msg)
            
        else:
            warnings.append(f"Unknown message type: {type(message)}")
    
    return messages, warnings


def _convert_content_parts(
    content: str | List[ContentPart], 
    warnings: List[str]
) -> str:
    """
    Convert content parts to string format for Perplexity.
    Perplexity only supports text content.
    """
    if isinstance(content, str):
        return content
        
    text_parts = []
    
    for part in content:
        if isinstance(part, TextContentPart):
            text_parts.append(part.text)
            
        elif isinstance(part, ImageContentPart):
            # Perplexity doesn't support direct image content
            warnings.append("Image content is not supported in Perplexity messages. Image content was skipped.")
            
        elif isinstance(part, AudioContentPart):
            # Perplexity doesn't support audio content
            warnings.append("Audio content is not supported in Perplexity messages. Audio content was skipped.")
            
        else:
            warnings.append(f"Unknown content part type: {type(part)}")
    
    return " ".join(text_parts) if text_parts else ""


def map_perplexity_finish_reason(perplexity_reason: str | None) -> str:
    """Map Perplexity finish reason to AI SDK finish reason."""
    if not perplexity_reason:
        return "unknown"
        
    mapping = {
        "stop": "stop",
        "length": "length", 
        "error": "error",
        "cancelled": "stop",
    }
    
    return mapping.get(perplexity_reason, "unknown")


def prepare_search_parameters(options: dict | None) -> dict:
    """
    Prepare Perplexity-specific search parameters.
    
    Args:
        options: Provider-specific options that may contain search parameters
        
    Returns:
        Dictionary with Perplexity search parameters
    """
    search_params = {
        "return_citations": True,  # Always return citations for transparency
        "return_related_questions": False,  # Can be enabled by user
    }
    
    if not options:
        return search_params
    
    # Extract Perplexity-specific parameters
    if "search_domain_filter" in options:
        search_params["search_domain_filter"] = options["search_domain_filter"]
        
    if "search_recency_filter" in options:
        search_params["search_recency_filter"] = options["search_recency_filter"]
        
    if "return_related_questions" in options:
        search_params["return_related_questions"] = options["return_related_questions"]
        
    if "return_citations" in options:
        search_params["return_citations"] = options["return_citations"]
    
    return search_params