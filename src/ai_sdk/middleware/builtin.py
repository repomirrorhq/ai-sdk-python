"""Built-in middleware implementations for common use cases.

This module provides ready-to-use middleware for common scenarios:
- Logging middleware for request/response tracking
- Caching middleware for performance optimization
- Default settings middleware for global configuration
- Telemetry middleware for usage tracking

These middleware can be used directly or as examples for custom implementations.
"""

import asyncio
import logging
import time
import hashlib
import json
import re
from typing import Optional, Dict, Any, Union, List
from datetime import datetime, timedelta

from ..providers.base import LanguageModel
from ..providers.types import Content, TextContent, ReasoningContent
from ..utils.text_utils import get_potential_start_index
from .types import GenerateTextParams, GenerateTextResult, StreamTextResult
from .base import SimpleMiddleware, LanguageModelMiddleware


# Simple in-memory cache for demonstration
# In production, you'd use Redis, Memcached, or similar
_cache_store: Dict[str, Dict[str, Any]] = {}


def logging_middleware(
    logger: Optional[logging.Logger] = None,
    level: str = "INFO",
    include_params: bool = True,
    include_response: bool = True,
    include_timing: bool = True,
) -> LanguageModelMiddleware:
    """Create a logging middleware for request/response tracking.
    
    This middleware logs requests and responses to help with debugging,
    monitoring, and audit trails. It can be configured to include or
    exclude specific information.
    
    Args:
        logger: Logger to use (defaults to 'ai_sdk.middleware.logging')
        level: Logging level to use ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        include_params: Whether to log request parameters
        include_response: Whether to log response content
        include_timing: Whether to log request timing
        
    Returns:
        A configured logging middleware
        
    Example:
        ```python
        middleware = logging_middleware(
            level="DEBUG",
            include_params=True,
            include_response=False  # Don't log potentially sensitive responses
        )
        ```
    """
    if logger is None:
        logger = logging.getLogger("ai_sdk.middleware.logging")
    
    log_level = getattr(logging, level.upper())
    
    async def wrap_generate(*, do_generate, params, model):
        start_time = time.time() if include_timing else None
        
        if include_params:
            logger.log(log_level, f"Generate request to {model.provider}/{model.model_id}: {len(params.get('messages', []))} messages")
        else:
            logger.log(log_level, f"Generate request to {model.provider}/{model.model_id}")
        
        try:
            result = await do_generate()
            
            if include_timing:
                duration = time.time() - start_time
                logger.log(log_level, f"Generate completed in {duration:.2f}s")
            
            if include_response:
                response_preview = (result.text[:100] + "...") if len(result.text) > 100 else result.text
                logger.log(log_level, f"Generated response: {response_preview}")
            
            return result
            
        except Exception as e:
            if include_timing:
                duration = time.time() - start_time
                logger.error(f"Generate failed after {duration:.2f}s: {e}")
            else:
                logger.error(f"Generate failed: {e}")
            raise
    
    async def wrap_stream(*, do_stream, params, model):
        logger.log(log_level, f"Stream request to {model.provider}/{model.model_id}")
        
        try:
            result = await do_stream()
            logger.log(log_level, "Stream initiated successfully")
            return result
            
        except Exception as e:
            logger.error(f"Stream failed: {e}")
            raise
    
    middleware = SimpleMiddleware()
    middleware.wrapGenerate = wrap_generate
    middleware.wrapStream = wrap_stream
    return middleware


def caching_middleware(
    ttl: int = 300,
    cache_key_fn: Optional[callable] = None,
    cache_store: Optional[Dict[str, Any]] = None,
) -> LanguageModelMiddleware:
    """Create a caching middleware for response optimization.
    
    This middleware caches responses to reduce API calls and improve performance.
    It's particularly useful for repeated requests with the same parameters.
    
    Args:
        ttl: Time-to-live for cached responses in seconds (default: 5 minutes)
        cache_key_fn: Custom function to generate cache keys from parameters
        cache_store: Custom cache store (defaults to in-memory dict)
        
    Returns:
        A configured caching middleware
        
    Warning:
        The default in-memory cache is not suitable for production use across
        multiple processes. Use Redis or similar for production deployments.
        
    Example:
        ```python
        # Simple caching
        middleware = caching_middleware(ttl=600)  # 10 minutes
        
        # Custom cache key function
        def my_cache_key(params):
            # Only cache based on the last message
            last_message = params["messages"][-1]["content"]
            return hashlib.md5(last_message.encode()).hexdigest()
        
        middleware = caching_middleware(
            ttl=300,
            cache_key_fn=my_cache_key
        )
        ```
    """
    cache = cache_store if cache_store is not None else _cache_store
    
    def default_cache_key(params: GenerateTextParams) -> str:
        """Default cache key generation based on request parameters."""
        # Create a deterministic hash of the parameters
        key_data = {
            "messages": params.get("messages", []),
            "temperature": params.get("temperature"),
            "max_tokens": params.get("max_tokens"),
            "stop": params.get("stop"),
            "top_p": params.get("top_p"),
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    key_fn = cache_key_fn or default_cache_key
    
    async def wrap_generate(*, do_generate, params, model):
        # Generate cache key
        cache_key = f"{model.provider}:{model.model_id}:{key_fn(params)}"
        
        # Check cache
        if cache_key in cache:
            cached_data = cache[cache_key]
            if datetime.now() < cached_data["expires_at"]:
                logging.getLogger("ai_sdk.middleware.caching").debug(f"Cache hit for key: {cache_key}")
                return cached_data["result"]
            else:
                # Expired, remove from cache
                del cache[cache_key]
        
        # Cache miss, execute request
        logging.getLogger("ai_sdk.middleware.caching").debug(f"Cache miss for key: {cache_key}")
        result = await do_generate()
        
        # Store in cache
        cache[cache_key] = {
            "result": result,
            "expires_at": datetime.now() + timedelta(seconds=ttl),
        }
        
        return result
    
    middleware = SimpleMiddleware()
    middleware.wrapGenerate = wrap_generate
    # Note: Streaming responses are not cached by default
    return middleware


def default_settings_middleware(
    default_temperature: Optional[float] = None,
    default_max_tokens: Optional[int] = None,
    default_system_message: Optional[str] = None,
    **other_defaults
) -> LanguageModelMiddleware:
    """Create a middleware that applies default settings to requests.
    
    This middleware applies default parameter values when they are not
    specified in the request. Useful for setting organization-wide defaults.
    
    Args:
        default_temperature: Default temperature value
        default_max_tokens: Default max tokens value  
        default_system_message: Default system message to prepend
        **other_defaults: Other default parameter values
        
    Returns:
        A configured default settings middleware
        
    Example:
        ```python
        middleware = default_settings_middleware(
            default_temperature=0.7,
            default_max_tokens=1000,
            default_system_message="You are a helpful assistant.",
        )
        ```
    """
    defaults = {
        "temperature": default_temperature,
        "max_tokens": default_max_tokens,
        **other_defaults
    }
    # Remove None values
    defaults = {k: v for k, v in defaults.items() if v is not None}
    
    async def transform_params(*, params, type, model):
        updated_params = dict(params)
        
        # Apply parameter defaults
        for key, value in defaults.items():
            if key not in updated_params or updated_params[key] is None:
                updated_params[key] = value
        
        # Handle system message
        if default_system_message:
            messages = list(updated_params.get("messages", []))
            if not messages or messages[0].get("role") != "system":
                messages.insert(0, {
                    "role": "system",
                    "content": default_system_message
                })
                updated_params["messages"] = messages
        
        return updated_params
    
    middleware = SimpleMiddleware()
    middleware.transformParams = transform_params
    return middleware


def telemetry_middleware(
    track_requests: bool = True,
    track_tokens: bool = True,
    track_timing: bool = True,
    callback: Optional[callable] = None,
) -> LanguageModelMiddleware:
    """Create a telemetry middleware for usage tracking.
    
    This middleware collects telemetry data about API usage including
    request counts, token usage, timing, and error rates. Data can be
    sent to external monitoring systems via the callback function.
    
    Args:
        track_requests: Whether to track request counts
        track_tokens: Whether to track token usage
        track_timing: Whether to track request timing
        callback: Function to call with telemetry data
        
    Returns:
        A configured telemetry middleware
        
    Example:
        ```python
        def send_to_datadog(data):
            # Send metrics to monitoring system
            pass
        
        middleware = telemetry_middleware(
            track_requests=True,
            track_tokens=True,
            callback=send_to_datadog
        )
        ```
    """
    logger = logging.getLogger("ai_sdk.middleware.telemetry")
    
    async def wrap_generate(*, do_generate, params, model):
        start_time = time.time() if track_timing else None
        
        telemetry_data = {
            "provider": model.provider,
            "model": model.model_id,
            "operation": "generate",
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        try:
            result = await do_generate()
            
            # Track success
            telemetry_data["status"] = "success"
            
            if track_timing and start_time:
                telemetry_data["duration_ms"] = int((time.time() - start_time) * 1000)
            
            if track_tokens and hasattr(result, 'usage') and result.usage:
                telemetry_data["input_tokens"] = result.usage.prompt_tokens
                telemetry_data["output_tokens"] = result.usage.completion_tokens
                telemetry_data["total_tokens"] = result.usage.total_tokens
            
            if track_requests:
                telemetry_data["request_count"] = 1
            
            # Send telemetry data
            if callback:
                try:
                    await callback(telemetry_data) if asyncio.iscoroutinefunction(callback) else callback(telemetry_data)
                except Exception as e:
                    logger.warning(f"Failed to send telemetry data: {e}")
            else:
                logger.info(f"Telemetry: {telemetry_data}")
            
            return result
            
        except Exception as e:
            # Track error
            telemetry_data["status"] = "error"
            telemetry_data["error"] = str(e)
            
            if track_timing and start_time:
                telemetry_data["duration_ms"] = int((time.time() - start_time) * 1000)
            
            # Send error telemetry
            if callback:
                try:
                    await callback(telemetry_data) if asyncio.iscoroutinefunction(callback) else callback(telemetry_data)
                except Exception as cb_e:
                    logger.warning(f"Failed to send error telemetry: {cb_e}")
            else:
                logger.info(f"Error Telemetry: {telemetry_data}")
            
            raise
    
    async def wrap_stream(*, do_stream, params, model):
        start_time = time.time() if track_timing else None
        
        telemetry_data = {
            "provider": model.provider,
            "model": model.model_id,
            "operation": "stream",
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        try:
            result = await do_stream()
            
            telemetry_data["status"] = "success"
            
            if track_timing and start_time:
                telemetry_data["duration_ms"] = int((time.time() - start_time) * 1000)
            
            if track_requests:
                telemetry_data["request_count"] = 1
            
            if callback:
                try:
                    await callback(telemetry_data) if asyncio.iscoroutinefunction(callback) else callback(telemetry_data)
                except Exception as e:
                    logger.warning(f"Failed to send stream telemetry data: {e}")
            else:
                logger.info(f"Stream Telemetry: {telemetry_data}")
            
            return result
            
        except Exception as e:
            telemetry_data["status"] = "error"
            telemetry_data["error"] = str(e)
            
            if callback:
                try:
                    await callback(telemetry_data) if asyncio.iscoroutinefunction(callback) else callback(telemetry_data)
                except Exception as cb_e:
                    logger.warning(f"Failed to send stream error telemetry: {cb_e}")
            else:
                logger.info(f"Stream Error Telemetry: {telemetry_data}")
            
            raise
    
    middleware = SimpleMiddleware()
    middleware.wrapGenerate = wrap_generate
    middleware.wrapStream = wrap_stream
    return middleware


def extract_reasoning_middleware(
    tag_name: str,
    separator: str = "\n",
    start_with_reasoning: bool = False,
) -> LanguageModelMiddleware:
    """Create a middleware to extract XML-tagged reasoning sections from responses.
    
    This middleware extracts reasoning sections wrapped in XML tags (e.g., <thinking>)
    from the generated text and exposes them as separate reasoning content parts.
    This is useful for models that include their reasoning process in the response.
    
    Args:
        tag_name: The XML tag name to extract reasoning from (e.g., "thinking")
        separator: Separator to use between reasoning and text sections
        start_with_reasoning: Whether the response starts with reasoning tokens
        
    Returns:
        A configured reasoning extraction middleware
        
    Example:
        ```python
        # Extract <thinking> tags from responses
        middleware = extract_reasoning_middleware(
            tag_name="thinking",
            separator="\\n",
            start_with_reasoning=False
        )
        
        # For models that start responses with reasoning
        middleware = extract_reasoning_middleware(
            tag_name="reasoning",
            start_with_reasoning=True
        )
        ```
    """
    opening_tag = f"<{tag_name}>"
    closing_tag = f"</{tag_name}>"
    
    async def wrap_generate(*, do_generate, params, model):
        result = await do_generate()
        
        transformed_content: List[Content] = []
        
        for part in result.content:
            if part.type != "text":
                transformed_content.append(part)
                continue
            
            text = opening_tag + part.text if start_with_reasoning else part.text
            
            # Find all reasoning sections
            pattern = rf"{re.escape(opening_tag)}(.*?){re.escape(closing_tag)}"
            matches = list(re.finditer(pattern, text, re.DOTALL))
            
            if not matches:
                transformed_content.append(part)
                continue
            
            # Extract reasoning text
            reasoning_text = separator.join(match.group(1) for match in matches)
            
            # Remove reasoning sections from text
            text_without_reasoning = text
            for match in reversed(matches):  # Reverse to maintain indices
                before_match = text_without_reasoning[:match.start()]
                after_match = text_without_reasoning[match.end():]
                
                # Add separator between sections if both have content
                connector = separator if (before_match and after_match) else ""
                text_without_reasoning = before_match + connector + after_match
            
            # Add reasoning content
            if reasoning_text.strip():
                transformed_content.append(ReasoningContent(
                    type="reasoning",
                    text=reasoning_text,
                    provider_metadata=getattr(part, 'provider_metadata', None)
                ))
            
            # Add cleaned text content
            if text_without_reasoning.strip():
                transformed_content.append(TextContent(
                    type="text", 
                    text=text_without_reasoning
                ))
        
        # Return result with transformed content
        result.content = transformed_content
        return result
    
    # Note: Stream processing for reasoning extraction would be complex
    # due to the need to handle partial tags across stream chunks.
    # For now, we only support generate mode.
    
    middleware = SimpleMiddleware()
    middleware.wrapGenerate = wrap_generate
    return middleware


def simulate_streaming_middleware() -> LanguageModelMiddleware:
    """Create a middleware that simulates streaming from a generate call.
    
    This middleware is useful for testing streaming behavior when you have
    a model that only supports generate mode, or for consistent behavior
    across streaming and non-streaming code paths.
    
    Returns:
        A middleware that simulates streaming responses
        
    Example:
        ```python
        # Make any model "streamable"
        middleware = simulate_streaming_middleware()
        
        wrapped_model = wrap_language_model(
            model=non_streaming_model,
            middleware=[middleware]
        )
        
        # Now you can use stream_text even with non-streaming models
        async for chunk in stream_text(model=wrapped_model, prompt="Hello"):
            print(chunk.text_delta)
        ```
    """
    async def wrap_stream(*, do_generate, params, model):
        # Call generate instead of stream
        result = await do_generate()
        
        # Create a simulated stream from the result
        async def simulate_stream():
            # Simulate stream-start
            yield {
                "type": "stream-start",
                "warnings": getattr(result, 'warnings', None)
            }
            
            # Simulate response metadata
            if hasattr(result, 'response_metadata') and result.response_metadata:
                yield {
                    "type": "response-metadata",
                    **result.response_metadata
                }
            
            text_id = 0
            reasoning_id = 0
            
            for part in result.content:
                if part.type == "text" and part.text:
                    yield {"type": "text-start", "id": str(text_id)}
                    yield {
                        "type": "text-delta", 
                        "id": str(text_id),
                        "text_delta": part.text
                    }
                    yield {"type": "text-end", "id": str(text_id)}
                    text_id += 1
                    
                elif part.type == "reasoning" and part.text:
                    yield {
                        "type": "reasoning-start",
                        "id": str(reasoning_id),
                        "provider_metadata": getattr(part, 'provider_metadata', None)
                    }
                    yield {
                        "type": "reasoning-delta",
                        "id": str(reasoning_id), 
                        "delta": part.text
                    }
                    yield {"type": "reasoning-end", "id": str(reasoning_id)}
                    reasoning_id += 1
                    
                else:
                    # Pass through other content types
                    yield part.dict() if hasattr(part, 'dict') else part
            
            # Simulate finish
            yield {
                "type": "finish",
                "finish_reason": result.finish_reason,
                "usage": result.usage.dict() if hasattr(result.usage, 'dict') else result.usage,
                "provider_metadata": getattr(result, 'provider_metadata', None)
            }
        
        # Return the simulated stream
        return {
            "stream": simulate_stream(),
            "request_metadata": getattr(result, 'request_metadata', None),
            "response_metadata": getattr(result, 'response_metadata', None)
        }
    
    middleware = SimpleMiddleware()
    middleware.wrapStream = wrap_stream
    return middleware