"""AssemblyAI provider for AI SDK."""

from .provider import AssemblyAIProvider, create_assemblyai
from .transcription_model import AssemblyAITranscriptionModel
from .types import (
    AssemblyAITranscriptionModelId,
    AssemblyAITranscriptionSettings,
    AssemblyAIProviderSettings,
)

# Default provider instance (lazy initialization to avoid requiring API key at import)
assemblyai = None

__all__ = [
    "AssemblyAIProvider",
    "AssemblyAITranscriptionModel",
    "AssemblyAITranscriptionModelId",
    "AssemblyAITranscriptionSettings", 
    "AssemblyAIProviderSettings",
    "create_assemblyai",
    "assemblyai",
]