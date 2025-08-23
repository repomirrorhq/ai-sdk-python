"""FAL.ai transcription model implementation."""

from typing import Dict, Any, Optional, List
import httpx
from datetime import datetime

from ...core.transcribe import TranscribeResult, TranscribeSegment, Warning
from ...errors.base import AISDKError
from .types import (
    FalTranscriptionModelId,
    FalProviderSettings,
    FalTranscriptionSettings,
    FalTranscriptionResponse,
    FalValidationErrorResponse,
    FalHttpErrorResponse,
)


class FalTranscriptionModel:
    """FAL.ai transcription model for converting audio to text."""
    
    def __init__(
        self,
        model_id: FalTranscriptionModelId,
        settings: FalProviderSettings,
    ):
        """Initialize FAL transcription model.
        
        Args:
            model_id: Model identifier
            settings: Provider configuration settings
        """
        self.model_id = model_id
        self.settings = settings
        
        # Construct headers
        self.headers = {
            "Authorization": f"Key {settings.api_key}",
            **(settings.headers or {}),
        }
    
    async def transcribe(
        self,
        audio: bytes,
        options: Optional[FalTranscriptionSettings] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> TranscribeResult:
        """Transcribe audio using FAL.ai.
        
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
            
            # Step 1: Upload audio file (FAL typically requires file upload)
            audio_url = await self._upload_audio(audio, request_headers)
            
            # Build request body
            body = {
                "audio_url": audio_url,
            }
            
            # Add options
            if options:
                options_dict = options.model_dump(exclude_none=True)
                body.update(options_dict)
            
            # Submit transcription job
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.settings.base_url}/{self.model_id}",
                    json=body,
                    headers=request_headers,
                    timeout=120.0,  # Transcription can be slow
                )
                response.raise_for_status()
                
                data = response.json()
                fal_response = FalTranscriptionResponse.model_validate(data)
            
            # Convert response to standard format
            return self._convert_response(fal_response)
            
        except httpx.HTTPStatusError as e:
            await self._handle_error_response(e)
        except Exception as e:
            raise AISDKError(f"FAL transcription failed: {str(e)}") from e
    
    async def _upload_audio(self, audio: bytes, headers: Dict[str, str]) -> str:
        """Upload audio file to FAL for transcription.
        
        Args:
            audio: Audio data as bytes
            headers: Request headers
            
        Returns:
            URL of uploaded audio file
        """
        # Note: This is a simplified approach. Real FAL API may require
        # a specific upload endpoint or process. This should be adjusted
        # based on actual FAL API documentation.
        
        upload_headers = {
            **headers,
            "Content-Type": "application/octet-stream",
        }
        
        async with httpx.AsyncClient() as client:
            # Upload to a generic upload endpoint
            # This may need to be adjusted based on actual FAL API
            response = await client.post(
                f"{self.settings.base_url}/upload",
                content=audio,
                headers=upload_headers,
                timeout=60.0,
            )
            response.raise_for_status()
            
            data = response.json()
            return data["url"]  # Assuming response contains URL
    
    def _convert_response(self, response: FalTranscriptionResponse) -> TranscribeResult:
        """Convert FAL response to standard format.
        
        Args:
            response: FAL transcription response
            
        Returns:
            Standardized transcription result
        """
        # Convert segments if available
        segments: List[TranscribeSegment] = []
        if response.segments:
            for segment in response.segments:
                if "start" in segment and "end" in segment and "text" in segment:
                    segments.append(TranscribeSegment(
                        text=segment["text"],
                        start_second=segment["start"],
                        end_second=segment["end"],
                    ))
        
        return TranscribeResult(
            text=response.text,
            segments=segments,
            language=response.language,
            duration_seconds=None,  # FAL may not provide duration
            warnings=[],
            response=response.model_dump(),
        )
    
    async def _handle_error_response(self, error: httpx.HTTPStatusError) -> None:
        """Handle HTTP error response from FAL.
        
        Args:
            error: HTTP status error
            
        Raises:
            AISDKError: With detailed error message
        """
        try:
            error_data = error.response.json()
            
            # Try to parse as validation error first
            try:
                validation_error = FalValidationErrorResponse.model_validate(error_data)
                messages = []
                for detail in validation_error.detail:
                    location = ".".join(detail.loc)
                    messages.append(f"{location}: {detail.msg}")
                message = "\n".join(messages)
            except:
                # Try to parse as HTTP error
                try:
                    http_error = FalHttpErrorResponse.model_validate(error_data)
                    message = http_error.message
                except:
                    message = f"FAL API error: {error.response.status_code}"
                    
        except Exception:
            message = f"FAL API error: {error.response.status_code}"
        
        raise AISDKError(
            f"FAL transcription failed: {message}",
            status_code=error.response.status_code,
        ) from error