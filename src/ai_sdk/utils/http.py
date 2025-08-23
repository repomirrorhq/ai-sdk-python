"""HTTP utilities for AI SDK Python."""

from typing import Dict, Optional

import httpx


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