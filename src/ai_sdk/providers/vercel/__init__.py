"""
Vercel Provider for AI SDK Python.

Provides access to Vercel's v0 API designed for building modern web applications.
The v0 models support framework-aware completions, auto-fix capabilities, 
and multimodal inputs optimized for web development workflows.
"""

from .provider import VercelProvider, create_vercel_provider, vercel_provider
from .language_model import VercelLanguageModel
from .types import (
    VercelChatModelId,
    VercelProviderSettings,
    VercelLanguageModelOptions,
)

__all__ = [
    # Main provider classes
    "VercelProvider",
    "create_vercel_provider",
    "vercel_provider",
    
    # Model classes
    "VercelLanguageModel",
    
    # Types
    "VercelChatModelId",
    "VercelProviderSettings", 
    "VercelLanguageModelOptions",
]