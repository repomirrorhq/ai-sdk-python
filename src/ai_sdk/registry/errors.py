"""Registry-specific error classes."""

from typing import List, Optional
from ..errors.base import AISDKError


class NoSuchProviderError(AISDKError):
    """Raised when a requested provider is not found in the registry."""
    
    def __init__(
        self,
        *,
        provider_id: str,
        model_id: str,
        model_type: str,
        available_providers: Optional[List[str]] = None,
        message: Optional[str] = None
    ):
        self.provider_id = provider_id
        self.model_id = model_id
        self.model_type = model_type
        self.available_providers = available_providers or []
        
        if message is None:
            available = ", ".join(self.available_providers) if self.available_providers else "none"
            message = (
                f"No such provider '{provider_id}' for {model_type} '{model_id}'. "
                f"Available providers: {available}"
            )
        
        super().__init__(message)


class NoSuchModelError(AISDKError):
    """Raised when a requested model is not found in a provider."""
    
    def __init__(
        self,
        *,
        model_id: str,
        model_type: str,
        provider_id: Optional[str] = None,
        message: Optional[str] = None
    ):
        self.model_id = model_id
        self.model_type = model_type
        self.provider_id = provider_id
        
        if message is None:
            provider_part = f" from provider '{provider_id}'" if provider_id else ""
            message = f"No such {model_type} '{model_id}'{provider_part}"
        
        super().__init__(message)