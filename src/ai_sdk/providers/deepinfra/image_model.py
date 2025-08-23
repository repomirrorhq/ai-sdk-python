"""
DeepInfra Image Model implementation.

DeepInfra provides access to state-of-the-art image generation models
including FLUX, Stable Diffusion 3.5, and other cutting-edge models.
"""

import base64
from typing import Any, Dict, List, Optional

from ai_sdk.core.types import (
    ImageModel,
    GenerateImageOptions,
    GenerateImageResult,
    ImageData,
    Usage,
    ResponseMetadata,
    ProviderMetadata
)
from ai_sdk.utils.http import make_request
from ai_sdk.errors.base import AISDKError
from .types import (
    DeepInfraImageModelId,
    DeepInfraProviderSettings,
    DeepInfraImageRequest,
    DeepInfraImageResponse
)


class DeepInfraImageModel(ImageModel):
    """
    DeepInfra image generation model implementation.
    
    Features:
    - FLUX models (state-of-the-art image generation)
    - Stable Diffusion 3.5 (latest SD model)
    - SDXL Turbo (fast generation)
    - High-quality image generation at competitive pricing
    """
    
    def __init__(
        self,
        model_id: DeepInfraImageModelId,
        settings: DeepInfraProviderSettings,
    ):
        self.model_id = model_id
        self.settings = settings
        self._provider = "deepinfra"
        
        # Model capabilities
        self.max_images_per_call = 4  # DeepInfra batch limit for images
    
    @property
    def provider(self) -> str:
        return self._provider
    
    async def generate_image(
        self,
        prompt: str,
        options: GenerateImageOptions,
    ) -> GenerateImageResult:
        """Generate images using DeepInfra image models."""
        
        try:
            # Prepare request
            request = DeepInfraImageRequest(
                model=self.model_id,
                prompt=prompt,
                n=options.n or 1,
                response_format="b64_json"  # Always use base64 for consistency
            )
            
            # Handle size/dimensions
            if options.size:
                request.size = options.size
            elif options.width and options.height:
                request.width = options.width
                request.height = options.height
            else:
                # Set default size based on model
                if "flux" in self.model_id.lower():
                    request.width = 1024
                    request.height = 1024
                elif "sd3.5" in self.model_id.lower():
                    request.width = 1024
                    request.height = 1024
                else:
                    request.size = "1024x1024"
            
            # Make API request to DeepInfra's image generation endpoint
            headers = self._get_headers()
            
            response_data = await make_request(
                method="POST",
                url=f"{self.settings.base_url}/inference/{self.model_id}",
                headers=headers,
                json=request.model_dump(exclude_none=True),
                timeout=60.0  # Image generation can take longer
            )
            
            response = DeepInfraImageResponse.model_validate(response_data)
            
            # Extract image data
            images = []
            for item in response.data:
                if "b64_json" in item:
                    # Decode base64 image
                    image_bytes = base64.b64decode(item["b64_json"])
                    images.append(ImageData(
                        data=image_bytes,
                        format="png",  # DeepInfra typically returns PNG
                        url=None
                    ))
                elif "url" in item:
                    # Handle URL response (if requested)
                    images.append(ImageData(
                        data=None,
                        format="png",
                        url=item["url"]
                    ))
            
            # Create response metadata
            response_metadata = ResponseMetadata(
                id="image-" + str(response.created),
                model_id=self.model_id,
                timestamp=response.created
            )
            
            # Create provider metadata
            provider_metadata = ProviderMetadata(
                deepinfra={
                    "created": response.created,
                    "model": self.model_id,
                    "image_count": len(response.data),
                    "response_format": request.response_format
                }
            )
            
            # Add model-specific warnings
            warnings = []
            if "turbo" in self.model_id.lower():
                warnings.append("SDXL Turbo optimized for speed, may have slightly lower quality")
            
            return GenerateImageResult(
                images=images,
                usage=None,  # DeepInfra doesn't provide usage stats for images
                response_metadata=response_metadata,
                provider_metadata=provider_metadata,
                warnings=warnings if warnings else None
            )
            
        except Exception as e:
            raise AISDKError(f"DeepInfra image generation error: {str(e)}") from e
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for DeepInfra API requests."""
        api_key = self.settings.api_key
        if not api_key:
            # Try to get from environment
            import os
            api_key = os.getenv("DEEPINFRA_API_KEY")
            
        if not api_key:
            raise AISDKError("DeepInfra API key is required. Set DEEPINFRA_API_KEY environment variable or provide api_key in settings.")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ai-sdk-python/1.0"
        }
        
        # Add custom headers
        if self.settings.headers:
            headers.update(self.settings.headers)
            
        return headers
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about this image model."""
        
        # Model-specific information
        model_info = {
            # FLUX Models (State-of-the-art)
            "black-forest-labs/FLUX-1.1-pro": {
                "description": "Latest FLUX Pro model with improved quality and speed",
                "max_resolution": "2048x2048",
                "supports_aspect_ratios": True,
                "quality": "highest",
                "speed": "fast"
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
                "quality": "high",
                "speed": "fast"
            },
            "black-forest-labs/FLUX-pro": {
                "description": "FLUX Pro model for highest quality generation",
                "max_resolution": "2048x2048",
                "supports_aspect_ratios": True,
                "quality": "highest",
                "speed": "medium"
            },
            
            # Stable Diffusion 3.5
            "stabilityai/sd3.5": {
                "description": "Latest Stable Diffusion 3.5 with improved quality",
                "max_resolution": "1024x1024",
                "supports_aspect_ratios": True,
                "quality": "high",
                "speed": "medium"
            },
            "stabilityai/sd3.5-medium": {
                "description": "SD 3.5 Medium for balanced quality and speed",
                "max_resolution": "1024x1024",
                "supports_aspect_ratios": True,
                "quality": "medium-high",
                "speed": "fast"
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
        
        # Get model-specific info or defaults
        specific_info = model_info.get(self.model_id, {
            "description": "Custom image generation model",
            "max_resolution": "1024x1024",
            "supports_aspect_ratios": True,
            "quality": "high",
            "speed": "medium"
        })
        
        return {
            "provider": self.provider,
            "model_id": self.model_id,
            "description": specific_info["description"],
            "max_resolution": specific_info["max_resolution"],
            "supports_aspect_ratios": specific_info["supports_aspect_ratios"],
            "quality_tier": specific_info["quality"],
            "speed_tier": specific_info["speed"],
            "max_images_per_call": self.max_images_per_call,
            "input_modalities": ["text"],
            "output_modalities": ["image"],
            "supported_formats": ["png", "jpeg"],
            "cost_effective": True,
            "special_capabilities": [
                "cost_effective",
                "state_of_the_art" if "flux" in self.model_id.lower() else "high_quality",
                "custom_dimensions",
                "batch_generation"
            ]
        }