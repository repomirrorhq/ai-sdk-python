"""OpenAI reasoning model configurations and utilities."""

from __future__ import annotations

from typing import Dict, List, Optional, Set

# Reasoning models that have special parameter restrictions
REASONING_MODELS: Set[str] = {
    "o1-mini",
    "o1-mini-2024-09-12", 
    "o1-preview",
    "o1-preview-2024-09-12",
    "o1",
    "o1-2024-12-17",
}

# System message modes for reasoning models
REASONING_MODEL_CONFIG: Dict[str, Dict[str, str]] = {
    "o1-mini": {
        "system_message_mode": "remove",
    },
    "o1-mini-2024-09-12": {
        "system_message_mode": "remove",
    },
    "o1-preview": {
        "system_message_mode": "remove", 
    },
    "o1-preview-2024-09-12": {
        "system_message_mode": "remove",
    },
    "o1": {
        "system_message_mode": "developer",
    },
    "o1-2024-12-17": {
        "system_message_mode": "developer",
    },
}

# Parameters that are not supported by reasoning models
UNSUPPORTED_REASONING_PARAMS = {
    "temperature",
    "top_p", 
    "frequency_penalty",
    "presence_penalty",
    "logit_bias",
    "logprobs",
    "top_logprobs",
    "response_format",  # Some reasoning models don't support structured output
}


def is_reasoning_model(model_id: str) -> bool:
    """Check if a model is a reasoning model.
    
    Args:
        model_id: OpenAI model identifier
        
    Returns:
        True if the model is a reasoning model, False otherwise
    """
    return model_id in REASONING_MODELS


def get_system_message_mode(model_id: str) -> str:
    """Get the system message mode for a reasoning model.
    
    Args:
        model_id: OpenAI model identifier
        
    Returns:
        System message mode: 'remove', 'developer', or 'system' (default)
    """
    if not is_reasoning_model(model_id):
        return "system"
        
    return REASONING_MODEL_CONFIG.get(model_id, {}).get(
        "system_message_mode", "developer"
    )


def filter_unsupported_params(
    model_id: str, 
    params: Dict[str, any]
) -> tuple[Dict[str, any], List[str]]:
    """Filter out parameters not supported by reasoning models.
    
    Args:
        model_id: OpenAI model identifier
        params: Request parameters dictionary
        
    Returns:
        Tuple of (filtered_params, list_of_removed_params)
    """
    if not is_reasoning_model(model_id):
        return params, []
        
    filtered_params = params.copy()
    removed_params = []
    
    for param in UNSUPPORTED_REASONING_PARAMS:
        if param in filtered_params and filtered_params[param] is not None:
            del filtered_params[param]
            removed_params.append(param)
    
    # Special handling for max_tokens -> max_completion_tokens
    if "max_tokens" in filtered_params:
        if "max_completion_tokens" not in filtered_params:
            filtered_params["max_completion_tokens"] = filtered_params["max_tokens"]
        del filtered_params["max_tokens"]
        removed_params.append("max_tokens (converted to max_completion_tokens)")
    
    return filtered_params, removed_params


def process_reasoning_messages(
    model_id: str,
    messages: List[Dict[str, any]]
) -> List[Dict[str, any]]:
    """Process messages for reasoning models.
    
    Some reasoning models require special handling of system messages.
    
    Args:
        model_id: OpenAI model identifier  
        messages: List of message dictionaries
        
    Returns:
        Processed messages list
    """
    if not is_reasoning_model(model_id):
        return messages
        
    system_mode = get_system_message_mode(model_id)
    
    if system_mode == "remove":
        # Remove system messages entirely
        return [msg for msg in messages if msg.get("role") != "system"]
    elif system_mode == "developer":
        # Convert system messages to developer messages
        processed = []
        for msg in messages:
            if msg.get("role") == "system":
                processed.append({
                    **msg,
                    "role": "developer"
                })
            else:
                processed.append(msg)
        return processed
    
    # Default: keep system messages as-is
    return messages


class ReasoningModelWarning:
    """Warning for reasoning model parameter usage."""
    
    def __init__(self, parameter: str, reason: str):
        self.parameter = parameter
        self.reason = reason
        
    def __str__(self) -> str:
        return f"Parameter '{self.parameter}' is not supported: {self.reason}"


def get_reasoning_warnings(
    model_id: str, 
    removed_params: List[str]
) -> List[ReasoningModelWarning]:
    """Generate warnings for removed reasoning model parameters.
    
    Args:
        model_id: OpenAI model identifier
        removed_params: List of parameters that were removed
        
    Returns:
        List of warning objects
    """
    if not is_reasoning_model(model_id):
        return []
        
    warnings = []
    for param in removed_params:
        if param == "temperature":
            warnings.append(ReasoningModelWarning(
                param, "temperature is not supported for reasoning models"
            ))
        elif param == "top_p":
            warnings.append(ReasoningModelWarning(
                param, "top_p is not supported for reasoning models"
            ))
        elif param in ["frequency_penalty", "presence_penalty"]:
            warnings.append(ReasoningModelWarning(
                param, f"{param} is not supported for reasoning models"
            ))
        else:
            warnings.append(ReasoningModelWarning(
                param, f"{param} is not supported for reasoning models"
            ))
            
    return warnings