"""
Cohere Provider for AI SDK Python.

Provides access to Cohere's Command models for text generation and Embed models for embeddings.
Supports advanced features like tool calling, document-aware chat, and search integration.
"""

from .provider import CohereProvider, create_cohere_provider, cohere_provider
from .language_model import CohereLanguageModel
from .embedding_model import CohereEmbeddingModel
from .types import (
    CohereChatModelId,
    CohereEmbeddingModelId, 
    CohereProviderSettings,
    CohereDocument,
    CohereTool,
    CohereToolChoice,
    CohereResponseFormat
)
from .message_converter import (
    convert_to_cohere_messages,
    prepare_cohere_tools,
    map_cohere_finish_reason
)

__all__ = [
    # Main provider classes
    "CohereProvider",
    "create_cohere_provider", 
    "cohere_provider",
    
    # Model classes
    "CohereLanguageModel",
    "CohereEmbeddingModel",
    
    # Types
    "CohereChatModelId",
    "CohereEmbeddingModelId",
    "CohereProviderSettings", 
    "CohereDocument",
    "CohereTool",
    "CohereToolChoice",
    "CohereResponseFormat",
    
    # Utilities
    "convert_to_cohere_messages",
    "prepare_cohere_tools",
    "map_cohere_finish_reason",
]