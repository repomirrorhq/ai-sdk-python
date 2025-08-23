"""Deepgram AI provider implementation."""

import os
from typing import Dict, Optional, Any

from ...errors import NoSuchModelError
from ..base import Provider
from .transcription_model import DeepgramTranscriptionModel
from .types import DeepgramTranscriptionModelId


class DeepgramProvider(Provider):
    """
    Deepgram AI provider for real-time and pre-recorded speech recognition.
    
    Provides access to Deepgram's advanced speech-to-text models with features
    like speaker diarization, sentiment analysis, topic detection, and more.
    
    Example:
        ```python
        from ai_sdk import Deepgram
        
        # Create provider with API key
        deepgram = Deepgram(api_key="your-api-key")
        
        # Transcribe audio with advanced features
        transcription_model = deepgram.transcription("nova-3")
        result = await transcription_model.transcribe(
            audio_data,
            provider_options={
                "diarize": True,
                "smart_format": True,
                "sentiment": True,
                "topics": True
            }
        )
        ```
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.deepgram.com",
        headers: Optional[Dict[str, str]] = None,
        http_client: Optional[Any] = None,
    ):
        """
        Initialize Deepgram provider.
        
        Args:
            api_key: Deepgram API key. If not provided, will look for DEEPGRAM_API_KEY env var.
            base_url: Base URL for Deepgram API (default: https://api.deepgram.com)
            headers: Additional headers to include in requests
            http_client: Custom HTTP client instance
        """
        super().__init__(http_client=http_client)
        
        # Get API key from parameter or environment variable
        self.api_key = api_key or os.getenv("DEEPGRAM_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Deepgram API key is required. "
                "Pass it as api_key parameter or set DEEPGRAM_API_KEY environment variable."
            )
        
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        
        # Provider name for logging and debugging
        self.name = "deepgram"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        return {
            "Authorization": f"Token {self.api_key}",
            "Content-Type": "application/json",
            **self.headers,
        }
    
    def _get_base_url(self, path: str = "") -> str:
        """Get full URL for API endpoint."""
        return f"{self.base_url}{path}"
    
    def transcription(
        self,
        model_id: DeepgramTranscriptionModelId = "nova-3",
        **kwargs: Any,
    ) -> DeepgramTranscriptionModel:
        """
        Create a transcription model.
        
        Args:
            model_id: The Deepgram model ID to use (default: nova-3)
            **kwargs: Additional model configuration
            
        Returns:
            DeepgramTranscriptionModel instance
            
        Example:
            ```python
            # Basic transcription
            transcription_model = provider.transcription("nova-3")
            result = await transcription_model.transcribe(audio_data)
            
            # Advanced transcription with features
            transcription_model = provider.transcription("nova-2-medical")
            result = await transcription_model.transcribe(
                audio_data,
                provider_options={
                    "diarize": True,          # Speaker identification
                    "smart_format": True,     # Smart formatting
                    "sentiment": True,        # Sentiment analysis
                    "topics": True,           # Topic detection
                    "summarize": "v2",        # Generate summary
                    "detect_entities": True,  # Named entity recognition
                }
            )
            ```
        """
        return DeepgramTranscriptionModel(
            model_id=model_id,
            provider=self,
            **kwargs,
        )
    
    # Implement abstract methods from base Provider
    def language_model(self, model_id: str, **kwargs: Any):
        """Deepgram does not provide language models."""
        raise NoSuchModelError(
            f"Deepgram does not provide language models. Model ID: {model_id}",
            model_id=model_id,
            provider="deepgram"
        )
    
    def embedding_model(self, model_id: str, **kwargs: Any):
        """Deepgram does not provide embedding models."""
        raise NoSuchModelError(
            f"Deepgram does not provide embedding models. Model ID: {model_id}",
            model_id=model_id,
            provider="deepgram"
        )
    
    def image_model(self, model_id: str, **kwargs: Any):
        """Deepgram does not provide image models."""
        raise NoSuchModelError(
            f"Deepgram does not provide image models. Model ID: {model_id}",
            model_id=model_id,
            provider="deepgram"
        )


def create_deepgram(
    api_key: Optional[str] = None,
    base_url: str = "https://api.deepgram.com",
    headers: Optional[Dict[str, str]] = None,
    http_client: Optional[Any] = None,
) -> DeepgramProvider:
    """
    Create a Deepgram provider instance.
    
    Args:
        api_key: Deepgram API key. If not provided, will look for DEEPGRAM_API_KEY env var.
        base_url: Base URL for Deepgram API
        headers: Additional headers to include in requests
        http_client: Custom HTTP client instance
        
    Returns:
        DeepgramProvider instance
        
    Example:
        ```python
        deepgram = create_deepgram(api_key="your-api-key")
        transcription_model = deepgram.transcription("nova-3")
        ```
    """
    return DeepgramProvider(
        api_key=api_key,
        base_url=base_url,
        headers=headers,
        http_client=http_client,
    )


# Default provider instance
Deepgram = create_deepgram