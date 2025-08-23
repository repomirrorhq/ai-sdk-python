"""OpenAI transcription models."""

import json
from typing import Dict, Optional, Any, List
import io

import httpx

from ..base import TranscriptionModel, TranscriptionResult, TranscriptionModelResponseMetadata
from ...errors.base import AISDKError
from ...utils.http import create_http_client


class OpenAITranscriptionError(AISDKError):
    """Error from OpenAI transcription API."""
    
    def __init__(self, message: str, status_code: Optional[int] = None, response: Optional[Dict] = None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class OpenAITranscriptionModel(TranscriptionModel):
    """OpenAI transcription model."""
    
    def __init__(self, provider, model_id: str, **kwargs):
        super().__init__(provider, model_id, **kwargs)
    
    async def do_transcribe(
        self,
        *,
        audio_data: bytes,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        temperature: Optional[float] = None,
        timestamp_granularities: Optional[List[str]] = None,
        provider_options: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> TranscriptionResult:
        """Transcribe audio using OpenAI's speech-to-text API."""
        
        # Create form data
        files = {
            "file": ("audio.mp3", io.BytesIO(audio_data), "audio/mpeg"),
            "model": (None, self.model_id),
        }
        
        # Add optional parameters
        if language:
            files["language"] = (None, language)
        if prompt:
            files["prompt"] = (None, prompt)
        if temperature is not None:
            files["temperature"] = (None, str(temperature))
        if timestamp_granularities:
            files["timestamp_granularities[]"] = (None, ",".join(timestamp_granularities))
        
        # Add provider-specific options
        if provider_options:
            openai_options = provider_options.get("openai", {})
            for key, value in openai_options.items():
                files[key] = (None, str(value))
        
        # Create HTTP client (without default JSON content-type for multipart)
        client_headers = {
            "Authorization": f"Bearer {self.provider.api_key}",
            **(headers or {})
        }
        
        client = httpx.AsyncClient(
            base_url=getattr(self.provider, 'base_url', 'https://api.openai.com/v1'),
            headers=client_headers,
            timeout=60.0
        )
        
        try:
            async with client:
                response = await client.post(
                    "/audio/transcriptions",
                    files=files
                )
                
                if response.status_code != 200:
                    error_data = {}
                    try:
                        error_data = response.json()
                    except:
                        pass
                    
                    error_message = error_data.get("error", {}).get("message", f"HTTP {response.status_code}")
                    raise OpenAITranscriptionError(
                        error_message,
                        status_code=response.status_code,
                        response=error_data
                    )
                
                result = response.json()
                
                return TranscriptionResult(
                    text=result.get("text", ""),
                    warnings=[],
                    response=TranscriptionModelResponseMetadata({
                        "model": self.model_id,
                        "language": language,
                        "duration": result.get("duration"),
                    }),
                    provider_metadata={
                        "openai": {
                            "segments": result.get("segments", []),
                            "language": result.get("language"),
                            "duration": result.get("duration"),
                        }
                    }
                )
                
        except httpx.RequestError as e:
            raise OpenAITranscriptionError(f"Request failed: {str(e)}")
        except json.JSONDecodeError:
            raise OpenAITranscriptionError("Invalid JSON response from OpenAI API")