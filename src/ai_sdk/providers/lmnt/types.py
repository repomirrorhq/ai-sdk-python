"""Type definitions for LMNT provider."""

from typing import Dict, Any, Optional, Union, Literal
from pydantic import BaseModel, Field


# Model IDs supported by LMNT
LMNTSpeechModelId = Literal[
    "aurora",    # Primary conversational model with advanced features
    "blizzard",  # Basic speech synthesis model
]

# Audio output formats
LMNTAudioFormat = Literal[
    "aac",    # Advanced Audio Coding
    "mp3",    # MPEG Audio Layer III (default)
    "mulaw",  # μ-law encoding
    "raw",    # Raw audio data
    "wav",    # Waveform Audio Format
]

# Supported sample rates
LMNTSampleRate = Literal[8000, 16000, 24000]

# Supported languages
LMNTLanguage = Literal[
    "auto",    # Auto-detection
    "en",      # English
    "es",      # Spanish
    "pt",      # Portuguese
    "fr",      # French
    "de",      # German
    "zh",      # Chinese
    "ko",      # Korean
    "hi",      # Hindi
    "ja",      # Japanese
    "ru",      # Russian
    "it",      # Italian
    "tr",      # Turkish
]


class LMNTSpeechOptions(BaseModel):
    """Options for LMNT speech synthesis."""
    
    model: Optional[LMNTSpeechModelId] = Field(default="aurora", description="Speech synthesis model to use")
    format: Optional[LMNTAudioFormat] = Field(default="mp3", description="Output audio format")
    sample_rate: Optional[LMNTSampleRate] = Field(default=24000, description="Audio sample rate in Hz")
    speed: Optional[float] = Field(default=1.0, ge=0.25, le=2.0, description="Speech speed multiplier")
    seed: Optional[int] = Field(default=None, description="Seed for deterministic generation")
    conversational: Optional[bool] = Field(default=False, description="Use conversational vs reading style (aurora only)")
    length: Optional[float] = Field(default=None, le=300.0, description="Maximum output length in seconds (aurora only)")
    top_p: Optional[float] = Field(default=None, ge=0.0, le=1.0, description="Stability control - lower is more consistent")
    temperature: Optional[float] = Field(default=None, ge=0.0, description="Expressiveness control - higher is more expressive")
    
    class Config:
        extra = "forbid"


class LMNTProviderSettings(BaseModel):
    """Settings for LMNT provider."""
    
    api_key: Optional[str] = Field(default=None, description="LMNT API key")
    base_url: Optional[str] = Field(default="https://api.lmnt.com/v1", description="Base API URL")
    headers: Optional[Dict[str, str]] = Field(default=None, description="Additional HTTP headers")
    
    class Config:
        extra = "forbid"


class LMNTAPIRequest(BaseModel):
    """Request payload for LMNT API."""
    
    text: str = Field(..., max_length=5000, description="Text to synthesize (max 5000 characters)")
    voice: Optional[str] = Field(default="ava", description="Voice ID to use")
    model: Optional[str] = Field(default="aurora", description="Model to use for synthesis")
    format: Optional[str] = Field(default="mp3", description="Output audio format")
    sample_rate: Optional[int] = Field(default=24000, description="Audio sample rate")
    speed: Optional[float] = Field(default=1.0, description="Speech speed")
    language: Optional[str] = Field(default=None, description="Language code")
    seed: Optional[int] = Field(default=None, description="Generation seed")
    conversational: Optional[bool] = Field(default=None, description="Conversational style")
    length: Optional[float] = Field(default=None, description="Output length")
    top_p: Optional[float] = Field(default=None, description="Stability control")
    temperature: Optional[float] = Field(default=None, description="Expressiveness")
    
    class Config:
        extra = "forbid"


class LMNTError(BaseModel):
    """LMNT API error response."""
    
    error: str = Field(..., description="Error message")
    code: Optional[str] = Field(default=None, description="Error code")
    
    class Config:
        extra = "allow"


class LMNTWarning(BaseModel):
    """LMNT API warning."""
    
    message: str = Field(..., description="Warning message")
    code: Optional[str] = Field(default=None, description="Warning code")
    
    class Config:
        extra = "allow"