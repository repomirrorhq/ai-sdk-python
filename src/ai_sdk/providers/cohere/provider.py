"""
Cohere Provider implementation.
"""

from typing import Any, Dict
from ai_sdk.core.types import Provider, LanguageModel, EmbeddingModel
from ai_sdk.errors.base import AISDKError
from .types import CohereChatModelId, CohereEmbeddingModelId, CohereProviderSettings
from .language_model import CohereLanguageModel
from .embedding_model import CohereEmbeddingModel


class CohereProvider(Provider):
    """
    Cohere AI provider for text generation and embeddings.
    
    Supports:
    - Text generation with Command models
    - Text embeddings with Embed models
    - Tool calling and function execution
    - Document-aware chat with citations
    - Streaming responses
    """
    
    def __init__(self, settings: CohereProviderSettings | None = None):
        """
        Initialize Cohere provider.
        
        Args:
            settings: Configuration settings for the provider.
                     If None, will use default settings with environment variables.
        """
        self.settings = settings or CohereProviderSettings()
        self._provider_name = "cohere"
    
    @property
    def provider(self) -> str:
        return self._provider_name
    
    def language_model(self, model_id: CohereChatModelId) -> LanguageModel:
        """
        Create a Cohere language model for text generation.
        
        Args:
            model_id: The Cohere model identifier (e.g., "command-r-plus", "command-r")
            
        Returns:
            CohereLanguageModel instance
            
        Example:
            >>> provider = CohereProvider()
            >>> model = provider.language_model("command-r-plus")
            >>> result = await model.generate_text(prompt)
        """
        return CohereLanguageModel(model_id, self.settings)
    
    def embedding_model(self, model_id: CohereEmbeddingModelId) -> EmbeddingModel:
        """
        Create a Cohere embedding model for text embeddings.
        
        Args:
            model_id: The Cohere embedding model identifier (e.g., "embed-english-v3.0")
            
        Returns:
            CohereEmbeddingModel instance
            
        Example:
            >>> provider = CohereProvider()
            >>> model = provider.embedding_model("embed-english-v3.0")
            >>> result = await model.embed(["Hello world", "How are you?"])
        """
        return CohereEmbeddingModel(model_id, self.settings)
    
    def __call__(self, model_id: CohereChatModelId) -> LanguageModel:
        """
        Convenient method to create a language model.
        
        Args:
            model_id: The Cohere chat model identifier
            
        Returns:
            CohereLanguageModel instance
        """
        return self.language_model(model_id)
    
    def get_available_models(self) -> Dict[str, Any]:
        """Get information about available Cohere models."""
        return {
            "language_models": {
                "command-a-03-2025": {
                    "description": "Latest Command model with advanced reasoning",
                    "context_length": 128000,
                    "supports_tools": True,
                    "supports_streaming": True,
                    "supports_json": True
                },
                "command-r7b-12-2024": {
                    "description": "Efficient 7B parameter Command model",
                    "context_length": 128000,
                    "supports_tools": True,
                    "supports_streaming": True,
                    "supports_json": True
                },
                "command-r-plus": {
                    "description": "Advanced Command model with enhanced capabilities",
                    "context_length": 128000,
                    "supports_tools": True,
                    "supports_streaming": True,
                    "supports_json": True
                },
                "command-r": {
                    "description": "Balanced Command model for general use",
                    "context_length": 128000,
                    "supports_tools": True,
                    "supports_streaming": True,
                    "supports_json": True
                },
                "command": {
                    "description": "General purpose Command model",
                    "context_length": 4000,
                    "supports_tools": True,
                    "supports_streaming": True,
                    "supports_json": False
                },
                "command-light": {
                    "description": "Lightweight Command model for faster responses",
                    "context_length": 4000,
                    "supports_tools": True,
                    "supports_streaming": True,
                    "supports_json": False
                }
            },
            "embedding_models": {
                "embed-english-v3.0": {
                    "description": "Latest English embedding model",
                    "dimensions": 1024,
                    "max_input_length": 512,
                    "languages": ["en"]
                },
                "embed-multilingual-v3.0": {
                    "description": "Latest multilingual embedding model",
                    "dimensions": 1024,
                    "max_input_length": 512,
                    "languages": ["100+ languages"]
                },
                "embed-english-v2.0": {
                    "description": "High-quality English embeddings",
                    "dimensions": 4096,
                    "max_input_length": 512,
                    "languages": ["en"]
                },
                "embed-english-light-v3.0": {
                    "description": "Lightweight English embeddings",
                    "dimensions": 384,
                    "max_input_length": 512,
                    "languages": ["en"]
                },
                "embed-multilingual-light-v3.0": {
                    "description": "Lightweight multilingual embeddings",
                    "dimensions": 384,
                    "max_input_length": 512,
                    "languages": ["100+ languages"]
                }
            }
        }
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about this provider."""
        return {
            "name": "cohere",
            "description": "Cohere AI provider for enterprise text generation and embeddings",
            "capabilities": [
                "text_generation",
                "text_embeddings", 
                "streaming",
                "tool_calling",
                "json_mode",
                "document_chat",
                "citations",
                "search_results"
            ],
            "supported_modalities": {
                "input": ["text"],
                "output": ["text", "embeddings"]
            },
            "base_url": self.settings.base_url,
            "api_version": "v2"
        }


def create_cohere_provider(
    api_key: str | None = None,
    base_url: str | None = None,
    headers: Dict[str, str] | None = None,
) -> CohereProvider:
    """
    Create a Cohere provider with custom settings.
    
    Args:
        api_key: Cohere API key. If None, uses COHERE_API_KEY environment variable.
        base_url: Custom base URL for API calls. Defaults to https://api.cohere.com/v2
        headers: Additional headers to include in requests.
        
    Returns:
        CohereProvider instance
        
    Example:
        >>> provider = create_cohere_provider(api_key="your-api-key")
        >>> model = provider.language_model("command-r-plus")
    """
    settings = CohereProviderSettings()
    
    if api_key is not None:
        settings.api_key = api_key
    if base_url is not None:
        settings.base_url = base_url
    if headers is not None:
        settings.headers = headers
    
    return CohereProvider(settings)


# Default provider instance
cohere_provider = CohereProvider()