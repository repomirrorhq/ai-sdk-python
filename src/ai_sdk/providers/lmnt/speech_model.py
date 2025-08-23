"""LMNT speech synthesis model implementation."""

import json
from typing import Any, Dict, List, Optional, Union, AsyncIterator, Literal
from datetime import datetime

import httpx
from pydantic import ValidationError

from ...core.generate_speech import SpeechGenerationResult
from ...errors import AISDKError, APICallError
from ...schemas import AudioData
from ...utils.http import create_http_client
from ...utils.json import parse_json_response, handle_json_parse_error
from .types import (
    LMNTSpeechModelId,
    LMNTSpeechOptions,
    LMNTAPIRequest,
    LMNTError,
    LMNTWarning,
    LMNTLanguage,
)


class LMNTSpeechModel:
    """
    LMNT speech synthesis model.
    
    Provides high-quality text-to-speech generation using LMNT's advanced speech synthesis models.
    Supports voice customization, multiple output formats, and conversational speech styles.
    
    Example:
        ```python
        from ai_sdk.providers.lmnt import LMNTProvider
        
        provider = LMNTProvider(api_key="your-api-key")
        model = provider.speech("aurora")
        
        # Basic speech generation
        result = await model.generate(
            text="Hello, world!",
            voice="ava"
        )
        
        # With conversational style (aurora model only)
        result = await model.generate(
            text="How are you doing today?",
            voice="ava",
            provider_options={
                "conversational": True,
                "speed": 1.2,
                "temperature": 0.8
            }
        )
        
        # Custom audio format and sample rate
        result = await model.generate(
            text="Professional announcement",
            voice="narrator",
            provider_options={
                "format": "wav",
                "sample_rate": 16000,
                "top_p": 0.5  # More consistent output
            }
        )
        ```
    """
    
    def __init__(
        self,
        model_id: LMNTSpeechModelId,
        api_key: str,
        base_url: str = "https://api.lmnt.com/v1",
        headers: Optional[Dict[str, str]] = None,
        client: Optional[httpx.AsyncClient] = None,
    ):
        """
        Initialize LMNT speech model.
        
        Args:
            model_id: LMNT model identifier ('aurora' or 'blizzard')
            api_key: LMNT API key
            base_url: Base API URL
            headers: Additional HTTP headers
            client: Optional HTTP client instance
        """
        self.model_id = model_id
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.custom_headers = headers or {}
        self._client = client

    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            # Create default headers
            default_headers = {
                "x-api-key": self.api_key,
                "content-type": "application/json",
                "user-agent": "ai-sdk-python/lmnt",
                **self.custom_headers,
            }
            
            self._client = create_http_client(
                headers=default_headers,
                timeout=httpx.Timeout(60.0)
            )
        return self._client

    async def generate(
        self,
        text: str,
        voice: Optional[str] = None,
        output_format: Optional[str] = None,
        speed: Optional[float] = None,
        language: Optional[Union[str, LMNTLanguage]] = None,
        provider_options: Optional[Dict[str, Any]] = None,
        request_options: Optional[Dict[str, Any]] = None,
    ) -> SpeechGenerationResult:
        """
        Generate speech from text using LMNT API.
        
        Args:
            text: Text to synthesize (max 5000 characters)
            voice: Voice ID (defaults to 'ava')
            output_format: Output audio format ('mp3', 'wav', 'aac', 'raw', 'mulaw')
            speed: Speech speed multiplier (0.25 to 2.0)
            language: Language code or 'auto' for detection
            provider_options: LMNT-specific options
            request_options: HTTP request options
            
        Returns:
            SpeechGenerationResult containing audio data and metadata
            
        Raises:
            APICallError: If the API request fails
            AISDKError: If response processing fails
        """
        if len(text) > 5000:
            raise AISDKError("Text must be 5000 characters or less")
        
        # Parse provider options
        options = LMNTSpeechOptions(**(provider_options or {}))
        
        # Build request payload
        request_payload = LMNTAPIRequest(
            text=text,
            voice=voice or "ava",
            model=self.model_id,
            format=output_format or options.format,
            sample_rate=options.sample_rate,
            speed=speed or options.speed,
            language=language,
            seed=options.seed,
            conversational=options.conversational if self.model_id == "aurora" else None,
            length=options.length if self.model_id == "aurora" else None,
            top_p=options.top_p,
            temperature=options.temperature,
        )
        
        # Remove None values
        payload_dict = request_payload.dict(exclude_none=True)
        
        try:
            # Make API request
            response = await self.client.post(
                f"{self.base_url}/ai/speech/bytes",
                json=payload_dict,
                **(request_options or {})
            )
            
            # Check for errors
            if response.status_code != 200:
                await self._handle_error_response(response)
            
            # Parse response headers for warnings
            warnings: List[str] = []
            warning_header = response.headers.get("x-lmnt-warnings")
            if warning_header:
                try:
                    warning_data = json.loads(warning_header)
                    if isinstance(warning_data, list):
                        warnings = [w.get("message", str(w)) if isinstance(w, dict) else str(w) for w in warning_data]
                except json.JSONDecodeError:
                    warnings = [warning_header]
            
            # Get audio content
            audio_bytes = response.content
            if not audio_bytes:
                raise AISDKError("No audio data received from LMNT API")
            
            # Create audio data object
            audio_data = AudioData(
                data=audio_bytes,
                format=payload_dict.get("format", "mp3"),
                sample_rate=payload_dict.get("sample_rate", 24000),
            )
            
            return SpeechGenerationResult(
                audio=audio_data,
                warnings=warnings,
                request={
                    "body": json.dumps(payload_dict, indent=2)
                },
                response={
                    "timestamp": datetime.now(),
                    "model_id": self.model_id,
                    "headers": dict(response.headers),
                    "body": f"<binary audio data: {len(audio_bytes)} bytes>",
                },
                usage=None,  # LMNT doesn't provide token usage
            )
            
        except httpx.RequestError as e:
            raise APICallError(
                message=f"LMNT API request failed: {str(e)}",
                cause=e,
                status_code=None,
            )
        except ValidationError as e:
            raise AISDKError(f"Invalid LMNT request parameters: {str(e)}")
        except Exception as e:
            if isinstance(e, (APICallError, AISDKError)):
                raise
            raise AISDKError(f"Unexpected error during LMNT speech generation: {str(e)}")

    async def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error response from LMNT API."""
        try:
            error_data = response.json()
            if isinstance(error_data, dict):
                error_obj = LMNTError(**error_data)
                message = error_obj.error
                if error_obj.code:
                    message = f"[{error_obj.code}] {message}"
            else:
                message = f"LMNT API error: {error_data}"
        except (json.JSONDecodeError, ValidationError):
            message = f"LMNT API error (status {response.status_code}): {response.text}"
        
        raise APICallError(
            message=message,
            status_code=response.status_code,
            response_headers=dict(response.headers),
            response_body=response.text,
        )

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None