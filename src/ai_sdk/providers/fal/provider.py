"""FAL.ai provider implementation."""

import os
from typing import Dict, Optional, Any

from ...errors.base import AISDKError
from ..base import BaseProvider
from .image_model import FalImageModel
from .speech_model import FalSpeechModel
from .transcription_model import FalTranscriptionModel
from .types import (
    FalImageModelId,
    FalSpeechModelId,
    FalTranscriptionModelId,
    FalProviderSettings,
)


class FalProvider(BaseProvider):
    """FAL.ai provider for image generation, speech synthesis, and transcription."""
    
    def __init__(self, settings: FalProviderSettings):
        """Initialize FAL provider.
        
        Args:
            settings: Provider configuration
        """
        super().__init__("fal")
        self.settings = settings
        self._provider_name = "fal"
        
        # Validate API key
        if not self.settings.api_key:
            raise AISDKError(
                "FAL API key is required. "
                "Set FAL_API_KEY or FAL_KEY environment variable or pass api_key parameter."
            )
    
    @property
    def name(self) -> str:
        """Name of the provider."""
        return self._provider_name
    
    def image_model(self, model_id: FalImageModelId) -> FalImageModel:
        """Create an image generation model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Image model instance
        """
        return FalImageModel(model_id, self.settings)
    
    def speech_model(self, model_id: FalSpeechModelId) -> FalSpeechModel:
        """Create a speech synthesis model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Speech model instance
        """
        return FalSpeechModel(model_id, self.settings)
    
    def transcription_model(self, model_id: FalTranscriptionModelId) -> FalTranscriptionModel:
        """Create a transcription model.
        
        Args:
            model_id: Model identifier
            
        Returns:
            Transcription model instance
        """
        return FalTranscriptionModel(model_id, self.settings)
    
    def language_model(self, model_id: str) -> None:
        """FAL does not provide language models.
        
        Raises:
            AISDKError: Always, as FAL doesn't provide language models
        """
        raise AISDKError("FAL does not provide language models")
    
    def embedding_model(self, model_id: str) -> None:
        """FAL does not provide embedding models.
        
        Raises:
            AISDKError: Always, as FAL doesn't provide embedding models
        """
        raise AISDKError("FAL does not provide embedding models")


def create_fal(
    api_key: Optional[str] = None,
    base_url: str = "https://fal.run",
    headers: Optional[Dict[str, str]] = None,
) -> FalProvider:
    """Create a FAL provider instance.
    
    Args:
        api_key: FAL API key. If not provided, will use FAL_API_KEY or FAL_KEY env var
        base_url: Base API URL
        headers: Additional headers to include in requests
        
    Returns:
        FAL provider instance
        
    Examples:
        Basic image generation:
        ```python
        from ai_sdk.providers.fal import create_fal, FalImageSettings
        
        # Using environment variable
        provider = create_fal()
        
        # Using explicit API key
        provider = create_fal(api_key="your-fal-key")
        
        # Create image model
        model = provider.image_model("fal-ai/flux/schnell")
        
        # Generate image
        result = await model.generate("A beautiful sunset over mountains")
        
        # Save first image
        with open("sunset.png", "wb") as f:
            f.write(result.images[0])
        ```
        
        Advanced image generation:
        ```python
        from ai_sdk.providers.fal import create_fal, FalImageSettings, FalImageSizeCustom
        
        provider = create_fal()
        model = provider.image_model("fal-ai/flux-pro/v1.1")
        
        # Generate with custom settings
        options = FalImageSettings(
            image_size=FalImageSizeCustom(width=1024, height=768),
            num_images=4,
            seed=42,
        )
        
        result = await model.generate(
            prompt="A cyberpunk cityscape at night with neon lights",
            options=options
        )
        
        print(f"Generated {len(result.images)} images")
        for i, image_data in enumerate(result.images):
            with open(f"cyberpunk_{i}.png", "wb") as f:
                f.write(image_data)
        ```
        
        Speech synthesis:
        ```python
        from ai_sdk.providers.fal import create_fal, FalSpeechSettings, FalVoiceSettings
        
        provider = create_fal()
        model = provider.speech_model("fal-ai/coqui-xtts")
        
        # Basic speech generation
        result = await model.generate("Hello, this is a test of FAL speech synthesis!")
        
        # Save audio
        with open("speech.wav", "wb") as f:
            f.write(result.audio)
        
        # Advanced speech with voice settings
        voice_settings = FalVoiceSettings(
            speed=1.2,
            pitch=0.8,
            emotion="happy",
        )
        
        options = FalSpeechSettings(
            voice_setting=voice_settings,
            language_boost="en",
        )
        
        result = await model.generate(
            text="Welcome to the advanced speech synthesis demo!",
            voice="female_voice",
            options=options
        )
        ```
        
        Audio transcription:
        ```python
        from ai_sdk.providers.fal import create_fal, FalTranscriptionSettings
        
        provider = create_fal()
        model = provider.transcription_model("fal-ai/whisper")
        
        # Read audio file
        with open("audio.mp3", "rb") as f:
            audio_data = f.read()
        
        # Transcribe with options
        options = FalTranscriptionSettings(
            language="en",
            task="transcribe",
        )
        
        result = await model.transcribe(audio_data, options=options)
        
        print(f"Transcription: {result.text}")
        print(f"Language: {result.language}")
        
        # Access segments if available
        for segment in result.segments:
            print(f"{segment.start_second}s-{segment.end_second}s: {segment.text}")
        ```
    """
    # Get API key from environment if not provided
    if api_key is None:
        api_key = os.getenv("FAL_API_KEY") or os.getenv("FAL_KEY")
    
    settings = FalProviderSettings(
        api_key=api_key,
        base_url=base_url,
        headers=headers,
    )
    
    return FalProvider(settings)