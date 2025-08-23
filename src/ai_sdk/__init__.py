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

# Middleware
from .middleware import (
    wrap_language_model,
    LanguageModelMiddleware, 
    logging_middleware,
    caching_middleware,
    default_settings_middleware,
    telemetry_middleware,
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
    # Middleware
    "wrap_language_model",
    "LanguageModelMiddleware",
    "logging_middleware", 
    "caching_middleware",
    "default_settings_middleware",
    "telemetry_middleware",
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
    # Errors
    "AISDKError",
    "APIError", 
    "InvalidArgumentError",
]