"""Hume AI provider for AI SDK."""

from .provider import HumeProvider, create_hume
from .speech_model import HumeSpeechModel
from .types import (
    HumeProviderSettings,
    HumeSpeechSettings,
    HumeVoice,
    HumeUtterance,
)

# Default provider instance (lazy initialization to avoid requiring API key at import)
hume = None

__all__ = [
    "HumeProvider",
    "HumeSpeechModel",
    "HumeProviderSettings",
    "HumeSpeechSettings",
    "HumeVoice",
    "HumeUtterance",
    "create_hume",
    "hume",
]