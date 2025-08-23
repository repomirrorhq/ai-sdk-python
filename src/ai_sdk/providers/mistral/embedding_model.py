"""
Mistral Embedding Model implementation.
Provides embedding capabilities for Mistral AI embedding models.
"""

from typing import Any, Dict, List, Optional
from ai_sdk.core.types import EmbeddingModel, GenerateEmbeddingOptions, GenerateEmbeddingResult
from ai_sdk.providers.types import Usage
from ai_sdk.errors.base import AISDKError
from ai_sdk.utils.http import create_http_client
from pydantic import BaseModel
from .types import MistralEmbeddingModelId


class MistralEmbeddingResponse(BaseModel):
    """Response schema for Mistral embedding API."""
    data: List[Dict[str, List[float]]]  # [{"embedding": [float, ...]}]
    usage: Optional[Dict[str, int]] = None  # {"prompt_tokens": int}


class MistralEmbeddingModel(EmbeddingModel):
    """
    Mistral AI Embedding Model implementation.
    
    Supports Mistral's embedding models including:
    - mistral-embed: General-purpose text embeddings
    
    Key features:
    - Batch processing: Up to 32 embeddings per call
    - High-quality embeddings optimized for semantic similarity
    - OpenAI-compatible API format
    """
    
    def __init__(
        self,
        model_id: MistralEmbeddingModelId,
        api_key: str,
        base_url: str = "https://api.mistral.ai/v1",
        max_retries: int = 3,
        timeout: float = 30.0,
    ):
        self.model_id = model_id
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.max_retries = max_retries
        self.timeout = timeout
        self.http_client = create_http_client(timeout=timeout, max_retries=max_retries)
        
        # Model capabilities
        self.max_embeddings_per_call = 32  # Mistral supports batch processing
        self.supports_parallel_calls = False  # Use batch processing instead
    
    def _get_headers(self) -> Dict[str, str]:
        """Get the headers for Mistral API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ai-sdk-python",
        }
    
    async def _prepare_request_body(self, texts: List[str]) -> Dict[str, Any]:
        """Prepare the request body for the Mistral embedding API."""
        return {
            "model": self.model_id,
            "input": texts,
            "encoding_format": "float"
        }
    
    async def generate_embedding(
        self,
        text: str,
        options: Optional[GenerateEmbeddingOptions] = None
    ) -> GenerateEmbeddingResult:
        """
        Generate a single embedding for the given text.
        
        Args:
            text: The input text to embed
            options: Optional generation options
            
        Returns:
            GenerateEmbeddingResult with the embedding and usage information
        """
        results = await self.generate_embeddings([text], options)
        return results[0]
    
    async def generate_embeddings(
        self,
        texts: List[str],
        options: Optional[GenerateEmbeddingOptions] = None
    ) -> List[GenerateEmbeddingResult]:
        """
        Generate embeddings for multiple texts.
        
        Mistral supports up to 32 texts per request for efficient batch processing.
        
        Args:
            texts: List of input texts to embed (max 32 per call)
            options: Optional generation options
            
        Returns:
            List of GenerateEmbeddingResult objects
        """
        if not texts:
            return []
        
        if len(texts) > self.max_embeddings_per_call:
            raise AISDKError(
                f"Too many texts for Mistral embedding call. "
                f"Maximum {self.max_embeddings_per_call}, got {len(texts)}"
            )
        
        url = f"{self.base_url}/embeddings"
        body = await self._prepare_request_body(texts)
        headers = self._get_headers()
        
        try:
            # Make the API request
            async with self.http_client as client:
                response = await client.post(
                    url,
                    json=body,
                    headers=headers
                )
                
                if response.status_code != 200:
                    error_data = response.json() if response.content else {}
                    error_message = error_data.get('message', 'Unknown error')
                    raise AISDKError(
                        f"Mistral embedding request failed: {response.status_code} - {error_message}"
                    )
                
                result_data = response.json()
                mistral_response = MistralEmbeddingResponse.model_validate(result_data)
                
                # Extract usage information
                usage = None
                if mistral_response.usage:
                    prompt_tokens = mistral_response.usage.get('prompt_tokens', 0)
                    usage = Usage(
                        input_tokens=prompt_tokens,
                        output_tokens=0,
                        total_tokens=prompt_tokens
                    )
                
                # Convert to individual results
                results = []
                for i, embedding_data in enumerate(mistral_response.data):
                    result = GenerateEmbeddingResult(
                        embedding=embedding_data['embedding'],
                        usage=usage if usage and i == 0 else None  # Only include usage in first result
                    )
                    results.append(result)
                
                return results
                
        except Exception as e:
            if isinstance(e, AISDKError):
                raise
            raise AISDKError(f"Failed to generate embeddings: {str(e)}") from e
    
    async def close(self):
        """Close the HTTP client."""
        if hasattr(self.http_client, 'aclose'):
            await self.http_client.aclose()