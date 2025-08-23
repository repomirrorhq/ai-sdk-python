"""Provider registry implementation for managing multiple AI providers."""

from typing import Dict, Any, Optional, List, Union
from abc import ABC, abstractmethod

from ..providers.base import (
    Provider, 
    LanguageModel, 
    EmbeddingModel, 
    ImageModel, 
    SpeechModel, 
    TranscriptionModel
)
from ..middleware.base import LanguageModelMiddleware
from ..middleware.wrapper import wrap_language_model
from .errors import NoSuchProviderError, NoSuchModelError


class ProviderRegistry(ABC):
    """Abstract base class for provider registries."""
    
    @abstractmethod
    def language_model(self, model_id: str) -> LanguageModel:
        """Get a language model by ID."""
        pass
    
    @abstractmethod  
    def embedding_model(self, model_id: str) -> EmbeddingModel:
        """Get an embedding model by ID."""
        pass
    
    @abstractmethod
    def image_model(self, model_id: str) -> ImageModel:
        """Get an image model by ID."""
        pass
    
    @abstractmethod
    def speech_model(self, model_id: str) -> SpeechModel:
        """Get a speech model by ID."""
        pass
    
    @abstractmethod
    def transcription_model(self, model_id: str) -> TranscriptionModel:
        """Get a transcription model by ID."""
        pass


class DefaultProviderRegistry(ProviderRegistry):
    """Default implementation of provider registry.
    
    This registry allows registering multiple providers and accessing their
    models using a unified interface with `provider:model` format.
    """
    
    def __init__(
        self,
        separator: str = ":",
        language_model_middleware: Optional[Union[LanguageModelMiddleware, List[LanguageModelMiddleware]]] = None
    ):
        self.providers: Dict[str, Provider] = {}
        self.separator = separator
        self.language_model_middleware = language_model_middleware
    
    def register_provider(self, provider_id: str, provider: Provider) -> None:
        """Register a provider in the registry.
        
        Args:
            provider_id: Unique identifier for the provider
            provider: Provider instance to register
        """
        self.providers[provider_id] = provider
    
    def unregister_provider(self, provider_id: str) -> None:
        """Remove a provider from the registry.
        
        Args:
            provider_id: ID of the provider to remove
        """
        if provider_id in self.providers:
            del self.providers[provider_id]
    
    def list_providers(self) -> List[str]:
        """Get a list of registered provider IDs.
        
        Returns:
            List of provider IDs
        """
        return list(self.providers.keys())
    
    def get_provider(self, provider_id: str, model_type: str) -> Provider:
        """Get a provider by ID.
        
        Args:
            provider_id: ID of the provider
            model_type: Type of model being requested (for error messages)
            
        Returns:
            Provider instance
            
        Raises:
            NoSuchProviderError: If provider is not found
        """
        if provider_id not in self.providers:
            raise NoSuchProviderError(
                provider_id=provider_id,
                model_id=f"{provider_id}{self.separator}unknown",
                model_type=model_type,
                available_providers=list(self.providers.keys())
            )
        
        return self.providers[provider_id]
    
    def split_model_id(self, model_id: str, model_type: str) -> tuple[str, str]:
        """Split a model ID into provider ID and model name.
        
        Args:
            model_id: Full model ID in format "provider:model"
            model_type: Type of model being requested
            
        Returns:
            Tuple of (provider_id, model_name)
            
        Raises:
            NoSuchModelError: If model ID format is invalid
        """
        if self.separator not in model_id:
            raise NoSuchModelError(
                model_id=model_id,
                model_type=model_type,
                message=(
                    f"Invalid {model_type} id for registry: {model_id} "
                    f"(must be in the format 'providerId{self.separator}modelId')"
                )
            )
        
        provider_id, model_name = model_id.split(self.separator, 1)
        return provider_id, model_name
    
    def language_model(self, model_id: str) -> LanguageModel:
        """Get a language model by ID.
        
        Args:
            model_id: Model ID in format "provider:model"
            
        Returns:
            Language model instance
            
        Raises:
            NoSuchProviderError: If provider is not found
            NoSuchModelError: If model is not found
        """
        provider_id, model_name = self.split_model_id(model_id, "language_model")
        provider = self.get_provider(provider_id, "language_model")
        
        model = provider.language_model(model_name)
        if model is None:
            raise NoSuchModelError(
                model_id=model_id,
                model_type="language_model",
                provider_id=provider_id
            )
        
        # Apply middleware if configured
        if self.language_model_middleware is not None:
            model = wrap_language_model(
                model=model,
                middleware=self.language_model_middleware
            )
        
        return model
    
    def embedding_model(self, model_id: str) -> EmbeddingModel:
        """Get an embedding model by ID.
        
        Args:
            model_id: Model ID in format "provider:model"
            
        Returns:
            Embedding model instance
        """
        provider_id, model_name = self.split_model_id(model_id, "embedding_model")
        provider = self.get_provider(provider_id, "embedding_model")
        
        model = provider.embedding_model(model_name)
        if model is None:
            raise NoSuchModelError(
                model_id=model_id,
                model_type="embedding_model",
                provider_id=provider_id
            )
        
        return model
    
    def image_model(self, model_id: str) -> ImageModel:
        """Get an image model by ID.
        
        Args:
            model_id: Model ID in format "provider:model"
            
        Returns:
            Image model instance
        """
        provider_id, model_name = self.split_model_id(model_id, "image_model")
        provider = self.get_provider(provider_id, "image_model")
        
        model = provider.image_model(model_name)
        if model is None:
            raise NoSuchModelError(
                model_id=model_id,
                model_type="image_model",
                provider_id=provider_id
            )
        
        return model
    
    def speech_model(self, model_id: str) -> SpeechModel:
        """Get a speech model by ID.
        
        Args:
            model_id: Model ID in format "provider:model"
            
        Returns:
            Speech model instance
        """
        provider_id, model_name = self.split_model_id(model_id, "speech_model")
        provider = self.get_provider(provider_id, "speech_model")
        
        model = provider.speech_model(model_name)
        if model is None:
            raise NoSuchModelError(
                model_id=model_id,
                model_type="speech_model", 
                provider_id=provider_id
            )
        
        return model
    
    def transcription_model(self, model_id: str) -> TranscriptionModel:
        """Get a transcription model by ID.
        
        Args:
            model_id: Model ID in format "provider:model"
            
        Returns:
            Transcription model instance
        """
        provider_id, model_name = self.split_model_id(model_id, "transcription_model")
        provider = self.get_provider(provider_id, "transcription_model")
        
        model = provider.transcription_model(model_name)
        if model is None:
            raise NoSuchModelError(
                model_id=model_id,
                model_type="transcription_model",
                provider_id=provider_id
            )
        
        return model


def create_provider_registry(
    providers: Dict[str, Provider],
    *,
    separator: str = ":",
    language_model_middleware: Optional[Union[LanguageModelMiddleware, List[LanguageModelMiddleware]]] = None
) -> ProviderRegistry:
    """Create a provider registry with the given providers.
    
    This function allows you to register multiple providers and optionally apply
    middleware to all language models from the registry.
    
    Args:
        providers: Dictionary mapping provider IDs to provider instances
        separator: Separator used between provider ID and model ID (default: ":")
        language_model_middleware: Optional middleware to apply to all language models
        
    Returns:
        Provider registry instance
        
    Example:
        ```python
        from ai_sdk import create_openai, create_anthropic
        from ai_sdk.registry import create_provider_registry
        from ai_sdk.middleware import logging_middleware
        
        registry = create_provider_registry(
            {
                "openai": create_openai(),
                "anthropic": create_anthropic(),
            },
            language_model_middleware=logging_middleware()
        )
        
        # Access models through registry
        gpt4 = registry.language_model("openai:gpt-4")
        claude = registry.language_model("anthropic:claude-3-sonnet")
        ```
    """
    registry = DefaultProviderRegistry(
        separator=separator,
        language_model_middleware=language_model_middleware
    )
    
    for provider_id, provider in providers.items():
        registry.register_provider(provider_id, provider)
    
    return registry