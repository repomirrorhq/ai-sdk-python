"""OpenAI embedding model implementation."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

import httpx

from ...errors import APIError, InvalidArgumentError
from ...utils.http import create_http_client, handle_http_error
from ...utils.json import secure_json_parse
from ..base import EmbeddingModel
from ..types import ProviderMetadata


class OpenAIEmbeddingModel(EmbeddingModel):
    """OpenAI embedding model implementation."""
    
    def __init__(self, provider: Any, model_id: str, **kwargs: Any) -> None:
        """Initialize OpenAI embedding model.
        
        Args:
            provider: OpenAI provider instance
            model_id: OpenAI embedding model ID (e.g., "text-embedding-ada-002")
            **kwargs: Additional model configuration
        """
        super().__init__(provider, model_id, **kwargs)
        
        # Model capabilities for OpenAI embedding models
        if model_id.startswith("text-embedding-3"):
            # text-embedding-3-small and text-embedding-3-large
            self.max_embeddings_per_call = 2048
        elif model_id == "text-embedding-ada-002":
            self.max_embeddings_per_call = 2048
        else:
            # Default for unknown models
            self.max_embeddings_per_call = 1000
        
        self.supports_parallel_calls = True
    
    async def do_embed(
        self,
        *,
        values: List[Any],
        headers: Optional[Dict[str, str]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate embeddings using OpenAI's embeddings API.
        
        Args:
            values: List of values to embed (will be converted to strings)
            headers: Additional HTTP headers
            extra_body: Additional request body parameters
            
        Returns:
            Dictionary containing embeddings and metadata
        """
        if not values:
            raise InvalidArgumentError("Values list cannot be empty")
        
        if len(values) > self.max_embeddings_per_call:
            raise InvalidArgumentError(
                f"Too many values for a single call. Maximum: {self.max_embeddings_per_call}, "
                f"got: {len(values)}. Use embed_many() for automatic batching."
            )
        
        # Convert all values to strings
        input_texts = [str(value) for value in values]
        
        # Prepare request
        request_body = {
            "model": self.model_id,
            "input": input_texts,
        }
        
        # Add dimensions if configured for this model
        if "dimensions" in self.config:
            request_body["dimensions"] = self.config["dimensions"]
        
        # Add any extra parameters
        if extra_body:
            request_body.update(extra_body)
        
        # Prepare headers
        request_headers = {
            "Authorization": f"Bearer {self.provider.api_key}",
            "Content-Type": "application/json",
        }
        
        if self.provider.organization:
            request_headers["OpenAI-Organization"] = self.provider.organization
        
        if headers:
            request_headers.update(headers)
        
        # Make the API call
        client = create_http_client()
        
        try:
            response = await client.post(
                f"{self.provider.base_url}/embeddings",
                json=request_body,
                headers=request_headers,
            )
            
            if response.status_code != 200:
                await handle_http_error(response, "OpenAI embeddings")
            
            # Parse response
            response_data = secure_json_parse(response.text, "OpenAI embeddings response")
            
            # Extract embeddings
            embeddings = []
            for embedding_data in response_data.get("data", []):
                embeddings.append(embedding_data["embedding"])
            
            # Extract usage information
            usage_data = response_data.get("usage", {})
            usage = {
                "tokens": usage_data.get("total_tokens", 0)
            }
            
            # Provider metadata
            provider_metadata = {
                "model": response_data.get("model", self.model_id),
                "usage": usage_data,
            }
            
            return {
                "embeddings": embeddings,
                "usage": usage,
                "provider_metadata": provider_metadata,
                "response": {
                    "headers": dict(response.headers),
                    "body": response_data,
                }
            }
            
        except httpx.HTTPStatusError as e:
            await handle_http_error(e.response, "OpenAI embeddings")
        except httpx.RequestError as e:
            raise APIError(f"OpenAI embeddings request failed: {str(e)}")
        finally:
            await client.aclose()
    
    def with_dimensions(self, dimensions: int) -> "OpenAIEmbeddingModel":
        """Set the number of dimensions for embedding models that support it.
        
        Note: Only text-embedding-3-small and text-embedding-3-large support this.
        
        Args:
            dimensions: Number of dimensions (must be positive)
            
        Returns:
            New model instance with dimension configuration
        """
        if dimensions <= 0:
            raise InvalidArgumentError("Dimensions must be positive")
        
        if not self.model_id.startswith("text-embedding-3"):
            raise InvalidArgumentError(
                f"Model {self.model_id} does not support custom dimensions. "
                "Only text-embedding-3-small and text-embedding-3-large support this feature."
            )
        
        # Create new instance with dimensions in config
        new_config = self.config.copy()
        new_config["dimensions"] = dimensions
        
        return OpenAIEmbeddingModel(
            provider=self.provider,
            model_id=self.model_id,
            **new_config
        )