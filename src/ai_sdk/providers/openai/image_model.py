"""OpenAI image generation models."""

import json
from typing import Dict, List, Optional, Any

import httpx

from ..base import ImageModel, ImageGenerationResult, ImageGenerationWarning, ImageModelResponseMetadata
from ...errors.base import AISDKError
from ...utils.http import create_http_client


class OpenAIImageGenerationError(AISDKError):
    """Error from OpenAI image generation API."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class OpenAIImageModel(ImageModel):
    """OpenAI image generation model."""
    
    def __init__(self, provider, model_id: str, **kwargs):
        super().__init__(provider, model_id, **kwargs)
        
        # Set max images per call based on model
        if model_id == "dall-e-2":
            self.max_images_per_call = 10
        elif model_id == "dall-e-3":
            self.max_images_per_call = 1
        else:
            self.max_images_per_call = 1
    
    async def do_generate(
        self,
        *,
        prompt: str,
        n: int = 1,
        size: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        seed: Optional[int] = None,
        provider_options: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> ImageGenerationResult:
        """Generate images using OpenAI's image generation API."""
        
        # Build request body
        body = {
            "model": self.model_id,
            "prompt": prompt,
            "n": n,
        }
        
        # Handle size parameter
        if size:
            body["size"] = size
        elif aspect_ratio:
            # Convert aspect ratio to size for DALL-E
            # This is a simple mapping - in practice you'd want more sophisticated conversion
            if aspect_ratio == "1:1":
                body["size"] = "1024x1024"
            elif aspect_ratio == "16:9":
                body["size"] = "1792x1024" 
            elif aspect_ratio == "9:16":
                body["size"] = "1024x1792"
            else:
                body["size"] = "1024x1024"  # default
        
        # Add provider-specific options
        if provider_options:
            openai_options = provider_options.get("openai", {})
            for key, value in openai_options.items():
                body[key] = value
        
        # Set response format to b64_json to get image data directly
        body["response_format"] = "b64_json"
        
        # Create HTTP client
        client = create_http_client(
            base_url=getattr(self.provider, 'base_url', 'https://api.openai.com/v1'),
            headers={
                "Authorization": f"Bearer {self.provider.api_key}",
                **(headers or {})
            }
        )
        
        try:
            async with client:
                response = await client.post(
                    "/images/generations",
                    json=body
                )
                
                if response.status_code != 200:
                    error_data = {}
                    try:
                        error_data = response.json()
                    except:
                        pass
                    
                    error_message = error_data.get("error", {}).get("message", f"HTTP {response.status_code}")
                    raise OpenAIImageGenerationError(
                        error_message,
                        status_code=response.status_code,
                        response=error_data
                    )
                
                result = response.json()
                
                # Convert base64 images to bytes
                images = []
                for image_data in result.get("data", []):
                    if "b64_json" in image_data:
                        import base64
                        image_bytes = base64.b64decode(image_data["b64_json"])
                        images.append(image_bytes)
                
                return ImageGenerationResult(
                    images=images,
                    warnings=[],
                    response=ImageModelResponseMetadata({
                        "id": result.get("created"),
                        "model": self.model_id,
                        "usage": {
                            "prompt_tokens": len(prompt.split()),  # rough estimate
                            "total_tokens": len(prompt.split()),
                        }
                    }),
                    provider_metadata={
                        "openai": {
                            "images": result.get("data", [])
                        }
                    }
                )
                
        except httpx.RequestError as e:
            raise OpenAIImageGenerationError(f"Request failed: {str(e)}")
        except json.JSONDecodeError:
            raise OpenAIImageGenerationError("Invalid JSON response from OpenAI API")