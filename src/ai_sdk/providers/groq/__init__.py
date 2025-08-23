"""
Groq AI provider implementation

This module provides integration with Groq's high-speed inference platform,
supporting various open-source models with extremely fast generation speeds.

Key features:
- Ultra-fast inference with LPU (Language Processing Unit) technology
- Support for popular open-source models (LLaMA, Mixtral, Gemma, etc.)
- Real-time streaming capabilities
- Function calling support
- Audio transcription with Whisper models
"""

from .provider import GroqProvider, create_groq
from .language_model import GroqChatLanguageModel
from .transcription_model import GroqTranscriptionModel
from .types import GroqChatModelId, GroqTranscriptionModelId

__all__ = [
    "GroqProvider",
    "create_groq",
    "GroqChatLanguageModel", 
    "GroqTranscriptionModel",
    "GroqChatModelId",
    "GroqTranscriptionModelId",
]