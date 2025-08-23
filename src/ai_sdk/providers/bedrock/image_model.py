"""
Bedrock Image Model implementation.
Provides image generation capabilities for Amazon Bedrock image models.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from ai_sdk.core.types import ImageModel, GenerateImageOptions, GenerateImageResult
from ai_sdk.providers.types import Usage
from ai_sdk.errors.base import AISDKError
from ai_sdk.utils.http import create_http_client
from pydantic import BaseModel, Field
from .types import BedrockImageModelId
from .auth import BedrockAuth


class BedrockImageOptions(BaseModel):
    """Bedrock-specific image generation options."""
    
    negative_text: Optional[str] = Field(
        default=None,
        description="Negative prompt text to avoid in image generation"
    )
    
    style: Optional[str] = Field(
        default=None,
        description="Style to apply to the generated image"
    )
    
    quality: Optional[str] = Field(
        default=None,
        description="Quality setting for image generation"
    )
    
    cfg_scale: Optional[float] = Field(
        default=None,
        alias="cfgScale",
        description="Classifier-free guidance scale (typically 1-20)"
    )


class BedrockImageResponse(BaseModel):
    """Response schema for Bedrock image generation API."""
    images: List[str]  # Base64 encoded images


class BedrockImageModel(ImageModel):
    """
    Amazon Bedrock Image Model implementation.
    
    Supports various image generation models available on Amazon Bedrock including:
    - Amazon Titan Image Generator (v1 and v2)
    - Stability AI models (Stable Diffusion XL, Stable Image Ultra/Core)
    - Amazon Nova Canvas models
    """
    
    # Model-specific maximum images per call
    MODEL_MAX_IMAGES = {
        "amazon.nova-canvas-v1:0": 5,
        "amazon.titan-image-generator-v1": 1,
        "amazon.titan-image-generator-v2:0": 1,
        "stability.stable-diffusion-xl-v1:0": 1,
        "stability.stable-image-ultra-v1:0": 1,
        "stability.stable-image-core-v1:0": 1,
        "us.amazon.nova-canvas-v1:0": 5,
    }
    
    def __init__(
        self,
        model_id: BedrockImageModelId,
        auth: BedrockAuth,
        region: str = "us-east-1",
        base_url: Optional[str] = None,
        max_retries: int = 3,
        timeout: float = 60.0,  # Image generation can take longer
    ):
        self.model_id = model_id
        self.auth = auth
        self.region = region
        self.base_url = base_url or f"https://bedrock-runtime.{region}.amazonaws.com"
        self.max_retries = max_retries
        self.timeout = timeout
        self.http_client = create_http_client(timeout=timeout, max_retries=max_retries)
    
    @property
    def max_images_per_call(self) -> int:
        """Get the maximum number of images that can be generated per call."""
        return self.MODEL_MAX_IMAGES.get(self.model_id, 1)
    
    def _get_url(self) -> str:
        """Get the API URL for the image model."""
        encoded_model_id = self.model_id.replace(":", "%3A")
        return f"{self.base_url}/model/{encoded_model_id}/invoke"
    
    def _parse_size(self, size: Optional[str]) -> tuple[Optional[int], Optional[int]]:
        """Parse size string (e.g., '1024x1024') into width and height."""
        if not size:
            return None, None
        
        try:
            width_str, height_str = size.split('x')
            return int(width_str), int(height_str)
        except (ValueError, AttributeError):
            return None, None
    
    async def _prepare_request_body(
        self,
        prompt: str,
        n: Optional[int] = None,
        size: Optional[str] = None,
        seed: Optional[int] = None,
        options: Optional[BedrockImageOptions] = None
    ) -> Dict[str, Any]:
        """Prepare the request body for the Bedrock image generation API."""
        width, height = self._parse_size(size)
        
        # Base request structure for Nova Canvas and Titan Image Generator
        body = {
            "taskType": "TEXT_IMAGE",
            "textToImageParams": {
                "text": prompt
            },
            "imageGenerationConfig": {}
        }
        
        # Add optional text-to-image parameters
        if options:
            if options.negative_text:
                body["textToImageParams"]["negativeText"] = options.negative_text
            if options.style:
                body["textToImageParams"]["style"] = options.style
        
        # Add image generation config
        if width:
            body["imageGenerationConfig"]["width"] = width
        if height:
            body["imageGenerationConfig"]["height"] = height
        if seed is not None:
            body["imageGenerationConfig"]["seed"] = seed
        if n is not None:
            body["imageGenerationConfig"]["numberOfImages"] = n
        
        # Add provider-specific options
        if options:
            if options.quality:
                body["imageGenerationConfig"]["quality"] = options.quality
            if options.cfg_scale is not None:
                body["imageGenerationConfig"]["cfgScale"] = options.cfg_scale
        
        return body
    
    async def generate_image(
        self,
        prompt: str,
        options: Optional[GenerateImageOptions] = None
    ) -> GenerateImageResult:
        """
        Generate a single image from the given prompt.
        
        Args:
            prompt: The text prompt for image generation
            options: Optional generation options
            
        Returns:
            GenerateImageResult with the generated image and metadata
        """
        # Parse options
        n = getattr(options, 'n', None) if options else None
        size = getattr(options, 'size', None) if options else None
        seed = getattr(options, 'seed', None) if options else None
        
        # Parse Bedrock-specific options
        bedrock_options = None
        if options and hasattr(options, 'provider_options') and options.provider_options:
            bedrock_options = BedrockImageOptions.model_validate(
                options.provider_options.get('bedrock', {})
            )
        
        # Validate number of images
        if n and n > self.max_images_per_call:
            raise AISDKError(
                f"Model {self.model_id} supports maximum {self.max_images_per_call} images per call, got {n}"
            )
        
        url = self._get_url()
        body = await self._prepare_request_body(
            prompt=prompt,
            n=n,
            size=size,
            seed=seed,
            options=bedrock_options
        )
        
        try:
            # Prepare headers with authentication
            headers = await self.auth.get_headers(
                method="POST",
                url=url,
                body=body
            )
            headers["Content-Type"] = "application/json"
            
            # Make the API request
            current_time = datetime.utcnow()
            async with self.http_client as client:
                response = await client.post(
                    url,
                    json=body,
                    headers=headers
                )
                
                if response.status_code != 200:
                    error_data = response.json() if response.content else {}
                    raise AISDKError(
                        f"Bedrock image generation request failed: {response.status_code} - {error_data}"
                    )
                
                result_data = response.json()
                bedrock_response = BedrockImageResponse.model_validate(result_data)
                
                return GenerateImageResult(
                    images=bedrock_response.images,  # Base64 encoded images
                    warnings=[],
                    response_metadata={
                        "timestamp": current_time.isoformat(),
                        "model_id": self.model_id,
                        "headers": dict(response.headers)
                    }
                )
                
        except Exception as e:
            if isinstance(e, AISDKError):
                raise
            raise AISDKError(f"Failed to generate image: {str(e)}") from e
    
    async def generate_images(
        self,
        prompts: List[str],
        options: Optional[GenerateImageOptions] = None
    ) -> List[GenerateImageResult]:
        """
        Generate images for multiple prompts.
        
        Args:
            prompts: List of text prompts for image generation
            options: Optional generation options
            
        Returns:
            List of GenerateImageResult objects
        """
        if not prompts:
            return []
        
        # Generate images for each prompt individually
        results = []
        for prompt in prompts:
            result = await self.generate_image(prompt, options)
            results.append(result)
        
        return results
    
    async def close(self):
        """Close the HTTP client."""
        if hasattr(self.http_client, 'aclose'):
            await self.http_client.aclose()