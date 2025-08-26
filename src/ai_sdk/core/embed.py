"""Core embedding functions for AI SDK Python."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional, TypeVar, Union, Generic

from ..errors import InvalidArgumentError, APIError
from ..providers.base import EmbeddingModel
from ..providers.types import ProviderMetadata
from ..utils.json import ensure_json_parsable

# Type variable for embedding values (usually string, but could be other types)
VALUE = TypeVar('VALUE', bound=Any)


class EmbedOptions:
    """Options for embedding generation."""
    
    def __init__(self, 
                 max_retries: int = 2,
                 headers: Optional[Dict[str, str]] = None,
                 extra_body: Optional[Dict[str, Any]] = None):
        self.max_retries = max_retries
        self.headers = headers
        self.extra_body = extra_body


class EmbeddingUsage:
    """Token usage information for embeddings."""
    
    def __init__(self, tokens: int) -> None:
        """Initialize embedding usage.
        
        Args:
            tokens: Number of input tokens used
        """
        self.tokens = tokens


class EmbedResult(Generic[VALUE]):
    """Result from embedding a single value."""
    
    def __init__(
        self,
        value: VALUE,
        embedding: List[float],
        usage: EmbeddingUsage,
        provider_metadata: Optional[ProviderMetadata] = None,
        response: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize embed result.
        
        Args:
            value: The original value that was embedded
            embedding: The generated embedding vector
            usage: Token usage information
            provider_metadata: Provider-specific metadata
            response: Raw response data
        """
        self.value = value
        self.embedding = embedding
        self.usage = usage
        self.provider_metadata = provider_metadata
        self.response = response


class EmbedManyResult(Generic[VALUE]):
    """Result from embedding multiple values."""
    
    def __init__(
        self,
        values: List[VALUE],
        embeddings: List[List[float]],
        usage: EmbeddingUsage,
        provider_metadata: Optional[ProviderMetadata] = None,
        response: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize embed many result.
        
        Args:
            values: The original values that were embedded
            embeddings: The generated embedding vectors
            usage: Token usage information  
            provider_metadata: Provider-specific metadata
            response: Raw response data
        """
        self.values = values
        self.embeddings = embeddings
        self.usage = usage
        self.provider_metadata = provider_metadata
        self.response = response


async def embed(
    model: EmbeddingModel,
    value: VALUE,
    *,
    max_retries: int = 2,
    headers: Optional[Dict[str, str]] = None,
    extra_body: Optional[Dict[str, Any]] = None,
) -> EmbedResult[VALUE]:
    """Generate an embedding for a single value.
    
    Args:
        model: The embedding model to use
        value: The value to embed (usually a string)
        max_retries: Maximum number of retries on failure
        headers: Additional HTTP headers
        extra_body: Additional request body parameters
        
    Returns:
        EmbedResult containing the embedding and metadata
        
    Raises:
        InvalidArgumentError: If arguments are invalid
        APIError: If the API call fails
    """
    if value is None:
        raise InvalidArgumentError("Value cannot be None")
    
    # Use embed_many with a single value for consistency
    result = await embed_many(
        model=model,
        values=[value],
        max_retries=max_retries,
        headers=headers,
        extra_body=extra_body,
    )
    
    return EmbedResult(
        value=value,
        embedding=result.embeddings[0],
        usage=result.usage,
        provider_metadata=result.provider_metadata,
        response=result.response,
    )


async def embed_many(
    model: EmbeddingModel,
    values: List[VALUE],
    *,
    max_retries: int = 2,
    max_parallel_calls: int = float('inf'),
    headers: Optional[Dict[str, str]] = None,
    extra_body: Optional[Dict[str, Any]] = None,
) -> EmbedManyResult[VALUE]:
    """Generate embeddings for multiple values.
    
    This function automatically handles batching and parallel processing
    based on the model's capabilities and limits.
    
    Args:
        model: The embedding model to use
        values: The values to embed (usually strings)
        max_retries: Maximum number of retries on failure
        max_parallel_calls: Maximum number of parallel API calls
        headers: Additional HTTP headers  
        extra_body: Additional request body parameters
        
    Returns:
        EmbedManyResult containing all embeddings and metadata
        
    Raises:
        InvalidArgumentError: If arguments are invalid
        APIError: If the API call fails
    """
    if not values:
        raise InvalidArgumentError("Values list cannot be empty")
    
    if any(v is None for v in values):
        raise InvalidArgumentError("Values cannot contain None")
    
    # Get model limits
    max_embeddings_per_call = getattr(model, 'max_embeddings_per_call', 1000)
    supports_parallel_calls = getattr(model, 'supports_parallel_calls', True)
    
    # If all values fit in one call, use simple approach
    if len(values) <= max_embeddings_per_call:
        return await _embed_batch(
            model=model,
            values=values,
            max_retries=max_retries,
            headers=headers,
            extra_body=extra_body,
        )
    
    # Split into batches
    batches = _split_into_batches(values, max_embeddings_per_call)
    
    if supports_parallel_calls and max_parallel_calls > 1:
        # Process batches in parallel
        batch_results = await _embed_batches_parallel(
            model=model,
            batches=batches,
            max_parallel_calls=min(max_parallel_calls, len(batches)),
            max_retries=max_retries,
            headers=headers,
            extra_body=extra_body,
        )
    else:
        # Process batches sequentially
        batch_results = []
        for batch in batches:
            result = await _embed_batch(
                model=model,
                values=batch,
                max_retries=max_retries,
                headers=headers,
                extra_body=extra_body,
            )
            batch_results.append(result)
    
    # Combine results
    all_embeddings = []
    total_tokens = 0
    combined_metadata = {}
    
    for result in batch_results:
        all_embeddings.extend(result.embeddings)
        total_tokens += result.usage.tokens
        if result.provider_metadata and result.provider_metadata.data:
            combined_metadata.update(result.provider_metadata.data)
    
    return EmbedManyResult(
        values=values,
        embeddings=all_embeddings,
        usage=EmbeddingUsage(tokens=total_tokens),
        provider_metadata=ProviderMetadata(data=combined_metadata) if combined_metadata else None,
        response=batch_results[0].response if batch_results else None,
    )


async def _embed_batch(
    model: EmbeddingModel,
    values: List[VALUE],
    max_retries: int,
    headers: Optional[Dict[str, str]],
    extra_body: Optional[Dict[str, Any]],
) -> EmbedManyResult[VALUE]:
    """Embed a single batch of values."""
    
    # Call the model's embedding method with retry logic
    for attempt in range(max_retries + 1):
        try:
            # Check if model has modern doEmbed interface or legacy embed_many
            if hasattr(model, 'do_embed'):
                # Modern interface matching TypeScript SDK
                result = await model.do_embed(
                    values=values,
                    headers=headers or {},
                    extra_body=extra_body or {},
                )
                
                usage = EmbeddingUsage(tokens=result.get('usage', {}).get('tokens', 0))
                provider_metadata = None
                if 'provider_metadata' in result:
                    provider_metadata = ProviderMetadata(data=result['provider_metadata'])
                
                return EmbedManyResult(
                    values=values,
                    embeddings=result['embeddings'],
                    usage=usage,
                    provider_metadata=provider_metadata,
                    response=result.get('response'),
                )
            else:
                # Legacy interface - convert strings for now  
                string_values = [str(v) for v in values]
                embeddings = await model.embed_many(string_values)
                
                # Estimate token usage (rough approximation)
                total_chars = sum(len(str(v)) for v in values)
                estimated_tokens = max(1, total_chars // 4)  # Rough token estimation
                
                return EmbedManyResult(
                    values=values,
                    embeddings=embeddings,
                    usage=EmbeddingUsage(tokens=estimated_tokens),
                    provider_metadata=None,
                    response=None,
                )
                
        except Exception as e:
            if attempt == max_retries:
                # Convert to our error type
                if isinstance(e, (APIError, InvalidArgumentError)):
                    raise
                else:
                    raise APIError(f"Embedding failed after {max_retries + 1} attempts: {str(e)}")
            
            # Wait before retry (exponential backoff)
            await asyncio.sleep(2 ** attempt)
    
    # Should never reach here, but just in case
    raise APIError("Embedding failed unexpectedly")


async def _embed_batches_parallel(
    model: EmbeddingModel,
    batches: List[List[VALUE]],
    max_parallel_calls: int,
    max_retries: int,
    headers: Optional[Dict[str, str]],
    extra_body: Optional[Dict[str, Any]],
) -> List[EmbedManyResult[VALUE]]:
    """Process multiple batches in parallel with concurrency limiting."""
    
    semaphore = asyncio.Semaphore(max_parallel_calls)
    
    async def _embed_batch_with_semaphore(batch: List[VALUE]) -> EmbedManyResult[VALUE]:
        async with semaphore:
            return await _embed_batch(
                model=model,
                values=batch,
                max_retries=max_retries,
                headers=headers,
                extra_body=extra_body,
            )
    
    # Create tasks for all batches
    tasks = [_embed_batch_with_semaphore(batch) for batch in batches]
    
    # Wait for all to complete
    return await asyncio.gather(*tasks)


def _split_into_batches(values: List[VALUE], batch_size: int) -> List[List[VALUE]]:
    """Split values into batches of specified size."""
    batches = []
    for i in range(0, len(values), batch_size):
        batches.append(values[i:i + batch_size])
    return batches


# Convenience function for cosine similarity (commonly used with embeddings)
def cosine_similarity(a: List[float], b: List[float]) -> float:
    """Calculate cosine similarity between two embedding vectors.
    
    Args:
        a: First embedding vector
        b: Second embedding vector
        
    Returns:
        Cosine similarity score (-1 to 1)
        
    Raises:
        ValueError: If vectors have different lengths
    """
    if len(a) != len(b):
        raise ValueError(f"Vector dimensions must match: {len(a)} != {len(b)}")
    
    if not a or not b:
        raise ValueError("Vectors cannot be empty")
    
    # Calculate dot product
    dot_product = sum(x * y for x, y in zip(a, b))
    
    # Calculate magnitudes
    magnitude_a = sum(x * x for x in a) ** 0.5
    magnitude_b = sum(x * x for x in b) ** 0.5
    
    # Avoid division by zero
    if magnitude_a == 0 or magnitude_b == 0:
        return 0.0
    
    return dot_product / (magnitude_a * magnitude_b)