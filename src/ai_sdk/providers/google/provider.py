"""Google Generative AI provider implementation."""

import os
from typing import Optional, Dict, Any

import httpx

from ...providers.base import Provider, LanguageModel
from .api_types import GoogleModelId
from .language_model import GoogleLanguageModel


class GoogleProvider(Provider):
    """Google Generative AI provider."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        http_client: Optional[httpx.AsyncClient] = None,
        **kwargs: Any,
    ):
        """
        Initialize Google provider.
        
        Args:
            api_key: Google API key (defaults to GOOGLE_GENERATIVE_AI_API_KEY env var)
            base_url: Base URL for API calls
            http_client: Optional HTTP client to use
            **kwargs: Additional provider options
        """
        super().__init__()
        
        # Use provided API key or get from environment
        self.api_key = api_key or os.getenv("GOOGLE_GENERATIVE_AI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Google API key is required. Set GOOGLE_GENERATIVE_AI_API_KEY environment variable "
                "or pass api_key parameter."
            )
        
        self.base_url = base_url or "https://generativelanguage.googleapis.com/v1beta"
        self.http_client = http_client
        self.provider_id = "google"
        self.provider_name = "Google Generative AI"
        
        # Store additional options
        self.provider_options = kwargs
    
    def language_model(self, model_id: GoogleModelId, **kwargs: Any) -> LanguageModel:
        """
        Create a Google language model.
        
        Args:
            model_id: The Google model ID (e.g., 'gemini-1.5-pro')
            **kwargs: Additional model options
            
        Returns:
            GoogleLanguageModel instance
        """
        return GoogleLanguageModel(
            model_id=model_id,
            api_key=self.api_key,
            base_url=self.base_url,
            http_client=self.http_client,
            **kwargs,
        )
    
    def chat(self, model_id: GoogleModelId, **kwargs: Any) -> LanguageModel:
        """
        Create a Google chat model (alias for language_model).
        
        Args:
            model_id: The Google model ID 
            **kwargs: Additional model options
            
        Returns:
            GoogleLanguageModel instance
        """
        return self.language_model(model_id, **kwargs)
    
    def __call__(self, model_id: GoogleModelId, **kwargs: Any) -> LanguageModel:
        """
        Create a Google language model (callable interface).
        
        Args:
            model_id: The Google model ID
            **kwargs: Additional model options
            
        Returns:
            GoogleLanguageModel instance
        """
        return self.language_model(model_id, **kwargs)
    
    @property
    def supported_models(self) -> Dict[str, str]:
        """Get supported Google models."""
        return {
            # Gemini 1.5 models
            "gemini-1.5-flash": "Gemini 1.5 Flash",
            "gemini-1.5-flash-latest": "Gemini 1.5 Flash (Latest)",
            "gemini-1.5-flash-001": "Gemini 1.5 Flash 001",
            "gemini-1.5-flash-002": "Gemini 1.5 Flash 002",
            "gemini-1.5-flash-8b": "Gemini 1.5 Flash 8B",
            "gemini-1.5-flash-8b-latest": "Gemini 1.5 Flash 8B (Latest)",
            "gemini-1.5-flash-8b-001": "Gemini 1.5 Flash 8B 001",
            "gemini-1.5-pro": "Gemini 1.5 Pro",
            "gemini-1.5-pro-latest": "Gemini 1.5 Pro (Latest)",
            "gemini-1.5-pro-001": "Gemini 1.5 Pro 001",
            "gemini-1.5-pro-002": "Gemini 1.5 Pro 002",
            
            # Gemini 2.0 models  
            "gemini-2.0-flash": "Gemini 2.0 Flash",
            "gemini-2.0-flash-001": "Gemini 2.0 Flash 001",
            "gemini-2.0-flash-live-001": "Gemini 2.0 Flash Live 001",
            "gemini-2.0-flash-lite": "Gemini 2.0 Flash Lite",
            "gemini-2.0-pro-exp-02-05": "Gemini 2.0 Pro Experimental",
            "gemini-2.0-flash-thinking-exp-01-21": "Gemini 2.0 Flash Thinking Experimental",
            "gemini-2.0-flash-exp": "Gemini 2.0 Flash Experimental",
            
            # Gemini 2.5 models
            "gemini-2.5-pro": "Gemini 2.5 Pro",
            "gemini-2.5-flash": "Gemini 2.5 Flash",
            "gemini-2.5-flash-lite": "Gemini 2.5 Flash Lite",
            "gemini-2.5-pro-exp-03-25": "Gemini 2.5 Pro Experimental",
            "gemini-2.5-flash-preview-04-17": "Gemini 2.5 Flash Preview",
            
            # Gemma models
            "gemma-3-12b-it": "Gemma 3 12B Instruction Tuned",
            "gemma-3-27b-it": "Gemma 3 27B Instruction Tuned",
        }


def create_google(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    http_client: Optional[httpx.AsyncClient] = None,
    **kwargs: Any,
) -> GoogleProvider:
    """
    Create a Google Generative AI provider instance.
    
    Args:
        api_key: Google API key (defaults to GOOGLE_GENERATIVE_AI_API_KEY env var)
        base_url: Base URL for API calls
        http_client: Optional HTTP client to use
        **kwargs: Additional provider options
        
    Returns:
        GoogleProvider instance
        
    Example:
        ```python
        from ai_sdk import create_google, generate_text
        
        # Create provider
        google = create_google(api_key="your-google-api-key")
        
        # Create model
        model = google.language_model("gemini-1.5-pro")
        
        # Generate text
        result = await generate_text(
            model=model,
            messages=[{"role": "user", "content": "Hello!"}]
        )
        print(result.text)
        ```
    """
    return GoogleProvider(
        api_key=api_key,
        base_url=base_url,
        http_client=http_client,
        **kwargs,
    )