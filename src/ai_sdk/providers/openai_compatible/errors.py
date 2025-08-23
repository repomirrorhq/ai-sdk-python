"""
Error handling for OpenAI-Compatible provider
"""

from typing import Optional, Dict, Any
from ...errors.base import AISDKError


class OpenAICompatibleError(AISDKError):
    """Base error class for OpenAI-Compatible provider"""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None,
        error_data: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        super().__init__(message, cause=cause)
        self.status_code = status_code
        self.error_data = error_data or {}


class OpenAICompatibleAuthenticationError(OpenAICompatibleError):
    """Authentication error for OpenAI-Compatible API"""
    pass


class OpenAICompatibleRateLimitError(OpenAICompatibleError):
    """Rate limit error for OpenAI-Compatible API"""
    pass


class OpenAICompatibleInvalidRequestError(OpenAICompatibleError):
    """Invalid request error for OpenAI-Compatible API"""
    pass


def as_openai_compatible_error(error: Exception, provider_name: str = "openai-compatible") -> OpenAICompatibleError:
    """Convert generic error to OpenAI-Compatible specific error"""
    
    if isinstance(error, OpenAICompatibleError):
        return error
    
    # Handle HTTP errors
    if hasattr(error, 'response') and hasattr(error.response, 'status_code'):
        status_code = error.response.status_code
        
        if status_code == 401:
            return OpenAICompatibleAuthenticationError(
                f"{provider_name} authentication failed", 
                status_code=status_code,
                cause=error
            )
        elif status_code == 429:
            return OpenAICompatibleRateLimitError(
                f"{provider_name} rate limit exceeded",
                status_code=status_code, 
                cause=error
            )
        elif status_code in (400, 422):
            return OpenAICompatibleInvalidRequestError(
                f"{provider_name} invalid request",
                status_code=status_code,
                cause=error
            )
    
    # Generic error conversion
    return OpenAICompatibleError(
        f"{provider_name} error: {str(error)}",
        cause=error
    )