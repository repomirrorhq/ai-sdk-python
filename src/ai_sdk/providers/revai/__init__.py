"""RevAI provider for speech-to-text transcription."""

from .provider import RevAIProvider, create_revai
from .transcription_model import RevAITranscriptionModel
from .types import (
    RevAIProviderSettings,
    RevAITranscriptionSettings,
    RevAITranscriptionModelId,
    RevAINotificationConfig,
    RevAISegmentToTranscribe,
    RevAISpeakerName,
    RevAISummarizationConfig,
    RevAITargetLanguage,
    RevAITranslationConfig,
)

__all__ = [
    "RevAIProvider",
    "create_revai",
    "RevAITranscriptionModel",
    "RevAIProviderSettings",
    "RevAITranscriptionSettings",
    "RevAITranscriptionModelId",
    "RevAINotificationConfig",
    "RevAISegmentToTranscribe",
    "RevAISpeakerName",
    "RevAISummarizationConfig",
    "RevAITargetLanguage",
    "RevAITranslationConfig",
]