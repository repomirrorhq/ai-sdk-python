"""
Gladia Provider for AI SDK Python.

Provides access to Gladia's advanced audio transcription API with support for
speaker diarization, multi-language detection, summarization, and other AI-powered features.
"""

from .provider import GladiaProvider, create_gladia_provider, gladia_provider
from .transcription_model import GladiaTranscriptionModel
from .types import (
    GladiaProviderSettings,
    GladiaTranscriptionOptions,
    GladiaDiarizationConfig,
    GladiaTranslationConfig,
    GladiaSummarizationConfig,
    GladiaCustomVocabularyConfig,
    GladiaSubtitlesConfig,
    GladiaCallbackConfig,
    GladiaCodeSwitchingConfig,
    GladiaCustomSpellingConfig,
    GladiaAudioToLlmConfig
)

__all__ = [
    # Main provider classes
    "GladiaProvider",
    "create_gladia_provider", 
    "gladia_provider",
    
    # Model classes
    "GladiaTranscriptionModel",
    
    # Types and configurations
    "GladiaProviderSettings",
    "GladiaTranscriptionOptions",
    "GladiaDiarizationConfig",
    "GladiaTranslationConfig", 
    "GladiaSummarizationConfig",
    "GladiaCustomVocabularyConfig",
    "GladiaSubtitlesConfig",
    "GladiaCallbackConfig",
    "GladiaCodeSwitchingConfig",
    "GladiaCustomSpellingConfig",
    "GladiaAudioToLlmConfig",
]