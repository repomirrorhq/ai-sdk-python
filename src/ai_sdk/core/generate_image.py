"""Image generation functionality for AI SDK Python."""

import asyncio
import math
from typing import List, Optional, Dict, Any, Union, Literal

from pydantic import BaseModel, Field

from ..providers.base import (
    ImageModel,
    ImageModelResponseMetadata,
    ImageGenerationWarning,
    ImageModelProviderMetadata,
    GeneratedFile,
)
from ..errors.base import AISDKError
from ..utils.http import retry_with_exponential_backoff


class NoImageGeneratedError(AISDKError):
    """Error raised when no image is generated."""

    def __init__(self, responses: List[ImageModelResponseMetadata]):
        self.responses = responses
        super().__init__("No image was generated")


class GenerateImageResult(BaseModel):
    """Result of image generation."""
    
    model_config = {'arbitrary_types_allowed': True}
    
    images: List[GeneratedFile] = Field(..., description="Generated images")
    warnings: List[ImageGenerationWarning] = Field(default_factory=list, description="Warnings from the provider")
    responses: List[ImageModelResponseMetadata] = Field(..., description="Response metadata")
    provider_metadata: ImageModelProviderMetadata = Field(default_factory=dict, description="Provider-specific metadata")
    
    @property
    def image(self) -> GeneratedFile:
        """First generated image."""
        if not self.images:
            raise NoImageGeneratedError([])
        return self.images[0]


class DefaultGeneratedFile(GeneratedFile):
    """Default implementation of generated file."""

    def __init__(self, data: bytes, media_type: str):
        self.data = data
        self.media_type = media_type


def detect_image_media_type(data: bytes) -> str:
    """Detect media type from image data."""
    if data.startswith(b'\xff\xd8\xff'):
        return 'image/jpeg'
    elif data.startswith(b'\x89PNG\r\n\x1a\n'):
        return 'image/png'
    elif data.startswith(b'GIF8'):
        return 'image/gif'
    elif data.startswith(b'RIFF') and b'WEBP' in data[:12]:
        return 'image/webp'
    else:
        return 'image/png'  # default


async def generate_image(
    *,
    model: ImageModel,
    prompt: str,
    n: int = 1,
    max_images_per_call: Optional[int] = None,
    size: Optional[str] = None,
    aspect_ratio: Optional[str] = None,
    seed: Optional[int] = None,
    provider_options: Optional[Dict[str, Any]] = None,
    max_retries: int = 2,
    headers: Optional[Dict[str, str]] = None,
) -> GenerateImageResult:
    """
    Generate images using an image model.
    
    Args:
        model: The image model to use
        prompt: The prompt for image generation
        n: Number of images to generate (default: 1)
        max_images_per_call: Maximum images per API call
        size: Size as "widthxheight" (e.g. "1024x1024")
        aspect_ratio: Aspect ratio as "width:height" (e.g. "16:9")
        seed: Seed for reproducible generation
        provider_options: Provider-specific options
        max_retries: Maximum number of retries (default: 2)
        headers: Additional HTTP headers
        
    Returns:
        GenerateImageResult containing generated images and metadata
        
    Raises:
        NoImageGeneratedError: When no images are generated
    """
    # Determine max images per call
    max_images_per_call_default = max_images_per_call or getattr(model, 'max_images_per_call', 1)
    
    # Calculate how many API calls we need to make
    call_count = math.ceil(n / max_images_per_call_default)
    call_image_counts = []
    
    for i in range(call_count):
        if i < call_count - 1:
            call_image_counts.append(max_images_per_call_default)
        else:
            remainder = n % max_images_per_call_default
            call_image_counts.append(remainder if remainder > 0 else max_images_per_call_default)
    
    # Create retry function
    async def make_call(call_image_count: int):
        return await retry_with_exponential_backoff(
            lambda: model.do_generate(
                prompt=prompt,
                n=call_image_count,
                size=size,
                aspect_ratio=aspect_ratio,
                seed=seed,
                provider_options=provider_options or {},
                headers=headers or {},
            ),
            max_retries=max_retries,
        )
    
    # Make parallel calls
    results = await asyncio.gather(*[make_call(count) for count in call_image_counts])
    
    # Collect results
    images: List[GeneratedFile] = []
    warnings: List[ImageGenerationWarning] = []
    responses: List[ImageModelResponseMetadata] = []
    provider_metadata: ImageModelProviderMetadata = {}
    
    for result in results:
        # Convert raw image data to GeneratedFile objects
        for image_data in result.images:
            media_type = detect_image_media_type(image_data)
            images.append(DefaultGeneratedFile(data=image_data, media_type=media_type))
        
        warnings.extend(result.warnings)
        responses.append(result.response)
        
        # Merge provider metadata
        if result.provider_metadata:
            for provider_name, metadata in result.provider_metadata.items():
                if provider_name not in provider_metadata:
                    provider_metadata[provider_name] = {'images': []}
                provider_metadata[provider_name]['images'].extend(metadata.get('images', []))
    
    if not images:
        raise NoImageGeneratedError(responses)
    
    return GenerateImageResult(
        images=images,
        warnings=warnings,
        responses=responses,
        provider_metadata=provider_metadata
    )


# Synchronous version
def generate_image_sync(
    *,
    model: ImageModel,
    prompt: str,
    n: int = 1,
    max_images_per_call: Optional[int] = None,
    size: Optional[str] = None,
    aspect_ratio: Optional[str] = None,
    seed: Optional[int] = None,
    provider_options: Optional[Dict[str, Any]] = None,
    max_retries: int = 2,
    headers: Optional[Dict[str, str]] = None,
) -> GenerateImageResult:
    """Synchronous version of generate_image."""
    import asyncio
    return asyncio.run(generate_image(
        model=model,
        prompt=prompt,
        n=n,
        max_images_per_call=max_images_per_call,
        size=size,
        aspect_ratio=aspect_ratio,
        seed=seed,
        provider_options=provider_options,
        max_retries=max_retries,
        headers=headers,
    ))