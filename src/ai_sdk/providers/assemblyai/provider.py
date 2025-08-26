"""AssemblyAI provider implementation."""

import os
from typing import Dict, Optional, Any

from ...errors.base import AISDKError
from ..base import BaseProvider
from .transcription_model import AssemblyAITranscriptionModel
from .types import (
    AssemblyAITranscriptionModelId,
    AssemblyAIProviderSettings,
)


class AssemblyAIProvider(BaseProvider):
    """AssemblyAI provider for transcription services."""
    
    def __init__(self, settings: AssemblyAIProviderSettings):
        """Initialize AssemblyAI provider.
        
        Args:
            settings: Provider configuration
        """
        super().__init__("assemblyai")
        self.settings = settings
        self._provider_name = "assemblyai"
        
        # Validate API key
        if not self.settings.api_key:
            raise AISDKError(
                "AssemblyAI API key is required. "
                "Set ASSEMBLYAI_API_KEY environment variable or pass api_key parameter."
            )
    
    @property
    def name(self) -> str:
        """Name of the provider."""
        return self._provider_name
    
    def transcription(self, model_id: AssemblyAITranscriptionModelId) -> AssemblyAITranscriptionModel:
        """Create a transcription model.
        
        Args:
            model_id: Model identifier ('best' or 'nano')
            
        Returns:
            Transcription model instance
        """
        return AssemblyAITranscriptionModel(model_id, self.settings)
    
    def language_model(self, model_id: str) -> None:
        """AssemblyAI does not provide language models.
        
        Raises:
            AISDKError: Always, as AssemblyAI doesn't provide language models
        """
        raise AISDKError("AssemblyAI does not provide language models")
    
    def embedding_model(self, model_id: str) -> None:
        """AssemblyAI does not provide embedding models.
        
        Raises:
            AISDKError: Always, as AssemblyAI doesn't provide embedding models
        """
        raise AISDKError("AssemblyAI does not provide embedding models")
    
    def image_model(self, model_id: str) -> None:
        """AssemblyAI does not provide image models.
        
        Raises:
            AISDKError: Always, as AssemblyAI doesn't provide image models
        """
        raise AISDKError("AssemblyAI does not provide image models")
    
    def speech_model(self, model_id: str) -> None:
        """AssemblyAI does not provide speech synthesis models.
        
        Raises:
            AISDKError: Always, as AssemblyAI doesn't provide speech synthesis
        """
        raise AISDKError("AssemblyAI does not provide speech synthesis models")


def create_assemblyai(
    api_key: Optional[str] = None,
    base_url: str = "https://api.assemblyai.com",
    headers: Optional[Dict[str, str]] = None,
) -> AssemblyAIProvider:
    """Create an AssemblyAI provider instance.
    
    Args:
        api_key: API key for authentication. If not provided, will use ASSEMBLYAI_API_KEY env var
        base_url: Base API URL
        headers: Additional headers to include in requests
        
    Returns:
        AssemblyAI provider instance
        
    Examples:
        Basic usage:
        ```python
        from ai_sdk.providers.assemblyai import create_assemblyai
        
        # Using environment variable
        provider = create_assemblyai()
        
        # Using explicit API key
        provider = create_assemblyai(api_key="your-api-key")
        
        # Create transcription model
        model = provider.transcription("best")
        
        # Transcribe audio
        with open("audio.mp3", "rb") as f:
            result = await model.transcribe(f.read())
        print(result.text)
        ```
        
        Advanced options:
        ```python
        from ai_sdk.providers.assemblyai import create_assemblyai, AssemblyAITranscriptionSettings
        
        provider = create_assemblyai()
        model = provider.transcription("best")
        
        # Transcribe with advanced options
        options = AssemblyAITranscriptionSettings(
            speaker_labels=True,
            auto_chapters=True,
            sentiment_analysis=True,
            language_detection=True,
            filter_profanity=True,
        )
        
        with open("audio.mp3", "rb") as f:
            result = await model.transcribe(f.read(), options=options)
        
        print(f"Text: {result.text}")
        print(f"Language: {result.language}")
        print(f"Duration: {result.duration_seconds}s")
        
        # Access word-level timestamps
        for segment in result.segments:
            print(f"{segment.start_second}s-{segment.end_second}s: {segment.text}")
        ```
    """
    # Get API key from environment if not provided
    if api_key is None:
        api_key = os.getenv("ASSEMBLYAI_API_KEY")
    
    settings = AssemblyAIProviderSettings(
        api_key=api_key,
        base_url=base_url,
        headers=headers,
    )
    
    return AssemblyAIProvider(settings)