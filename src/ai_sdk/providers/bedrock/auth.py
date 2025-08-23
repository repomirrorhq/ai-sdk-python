"""AWS SigV4 authentication for Bedrock API calls."""

from typing import Dict, Any, Optional, Callable, Awaitable, Union

import httpx

from .types import BedrockCredentials

try:
    from botocore.auth import SigV4Auth
    from botocore.awsrequest import AWSRequest
    from botocore.credentials import Credentials
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False


async def create_sigv4_fetch_function(
    get_credentials: Callable[[], Union[BedrockCredentials, Awaitable[BedrockCredentials]]],
    base_fetch: Optional[httpx.AsyncClient] = None
) -> Callable:
    """Create a fetch function that applies AWS SigV4 signing."""
    
    if not BOTO3_AVAILABLE:
        raise ImportError(
            "boto3 is required for AWS SigV4 authentication. "
            "Install it with: pip install 'ai-sdk[bedrock]'"
        )
    
    if base_fetch is None:
        base_fetch = httpx.AsyncClient()
    
    async def sigv4_fetch(
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        **kwargs
    ) -> httpx.Response:
        """Fetch function with SigV4 signing."""
        
        if method.upper() != 'POST' or not body:
            return await base_fetch.request(method, url, headers=headers, content=body, **kwargs)
            
        # Get credentials (handle both sync and async)
        credentials = get_credentials()
        if hasattr(credentials, '__await__'):
            credentials = await credentials
            
        # Create AWS request
        aws_request = AWSRequest(
            method=method,
            url=url,
            data=body,
            headers=headers or {}
        )
        
        # Create credentials object for botocore
        boto_credentials = Credentials(
            access_key=credentials.access_key_id,
            secret_key=credentials.secret_access_key,
            token=credentials.session_token
        )
        
        # Sign the request
        signer = SigV4Auth(boto_credentials, "bedrock", credentials.region)
        signer.add_auth(aws_request)
        
        # Convert back to httpx format
        signed_headers = dict(aws_request.headers)
        
        return await base_fetch.request(
            method, 
            url, 
            headers=signed_headers, 
            content=body, 
            **kwargs
        )
    
    return sigv4_fetch


async def create_api_key_fetch_function(
    api_key: str,
    base_fetch: Optional[httpx.AsyncClient] = None
) -> Callable:
    """Create a fetch function that uses Bearer token authentication."""
    
    if base_fetch is None:
        base_fetch = httpx.AsyncClient()
        
    async def api_key_fetch(
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        body: Optional[str] = None,
        **kwargs
    ) -> httpx.Response:
        """Fetch function with API key authentication."""
        
        request_headers = dict(headers) if headers else {}
        request_headers['authorization'] = f"Bearer {api_key}"
        
        return await base_fetch.request(method, url, headers=request_headers, content=body, **kwargs)
    
    return api_key_fetch