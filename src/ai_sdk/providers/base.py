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
        
        # Model capabilities (can be overridden by subclasses)
        self.max_embeddings_per_call: int = 1000
        self.supports_parallel_calls: bool = True
    
    @property
    def specification_version(self) -> str:
        """Embedding model interface version."""
        return "v2"
    
    @property 
    def provider_name(self) -> str:
        """Name of the provider."""
        return self.provider.name
    
    @abstractmethod
    async def do_embed(
        self,
        *,
        values: List[Any],
        headers: Optional[Dict[str, str]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Generate embeddings for multiple values (modern interface).
        
        Args:
            values: List of values to embed
            headers: Additional HTTP headers
            extra_body: Additional request body parameters
            
        Returns:
            Dictionary containing:
            - embeddings: List[List[float]] - Generated embeddings
            - usage: Dict with 'tokens' count
            - provider_metadata: Optional provider-specific metadata
            - response: Optional raw response data
        """
        pass
    
    # Legacy interface for backwards compatibility
    async def embed(self, input_text: str) -> List[float]:
        """Generate embeddings for a single text (legacy interface).
        
        Args:
            input_text: Text to embed
            
        Returns:
            Embedding vector
        """
        result = await self.do_embed(values=[input_text])
        return result['embeddings'][0]
    
    async def embed_many(self, inputs: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (legacy interface).
        
        Args:
            inputs: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        result = await self.do_embed(values=inputs)
        return result['embeddings']


class GeneratedFile(ABC):
    """Base class for generated files."""
    
    @property
    @abstractmethod
    def data(self) -> bytes:
        """File data."""
        pass
    
    @property
    @abstractmethod
    def media_type(self) -> str:
        """File media type."""
        pass


class ImageGenerationWarning(dict):
    """Warning from image generation."""
    pass


class ImageModelResponseMetadata(dict):
    """Response metadata from image model."""
    pass


class ImageModelProviderMetadata(dict):
    """Provider-specific metadata for image models."""
    pass


class ImageGenerationResult(dict):
    """Result from image generation."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.images: List[bytes] = kwargs.get('images', [])
        self.warnings: List[ImageGenerationWarning] = kwargs.get('warnings', [])
        self.response: ImageModelResponseMetadata = kwargs.get('response', {})
        self.provider_metadata: ImageModelProviderMetadata = kwargs.get('provider_metadata', {})


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
        self.max_images_per_call = kwargs.get('max_images_per_call', 1)
    
    @property
    def specification_version(self) -> str:
        """Image model interface version."""
        return "v2"
    
    @property
    def provider_name(self) -> str:
        """Name of the provider."""
        return self.provider.name
    
    @abstractmethod
    async def do_generate(
        self,
        *,
        prompt: str,
        n: int = 1,
        size: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        seed: Optional[int] = None,
        provider_options: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> ImageGenerationResult:
        """Generate images.
        
        Args:
            prompt: Text prompt for image generation
            n: Number of images to generate
            size: Size as "widthxheight" (e.g. "1024x1024")
            aspect_ratio: Aspect ratio as "width:height" (e.g. "16:9")
            seed: Seed for reproducible generation
            provider_options: Provider-specific options
            headers: Additional HTTP headers
            
        Returns:
            Image generation result
        """
        pass


class SpeechGenerationWarning(dict):
    """Warning from speech generation."""
    pass


class SpeechModelResponseMetadata(dict):
    """Response metadata from speech model."""
    pass


class SpeechModelProviderMetadata(dict):
    """Provider-specific metadata for speech models."""
    pass


class SpeechGenerationResult(dict):
    """Result from speech generation."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.audio_data: bytes = kwargs.get('audio_data', b'')
        self.warnings: List[SpeechGenerationWarning] = kwargs.get('warnings', [])
        self.response: SpeechModelResponseMetadata = kwargs.get('response', {})
        self.provider_metadata: SpeechModelProviderMetadata = kwargs.get('provider_metadata', {})


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
    
    @property
    def specification_version(self) -> str:
        """Speech model interface version."""
        return "v2"
    
    @property
    def provider_name(self) -> str:
        """Name of the provider."""
        return self.provider.name
    
    @abstractmethod
    async def do_generate(
        self,
        *,
        text: str,
        voice: Optional[str] = None,
        output_format: Optional[str] = None,
        instructions: Optional[str] = None,
        speed: Optional[float] = None,
        language: Optional[str] = None,
        provider_options: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> SpeechGenerationResult:
        """Generate speech from text.
        
        Args:
            text: Text to synthesize
            voice: Voice identifier
            output_format: Output format (e.g. "mp3", "wav")
            instructions: Instructions for speech generation
            speed: Speech speed
            language: Language for speech generation
            provider_options: Provider-specific options
            headers: Additional HTTP headers
            
        Returns:
            Speech generation result
        """
        pass


class TranscriptionWarning(dict):
    """Warning from transcription."""
    pass


class TranscriptionModelResponseMetadata(dict):
    """Response metadata from transcription model."""
    pass


class TranscriptionModelProviderMetadata(dict):
    """Provider-specific metadata for transcription models."""
    pass


class TranscriptionResult(dict):
    """Result from transcription."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.text: str = kwargs.get('text', '')
        self.warnings: List[TranscriptionWarning] = kwargs.get('warnings', [])
        self.response: TranscriptionModelResponseMetadata = kwargs.get('response', {})
        self.provider_metadata: TranscriptionModelProviderMetadata = kwargs.get('provider_metadata', {})


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
    
    @property
    def specification_version(self) -> str:
        """Transcription model interface version."""
        return "v2"
    
    @property
    def provider_name(self) -> str:
        """Name of the provider."""
        return self.provider.name
    
    @abstractmethod
    async def do_transcribe(
        self,
        *,
        audio_data: bytes,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        timestamp_granularities: Optional[List[str]] = None,
        provider_options: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> TranscriptionResult:
        """Transcribe audio to text.
        
        Args:
            audio_data: Audio data to transcribe
            language: Language code
            prompt: Prompt to guide transcription
            temperature: Sampling temperature
            timestamp_granularities: Timestamp granularities
            provider_options: Provider-specific options
            headers: Additional HTTP headers
            
        Returns:
            Transcription result
        """
        pass