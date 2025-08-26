"""Speech generation functionality for AI SDK Python."""

from typing import Optional, Dict, Any, List

from pydantic import BaseModel, Field

from ..providers.base import (
    SpeechModel,
    SpeechModelResponseMetadata,
    GeneratedFile,
)
from ..errors.base import AISDKError
from ..utils.http import retry_with_exponential_backoff


class NoSpeechGeneratedError(AISDKError):
    """Error raised when no speech is generated."""

    def __init__(self, responses: List[SpeechModelResponseMetadata]):
        self.responses = responses
        super().__init__("No speech was generated")


class SpeechWarning(dict):
    """Warning from speech generation."""
    pass


class SpeechModelProviderMetadata(dict):
    """Provider-specific metadata for speech models."""
    pass


class GeneratedAudioFile(GeneratedFile):
    """Generated audio file."""
    
    def __init__(self, data: bytes, media_type: str):
        self._data = data
        self._media_type = media_type
    
    @property
    def data(self) -> bytes:
        return self._data
    
    @property 
    def media_type(self) -> str:
        return self._media_type


class GenerateSpeechResult(BaseModel):
    """Result of speech generation."""
    
    model_config = {'arbitrary_types_allowed': True}
    
    audio: GeneratedAudioFile = Field(..., description="Generated audio file")
    warnings: List[SpeechWarning] = Field(default_factory=list, description="Warnings from the provider")
    response: SpeechModelResponseMetadata = Field(..., description="Response metadata")
    provider_metadata: SpeechModelProviderMetadata = Field(default_factory=dict, description="Provider-specific metadata")


def detect_audio_media_type(data: bytes) -> str:
    """Detect media type from audio data."""
    if data.startswith(b'ID3') or data.startswith(b'\xff\xfb') or data.startswith(b'\xff\xf3') or data.startswith(b'\xff\xf2'):
        return 'audio/mpeg'
    elif data.startswith(b'RIFF') and b'WAVE' in data[:12]:
        return 'audio/wav'
    elif data.startswith(b'fLaC'):
        return 'audio/flac'
    elif data.startswith(b'OggS'):
        return 'audio/ogg'
    elif data.startswith(b'ftypM4A') or data[4:8] == b'ftyp':
        return 'audio/mp4'
    else:
        return 'audio/mpeg'  # default


async def generate_speech(
    *,
    model: SpeechModel,
    text: str,
    voice: Optional[str] = None,
    output_format: Optional[str] = None,
    instructions: Optional[str] = None,
    speed: Optional[float] = None,
    language: Optional[str] = None,
    provider_options: Optional[Dict[str, Any]] = None,
    max_retries: int = 2,
    headers: Optional[Dict[str, str]] = None,
) -> GenerateSpeechResult:
    """
    Generate speech audio using a speech model.
    
    Args:
        model: The speech model to use
        text: The text to convert to speech
        voice: The voice to use for speech generation
        output_format: The output format (e.g. "mp3", "wav", "flac")
        instructions: Instructions for speech generation
        speed: The speed of speech generation
        language: Language for speech generation
        provider_options: Provider-specific options
        max_retries: Maximum number of retries (default: 2)
        headers: Additional HTTP headers
        
    Returns:
        GenerateSpeechResult containing generated audio and metadata
        
    Raises:
        NoSpeechGeneratedError: When no speech is generated
    """
    
    # Create retry function
    async def make_call():
        return await model.do_generate(
            text=text,
            voice=voice,
            output_format=output_format,
            instructions=instructions,
            speed=speed,
            language=language,
            provider_options=provider_options or {},
            headers=headers or {},
        )
    
    # Make the call with retry
    result = await retry_with_exponential_backoff(
        make_call,
        max_retries=max_retries,
    )
    
    if not result.audio_data:
        raise NoSpeechGeneratedError([result.response])
    
    # Detect media type
    media_type = detect_audio_media_type(result.audio_data)
    audio_file = GeneratedAudioFile(data=result.audio_data, media_type=media_type)
    
    return GenerateSpeechResult(
        audio=audio_file,
        warnings=result.warnings or [],
        response=result.response,
        provider_metadata=result.provider_metadata or {}
    )


# Synchronous version
def generate_speech_sync(
    *,
    model: SpeechModel,
    text: str,
    voice: Optional[str] = None,
    output_format: Optional[str] = None,
    instructions: Optional[str] = None,
    speed: Optional[float] = None,
    language: Optional[str] = None,
    provider_options: Optional[Dict[str, Any]] = None,
    max_retries: int = 2,
    headers: Optional[Dict[str, str]] = None,
) -> GenerateSpeechResult:
    """Synchronous version of generate_speech."""
    import asyncio
    return asyncio.run(generate_speech(
        model=model,
        text=text,
        voice=voice,
        output_format=output_format,
        instructions=instructions,
        speed=speed,
        language=language,
        provider_options=provider_options,
        max_retries=max_retries,
        headers=headers,
    ))


# Result class for speech generation
class SpeechGenerationResult:
    """Result from speech generation."""
    
    def __init__(self, 
                 audio_data: bytes,
                 warnings: Optional[List[Any]] = None,
                 provider_metadata: Optional[Dict[str, Any]] = None):
        self.audio_data = audio_data
        self.warnings = warnings or []
        self.provider_metadata = provider_metadata


class GenerateSpeechUsage:
    """Usage statistics for speech generation."""
    
    def __init__(self, characters_generated: int = 0, total_cost: float = 0.0, **kwargs):
        self.characters_generated = characters_generated
        self.total_cost = total_cost
        for key, value in kwargs.items():
            setattr(self, key, value)