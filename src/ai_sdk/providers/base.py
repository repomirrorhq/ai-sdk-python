"""Base classes for AI providers."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

from .types import (
    GenerateOptions,
    GenerateResult,
    StreamOptions,
    StreamPart,
)


class Provider(ABC):
    """Base class for AI providers."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs: Any) -> None:
        """Initialize the provider.
        
        Args:
            api_key: API key for the provider
            **kwargs: Additional provider-specific configuration
        """
        self.api_key = api_key
        self.config = kwargs
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the provider."""
        pass
    
    @abstractmethod
    def language_model(self, model_id: str, **kwargs: Any) -> LanguageModel:
        """Get a language model instance.
        
        Args:
            model_id: Model identifier
            **kwargs: Model-specific configuration
            
        Returns:
            Language model instance
        """
        pass


class LanguageModel(ABC):
    """Base class for language models."""
    
    def __init__(
        self,
        provider: Provider,
        model_id: str,
        **kwargs: Any,
    ) -> None:
        """Initialize the language model.
        
        Args:
            provider: Provider instance
            model_id: Model identifier
            **kwargs: Model-specific configuration
        """
        self.provider = provider
        self.model_id = model_id
        self.config = kwargs
    
    @property
    def specification_version(self) -> str:
        """Language model interface version."""
        return "v1"
    
    @property
    def provider_name(self) -> str:
        """Name of the provider."""
        return self.provider.name
    
    @property
    def supported_urls(self) -> Dict[str, List[str]]:
        """Supported URL patterns by media type.
        
        Returns mapping of media type patterns to URL regex patterns.
        """
        return {}
    
    @abstractmethod
    async def generate(self, options: GenerateOptions) -> GenerateResult:
        """Generate text (non-streaming).
        
        Args:
            options: Generation options
            
        Returns:
            Generation result
        """
        pass
    
    @abstractmethod
    async def stream(self, options: StreamOptions) -> AsyncGenerator[StreamPart, None]:
        """Generate text (streaming).
        
        Args:
            options: Streaming options
            
        Yields:
            Stream parts
        """
        pass


class EmbeddingModel(ABC):
    """Base class for embedding models."""
    
    def __init__(
        self,
        provider: Provider,
        model_id: str,
        **kwargs: Any,
    ) -> None:
        """Initialize the embedding model.
        
        Args:
            provider: Provider instance
            model_id: Model identifier
            **kwargs: Model-specific configuration
        """
        self.provider = provider
        self.model_id = model_id
        self.config = kwargs
    
    @abstractmethod
    async def embed(self, input_text: str) -> List[float]:
        """Generate embeddings for a single text.
        
        Args:
            input_text: Text to embed
            
        Returns:
            Embedding vector
        """
        pass
    
    @abstractmethod
    async def embed_many(self, inputs: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts.
        
        Args:
            inputs: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        pass


class ImageModel(ABC):
    """Base class for image generation models."""
    
    def __init__(
        self,
        provider: Provider,
        model_id: str,
        **kwargs: Any,
    ) -> None:
        """Initialize the image model.
        
        Args:
            provider: Provider instance
            model_id: Model identifier
            **kwargs: Model-specific configuration
        """
        self.provider = provider
        self.model_id = model_id
        self.config = kwargs
    
    @abstractmethod
    async def generate_image(
        self,
        prompt: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        **kwargs: Any,
    ) -> bytes:
        """Generate an image.
        
        Args:
            prompt: Text prompt for image generation
            width: Image width
            height: Image height
            **kwargs: Additional generation parameters
            
        Returns:
            Generated image data
        """
        pass


class SpeechModel(ABC):
    """Base class for text-to-speech models."""
    
    def __init__(
        self,
        provider: Provider,
        model_id: str,
        **kwargs: Any,
    ) -> None:
        """Initialize the speech model.
        
        Args:
            provider: Provider instance
            model_id: Model identifier
            **kwargs: Model-specific configuration
        """
        self.provider = provider
        self.model_id = model_id
        self.config = kwargs
    
    @abstractmethod
    async def synthesize(
        self,
        text: str,
        voice: Optional[str] = None,
        **kwargs: Any,
    ) -> bytes:
        """Synthesize speech from text.
        
        Args:
            text: Text to synthesize
            voice: Voice identifier
            **kwargs: Additional synthesis parameters
            
        Returns:
            Audio data
        """
        pass


class TranscriptionModel(ABC):
    """Base class for speech-to-text models."""
    
    def __init__(
        self,
        provider: Provider,
        model_id: str,
        **kwargs: Any,
    ) -> None:
        """Initialize the transcription model.
        
        Args:
            provider: Provider instance
            model_id: Model identifier
            **kwargs: Model-specific configuration
        """
        self.provider = provider
        self.model_id = model_id
        self.config = kwargs
    
    @abstractmethod
    async def transcribe(
        self,
        audio_data: bytes,
        language: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Transcribe audio to text.
        
        Args:
            audio_data: Audio data to transcribe
            language: Language code
            **kwargs: Additional transcription parameters
            
        Returns:
            Transcribed text
        """
        pass