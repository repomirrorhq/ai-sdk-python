"""Error classes for AI SDK Python."""

from .base import (
    AISDKError,
    APIError,
    InvalidArgumentError,
    InvalidResponseError,
    NetworkError,
    RateLimitError,
    AuthenticationError,
    ModelNotFoundError,
    ContentFilterError,
    NoObjectGeneratedError,
    LoadAPIKeyError,
)

# Aliases for compatibility
NoSuchModelError = ModelNotFoundError
APICallError = APIError

__all__ = [
    "AISDKError",
    "APIError",
    "APICallError",
    "InvalidArgumentError",
    "InvalidResponseError",
    "NetworkError",
    "RateLimitError",
    "AuthenticationError",
    "ModelNotFoundError",
    "NoSuchModelError",
    "ContentFilterError",
    "NoObjectGeneratedError",
    "LoadAPIKeyError",
]