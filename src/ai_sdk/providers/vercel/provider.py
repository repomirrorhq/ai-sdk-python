"""
Vercel Provider implementation.
Provides access to Vercel's v0 API for web development-focused AI capabilities.
"""

import os
from typing import Optional
from ai_sdk.core.types import Provider, LanguageModel, EmbeddingModel, ImageModel
from ai_sdk.errors.base import AISDKError
from .types import VercelChatModelId, VercelProviderSettings
from .language_model import VercelLanguageModel


class VercelProvider(Provider):
    """
    Vercel AI Provider for v0 API.
    
    The v0 API is designed for building modern web applications with:
    - Framework-aware completions optimized for Next.js, React, Vue, Svelte
    - Auto-fix capabilities that identify and correct common coding issues
    - Quick edit features for inline code improvements
    - Multimodal support for text and image inputs
    
    Example usage:
        provider = VercelProvider(api_key="your-api-key")
        model = await provider.language_model("v0-1.5-lg")
        
        result = await model.generate(
            "Create a Next.js component for a responsive navbar",
            provider_options={
                "vercel": {
                    "framework": "next.js",
                    "typescript": True,
                    "design_system": "tailwind"
                }
            }
        )
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.v0.dev/v1",
        headers: Optional[dict] = None,
        max_retries: int = 3,
        timeout: float = 60.0,
    ):
        # Load API key from environment if not provided
        self.api_key = api_key or os.getenv("VERCEL_API_KEY")
        if not self.api_key:
            raise AISDKError(
                "Vercel API key is required. Set VERCEL_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.base_url = base_url.rstrip('/')
        self.headers = headers or {}
        self.max_retries = max_retries
        self.timeout = timeout
    
    async def language_model(self, model_id: VercelChatModelId, **kwargs) -> LanguageModel:
        """
        Create a Vercel language model.
        
        Args:
            model_id: Vercel model identifier (v0-1.0-md, v0-1.5-md, v0-1.5-lg)
            **kwargs: Additional model configuration options
            
        Returns:
            VercelLanguageModel instance
        """
        return VercelLanguageModel(
            model_id=model_id,
            api_key=self.api_key,
            base_url=self.base_url,
            max_retries=self.max_retries,
            timeout=self.timeout,
            **kwargs
        )
    
    async def embedding_model(self, model_id: str, **kwargs) -> EmbeddingModel:
        """
        Create a Vercel embedding model.
        
        Note: Vercel v0 API does not currently support embedding models.
        """
        raise AISDKError(
            f"Vercel provider does not support embedding model '{model_id}'. "
            "The v0 API is focused on code generation and does not provide embedding capabilities."
        )
    
    async def image_model(self, model_id: str, **kwargs) -> ImageModel:
        """
        Create a Vercel image model.
        
        Note: Vercel v0 API does not currently support image generation models.
        """
        raise AISDKError(
            f"Vercel provider does not support image model '{model_id}'. "
            "The v0 API is focused on code generation and does not provide image generation capabilities."
        )
    
    async def close(self):
        """Close any resources used by the provider."""
        # No persistent resources to close for Vercel provider
        pass


def create_vercel_provider(
    api_key: Optional[str] = None,
    base_url: str = "https://api.v0.dev/v1", 
    headers: Optional[dict] = None,
    max_retries: int = 3,
    timeout: float = 60.0,
) -> VercelProvider:
    """
    Create a Vercel provider instance.
    
    Args:
        api_key: Vercel API key (defaults to VERCEL_API_KEY env var)
        base_url: Base URL for Vercel API (default: https://api.v0.dev/v1)
        headers: Additional headers for requests
        max_retries: Maximum retry attempts for failed requests
        timeout: Request timeout in seconds
        
    Returns:
        VercelProvider instance
        
    Example:
        # Using environment variable
        provider = create_vercel_provider()
        
        # With explicit API key
        provider = create_vercel_provider(api_key="your-api-key")
        
        # With custom configuration
        provider = create_vercel_provider(
            api_key="your-api-key",
            timeout=120.0,
            headers={"Custom-Header": "value"}
        )
    """
    return VercelProvider(
        api_key=api_key,
        base_url=base_url,
        headers=headers,
        max_retries=max_retries,
        timeout=timeout,
    )


# Create default provider instance
vercel_provider = create_vercel_provider