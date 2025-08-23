"""FAL.ai provider types and data models."""

from typing import Dict, List, Literal, Optional, Union, Any
from pydantic import BaseModel, Field

# FAL image model identifiers
FalImageModelId = Literal[
    "fal-ai/aura-sr",
    "fal-ai/bria/background/remove",
    "fal-ai/bria/eraser",
    "fal-ai/bria/product-shot", 
    "fal-ai/bria/reimagine",
    "bria/text-to-image/3.2",
    "fal-ai/bria/text-to-image/base",
    "fal-ai/bria/text-to-image/fast",
    "fal-ai/bria/text-to-image/hd",
    "fal-ai/bytedance/dreamina/v3.1/text-to-image",
    "fal-ai/ccsr",
    "fal-ai/clarity-upscaler",
    "fal-ai/creative-upscaler",
    "fal-ai/esrgan",
    "fal-ai/flux-general",
    "fal-ai/flux-general/differential-diffusion",
    "fal-ai/flux-general/image-to-image",
    "fal-ai/flux-general/inpainting",
    "fal-ai/flux-general/rf-inversion",
    "fal-ai/flux-kontext-lora/text-to-image",
    "fal-ai/flux-lora",
    "fal-ai/flux-lora/image-to-image",
    "fal-ai/flux-lora/inpainting", 
    "fal-ai/flux-pro/kontext",
    "fal-ai/flux-pro/kontext/max",
    "fal-ai/flux-pro/v1.1",
    "fal-ai/flux-pro/v1.1-ultra",
    "fal-ai/flux-pro/v1.1-ultra-finetuned",
    "fal-ai/flux-pro/v1.1-ultra/redux",
    "fal-ai/flux-pro/v1.1/redux",
    "fal-ai/flux/dev",
    "fal-ai/flux/dev/image-to-image",
    "fal-ai/flux/dev/redux",
    "fal-ai/flux/krea",
    "fal-ai/flux/krea/image-to-image",
    "fal-ai/flux/krea/redux",
    "fal-ai/flux/schnell",
    "fal-ai/flux/schnell/redux",
    "fal-ai/ideogram/character",
    "fal-ai/ideogram/character/edit",
    "fal-ai/ideogram/character/remix",
    "fal-ai/imagen4/preview",
    "fal-ai/luma-photon",
    "fal-ai/luma-photon/flash",
    "fal-ai/object-removal",
    "fal-ai/omnigen-v2",
    "fal-ai/qwen-image",
    "fal-ai/recraft/v3/text-to-image",
    "fal-ai/recraft/v3/image-to-image",
    "fal-ai/sana/sprint",
    "fal-ai/sana/v1.5/4.8b",
    "fal-ai/sana/v1.5/1.6b",
    "fal-ai/sky-raccoon",
    "fal-ai/wan/v2.2-5b/text-to-image",
    "fal-ai/wan/v2.2-a14b/text-to-image",
    "fal-ai/fashn/tryon/v1.6",
]

# FAL speech model identifiers
FalSpeechModelId = Literal[
    "fal-ai/coqui-xtts",
    "fal-ai/tortoise-tts",
]

# FAL transcription model identifiers  
FalTranscriptionModelId = Literal[
    "fal-ai/whisper",
    "fal-ai/whisper-diarization",
]

# Image size types
FalImageSizePreset = Literal[
    "square",
    "square_hd", 
    "landscape_16_9",
    "landscape_4_3",
    "portrait_16_9",
    "portrait_4_3",
]

class FalImageSizeCustom(BaseModel):
    """Custom image size specification."""
    width: int = Field(gt=0, description="Image width in pixels")
    height: int = Field(gt=0, description="Image height in pixels")

FalImageSize = Union[FalImageSizePreset, FalImageSizeCustom]

# FAL emotions for speech
FalEmotion = Literal[
    "angry", "disgusted", "fearful", "happy", "neutral", "sad", "surprised"
]

# FAL language boosts for speech
FalLanguageBoost = Literal[
    "en", "es", "fr", "de", "it", "pt", "pl", "tr", "ru", "nl", "cs", "ar", 
    "zh-cn", "ja", "ko", "hu"
]

class FalVoiceSettings(BaseModel):
    """Voice settings for FAL speech generation."""
    speed: Optional[float] = Field(None, description="Speech speed")
    vol: Optional[float] = Field(None, description="Volume level")
    voice_id: Optional[str] = Field(None, description="Voice ID")
    pitch: Optional[float] = Field(None, description="Voice pitch")
    english_normalization: Optional[bool] = Field(None, description="Enable English normalization")
    emotion: Optional[FalEmotion] = Field(None, description="Voice emotion")

class FalProviderSettings(BaseModel):
    """FAL provider configuration."""
    api_key: Optional[str] = Field(None, description="FAL API key")
    base_url: str = Field("https://fal.run", description="Base API URL")
    headers: Optional[Dict[str, str]] = Field(None, description="Additional headers")

class FalImageSettings(BaseModel):
    """FAL image generation settings.""" 
    image_size: Optional[FalImageSize] = Field(None, description="Image dimensions")
    num_images: Optional[int] = Field(None, ge=1, le=10, description="Number of images to generate")
    seed: Optional[int] = Field(None, description="Random seed for reproducible results")
    
    # Allow additional provider-specific options
    model_config = {"extra": "allow"}

class FalSpeechSettings(BaseModel):
    """FAL speech generation settings."""
    voice_setting: Optional[FalVoiceSettings] = Field(None, description="Voice configuration")
    audio_setting: Optional[Dict[str, Any]] = Field(None, description="Audio configuration")
    language_boost: Optional[FalLanguageBoost] = Field(None, description="Language boost setting")
    pronunciation_dict: Optional[Dict[str, str]] = Field(None, description="Pronunciation dictionary")
    output_format: Literal["url", "hex"] = Field("url", description="Output format")

class FalTranscriptionSettings(BaseModel):
    """FAL transcription settings."""
    language: Optional[str] = Field(None, description="Input language code")
    task: Optional[Literal["transcribe", "translate"]] = Field(None, description="Task type")
    
    # Allow additional provider-specific options
    model_config = {"extra": "allow"}

# Response schemas
class FalImage(BaseModel):
    """FAL image response."""
    url: str
    width: Optional[int] = None
    height: Optional[int] = None
    content_type: Optional[str] = None
    file_name: Optional[str] = None
    file_data: Optional[str] = None
    file_size: Optional[int] = None

class FalImageResponse(BaseModel):
    """FAL image generation response."""
    images: List[FalImage]
    prompt: Optional[str] = None
    seed: Optional[int] = None
    has_nsfw_concepts: Optional[List[bool]] = None
    nsfw_content_detected: Optional[List[bool]] = None
    timings: Optional[Dict[str, Any]] = None
    
    # Allow additional fields
    model_config = {"extra": "allow"}

class FalSpeechResponse(BaseModel):
    """FAL speech generation response."""
    audio: Dict[str, str]  # Contains 'url' key
    duration_ms: Optional[float] = None
    request_id: Optional[str] = None

class FalTranscriptionResponse(BaseModel):
    """FAL transcription response."""
    text: str
    segments: Optional[List[Dict[str, Any]]] = None
    language: Optional[str] = None
    
    # Allow additional fields
    model_config = {"extra": "allow"}

# Error schemas
class FalValidationError(BaseModel):
    """FAL validation error detail."""
    loc: List[str]
    msg: str
    type: str

class FalValidationErrorResponse(BaseModel):
    """FAL validation error response."""
    detail: List[FalValidationError]

class FalHttpErrorResponse(BaseModel):
    """FAL HTTP error response."""
    message: str