"""
Luma Image Model implementation.
"""

import asyncio
import os
from typing import Any, Dict, List, Optional, Union
import httpx
from ai_sdk.core.types import ImageModel, ImageResult
from ai_sdk.errors.base import AISDKError, APIError
from ai_sdk.utils.http import create_http_client
from .types import (
    LumaProviderSettings,
    LumaImageModelId,
    LumaImageOptions,
    LumaGenerationResponse,
    LumaError
)


class LumaImageModel(ImageModel):
    """
    Luma image model implementation.
    
    Provides high-quality image generation using Luma's Photon models
    with support for custom aspect ratios and professional rendering quality.
    """
    
    def __init__(self, model_id: LumaImageModelId, settings: LumaProviderSettings):
        """
        Initialize Luma image model.
        
        Args:
            model_id: The Luma model identifier ("photon-1" or "photon-flash-1")
            settings: Provider settings including API key and configuration.
        """
        self.model_id = model_id
        self.settings = settings
        self.api_key = settings.api_key or os.getenv("LUMA_API_KEY")
        
        if not self.api_key:
            raise AISDKError("Luma API key is required. Set LUMA_API_KEY environment variable or pass api_key parameter.")
        
        self.base_url = settings.base_url.rstrip("/")
        self.client = create_http_client(
            timeout=settings.timeout,
            max_retries=settings.max_retries
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        if self.settings.headers:
            headers.update(self.settings.headers)
        
        return headers
    
    async def _start_generation(
        self, 
        prompt: str,
        options: Optional[LumaImageOptions] = None
    ) -> str:
        """Start image generation and return generation ID."""
        
        body = {
            "prompt": prompt,
            "model": self.model_id,
        }
        
        if options and options.aspect_ratio:
            body["aspect_ratio"] = options.aspect_ratio
        
        try:
            response = await self.client.post(
                f"{self.base_url}/dream-machine/v1/generations/image",
                headers=self._get_headers(),
                json=body
            )
            response.raise_for_status()
            
            data = response.json()
            generation_response = LumaGenerationResponse.model_validate(data)
            return generation_response.id
            
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                if "detail" in error_data:
                    luma_error = LumaError.model_validate(error_data)
                    error_detail = luma_error.detail[0].msg if luma_error.detail else "Unknown error"
                else:
                    error_detail = str(error_data)
            except:
                error_detail = e.response.text
            
            raise APIError(
                f"Luma image generation start failed: {error_detail}",
                status_code=e.response.status_code
            )
        except Exception as e:
            raise APIError(f"Luma image generation start failed: {str(e)}")
    
    async def _poll_generation(
        self, 
        generation_id: str,
        options: Optional[LumaImageOptions] = None
    ) -> str:
        """Poll for generation completion and return image URL."""
        
        poll_interval = (options.poll_interval_millis / 1000 
                        if options and options.poll_interval_millis 
                        else 0.5)
        max_attempts = (options.max_poll_attempts 
                       if options and options.max_poll_attempts 
                       else 120)
        
        for attempt in range(max_attempts):
            try:
                response = await self.client.get(
                    f"{self.base_url}/dream-machine/v1/generations/{generation_id}",
                    headers=self._get_headers()
                )
                response.raise_for_status()
                
                data = response.json()
                status = LumaGenerationResponse.model_validate(data)
                
                if status.state == "completed":
                    if not status.assets or not status.assets.image:
                        raise APIError("Image generation completed but no image was found")
                    return status.assets.image
                elif status.state == "failed":
                    raise APIError(f"Image generation failed: {status.failure_reason or 'Unknown reason'}")
                
                # Continue polling for "queued" or "dreaming"
                await asyncio.sleep(poll_interval)
                
            except httpx.HTTPStatusError as e:
                error_detail = "Unknown error"
                try:
                    error_data = e.response.json()
                    if "detail" in error_data:
                        luma_error = LumaError.model_validate(error_data)
                        error_detail = luma_error.detail[0].msg if luma_error.detail else "Unknown error"
                    else:
                        error_detail = str(error_data)
                except:
                    error_detail = e.response.text
                
                raise APIError(
                    f"Luma generation polling failed: {error_detail}",
                    status_code=e.response.status_code
                )
            except APIError:
                raise
            except Exception as e:
                raise APIError(f"Luma generation polling failed: {str(e)}")
        
        raise APIError(f"Image generation timed out after {max_attempts} attempts")
    
    async def _download_image(self, image_url: str) -> bytes:
        """Download the generated image."""
        
        try:
            response = await self.client.get(image_url)
            response.raise_for_status()
            return response.content
            
        except httpx.HTTPStatusError as e:
            raise APIError(
                f"Failed to download image: HTTP {e.response.status_code}",
                status_code=e.response.status_code
            )
        except Exception as e:
            raise APIError(f"Failed to download image: {str(e)}")
    
    async def generate_image(
        self,
        prompt: str,
        *,
        n: int = 1,
        size: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        options: Optional[LumaImageOptions] = None,
        **kwargs
    ) -> ImageResult:
        """
        Generate an image using Luma AI.
        
        Args:
            prompt: Text description of the desired image
            n: Number of images to generate (Luma supports 1 image per request)
            size: Image size (not supported by Luma, use aspect_ratio instead)
            aspect_ratio: Aspect ratio for the image (e.g., "16:9", "1:1", "4:3")
            options: Luma-specific generation options
            **kwargs: Additional parameters
            
        Returns:
            ImageResult with generated image data
        """
        
        if n > 1:
            raise APIError("Luma only supports generating 1 image per request")
        
        if size and not aspect_ratio:
            # Try to convert size to aspect ratio
            size_to_aspect = {
                "1024x1024": "1:1",
                "1024x768": "4:3", 
                "768x1024": "3:4",
                "1280x720": "16:9",
                "720x1280": "9:16",
            }
            aspect_ratio = size_to_aspect.get(size)
        
        # Merge options
        final_options = options or LumaImageOptions()
        if aspect_ratio and not final_options.aspect_ratio:
            final_options.aspect_ratio = aspect_ratio
        
        try:
            # Step 1: Start generation
            generation_id = await self._start_generation(prompt, final_options)
            
            # Step 2: Poll for completion
            image_url = await self._poll_generation(generation_id, final_options)
            
            # Step 3: Download image
            image_data = await self._download_image(image_url)
            
            return ImageResult(
                images=[image_data],
                prompt=prompt,
                model_id=self.model_id,
                provider_metadata={
                    "luma": {
                        "generation_id": generation_id,
                        "image_url": image_url,
                        "aspect_ratio": final_options.aspect_ratio
                    }
                }
            )
            
        except APIError:
            raise
        except Exception as e:
            raise APIError(f"Luma image generation failed: {str(e)}")