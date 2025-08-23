"""Transcription functionality for AI SDK Python."""

from typing import Optional, Dict, Any, List, Union
from pathlib import Path

from pydantic import BaseModel, Field

from ..providers.base import (
    TranscriptionModel,
    TranscriptionModelResponseMetadata,
)
from ..errors.base import AISDKError
from ..utils.http import retry_with_exponential_backoff


class NoTranscriptGeneratedError(AISDKError):
    """Error raised when no transcript is generated."""

    def __init__(self, responses: List[TranscriptionModelResponseMetadata]):
        self.responses = responses
        super().__init__("No transcript was generated")


class TranscriptionWarning(dict):
    """Warning from transcription."""
    pass


class TranscriptionModelProviderMetadata(dict):
    """Provider-specific metadata for transcription models."""
    pass


class TranscriptionResult(BaseModel):
    """Result of transcription."""
    
    text: str = Field(..., description="Transcribed text")
    warnings: List[TranscriptionWarning] = Field(default_factory=list, description="Warnings from the provider") 
    response: TranscriptionModelResponseMetadata = Field(..., description="Response metadata")
    provider_metadata: TranscriptionModelProviderMetadata = Field(default_factory=dict, description="Provider-specific metadata")


AudioData = Union[bytes, str, Path]


def load_audio_data(audio: AudioData) -> bytes:
    """Load audio data from various sources."""
    if isinstance(audio, bytes):
        return audio
    elif isinstance(audio, str):
        # Check if it's a file path
        if Path(audio).exists():
            return Path(audio).read_bytes()
        else:
            raise ValueError(f"File not found: {audio}")
    elif isinstance(audio, Path):
        return audio.read_bytes()
    else:
        raise ValueError(f"Unsupported audio data type: {type(audio)}")


async def transcribe(
    *,
    model: TranscriptionModel,
    audio: AudioData,
    language: Optional[str] = None,
    prompt: Optional[str] = None,
    temperature: Optional[float] = None,
    timestamp_granularities: Optional[List[str]] = None,
    provider_options: Optional[Dict[str, Any]] = None,
    max_retries: int = 2,
    headers: Optional[Dict[str, str]] = None,
) -> TranscriptionResult:
    """
    Generate transcript using a transcription model.
    
    Args:
        model: The transcription model to use
        audio: Audio data as bytes, file path, or Path object
        language: Language of the audio (optional)
        prompt: Prompt to guide the transcription (optional)
        temperature: Sampling temperature (optional)
        timestamp_granularities: Timestamp granularities (optional)
        provider_options: Provider-specific options
        max_retries: Maximum number of retries (default: 2)
        headers: Additional HTTP headers
        
    Returns:
        TranscriptionResult containing transcribed text and metadata
        
    Raises:
        NoTranscriptGeneratedError: When no transcript is generated
    """
    
    # Load audio data
    audio_bytes = load_audio_data(audio)
    
    # Create retry function
    async def make_call():
        return await model.do_transcribe(
            audio_data=audio_bytes,
            language=language,
            prompt=prompt,
            temperature=temperature,
            timestamp_granularities=timestamp_granularities,
            provider_options=provider_options or {},
            headers=headers or {},
        )
    
    # Make the call with retry
    result = await retry_with_exponential_backoff(
        make_call,
        max_retries=max_retries,
    )
    
    if not result.text:
        raise NoTranscriptGeneratedError([result.response])
    
    return TranscriptionResult(
        text=result.text,
        warnings=result.warnings or [],
        response=result.response,
        provider_metadata=result.provider_metadata or {}
    )


# Synchronous version
def transcribe_sync(
    *,
    model: TranscriptionModel,
    audio: AudioData,
    language: Optional[str] = None,
    prompt: Optional[str] = None,
    temperature: Optional[float] = None,
    timestamp_granularities: Optional[List[str]] = None,
    provider_options: Optional[Dict[str, Any]] = None,
    max_retries: int = 2,
    headers: Optional[Dict[str, str]] = None,
) -> TranscriptionResult:
    """Synchronous version of transcribe."""
    import asyncio
    return asyncio.run(transcribe(
        model=model,
        audio=audio,
        language=language,
        prompt=prompt,
        temperature=temperature,
        timestamp_granularities=timestamp_granularities,
        provider_options=provider_options,
        max_retries=max_retries,
        headers=headers,
    ))