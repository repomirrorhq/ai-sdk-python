"""AI SDK Middleware System - Production-Ready Middleware Framework.

This module provides a comprehensive middleware system for the AI SDK, allowing
developers to wrap language models with additional functionality such as:

- Response caching for performance and cost optimization
- Request/response logging and telemetry
- Rate limiting and quota management
- Safety guardrails and content filtering
- Retry logic with exponential backoff
- Parameter transformation and preprocessing

The middleware system is designed to be:
- Language model agnostic (works with OpenAI, Anthropic, Google, etc.)
- Composable (multiple middleware can be chained together)
- Type-safe (full type hints and validation)
- Production-ready (comprehensive error handling and performance)

Example Usage:
    ```python
    from ai_sdk import create_openai
    from ai_sdk.middleware import wrap_language_model, caching_middleware, logging_middleware
    
    # Create base model
    model = create_openai().chat("gpt-4")
    
    # Wrap with middleware
    enhanced_model = wrap_language_model(
        model=model,
        middleware=[
            logging_middleware(),
            caching_middleware(ttl=300),
        ]
    )
    
    # Use as normal - middleware is transparent
    result = await enhanced_model.generate_text("Hello world")
    ```
"""

from .base import (
    LanguageModelMiddleware,
    MiddlewareFunction,
    TransformParamsFunction,
    WrapGenerateFunction,
    WrapStreamFunction,
)
from .wrapper import wrap_language_model
from .builtin import (
    logging_middleware,
    caching_middleware,
    default_settings_middleware,
    telemetry_middleware,
    extract_reasoning_middleware,
    simulate_streaming_middleware,
)

__all__ = [
    # Core types
    "LanguageModelMiddleware",
    "MiddlewareFunction",
    "TransformParamsFunction", 
    "WrapGenerateFunction",
    "WrapStreamFunction",
    
    # Core functionality
    "wrap_language_model",
    
    # Built-in middleware
    "logging_middleware",
    "caching_middleware", 
    "default_settings_middleware",
    "telemetry_middleware",
    "extract_reasoning_middleware",
    "simulate_streaming_middleware",
]