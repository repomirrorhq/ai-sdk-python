"""AssemblyAI provider for AI SDK."""

from .provider import AssemblyAIProvider, create_assemblyai
from .transcription_model import AssemblyAITranscriptionModel
from .types import (
    AssemblyAITranscriptionModelId,
    AssemblyAITranscriptionSettings,
    AssemblyAIProviderSettings,
)

# Default provider instance
assemblyai = create_assemblyai()

__all__ = [
    "AssemblyAIProvider",
    "AssemblyAITranscriptionModel",
    "AssemblyAITranscriptionModelId",
    "AssemblyAITranscriptionSettings", 
    "AssemblyAIProviderSettings",
    "create_assemblyai",
    "assemblyai",
]