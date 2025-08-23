"""Mistral AI provider implementation."""

import os
from typing import Optional, Dict, Any
from pydantic import BaseModel

from ...providers.base import Provider, LanguageModel, EmbeddingModel
from ...utils.http import create_http_client
from .types import MistralChatModelId, MistralEmbeddingModelId
from .language_model import MistralLanguageModel


class MistralProviderSettings(BaseModel):
    """Settings for Mistral AI provider."""
    
    # API configuration
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    
    # Custom settings  
    headers: Optional[Dict[str, str]] = None
    
    # HTTP client settings
    timeout: Optional[int] = 60
    max_retries: Optional[int] = 3


class MistralProvider(Provider):
    """Mistral AI provider."""
    
    def __init__(self, settings: MistralProviderSettings):
        self.settings = settings
        self._http_client = None
        
    def _get_http_client(self):
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = create_http_client(
                timeout=self.settings.timeout,
                max_retries=self.settings.max_retries
            )
        return self._http_client
    
    def _get_api_key(self) -> str:
        """Get API key from settings or environment."""
        api_key = self.settings.api_key or os.getenv("MISTRAL_API_KEY")
        if not api_key:
            raise ValueError(
                "Mistral API key is required. Set MISTRAL_API_KEY environment variable "
                "or provide api_key in MistralProviderSettings."
            )
        return api_key
    
    def _get_base_url(self) -> str:
        """Get base URL for Mistral API."""
        return self.settings.base_url or "https://api.mistral.ai/v1"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        api_key = self._get_api_key()
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        
        # Add custom headers if provided
        if self.settings.headers:
            headers.update(self.settings.headers)
            
        return headers
    
    async def language_model(self, model_id: MistralChatModelId, **kwargs) -> LanguageModel:
        """Create a Mistral language model."""
        http_client = self._get_http_client()
        base_url = self._get_base_url()
        headers = self._get_headers()
        
        return MistralLanguageModel(
            model_id=model_id,
            base_url=base_url,
            headers=headers,
            http_client=http_client,
            **kwargs
        )
    
    async def embedding_model(self, model_id: MistralEmbeddingModelId, **kwargs) -> EmbeddingModel:
        """Create a Mistral embedding model."""
        from .embedding_model import MistralEmbeddingModel
        
        api_key = self._get_api_key()
        base_url = self._get_base_url()
        
        return MistralEmbeddingModel(
            model_id=model_id,
            api_key=api_key,
            base_url=base_url,
            **kwargs
        )
        
    async def close(self):
        """Close the HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None


def create_mistral(settings: Optional[MistralProviderSettings] = None) -> MistralProvider:
    """Create a Mistral provider instance."""
    if settings is None:
        settings = MistralProviderSettings()
    return MistralProvider(settings)


# Default instance
mistral = create_mistral()