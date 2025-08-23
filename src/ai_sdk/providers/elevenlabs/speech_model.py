"""ElevenLabs speech synthesis model implementation."""

import json
from typing import Any, Dict, List, Optional, Union, AsyncIterator, Literal
from datetime import datetime

import httpx
from pydantic import ValidationError

from ...core.generate_speech import SpeechGenerationResult
from ...errors import AISDKError, APICallError
from ...schemas import AudioData
from .types import (
    ElevenLabsSpeechModelId,
    ElevenLabsSpeechVoiceId,
    ElevenLabsSpeechAPIRequest,
    ElevenLabsSpeechOptions,
    ElevenLabsVoiceSettings,
    ElevenLabsError,
)


class ElevenLabsSpeechModel:
    """
    ElevenLabs speech synthesis model.
    
    Provides text-to-speech generation using ElevenLabs' advanced speech synthesis models.
    Supports voice customization, multiple output formats, and context-aware generation.
    
    Example:
        ```python
        from ai_sdk.providers.elevenlabs import ElevenLabsProvider
        
        provider = ElevenLabsProvider(api_key="your-api-key")
        model = provider.speech("eleven_v3")
        
        # Basic speech generation
        result = await model.generate(
            text="Hello, world!",
            voice="21m00Tcm4TlvDq8ikWAM"  # Rachel voice
        )
        
        # With custom voice settings
        result = await model.generate(
            text="Hello, world!",
            voice="21m00Tcm4TlvDq8ikWAM",
            provider_options={
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5,
                    "style": 0.3
                }
            }
        )
        ```
    """
    
    def __init__(
        self,
        model_id: ElevenLabsSpeechModelId,
        provider: "ElevenLabsProvider",
        **kwargs: Any,
    ):
        """
        Initialize ElevenLabs speech model.
        
        Args:
            model_id: The ElevenLabs speech model ID
            provider: The ElevenLabs provider instance
            **kwargs: Additional configuration options
        """
        self.model_id = model_id
        self.provider = provider
        self.config = kwargs
    
    async def generate(
        self,
        text: str,
        voice: ElevenLabsSpeechVoiceId = "21m00Tcm4TlvDq8ikWAM",  # Rachel voice (default)
        output_format: Optional[str] = "mp3_44100_128",
        language: Optional[str] = None,
        speed: Optional[float] = None,
        provider_options: Optional[Union[Dict[str, Any], ElevenLabsSpeechOptions]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> SpeechGenerationResult:
        """
        Generate speech from text using ElevenLabs.
        
        Args:
            text: Text to synthesize into speech
            voice: Voice ID to use (default: Rachel voice)
            output_format: Audio output format (default: mp3_44100_128)
            language: Language code for the text
            speed: Speech speed multiplier
            provider_options: ElevenLabs-specific options
            headers: Additional HTTP headers
            **kwargs: Additional options
            
        Returns:
            SpeechGenerationResult with audio data and metadata
            
        Raises:
            APICallError: If the API request fails
            AISDKError: If there's a validation or processing error
        """
        try:
            # Parse provider options
            if provider_options:
                if isinstance(provider_options, dict):
                    try:
                        options = ElevenLabsSpeechOptions(**provider_options)
                    except ValidationError as e:
                        raise AISDKError(f"Invalid provider options: {e}")
                else:
                    options = provider_options
            else:
                options = ElevenLabsSpeechOptions()
            
            # Build request body
            request_body = ElevenLabsSpeechAPIRequest(
                text=text,
                model_id=self.model_id,
                language_code=language or options.language_code,
            )
            
            # Configure voice settings
            voice_settings = {}
            if speed is not None:
                voice_settings["speed"] = speed
                
            # Add provider-specific voice settings
            if options.voice_settings:
                if options.voice_settings.stability is not None:
                    voice_settings["stability"] = options.voice_settings.stability
                if options.voice_settings.similarity_boost is not None:
                    voice_settings["similarity_boost"] = options.voice_settings.similarity_boost
                if options.voice_settings.style is not None:
                    voice_settings["style"] = options.voice_settings.style
                if options.voice_settings.use_speaker_boost is not None:
                    voice_settings["use_speaker_boost"] = options.voice_settings.use_speaker_boost
            
            if voice_settings:
                request_body.voice_settings = ElevenLabsVoiceSettings(**voice_settings)
            
            # Add other provider options
            if options.pronunciation_dictionary_locators:
                request_body.pronunciation_dictionary_locators = options.pronunciation_dictionary_locators
            if options.seed is not None:
                request_body.seed = options.seed
            if options.previous_text:
                request_body.previous_text = options.previous_text
            if options.next_text:
                request_body.next_text = options.next_text
            if options.previous_request_ids:
                request_body.previous_request_ids = options.previous_request_ids
            if options.next_request_ids:
                request_body.next_request_ids = options.next_request_ids
            if options.apply_text_normalization:
                request_body.apply_text_normalization = options.apply_text_normalization
            if options.apply_language_text_normalization is not None:
                request_body.apply_language_text_normalization = options.apply_language_text_normalization
            
            # Build query parameters
            query_params = {}
            
            # Map output format
            if output_format:
                format_map = {
                    "mp3": "mp3_44100_128",
                    "mp3_32": "mp3_44100_32",
                    "mp3_64": "mp3_44100_64", 
                    "mp3_96": "mp3_44100_96",
                    "mp3_128": "mp3_44100_128",
                    "mp3_192": "mp3_44100_192",
                    "pcm": "pcm_44100",
                    "pcm_16000": "pcm_16000",
                    "pcm_22050": "pcm_22050",
                    "pcm_24000": "pcm_24000",
                    "pcm_44100": "pcm_44100",
                    "ulaw": "ulaw_8000",
                }
                mapped_format = format_map.get(output_format, output_format)
                query_params["output_format"] = mapped_format
            
            if options.enable_logging is not None:
                query_params["enable_logging"] = str(options.enable_logging).lower()
            
            # Build URL
            url = self.provider._get_base_url(f"/v1/text-to-speech/{voice}")
            if query_params:
                query_string = "&".join([f"{k}={v}" for k, v in query_params.items()])
                url = f"{url}?{query_string}"
            
            # Prepare headers
            request_headers = self.provider._get_headers()
            if headers:
                request_headers.update(headers)
            
            # Make API request
            async with self.provider.http_client as client:
                response = await client.post(
                    url,
                    json=request_body.model_dump(exclude_none=True),
                    headers=request_headers,
                )
                
                if response.status_code != 200:
                    await self._handle_error_response(response)
                
                # Get audio data
                audio_data = response.content
                response_headers = dict(response.headers)
                
                return SpeechGenerationResult(
                    audio=AudioData(
                        data=audio_data,
                        format=output_format or "mp3_44100_128",
                        sample_rate=self._extract_sample_rate(output_format),
                    ),
                    model_id=self.model_id,
                    provider="elevenlabs",
                    timestamp=datetime.now(),
                    usage=None,  # ElevenLabs doesn't provide usage info in response
                    response_headers=response_headers,
                    request_body=request_body.model_dump(exclude_none=True),
                )
                
        except httpx.RequestError as e:
            raise APICallError(
                f"ElevenLabs API request failed: {str(e)}",
                provider="elevenlabs",
                model_id=self.model_id,
            )
        except ValidationError as e:
            raise AISDKError(f"Request validation failed: {str(e)}")
        except Exception as e:
            if isinstance(e, (APICallError, AISDKError)):
                raise
            raise AISDKError(f"Unexpected error in ElevenLabs speech generation: {str(e)}")
    
    def _extract_sample_rate(self, output_format: Optional[str]) -> Optional[int]:
        """Extract sample rate from output format."""
        if not output_format:
            return 44100  # Default for mp3_44100_128
        
        # Extract sample rate from format name
        if "44100" in output_format:
            return 44100
        elif "22050" in output_format:
            return 22050
        elif "24000" in output_format:
            return 24000
        elif "16000" in output_format:
            return 16000
        elif "8000" in output_format:
            return 8000
        
        return None
    
    async def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses from ElevenLabs API."""
        try:
            error_data = response.json()
            if isinstance(error_data, dict) and "error" in error_data:
                error_info = ElevenLabsError(**error_data)
                error_message = error_info.error.message
                error_code = error_info.error.code
            else:
                error_message = f"HTTP {response.status_code}: {response.text}"
                error_code = response.status_code
        except (json.JSONDecodeError, ValidationError, KeyError):
            error_message = f"HTTP {response.status_code}: {response.text}"
            error_code = response.status_code
        
        raise APICallError(
            message=f"ElevenLabs API error: {error_message}",
            status_code=response.status_code,
            provider="elevenlabs",
            model_id=self.model_id,
            response_body=response.text,
        )