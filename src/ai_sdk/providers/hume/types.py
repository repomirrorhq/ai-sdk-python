"""Hume AI provider types and data models."""

from typing import Dict, List, Literal, Optional, Union, Any
from pydantic import BaseModel, Field

# Hume voice provider types
HumeVoiceProvider = Literal["HUME_AI", "CUSTOM_VOICE"]

# Audio format types
HumeAudioFormat = Literal["mp3", "pcm", "wav"]

class HumeVoiceById(BaseModel):
    """Hume voice specification by ID."""
    id: str = Field(description="Voice ID")
    provider: Optional[HumeVoiceProvider] = Field(None, description="Voice provider")

class HumeVoiceByName(BaseModel):
    """Hume voice specification by name."""
    name: str = Field(description="Voice name")
    provider: Optional[HumeVoiceProvider] = Field(None, description="Voice provider")

# Union type for voice specification
HumeVoice = Union[HumeVoiceById, HumeVoiceByName]

class HumeUtterance(BaseModel):
    """Hume utterance configuration."""
    text: str = Field(description="Text to convert to speech")
    description: Optional[str] = Field(None, description="Instructions for how the text should be spoken")
    speed: Optional[float] = Field(None, description="Speech rate multiplier")
    trailing_silence: Optional[float] = Field(None, description="Duration of silence after utterance in seconds")
    voice: Optional[HumeVoice] = Field(None, description="Voice configuration")

class HumeContextGeneration(BaseModel):
    """Context referencing a previous generation."""
    generation_id: str = Field(description="ID of a previously generated speech synthesis")

class HumeContextUtterances(BaseModel):
    """Context with list of utterances to synthesize."""
    utterances: List[HumeUtterance] = Field(description="List of utterances to synthesize")

# Union type for context specification
HumeContext = Union[HumeContextGeneration, HumeContextUtterances]

class HumeFormatSpec(BaseModel):
    """Audio format specification."""
    type: HumeAudioFormat = Field(description="Audio format type")

class HumeSpeechSettings(BaseModel):
    """Hume speech generation settings."""
    context: Optional[HumeContext] = Field(None, description="Context for speech synthesis")
    format: Optional[HumeFormatSpec] = Field(None, description="Output audio format")

class HumeProviderSettings(BaseModel):
    """Hume provider configuration."""
    api_key: Optional[str] = Field(None, description="Hume API key")
    base_url: str = Field("https://api.hume.ai", description="Base API URL")
    headers: Optional[Dict[str, str]] = Field(None, description="Additional headers")

# API types for request/response
class HumeSpeechAPIVoice(BaseModel):
    """Voice specification for API."""
    id: Optional[str] = None
    name: Optional[str] = None
    provider: Optional[HumeVoiceProvider] = None

class HumeSpeechAPIUtterance(BaseModel):
    """Utterance for API request."""
    text: str
    description: Optional[str] = None
    speed: Optional[float] = None
    trailing_silence: Optional[float] = None
    voice: Optional[HumeSpeechAPIVoice] = None

class HumeSpeechAPIContextGeneration(BaseModel):
    """API context with generation ID."""
    generation_id: str

class HumeSpeechAPIContextUtterances(BaseModel):
    """API context with utterances."""
    utterances: List[HumeSpeechAPIUtterance]

# Union type for API context
HumeSpeechAPIContext = Union[HumeSpeechAPIContextGeneration, HumeSpeechAPIContextUtterances]

class HumeSpeechAPIRequest(BaseModel):
    """Hume speech synthesis API request."""
    utterances: List[HumeSpeechAPIUtterance]
    context: Optional[HumeSpeechAPIContext] = None
    format: HumeFormatSpec

class HumeErrorResponse(BaseModel):
    """Hume error response."""
    message: str
    code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None