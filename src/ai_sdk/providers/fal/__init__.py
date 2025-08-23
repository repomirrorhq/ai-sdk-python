"""FAL.ai provider for AI SDK."""

from .provider import FalProvider, create_fal
from .image_model import FalImageModel
from .speech_model import FalSpeechModel
from .transcription_model import FalTranscriptionModel
from .types import (
    FalImageModelId,
    FalSpeechModelId,
    FalTranscriptionModelId,
    FalProviderSettings,
    FalImageSettings,
    FalSpeechSettings,
    FalTranscriptionSettings,
)

# Default provider instance
fal = create_fal()

__all__ = [
    "FalProvider",
    "FalImageModel",
    "FalSpeechModel",
    "FalTranscriptionModel",
    "FalImageModelId",
    "FalSpeechModelId", 
    "FalTranscriptionModelId",
    "FalProviderSettings",
    "FalImageSettings",
    "FalSpeechSettings",
    "FalTranscriptionSettings",
    "create_fal",
    "fal",
]