"""ElevenLabs transcription model implementation."""

import json
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

import httpx
from pydantic import ValidationError

from ...core.transcribe import TranscriptionResult, TranscriptionSegment
from ...errors import AISDKError, APICallError
from ...schemas import AudioData
from .types import (
    ElevenLabsTranscriptionModelId,
    ElevenLabsTranscriptionOptions,
    ElevenLabsTranscriptionResponse,
    ElevenLabsError,
)


class ElevenLabsTranscriptionModel:
    """
    ElevenLabs transcription model.
    
    Provides speech-to-text transcription using ElevenLabs' transcription models
    with support for speaker diarization, timestamps, and multilingual recognition.
    
    Example:
        ```python
        from ai_sdk.providers.elevenlabs import ElevenLabsProvider
        
        provider = ElevenLabsProvider(api_key="your-api-key")
        model = provider.transcription("scribe_v1")
        
        # Basic transcription
        with open("audio.mp3", "rb") as f:
            audio_data = f.read()
        
        result = await model.transcribe(
            audio=audio_data,
            media_type="audio/mp3"
        )
        
        # With speaker diarization and custom options
        result = await model.transcribe(
            audio=audio_data,
            media_type="audio/mp3",
            provider_options={
                "diarize": True,
                "num_speakers": 2,
                "timestamps_granularity": "word",
                "tag_audio_events": True
            }
        )
        ```
    """
    
    def __init__(
        self,
        model_id: ElevenLabsTranscriptionModelId,
        provider: "ElevenLabsProvider",
        **kwargs: Any,
    ):
        """
        Initialize ElevenLabs transcription model.
        
        Args:
            model_id: The ElevenLabs transcription model ID
            provider: The ElevenLabs provider instance
            **kwargs: Additional configuration options
        """
        self.model_id = model_id
        self.provider = provider
        self.config = kwargs
    
    async def transcribe(
        self,
        audio: Union[bytes, AudioData],
        media_type: Optional[str] = None,
        language: Optional[str] = None,
        provider_options: Optional[Union[Dict[str, Any], ElevenLabsTranscriptionOptions]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> TranscriptionResult:
        """
        Transcribe audio to text using ElevenLabs.
        
        Args:
            audio: Audio data as bytes or AudioData object
            media_type: MIME type of the audio (e.g., 'audio/mp3', 'audio/wav')
            language: Language code hint for transcription
            provider_options: ElevenLabs-specific options
            headers: Additional HTTP headers
            **kwargs: Additional options
            
        Returns:
            TranscriptionResult with transcribed text and metadata
            
        Raises:
            APICallError: If the API request fails
            AISDKError: If there's a validation or processing error
        """
        try:
            # Parse provider options
            if provider_options:
                if isinstance(provider_options, dict):
                    try:
                        options = ElevenLabsTranscriptionOptions(**provider_options)
                    except ValidationError as e:
                        raise AISDKError(f"Invalid provider options: {e}")
                else:
                    options = provider_options
            else:
                options = ElevenLabsTranscriptionOptions()
            
            # Extract audio data
            if isinstance(audio, AudioData):
                audio_bytes = audio.data
                if not media_type and audio.format:
                    # Map format to media type
                    format_map = {
                        "mp3": "audio/mp3",
                        "wav": "audio/wav",
                        "m4a": "audio/mp4",
                        "flac": "audio/flac",
                        "ogg": "audio/ogg",
                        "webm": "audio/webm",
                    }
                    media_type = format_map.get(audio.format.lower(), "audio/mpeg")
            else:
                audio_bytes = audio
            
            if not media_type:
                media_type = "audio/mpeg"  # Default fallback
            
            # Create form data
            files = {"file": ("audio", audio_bytes, media_type)}
            data = {
                "model_id": self.model_id,
                "diarize": str(options.diarize).lower() if options.diarize is not None else "false",
            }
            
            # Add language code
            language_code = language or options.language_code
            if language_code:
                data["language_code"] = language_code
            
            # Add other transcription options
            if options.tag_audio_events is not None:
                data["tag_audio_events"] = str(options.tag_audio_events).lower()
            
            if options.num_speakers is not None:
                data["num_speakers"] = str(options.num_speakers)
            
            if options.timestamps_granularity:
                data["timestamps_granularity"] = options.timestamps_granularity
            
            if options.file_format:
                data["file_format"] = options.file_format
            
            # Build URL
            url = self.provider._get_base_url("/v1/speech-to-text")
            
            # Prepare headers
            request_headers = self.provider._get_headers()
            # Remove Content-Type - let httpx set it for multipart
            request_headers.pop("Content-Type", None)
            
            if headers:
                request_headers.update(headers)
            
            # Make API request
            async with self.provider.http_client as client:
                response = await client.post(
                    url,
                    files=files,
                    data=data,
                    headers=request_headers,
                )
                
                if response.status_code != 200:
                    await self._handle_error_response(response)
                
                # Parse response
                response_data = response.json()
                transcription_response = ElevenLabsTranscriptionResponse(**response_data)
                
                # Convert to standard format
                segments = []
                if transcription_response.words:
                    for word in transcription_response.words:
                        if word.type == "word":  # Only include actual words, not spacing/events
                            segment = TranscriptionSegment(
                                text=word.text,
                                start_time=word.start or 0.0,
                                end_time=word.end or 0.0,
                                speaker_id=word.speaker_id,
                            )
                            segments.append(segment)
                
                # Calculate duration
                duration = None
                if transcription_response.words:
                    last_word = max(
                        (w for w in transcription_response.words if w.end is not None),
                        key=lambda w: w.end or 0,
                        default=None
                    )
                    if last_word and last_word.end:
                        duration = last_word.end
                
                return TranscriptionResult(
                    text=transcription_response.text,
                    segments=segments,
                    language=transcription_response.language_code,
                    duration_seconds=duration,
                    model_id=self.model_id,
                    provider="elevenlabs",
                    timestamp=datetime.now(),
                    usage=None,  # ElevenLabs doesn't provide usage info
                    response_headers=dict(response.headers),
                    metadata={
                        "language_probability": transcription_response.language_probability,
                        "detected_language": transcription_response.language_code,
                    },
                )
                
        except httpx.RequestError as e:
            raise APICallError(
                f"ElevenLabs API request failed: {str(e)}",
                provider="elevenlabs",
                model_id=self.model_id,
            )
        except ValidationError as e:
            raise AISDKError(f"Response validation failed: {str(e)}")
        except Exception as e:
            if isinstance(e, (APICallError, AISDKError)):
                raise
            raise AISDKError(f"Unexpected error in ElevenLabs transcription: {str(e)}")
    
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