"""
Type definitions for Gladia Provider.
"""

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


class GladiaProviderSettings(BaseModel):
    """Settings for configuring the Gladia provider."""
    
    api_key: Optional[str] = Field(
        default=None,
        description="Gladia API key. If not provided, uses GLADIA_API_KEY environment variable."
    )
    base_url: str = Field(
        default="https://api.gladia.io",
        description="Base URL for Gladia API calls."
    )
    headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="Additional headers to include in API requests."
    )
    timeout: float = Field(
        default=300.0,
        description="Request timeout in seconds (default 5 minutes for transcription)."
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts for failed requests."
    )


class GladiaCustomVocabularyItem(BaseModel):
    """Configuration for a custom vocabulary item."""
    
    value: str = Field(description="The vocabulary term")
    intensity: Optional[float] = Field(
        default=None,
        description="Intensity of the term in recognition"
    )
    pronunciations: Optional[List[str]] = Field(
        default=None,
        description="Alternative pronunciations for the term"
    )
    language: Optional[str] = Field(
        default=None,
        description="Language of the term"
    )


class GladiaCustomVocabularyConfig(BaseModel):
    """Configuration for custom vocabulary."""
    
    vocabulary: List[Union[str, GladiaCustomVocabularyItem]] = Field(
        description="Array of vocabulary terms or objects with pronunciation details"
    )
    default_intensity: Optional[float] = Field(
        default=None,
        description="Default intensity for all vocabulary terms"
    )


class GladiaCodeSwitchingConfig(BaseModel):
    """Configuration for code switching (multiple languages)."""
    
    languages: Optional[List[str]] = Field(
        default=None,
        description="Languages to consider for code switching"
    )


class GladiaCallbackConfig(BaseModel):
    """Configuration for transcription completion callbacks."""
    
    url: str = Field(description="URL to send the callback to")
    method: Optional[Literal["POST", "PUT"]] = Field(
        default="POST",
        description="HTTP method for the callback"
    )


class GladiaSubtitlesConfig(BaseModel):
    """Configuration for subtitle generation."""
    
    formats: Optional[List[Literal["srt", "vtt"]]] = Field(
        default=None,
        description="Subtitle file formats to generate"
    )
    minimum_duration: Optional[float] = Field(
        default=None,
        description="Minimum duration for subtitle segments in seconds"
    )
    maximum_duration: Optional[float] = Field(
        default=None,
        description="Maximum duration for subtitle segments in seconds"
    )
    maximum_characters_per_row: Optional[int] = Field(
        default=None,
        description="Maximum characters per row in subtitles"
    )
    maximum_rows_per_caption: Optional[int] = Field(
        default=None,
        description="Maximum rows per caption in subtitles"
    )
    style: Optional[Literal["default", "compliance"]] = Field(
        default="default",
        description="Style of subtitles"
    )


class GladiaDiarizationConfig(BaseModel):
    """Configuration for speaker diarization."""
    
    number_of_speakers: Optional[int] = Field(
        default=None,
        description="Exact number of speakers to identify"
    )
    min_speakers: Optional[int] = Field(
        default=None,
        description="Minimum number of speakers to identify"
    )
    max_speakers: Optional[int] = Field(
        default=None,
        description="Maximum number of speakers to identify"
    )
    enhanced: Optional[bool] = Field(
        default=False,
        description="Whether to use enhanced diarization"
    )


class GladiaTranslationConfig(BaseModel):
    """Configuration for translation."""
    
    target_languages: List[str] = Field(
        description="Target languages for translation"
    )
    model: Optional[Literal["base", "enhanced"]] = Field(
        default="base",
        description="Translation model to use"
    )
    match_original_utterances: Optional[bool] = Field(
        default=False,
        description="Whether to match original utterances in translation"
    )


class GladiaSummarizationConfig(BaseModel):
    """Configuration for summarization."""
    
    type: Optional[Literal["general", "bullet_points", "concise"]] = Field(
        default="general",
        description="Type of summary to generate"
    )


class GladiaCustomSpellingConfig(BaseModel):
    """Configuration for custom spelling."""
    
    spelling_dictionary: Dict[str, List[str]] = Field(
        description="Dictionary of custom spellings"
    )


class GladiaAudioToLlmConfig(BaseModel):
    """Configuration for audio to language model processing."""
    
    prompts: List[str] = Field(
        description="Prompts to send to the language model"
    )


class GladiaTranscriptionOptions(BaseModel):
    """Options for Gladia transcription requests."""
    
    context_prompt: Optional[str] = Field(
        default=None,
        description="Optional context prompt to guide the transcription"
    )
    custom_vocabulary: Optional[Union[bool, List[Any]]] = Field(
        default=None,
        description="Custom vocabulary to improve transcription accuracy"
    )
    custom_vocabulary_config: Optional[GladiaCustomVocabularyConfig] = Field(
        default=None,
        description="Configuration for custom vocabulary"
    )
    detect_language: Optional[bool] = Field(
        default=None,
        description="Whether to automatically detect the language of the audio"
    )
    enable_code_switching: Optional[bool] = Field(
        default=None,
        description="Whether to enable code switching (multiple languages in the same audio)"
    )
    code_switching_config: Optional[GladiaCodeSwitchingConfig] = Field(
        default=None,
        description="Configuration for code switching"
    )
    language: Optional[str] = Field(
        default=None,
        description="Specific language for transcription (ISO 639-1 code)"
    )
    callback: Optional[bool] = Field(
        default=None,
        description="Whether to enable callback when transcription is complete"
    )
    callback_config: Optional[GladiaCallbackConfig] = Field(
        default=None,
        description="Configuration for callback"
    )
    subtitles: Optional[bool] = Field(
        default=None,
        description="Whether to generate subtitles"
    )
    subtitles_config: Optional[GladiaSubtitlesConfig] = Field(
        default=None,
        description="Configuration for subtitles generation"
    )
    diarization: Optional[bool] = Field(
        default=None,
        description="Whether to enable speaker diarization (speaker identification)"
    )
    diarization_config: Optional[GladiaDiarizationConfig] = Field(
        default=None,
        description="Configuration for diarization"
    )
    translation: Optional[bool] = Field(
        default=None,
        description="Whether to translate the transcription"
    )
    translation_config: Optional[GladiaTranslationConfig] = Field(
        default=None,
        description="Configuration for translation"
    )
    summarization: Optional[bool] = Field(
        default=None,
        description="Whether to generate a summary of the transcription"
    )
    summarization_config: Optional[GladiaSummarizationConfig] = Field(
        default=None,
        description="Configuration for summarization"
    )
    moderation: Optional[bool] = Field(
        default=None,
        description="Whether to enable content moderation"
    )
    named_entity_recognition: Optional[bool] = Field(
        default=None,
        description="Whether to enable named entity recognition"
    )
    chapterization: Optional[bool] = Field(
        default=None,
        description="Whether to enable automatic chapter creation"
    )
    name_consistency: Optional[bool] = Field(
        default=None,
        description="Whether to ensure consistent naming of entities"
    )
    custom_spelling: Optional[bool] = Field(
        default=None,
        description="Whether to enable custom spelling"
    )
    custom_spelling_config: Optional[GladiaCustomSpellingConfig] = Field(
        default=None,
        description="Configuration for custom spelling"
    )
    structured_data_extraction: Optional[bool] = Field(
        default=None,
        description="Whether to extract structured data from the transcription"
    )
    structured_data_extraction_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Configuration for structured data extraction"
    )
    sentiment_analysis: Optional[bool] = Field(
        default=None,
        description="Whether to perform sentiment analysis on the transcription"
    )
    audio_to_llm: Optional[bool] = Field(
        default=None,
        description="Whether to send audio to a language model for processing"
    )
    audio_to_llm_config: Optional[GladiaAudioToLlmConfig] = Field(
        default=None,
        description="Configuration for audio to language model processing"
    )
    custom_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Custom metadata to include with the transcription"
    )
    sentences: Optional[bool] = Field(
        default=None,
        description="Whether to include sentence-level segmentation"
    )
    display_mode: Optional[bool] = Field(
        default=None,
        description="Whether to enable display mode"
    )
    punctuation_enhanced: Optional[bool] = Field(
        default=None,
        description="Whether to enhance punctuation in the transcription"
    )


# API Response Types
class GladiaUploadResponse(BaseModel):
    """Response from Gladia upload endpoint."""
    audio_url: str


class GladiaTranscriptionInitResponse(BaseModel):
    """Response from Gladia transcription initialization."""
    result_url: str


class GladiaTranscriptionUtterance(BaseModel):
    """A single utterance in the transcription."""
    start: float
    end: float
    text: str
    confidence: Optional[float] = None
    speaker: Optional[str] = None


class GladiaTranscriptionMetadata(BaseModel):
    """Metadata about the transcribed audio."""
    audio_duration: float
    number_of_distinct_channels: Optional[int] = None


class GladiaTranscriptionData(BaseModel):
    """Transcription data from Gladia."""
    full_transcript: str
    languages: List[str]
    utterances: List[GladiaTranscriptionUtterance]


class GladiaTranscriptionResult(BaseModel):
    """Complete transcription result from Gladia."""
    metadata: GladiaTranscriptionMetadata
    transcription: GladiaTranscriptionData


class GladiaTranscriptionStatus(BaseModel):
    """Transcription status response."""
    status: Literal["queued", "processing", "done", "error"]
    result: Optional[GladiaTranscriptionResult] = None
    error: Optional[str] = None