"""
Groq Provider Implementation

High-speed inference provider using Groq's Language Processing Units (LPUs)
for ultra-fast AI model serving.
"""

from __future__ import annotations

import os
from typing import Optional, Dict, Any, Callable

from ..base import Provider, LanguageModel, TranscriptionModel
from ..types import ProviderMetadata
from .language_model import GroqChatLanguageModel
from .transcription_model import GroqTranscriptionModel
from .types import GroqChatModelId, GroqTranscriptionModelId


class GroqProvider(Provider):
    """Groq AI provider for high-speed inference."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        fetch_implementation: Optional[Callable] = None,
    ):
        """Initialize Groq provider.
        
        Args:
            api_key: Groq API key. If not provided, will look for GROQ_API_KEY environment variable
            base_url: Base URL for Groq API. Defaults to https://api.groq.com/openai/v1
            headers: Additional headers to include in requests
            fetch_implementation: Custom fetch implementation
        """
        self._api_key = api_key or os.getenv("GROQ_API_KEY")
        if not self._api_key:
            raise ValueError(
                "Groq API key is required. Either pass api_key parameter or set GROQ_API_KEY environment variable."
            )
            
        self._base_url = base_url or "https://api.groq.com/openai/v1"
        if self._base_url.endswith("/"):
            self._base_url = self._base_url.rstrip("/")
            
        self._headers = headers or {}
        self._fetch_implementation = fetch_implementation
        
    @property
    def provider_id(self) -> str:
        return "groq"
        
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }
        headers.update(self._headers)
        return headers
        
    def __call__(self, model_id: GroqChatModelId) -> LanguageModel:
        """Create a language model instance."""
        return self.language_model(model_id)
        
    def language_model(self, model_id: GroqChatModelId) -> LanguageModel:
        """Create a chat language model.
        
        Args:
            model_id: The Groq model identifier
            
        Returns:
            GroqChatLanguageModel instance
        """
        return GroqChatLanguageModel(
            model_id=model_id,
            api_key=self._api_key,
            base_url=self._base_url,
            headers=self._get_headers(),
            fetch_implementation=self._fetch_implementation,
        )
        
    def chat(self, model_id: GroqChatModelId) -> LanguageModel:
        """Alias for language_model for compatibility."""
        return self.language_model(model_id)
        
    def transcription(self, model_id: GroqTranscriptionModelId) -> TranscriptionModel:
        """Create a transcription model.
        
        Args:
            model_id: The Groq transcription model identifier
            
        Returns:
            GroqTranscriptionModel instance
        """
        return GroqTranscriptionModel(
            model_id=model_id,
            api_key=self._api_key,
            base_url=self._base_url,
            headers=self._get_headers(),
            fetch_implementation=self._fetch_implementation,
        )
        
    def embedding_model(self, model_id: str):
        """Groq does not support embedding models."""
        raise NotImplementedError("Groq does not support embedding models")
        
    def image_model(self, model_id: str):
        """Groq does not support image generation models."""  
        raise NotImplementedError("Groq does not support image generation models")


def create_groq(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    fetch_implementation: Optional[Callable] = None,
) -> GroqProvider:
    """Create a Groq provider instance.
    
    Args:
        api_key: Groq API key. If not provided, will look for GROQ_API_KEY environment variable
        base_url: Base URL for Groq API. Defaults to https://api.groq.com/openai/v1
        headers: Additional headers to include in requests
        fetch_implementation: Custom fetch implementation
        
    Returns:
        GroqProvider instance
    """
    return GroqProvider(
        api_key=api_key,
        base_url=base_url,
        headers=headers,
        fetch_implementation=fetch_implementation,
    )


# Default instance for convenience
groq = create_groq()