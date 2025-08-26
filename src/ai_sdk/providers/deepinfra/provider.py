"""
DeepInfra Provider implementation.
"""

from typing import Any, Dict
from ai_sdk.core.types import Provider, LanguageModel, EmbeddingModel, ImageModel
from ai_sdk.errors.base import AISDKError
from .types import DeepInfraChatModelId, DeepInfraEmbeddingModelId, DeepInfraImageModelId, DeepInfraProviderSettings
from .language_model import DeepInfraLanguageModel
from .embedding_model import DeepInfraEmbeddingModel
from .image_model import DeepInfraImageModel


class DeepInfraProvider(Provider):
    """
    DeepInfra AI provider for cost-effective access to 50+ open-source models.
    
    Supports:
    - 50+ chat models (Llama, Qwen, Mistral, CodeLlama, etc.)
    - 15+ embedding models (BGE, E5, Sentence Transformers, CLIP)
    - 8+ image generation models (FLUX, Stable Diffusion 3.5, SDXL Turbo)
    - OpenAI-compatible API for seamless integration
    - Cost-effective pricing with high performance
    """
    
    def __init__(self, settings: DeepInfraProviderSettings | None = None):
        """
        Initialize DeepInfra provider.
        
        Args:
            settings: Configuration settings for the provider.
                     If None, will use default settings with environment variables.
        """
        self.settings = settings or DeepInfraProviderSettings()
        self._provider_name = "deepinfra"
    
    @property
    def provider(self) -> str:
        return self._provider_name
    
    @property
    def name(self) -> str:
        """Name of the provider."""
        return self._provider_name
    
    def language_model(self, model_id: DeepInfraChatModelId) -> LanguageModel:
        """
        Create a DeepInfra language model for text generation.
        
        Args:
            model_id: The DeepInfra model identifier (e.g., "meta-llama/Meta-Llama-3.1-70B-Instruct")
            
        Returns:
            DeepInfraLanguageModel instance
            
        Example:
            >>> provider = DeepInfraProvider()
            >>> model = provider.language_model("meta-llama/Meta-Llama-3.1-70B-Instruct")
            >>> result = await model.generate_text(prompt)
        """
        return DeepInfraLanguageModel(model_id, self.settings)
    
    def embedding_model(self, model_id: DeepInfraEmbeddingModelId) -> EmbeddingModel:
        """
        Create a DeepInfra embedding model for text embeddings.
        
        Args:
            model_id: The DeepInfra embedding model identifier (e.g., "BAAI/bge-large-en-v1.5")
            
        Returns:
            DeepInfraEmbeddingModel instance
            
        Example:
            >>> provider = DeepInfraProvider()
            >>> model = provider.embedding_model("BAAI/bge-large-en-v1.5")
            >>> result = await model.embed(["Hello world", "How are you?"])
        """
        return DeepInfraEmbeddingModel(model_id, self.settings)
    
    def image_model(self, model_id: DeepInfraImageModelId) -> ImageModel:
        """
        Create a DeepInfra image model for image generation.
        
        Args:
            model_id: The DeepInfra image model identifier (e.g., "black-forest-labs/FLUX-1.1-pro")
            
        Returns:
            DeepInfraImageModel instance
            
        Example:
            >>> provider = DeepInfraProvider()
            >>> model = provider.image_model("black-forest-labs/FLUX-1.1-pro")
            >>> result = await model.generate_image("A beautiful sunset over mountains")
        """
        return DeepInfraImageModel(model_id, self.settings)
    
    def __call__(self, model_id: DeepInfraChatModelId) -> LanguageModel:
        """
        Convenient method to create a language model.
        
        Args:
            model_id: The DeepInfra chat model identifier
            
        Returns:
            DeepInfraLanguageModel instance
        """
        return self.language_model(model_id)
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get information about available DeepInfra models."""
        return {
            "language_models": {
                # Latest Llama 4 Models
                "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8": {
                    "description": "Latest Llama 4 Maverick model with 128E mixture-of-experts",
                    "context_length": 128000,
                    "supports_tools": True,
                    "supports_streaming": True,
                    "family": "llama-4"
                },
                "meta-llama/Llama-4-Scout-17B-16E-Instruct": {
                    "description": "Llama 4 Scout model optimized for efficiency",
                    "context_length": 128000,
                    "supports_tools": True,
                    "supports_streaming": True,
                    "family": "llama-4"
                },
                
                # Llama 3.3 Models
                "meta-llama/Llama-3.3-70B-Instruct": {
                    "description": "Latest Llama 3.3 70B with improved performance",
                    "context_length": 128000,
                    "supports_tools": True,
                    "supports_streaming": True,
                    "family": "llama-3.3"
                },
                "meta-llama/Llama-3.3-70B-Instruct-Turbo": {
                    "description": "Turbo version of Llama 3.3 70B for faster inference",
                    "context_length": 128000,
                    "supports_tools": True,
                    "supports_streaming": True,
                    "family": "llama-3.3"
                },
                
                # Llama 3.1 Models
                "meta-llama/Meta-Llama-3.1-405B-Instruct": {
                    "description": "Largest Llama 3.1 model with 405B parameters",
                    "context_length": 128000,
                    "supports_tools": True,
                    "supports_streaming": True,
                    "family": "llama-3.1"
                },
                "meta-llama/Meta-Llama-3.1-70B-Instruct": {
                    "description": "Llama 3.1 70B for high-quality generation",
                    "context_length": 128000,
                    "supports_tools": True,
                    "supports_streaming": True,
                    "family": "llama-3.1"
                },
                "meta-llama/Meta-Llama-3.1-8B-Instruct": {
                    "description": "Efficient Llama 3.1 8B model",
                    "context_length": 128000,
                    "supports_tools": True,
                    "supports_streaming": True,
                    "family": "llama-3.1"
                },
                
                # Qwen Models
                "Qwen/QwQ-32B-Preview": {
                    "description": "Qwen QwQ model with advanced reasoning capabilities",
                    "context_length": 32768,
                    "supports_tools": True,
                    "supports_streaming": True,
                    "family": "qwen"
                },
                "Qwen/Qwen2.5-Coder-32B-Instruct": {
                    "description": "Qwen 2.5 specialized for code generation",
                    "context_length": 32768,
                    "supports_tools": True,
                    "supports_streaming": True,
                    "family": "qwen-coder"
                },
                "Qwen/Qwen2.5-72B-Instruct": {
                    "description": "Large Qwen 2.5 model for high-quality generation",
                    "context_length": 32768,
                    "supports_tools": True,
                    "supports_streaming": True,
                    "family": "qwen"
                },
                
                # Vision Models
                "meta-llama/Llama-3.2-90B-Vision-Instruct": {
                    "description": "Llama 3.2 with vision capabilities, 90B parameters",
                    "context_length": 128000,
                    "supports_tools": True,
                    "supports_streaming": True,
                    "supports_vision": True,
                    "family": "llama-vision"
                },
                "meta-llama/Llama-3.2-11B-Vision-Instruct": {
                    "description": "Efficient Llama 3.2 vision model, 11B parameters",
                    "context_length": 128000,
                    "supports_tools": True,
                    "supports_streaming": True,
                    "supports_vision": True,
                    "family": "llama-vision"
                },
                
                # Specialized Models
                "deepseek-ai/DeepSeek-V3": {
                    "description": "DeepSeek V3 with advanced reasoning",
                    "context_length": 64000,
                    "supports_tools": True,
                    "supports_streaming": True,
                    "family": "deepseek"
                },
                "nvidia/Nemotron-4-340B-Instruct": {
                    "description": "NVIDIA Nemotron 4 340B for enterprise use",
                    "context_length": 4096,
                    "supports_tools": True,
                    "supports_streaming": True,
                    "family": "nemotron"
                },
                
                # Code Models
                "codellama/CodeLlama-70b-Instruct-hf": {
                    "description": "CodeLlama 70B specialized for code generation",
                    "context_length": 16384,
                    "supports_tools": True,
                    "supports_streaming": True,
                    "family": "code-llama"
                },
                "bigcode/starcoder2-15b": {
                    "description": "StarCoder2 15B for code generation",
                    "context_length": 16384,
                    "supports_tools": False,
                    "supports_streaming": True,
                    "family": "starcoder"
                }
            },
            
            "embedding_models": {
                # BGE Models (Best Performance)
                "BAAI/bge-large-en-v1.5": {
                    "description": "High-quality English embeddings, large model",
                    "dimensions": 1024,
                    "max_input_length": 512,
                    "languages": ["en"]
                },
                "BAAI/bge-base-en-v1.5": {
                    "description": "High-quality English embeddings, base model",
                    "dimensions": 768,
                    "max_input_length": 512,
                    "languages": ["en"]
                },
                "BAAI/bge-m3": {
                    "description": "Multilingual embeddings with long context support",
                    "dimensions": 1024,
                    "max_input_length": 8192,
                    "languages": ["100+ languages"]
                },
                
                # E5 Models (Multilingual)
                "intfloat/multilingual-e5-large": {
                    "description": "Large multilingual embedding model",
                    "dimensions": 1024,
                    "max_input_length": 512,
                    "languages": ["100+ languages"]
                },
                "intfloat/e5-large-v2": {
                    "description": "High-quality multilingual embeddings",
                    "dimensions": 1024,
                    "max_input_length": 512,
                    "languages": ["100+ languages"]
                },
                
                # Sentence Transformers
                "sentence-transformers/all-mpnet-base-v2": {
                    "description": "General-purpose sentence embeddings",
                    "dimensions": 768,
                    "max_input_length": 384,
                    "languages": ["en"]
                },
                "sentence-transformers/all-MiniLM-L6-v2": {
                    "description": "Lightweight, fast sentence embeddings",
                    "dimensions": 384,
                    "max_input_length": 256,
                    "languages": ["en"]
                },
                
                # CLIP Models (Multimodal)
                "sentence-transformers/clip-ViT-B-32": {
                    "description": "Multimodal text-image embeddings",
                    "dimensions": 512,
                    "max_input_length": 77,
                    "languages": ["en"],
                    "modalities": ["text", "image"]
                }
            },
            
            "image_models": {
                # FLUX Models (State-of-the-art)
                "black-forest-labs/FLUX-1.1-pro": {
                    "description": "Latest FLUX Pro model with improved quality and speed",
                    "max_resolution": "2048x2048",
                    "supports_aspect_ratios": True,
                    "quality": "highest"
                },
                "black-forest-labs/FLUX-1-schnell": {
                    "description": "FLUX Schnell for ultra-fast generation",
                    "max_resolution": "1024x1024",
                    "supports_aspect_ratios": True,
                    "quality": "high",
                    "speed": "fastest"
                },
                "black-forest-labs/FLUX-1-dev": {
                    "description": "FLUX Dev model for development and experimentation",
                    "max_resolution": "1024x1024",
                    "supports_aspect_ratios": True,
                    "quality": "high"
                },
                
                # Stable Diffusion 3.5
                "stabilityai/sd3.5": {
                    "description": "Latest Stable Diffusion 3.5 with improved quality",
                    "max_resolution": "1024x1024",
                    "supports_aspect_ratios": True,
                    "quality": "high"
                },
                "stabilityai/sd3.5-medium": {
                    "description": "SD 3.5 Medium for balanced quality and speed",
                    "max_resolution": "1024x1024",
                    "supports_aspect_ratios": True,
                    "quality": "medium-high"
                },
                
                # SDXL Turbo
                "stabilityai/sdxl-turbo": {
                    "description": "SDXL Turbo for ultra-fast generation",
                    "max_resolution": "1024x1024",
                    "supports_aspect_ratios": False,
                    "quality": "medium",
                    "speed": "fastest"
                }
            }
        }
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about this provider."""
        return {
            "name": "deepinfra",
            "description": "DeepInfra provider for cost-effective access to 50+ open-source AI models",
            "capabilities": [
                "text_generation",
                "text_embeddings",
                "image_generation",
                "streaming",
                "tool_calling",
                "json_mode",
                "vision_models",
                "code_models",
                "multimodal_embeddings"
            ],
            "supported_modalities": {
                "input": ["text", "image"],
                "output": ["text", "embeddings", "image"]
            },
            "base_url": self.settings.base_url,
            "api_compatibility": "openai",
            "cost_tier": "cost_effective",
            "model_families": [
                "llama-4", "llama-3.3", "llama-3.1", "llama-vision",
                "qwen", "qwen-coder", "deepseek", "nemotron",
                "code-llama", "starcoder", "mistral", "gemma",
                "bge", "e5", "sentence-transformers", "clip",
                "flux", "stable-diffusion", "sdxl"
            ]
        }


def create_deepinfra_provider(
    api_key: str | None = None,
    base_url: str | None = None,
    headers: Dict[str, str] | None = None,
) -> DeepInfraProvider:
    """
    Create a DeepInfra provider with custom settings.
    
    Args:
        api_key: DeepInfra API key. If None, uses DEEPINFRA_API_KEY environment variable.
        base_url: Custom base URL for API calls. Defaults to https://api.deepinfra.com/v1
        headers: Additional headers to include in requests.
        
    Returns:
        DeepInfraProvider instance
        
    Example:
        >>> provider = create_deepinfra_provider(api_key="your-api-key")
        >>> model = provider.language_model("meta-llama/Meta-Llama-3.1-70B-Instruct")
    """
    settings = DeepInfraProviderSettings()
    
    if api_key is not None:
        settings.api_key = api_key
    if base_url is not None:
        settings.base_url = base_url
    if headers is not None:
        settings.headers = headers
    
    return DeepInfraProvider(settings)


# Default provider instance
deepinfra_provider = DeepInfraProvider()