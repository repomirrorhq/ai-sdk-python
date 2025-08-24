"""
Anthropic provider implementation for AI SDK Python.

This module provides the main provider class for Anthropic's Claude models.
"""

import os
from typing import Optional, Dict, Any, Callable

from ...providers.base import BaseProvider
from ...providers.types import ProviderSettings
from .language_model import AnthropicLanguageModel


class AnthropicProvider(BaseProvider):
    """
    Provider for Anthropic Claude models.
    
    Supports all Claude models including:
    - claude-3-opus-20240229
    - claude-3-sonnet-20240229  
    - claude-3-haiku-20240307
    - claude-3-5-sonnet-20241022
    - claude-3-5-haiku-20241022
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        generate_id: Optional[Callable[[], str]] = None,
    ):
        """
        Initialize Anthropic provider.
        
        Args:
            api_key: Anthropic API key. If not provided, will look for ANTHROPIC_API_KEY env var.
            base_url: Base URL for Anthropic API. Defaults to https://api.anthropic.com/v1
            headers: Additional headers to send with requests
            generate_id: Function to generate unique IDs. Uses uuid4 if not provided.
        """
        if api_key is None:
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key is None:
                raise ValueError(
                    "Anthropic API key not found. Please provide api_key parameter "
                    "or set ANTHROPIC_API_KEY environment variable."
                )
        
        if base_url is None:
            base_url = "https://api.anthropic.com/v1"
        
        settings = ProviderSettings(
            api_key=api_key,
            base_url=base_url.rstrip("/"),
            headers=headers or {},
            generate_id=generate_id,
        )
        
        super().__init__(api_key=api_key, **settings.__dict__)
        self.settings = settings
    
    @property
    def name(self) -> str:
        """Name of the provider."""
        return "anthropic"
    
    def language_model(self, model_id: str, **kwargs: Any) -> AnthropicLanguageModel:
        """
        Create an Anthropic language model.
        
        Args:
            model_id: Model identifier (e.g., "claude-3-sonnet-20240229")
            
        Returns:
            AnthropicLanguageModel instance
        """
        return AnthropicLanguageModel(
            model_id=model_id,
            settings=self.settings,
        )
    
    def chat(self, model_id: str) -> AnthropicLanguageModel:
        """
        Create an Anthropic chat model (alias for language_model).
        
        Args:
            model_id: Model identifier
            
        Returns:
            AnthropicLanguageModel instance
        """
        return self.language_model(model_id)
    
    def messages(self, model_id: str) -> AnthropicLanguageModel:
        """
        Create an Anthropic messages model (alias for language_model).
        
        Args:
            model_id: Model identifier
            
        Returns:
            AnthropicLanguageModel instance
        """
        return self.language_model(model_id)


def create_anthropic(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    generate_id: Optional[Callable[[], str]] = None,
) -> AnthropicProvider:
    """
    Create an Anthropic provider instance.
    
    Args:
        api_key: Anthropic API key
        base_url: Base URL for Anthropic API
        headers: Additional headers to send with requests
        generate_id: Function to generate unique IDs
        
    Returns:
        AnthropicProvider instance
    """
    return AnthropicProvider(
        api_key=api_key,
        base_url=base_url,
        headers=headers,
        generate_id=generate_id,
    )


# Default provider instance (lazy initialization)
anthropic = None


def get_anthropic():
    """Get the default anthropic provider instance (lazy initialization)."""
    global anthropic
    if anthropic is None:
        anthropic = create_anthropic()
    return anthropic