"""Azure OpenAI provider for AI SDK."""

from .embedding_model import AzureOpenAIEmbeddingModel
from .language_model import AzureOpenAIChatLanguageModel
from .provider import AzureOpenAIProvider, azure, create_azure

__all__ = [
    "AzureOpenAIProvider",
    "AzureOpenAIChatLanguageModel", 
    "AzureOpenAIEmbeddingModel",
    "create_azure",
    "azure",
]