"""
Type definitions for Fireworks provider.
"""

from typing import Any, Dict, Literal, Union
from pydantic import BaseModel, Field
import os


# Fireworks chat model identifiers based on https://docs.fireworks.ai/docs/serverless-models#chat-models
FireworksChatModelId = Union[
    # Latest models
    Literal["accounts/fireworks/models/deepseek-v3"],
    Literal["accounts/fireworks/models/llama-v3p3-70b-instruct"],
    Literal["accounts/fireworks/models/llama-v3p2-3b-instruct"],
    Literal["accounts/fireworks/models/llama-v3p1-405b-instruct"],
    Literal["accounts/fireworks/models/llama-v3p1-8b-instruct"],
    
    # Mixtral models
    Literal["accounts/fireworks/models/mixtral-8x7b-instruct"],
    Literal["accounts/fireworks/models/mixtral-8x22b-instruct"],
    Literal["accounts/fireworks/models/mixtral-8x7b-instruct-hf"],
    
    # Qwen models
    Literal["accounts/fireworks/models/qwen2p5-coder-32b-instruct"],
    Literal["accounts/fireworks/models/qwen2p5-72b-instruct"],
    Literal["accounts/fireworks/models/qwen-qwq-32b-preview"],
    Literal["accounts/fireworks/models/qwen2-vl-72b-instruct"],
    Literal["accounts/fireworks/models/qwq-32b"],
    
    # Other models
    Literal["accounts/fireworks/models/llama-v3p2-11b-vision-instruct"],
    Literal["accounts/fireworks/models/yi-large"],
    Literal["accounts/fireworks/models/kimi-k2-instruct"],
    
    str  # Allow custom model IDs
]


# Fireworks embedding model identifiers
FireworksEmbeddingModelId = Union[
    Literal["nomic-ai/nomic-embed-text-v1.5"],
    str  # Allow custom model IDs
]


class FireworksProviderSettings(BaseModel):
    """
    Configuration settings for the Fireworks provider.
    
    Features:
    - High-performance model hosting platform
    - Wide variety of open-source models
    - Optimized inference infrastructure
    - Competitive pricing and speed
    """
    
    api_key: str = Field(
        default_factory=lambda: os.getenv("FIREWORKS_API_KEY", ""),
        description="Fireworks API key. Can also be set via FIREWORKS_API_KEY environment variable."
    )
    
    base_url: str = Field(
        default="https://api.fireworks.ai/inference/v1",
        description="Base URL for Fireworks API endpoints."
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


class FireworksError(BaseModel):
    """Fireworks API error structure."""
    error: str


# Model capabilities and specifications
FIREWORKS_MODEL_INFO = {
    "accounts/fireworks/models/deepseek-v3": {
        "description": "DeepSeek V3 - Advanced reasoning and coding capabilities",
        "context_length": 65536,
        "supports_streaming": True,
        "supports_tools": True,
        "supports_json_mode": True,
        "model_type": "chat",
        "use_cases": ["advanced_reasoning", "coding", "complex_analysis"],
        "provider_optimization": "fireworks_hosted"
    },
    "accounts/fireworks/models/llama-v3p3-70b-instruct": {
        "description": "Llama 3.3 70B Instruct - Latest large language model",
        "context_length": 128000,
        "supports_streaming": True,
        "supports_tools": True,
        "supports_json_mode": True,
        "model_type": "chat",
        "use_cases": ["general_purpose", "complex_reasoning", "content_creation"],
        "provider_optimization": "fireworks_optimized"
    },
    "accounts/fireworks/models/llama-v3p2-3b-instruct": {
        "description": "Llama 3.2 3B Instruct - Efficient small model",
        "context_length": 128000,
        "supports_streaming": True,
        "supports_tools": True,
        "supports_json_mode": True,
        "model_type": "chat",
        "use_cases": ["fast_responses", "cost_effective", "simple_tasks"],
        "provider_optimization": "fireworks_optimized"
    },
    "accounts/fireworks/models/llama-v3p1-405b-instruct": {
        "description": "Llama 3.1 405B Instruct - Massive frontier model",
        "context_length": 128000,
        "supports_streaming": True,
        "supports_tools": True,
        "supports_json_mode": True,
        "model_type": "chat",
        "use_cases": ["frontier_capabilities", "research", "complex_reasoning"],
        "provider_optimization": "fireworks_optimized"
    },
    "accounts/fireworks/models/mixtral-8x7b-instruct": {
        "description": "Mixtral 8x7B - Efficient mixture of experts model",
        "context_length": 32768,
        "supports_streaming": True,
        "supports_tools": True,
        "supports_json_mode": True,
        "model_type": "chat",
        "use_cases": ["efficient_inference", "multilingual", "general_purpose"],
        "provider_optimization": "fireworks_optimized"
    },
    "accounts/fireworks/models/qwen2p5-coder-32b-instruct": {
        "description": "Qwen 2.5 Coder 32B - Specialized coding model",
        "context_length": 131072,
        "supports_streaming": True,
        "supports_tools": True,
        "supports_json_mode": True,
        "model_type": "chat",
        "use_cases": ["code_generation", "programming", "software_development"],
        "provider_optimization": "fireworks_optimized"
    },
    "accounts/fireworks/models/qwen2-vl-72b-instruct": {
        "description": "Qwen 2 VL 72B - Multimodal vision-language model",
        "context_length": 32768,
        "supports_streaming": True,
        "supports_tools": True,
        "supports_json_mode": True,
        "supports_vision": True,
        "model_type": "chat",
        "use_cases": ["multimodal", "vision_tasks", "image_analysis"],
        "provider_optimization": "fireworks_optimized"
    },
    "nomic-ai/nomic-embed-text-v1.5": {
        "description": "Nomic Embed Text v1.5 - High-quality text embeddings",
        "dimensions": 768,
        "max_input_length": 8192,
        "model_type": "embedding",
        "use_cases": ["text_embeddings", "semantic_search", "similarity"],
        "provider_optimization": "fireworks_optimized"
    }
}


def get_model_info(model_id: str) -> Dict[str, Any]:
    """Get information about a specific Fireworks model."""
    return FIREWORKS_MODEL_INFO.get(model_id, {
        "description": f"Custom Fireworks model: {model_id}",
        "context_length": 32768,
        "supports_streaming": True,
        "supports_tools": True,
        "supports_json_mode": True,
        "model_type": "chat",
        "provider_optimization": "fireworks_hosted"
    })


def is_supported_model(model_id: str) -> bool:
    """Check if a model is officially supported by Fireworks."""
    return model_id in FIREWORKS_MODEL_INFO


def is_vision_model(model_id: str) -> bool:
    """Check if a model supports vision/multimodal capabilities."""
    model_info = FIREWORKS_MODEL_INFO.get(model_id, {})
    return model_info.get("supports_vision", False)


def is_embedding_model(model_id: str) -> bool:
    """Check if a model is an embedding model."""
    model_info = FIREWORKS_MODEL_INFO.get(model_id, {})
    return model_info.get("model_type") == "embedding"