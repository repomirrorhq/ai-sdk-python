"""AI SDK for Python - The AI Toolkit for Python.

This is a Python port of the AI SDK, providing a unified interface for working
with various AI providers including OpenAI, Anthropic, Google, and many more.

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
from .core.embed import embed, embed_many, EmbedResult, EmbedManyResult, EmbeddingUsage, cosine_similarity

# Tools
from .tools import Tool, ToolCall, ToolResult, tool, simple_tool, ToolRegistry

# Provider interfaces
from .providers.base import Provider, LanguageModel, EmbeddingModel
from .providers.types import Message, Content, FinishReason

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
    # Provider interfaces  
    "Provider",
    "LanguageModel", 
    "EmbeddingModel",
    "Message",
    "Content",
    "FinishReason",
    # Errors
    "AISDKError",
    "APIError", 
    "InvalidArgumentError",
]