"""Type definitions for ElevenLabs AI provider."""

from typing import List, Literal, Optional, Union
from pydantic import BaseModel, Field


# ElevenLabs Speech Model IDs
ElevenLabsSpeechModelId = Literal[
    "eleven_v3",
    "eleven_multilingual_v2", 
    "eleven_flash_v2_5",
    "eleven_flash_v2",
    "eleven_turbo_v2_5",
    "eleven_turbo_v2",
    "eleven_monolingual_v1",
    "eleven_multilingual_v1",
]

# ElevenLabs Transcription Model IDs  
ElevenLabsTranscriptionModelId = Literal["scribe_v1"]

# Voice ID can be any string
ElevenLabsSpeechVoiceId = str


class ElevenLabsSpeechAPIRequest(BaseModel):
    """Request body for ElevenLabs speech synthesis API."""
    
    text: str = Field(description="The text to synthesize into speech")
    model_id: Optional[str] = Field(default=None, description="The model ID to use for synthesis")
    language_code: Optional[str] = Field(default=None, description="Language code for the text")
    voice_settings: Optional['ElevenLabsVoiceSettings'] = Field(default=None, description="Voice configuration")
    pronunciation_dictionary_locators: Optional[List['ElevenLabsPronunciationDictionary']] = Field(
        default=None, description="Pronunciation dictionaries to use"
    )
    seed: Optional[int] = Field(default=None, ge=0, le=4294967295, description="Seed for reproducible results")
    previous_text: Optional[str] = Field(default=None, description="Previous text for context")
    next_text: Optional[str] = Field(default=None, description="Next text for context")
    previous_request_ids: Optional[List[str]] = Field(default=None, max_length=3, description="Previous request IDs")
    next_request_ids: Optional[List[str]] = Field(default=None, max_length=3, description="Next request IDs")
    apply_text_normalization: Optional[Literal["auto", "on", "off"]] = Field(
        default=None, description="Text normalization setting"
    )
    apply_language_text_normalization: Optional[bool] = Field(
        default=None, description="Whether to apply language-specific text normalization"
    )


class ElevenLabsVoiceSettings(BaseModel):
    """Voice settings for ElevenLabs speech synthesis."""
    
    stability: Optional[float] = Field(default=None, ge=0, le=1, description="Voice stability (0-1)")
    similarity_boost: Optional[float] = Field(default=None, ge=0, le=1, description="Similarity boost (0-1)")
    style: Optional[float] = Field(default=None, ge=0, le=1, description="Voice style (0-1)")
    use_speaker_boost: Optional[bool] = Field(default=None, description="Whether to use speaker boost")
    speed: Optional[float] = Field(default=None, description="Speech speed")


class ElevenLabsPronunciationDictionary(BaseModel):
    """Pronunciation dictionary reference."""
    
    pronunciation_dictionary_id: str = Field(description="Dictionary ID")
    version_id: Optional[str] = Field(default=None, description="Dictionary version ID")


class ElevenLabsSpeechOptions(BaseModel):
    """Provider-specific options for ElevenLabs speech synthesis."""
    
    language_code: Optional[str] = Field(default=None, description="Language code for the text")
    voice_settings: Optional[ElevenLabsVoiceSettings] = Field(default=None, description="Voice configuration")
    pronunciation_dictionary_locators: Optional[List[ElevenLabsPronunciationDictionary]] = Field(
        default=None, max_length=3, description="Pronunciation dictionaries"
    )
    seed: Optional[int] = Field(default=None, ge=0, le=4294967295, description="Seed for reproducible results")
    previous_text: Optional[str] = Field(default=None, description="Previous text for context")
    next_text: Optional[str] = Field(default=None, description="Next text for context")
    previous_request_ids: Optional[List[str]] = Field(default=None, max_length=3, description="Previous request IDs")
    next_request_ids: Optional[List[str]] = Field(default=None, max_length=3, description="Next request IDs")
    apply_text_normalization: Optional[Literal["auto", "on", "off"]] = Field(
        default=None, description="Text normalization setting"
    )
    apply_language_text_normalization: Optional[bool] = Field(
        default=None, description="Whether to apply language-specific text normalization"
    )
    enable_logging: Optional[bool] = Field(default=None, description="Whether to enable logging")


class ElevenLabsTranscriptionOptions(BaseModel):
    """Provider-specific options for ElevenLabs transcription."""
    
    language_code: Optional[str] = Field(default=None, description="Language code of the audio")
    tag_audio_events: Optional[bool] = Field(default=True, description="Tag audio events like laughter")
    num_speakers: Optional[int] = Field(default=None, ge=1, le=32, description="Maximum number of speakers")
    timestamps_granularity: Optional[Literal["none", "word", "character"]] = Field(
        default="word", description="Timestamp granularity"
    )
    diarize: Optional[bool] = Field(default=False, description="Whether to identify speakers")
    file_format: Optional[Literal["pcm_s16le_16", "other"]] = Field(
        default="other", description="Audio file format"
    )


class ElevenLabsTranscriptionAPIRequest(BaseModel):
    """API types for ElevenLabs transcription."""
    
    language_code: Optional[str] = Field(default=None, description="Language code")
    tag_audio_events: Optional[bool] = Field(default=None, description="Tag audio events")
    num_speakers: Optional[int] = Field(default=None, description="Number of speakers")
    timestamps_granularity: Optional[Literal["none", "word", "character"]] = Field(
        default=None, description="Timestamp granularity"
    )
    file_format: Optional[Literal["pcm_s16le_16", "other"]] = Field(
        default=None, description="File format"
    )


class ElevenLabsTranscriptionWord(BaseModel):
    """Word in transcription response."""
    
    text: str = Field(description="Word text")
    type: Literal["word", "spacing", "audio_event"] = Field(description="Word type")
    start: Optional[float] = Field(default=None, description="Start time in seconds")
    end: Optional[float] = Field(default=None, description="End time in seconds")
    speaker_id: Optional[str] = Field(default=None, description="Speaker ID")
    characters: Optional[List['ElevenLabsTranscriptionCharacter']] = Field(
        default=None, description="Character-level timestamps"
    )


class ElevenLabsTranscriptionCharacter(BaseModel):
    """Character in transcription response."""
    
    text: str = Field(description="Character text")
    start: Optional[float] = Field(default=None, description="Start time in seconds")
    end: Optional[float] = Field(default=None, description="End time in seconds")


class ElevenLabsTranscriptionResponse(BaseModel):
    """Response from ElevenLabs transcription API."""
    
    language_code: str = Field(description="Detected language code")
    language_probability: float = Field(description="Language detection confidence")
    text: str = Field(description="Full transcribed text")
    words: Optional[List[ElevenLabsTranscriptionWord]] = Field(
        default=None, description="Word-level transcription data"
    )


class ElevenLabsError(BaseModel):
    """Error response from ElevenLabs API."""
    
    error: 'ElevenLabsErrorDetail' = Field(description="Error details")


class ElevenLabsErrorDetail(BaseModel):
    """Error detail from ElevenLabs API."""
    
    message: str = Field(description="Error message")
    code: int = Field(description="Error code")