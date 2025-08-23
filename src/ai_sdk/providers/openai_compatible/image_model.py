"""
OpenAI-Compatible Image Model implementation
"""

from typing import Dict, Any, List, Optional, Union
from urllib.parse import urlencode

from ...core.generate_image import ImageModel, GenerateImageResult
from ...utils.http import make_request
from .types import OpenAICompatibleConfig, OpenAICompatibleImageModelId
from .errors import as_openai_compatible_error


class OpenAICompatibleImageModel(ImageModel):
    """OpenAI-Compatible image generation model"""
    
    def __init__(self, model_id: OpenAICompatibleImageModelId, config: OpenAICompatibleConfig):
        self.model_id = model_id
        self.config = config
    
    @property
    def provider(self) -> str:
        return self.config.provider
    
    def _get_url(self, path: str) -> str:
        """Build full URL with query parameters"""
        base_url = f"{self.config.base_url.rstrip('/')}{path}"
        if self.config.fetch is None:
            query_params = getattr(self.config, 'query_params', None)
            if query_params:
                separator = '&' if '?' in base_url else '?'
                return f"{base_url}{separator}{urlencode(query_params)}"
        return base_url
    
    async def generate_image(
        self,
        prompt: str,
        *,
        n: Optional[int] = None,
        size: Optional[str] = None,
        quality: Optional[str] = None,
        response_format: Optional[str] = None,
        style: Optional[str] = None,
        user: Optional[str] = None,
        **kwargs
    ) -> GenerateImageResult:
        """Generate images using OpenAI-compatible API"""
        try:
            url = self._get_url("/v1/images/generations")
            headers = self.config.headers()
            headers.update({
                "Content-Type": "application/json",
            })
            
            # Prepare request body
            body = {
                "model": self.model_id,
                "prompt": prompt,
            }
            
            # Add optional parameters
            if n is not None:
                body["n"] = n
            if size is not None:
                body["size"] = size
            if quality is not None:
                body["quality"] = quality
            if response_format is not None:
                body["response_format"] = response_format
            if style is not None:
                body["style"] = style
            if user is not None:
                body["user"] = user
            
            # Add any additional parameters
            body.update(kwargs)
            
            response_data = await make_request(
                url=url,
                method="POST",
                headers=headers,
                json=body,
                http_client=self.config.fetch
            )
            
            # Extract images
            images = []
            for item in response_data["data"]:
                image_data = {
                    "url": item.get("url"),
                    "b64_json": item.get("b64_json"),
                    "revised_prompt": item.get("revised_prompt"),
                }
                images.append(image_data)
            
            return GenerateImageResult(
                images=images,
                response_metadata={
                    "created": response_data.get("created"),
                }
            )
            
        except Exception as error:
            raise as_openai_compatible_error(error, self.config.provider)
    
    async def create_variation(
        self,
        image: Union[str, bytes],
        *,
        n: Optional[int] = None,
        size: Optional[str] = None,
        response_format: Optional[str] = None,
        user: Optional[str] = None,
        **kwargs
    ) -> GenerateImageResult:
        """Create image variations (if supported by provider)"""
        try:
            url = self._get_url("/v1/images/variations")
            headers = self.config.headers()
            
            # For file uploads, we need multipart/form-data
            if isinstance(image, bytes):
                # This would require a more sophisticated multipart implementation
                # For now, raise an error indicating this needs to be implemented
                raise NotImplementedError(
                    "Image variations with binary data not yet implemented. "
                    "Please use a URL instead."
                )
            
            # For URL-based variations (some providers support this)
            headers.update({
                "Content-Type": "application/json",
            })
            
            body = {
                "model": self.model_id,
                "image": image,  # Assuming image is a URL
            }
            
            if n is not None:
                body["n"] = n
            if size is not None:
                body["size"] = size
            if response_format is not None:
                body["response_format"] = response_format
            if user is not None:
                body["user"] = user
            
            body.update(kwargs)
            
            response_data = await make_request(
                url=url,
                method="POST",
                headers=headers,
                json=body,
                http_client=self.config.fetch
            )
            
            # Extract images
            images = []
            for item in response_data["data"]:
                image_data = {
                    "url": item.get("url"),
                    "b64_json": item.get("b64_json"),
                }
                images.append(image_data)
            
            return GenerateImageResult(
                images=images,
                response_metadata={
                    "created": response_data.get("created"),
                }
            )
            
        except Exception as error:
            raise as_openai_compatible_error(error, self.config.provider)
    
    async def create_edit(
        self,
        image: Union[str, bytes],
        prompt: str,
        *,
        mask: Optional[Union[str, bytes]] = None,
        n: Optional[int] = None,
        size: Optional[str] = None,
        response_format: Optional[str] = None,
        user: Optional[str] = None,
        **kwargs
    ) -> GenerateImageResult:
        """Create image edits (if supported by provider)"""
        try:
            url = self._get_url("/v1/images/edits")
            
            # This would require multipart/form-data implementation
            # For now, indicate this is not yet implemented
            raise NotImplementedError(
                "Image editing not yet implemented for OpenAI-compatible provider. "
                "This requires multipart/form-data support."
            )
            
        except Exception as error:
            raise as_openai_compatible_error(error, self.config.provider)