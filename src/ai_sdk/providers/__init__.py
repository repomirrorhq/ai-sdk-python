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
from .groq import GroqProvider, create_groq
from .together import TogetherAIProvider, create_together
from .bedrock import BedrockProvider, create_bedrock
from .mistral import MistralProvider, create_mistral
from .cohere import CohereProvider, create_cohere_provider
from .perplexity import PerplexityProvider, create_perplexity_provider
from .deepseek import DeepSeekProvider, create_deepseek_provider

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
    "GroqProvider",
    "create_groq",
    "TogetherAIProvider",
    "create_together",
    "BedrockProvider",
    "create_bedrock",
    "MistralProvider",
    "create_mistral",
    "CohereProvider",
    "create_cohere_provider",
    "PerplexityProvider",
    "create_perplexity_provider",
    "DeepSeekProvider",
    "create_deepseek_provider",
]