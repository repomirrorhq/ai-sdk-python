"""Amazon Bedrock provider for AI SDK Python.

This module provides support for AWS Bedrock models including:
- Language models (Claude, Llama, Titan, etc.)
- Embedding models (Titan, Cohere)
- Image generation models (Titan, Stability AI)

Authentication is handled via AWS SigV4 or API key (Bearer token).
"""

from .provider import create_bedrock, bedrock, BedrockProvider, BedrockProviderSettings

__all__ = [
    "create_bedrock",
    "bedrock", 
    "BedrockProvider",
    "BedrockProviderSettings",
]