"""
Error classes for Gateway Provider
"""

import json
from typing import Optional, Dict, Any, Union
from ai_sdk.errors.base import AISDKError


class GatewayError(AISDKError):
    """Base error class for Gateway provider errors"""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        **kwargs
    ):
        super().__init__(message, **kwargs)
        self.status_code = status_code
        self.response_body = response_body


class GatewayAuthenticationError(GatewayError):
    """Thrown when Gateway authentication fails"""
    
    @classmethod
    def create_contextual_error(
        cls,
        api_key_provided: bool,
        oidc_token_provided: bool,
        status_code: int = 401
    ) -> "GatewayAuthenticationError":
        if not api_key_provided and not oidc_token_provided:
            message = (
                "AI Gateway authentication failed. Please provide either:\n"
                "1. An API key via AI_GATEWAY_API_KEY environment variable or apiKey option\n"
                "2. Deploy to Vercel with OIDC token available"
            )
        elif api_key_provided:
            message = "AI Gateway authentication failed. The provided API key is invalid."
        else:
            message = "AI Gateway authentication failed. OIDC token validation failed."
            
        return cls(
            message=message,
            status_code=status_code
        )


class GatewayInvalidRequestError(GatewayError):
    """Thrown when the Gateway request is invalid"""
    pass


class GatewayRateLimitError(GatewayError):
    """Thrown when Gateway rate limits are exceeded"""
    pass


class GatewayModelNotFoundError(GatewayError):
    """Thrown when the requested model is not found"""
    
    def __init__(self, model_id: str, **kwargs):
        super().__init__(
            f"Gateway model '{model_id}' not found",
            **kwargs
        )
        self.model_id = model_id


class GatewayInternalServerError(GatewayError):
    """Thrown when Gateway has internal server errors"""
    pass


class GatewayResponseError(GatewayError):
    """Thrown when Gateway returns an unexpected response format"""
    pass


def as_gateway_error(
    error: Exception,
    auth_method: Optional[str] = None
) -> GatewayError:
    """Convert various errors to Gateway-specific errors"""
    
    if isinstance(error, GatewayError):
        return error
    
    # Handle HTTP errors (assuming we have status_code and response attributes)
    if hasattr(error, 'status_code') and hasattr(error, 'response'):
        status_code = getattr(error, 'status_code', None)
        response_body = getattr(error, 'response', None)
        
        if status_code == 401:
            return GatewayAuthenticationError.create_contextual_error(
                api_key_provided=auth_method == 'api-key',
                oidc_token_provided=auth_method == 'oidc',
                status_code=status_code
            )
        elif status_code == 400:
            return GatewayInvalidRequestError(
                str(error),
                status_code=status_code,
                response_body=response_body
            )
        elif status_code == 429:
            return GatewayRateLimitError(
                str(error),
                status_code=status_code,
                response_body=response_body
            )
        elif status_code == 404:
            return GatewayModelNotFoundError(
                "Model not found",
                status_code=status_code,
                response_body=response_body
            )
        elif status_code >= 500:
            return GatewayInternalServerError(
                str(error),
                status_code=status_code, 
                response_body=response_body
            )
    
    # Default to generic Gateway error
    return GatewayError(str(error))


def create_gateway_error_from_response(
    status_code: int,
    response_body: str
) -> GatewayError:
    """Create Gateway error from HTTP response"""
    
    try:
        data = json.loads(response_body)
        message = data.get('message', response_body)
    except (json.JSONDecodeError, AttributeError):
        message = response_body or f"HTTP {status_code} error"
    
    if status_code == 401:
        return GatewayAuthenticationError(
            message,
            status_code=status_code,
            response_body=response_body
        )
    elif status_code == 400:
        return GatewayInvalidRequestError(
            message,
            status_code=status_code,
            response_body=response_body
        )
    elif status_code == 429:
        return GatewayRateLimitError(
            message,
            status_code=status_code,
            response_body=response_body
        )
    elif status_code == 404:
        return GatewayModelNotFoundError(
            message,
            status_code=status_code,
            response_body=response_body
        )
    elif status_code >= 500:
        return GatewayInternalServerError(
            message,
            status_code=status_code,
            response_body=response_body
        )
    else:
        return GatewayResponseError(
            message,
            status_code=status_code,
            response_body=response_body
        )