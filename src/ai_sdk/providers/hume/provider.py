"""Hume AI provider implementation."""

import os
from typing import Dict, Optional, Any

from ...errors.base import AISDKError
from ..base import BaseProvider
from .speech_model import HumeSpeechModel
from .types import HumeProviderSettings


class HumeProvider(BaseProvider):
    """Hume AI provider for emotionally expressive speech synthesis."""
    
    def __init__(self, settings: HumeProviderSettings):
        """Initialize Hume provider.
        
        Args:
            settings: Provider configuration
        """
        super().__init__("hume")
        self.settings = settings
        
        # Validate API key
        if not self.settings.api_key:
            raise AISDKError(
                "Hume API key is required. "
                "Set HUME_API_KEY environment variable or pass api_key parameter."
            )
    
    def speech_model(self) -> HumeSpeechModel:
        """Create a speech synthesis model.
        
        Returns:
            Speech model instance
        """
        return HumeSpeechModel(self.settings)
    
    def language_model(self, model_id: str) -> None:
        """Hume does not provide language models.
        
        Raises:
            AISDKError: Always, as Hume doesn't provide language models
        """
        raise AISDKError("Hume does not provide language models")
    
    def embedding_model(self, model_id: str) -> None:
        """Hume does not provide embedding models.
        
        Raises:
            AISDKError: Always, as Hume doesn't provide embedding models
        """
        raise AISDKError("Hume does not provide embedding models")
    
    def image_model(self, model_id: str) -> None:
        """Hume does not provide image models.
        
        Raises:
            AISDKError: Always, as Hume doesn't provide image models
        """
        raise AISDKError("Hume does not provide image models")
    
    def transcription_model(self, model_id: str) -> None:
        """Hume does not provide transcription models.
        
        Raises:
            AISDKError: Always, as Hume doesn't provide transcription models
        """
        raise AISDKError("Hume does not provide transcription models")


def create_hume(
    api_key: Optional[str] = None,
    base_url: str = "https://api.hume.ai",
    headers: Optional[Dict[str, str]] = None,
) -> HumeProvider:
    """Create a Hume provider instance.
    
    Args:
        api_key: Hume API key. If not provided, will use HUME_API_KEY env var
        base_url: Base API URL
        headers: Additional headers to include in requests
        
    Returns:
        Hume provider instance
        
    Examples:
        Basic emotional speech:
        ```python
        from ai_sdk.providers.hume import create_hume
        
        # Using environment variable
        provider = create_hume()
        
        # Using explicit API key
        provider = create_hume(api_key="your-hume-key")
        
        # Create speech model
        model = provider.speech_model()
        
        # Generate emotional speech
        result = await model.generate("I'm so excited about this project!")
        
        # Save audio with emotional expression
        with open("excited_speech.mp3", "wb") as f:
            f.write(result.audio)
        ```
        
        Advanced emotional control:
        ```python
        from ai_sdk.providers.hume import (
            create_hume, 
            HumeSpeechSettings, 
            HumeUtterance, 
            HumeVoiceById,
            HumeContextUtterances,
        )
        
        provider = create_hume()
        model = provider.speech_model()
        
        # Create expressive utterances
        utterances = [
            HumeUtterance(
                text="Hello there!",
                description="Greeting with enthusiasm and warmth",
                speed=1.1,
                voice=HumeVoiceById(id="voice-happy-female"),
            ),
            HumeUtterance(
                text="How are you feeling today?",
                description="Caring and empathetic inquiry",
                speed=0.95,
                trailing_silence=0.5,
            ),
        ]
        
        # Configure context for multi-utterance synthesis
        context = HumeContextUtterances(utterances=utterances)
        options = HumeSpeechSettings(context=context)
        
        # Generate with emotional context
        result = await model.generate(
            text="This will be replaced by the context utterances",
            options=options
        )
        
        print(f"Generated emotional speech for {len(utterances)} utterances")
        
        # Save the emotionally expressive audio
        with open("emotional_conversation.mp3", "wb") as f:
            f.write(result.audio)
        ```
        
        Voice cloning and custom expressions:
        ```python
        from ai_sdk.providers.hume import create_hume, HumeSpeechSettings, HumeFormatSpec
        
        provider = create_hume()
        model = provider.speech_model()
        
        # Use high-quality WAV format
        options = HumeSpeechSettings(
            format=HumeFormatSpec(type="wav")
        )
        
        # Generate speech with specific emotional instruction
        result = await model.generate(
            text="The weather is absolutely beautiful today!",
            voice="d8ab67c6-953d-4bd8-9370-8fa53a0f1453",  # Hume voice ID
            instructions="Express genuine joy and wonder about nature",
            speed=1.0,
            options=options
        )
        
        print("Generated emotionally nuanced speech with custom voice")
        
        # High-quality output for further processing
        with open("beautiful_weather.wav", "wb") as f:
            f.write(result.audio)
        ```
    """
    # Get API key from environment if not provided
    if api_key is None:
        api_key = os.getenv("HUME_API_KEY")
    
    settings = HumeProviderSettings(
        api_key=api_key,
        base_url=base_url,
        headers=headers,
    )
    
    return HumeProvider(settings)