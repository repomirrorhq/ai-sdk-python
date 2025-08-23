"""
DeepSeek Provider for AI SDK Python.

Provides access to DeepSeek's models including the advanced reasoning model (deepseek-reasoner).
Features OpenAI-compatible API with DeepSeek-specific enhancements like prompt caching metrics.
"""

from .provider import DeepSeekProvider, create_deepseek_provider, deepseek_provider
from .language_model import DeepSeekLanguageModel
from .types import (
    DeepSeekChatModelId,
    DeepSeekProviderSettings,
    DeepSeekUsage,
    DeepSeekMetadataKeys
)

__all__ = [
    # Main provider classes
    "DeepSeekProvider",
    "create_deepseek_provider", 
    "deepseek_provider",
    
    # Model classes
    "DeepSeekLanguageModel",
    
    # Types
    "DeepSeekChatModelId",
    "DeepSeekProviderSettings",
    "DeepSeekUsage",
    "DeepSeekMetadataKeys",
]