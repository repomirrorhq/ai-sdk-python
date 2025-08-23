"""
Type definitions for Together AI Provider
"""

from typing import Optional, Dict
from pydantic import BaseModel, Field
from typing_extensions import TypeAlias

# Model ID type aliases for popular Together AI models
TogetherAIChatModelId: TypeAlias = str
TogetherAICompletionModelId: TypeAlias = str
TogetherAIEmbeddingModelId: TypeAlias = str
TogetherAIImageModelId: TypeAlias = str

# Popular Together AI model IDs
TOGETHER_CHAT_MODELS = {
    # Meta LLaMA models
    "meta-llama/Llama-3.3-70B-Instruct-Turbo": "meta-llama/Llama-3.3-70B-Instruct-Turbo",
    "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo": "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
    "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo": "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
    "meta-llama/Llama-3.2-3B-Instruct-Turbo": "meta-llama/Llama-3.2-3B-Instruct-Turbo",
    "meta-llama/Llama-3.2-1B-Instruct-Turbo": "meta-llama/Llama-3.2-1B-Instruct-Turbo",
    "meta-llama/Llama-3.1-70B-Instruct-Turbo": "meta-llama/Llama-3.1-70B-Instruct-Turbo",
    "meta-llama/Llama-3.1-8B-Instruct-Turbo": "meta-llama/Llama-3.1-8B-Instruct-Turbo",
    
    # Mistral models
    "mistralai/Mistral-7B-Instruct-v0.3": "mistralai/Mistral-7B-Instruct-v0.3",
    "mistralai/Mixtral-8x7B-Instruct-v0.1": "mistralai/Mixtral-8x7B-Instruct-v0.1",
    "mistralai/Mixtral-8x22B-Instruct-v0.1": "mistralai/Mixtral-8x22B-Instruct-v0.1",
    
    # Google models
    "google/gemma-2-9b-it": "google/gemma-2-9b-it",
    "google/gemma-2-27b-it": "google/gemma-2-27b-it",
    
    # Qwen models
    "Qwen/Qwen2.5-7B-Instruct-Turbo": "Qwen/Qwen2.5-7B-Instruct-Turbo",
    "Qwen/Qwen2.5-72B-Instruct-Turbo": "Qwen/Qwen2.5-72B-Instruct-Turbo",
}

TOGETHER_EMBEDDING_MODELS = {
    "togethercomputer/m2-bert-80M-8k-retrieval": "togethercomputer/m2-bert-80M-8k-retrieval",
    "togethercomputer/m2-bert-80M-32k-retrieval": "togethercomputer/m2-bert-80M-32k-retrieval",
    "WhereIsAI/UAE-Large-V1": "WhereIsAI/UAE-Large-V1",
    "BAAI/bge-large-en-v1.5": "BAAI/bge-large-en-v1.5",
    "BAAI/bge-base-en-v1.5": "BAAI/bge-base-en-v1.5",
}

TOGETHER_IMAGE_MODELS = {
    "black-forest-labs/FLUX.1-schnell-Free": "black-forest-labs/FLUX.1-schnell-Free",
    "black-forest-labs/FLUX.1-schnell": "black-forest-labs/FLUX.1-schnell",
    "stabilityai/stable-diffusion-xl-base-1.0": "stabilityai/stable-diffusion-xl-base-1.0",
    "stabilityai/stable-diffusion-2-1": "stabilityai/stable-diffusion-2-1",
    "prompthero/openjourney": "prompthero/openjourney",
}


class TogetherAIProviderSettings(BaseModel):
    """Settings for configuring the Together AI Provider"""
    
    api_key: Optional[str] = Field(
        default=None,
        description="Together AI API key (or set TOGETHER_AI_API_KEY environment variable)"
    )
    
    base_url: Optional[str] = Field(
        default="https://api.together.xyz/v1",
        description="Base URL for Together AI API calls"
    )
    
    headers: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="Custom headers to include in requests"
    )
    
    query_params: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="Custom query parameters to include in request URLs"
    )
    
    fetch: Optional[callable] = Field(
        default=None,
        description="Custom fetch implementation for testing/middleware"
    )
    
    include_usage: bool = Field(
        default=True,
        description="Include usage information in responses"
    )
    
    class Config:
        extra = "forbid"