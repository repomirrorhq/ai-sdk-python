"""
Luma AI Provider implementation.
"""

from typing import Any, Dict
from ai_sdk.core.types import Provider, ImageModel
from ai_sdk.errors.base import AISDKError
from .types import LumaProviderSettings, LumaImageModelId
from .image_model import LumaImageModel


class LumaProvider(Provider):
    """
    Luma AI provider for high-quality image generation.
    
    Supports:
    - Photon image generation models
    - High-resolution image synthesis
    - Custom aspect ratios
    - Asynchronous generation with polling
    """
    
    def __init__(self, settings: LumaProviderSettings | None = None):
        """
        Initialize Luma provider.
        
        Args:
            settings: Configuration settings for the provider.
                     If None, will use default settings with environment variables.
        """
        self.settings = settings or LumaProviderSettings()
        self._provider_name = "luma"
    
    @property
    def provider(self) -> str:
        return self._provider_name
    
    @property
    def name(self) -> str:
        """Name of the provider."""
        return self._provider_name
    
    def image_model(self, model_id: LumaImageModelId) -> ImageModel:
        """
        Create a Luma image model for image generation.
        
        Args:
            model_id: The Luma model identifier ("photon-1" or "photon-flash-1")
            
        Returns:
            LumaImageModel instance
            
        Example:
            >>> provider = LumaProvider()
            >>> model = provider.image_model("photon-1")
            >>> result = await model.generate_image(prompt)
        """
        return LumaImageModel(model_id, self.settings)
    
    def language_model(self, model_id: str):
        """Luma does not provide language models."""
        raise AISDKError("Luma does not provide language models")
    
    def embedding_model(self, model_id: str):
        """Luma does not provide embedding models."""
        raise AISDKError("Luma does not provide embedding models")
    
    def transcription_model(self):
        """Luma does not provide transcription models."""
        raise AISDKError("Luma does not provide transcription models")
    
    def speech_model(self, model_id: str):
        """Luma does not provide speech models."""
        raise AISDKError("Luma does not provide speech models")
    
    def __call__(self, model_id: LumaImageModelId) -> ImageModel:
        """
        Convenient method to create an image model.
        
        Args:
            model_id: The Luma image model identifier
            
        Returns:
            LumaImageModel instance
        """
        return self.image_model(model_id)
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get information about available Luma models."""
        return {
            "image_models": {
                "photon-1": {
                    "description": "High-quality Photon image generation model",
                    "features": [
                        "High-resolution image synthesis",
                        "Advanced rendering capabilities",
                        "Custom aspect ratios",
                        "Professional quality output"
                    ],
                    "max_resolution": "2048x2048",
                    "supported_formats": ["PNG", "JPEG"],
                    "typical_generation_time": "10-30 seconds"
                },
                "photon-flash-1": {
                    "description": "Fast Photon image generation model optimized for speed",
                    "features": [
                        "Rapid image synthesis",
                        "Good quality output",
                        "Custom aspect ratios",
                        "Optimized for quick iterations"
                    ],
                    "max_resolution": "2048x2048", 
                    "supported_formats": ["PNG", "JPEG"],
                    "typical_generation_time": "5-15 seconds"
                }
            }
        }
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about this provider."""
        return {
            "name": "luma",
            "description": "Luma AI provider for high-quality image generation with Photon models",
            "capabilities": [
                "image_generation",
                "high_resolution_synthesis",
                "custom_aspect_ratios",
                "professional_rendering"
            ],
            "supported_modalities": {
                "input": ["text"],
                "output": ["image"]
            },
            "base_url": self.settings.base_url,
            "api_version": "v1"
        }


def create_luma_provider(
    api_key: str | None = None,
    base_url: str | None = None,
    headers: Dict[str, str] | None = None,
    timeout: float = 120.0,
    max_retries: int = 3,
) -> LumaProvider:
    """
    Create a Luma provider with custom settings.
    
    Args:
        api_key: Luma API key. If None, uses LUMA_API_KEY environment variable.
        base_url: Custom base URL for API calls. Defaults to https://api.lumalabs.ai
        headers: Additional headers to include in requests.
        timeout: Request timeout in seconds.
        max_retries: Maximum number of retry attempts.
        
    Returns:
        LumaProvider instance
        
    Example:
        >>> provider = create_luma_provider(api_key="your-api-key")
        >>> model = provider.image_model("photon-1")
    """
    settings = LumaProviderSettings()
    
    if api_key is not None:
        settings.api_key = api_key
    if base_url is not None:
        settings.base_url = base_url
    if headers is not None:
        settings.headers = headers
    if timeout != 120.0:
        settings.timeout = timeout
    if max_retries != 3:
        settings.max_retries = max_retries
    
    return LumaProvider(settings)


# Default provider instance
luma_provider = LumaProvider()