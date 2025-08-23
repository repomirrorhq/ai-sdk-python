"""Custom provider implementation for creating providers with specific models."""

from typing import Dict, Optional, Any, TypeVar, Generic

from ..providers.base import (
    Provider,
    LanguageModel,
    EmbeddingModel, 
    ImageModel,
    SpeechModel,
    TranscriptionModel
)
from .errors import NoSuchModelError


T = TypeVar('T')


class CustomProvider(Provider):
    """Custom provider that allows specifying individual models with fallback support.
    
    This provider allows you to create a custom provider by specifying individual
    models of different types. It supports fallback to another provider when a
    requested model is not found in the custom mappings.
    """
    
    def __init__(
        self,
        *,
        language_models: Optional[Dict[str, LanguageModel]] = None,
        embedding_models: Optional[Dict[str, EmbeddingModel]] = None,
        image_models: Optional[Dict[str, ImageModel]] = None,
        speech_models: Optional[Dict[str, SpeechModel]] = None,
        transcription_models: Optional[Dict[str, TranscriptionModel]] = None,
        fallback_provider: Optional[Provider] = None
    ):
        """Initialize custom provider.
        
        Args:
            language_models: Dictionary of language models by ID
            embedding_models: Dictionary of embedding models by ID
            image_models: Dictionary of image models by ID
            speech_models: Dictionary of speech models by ID
            transcription_models: Dictionary of transcription models by ID
            fallback_provider: Optional fallback provider for unknown models
        """
        self._language_models = language_models or {}
        self._embedding_models = embedding_models or {}
        self._image_models = image_models or {}
        self._speech_models = speech_models or {}
        self._transcription_models = transcription_models or {}
        self._fallback_provider = fallback_provider
        
        # Provider metadata
        self.provider_id = "custom"
        self.provider_name = "Custom Provider"
    
    def language_model(self, model_id: str) -> Optional[LanguageModel]:
        """Get a language model by ID.
        
        Args:
            model_id: ID of the model to retrieve
            
        Returns:
            Language model instance or None if not found
        """
        if model_id in self._language_models:
            return self._language_models[model_id]
        
        if self._fallback_provider:
            return self._fallback_provider.language_model(model_id)
        
        return None
    
    def embedding_model(self, model_id: str) -> Optional[EmbeddingModel]:
        """Get an embedding model by ID.
        
        Args:
            model_id: ID of the model to retrieve
            
        Returns:
            Embedding model instance or None if not found
        """
        if model_id in self._embedding_models:
            return self._embedding_models[model_id]
        
        if self._fallback_provider:
            return self._fallback_provider.embedding_model(model_id)
        
        return None
    
    def image_model(self, model_id: str) -> Optional[ImageModel]:
        """Get an image model by ID.
        
        Args:
            model_id: ID of the model to retrieve
            
        Returns:
            Image model instance or None if not found
        """
        if model_id in self._image_models:
            return self._image_models[model_id]
        
        if self._fallback_provider:
            return self._fallback_provider.image_model(model_id)
        
        return None
    
    def speech_model(self, model_id: str) -> Optional[SpeechModel]:
        """Get a speech model by ID.
        
        Args:
            model_id: ID of the model to retrieve
            
        Returns:
            Speech model instance or None if not found
        """
        if model_id in self._speech_models:
            return self._speech_models[model_id]
        
        if self._fallback_provider:
            return self._fallback_provider.speech_model(model_id)
        
        return None
    
    def transcription_model(self, model_id: str) -> Optional[TranscriptionModel]:
        """Get a transcription model by ID.
        
        Args:
            model_id: ID of the model to retrieve
            
        Returns:
            Transcription model instance or None if not found
        """
        if model_id in self._transcription_models:
            return self._transcription_models[model_id]
        
        if self._fallback_provider:
            return self._fallback_provider.transcription_model(model_id)
        
        return None
    
    def add_language_model(self, model_id: str, model: LanguageModel) -> None:
        """Add a language model to the custom provider.
        
        Args:
            model_id: ID for the model
            model: Language model instance
        """
        self._language_models[model_id] = model
    
    def add_embedding_model(self, model_id: str, model: EmbeddingModel) -> None:
        """Add an embedding model to the custom provider.
        
        Args:
            model_id: ID for the model
            model: Embedding model instance
        """
        self._embedding_models[model_id] = model
    
    def add_image_model(self, model_id: str, model: ImageModel) -> None:
        """Add an image model to the custom provider.
        
        Args:
            model_id: ID for the model
            model: Image model instance
        """
        self._image_models[model_id] = model
    
    def add_speech_model(self, model_id: str, model: SpeechModel) -> None:
        """Add a speech model to the custom provider.
        
        Args:
            model_id: ID for the model
            model: Speech model instance
        """
        self._speech_models[model_id] = model
    
    def add_transcription_model(self, model_id: str, model: TranscriptionModel) -> None:
        """Add a transcription model to the custom provider.
        
        Args:
            model_id: ID for the model
            model: Transcription model instance
        """
        self._transcription_models[model_id] = model
    
    def remove_model(self, model_type: str, model_id: str) -> bool:
        """Remove a model from the custom provider.
        
        Args:
            model_type: Type of model ("language", "embedding", "image", "speech", "transcription")
            model_id: ID of the model to remove
            
        Returns:
            True if model was removed, False if not found
        """
        model_dict = {
            "language": self._language_models,
            "embedding": self._embedding_models,
            "image": self._image_models,
            "speech": self._speech_models,
            "transcription": self._transcription_models
        }.get(model_type)
        
        if model_dict and model_id in model_dict:
            del model_dict[model_id]
            return True
        
        return False
    
    def list_models(self, model_type: str) -> list[str]:
        """List available models of a given type.
        
        Args:
            model_type: Type of model to list
            
        Returns:
            List of model IDs
        """
        model_dict = {
            "language": self._language_models,
            "embedding": self._embedding_models,
            "image": self._image_models,
            "speech": self._speech_models,
            "transcription": self._transcription_models
        }.get(model_type)
        
        if model_dict:
            return list(model_dict.keys())
        
        return []


def custom_provider(
    *,
    language_models: Optional[Dict[str, LanguageModel]] = None,
    embedding_models: Optional[Dict[str, EmbeddingModel]] = None,
    image_models: Optional[Dict[str, ImageModel]] = None,
    speech_models: Optional[Dict[str, SpeechModel]] = None,
    transcription_models: Optional[Dict[str, TranscriptionModel]] = None,
    fallback_provider: Optional[Provider] = None
) -> Provider:
    """Create a custom provider with specified models.
    
    This function creates a custom provider that allows you to specify individual
    models for different types. It supports fallback to another provider when a
    requested model is not found.
    
    Args:
        language_models: Dictionary of language models by ID
        embedding_models: Dictionary of embedding models by ID  
        image_models: Dictionary of image models by ID
        speech_models: Dictionary of speech models by ID
        transcription_models: Dictionary of transcription models by ID
        fallback_provider: Optional fallback provider for unknown models
        
    Returns:
        Custom provider instance
        
    Example:
        ```python
        from ai_sdk import create_openai, create_anthropic
        from ai_sdk.registry import custom_provider
        
        # Create base providers
        openai = create_openai()
        anthropic = create_anthropic()
        
        # Create custom provider with specific models
        custom = custom_provider(
            language_models={
                "smart": openai.language_model("gpt-4"),
                "fast": openai.language_model("gpt-3.5-turbo"),
                "claude": anthropic.language_model("claude-3-sonnet")
            },
            embedding_models={
                "default": openai.embedding_model("text-embedding-3-small")
            },
            fallback_provider=openai  # Use OpenAI for any unlisted models
        )
        
        # Use the custom provider
        smart_model = custom.language_model("smart")  # Gets GPT-4
        unknown_model = custom.language_model("gpt-4o")  # Falls back to OpenAI
        ```
    """
    return CustomProvider(
        language_models=language_models,
        embedding_models=embedding_models,
        image_models=image_models,
        speech_models=speech_models,
        transcription_models=transcription_models,
        fallback_provider=fallback_provider
    )