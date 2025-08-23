"""
OpenAI-Compatible Provider for AI SDK

This provider supports any API that implements OpenAI-compatible endpoints,
including local models (Ollama, LMStudio, vLLM), custom deployments, and 
third-party services that follow the OpenAI API specification.

Key features:
- Configurable base URL and authentication
- Support for chat completions, embeddings, and image generation
- Custom headers and query parameters
- Compatible with popular local model servers
"""

from .provider import OpenAICompatibleProvider, create_openai_compatible
from .types import OpenAICompatibleProviderSettings
from .errors import OpenAICompatibleError

__all__ = [
    "OpenAICompatibleProvider",
    "create_openai_compatible", 
    "OpenAICompatibleProviderSettings",
    "OpenAICompatibleError",
]