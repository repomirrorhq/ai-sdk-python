"""
Perplexity Provider for AI SDK Python.

Provides access to Perplexity's Sonar models for search-augmented text generation.
Specializes in real-time information access with web citations and source attribution.
"""

from .provider import PerplexityProvider, create_perplexity_provider, perplexity_provider
from .language_model import PerplexityLanguageModel
from .types import (
    PerplexityLanguageModelId,
    PerplexityProviderSettings,
    PerplexityCitation,
    PerplexityResponseFormat
)
from .message_converter import (
    convert_to_perplexity_messages,
    map_perplexity_finish_reason,
    prepare_search_parameters
)

__all__ = [
    # Main provider classes
    "PerplexityProvider",
    "create_perplexity_provider", 
    "perplexity_provider",
    
    # Model classes
    "PerplexityLanguageModel",
    
    # Types
    "PerplexityLanguageModelId",
    "PerplexityProviderSettings",
    "PerplexityCitation",
    "PerplexityResponseFormat",
    
    # Utilities
    "convert_to_perplexity_messages",
    "map_perplexity_finish_reason",
    "prepare_search_parameters",
]