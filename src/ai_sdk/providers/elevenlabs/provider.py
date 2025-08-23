"""ElevenLabs AI provider implementation."""

import os
from typing import Dict, Optional, Callable, Any

from ...errors import NoSuchModelError
from ..base import Provider
from .speech_model import ElevenLabsSpeechModel
from .transcription_model import ElevenLabsTranscriptionModel
from .types import ElevenLabsSpeechModelId, ElevenLabsTranscriptionModelId


class ElevenLabsProvider(Provider):
    """
    ElevenLabs AI provider for speech synthesis and transcription.
    
    Provides access to ElevenLabs' speech models for text-to-speech generation
    and transcription models for speech-to-text conversion.
    
    Example:
        ```python
        from ai_sdk import ElevenLabs
        
        # Create provider with API key
        elevenlabs = ElevenLabs(api_key="your-api-key")
        
        # Generate speech
        speech_model = elevenlabs.speech("eleven_v3")
        result = await speech_model.generate(text="Hello, world!")
        
        # Transcribe audio
        transcription_model = elevenlabs.transcription("scribe_v1")  
        result = await transcription_model.transcribe(audio_data)
        ```
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.elevenlabs.io",
        headers: Optional[Dict[str, str]] = None,
        http_client: Optional[Any] = None,
    ):
        """
        Initialize ElevenLabs provider.
        
        Args:
            api_key: ElevenLabs API key. If not provided, will look for ELEVENLABS_API_KEY env var.
            base_url: Base URL for ElevenLabs API (default: https://api.elevenlabs.io)
            headers: Additional headers to include in requests
            http_client: Custom HTTP client instance
        """
        super().__init__(http_client=http_client)
        
        # Get API key from parameter or environment variable
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError(
                "ElevenLabs API key is required. "
                "Pass it as api_key parameter or set ELEVENLABS_API_KEY environment variable."
            )
        
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        
        # Provider name for logging and debugging
        self.name = "elevenlabs"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json",
            **self.headers,
        }
    
    def _get_base_url(self, path: str = "") -> str:
        """Get full URL for API endpoint."""
        return f"{self.base_url}{path}"
    
    def speech(
        self,
        model_id: ElevenLabsSpeechModelId,
        **kwargs: Any,
    ) -> ElevenLabsSpeechModel:
        """
        Create a speech synthesis model.
        
        Args:
            model_id: The ElevenLabs speech model ID to use
            **kwargs: Additional model configuration
            
        Returns:
            ElevenLabsSpeechModel instance
            
        Example:
            ```python
            speech_model = provider.speech("eleven_v3")
            result = await speech_model.generate(
                text="Hello, world!",
                voice="21m00Tcm4TlvDq8ikWAM"
            )
            ```
        """
        return ElevenLabsSpeechModel(
            model_id=model_id,
            provider=self,
            **kwargs,
        )
    
    def transcription(
        self,
        model_id: ElevenLabsTranscriptionModelId = "scribe_v1",
        **kwargs: Any,
    ) -> ElevenLabsTranscriptionModel:
        """
        Create a transcription model.
        
        Args:
            model_id: The ElevenLabs transcription model ID to use
            **kwargs: Additional model configuration
            
        Returns:
            ElevenLabsTranscriptionModel instance
            
        Example:
            ```python
            transcription_model = provider.transcription("scribe_v1")
            result = await transcription_model.transcribe(audio_data)
            ```
        """
        return ElevenLabsTranscriptionModel(
            model_id=model_id,
            provider=self,
            **kwargs,
        )
    
    # Implement abstract methods from base Provider
    def language_model(self, model_id: str, **kwargs: Any):
        """ElevenLabs does not provide language models."""
        raise NoSuchModelError(
            f"ElevenLabs does not provide language models. Model ID: {model_id}",
            model_id=model_id,
            provider="elevenlabs"
        )
    
    def embedding_model(self, model_id: str, **kwargs: Any):
        """ElevenLabs does not provide embedding models."""
        raise NoSuchModelError(
            f"ElevenLabs does not provide embedding models. Model ID: {model_id}",
            model_id=model_id,
            provider="elevenlabs"
        )
    
    def image_model(self, model_id: str, **kwargs: Any):
        """ElevenLabs does not provide image models."""
        raise NoSuchModelError(
            f"ElevenLabs does not provide image models. Model ID: {model_id}",
            model_id=model_id,
            provider="elevenlabs"
        )


def create_elevenlabs(
    api_key: Optional[str] = None,
    base_url: str = "https://api.elevenlabs.io",
    headers: Optional[Dict[str, str]] = None,
    http_client: Optional[Any] = None,
) -> ElevenLabsProvider:
    """
    Create an ElevenLabs provider instance.
    
    Args:
        api_key: ElevenLabs API key. If not provided, will look for ELEVENLABS_API_KEY env var.
        base_url: Base URL for ElevenLabs API
        headers: Additional headers to include in requests
        http_client: Custom HTTP client instance
        
    Returns:
        ElevenLabsProvider instance
        
    Example:
        ```python
        elevenlabs = create_elevenlabs(api_key="your-api-key")
        speech_model = elevenlabs.speech("eleven_v3")
        ```
    """
    return ElevenLabsProvider(
        api_key=api_key,
        base_url=base_url,
        headers=headers,
        http_client=http_client,
    )


# Default provider instance
ElevenLabs = create_elevenlabs