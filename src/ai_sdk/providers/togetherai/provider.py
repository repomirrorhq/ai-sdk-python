"""
Together AI Provider implementation

This provider integrates with Together AI's platform for accessing
100+ open-source AI models. It is built on top of the OpenAI-Compatible
provider since Together AI uses an OpenAI-compatible API.
"""

import os
from typing import Optional, Dict, Any

from ..base import BaseProvider
from ..openai_compatible import create_openai_compatible, OpenAICompatibleProviderSettings
from .image_model import TogetherAIImageModel
from .types import (
    TogetherAIChatModelId,
    TogetherAICompletionModelId,
    TogetherAIEmbeddingModelId,
    TogetherAIImageModelId,
    TogetherAIProviderSettings
)


class TogetherAIProvider(BaseProvider):
    """
    Provider for Together AI service.
    
    Together AI provides access to 100+ open-source models including
    LLaMA, Mixtral, Gemma, and other popular models with competitive pricing.
    
    This provider is built on the OpenAI-Compatible provider since
    Together AI uses an OpenAI-compatible API.
    """
    
    def __init__(self, settings: Optional[TogetherAIProviderSettings] = None):
        """
        Initialize Together AI provider.
        
        Args:
            settings: Together AI provider configuration settings
        """
        self.settings = settings or TogetherAIProviderSettings()
        
        # Create underlying OpenAI-compatible provider
        compatible_settings = OpenAICompatibleProviderSettings(
            name="togetherai",
            base_url=self.settings.base_url or "https://api.together.xyz/v1",
            api_key=self._get_api_key(),
            headers=self.settings.headers,
            query_params=self.settings.query_params,
            fetch=self.settings.fetch,
            include_usage=self.settings.include_usage,
        )
        
        self._provider = create_openai_compatible(compatible_settings)
    
    @property
    def name(self) -> str:
        return "togetherai"
    
    def __call__(self, model_id: TogetherAIChatModelId):
        """Create a language model instance (callable interface)"""
        return self.language_model(model_id)
    
    def language_model(self, model_id: TogetherAIChatModelId, **kwargs):
        """
        Create a language model instance.
        
        Args:
            model_id: Together AI model identifier
            **kwargs: Additional model configuration
            
        Returns:
            Language model instance
        """
        return self._provider.language_model(model_id)
    
    def chat_model(self, model_id: TogetherAIChatModelId, **kwargs):
        """
        Create a chat model instance.
        
        Args:
            model_id: Together AI chat model identifier
            **kwargs: Additional model configuration
            
        Returns:
            Chat model instance
        """
        return self._provider.chat_model(model_id)
    
    def completion_model(self, model_id: TogetherAICompletionModelId, **kwargs):
        """
        Create a completion model instance.
        
        Args:
            model_id: Together AI completion model identifier
            **kwargs: Additional model configuration
            
        Returns:
            Completion model instance
        """
        return self._provider.completion_model(model_id)
    
    def text_embedding_model(self, model_id: TogetherAIEmbeddingModelId, **kwargs):
        """
        Create a text embedding model instance.
        
        Args:
            model_id: Together AI embedding model identifier
            **kwargs: Additional model configuration
            
        Returns:
            Text embedding model instance
        """
        return self._provider.text_embedding_model(model_id)
    
    def image_model(self, model_id: TogetherAIImageModelId, **kwargs):
        """
        Create an image model instance.
        
        Args:
            model_id: Together AI image model identifier
            **kwargs: Additional model configuration
            
        Returns:
            Image model instance
        """
        # Use custom TogetherAI image model for proper API handling
        config = {
            'provider': 'togetherai.image',
            'base_url': self.settings.base_url or "https://api.together.xyz/v1",
            'headers': self._get_headers,
            'fetch': self.settings.fetch,
        }
        
        return TogetherAIImageModel(model_id, config)
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from settings or environment"""
        return (
            self.settings.api_key 
            or os.getenv("TOGETHER_AI_API_KEY")
            or os.getenv("TOGETHER_API_KEY")  # Alternative env var name
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API calls"""
        headers = {}
        
        # Add API key authentication
        api_key = self._get_api_key()
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        # Add custom headers
        if self.settings.headers:
            headers.update(self.settings.headers)
        
        return headers


def create_together(settings: Optional[TogetherAIProviderSettings] = None) -> TogetherAIProvider:
    """
    Create a Together AI provider instance.
    
    Args:
        settings: Together AI provider configuration settings
        
    Returns:
        Together AI provider instance
    """
    return TogetherAIProvider(settings)


# Default together provider instance for convenience
together = create_together()