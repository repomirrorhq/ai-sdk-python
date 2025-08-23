"""
OpenAI-Compatible Provider implementation

Supports any API that implements OpenAI-compatible endpoints including:
- Local models (Ollama, LMStudio, vLLM)
- Custom deployments
- Third-party services with OpenAI API compatibility
"""

from typing import Optional, Dict, Any, Generic, TypeVar
from urllib.parse import urljoin

from ..base import BaseProvider
from .types import (
    OpenAICompatibleProviderSettings, 
    OpenAICompatibleConfig,
    OpenAICompatibleChatModelId,
    OpenAICompatibleCompletionModelId, 
    OpenAICompatibleEmbeddingModelId,
    OpenAICompatibleImageModelId
)
from .language_model import OpenAICompatibleChatLanguageModel, OpenAICompatibleCompletionLanguageModel
from .embedding_model import OpenAICompatibleEmbeddingModel
from .image_model import OpenAICompatibleImageModel


# Type variables for generic provider
ChatModelId = TypeVar('ChatModelId', bound=str)
CompletionModelId = TypeVar('CompletionModelId', bound=str)
EmbeddingModelId = TypeVar('EmbeddingModelId', bound=str)
ImageModelId = TypeVar('ImageModelId', bound=str)


class OpenAICompatibleProvider(BaseProvider, Generic[ChatModelId, CompletionModelId, EmbeddingModelId, ImageModelId]):
    """
    Provider for OpenAI-compatible APIs.
    
    Supports any service that implements OpenAI's API specification,
    including local model servers and third-party providers.
    """
    
    def __init__(self, settings: OpenAICompatibleProviderSettings):
        """
        Initialize OpenAI-Compatible provider.
        
        Args:
            settings: Provider configuration settings including base URL and auth
        """
        self.settings = settings
    
    @property
    def name(self) -> str:
        return self.settings.name
    
    def __call__(self, model_id: ChatModelId) -> OpenAICompatibleChatLanguageModel:
        """Create a chat language model instance (callable interface)"""
        return self.language_model(model_id)
    
    def language_model(self, model_id: ChatModelId, **kwargs) -> OpenAICompatibleChatLanguageModel:
        """
        Create a chat language model instance.
        
        Args:
            model_id: Model identifier
            **kwargs: Additional model configuration
            
        Returns:
            OpenAI-compatible chat language model instance
        """
        return OpenAICompatibleChatLanguageModel(
            model_id=model_id,
            config=self._create_config("chat")
        )
    
    def chat_model(self, model_id: ChatModelId) -> OpenAICompatibleChatLanguageModel:
        """
        Create a chat model instance (alias for language_model).
        
        Args:
            model_id: Chat model identifier
            
        Returns:
            OpenAI-compatible chat language model instance
        """
        return self.language_model(model_id)
    
    def completion_model(self, model_id: CompletionModelId) -> OpenAICompatibleCompletionLanguageModel:
        """
        Create a completion model instance.
        
        Args:
            model_id: Completion model identifier
            
        Returns:
            OpenAI-compatible completion language model instance
        """
        return OpenAICompatibleCompletionLanguageModel(
            model_id=model_id,
            config=self._create_config("completion")
        )
    
    def text_embedding_model(self, model_id: EmbeddingModelId) -> OpenAICompatibleEmbeddingModel:
        """
        Create a text embedding model instance.
        
        Args:
            model_id: Embedding model identifier
            
        Returns:
            OpenAI-compatible embedding model instance
        """
        return OpenAICompatibleEmbeddingModel(
            model_id=model_id,
            config=self._create_config("embedding")
        )
    
    def image_model(self, model_id: ImageModelId) -> OpenAICompatibleImageModel:
        """
        Create an image generation model instance.
        
        Args:
            model_id: Image model identifier
            
        Returns:
            OpenAI-compatible image model instance
        """
        return OpenAICompatibleImageModel(
            model_id=model_id,
            config=self._create_config("image")
        )
    
    def _create_config(self, model_type: str) -> OpenAICompatibleConfig:
        """Create configuration for OpenAI-compatible models"""
        return OpenAICompatibleConfig(
            provider=f"{self.settings.name}.{model_type}",
            base_url=self._get_base_url(),
            headers=self._get_headers,
            fetch=self.settings.fetch,
            include_usage=self.settings.include_usage
        )
    
    def _get_base_url(self) -> str:
        """Get the base URL, removing trailing slash"""
        return self.settings.base_url.rstrip('/')
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        headers = {}
        
        # Add API key authentication if provided
        if self.settings.api_key:
            headers["Authorization"] = f"Bearer {self.settings.api_key}"
        
        # Add custom headers
        if self.settings.headers:
            headers.update(self.settings.headers)
        
        return headers


def create_openai_compatible(settings: OpenAICompatibleProviderSettings) -> OpenAICompatibleProvider:
    """
    Create an OpenAI-compatible provider instance.
    
    Args:
        settings: Provider configuration settings
        
    Returns:
        OpenAI-compatible provider instance
        
    Example:
        ```python
        # For Ollama local server
        ollama = create_openai_compatible(
            OpenAICompatibleProviderSettings(
                name="ollama",
                base_url="http://localhost:11434/v1",
            )
        )
        
        # For LMStudio local server
        lmstudio = create_openai_compatible(
            OpenAICompatibleProviderSettings(
                name="lmstudio",
                base_url="http://localhost:1234/v1",
            )
        )
        
        # For a custom service with API key
        custom = create_openai_compatible(
            OpenAICompatibleProviderSettings(
                name="custom-service",
                base_url="https://api.custom-service.com/v1",
                api_key="your-api-key",
                headers={"X-Custom-Header": "value"}
            )
        )
        ```
    """
    return OpenAICompatibleProvider(settings)