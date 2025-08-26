"""LMNT AI provider implementation."""

import os
from typing import Optional, Dict, Any, Union

from ...providers.base import BaseProvider
from ...errors import AISDKError
from .speech_model import LMNTSpeechModel
from .types import LMNTSpeechModelId, LMNTProviderSettings


class LMNTProvider(BaseProvider):
    """
    LMNT AI provider for high-quality speech synthesis.
    
    LMNT provides advanced text-to-speech capabilities with natural-sounding voices
    and conversational speech styles. Supports multiple audio formats and
    real-time speech generation.
    
    Example:
        ```python
        from ai_sdk.providers.lmnt import LMNTProvider, create_lmnt
        
        # Using provider directly
        provider = LMNTProvider(api_key="your-lmnt-api-key")
        
        # Using factory function (recommended)
        lmnt = create_lmnt(api_key="your-lmnt-api-key")
        
        # Get speech model
        model = provider.speech("aurora")
        
        # Generate speech
        result = await model.generate(
            text="Welcome to LMNT's advanced speech synthesis!",
            voice="ava",
            provider_options={
                "conversational": True,
                "speed": 1.1,
                "format": "wav"
            }
        )
        
        # Save audio to file
        with open("speech.wav", "wb") as f:
            f.write(result.audio.data)
        ```
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ):
        """
        Initialize LMNT provider.
        
        Args:
            api_key: LMNT API key (defaults to LMNT_API_KEY environment variable)
            base_url: Base API URL (defaults to https://api.lmnt.com/v1)
            headers: Additional HTTP headers
            **kwargs: Additional provider options
            
        Raises:
            AISDKError: If no API key is provided or found in environment
        """
        # Load API key from environment if not provided
        self.api_key = api_key or os.getenv("LMNT_API_KEY")
        if not self.api_key:
            raise AISDKError(
                "LMNT API key is required. Provide it via the 'api_key' parameter "
                "or set the 'LMNT_API_KEY' environment variable."
            )
        
        self.base_url = base_url or "https://api.lmnt.com/v1"
        self.headers = headers or {}
        self.settings = LMNTProviderSettings(
            api_key=self.api_key,
            base_url=self.base_url,
            headers=self.headers,
        )
        
        super().__init__(**kwargs)

    def speech(
        self,
        model_id: Union[LMNTSpeechModelId, str],
        **kwargs: Any,
    ) -> LMNTSpeechModel:
        """
        Create an LMNT speech synthesis model.
        
        Args:
            model_id: LMNT speech model identifier
            **kwargs: Additional model options
            
        Returns:
            LMNTSpeechModel instance
            
        Example:
            ```python
            # Aurora model (advanced features)
            aurora_model = provider.speech("aurora")
            
            # Blizzard model (basic synthesis)
            blizzard_model = provider.speech("blizzard")
            ```
        """
        return LMNTSpeechModel(
            model_id=model_id,  # type: ignore
            api_key=self.api_key,
            base_url=self.base_url,
            headers=self.headers,
            **kwargs,
        )

    @property
    def provider_id(self) -> str:
        """Get provider identifier."""
        return "lmnt"
    
    @property
    def name(self) -> str:
        """Name of the provider."""
        return "lmnt"

    def __repr__(self) -> str:
        """Return string representation of provider."""
        return f"LMNTProvider(base_url='{self.base_url}')"


def create_lmnt(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    **kwargs: Any,
) -> LMNTProvider:
    """
    Create an LMNT provider instance.
    
    This is the recommended way to create an LMNT provider as it provides
    a clean interface and follows AI SDK conventions.
    
    Args:
        api_key: LMNT API key (defaults to LMNT_API_KEY environment variable)
        base_url: Base API URL (defaults to https://api.lmnt.com/v1)  
        headers: Additional HTTP headers
        **kwargs: Additional provider options
        
    Returns:
        LMNTProvider instance
        
    Example:
        ```python
        from ai_sdk.providers.lmnt import create_lmnt
        
        # Create provider with API key
        lmnt = create_lmnt(api_key="your-api-key")
        
        # Create provider with custom base URL
        lmnt = create_lmnt(
            api_key="your-api-key",
            base_url="https://custom.lmnt.api.endpoint"
        )
        
        # Create provider with additional headers
        lmnt = create_lmnt(
            api_key="your-api-key",
            headers={"x-custom-header": "value"}
        )
        ```
    """
    return LMNTProvider(
        api_key=api_key,
        base_url=base_url,
        headers=headers,
        **kwargs,
    )


# Default provider instance
LMNT = create_lmnt