"""Provider interfaces and base classes for AI SDK Python."""

from .base import (
    Provider,
    LanguageModel,
    EmbeddingModel,
    ImageModel,
    SpeechModel,
    TranscriptionModel,
)
from .types import (
    GenerateOptions,
    StreamOptions,
    GenerateResult,
    StreamResult,
    Usage,
    FinishReason,
    Content,
    Message,
    ProviderMetadata,
)

# Import available providers
from .openai import OpenAIProvider, create_openai
from .anthropic import AnthropicProvider, create_anthropic
from .google import GoogleProvider, create_google
from .azure import AzureOpenAIProvider, create_azure

__all__ = [
    "Provider",
    "LanguageModel",
    "EmbeddingModel",
    "ImageModel",
    "SpeechModel",
    "TranscriptionModel",
    "GenerateOptions",
    "StreamOptions",
    "GenerateResult",
    "StreamResult",
    "Usage",
    "FinishReason",
    "Content",
    "Message",
    "ProviderMetadata",
    # Providers
    "OpenAIProvider",
    "create_openai",
    "AnthropicProvider", 
    "create_anthropic",
    "GoogleProvider",
    "create_google",
    "AzureOpenAIProvider",
    "create_azure",
]