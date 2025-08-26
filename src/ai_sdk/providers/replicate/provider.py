"""
Replicate Provider implementation.
"""

from typing import Any, Dict
from ai_sdk.core.types import Provider, LanguageModel, ImageModel  
from ai_sdk.errors.base import AISDKError
from .types import (
    ReplicateLanguageModelId,
    ReplicateImageModelId, 
    ReplicateProviderSettings,
    is_image_model,
    get_model_info,
    REPLICATE_MODEL_INFO
)


class ReplicateProvider(Provider):
    """
    Replicate AI provider for accessing thousands of open-source models.
    
    Features:
    - Access to comprehensive model marketplace
    - Language models (Llama, Mistral, CodeLlama, etc.)
    - Image generation models (FLUX, Stable Diffusion, etc.)
    - Community-driven model ecosystem
    - Flexible deployment and scaling
    - Support for custom and fine-tuned models
    """
    
    def __init__(self, settings: ReplicateProviderSettings | None = None):
        """
        Initialize Replicate provider.
        
        Args:
            settings: Configuration settings for the provider.
                     If None, will use default settings with environment variables.
        """
        self.settings = settings or ReplicateProviderSettings()
        self._provider_name = "replicate"
    
    @property
    def provider(self) -> str:
        return self._provider_name
    
    @property
    def name(self) -> str:
        """Name of the provider."""
        return self._provider_name
    
    def language_model(self, model_id: ReplicateLanguageModelId) -> LanguageModel:
        """
        Create a Replicate language model for text generation.
        
        Args:
            model_id: The Replicate model identifier (e.g., "meta/llama-3.1-70b-instruct")
            
        Returns:
            ReplicateLanguageModel instance
            
        Example:
            >>> provider = ReplicateProvider()
            >>> model = provider.language_model("meta/llama-3.1-70b-instruct")
            >>> result = await model.generate_text(prompt)
        """
        if is_image_model(model_id):
            raise AISDKError(f"Model '{model_id}' is an image generation model. Use image_model() method instead.")
        
        from .language_model import ReplicateLanguageModel
        return ReplicateLanguageModel(model_id, self.settings)
    
    def image_model(self, model_id: ReplicateImageModelId) -> ImageModel:
        """
        Create a Replicate image generation model.
        
        Args:
            model_id: The Replicate image model identifier (e.g., "black-forest-labs/flux-1.1-pro")
            
        Returns:
            ReplicateImageModel instance
        """
        from .image_model import ReplicateImageModel
        return ReplicateImageModel(model_id, self.settings)
    
    def embedding_model(self, model_id: str):
        """
        Replicate does not currently provide dedicated embedding models.
        Use other providers like OpenAI, Cohere, or Fireworks for embeddings.
        """
        raise AISDKError(f"Replicate does not provide dedicated embedding models. Model '{model_id}' is not available.")
    
    def __call__(self, model_id: ReplicateLanguageModelId) -> LanguageModel:
        """
        Convenient method to create a language model.
        
        Args:
            model_id: The Replicate language model identifier
            
        Returns:
            ReplicateLanguageModel instance
        """
        return self.language_model(model_id)
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get information about popular Replicate models."""
        
        language_models = {}
        image_models = {}
        
        for model_id, info in REPLICATE_MODEL_INFO.items():
            model_type = info.get("model_type", "language")
            
            if model_type == "image":
                image_models[model_id] = info
            else:
                language_models[model_id] = info
        
        return {
            "language_models": language_models,
            "image_models": image_models,
            "total_featured_models": len(REPLICATE_MODEL_INFO),
            "marketplace_note": "Thousands more models available on Replicate marketplace",
            "model_categories": {
                "meta_llama": [k for k in REPLICATE_MODEL_INFO.keys() if k.startswith("meta/llama")],
                "code_models": [k for k in REPLICATE_MODEL_INFO.keys() if "code" in k.lower()],
                "image_generation": [k for k, v in REPLICATE_MODEL_INFO.items() if v.get("model_type") == "image"],
                "multimodal": [k for k, v in REPLICATE_MODEL_INFO.items() if v.get("supports_vision", False)]
            }
        }
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about this provider."""
        return {
            "name": "replicate",
            "description": "Replicate AI provider for accessing thousands of open-source models via marketplace",
            "capabilities": [
                "text_generation",
                "image_generation", 
                "model_marketplace_access",
                "community_models",
                "custom_model_deployment",
                "flexible_scaling"
            ],
            "supported_modalities": {
                "input": ["text", "images"],
                "output": ["text", "images"]
            },
            "special_features": [
                "Access to thousands of open-source models",
                "Community-driven model marketplace", 
                "Custom model deployment capabilities",
                "Flexible pay-per-use pricing",
                "Support for fine-tuned models",
                "Popular foundation models (Llama, Mistral, FLUX, etc.)"
            ],
            "model_providers": [
                "Meta (Llama models)",
                "Mistral AI (Mixtral models)",
                "Black Forest Labs (FLUX models)",
                "Stability AI (Stable Diffusion)",
                "Community contributors"
            ],
            "base_url": self.settings.base_url,
            "pricing": "pay_per_prediction"
        }


def create_replicate_provider(
    api_token: str | None = None,
    base_url: str | None = None,
    headers: Dict[str, str] | None = None,
) -> ReplicateProvider:
    """
    Create a Replicate provider with custom settings.
    
    Args:
        api_token: Replicate API token. If None, uses REPLICATE_API_TOKEN environment variable.
        base_url: Custom base URL for API calls. Defaults to https://api.replicate.com/v1
        headers: Additional headers to include in requests.
        
    Returns:
        ReplicateProvider instance
        
    Example:
        >>> provider = create_replicate_provider(api_token="your-api-token")
        >>> model = provider.language_model("meta/llama-3.1-70b-instruct")
    """
    settings = ReplicateProviderSettings()
    
    if api_token is not None:
        settings.api_token = api_token
    if base_url is not None:
        settings.base_url = base_url
    if headers is not None:
        settings.headers = headers
    
    return ReplicateProvider(settings)


# Default provider instance
replicate_provider = ReplicateProvider()