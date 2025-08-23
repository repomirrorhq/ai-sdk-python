"""AssemblyAI transcription model implementation."""

import asyncio
from typing import Dict, Any, Optional, List, cast
import httpx
from datetime import datetime

from ...core.transcribe import TranscribeResult, TranscribeSegment, Warning
from ...errors.base import AISDKError
from ...utils.http import make_request
from ...utils.json import parse_json
from .types import (
    AssemblyAITranscriptionModelId,
    AssemblyAITranscriptionSettings,
    AssemblyAIProviderSettings,
    AssemblyAIUploadResponse,
    AssemblyAITranscriptionResponse,
    AssemblyAIError,
)


class AssemblyAITranscriptionModel:
    """AssemblyAI transcription model for converting audio to text."""
    
    def __init__(
        self,
        model_id: AssemblyAITranscriptionModelId,
        settings: AssemblyAIProviderSettings,
    ):
        """Initialize AssemblyAI transcription model.
        
        Args:
            model_id: Model identifier ('best' or 'nano')
            settings: Provider configuration settings
        """
        self.model_id = model_id
        self.settings = settings
        
        # Construct headers
        self.headers = {
            "authorization": settings.api_key or "",
            **(settings.headers or {}),
        }
    
    async def transcribe(
        self,
        audio: bytes,
        options: Optional[AssemblyAITranscriptionSettings] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> TranscribeResult:
        """Transcribe audio using AssemblyAI.
        
        Args:
            audio: Audio data as bytes
            options: Transcription options
            headers: Additional headers
            
        Returns:
            Transcription result with text and metadata
            
        Raises:
            AISDKError: If transcription fails
        """
        try:
            # Combine headers
            request_headers = {**self.headers}
            if headers:
                request_headers.update(headers)
            
            # Step 1: Upload audio file
            upload_response = await self._upload_audio(audio, request_headers)
            
            # Step 2: Submit transcription job
            transcription_response = await self._submit_transcription(
                upload_response.upload_url, options, request_headers
            )
            
            # Convert response to standard format
            return self._convert_response(transcription_response)
            
        except httpx.HTTPStatusError as e:
            await self._handle_error_response(e)
        except Exception as e:
            raise AISDKError(f"AssemblyAI transcription failed: {str(e)}") from e
    
    async def _upload_audio(
        self, audio: bytes, headers: Dict[str, str]
    ) -> AssemblyAIUploadResponse:
        """Upload audio file to AssemblyAI.
        
        Args:
            audio: Audio data as bytes
            headers: Request headers
            
        Returns:
            Upload response with URL
        """
        upload_headers = {
            **headers,
            "Content-Type": "application/octet-stream",
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.settings.base_url}/v2/upload",
                content=audio,
                headers=upload_headers,
                timeout=60.0,
            )
            response.raise_for_status()
            
            data = response.json()
            return AssemblyAIUploadResponse.model_validate(data)
    
    async def _submit_transcription(
        self,
        audio_url: str,
        options: Optional[AssemblyAITranscriptionSettings],
        headers: Dict[str, str],
    ) -> AssemblyAITranscriptionResponse:
        """Submit transcription job to AssemblyAI.
        
        Args:
            audio_url: URL of uploaded audio
            options: Transcription options
            headers: Request headers
            
        Returns:
            Transcription response
        """
        # Build request body
        body: Dict[str, Any] = {
            "audio_url": audio_url,
            "speech_model": self.model_id,
        }
        
        # Add transcription options
        if options:
            # Convert from Pydantic model to dict, excluding None values
            options_dict = options.model_dump(exclude_none=True, by_alias=True)
            body.update(options_dict)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.settings.base_url}/v2/transcript",
                json=body,
                headers=headers,
                timeout=60.0,
            )
            response.raise_for_status()
            
            data = response.json()
            return AssemblyAITranscriptionResponse.model_validate(data)
    
    def _convert_response(
        self, response: AssemblyAITranscriptionResponse
    ) -> TranscribeResult:
        """Convert AssemblyAI response to standard format.
        
        Args:
            response: AssemblyAI transcription response
            
        Returns:
            Standardized transcription result
        """
        # Convert word timestamps to segments
        segments: List[TranscribeSegment] = []
        if response.words:
            segments = [
                TranscribeSegment(
                    text=word.text,
                    start_second=word.start,
                    end_second=word.end,
                )
                for word in response.words
            ]
        
        # Calculate duration
        duration_seconds = response.audio_duration
        if not duration_seconds and response.words:
            # Use last word end time as fallback
            duration_seconds = response.words[-1].end
        
        return TranscribeResult(
            text=response.text or "",
            segments=segments,
            language=response.language_code,
            duration_seconds=duration_seconds,
            warnings=[],
            response=response.model_dump(),
        )
    
    async def _handle_error_response(self, error: httpx.HTTPStatusError) -> None:
        """Handle HTTP error response from AssemblyAI.
        
        Args:
            error: HTTP status error
            
        Raises:
            AISDKError: With detailed error message
        """
        try:
            error_data = error.response.json()
            assemblyai_error = AssemblyAIError.model_validate(error_data)
            message = assemblyai_error.error.message
        except Exception:
            message = f"AssemblyAI API error: {error.response.status_code}"
        
        raise AISDKError(
            f"AssemblyAI transcription failed: {message}",
            status_code=error.response.status_code,
        ) from error