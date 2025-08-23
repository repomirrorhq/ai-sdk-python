"""AI SDK Registry System - Dynamic provider registration and management.

This module provides a registry system for managing multiple AI providers
and accessing their models through a unified interface. Key features:

- Register multiple providers in a single registry
- Access models using `provider:model` format (e.g., 'openai:gpt-4')
- Apply middleware to all language models from the registry
- Create custom providers with fallback support
- Dynamic model resolution and provider routing

Example Usage:
    ```python
    from ai_sdk import create_openai, create_anthropic
    from ai_sdk.registry import create_provider_registry, custom_provider
    
    # Create registry with multiple providers
    registry = create_provider_registry({
        "openai": create_openai(),
        "anthropic": create_anthropic()
    })
    
    # Access models through registry
    gpt4 = registry.language_model("openai:gpt-4")
    claude = registry.language_model("anthropic:claude-3-sonnet")
    
    # Create custom provider
    custom = custom_provider(
        language_models={
            "my-model": gpt4
        },
        fallback_provider=create_openai()
    )
    ```
"""

from .provider_registry import create_provider_registry, ProviderRegistry
from .custom_provider import custom_provider
from .errors import NoSuchProviderError, NoSuchModelError

__all__ = [
    "create_provider_registry",
    "ProviderRegistry", 
    "custom_provider",
    "NoSuchProviderError",
    "NoSuchModelError",
]