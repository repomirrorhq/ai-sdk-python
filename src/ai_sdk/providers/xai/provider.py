"""xAI provider implementation."""

import os
from typing import Optional, Union

import httpx

from ..base import BaseProvider
from .language_model import XAILanguageModel
from .types import XAIChatModelId


class XAIProvider(BaseProvider):
    """
    xAI provider for accessing Grok models.
    
    This provider supports:
    - Grok 4, 3, 3 Mini models for text generation
    - Grok 2 Vision and Image models for multimodal tasks
    - Advanced reasoning capabilities with transparent thinking
    - Search-augmented generation with web citations
    - Tool calling and JSON mode
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.x.ai/v1",
        http_client: Optional[httpx.AsyncClient] = None,
    ):
        """
        Initialize xAI provider.
        
        Args:
            api_key: xAI API key. If not provided, will look for XAI_API_KEY environment variable.
            base_url: Base URL for xAI API
            http_client: Optional HTTP client to use for requests
            
        Raises:
            ValueError: If no API key is provided or found in environment
        """
        if not api_key:
            api_key = os.getenv("XAI_API_KEY")
        
        if not api_key:
            raise ValueError(
                "xAI API key is required. Provide it as an argument or set the XAI_API_KEY environment variable."
            )

        self.api_key = api_key
        self.base_url = base_url
        self.http_client = http_client
        
        super().__init__(provider_name="xai")

    def language_model(self, model_id: Union[XAIChatModelId, str]) -> XAILanguageModel:
        """
        Create a xAI language model.
        
        Args:
            model_id: The model identifier (e.g., "grok-4", "grok-3-mini")
            
        Returns:
            XAILanguageModel instance
            
        Examples:
            >>> provider = XAIProvider()
            >>> model = provider.language_model("grok-4")
            >>> 
            >>> # Use advanced reasoning
            >>> reasoner = provider.language_model("grok-3-mini")
            >>> 
            >>> # Use vision model
            >>> vision = provider.language_model("grok-2-vision")
        """
        return XAILanguageModel(
            model_id=model_id,
            api_key=self.api_key,
            base_url=self.base_url,
            http_client=self.http_client,
        )

    def chat(self, model_id: Union[XAIChatModelId, str]) -> XAILanguageModel:
        """
        Create a xAI chat model (alias for language_model).
        
        Args:
            model_id: The model identifier
            
        Returns:
            XAILanguageModel instance
        """
        return self.language_model(model_id)

    # Convenience methods for popular models
    def grok_4(self) -> XAILanguageModel:
        """Create Grok-4 model instance."""
        return self.language_model(XAIChatModelId.GROK_4)
    
    def grok_4_latest(self) -> XAILanguageModel:
        """Create Grok-4 latest model instance."""
        return self.language_model(XAIChatModelId.GROK_4_LATEST)

    def grok_3(self) -> XAILanguageModel:
        """Create Grok-3 model instance."""
        return self.language_model(XAIChatModelId.GROK_3)

    def grok_3_fast(self) -> XAILanguageModel:
        """Create Grok-3 fast model instance."""
        return self.language_model(XAIChatModelId.GROK_3_FAST)

    def grok_3_mini(self) -> XAILanguageModel:
        """Create Grok-3 mini model instance with reasoning capabilities."""
        return self.language_model(XAIChatModelId.GROK_3_MINI)

    def grok_3_mini_fast(self) -> XAILanguageModel:
        """Create Grok-3 mini fast model instance with reasoning capabilities."""
        return self.language_model(XAIChatModelId.GROK_3_MINI_FAST)

    def grok_2_vision(self) -> XAILanguageModel:
        """Create Grok-2 vision model instance for multimodal tasks."""
        return self.language_model(XAIChatModelId.GROK_2_VISION)

    def grok_2_image(self) -> XAILanguageModel:
        """Create Grok-2 image model instance for image generation.""" 
        return self.language_model(XAIChatModelId.GROK_2_IMAGE)

    def __call__(self, model_id: Union[XAIChatModelId, str]) -> XAILanguageModel:
        """Allow direct calling of provider to create language model."""
        return self.language_model(model_id)