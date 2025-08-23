"""
Groq Transcription Model Implementation

Implements transcription using Groq's Whisper models for speech-to-text.
"""

from __future__ import annotations

import asyncio
from typing import Dict, Optional, Any, Callable, BinaryIO, Union
from pathlib import Path

import httpx

from ...errors import APIError, InvalidArgumentError
from ..base import TranscriptionModel
from ..types import TranscriptionResult, ProviderMetadata
from .types import GroqTranscriptionModelId


class GroqTranscriptionModel(TranscriptionModel):
    """Groq transcription model using Whisper."""
    
    def __init__(
        self,
        model_id: GroqTranscriptionModelId,
        api_key: str,
        base_url: str = "https://api.groq.com/openai/v1",
        headers: Optional[Dict[str, str]] = None,
        fetch_implementation: Optional[Callable] = None,
    ):
        """Initialize Groq transcription model.
        
        Args:
            model_id: The Groq transcription model identifier (e.g., 'whisper-large-v3')
            api_key: Groq API key
            base_url: Base URL for Groq API
            headers: Additional headers for requests
            fetch_implementation: Custom fetch implementation
        """
        self.model_id = model_id
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.fetch_implementation = fetch_implementation
        
        # Set up HTTP client
        self._client = httpx.AsyncClient(
            headers=self.headers,
            timeout=httpx.Timeout(120.0)  # 2 minute timeout for audio processing
        )
        
    @property
    def provider_id(self) -> str:
        return "groq"
        
    async def transcribe(
        self,
        audio: Union[str, Path, BinaryIO, bytes],
        *,
        language: Optional[str] = None,
        prompt: Optional[str] = None,
        response_format: Optional[str] = None,
        temperature: Optional[float] = None,
        timestamp_granularities: Optional[list] = None,
        **kwargs: Any,
    ) -> TranscriptionResult:
        """Transcribe audio using Groq Whisper models.
        
        Args:
            audio: Audio file path, file object, or raw bytes
            language: Language code (e.g., 'en', 'es', 'fr')
            prompt: Optional text to guide the model's style  
            response_format: Response format ('json', 'text', 'srt', 'verbose_json', 'vtt')
            temperature: Sampling temperature (0.0 to 1.0)
            timestamp_granularities: Timestamp granularities (e.g., ['word', 'segment'])
            **kwargs: Additional provider-specific arguments
            
        Returns:
            TranscriptionResult with transcribed text and metadata
        """
        # Prepare the audio data
        audio_data, filename = await self._prepare_audio_data(audio)
        
        # Build the request data
        files = {
            'file': (filename, audio_data, 'audio/wav'),
            'model': (None, self.model_id),
        }
        
        # Add optional parameters
        if language:
            files['language'] = (None, language)
        if prompt:
            files['prompt'] = (None, prompt)
        if response_format:
            files['response_format'] = (None, response_format)
        if temperature is not None:
            files['temperature'] = (None, str(temperature))
        if timestamp_granularities:
            files['timestamp_granularities[]'] = [
                (None, granularity) for granularity in timestamp_granularities
            ]
            
        # Add any additional kwargs
        for key, value in kwargs.items():
            if value is not None:
                files[key] = (None, str(value))
        
        try:
            # Make the API call
            response = await self._client.post(
                f"{self.base_url}/audio/transcriptions",
                files=files,
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            
            # Parse the response
            result_data = response.json()
            
            # Extract transcription text
            if isinstance(result_data, dict):
                text = result_data.get('text', '')
                # Additional data might include segments, words, etc.
                additional_data = {
                    k: v for k, v in result_data.items() 
                    if k not in ['text']
                }
            else:
                # Plain text response
                text = str(result_data)
                additional_data = {}
            
            # Build metadata
            metadata = ProviderMetadata(
                provider_id="groq",
                model_id=self.model_id,
                extra=additional_data
            )
            
            return TranscriptionResult(
                text=text,
                metadata=metadata
            )
            
        except httpx.HTTPStatusError as e:
            error_data = {}
            try:
                error_data = e.response.json()
            except:
                pass
                
            raise APIError(
                f"Groq transcription API error: {e.response.status_code} - {error_data.get('error', {}).get('message', str(e))}",
                status_code=e.response.status_code,
                response_data=error_data
            )
            
        except Exception as e:
            raise APIError(f"Unexpected error calling Groq transcription API: {str(e)}")
            
    async def _prepare_audio_data(
        self, 
        audio: Union[str, Path, BinaryIO, bytes]
    ) -> tuple[bytes, str]:
        """Prepare audio data for upload.
        
        Args:
            audio: Audio input in various formats
            
        Returns:
            Tuple of (audio_bytes, filename)
        """
        if isinstance(audio, (str, Path)):
            # File path
            audio_path = Path(audio)
            if not audio_path.exists():
                raise InvalidArgumentError(f"Audio file not found: {audio}")
            
            with open(audio_path, 'rb') as f:
                audio_bytes = f.read()
            filename = audio_path.name
            
        elif isinstance(audio, bytes):
            # Raw bytes
            audio_bytes = audio
            filename = "audio.wav"  # Default filename
            
        elif hasattr(audio, 'read'):
            # File-like object
            if hasattr(audio, 'seek'):
                audio.seek(0)  # Reset to beginning
            audio_bytes = audio.read()
            filename = getattr(audio, 'name', 'audio.wav')
            
        else:
            raise InvalidArgumentError(
                f"Unsupported audio type: {type(audio)}. "
                "Supported types: file path (str/Path), bytes, or file-like object."
            )
            
        if not audio_bytes:
            raise InvalidArgumentError("Audio data is empty")
            
        return audio_bytes, filename
        
    async def __aenter__(self):
        """Async context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._client.aclose()