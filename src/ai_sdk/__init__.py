"""AI SDK for Python - The AI Toolkit for Python.

This is a Python port of the AI SDK, providing a unified interface for working
with various AI providers including OpenAI, Anthropic, Google, Azure OpenAI, and many more.

Key features:
- Text generation with `generate_text()` and `stream_text()`
- Structured object generation with `generate_object()` and `stream_object()`
- Tool calling and function calling support
- Embeddings with `embed()` and `embed_many()`
- Multiple AI provider support
- Async/await native support
- Type safety with Pydantic models
"""

__version__ = "0.1.0"

# Core functionality
from .core.generate_text import generate_text, stream_text
from .core.generate_object import generate_object, stream_object, GenerateObjectResult, StreamObjectResult
from .core.generate_image import generate_image, generate_image_sync, GenerateImageResult, NoImageGeneratedError
from .core.generate_speech import generate_speech, generate_speech_sync, GenerateSpeechResult, NoSpeechGeneratedError
from .core.transcribe import transcribe, transcribe_sync, TranscriptionResult, NoTranscriptGeneratedError
from .core.embed import embed, embed_many, EmbedResult, EmbedManyResult, EmbeddingUsage, cosine_similarity

# Tools
from .tools import Tool, ToolCall, ToolResult, tool, simple_tool, ToolRegistry

# Agent system
from .agent import Agent, AgentSettings

# Registry system
from .registry import create_provider_registry, ProviderRegistry, custom_provider

# Middleware
from .middleware import (
    wrap_language_model,
    LanguageModelMiddleware, 
    logging_middleware,
    caching_middleware,
    default_settings_middleware,
    telemetry_middleware,
    extract_reasoning_middleware,
    simulate_streaming_middleware,
)

# Provider interfaces
from .providers.base import Provider, LanguageModel, EmbeddingModel, ImageModel, SpeechModel, TranscriptionModel
from .providers.types import Message, Content, FinishReason

# Providers
from .providers.openai import create_openai
from .providers.anthropic import create_anthropic
from .providers.google import create_google
from .providers.azure import create_azure
from .providers.groq import create_groq
from .providers.together import create_together
from .providers.bedrock import create_bedrock
from .providers.mistral import create_mistral
from .providers.cohere import create_cohere_provider as create_cohere
from .providers.xai import XAIProvider as create_xai
from .providers.perplexity import create_perplexity_provider as create_perplexity
from .providers.deepseek import create_deepseek_provider as create_deepseek
from .providers.cerebras import create_cerebras_provider as create_cerebras
from .providers.fireworks import create_fireworks_provider as create_fireworks

# Errors
from .errors import AISDKError, APIError, InvalidArgumentError

# For now, export implemented functionality
__all__ = [
    "__version__",
    # Core functions
    "generate_text",
    "stream_text",
    "generate_object", 
    "stream_object",
    "GenerateObjectResult",
    "StreamObjectResult",
    "generate_image",
    "generate_image_sync",
    "GenerateImageResult",
    "NoImageGeneratedError",
    "generate_speech",
    "generate_speech_sync",
    "GenerateSpeechResult",
    "NoSpeechGeneratedError",
    "transcribe",
    "transcribe_sync",
    "TranscriptionResult", 
    "NoTranscriptGeneratedError",
    "embed",
    "embed_many",
    "EmbedResult",
    "EmbedManyResult", 
    "EmbeddingUsage",
    "cosine_similarity",
    # Tools
    "Tool",
    "ToolCall", 
    "ToolResult",
    "tool",
    "simple_tool",
    "ToolRegistry",
    # Agent system
    "Agent",
    "AgentSettings",
    # Registry system
    "create_provider_registry",
    "ProviderRegistry",
    "custom_provider",
    # Middleware
    "wrap_language_model",
    "LanguageModelMiddleware",
    "logging_middleware", 
    "caching_middleware",
    "default_settings_middleware",
    "telemetry_middleware",
    "extract_reasoning_middleware",
    "simulate_streaming_middleware",
    # Provider interfaces  
    "Provider",
    "LanguageModel", 
    "EmbeddingModel",
    "ImageModel",
    "SpeechModel",
    "TranscriptionModel",
    "Message",
    "Content",
    "FinishReason",
    # Providers
    "create_openai",
    "create_anthropic",
    "create_google",
    "create_azure",
    "create_groq",
    "create_together",
    "create_bedrock",
    "create_mistral",
    "create_cohere",
    "create_xai",
    "create_perplexity",
    "create_deepseek",
    "create_cerebras",
    "create_fireworks",
    # Errors
    "AISDKError",
    "APIError", 
    "InvalidArgumentError",
]