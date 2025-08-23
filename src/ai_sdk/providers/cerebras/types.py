"""
Type definitions for Cerebras provider.
"""

from typing import Any, Dict, Literal, Union
from pydantic import BaseModel, Field
import os


# Cerebras model identifiers based on https://inference-docs.cerebras.ai/introduction
CerebrasChatModelId = Union[
    # Latest Llama models optimized for Cerebras hardware
    Literal["llama3.1-8b"],      # Fast 8B parameter model
    Literal["llama3.1-70b"],     # High-performance 70B parameter model  
    Literal["llama-3.3-70b"],    # Latest Llama 3.3 70B model
    str  # Allow custom model IDs
]


class CerebrasProviderSettings(BaseModel):
    """
    Configuration settings for the Cerebras provider.
    
    Features:
    - Ultra-fast inference with specialized hardware
    - OpenAI-compatible API
    - Optimized Llama model variants
    - Competitive pricing with speed focus
    """
    
    api_key: str = Field(
        default_factory=lambda: os.getenv("CEREBRAS_API_KEY", ""),
        description="Cerebras API key. Can also be set via CEREBRAS_API_KEY environment variable."
    )
    
    base_url: str = Field(
        default="https://api.cerebras.ai/v1",
        description="Base URL for Cerebras API endpoints."
    )
    
    headers: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional headers to include in API requests."
    )
    
    timeout: float = Field(
        default=60.0,
        description="Request timeout in seconds."
    )
    
    max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts for failed requests."
    )
    
    class Config:
        extra = "forbid"


class CerebrasError(BaseModel):
    """Cerebras API error structure."""
    message: str
    type: str
    param: str
    code: str


# Model capabilities and specifications
CEREBRAS_MODEL_INFO = {
    "llama3.1-8b": {
        "description": "Llama 3.1 8B optimized for ultra-fast inference on Cerebras hardware",
        "context_length": 128000,
        "supports_streaming": True,
        "supports_tools": True,
        "supports_json_mode": True,
        "speed": "ultra_fast",
        "use_cases": [
            "real_time_chat",
            "content_generation",
            "quick_responses",
            "interactive_applications"
        ],
        "hardware_optimization": "cerebras_wse",
        "inference_speed": "~10x faster than traditional GPUs"
    },
    "llama3.1-70b": {
        "description": "Llama 3.1 70B optimized for high-performance inference on Cerebras hardware", 
        "context_length": 128000,
        "supports_streaming": True,
        "supports_tools": True,
        "supports_json_mode": True,
        "speed": "very_fast",
        "use_cases": [
            "complex_reasoning",
            "advanced_chat",
            "content_creation",
            "analytical_tasks",
            "code_generation"
        ],
        "hardware_optimization": "cerebras_wse",
        "inference_speed": "~5x faster than traditional GPUs"
    },
    "llama-3.3-70b": {
        "description": "Latest Llama 3.3 70B model optimized for Cerebras ultra-fast inference",
        "context_length": 128000,
        "supports_streaming": True, 
        "supports_tools": True,
        "supports_json_mode": True,
        "speed": "very_fast",
        "use_cases": [
            "latest_capabilities",
            "complex_reasoning", 
            "advanced_applications",
            "research_tasks",
            "sophisticated_analysis"
        ],
        "hardware_optimization": "cerebras_wse",
        "inference_speed": "~5x faster than traditional GPUs",
        "model_version": "latest"
    }
}


def get_model_info(model_id: str) -> Dict[str, Any]:
    """Get information about a specific Cerebras model."""
    return CEREBRAS_MODEL_INFO.get(model_id, {
        "description": f"Custom Cerebras model: {model_id}",
        "context_length": 128000,
        "supports_streaming": True,
        "supports_tools": True,
        "supports_json_mode": True,
        "speed": "fast",
        "hardware_optimization": "cerebras_wse"
    })


def is_supported_model(model_id: str) -> bool:
    """Check if a model is officially supported by Cerebras."""
    return model_id in CEREBRAS_MODEL_INFO