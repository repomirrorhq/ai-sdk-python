"""
TogetherAI Image Model implementation

This provides a custom image model for TogetherAI that handles their specific
API requirements, including width/height parameters and base64 response format.
"""

import base64
from typing import Dict, Any, List, Optional, Union
from datetime import datetime

from ...core.generate_image import ImageModel, GenerateImageResult, NoImageGeneratedError
from ...utils.http import make_request
from .types import TogetherAIImageModelId, TogetherAIProviderSettings
from ...errors.base import AISDKError


class TogetherAIImageGenerationError(AISDKError):
    """Error that occurs during TogetherAI image generation."""
    pass


class TogetherAIImageModel(ImageModel):
    """TogetherAI image generation model with custom API handling."""
    
    def __init__(self, model_id: TogetherAIImageModelId, config: Dict[str, Any]):
        self.model_id = model_id
        self.config = config
    
    @property
    def provider(self) -> str:
        return self.config.get('provider', 'togetherai.image')
    
    def _get_base_url(self) -> str:
        """Get the base URL for API calls."""
        return self.config.get('base_url', 'https://api.together.xyz/v1').rstrip('/')
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API calls."""
        headers = {
            'Content-Type': 'application/json',
        }
        
        # Add custom headers from config
        if 'headers' in self.config and callable(self.config['headers']):
            custom_headers = self.config['headers']()
            headers.update(custom_headers)
        elif 'headers' in self.config and isinstance(self.config['headers'], dict):
            headers.update(self.config['headers'])
        
        return headers
    
    def _parse_size(self, size: Optional[str]) -> Optional[Dict[str, int]]:
        """Parse size string (e.g., '1024x1024') into width and height."""
        if not size:
            return None
        
        try:
            if 'x' in size.lower():
                width_str, height_str = size.lower().split('x', 1)
                return {
                    'width': int(width_str.strip()),
                    'height': int(height_str.strip())
                }
        except (ValueError, IndexError):
            pass
        
        return None
    
    async def generate_image(
        self,
        prompt: str,
        *,
        n: Optional[int] = None,
        size: Optional[str] = None,
        seed: Optional[int] = None,
        quality: Optional[str] = None,
        response_format: Optional[str] = None,
        style: Optional[str] = None,
        user: Optional[str] = None,
        **kwargs
    ) -> GenerateImageResult:
        """Generate images using TogetherAI API."""
        try:
            url = f"{self._get_base_url()}/images/generations"
            headers = self._get_headers()
            
            # Build request body with TogetherAI-specific format
            body = {
                "model": self.model_id,
                "prompt": prompt,
                "response_format": "base64",  # TogetherAI uses base64 format
            }
            
            # Add optional parameters
            if n is not None:
                body["n"] = n
            
            # Handle size parameter - convert to width/height for TogetherAI
            size_params = self._parse_size(size)
            if size_params:
                body.update(size_params)
            
            if seed is not None:
                body["seed"] = seed
            
            # Add any provider-specific options
            together_options = kwargs.get('togetherai', {})
            if together_options:
                body.update(together_options)
            
            # Remove togetherai from kwargs to avoid double-adding
            filtered_kwargs = {k: v for k, v in kwargs.items() if k != 'togetherai'}
            body.update(filtered_kwargs)
            
            response_data = await make_request(
                url=url,
                method="POST",
                headers=headers,
                json=body,
                http_client=self.config.get('fetch')
            )
            
            # Extract images from response
            if "data" not in response_data or not response_data["data"]:
                raise NoImageGeneratedError("No image data in response")
            
            images = []
            for item in response_data["data"]:
                image_data = {
                    "b64_json": item.get("b64_json"),
                    "url": item.get("url"),  # Some providers might return URLs too
                }
                images.append(image_data)
            
            return GenerateImageResult(
                images=images,
                response_metadata={
                    "model_id": self.model_id,
                    "provider": self.provider,
                    "timestamp": datetime.utcnow(),
                    "usage": response_data.get("usage", {}),
                }
            )
            
        except Exception as error:
            if isinstance(error, (NoImageGeneratedError, TogetherAIImageGenerationError)):
                raise
            raise TogetherAIImageGenerationError(
                f"TogetherAI image generation failed: {str(error)}"
            ) from error
    
    def get_supported_sizes(self) -> List[str]:
        """Get list of supported image sizes."""
        # Common sizes supported by TogetherAI image models
        return [
            "256x256",
            "512x512", 
            "768x768",
            "1024x1024",
            "1152x896",
            "896x1152",
            "1216x832",
            "832x1216",
            "1344x768",
            "768x1344",
            "1536x640",
            "640x1536",
        ]
    
    def get_max_images_per_call(self) -> int:
        """Get maximum number of images that can be generated in one call."""
        # TogetherAI typically supports up to 4 images per call
        return 4