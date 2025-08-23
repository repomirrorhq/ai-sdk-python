"""
Fireworks Provider for AI SDK Python.

Provides access to Fireworks AI's high-performance model hosting platform
with optimized inference and a comprehensive model marketplace.
"""

from .provider import FireworksProvider, create_fireworks_provider, fireworks_provider
from .language_model import FireworksLanguageModel
from .embedding_model import FireworksEmbeddingModel
from .types import (
    FireworksChatModelId,
    FireworksEmbeddingModelId,
    FireworksProviderSettings,
)

__all__ = [
    # Main provider classes
    "FireworksProvider",
    "create_fireworks_provider", 
    "fireworks_provider",
    
    # Model classes
    "FireworksLanguageModel",
    "FireworksEmbeddingModel",
    
    # Types
    "FireworksChatModelId",
    "FireworksEmbeddingModelId",
    "FireworksProviderSettings",
]