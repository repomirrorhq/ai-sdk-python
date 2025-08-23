"""FAL.ai image model implementation."""

import asyncio
from typing import Dict, Any, Optional, List, cast, Tuple
import httpx
from datetime import datetime

from ...core.generate_image import GenerateImageResult, GenerateImageUsage
from ...errors.base import AISDKError
from ...utils.http import make_request
from ...utils.json import parse_json
from .types import (
    FalImageModelId,
    FalProviderSettings,
    FalImageSettings,
    FalImageSize,
    FalImageSizeCustom,
    FalImageResponse,
    FalValidationErrorResponse,
    FalHttpErrorResponse,
)


class FalImageModel:
    """FAL.ai image model for generating images from text prompts."""
    
    def __init__(
        self,
        model_id: FalImageModelId,
        settings: FalProviderSettings,
    ):
        """Initialize FAL image model.
        
        Args:
            model_id: Model identifier
            settings: Provider configuration settings
        """
        self.model_id = model_id
        self.settings = settings
        
        # Construct headers
        self.headers = {
            "Authorization": f"Key {settings.api_key}",
            **(settings.headers or {}),
        }
    
    async def generate(
        self,
        prompt: str,
        n: Optional[int] = None,
        size: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        seed: Optional[int] = None,
        options: Optional[FalImageSettings] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> GenerateImageResult:
        """Generate images using FAL.ai.
        
        Args:
            prompt: Text prompt for image generation
            n: Number of images to generate
            size: Image size specification (e.g. "1024x1024")
            aspect_ratio: Aspect ratio (e.g. "16:9")
            seed: Random seed for reproducible results
            options: Additional generation options
            headers: Additional headers
            
        Returns:
            Image generation result
            
        Raises:
            AISDKError: If image generation fails
        """
        try:
            # Combine headers
            request_headers = {**self.headers}
            if headers:
                request_headers.update(headers)
            
            # Build request body
            body = {
                "prompt": prompt,
                "num_images": n or 1,
            }
            
            # Add seed if provided
            if seed is not None:
                body["seed"] = seed
            
            # Determine image size
            image_size = self._determine_image_size(size, aspect_ratio, options)
            if image_size:
                body["image_size"] = image_size
            
            # Add additional options
            if options:
                # Convert Pydantic model to dict, excluding None values
                options_dict = options.model_dump(exclude_none=True, exclude={"image_size", "num_images", "seed"})
                body.update(options_dict)
            
            # Generate images
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.settings.base_url}/{self.model_id}",
                    json=body,
                    headers=request_headers,
                    timeout=120.0,  # FAL can be slow for image generation
                )
                response.raise_for_status()
                
                data = response.json()
                fal_response = FalImageResponse.model_validate(data)
            
            # Download generated images
            images = await self._download_images(fal_response.images)
            
            return GenerateImageResult(
                images=images,
                usage=GenerateImageUsage(
                    prompt_tokens=len(prompt.split()),  # Rough estimate
                    total_tokens=len(prompt.split()),
                ),
                response=fal_response.model_dump(),
            )
            
        except httpx.HTTPStatusError as e:
            await self._handle_error_response(e)
        except Exception as e:
            raise AISDKError(f"FAL image generation failed: {str(e)}") from e
    
    def _determine_image_size(
        self, 
        size: Optional[str], 
        aspect_ratio: Optional[str], 
        options: Optional[FalImageSettings]
    ) -> Optional[Any]:
        """Determine the image size from various inputs.
        
        Args:
            size: Size string (e.g. "1024x1024")
            aspect_ratio: Aspect ratio (e.g. "16:9")
            options: Additional options that may contain image_size
            
        Returns:
            Image size specification for FAL API
        """
        # Priority: options.image_size > size > aspect_ratio
        if options and options.image_size:
            if isinstance(options.image_size, FalImageSizeCustom):
                return {"width": options.image_size.width, "height": options.image_size.height}
            else:
                return options.image_size
        
        if size:
            try:
                width, height = map(int, size.split('x'))
                return {"width": width, "height": height}
            except ValueError:
                pass
        
        if aspect_ratio:
            return self._convert_aspect_ratio_to_size(aspect_ratio)
        
        return None
    
    def _convert_aspect_ratio_to_size(self, aspect_ratio: str) -> Optional[str]:
        """Convert aspect ratio to FAL image size preset.
        
        Args:
            aspect_ratio: Aspect ratio string (e.g. "16:9")
            
        Returns:
            FAL size preset or None
        """
        aspect_ratio_map = {
            "1:1": "square_hd",
            "16:9": "landscape_16_9", 
            "9:16": "portrait_16_9",
            "4:3": "landscape_4_3",
            "3:4": "portrait_4_3",
            "16:10": {"width": 1280, "height": 800},
            "10:16": {"width": 800, "height": 1280},
            "21:9": {"width": 2560, "height": 1080},
            "9:21": {"width": 1080, "height": 2560},
        }
        
        return aspect_ratio_map.get(aspect_ratio)
    
    async def _download_images(self, fal_images: List[Any]) -> List[bytes]:
        """Download images from FAL URLs.
        
        Args:
            fal_images: List of FAL image objects with URLs
            
        Returns:
            List of image data as bytes
        """
        async def download_image(image_data: Any) -> bytes:
            async with httpx.AsyncClient() as client:
                response = await client.get(image_data.url, timeout=30.0)
                response.raise_for_status()
                return response.content
        
        # Download all images concurrently
        tasks = [download_image(img) for img in fal_images]
        return await asyncio.gather(*tasks)
    
    async def _handle_error_response(self, error: httpx.HTTPStatusError) -> None:
        """Handle HTTP error response from FAL.
        
        Args:
            error: HTTP status error
            
        Raises:
            AISDKError: With detailed error message
        """
        try:
            error_data = error.response.json()
            
            # Try to parse as validation error first
            try:
                validation_error = FalValidationErrorResponse.model_validate(error_data)
                messages = []
                for detail in validation_error.detail:
                    location = ".".join(detail.loc)
                    messages.append(f"{location}: {detail.msg}")
                message = "\n".join(messages)
            except:
                # Try to parse as HTTP error
                try:
                    http_error = FalHttpErrorResponse.model_validate(error_data)
                    message = http_error.message
                except:
                    message = f"FAL API error: {error.response.status_code}"
                    
        except Exception:
            message = f"FAL API error: {error.response.status_code}"
        
        raise AISDKError(
            f"FAL image generation failed: {message}",
            status_code=error.response.status_code,
        ) from error