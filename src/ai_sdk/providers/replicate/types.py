"""
Type definitions for Replicate provider.
"""

from typing import Any, Dict, Literal, Union
from pydantic import BaseModel, Field
import os


# Replicate language model identifiers - popular models on the platform
ReplicateLanguageModelId = Union[
    # Meta Llama models
    Literal["meta/llama-2-70b-chat"],
    Literal["meta/llama-2-13b-chat"], 
    Literal["meta/llama-2-7b-chat"],
    Literal["meta/llama-3.1-405b-instruct"],
    Literal["meta/llama-3.1-70b-instruct"],
    Literal["meta/llama-3.1-8b-instruct"],
    Literal["meta/llama-3.2-90b-vision-instruct"],
    Literal["meta/llama-3.2-11b-vision-instruct"],
    Literal["meta/llama-3.2-3b-instruct"],
    Literal["meta/llama-3.2-1b-instruct"],
    
    # Code-specialized models
    Literal["meta/codellama-34b-instruct"],
    Literal["meta/codellama-13b-instruct"],
    Literal["meta/codellama-7b-instruct"],
    
    # Mistral models
    Literal["mistralai/mistral-7b-instruct-v0.2"],
    Literal["mistralai/mixtral-8x7b-instruct-v0.1"],
    Literal["mistralai/mixtral-8x22b-instruct-v0.1"],
    
    # Other popular models
    Literal["microsoft/wizardcoder-15b"],
    Literal["huggingfaceh4/zephyr-7b-beta"],
    Literal["togethercomputer/redpajama-incite-7b-chat"],
    Literal["01-ai/yi-34b-chat"],
    
    str  # Allow any model ID from the Replicate marketplace
]


# Replicate image model identifiers
ReplicateImageModelId = Union[
    # Flux models (Black Forest Labs)
    Literal["black-forest-labs/flux-1.1-pro"],
    Literal["black-forest-labs/flux-1.1-pro-ultra"],
    Literal["black-forest-labs/flux-dev"],
    Literal["black-forest-labs/flux-pro"], 
    Literal["black-forest-labs/flux-schnell"],
    
    # Stable Diffusion models
    Literal["stability-ai/stable-diffusion-3.5-large"],
    Literal["stability-ai/stable-diffusion-3.5-large-turbo"],
    Literal["stability-ai/stable-diffusion-3.5-medium"],
    
    # SDXL variants
    Literal["bytedance/sdxl-lightning-4step"],
    Literal["lucataco/dreamshaper-xl-turbo"],
    Literal["playgroundai/playground-v2.5-1024px-aesthetic"],
    
    # Ideogram models
    Literal["ideogram-ai/ideogram-v2"],
    Literal["ideogram-ai/ideogram-v2-turbo"],
    
    # Luma models
    Literal["luma/photon"],
    Literal["luma/photon-flash"],
    
    # Other specialized models
    Literal["recraft-ai/recraft-v3"],
    Literal["recraft-ai/recraft-v3-svg"],
    Literal["nvidia/sana"],
    Literal["fofr/aura-flow"],
    Literal["fofr/sdxl-emoji"],
    
    str  # Allow any image model ID from Replicate
]


class ReplicateProviderSettings(BaseModel):
    """
    Configuration settings for the Replicate provider.
    
    Features:
    - Access to thousands of open-source models
    - Language models, image generation, and specialized AI tasks
    - Community-driven model marketplace
    - Flexible deployment and scaling
    """
    
    api_token: str = Field(
        default_factory=lambda: os.getenv("REPLICATE_API_TOKEN", ""),
        description="Replicate API token. Can also be set via REPLICATE_API_TOKEN environment variable."
    )
    
    base_url: str = Field(
        default="https://api.replicate.com/v1",
        description="Base URL for Replicate API endpoints."
    )
    
    headers: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional headers to include in API requests."
    )
    
    timeout: float = Field(
        default=300.0,  # Longer timeout for potentially slow model predictions
        description="Request timeout in seconds."
    )
    
    max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts for failed requests."
    )
    
    # Replicate-specific settings
    webhook_url: str = Field(
        default="",
        description="Optional webhook URL for async prediction notifications."
    )
    
    wait_for_completion: bool = Field(
        default=True,
        description="Whether to wait for predictions to complete or return immediately."
    )
    
    class Config:
        extra = "forbid"


class ReplicateError(BaseModel):
    """Replicate API error structure."""
    detail: str
    status: int


# Model information for popular Replicate models
REPLICATE_MODEL_INFO = {
    # Llama models
    "meta/llama-3.1-405b-instruct": {
        "description": "Llama 3.1 405B - Meta's largest and most capable model",
        "context_length": 128000,
        "supports_streaming": True,
        "model_type": "language",
        "parameters": "405B",
        "use_cases": ["complex_reasoning", "advanced_analysis", "research"],
        "provider": "meta"
    },
    "meta/llama-3.1-70b-instruct": {
        "description": "Llama 3.1 70B - High-performance balanced model", 
        "context_length": 128000,
        "supports_streaming": True,
        "model_type": "language",
        "parameters": "70B",
        "use_cases": ["general_chat", "reasoning", "content_creation"],
        "provider": "meta"
    },
    "meta/llama-3.2-90b-vision-instruct": {
        "description": "Llama 3.2 90B Vision - Multimodal vision-language model",
        "context_length": 128000,
        "supports_streaming": True,
        "supports_vision": True,
        "model_type": "language",
        "parameters": "90B",
        "use_cases": ["multimodal", "vision_tasks", "image_analysis"],
        "provider": "meta"
    },
    "meta/codellama-34b-instruct": {
        "description": "Code Llama 34B - Specialized code generation model",
        "context_length": 16384,
        "supports_streaming": True,
        "model_type": "language",
        "parameters": "34B",
        "use_cases": ["code_generation", "programming", "software_development"],
        "provider": "meta"
    },
    
    # Mistral models
    "mistralai/mixtral-8x7b-instruct-v0.1": {
        "description": "Mixtral 8x7B - Efficient mixture of experts model",
        "context_length": 32768,
        "supports_streaming": True,
        "model_type": "language",
        "parameters": "8x7B MoE",
        "use_cases": ["efficient_inference", "multilingual", "general_purpose"],
        "provider": "mistralai"
    },
    
    # Image models
    "black-forest-labs/flux-1.1-pro": {
        "description": "FLUX.1.1 [pro] - State-of-the-art image generation",
        "model_type": "image",
        "max_resolution": "2048x2048",
        "use_cases": ["high_quality_images", "artistic_generation", "professional_content"],
        "provider": "black-forest-labs"
    },
    "stability-ai/stable-diffusion-3.5-large": {
        "description": "Stable Diffusion 3.5 Large - Advanced image generation",
        "model_type": "image", 
        "max_resolution": "1536x1536",
        "use_cases": ["image_generation", "creative_content", "artistic_work"],
        "provider": "stability-ai"
    },
    "ideogram-ai/ideogram-v2": {
        "description": "Ideogram V2 - Text-to-image with excellent typography",
        "model_type": "image",
        "max_resolution": "1024x1024",
        "use_cases": ["typography", "logos", "text_in_images"],
        "provider": "ideogram-ai"
    }
}


def get_model_info(model_id: str) -> Dict[str, Any]:
    """Get information about a specific Replicate model."""
    return REPLICATE_MODEL_INFO.get(model_id, {
        "description": f"Custom Replicate model: {model_id}",
        "model_type": "language",
        "use_cases": ["general_purpose"],
        "provider": model_id.split('/')[0] if '/' in model_id else "community"
    })


def is_vision_model(model_id: str) -> bool:
    """Check if a model supports vision/multimodal capabilities."""
    model_info = REPLICATE_MODEL_INFO.get(model_id, {})
    return model_info.get("supports_vision", False) or "vision" in model_id.lower()


def is_image_model(model_id: str) -> bool:
    """Check if a model is for image generation."""
    model_info = REPLICATE_MODEL_INFO.get(model_id, {})
    return model_info.get("model_type") == "image"


def is_code_model(model_id: str) -> bool:
    """Check if a model is specialized for code generation."""
    return "code" in model_id.lower() or "wizard" in model_id.lower()


def get_model_provider(model_id: str) -> str:
    """Extract the provider/organization from a model ID."""
    if '/' in model_id:
        return model_id.split('/')[0]
    return "community"