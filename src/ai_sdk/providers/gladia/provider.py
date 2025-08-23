"""
Gladia Provider implementation.
"""

from typing import Any, Dict
from ai_sdk.core.types import Provider, TranscriptionModel
from ai_sdk.errors.base import AISDKError
from .types import GladiaProviderSettings
from .transcription_model import GladiaTranscriptionModel


class GladiaProvider(Provider):
    """
    Gladia AI provider for advanced audio transcription.
    
    Supports:
    - High-accuracy audio transcription
    - Speaker diarization (speaker identification)
    - Multi-language detection and code-switching
    - Real-time translation
    - Automatic summarization
    - Named entity recognition
    - Custom vocabulary and spelling
    - Subtitle generation
    - Content moderation
    """
    
    def __init__(self, settings: GladiaProviderSettings | None = None):
        """
        Initialize Gladia provider.
        
        Args:
            settings: Configuration settings for the provider.
                     If None, will use default settings with environment variables.
        """
        self.settings = settings or GladiaProviderSettings()
        self._provider_name = "gladia"
    
    @property
    def provider(self) -> str:
        return self._provider_name
    
    def transcription_model(self) -> TranscriptionModel:
        """
        Create a Gladia transcription model for audio transcription.
        
        Returns:
            GladiaTranscriptionModel instance
            
        Example:
            >>> provider = GladiaProvider()
            >>> model = provider.transcription_model()
            >>> result = await model.transcribe(audio_data)
        """
        return GladiaTranscriptionModel(self.settings)
    
    def language_model(self, model_id: str):
        """Gladia does not provide language models."""
        raise AISDKError("Gladia does not provide language models")
    
    def embedding_model(self, model_id: str):
        """Gladia does not provide embedding models."""
        raise AISDKError("Gladia does not provide embedding models")
    
    def image_model(self, model_id: str):
        """Gladia does not provide image models."""
        raise AISDKError("Gladia does not provide image models")
    
    def speech_model(self, model_id: str):
        """Gladia does not provide speech generation models."""
        raise AISDKError("Gladia does not provide speech generation models")
    
    def __call__(self):
        """
        Convenient method to get transcription model.
        
        Returns:
            GladiaTranscriptionModel instance
        """
        return self.transcription_model()
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get information about available Gladia models."""
        return {
            "transcription_models": {
                "default": {
                    "description": "Gladia's advanced transcription model",
                    "features": [
                        "Multi-language support (90+ languages)",
                        "Speaker diarization",
                        "Real-time translation",
                        "Automatic summarization",
                        "Named entity recognition",
                        "Custom vocabulary",
                        "Content moderation",
                        "Subtitle generation",
                        "Code-switching detection",
                        "Sentiment analysis"
                    ],
                    "supported_formats": [
                        "wav", "mp3", "flac", "aac", "ogg", "m4a",
                        "mp4", "mov", "avi", "mkv", "webm"
                    ],
                    "max_file_size": "1GB",
                    "max_duration": "24 hours"
                }
            }
        }
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about this provider."""
        return {
            "name": "gladia",
            "description": "Gladia AI provider for advanced audio transcription with AI-powered features",
            "capabilities": [
                "audio_transcription",
                "speaker_diarization", 
                "multi_language_detection",
                "real_time_translation",
                "automatic_summarization",
                "named_entity_recognition",
                "custom_vocabulary",
                "content_moderation",
                "subtitle_generation",
                "sentiment_analysis",
                "code_switching",
                "structured_data_extraction"
            ],
            "supported_modalities": {
                "input": ["audio", "video"],
                "output": ["text", "subtitles", "structured_data"]
            },
            "base_url": self.settings.base_url,
            "api_version": "v2"
        }


def create_gladia_provider(
    api_key: str | None = None,
    base_url: str | None = None,
    headers: Dict[str, str] | None = None,
    timeout: float = 300.0,
    max_retries: int = 3,
) -> GladiaProvider:
    """
    Create a Gladia provider with custom settings.
    
    Args:
        api_key: Gladia API key. If None, uses GLADIA_API_KEY environment variable.
        base_url: Custom base URL for API calls. Defaults to https://api.gladia.io
        headers: Additional headers to include in requests.
        timeout: Request timeout in seconds (default 5 minutes).
        max_retries: Maximum number of retry attempts.
        
    Returns:
        GladiaProvider instance
        
    Example:
        >>> provider = create_gladia_provider(api_key="your-api-key")
        >>> model = provider.transcription_model()
    """
    settings = GladiaProviderSettings()
    
    if api_key is not None:
        settings.api_key = api_key
    if base_url is not None:
        settings.base_url = base_url
    if headers is not None:
        settings.headers = headers
    if timeout != 300.0:
        settings.timeout = timeout
    if max_retries != 3:
        settings.max_retries = max_retries
    
    return GladiaProvider(settings)


# Default provider instance
gladia_provider = GladiaProvider()