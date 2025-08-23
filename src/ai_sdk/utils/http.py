"""HTTP utilities for AI SDK Python."""

import asyncio
from typing import Dict, Optional, TypeVar, Callable, Awaitable

import httpx

from ..errors import APIError

T = TypeVar('T')


def create_http_client(
    base_url: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    timeout: float = 60.0,
    **kwargs,
) -> httpx.AsyncClient:
    """Create an async HTTP client with default configuration.
    
    Args:
        base_url: Base URL for requests
        headers: Default headers
        timeout: Request timeout in seconds
        **kwargs: Additional httpx.AsyncClient arguments
        
    Returns:
        Configured async HTTP client
    """
    default_headers = {
        "User-Agent": "ai-sdk-python/0.1.0",
        "Content-Type": "application/json",
    }
    
    if headers:
        default_headers.update(headers)
    
    return httpx.AsyncClient(
        base_url=base_url,
        headers=default_headers,
        timeout=timeout,
        **kwargs,
    )


async def retry_with_exponential_backoff(
    func: Callable[[], Awaitable[T]],
    max_retries: int = 2,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
) -> T:
    """Retry a function with exponential backoff.
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay in seconds
        backoff_factor: Backoff multiplier
        
    Returns:
        Result of the function call
        
    Raises:
        The last exception if all retries fail
    """
    delay = initial_delay
    last_exception = None
    
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except Exception as e:
            last_exception = e
            if attempt == max_retries:
                # Last attempt failed, re-raise the exception
                break
            
            # Wait before retrying
            await asyncio.sleep(min(delay, max_delay))
            delay *= backoff_factor
    
    # Re-raise the last exception
    if last_exception is not None:
        raise last_exception
    else:
        raise RuntimeError("Retry failed without exception")


async def handle_http_error(response: httpx.Response, context: str) -> None:
    """Handle HTTP error responses.
    
    Args:
        response: The HTTP response object
        context: Context string for error messages
        
    Raises:
        APIError: For non-200 status codes
    """
    if response.status_code == 200:
        return
        
    try:
        error_data = response.json()
        error_message = error_data.get('error', {}).get('message', f'{context} request failed')
    except Exception:
        error_message = f'{context} request failed'
    
    raise APIError(
        f"{context} error: {response.status_code} - {error_message}",
        status_code=response.status_code,
        response_body=response.text,
    )