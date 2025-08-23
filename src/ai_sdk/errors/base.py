"""Base error classes for AI SDK Python."""

from __future__ import annotations

from typing import Any, Dict, Optional


class AISDKError(Exception):
    """Base exception for all AI SDK errors."""
    
    def __init__(
        self,
        message: str,
        cause: Optional[Exception] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize the error.
        
        Args:
            message: Error message
            cause: Underlying cause of the error
            metadata: Additional error metadata
        """
        super().__init__(message)
        self.message = message
        self.cause = cause
        self.metadata = metadata or {}


class APIError(AISDKError):
    """Error from an API call to a provider."""
    
    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_body: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize the API error.
        
        Args:
            message: Error message
            status_code: HTTP status code
            response_body: Response body content
            headers: Response headers
            cause: Underlying cause of the error
        """
        super().__init__(
            message,
            cause=cause,
            metadata={
                "status_code": status_code,
                "response_body": response_body,
                "headers": headers,
            },
        )
        self.status_code = status_code
        self.response_body = response_body
        self.headers = headers


class InvalidArgumentError(AISDKError):
    """Error for invalid arguments passed to a function."""
    
    def __init__(
        self,
        message: str,
        argument: Optional[str] = None,
        value: Any = None,
    ) -> None:
        """Initialize the invalid argument error.
        
        Args:
            message: Error message
            argument: Name of the invalid argument
            value: Value of the invalid argument
        """
        super().__init__(
            message,
            metadata={"argument": argument, "value": value},
        )
        self.argument = argument
        self.value = value


class InvalidResponseError(AISDKError):
    """Error for invalid responses from providers."""
    
    def __init__(
        self,
        message: str,
        response_body: Optional[str] = None,
        expected_format: Optional[str] = None,
    ) -> None:
        """Initialize the invalid response error.
        
        Args:
            message: Error message
            response_body: Response body that was invalid
            expected_format: Expected response format
        """
        super().__init__(
            message,
            metadata={
                "response_body": response_body,
                "expected_format": expected_format,
            },
        )
        self.response_body = response_body
        self.expected_format = expected_format


class NetworkError(AISDKError):
    """Error for network-related issues."""
    
    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        cause: Optional[Exception] = None,
    ) -> None:
        """Initialize the network error.
        
        Args:
            message: Error message
            url: URL that failed
            cause: Underlying network error
        """
        super().__init__(
            message,
            cause=cause,
            metadata={"url": url},
        )
        self.url = url


class RateLimitError(APIError):
    """Error for rate limit exceeded."""
    
    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the rate limit error.
        
        Args:
            message: Error message
            retry_after: Number of seconds to wait before retrying
            **kwargs: Additional API error arguments
        """
        super().__init__(message, **kwargs)
        self.retry_after = retry_after
        self.metadata["retry_after"] = retry_after


class AuthenticationError(APIError):
    """Error for authentication failures."""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        **kwargs: Any,
    ) -> None:
        """Initialize the authentication error.
        
        Args:
            message: Error message
            **kwargs: Additional API error arguments
        """
        super().__init__(message, **kwargs)


class ModelNotFoundError(APIError):
    """Error for when a requested model is not found."""
    
    def __init__(
        self,
        message: str,
        model_id: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the model not found error.
        
        Args:
            message: Error message
            model_id: Model ID that was not found
            **kwargs: Additional API error arguments
        """
        super().__init__(message, **kwargs)
        self.model_id = model_id
        self.metadata["model_id"] = model_id


class ContentFilterError(APIError):
    """Error for content filtering violations."""
    
    def __init__(
        self,
        message: str = "Content was filtered",
        filter_type: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize the content filter error.
        
        Args:
            message: Error message
            filter_type: Type of content filter that triggered
            **kwargs: Additional API error arguments
        """
        super().__init__(message, **kwargs)
        self.filter_type = filter_type
        self.metadata["filter_type"] = filter_type


class NoObjectGeneratedError(AISDKError):
    """Error for when no valid object could be generated."""
    
    def __init__(
        self,
        message: str = "No valid object was generated",
        response_text: Optional[str] = None,
        schema_name: Optional[str] = None,
    ) -> None:
        """Initialize the no object generated error.
        
        Args:
            message: Error message
            response_text: The response text that failed to generate an object
            schema_name: Name of the schema that was expected
        """
        super().__init__(
            message,
            metadata={
                "response_text": response_text,
                "schema_name": schema_name,
            },
        )
        self.response_text = response_text
        self.schema_name = schema_name