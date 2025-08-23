"""OpenAI provider implementation."""

from __future__ import annotations

import os
from typing import Any, Optional

from ..base import EmbeddingModel, LanguageModel, Provider
from .embedding_model import OpenAIEmbeddingModel
from .language_model import OpenAIChatLanguageModel


class OpenAIProvider(Provider):
    """OpenAI provider for language models, embeddings, and more."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        organization: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Initialize OpenAI provider.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            base_url: Base URL for API requests (defaults to OpenAI's API)
            organization: OpenAI organization ID
            **kwargs: Additional configuration options
        """
        # Load API key from environment if not provided
        if api_key is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key is None:
                raise ValueError(
                    "OpenAI API key not found. Please provide it via the 'api_key' "
                    "parameter or set the OPENAI_API_KEY environment variable."
                )
        
        super().__init__(api_key=api_key, **kwargs)
        self.base_url = base_url or "https://api.openai.com/v1"
        self.organization = organization
    
    @property
    def name(self) -> str:
        """Name of the provider."""
        return "openai"
    
    def language_model(
        self,
        model_id: str = "gpt-3.5-turbo",
        **kwargs: Any,
    ) -> LanguageModel:
        """Get an OpenAI language model.
        
        Args:
            model_id: OpenAI model ID (e.g., "gpt-4", "gpt-3.5-turbo")
            **kwargs: Additional model configuration
            
        Returns:
            OpenAI language model instance
        """
        return OpenAIChatLanguageModel(
            provider=self,
            model_id=model_id,
            **kwargs,
        )
    
    def chat(self, model_id: str = "gpt-3.5-turbo", **kwargs: Any) -> LanguageModel:
        """Alias for language_model() for compatibility."""
        return self.language_model(model_id=model_id, **kwargs)
    
    def embedding_model(
        self,
        model_id: str = "text-embedding-3-small",
        **kwargs: Any,
    ) -> EmbeddingModel:
        """Get an OpenAI embedding model.
        
        Args:
            model_id: OpenAI embedding model ID 
                     (e.g., "text-embedding-3-small", "text-embedding-3-large", "text-embedding-ada-002")
            **kwargs: Additional model configuration
            
        Returns:
            OpenAI embedding model instance
        """
        return OpenAIEmbeddingModel(
            provider=self,
            model_id=model_id,
            **kwargs,
        )
    
    def embedding(self, model_id: str = "text-embedding-3-small", **kwargs: Any) -> EmbeddingModel:
        """Alias for embedding_model() for compatibility."""
        return self.embedding_model(model_id=model_id, **kwargs)