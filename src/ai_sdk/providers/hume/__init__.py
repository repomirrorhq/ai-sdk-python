"""Hume AI provider for AI SDK."""

from .provider import HumeProvider, create_hume
from .speech_model import HumeSpeechModel
from .types import (
    HumeProviderSettings,
    HumeSpeechSettings,
    HumeVoice,
    HumeUtterance,
)

# Default provider instance
hume = create_hume()

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