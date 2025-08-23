"""RevAI provider type definitions."""

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field


class RevAIProviderSettings(BaseModel):
    """Settings for RevAI provider."""
    
    api_key: Optional[str] = None
    base_url: str = "https://api.rev.ai"
    headers: Optional[Dict[str, str]] = None


RevAITranscriptionModelId = Literal["machine", "low_cost", "fusion"]


class RevAINotificationConfig(BaseModel):
    """Configuration for webhook notifications when job is complete."""
    
    url: str = Field(description="URL to send the notification to")
    auth_headers: Optional[Dict[Literal["Authorization"], str]] = Field(
        None, description="Optional authorization headers for the notification request"
    )


class RevAISegmentToTranscribe(BaseModel):
    """Segment specification for partial transcription."""
    
    start: float = Field(description="Start time of the segment in seconds")
    end: float = Field(description="End time of the segment in seconds")


class RevAISpeakerName(BaseModel):
    """Speaker name configuration."""
    
    display_name: str = Field(description="Display name for the speaker")


class RevAISummarizationConfig(BaseModel):
    """Configuration for generating a summary of the transcription."""
    
    model: Optional[Literal["standard", "premium"]] = Field(
        "standard", description="Model to use for summarization"
    )
    type: Optional[Literal["paragraph", "bullets"]] = Field(
        "paragraph", description="Format of the summary"
    )
    prompt: Optional[str] = Field(None, description="Custom prompt for the summarization")


class RevAITargetLanguage(BaseModel):
    """Target language for translation."""
    
    language: Literal[
        "en", "en-us", "en-gb", "ar", "pt", "pt-br", "pt-pt", "fr", "fr-ca",
        "es", "es-es", "es-la", "it", "ja", "ko", "de", "ru"
    ] = Field(description="Language code for translation target")


class RevAITranslationConfig(BaseModel):
    """Configuration for translating the transcription."""
    
    target_languages: List[RevAITargetLanguage] = Field(description="Target languages for translation")
    model: Optional[Literal["standard", "premium"]] = Field(
        "standard", description="Model to use for translation"
    )


class RevAITranscriptionSettings(BaseModel):
    """Settings for RevAI transcription requests."""
    
    metadata: Optional[str] = Field(None, description="Optional metadata string to associate with the transcription job")
    notification_config: Optional[RevAINotificationConfig] = Field(None, description="Configuration for webhook notifications when job is complete")
    delete_after_seconds: Optional[int] = Field(None, description="Number of seconds after which the job will be automatically deleted")
    verbatim: Optional[bool] = Field(None, description="Whether to include filler words and false starts in the transcription")
    rush: Optional[bool] = Field(False, description="Whether to prioritize the job for faster processing")
    test_mode: Optional[bool] = Field(False, description="Whether to run the job in test mode")
    segments_to_transcribe: Optional[List[RevAISegmentToTranscribe]] = Field(None, description="Specific segments of the audio to transcribe")
    speaker_names: Optional[List[RevAISpeakerName]] = Field(None, description="Names to assign to speakers in the transcription")
    skip_diarization: Optional[bool] = Field(False, description="Whether to skip speaker diarization")
    skip_postprocessing: Optional[bool] = Field(False, description="Whether to skip post-processing steps")
    skip_punctuation: Optional[bool] = Field(False, description="Whether to skip adding punctuation to the transcription")
    remove_disfluencies: Optional[bool] = Field(False, description="Whether to remove disfluencies (um, uh, etc.) from the transcription")
    remove_atmospherics: Optional[bool] = Field(False, description="Whether to remove atmospheric sounds from the transcription")
    filter_profanity: Optional[bool] = Field(False, description="Whether to filter profanity from the transcription")
    speaker_channels_count: Optional[int] = Field(None, description="Number of speaker channels in the audio")
    speakers_count: Optional[int] = Field(None, description="Expected number of speakers in the audio")
    diarization_type: Optional[Literal["standard", "premium"]] = Field("standard", description="Type of diarization to use")
    custom_vocabulary_id: Optional[str] = Field(None, description="ID of a custom vocabulary to use for the transcription")
    custom_vocabularies: Optional[List[Dict[str, Any]]] = Field(None, description="Custom vocabularies to use for the transcription")
    strict_custom_vocabulary: Optional[bool] = Field(None, description="Whether to strictly enforce custom vocabulary")
    summarization_config: Optional[RevAISummarizationConfig] = Field(None, description="Configuration for generating a summary of the transcription")
    translation_config: Optional[RevAITranslationConfig] = Field(None, description="Configuration for translating the transcription")
    language: Optional[str] = Field("en", description="Language of the audio content")
    forced_alignment: Optional[bool] = Field(False, description="Whether to perform forced alignment")


class RevAIJobResponse(BaseModel):
    """Response from RevAI job submission or status check."""
    
    id: Optional[str] = None
    status: Optional[str] = None
    language: Optional[str] = None


class RevAIElement(BaseModel):
    """Individual element in a RevAI transcription monologue."""
    
    type: Optional[str] = None
    value: Optional[str] = None
    ts: Optional[float] = None
    end_ts: Optional[float] = None


class RevAIMonologue(BaseModel):
    """Monologue in RevAI transcription response."""
    
    elements: Optional[List[RevAIElement]] = None


class RevAITranscriptionResponse(BaseModel):
    """Complete transcription response from RevAI."""
    
    monologues: Optional[List[RevAIMonologue]] = None


class RevAIErrorDetail(BaseModel):
    """RevAI error detail structure."""
    
    message: str
    code: int


class RevAIError(BaseModel):
    """RevAI API error response."""
    
    error: RevAIErrorDetail