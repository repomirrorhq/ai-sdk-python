"""ElevenLabs AI provider for speech synthesis and transcription."""

from .provider import ElevenLabsProvider, create_elevenlabs, ElevenLabs
from .speech_model import ElevenLabsSpeechModel
from .transcription_model import ElevenLabsTranscriptionModel
from .types import (
    ElevenLabsSpeechModelId,
    ElevenLabsTranscriptionModelId,
    ElevenLabsSpeechVoiceId,
    ElevenLabsSpeechOptions,
    ElevenLabsTranscriptionOptions,
    ElevenLabsVoiceSettings,
    ElevenLabsPronunciationDictionary,
)

__all__ = [
    # Main provider
    "ElevenLabsProvider",
    "create_elevenlabs", 
    "ElevenLabs",
    
    # Models
    "ElevenLabsSpeechModel",
    "ElevenLabsTranscriptionModel",
    
    # Types
    "ElevenLabsSpeechModelId",
    "ElevenLabsTranscriptionModelId",
    "ElevenLabsSpeechVoiceId",
    "ElevenLabsSpeechOptions",
    "ElevenLabsTranscriptionOptions",
    "ElevenLabsVoiceSettings",
    "ElevenLabsPronunciationDictionary",
]