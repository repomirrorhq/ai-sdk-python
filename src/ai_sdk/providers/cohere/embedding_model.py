"""
Cohere Embedding Model implementation.
"""

from typing import Any, Dict, List
from pydantic import BaseModel

from ai_sdk.core.types import (
    EmbeddingModel,
    EmbedOptions,
    EmbedResult,
    EmbedManyOptions,
    EmbedManyResult,
    Usage,
    ResponseMetadata,
    ProviderMetadata
)
from ai_sdk.utils.http import make_request
from ai_sdk.errors.base import AISDKError
from .types import (
    CohereEmbeddingModelId,
    CohereEmbeddingRequest,
    CohereEmbeddingResponse,
    CohereProviderSettings
)


class CohereEmbeddingModel(EmbeddingModel):
    """
    Cohere embedding model implementation.
    
    Supports text embeddings with various input types and embedding formats.
    """
    
    def __init__(
        self,
        model_id: CohereEmbeddingModelId,
        settings: CohereProviderSettings,
    ):
        self.model_id = model_id
        self.settings = settings
        self._provider = "cohere"
        
        # Cohere embedding model limits
        self.max_embeddings_per_call = 96
        self.supports_parallel_calls = True
    
    @property
    def provider(self) -> str:
        return self._provider
    
    async def embed(
        self,
        values: List[str],
        options: EmbedOptions | None = None,
    ) -> EmbedResult:
        """Generate embeddings for a list of texts."""
        
        if not values:
            raise AISDKError("At least one text value is required for embedding")
            
        if len(values) > self.max_embeddings_per_call:
            raise AISDKError(
                f"Too many values for single call. Maximum {self.max_embeddings_per_call}, got {len(values)}."
                " Use embed_many() for larger batches."
            )
        
        try:
            # Prepare request
            request = CohereEmbeddingRequest(
                model=self.model_id,
                texts=values,
                input_type=self._get_input_type(options),
                embedding_types=["float"],  # Default to float embeddings
                truncate="end"  # Truncate from end if too long
            )
            
            # Make API request
            headers = self._get_headers()
            
            response_data = await make_request(
                method="POST",
                url=f"{self.settings.base_url}/embed",
                headers=headers,
                json=request.model_dump(exclude_none=True),
                timeout=getattr(options, 'request_timeout', None) if options else None
            )
            
            response = CohereEmbeddingResponse.model_validate(response_data)
            
            # Convert usage information
            usage = None
            if response.usage:
                # Cohere doesn't provide detailed token counts for embeddings
                # Use a reasonable estimate
                total_tokens = sum(len(text.split()) for text in values)
                usage = Usage(
                    prompt_tokens=total_tokens,
                    completion_tokens=0,
                    total_tokens=total_tokens
                )
            
            # Create response metadata
            response_metadata = ResponseMetadata(
                id=response.id,
                model_id=self.model_id,
                timestamp=None
            )
            
            provider_metadata = ProviderMetadata(
                cohere={
                    "texts": response.texts,
                    "model": self.model_id,
                    "embedding_type": "float"
                }
            )
            
            return EmbedResult(
                embeddings=response.embeddings,
                usage=usage,
                response_metadata=response_metadata,
                provider_metadata=provider_metadata
            )
            
        except Exception as e:
            raise AISDKError(f"Cohere embedding error: {str(e)}") from e
    
    async def embed_many(
        self,
        values: List[str],
        options: EmbedManyOptions | None = None,
    ) -> EmbedManyResult:
        """Generate embeddings for many texts, handling batching automatically."""
        
        if not values:
            raise AISDKError("At least one text value is required for embedding")
        
        # Split into batches
        batches = [
            values[i:i + self.max_embeddings_per_call]
            for i in range(0, len(values), self.max_embeddings_per_call)
        ]
        
        all_embeddings = []
        total_usage = Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
        
        for batch in batches:
            # Create embed options from embed_many options
            embed_options = EmbedOptions() if options else None
            if options:
                embed_options.request_timeout = options.request_timeout
            
            batch_result = await self.embed(batch, embed_options)
            
            all_embeddings.extend(batch_result.embeddings)
            
            if batch_result.usage:
                total_usage.prompt_tokens += batch_result.usage.prompt_tokens
                total_usage.completion_tokens += batch_result.usage.completion_tokens
                total_usage.total_tokens += batch_result.usage.total_tokens
        
        # Use metadata from the last batch (they should be similar)
        response_metadata = ResponseMetadata(
            id=f"batch_{len(batches)}_embeddings",
            model_id=self.model_id,
            timestamp=None
        )
        
        provider_metadata = ProviderMetadata(
            cohere={
                "texts": values,
                "model": self.model_id,
                "embedding_type": "float",
                "batch_count": len(batches)
            }
        )
        
        return EmbedManyResult(
            embeddings=all_embeddings,
            usage=total_usage,
            response_metadata=response_metadata,
            provider_metadata=provider_metadata
        )
    
    def _get_input_type(self, options: EmbedOptions | None) -> str:
        """
        Determine the appropriate input type for Cohere embeddings.
        
        Cohere supports different input types that optimize embeddings for different use cases:
        - search_document: For documents to be searched over
        - search_query: For search queries
        - classification: For text classification
        - clustering: For text clustering
        """
        if options and hasattr(options, 'input_type'):
            return getattr(options, 'input_type')
            
        # Default to search_document which works well for general text
        return "search_document"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Cohere API requests."""
        api_key = self.settings.api_key
        if not api_key:
            # Try to get from environment
            import os
            api_key = os.getenv("COHERE_API_KEY")
            
        if not api_key:
            raise AISDKError("Cohere API key is required. Set COHERE_API_KEY environment variable or provide api_key in settings.")
        
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
        """Get information about this embedding model."""
        return {
            "provider": self.provider,
            "model_id": self.model_id,
            "max_embeddings_per_call": self.max_embeddings_per_call,
            "supports_parallel_calls": self.supports_parallel_calls,
            "embedding_dimensions": self._get_embedding_dimensions(),
            "input_types": ["search_document", "search_query", "classification", "clustering"],
            "embedding_types": ["float", "int8", "uint8", "binary", "ubinary"]
        }
    
    def _get_embedding_dimensions(self) -> int | None:
        """Get the embedding dimensions for different Cohere models."""
        # Common Cohere embedding model dimensions
        model_dimensions = {
            "embed-english-v3.0": 1024,
            "embed-multilingual-v3.0": 1024,
            "embed-english-v2.0": 4096,
            "embed-multilingual-v2.0": 768,
            "embed-english-light-v3.0": 384,
            "embed-multilingual-light-v3.0": 384,
            "embed-english-light-v2.0": 1024,
            "embed-multilingual-light-v2.0": 768,
        }
        
        return model_dimensions.get(self.model_id, None)