"""RevAI provider implementation."""

import os
from typing import Optional

from ..base import Provider
from ...errors.base import AISDKError
from .transcription_model import RevAITranscriptionModel
from .types import (
    RevAIProviderSettings,
    RevAITranscriptionModelId,
)


class RevAIProvider(Provider):
    """RevAI provider for transcription services."""
    
    def __init__(self, settings: Optional[RevAIProviderSettings] = None):
        """Initialize RevAI provider.
        
        Args:
            settings: Provider configuration settings
        """
        if settings is None:
            settings = RevAIProviderSettings()
        
        # Load API key from environment if not provided
        if not settings.api_key:
            settings.api_key = os.getenv("REVAI_API_KEY")
            if not settings.api_key:
                raise AISDKError(
                    "RevAI API key is required. "
                    "Set REVAI_API_KEY environment variable or provide api_key in settings."
                )
        
        self.settings = settings
    
    async def transcription_model(
        self, model_id: RevAITranscriptionModelId
    ) -> RevAITranscriptionModel:
        """Create a RevAI transcription model.
        
        Args:
            model_id: Model identifier ('machine', 'low_cost', or 'fusion')
            
        Returns:
            RevAI transcription model instance
        """
        return RevAITranscriptionModel(model_id, self.settings)
    
    async def language_model(self, model_id: str):
        """RevAI does not provide language models.
        
        Args:
            model_id: Model identifier
            
        Raises:
            AISDKError: Always, as RevAI doesn't provide language models
        """
        raise AISDKError(
            "RevAI does not provide language models. "
            "Use transcription_model() for speech-to-text services."
        )
    
    async def embedding_model(self, model_id: str):
        """RevAI does not provide embedding models.
        
        Args:
            model_id: Model identifier
            
        Raises:
            AISDKError: Always, as RevAI doesn't provide embedding models
        """
        raise AISDKError(
            "RevAI does not provide embedding models. "
            "Use transcription_model() for speech-to-text services."
        )
    
    async def image_model(self, model_id: str):
        """RevAI does not provide image models.
        
        Args:
            model_id: Model identifier
            
        Raises:
            AISDKError: Always, as RevAI doesn't provide image models
        """
        raise AISDKError(
            "RevAI does not provide image models. "
            "Use transcription_model() for speech-to-text services."
        )


def create_revai(
    api_key: Optional[str] = None,
    base_url: str = "https://api.rev.ai",
    **kwargs
) -> RevAIProvider:
    """Create a RevAI provider instance.
    
    Args:
        api_key: RevAI API key (optional, will use REVAI_API_KEY env var if not provided)
        base_url: Base URL for RevAI API
        **kwargs: Additional settings
        
    Returns:
        RevAI provider instance
        
    Example:
        ```python
        from ai_sdk import create_revai, transcribe
        
        # Create provider
        revai = create_revai(api_key="your-api-key")
        
        # Create transcription model
        model = await revai.transcription_model("machine")
        
        # Transcribe audio
        with open("audio.wav", "rb") as f:
            audio_data = f.read()
            
        result = await transcribe(
            model=model,
            audio=audio_data,
            media_type="audio/wav"
        )
        
        print(result.text)
        ```
    """
    settings = RevAIProviderSettings(
        api_key=api_key,
        base_url=base_url,
        **kwargs
    )
    return RevAIProvider(settings)