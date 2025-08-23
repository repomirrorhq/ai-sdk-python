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

# Core functionality (will be implemented in phases)
# from .core.generate_text import generate_text, stream_text
# from .core.generate_object import generate_object, stream_object
# from .core.embed import embed, embed_many
# from .core.tools import tool, dynamic_tool
# from .schemas import json_schema, pydantic_schema
# from .providers import openai, anthropic, google, azure
# from .errors import AISDKError

# For now, export version and basic info
__all__ = [
    "__version__",
]