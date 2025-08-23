"""OpenAI speech generation models."""

import json
from typing import Dict, Optional, Any

import httpx

from ..base import SpeechModel, SpeechGenerationResult, SpeechModelResponseMetadata
from ...errors.base import AISDKError
from ...utils.http import create_http_client


class OpenAISpeechGenerationError(AISDKError):
    """Error from OpenAI speech generation API."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class OpenAISpeechModel(SpeechModel):
    """OpenAI speech generation model."""
    
    def __init__(self, provider, model_id: str, **kwargs):
        super().__init__(provider, model_id, **kwargs)
    
    async def do_generate(
        self,
        *,
        text: str,
        voice: Optional[str] = None,
        output_format: Optional[str] = None,
        instructions: Optional[str] = None,
        speed: Optional[float] = None,
        language: Optional[str] = None,
        provider_options: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> SpeechGenerationResult:
        """Generate speech using OpenAI's text-to-speech API."""
        
        # Build request body
        body = {
            "model": self.model_id,
            "input": text,
            "voice": voice or "alloy",  # Default voice
        }
        
        # Add optional parameters
        if output_format:
            body["response_format"] = output_format
        if speed is not None:
            body["speed"] = speed
        
        # Add provider-specific options
        if provider_options:
            openai_options = provider_options.get("openai", {})
            for key, value in openai_options.items():
                body[key] = value
        
        # Create HTTP client
        client = create_http_client(
            base_url=getattr(self.provider, 'base_url', 'https://api.openai.com/v1'),
            headers={
                "Authorization": f"Bearer {self.provider.api_key}",
                **(headers or {})
            }
        )
        
        try:
            async with client:
                response = await client.post(
                    "/audio/speech",
                    json=body
                )
                
                if response.status_code != 200:
                    error_data = {}
                    try:
                        error_data = response.json()
                    except:
                        pass
                    
                    error_message = error_data.get("error", {}).get("message", f"HTTP {response.status_code}")
                    raise OpenAISpeechGenerationError(
                        error_message,
                        status_code=response.status_code,
                        response=error_data
                    )
                
                # Get audio data as bytes
                audio_data = response.content
                
                return SpeechGenerationResult(
                    audio_data=audio_data,
                    warnings=[],
                    response=SpeechModelResponseMetadata({
                        "model": self.model_id,
                        "voice": voice or "alloy",
                        "format": output_format or "mp3",
                        "speed": speed or 1.0,
                    }),
                    provider_metadata={
                        "openai": {
                            "audio_length": len(audio_data),
                            "format": output_format or "mp3"
                        }
                    }
                )
                
        except httpx.RequestError as e:
            raise OpenAISpeechGenerationError(f"Request failed: {str(e)}")
        except json.JSONDecodeError:
            raise OpenAISpeechGenerationError("Invalid JSON response from OpenAI API")