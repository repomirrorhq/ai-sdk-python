"""Utility functions for Mistral provider."""

import json
from typing import List, Dict, Any, Union

from ...providers.types import Message, Content, TextContent, ImageContent, ToolCallContent, ToolResultContent, FinishReason
from ...providers.openai.utils import (
    convert_to_openai_messages as _convert_to_openai_messages,
    convert_to_openai_tools as _convert_to_openai_tools
)


def convert_to_mistral_messages(messages: List[Message]) -> List[Message]:
    """Convert AI SDK messages to Mistral format.
    
    Mistral API is OpenAI-compatible, so we can reuse OpenAI conversion logic.
    """
    return _convert_to_openai_messages(messages)


def convert_to_mistral_tools(tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert AI SDK tools to Mistral tool format.
    
    Mistral API is OpenAI-compatible, so we can reuse OpenAI conversion logic.
    """
    return _convert_to_openai_tools(tools)


def convert_mistral_finish_reason(mistral_reason: str) -> FinishReason:
    """Map Mistral finish reason to AI SDK finish reason."""
    mapping = {
        "stop": "stop",
        "length": "length",
        "tool_calls": "tool_calls",
        "content_filter": "content_filter",
        "model_length": "length",
    }
    return mapping.get(mistral_reason, "stop")


def get_model_context_window(model_id: str) -> int:
    """Get the context window size for a Mistral model."""
    context_windows = {
        # Premier models
        "mistral-large-latest": 128000,
        "mistral-large-2411": 128000,
        "mistral-large-2407": 128000,
        "mistral-medium-latest": 32000,
        "mistral-medium-2508": 32000,
        "mistral-medium-2505": 32000,
        "mistral-small-latest": 32000,
        "ministral-3b-latest": 128000,
        "ministral-8b-latest": 128000,
        "pixtral-large-latest": 128000,
        
        # Reasoning models
        "magistral-small-2507": 32000,
        "magistral-medium-2507": 32000,
        "magistral-small-2506": 32000,
        "magistral-medium-2506": 32000,
        
        # Free models
        "pixtral-12b-2409": 128000,
        
        # Legacy open source models
        "open-mistral-7b": 32000,
        "open-mixtral-8x7b": 32000,
        "open-mixtral-8x22b": 64000,
    }
    return context_windows.get(model_id, 32000)  # Default to 32K


def get_model_max_tokens(model_id: str) -> int:
    """Get the default max tokens for a Mistral model."""
    max_tokens = {
        # Premier models
        "mistral-large-latest": 8192,
        "mistral-large-2411": 8192,
        "mistral-large-2407": 8192,
        "mistral-medium-latest": 8192,
        "mistral-medium-2508": 8192,
        "mistral-medium-2505": 8192,
        "mistral-small-latest": 8192,
        "ministral-3b-latest": 8192,
        "ministral-8b-latest": 8192,
        "pixtral-large-latest": 8192,
        
        # Reasoning models
        "magistral-small-2507": 8192,
        "magistral-medium-2507": 8192,
        "magistral-small-2506": 8192,
        "magistral-medium-2506": 8192,
        
        # Free models
        "pixtral-12b-2409": 8192,
        
        # Legacy open source models
        "open-mistral-7b": 8192,
        "open-mixtral-8x7b": 8192,
        "open-mixtral-8x22b": 8192,
    }
    return max_tokens.get(model_id, 8192)  # Default to 8K


def supports_tool_calling(model_id: str) -> bool:
    """Check if a Mistral model supports tool calling."""
    # Most Mistral models support tool calling, except some legacy models
    non_tool_models = {
        "open-mistral-7b",  # Legacy model without tool calling
    }
    return model_id not in non_tool_models


def supports_vision(model_id: str) -> bool:
    """Check if a Mistral model supports vision (image inputs)."""
    vision_models = {
        "pixtral-large-latest",
        "pixtral-12b-2409",
    }
    return model_id in vision_models


def is_reasoning_model(model_id: str) -> bool:
    """Check if a Mistral model is a reasoning model."""
    return model_id.startswith("magistral-")


def get_model_family(model_id: str) -> str:
    """Get the model family for a Mistral model."""
    if model_id.startswith("magistral-"):
        return "reasoning"
    elif model_id.startswith("pixtral-"):
        return "vision"
    elif model_id.startswith("ministral-"):
        return "small"
    elif model_id.startswith("mistral-large"):
        return "large"
    elif model_id.startswith("mistral-medium"):
        return "medium"
    elif model_id.startswith("mistral-small"):
        return "small"
    elif model_id.startswith("open-"):
        return "open-source"
    else:
        return "unknown"