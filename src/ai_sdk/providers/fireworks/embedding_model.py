"""
Fireworks Embedding Model implementation.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union
import httpx
from pydantic import BaseModel

from ...providers.base import EmbeddingModel
from ...providers.types import EmbedResult, EmbedManyResult, EmbeddingUsage
from ...utils.http import create_http_client
from ...errors.base import APIError, InvalidArgumentError
from .types import FireworksEmbeddingModelId, FireworksProviderSettings, get_model_info


class FireworksEmbeddingModel(EmbeddingModel):
    """
    Fireworks embedding model implementation using OpenAI-compatible API.
    
    Features:
    - High-quality text embeddings via Nomic and other models
    - Batch processing support
    - Optimized inference on Fireworks infrastructure
    - Cost-effective embedding generation
    """
    
    def __init__(self, model_id: FireworksEmbeddingModelId, settings: FireworksProviderSettings):
        self.model_id = model_id
        self.settings = settings
        self.model_info = get_model_info(model_id)
        self._provider_name = "fireworks"
    
    @property
    def provider(self) -> str:
        return self._provider_name
    
    def _prepare_headers(self) -> Dict[str, str]:
        """Prepare headers for API requests."""
        headers = {
            "Authorization": f"Bearer {self.settings.api_key}",
            "Content-Type": "application/json",
        }
        headers.update(self.settings.headers)
        return headers
    
    async def embed(
        self,
        input_text: Union[str, List[str]],
        dimensions: Optional[int] = None,
        **kwargs
    ) -> Union[EmbedResult, EmbedManyResult]:
        """
        Generate embeddings for input text using Fireworks embedding models.
        
        Args:
            input_text: Single string or list of strings to embed
            dimensions: Optional dimension count for the embeddings
            **kwargs: Additional provider-specific options
            
        Returns:
            EmbedResult for single input or EmbedManyResult for multiple inputs
        """
        
        # Determine if we're processing single or multiple inputs
        is_single_input = isinstance(input_text, str)
        input_list = [input_text] if is_single_input else input_text
        
        if not input_list:
            raise InvalidArgumentError("Input text cannot be empty")
        
        # Prepare request payload
        payload = {
            "model": self.model_id,
            "input": input_list,
        }
        
        # Add optional parameters
        if dimensions is not None:
            payload["dimensions"] = dimensions
        
        # Add any additional provider-specific options
        payload.update(kwargs)
        
        try:
            async with create_http_client(
                timeout=self.settings.timeout,
                max_retries=self.settings.max_retries
            ) as client:
                response = await client.post(
                    f"{self.settings.base_url}/embeddings",
                    headers=self._prepare_headers(),
                    json=payload
                )
                
                if response.status_code != 200:
                    error_text = response.text
                    raise APIError(f"Fireworks API error {response.status_code}: {error_text}")
                
                data = response.json()
                return self._process_response(data, is_single_input)
        
        except httpx.HTTPError as e:
            raise APIError(f"HTTP error occurred: {str(e)}")
        except Exception as e:
            raise APIError(f"Unexpected error: {str(e)}")
    
    def _process_response(
        self, 
        data: Dict[str, Any], 
        is_single_input: bool
    ) -> Union[EmbedResult, EmbedManyResult]:
        """Process the API response into the appropriate result format."""
        
        # Extract embeddings from response
        embeddings_data = data.get("data", [])
        embeddings = [item["embedding"] for item in embeddings_data]
        
        # Extract usage information
        usage_info = data.get("usage", {})
        usage = EmbeddingUsage(
            tokens=usage_info.get("total_tokens", 0)
        )
        
        # Create provider metadata
        provider_metadata = {
            "fireworks": {
                "model": data.get("model", self.model_id),
                "embedding_dimensions": len(embeddings[0]) if embeddings else 0,
                "model_type": "embedding",
                "provider_optimization": self.model_info.get("provider_optimization", "fireworks_optimized")
            }
        }
        
        if is_single_input:
            return EmbedResult(
                embedding=embeddings[0] if embeddings else [],
                usage=usage,
                providerMetadata=provider_metadata
            )
        else:
            return EmbedManyResult(
                embeddings=embeddings,
                usage=usage,
                providerMetadata=provider_metadata
            )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about this embedding model."""
        return {
            "model_id": self.model_id,
            "provider": self.provider,
            **self.model_info
        }