"""Language model wrapping functionality for middleware composition.

This module provides the core `wrap_language_model` function that applies
middleware to language models. It handles middleware composition, parameter
transformation, and method wrapping while preserving the original language
model interface.
"""

from typing import Optional, Union, List, Callable, Awaitable
import asyncio
from functools import wraps

from ..providers.base import LanguageModel
from .types import GenerateTextParams, GenerateTextResult, StreamTextResult
from .base import LanguageModelMiddleware, MiddlewareOrFunction


def as_list(item: Union[LanguageModelMiddleware, List[LanguageModelMiddleware]]) -> List[LanguageModelMiddleware]:
    """Convert a single middleware or list of middleware to a list."""
    if isinstance(item, list):
        return item
    return [item]


def resolve_middleware(middleware: MiddlewareOrFunction) -> LanguageModelMiddleware:
    """Resolve a middleware or middleware function to a middleware instance."""
    if callable(middleware) and not hasattr(middleware, 'transformParams'):
        # This is a middleware function, call it to get the middleware
        return middleware()
    return middleware


class WrappedLanguageModel:
    """A language model wrapped with middleware functionality.
    
    This class wraps a language model and applies a chain of middleware
    to transform parameters and wrap method calls. It maintains the same
    interface as the original language model.
    """
    
    def __init__(
        self,
        model: LanguageModel,
        middleware_chain: List[LanguageModelMiddleware],
        model_id: Optional[str] = None,
        provider_id: Optional[str] = None,
    ):
        self._original_model = model
        self._middleware_chain = middleware_chain
        self._custom_model_id = model_id
        self._custom_provider_id = provider_id
    
    @property
    def provider(self) -> str:
        """Get the provider name, applying any overrides from middleware."""
        for middleware in reversed(self._middleware_chain):
            if hasattr(middleware, 'overrideProvider') and middleware.overrideProvider:
                return middleware.overrideProvider(self._original_model)
        
        return self._custom_provider_id or self._original_model.provider
    
    @property
    def model_id(self) -> str:
        """Get the model ID, applying any overrides from middleware."""
        for middleware in reversed(self._middleware_chain):
            if hasattr(middleware, 'overrideModelId') and middleware.overrideModelId:
                return middleware.overrideModelId(self._original_model)
        
        return self._custom_model_id or self._original_model.model_id
    
    async def _transform_params(
        self, 
        params: GenerateTextParams, 
        operation_type: str
    ) -> GenerateTextParams:
        """Apply parameter transformations from middleware chain."""
        transformed_params = params
        
        # Apply transformParams from each middleware in order
        for middleware in self._middleware_chain:
            if hasattr(middleware, 'transformParams') and middleware.transformParams:
                transformed_params = await middleware.transformParams(
                    params=transformed_params,
                    type=operation_type,
                    model=self._original_model
                )
        
        return transformed_params
    
    async def _wrap_generate(
        self,
        params: GenerateTextParams,
        base_generate: Callable[[], Awaitable[GenerateTextResult]]
    ) -> GenerateTextResult:
        """Apply generate wrappers from middleware chain."""
        current_generate = base_generate
        
        # Apply wrapGenerate from each middleware in reverse order
        # This ensures the last middleware in the chain is closest to the model
        for middleware in reversed(self._middleware_chain):
            if hasattr(middleware, 'wrapGenerate') and middleware.wrapGenerate:
                # Capture the current generate function
                wrapped_generate = current_generate
                current_generate = lambda: middleware.wrapGenerate(
                    do_generate=wrapped_generate,
                    params=params,
                    model=self._original_model
                )
        
        return await current_generate()
    
    async def _wrap_stream(
        self,
        params: GenerateTextParams,
        base_stream: Callable[[], Awaitable[StreamTextResult]]
    ) -> StreamTextResult:
        """Apply stream wrappers from middleware chain."""
        current_stream = base_stream
        
        # Apply wrapStream from each middleware in reverse order
        for middleware in reversed(self._middleware_chain):
            if hasattr(middleware, 'wrapStream') and middleware.wrapStream:
                # Capture the current stream function
                wrapped_stream = current_stream
                current_stream = lambda: middleware.wrapStream(
                    do_stream=wrapped_stream,
                    params=params,
                    model=self._original_model
                )
        
        return await current_stream()
    
    async def generate_text(
        self, 
        params: GenerateTextParams
    ) -> GenerateTextResult:
        """Generate text with middleware applied."""
        # Transform parameters
        transformed_params = await self._transform_params(params, "generate")
        
        # Create base generate function
        async def base_generate() -> GenerateTextResult:
            return await self._original_model.generate_text(transformed_params)
        
        # Apply wrappers and execute
        return await self._wrap_generate(transformed_params, base_generate)
    
    async def stream_text(
        self, 
        params: GenerateTextParams
    ) -> StreamTextResult:
        """Stream text with middleware applied."""
        # Transform parameters
        transformed_params = await self._transform_params(params, "stream")
        
        # Create base stream function
        async def base_stream() -> StreamTextResult:
            return await self._original_model.stream_text(transformed_params)
        
        # Apply wrappers and execute
        return await self._wrap_stream(transformed_params, base_stream)
    
    def __getattr__(self, name: str):
        """Delegate unknown attributes to the original model."""
        return getattr(self._original_model, name)


def wrap_language_model(
    *,
    model: LanguageModel,
    middleware: Union[MiddlewareOrFunction, List[MiddlewareOrFunction]],
    model_id: Optional[str] = None,
    provider_id: Optional[str] = None,
) -> LanguageModel:
    """Wrap a language model with middleware functionality.
    
    This function applies middleware to a language model, enabling features like:
    - Parameter transformation (adding system messages, context, etc.)
    - Response caching and optimization
    - Request/response logging and telemetry
    - Rate limiting and quota management
    - Safety guardrails and content filtering
    - Retry logic with exponential backoff
    
    Args:
        model: The original language model to wrap
        middleware: Single middleware or list of middleware to apply.
                   When multiple middleware are provided, they are applied
                   in order for parameter transformation, and in reverse
                   order for method wrapping.
        model_id: Optional custom model ID to override the original
        provider_id: Optional custom provider ID to override the original
        
    Returns:
        A wrapped language model with the same interface as the original
        
    Example:
        ```python
        from ai_sdk import create_openai
        from ai_sdk.middleware import wrap_language_model, logging_middleware, caching_middleware
        
        model = create_openai().chat("gpt-4")
        
        wrapped = wrap_language_model(
            model=model,
            middleware=[
                logging_middleware(level="INFO"),
                caching_middleware(ttl=300),
            ]
        )
        
        # Use the wrapped model like normal
        result = await wrapped.generate_text({
            "messages": [{"role": "user", "content": "Hello!"}]
        })
        ```
    """
    middleware_list = as_list(middleware)
    resolved_middleware = [resolve_middleware(mw) for mw in middleware_list]
    
    return WrappedLanguageModel(
        model=model,
        middleware_chain=resolved_middleware,
        model_id=model_id,
        provider_id=provider_id,
    )