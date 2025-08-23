"""Core middleware interfaces and types for the AI SDK.

This module defines the fundamental middleware interfaces that allow wrapping
language models with additional functionality. The middleware system is based
on functional composition patterns and supports both synchronous and 
asynchronous operations.
"""

from typing import Protocol, Optional, Callable, Awaitable, Any, Dict, Union, Literal
from abc import ABC, abstractmethod

from ..providers.base import LanguageModel
from .types import GenerateTextParams, GenerateTextResult, StreamTextResult


class TransformParamsFunction(Protocol):
    """Protocol for parameter transformation middleware functions.
    
    Transform parameters before they are passed to the language model.
    Useful for:
    - Adding system messages or context
    - Parameter validation and normalization  
    - Dynamic prompt injection
    - External data integration
    """
    
    async def __call__(
        self,
        *,
        params: GenerateTextParams,
        type: Literal["generate", "stream"],
        model: LanguageModel,
    ) -> GenerateTextParams:
        """Transform parameters before model execution.
        
        Args:
            params: The original parameters to transform
            type: Whether this is for generate or stream operation
            model: The language model being called
            
        Returns:
            Transformed parameters to pass to the model
        """
        ...


class WrapGenerateFunction(Protocol):
    """Protocol for wrapping generate method calls.
    
    Wrap the generate method to add functionality like:
    - Request/response logging
    - Response caching
    - Retry logic and error handling
    - Performance monitoring
    - Content filtering
    """
    
    async def __call__(
        self,
        *,
        do_generate: Callable[[], Awaitable[GenerateTextResult]],
        params: GenerateTextParams,
        model: LanguageModel,
    ) -> GenerateTextResult:
        """Wrap a generate method call.
        
        Args:
            do_generate: Function to call the original generate method
            params: The parameters being passed to generate
            model: The language model being called
            
        Returns:
            The result from the generate call (potentially modified)
        """
        ...


class WrapStreamFunction(Protocol):
    """Protocol for wrapping stream method calls.
    
    Wrap the stream method to add functionality like:
    - Stream processing and filtering
    - Real-time logging of streaming data
    - Stream caching strategies
    - Rate limiting for streaming operations
    """
    
    async def __call__(
        self,
        *,
        do_stream: Callable[[], Awaitable[StreamTextResult]],
        params: GenerateTextParams, 
        model: LanguageModel,
    ) -> StreamTextResult:
        """Wrap a stream method call.
        
        Args:
            do_stream: Function to call the original stream method
            params: The parameters being passed to stream
            model: The language model being called
            
        Returns:
            The result from the stream call (potentially modified)
        """
        ...


class LanguageModelMiddleware(Protocol):
    """Protocol defining the middleware interface for language models.
    
    Middleware can implement any combination of:
    - transformParams: Transform parameters before model execution
    - wrapGenerate: Wrap the generate method call
    - wrapStream: Wrap the stream method call
    - overrideProvider: Override the provider name
    - overrideModelId: Override the model identifier
    
    All methods are optional - implement only what you need.
    """
    
    transformParams: Optional[TransformParamsFunction] = None
    wrapGenerate: Optional[WrapGenerateFunction] = None
    wrapStream: Optional[WrapStreamFunction] = None
    overrideProvider: Optional[Callable[[LanguageModel], str]] = None
    overrideModelId: Optional[Callable[[LanguageModel], str]] = None


class MiddlewareFunction(Protocol):
    """Protocol for middleware factory functions.
    
    A middleware function is a callable that returns a LanguageModelMiddleware
    instance. This allows for parameterized middleware creation.
    """
    
    def __call__(self, **kwargs: Any) -> LanguageModelMiddleware:
        """Create a middleware instance with the given parameters.
        
        Args:
            **kwargs: Configuration parameters for the middleware
            
        Returns:
            A configured middleware instance
        """
        ...


# Type aliases for convenience
MiddlewareOrFunction = Union[LanguageModelMiddleware, MiddlewareFunction]
MiddlewareList = list[MiddlewareOrFunction]


class BaseMiddleware(ABC):
    """Abstract base class for implementing middleware.
    
    Provides a convenient base class for implementing middleware with
    default implementations for all methods. Subclasses can override
    only the methods they need.
    """
    
    @property
    def transformParams(self) -> Optional[TransformParamsFunction]:
        """Transform parameters before model execution."""
        return None
        
    @property
    def wrapGenerate(self) -> Optional[WrapGenerateFunction]:
        """Wrap the generate method call."""
        return None
        
    @property
    def wrapStream(self) -> Optional[WrapStreamFunction]:
        """Wrap the stream method call."""
        return None
        
    @property  
    def overrideProvider(self) -> Optional[Callable[[LanguageModel], str]]:
        """Override the provider name."""
        return None
        
    @property
    def overrideModelId(self) -> Optional[Callable[[LanguageModel], str]]:
        """Override the model identifier."""
        return None


class SimpleMiddleware:
    """Simple middleware implementation using property assignment.
    
    This class provides a convenient way to create middleware by assigning
    functions to properties. More flexible than BaseMiddleware for simple
    use cases.
    
    Example:
        ```python
        def my_transform_params(*, params, type, model):
            # Add system message
            return params.model_copy(update={
                "messages": [
                    {"role": "system", "content": "You are helpful."},
                    *params.messages
                ]
            })
        
        middleware = SimpleMiddleware()
        middleware.transformParams = my_transform_params
        ```
    """
    
    def __init__(self):
        self.transformParams: Optional[TransformParamsFunction] = None
        self.wrapGenerate: Optional[WrapGenerateFunction] = None
        self.wrapStream: Optional[WrapStreamFunction] = None
        self.overrideProvider: Optional[Callable[[LanguageModel], str]] = None
        self.overrideModelId: Optional[Callable[[LanguageModel], str]] = None