"""
DeepInfra Embedding Model implementation.

DeepInfra provides cost-effective access to high-quality embedding models
including BGE, E5, Sentence Transformers, and multilingual models.
"""

from typing import Any, Dict, List

from ai_sdk.core.types import (
    EmbeddingModel,
    EmbedResult,
    EmbedManyResult,
    Usage,
    ResponseMetadata,
    ProviderMetadata
)
from ai_sdk.utils.http import make_request
from ai_sdk.errors.base import AISDKError
from .types import (
    DeepInfraEmbeddingModelId,
    DeepInfraProviderSettings,
    DeepInfraEmbeddingRequest,
    DeepInfraEmbeddingResponse
)


class DeepInfraEmbeddingModel(EmbeddingModel):
    """
    DeepInfra embedding model implementation.
    
    Features:
    - High-quality embedding models (BGE, E5, Sentence Transformers)
    - Cost-effective pricing for embeddings
    - Multilingual support
    - CLIP models for multimodal embeddings
    - Batch processing support
    """
    
    def __init__(
        self,
        model_id: DeepInfraEmbeddingModelId,
        settings: DeepInfraProviderSettings,
    ):
        self.model_id = model_id
        self.settings = settings
        self._provider = "deepinfra"
        
        # Model capabilities
        self.max_embeddings_per_call = 96  # DeepInfra batch limit
        self.supports_parallel_calls = True
    
    @property
    def provider(self) -> str:
        return self._provider
    
    async def embed(self, values: List[str]) -> EmbedResult:
        """Generate embeddings for multiple texts."""
        
        try:
            # Prepare request
            request = DeepInfraEmbeddingRequest(
                model=self.model_id,
                input=values,
                encoding_format="float"
            )
            
            # Make API request
            headers = self._get_headers()
            
            response_data = await make_request(
                method="POST",
                url=f"{self.settings.base_url}/openai/embeddings",
                headers=headers,
                json=request.model_dump(exclude_none=True),
                timeout=30.0
            )
            
            response = DeepInfraEmbeddingResponse.model_validate(response_data)
            
            # Extract embeddings
            embeddings = []
            for item in response.data:
                embeddings.append(item["embedding"])
            
            # Convert usage information
            usage = None
            if response.usage:
                usage = Usage(
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=0,  # No completion tokens for embeddings
                    total_tokens=response.usage.total_tokens
                )
            
            # Create response metadata
            response_metadata = ResponseMetadata(
                id="embedding-" + str(hash(str(values))),  # Generate a hash-based ID
                model_id=self.model_id,
                timestamp=None
            )
            
            # Create provider metadata
            provider_metadata = ProviderMetadata(
                deepinfra={
                    "object": response.object,
                    "model": response.model,
                    "data_count": len(response.data)
                }
            )
            
            return EmbedResult(
                embeddings=embeddings,
                usage=usage,
                response_metadata=response_metadata,
                provider_metadata=provider_metadata
            )
            
        except Exception as e:
            raise AISDKError(f"DeepInfra embedding error: {str(e)}") from e
    
    async def embed_many(
        self, 
        values: List[str],
        batch_size: int | None = None
    ) -> EmbedManyResult:
        """Generate embeddings for many texts with automatic batching."""
        
        if batch_size is None:
            batch_size = self.max_embeddings_per_call
        
        all_embeddings = []
        total_usage = Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
        batch_count = 0
        
        try:
            # Process in batches
            for i in range(0, len(values), batch_size):
                batch = values[i:i + batch_size]
                result = await self.embed(batch)
                
                all_embeddings.extend(result.embeddings)
                batch_count += 1
                
                # Accumulate usage
                if result.usage:
                    total_usage.prompt_tokens += result.usage.prompt_tokens
                    total_usage.total_tokens += result.usage.total_tokens
            
            # Create final response metadata
            response_metadata = ResponseMetadata(
                id="embedding-batch-" + str(hash(str(values))),
                model_id=self.model_id,
                timestamp=None
            )
            
            # Create provider metadata with batch info
            provider_metadata = ProviderMetadata(
                deepinfra={
                    "batch_count": batch_count,
                    "total_texts": len(values),
                    "batch_size": batch_size,
                    "model": self.model_id
                }
            )
            
            return EmbedManyResult(
                embeddings=all_embeddings,
                usage=total_usage,
                response_metadata=response_metadata,
                provider_metadata=provider_metadata
            )
            
        except Exception as e:
            raise AISDKError(f"DeepInfra batch embedding error: {str(e)}") from e
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for DeepInfra API requests."""
        api_key = self.settings.api_key
        if not api_key:
            # Try to get from environment
            import os
            api_key = os.getenv("DEEPINFRA_API_KEY")
            
        if not api_key:
            raise AISDKError("DeepInfra API key is required. Set DEEPINFRA_API_KEY environment variable or provide api_key in settings.")
        
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
        # Model-specific information
        model_info = {
            # BGE Models (Best for general use)
            "BAAI/bge-base-en-v1.5": {
                "dimensions": 768,
                "max_input_length": 512,
                "languages": ["en"],
                "description": "High-quality English embeddings, base model"
            },
            "BAAI/bge-large-en-v1.5": {
                "dimensions": 1024,
                "max_input_length": 512,
                "languages": ["en"],
                "description": "High-quality English embeddings, large model"
            },
            "BAAI/bge-m3": {
                "dimensions": 1024,
                "max_input_length": 8192,
                "languages": ["100+ languages"],
                "description": "Multilingual embeddings with long context support"
            },
            
            # E5 Models (Multilingual)
            "intfloat/multilingual-e5-large": {
                "dimensions": 1024,
                "max_input_length": 512,
                "languages": ["100+ languages"],
                "description": "Large multilingual embedding model"
            },
            
            # Sentence Transformers
            "sentence-transformers/all-mpnet-base-v2": {
                "dimensions": 768,
                "max_input_length": 384,
                "languages": ["en"],
                "description": "General-purpose sentence embeddings"
            },
            
            # CLIP (Multimodal)
            "sentence-transformers/clip-ViT-B-32": {
                "dimensions": 512,
                "max_input_length": 77,
                "languages": ["en"],
                "description": "Multimodal text-image embeddings",
                "modalities": ["text", "image"]
            }
        }
        
        # Get model-specific info or defaults
        specific_info = model_info.get(self.model_id, {
            "dimensions": 768,
            "max_input_length": 512,
            "languages": ["en"],
            "description": "Custom embedding model"
        })
        
        return {
            "provider": self.provider,
            "model_id": self.model_id,
            "dimensions": specific_info.get("dimensions", 768),
            "max_input_length": specific_info.get("max_input_length", 512),
            "languages": specific_info.get("languages", ["en"]),
            "description": specific_info.get("description", ""),
            "input_modalities": specific_info.get("modalities", ["text"]),
            "output_modalities": ["embeddings"],
            "batch_size": self.max_embeddings_per_call,
            "supports_batching": True,
            "cost_effective": True,
            "special_capabilities": [
                "cost_effective",
                "batch_processing",
                "multilingual" if "multilingual" in self.model_id.lower() or "m3" in self.model_id else "english",
                "openai_compatible"
            ]
        }