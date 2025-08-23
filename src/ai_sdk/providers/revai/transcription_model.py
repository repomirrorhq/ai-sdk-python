"""RevAI transcription model implementation."""

import asyncio
import json
from typing import Dict, Any, Optional, List
import httpx
from datetime import datetime

from ...core.transcribe import TranscribeResult, TranscribeSegment, Warning
from ...errors.base import AISDKError
from .types import (
    RevAITranscriptionModelId,
    RevAITranscriptionSettings,
    RevAIProviderSettings,
    RevAIJobResponse,
    RevAITranscriptionResponse,
    RevAIError,
)


class RevAITranscriptionModel:
    """RevAI transcription model for converting audio to text."""
    
    def __init__(
        self,
        model_id: RevAITranscriptionModelId,
        settings: RevAIProviderSettings,
    ):
        """Initialize RevAI transcription model.
        
        Args:
            model_id: Model identifier ('machine', 'low_cost', or 'fusion')
            settings: Provider configuration settings
        """
        self.model_id = model_id
        self.settings = settings
        
        # Construct headers
        api_key = settings.api_key or ""
        if not api_key.startswith("Bearer "):
            api_key = f"Bearer {api_key}"
            
        self.headers = {
            "authorization": api_key,
            **(settings.headers or {}),
        }
    
    async def transcribe(
        self,
        audio: bytes,
        media_type: str = "audio/wav",
        options: Optional[RevAITranscriptionSettings] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> TranscribeResult:
        """Transcribe audio using RevAI.
        
        Args:
            audio: Audio data as bytes
            media_type: MIME type of the audio
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
            
            # Step 1: Submit transcription job
            job_response = await self._submit_transcription_job(
                audio, media_type, options, request_headers
            )
            
            if not job_response.id:
                raise AISDKError("RevAI job submission failed: No job ID returned")
            
            # Step 2: Poll for completion
            final_job_response = await self._poll_for_completion(
                job_response.id, request_headers
            )
            
            # Step 3: Retrieve transcript
            transcription_response = await self._get_transcript(
                job_response.id, request_headers
            )
            
            # Convert response to standard format
            return self._convert_response(
                transcription_response, final_job_response
            )
            
        except httpx.HTTPStatusError as e:
            await self._handle_error_response(e)
        except Exception as e:
            raise AISDKError(f"RevAI transcription failed: {str(e)}") from e
    
    async def _submit_transcription_job(
        self,
        audio: bytes,
        media_type: str,
        options: Optional[RevAITranscriptionSettings],
        headers: Dict[str, str],
    ) -> RevAIJobResponse:
        """Submit transcription job to RevAI.
        
        Args:
            audio: Audio data as bytes
            media_type: MIME type of the audio
            options: Transcription options
            headers: Request headers
            
        Returns:
            Job response with ID
        """
        # Build config
        config: Dict[str, Any] = {"transcriber": self.model_id}
        
        if options:
            # Convert options to dict, excluding None values
            options_dict = options.model_dump(exclude_none=True, by_alias=True)
            config.update(options_dict)
        
        # Create multipart form data
        files = {
            "media": ("audio", audio, media_type),
            "config": (None, json.dumps(config), "application/json"),
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.settings.base_url}/speechtotext/v1/jobs",
                files=files,
                headers=headers,
                timeout=60.0,
            )
            response.raise_for_status()
            
            data = response.json()
            return RevAIJobResponse.model_validate(data)
    
    async def _poll_for_completion(
        self,
        job_id: str,
        headers: Dict[str, str],
        timeout_seconds: int = 300,  # 5 minutes
        poll_interval: int = 2,
    ) -> RevAIJobResponse:
        """Poll RevAI job until completion.
        
        Args:
            job_id: Job identifier
            headers: Request headers
            timeout_seconds: Maximum wait time
            poll_interval: Polling interval in seconds
            
        Returns:
            Final job response
            
        Raises:
            AISDKError: If job fails or times out
        """
        start_time = asyncio.get_event_loop().time()
        
        while True:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.settings.base_url}/speechtotext/v1/jobs/{job_id}",
                    headers=headers,
                    timeout=30.0,
                )
                response.raise_for_status()
                
                data = response.json()
                job_response = RevAIJobResponse.model_validate(data)
            
            if job_response.status == "transcribed":
                return job_response
            elif job_response.status == "failed":
                raise AISDKError(f"RevAI transcription job {job_id} failed")
            
            # Check timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout_seconds:
                raise AISDKError(f"RevAI transcription job {job_id} timed out after {timeout_seconds} seconds")
            
            # Wait before next poll
            await asyncio.sleep(poll_interval)
    
    async def _get_transcript(
        self,
        job_id: str,
        headers: Dict[str, str],
    ) -> RevAITranscriptionResponse:
        """Get transcript from completed job.
        
        Args:
            job_id: Job identifier
            headers: Request headers
            
        Returns:
            Transcription response
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.settings.base_url}/speechtotext/v1/jobs/{job_id}/transcript",
                headers=headers,
                timeout=30.0,
            )
            response.raise_for_status()
            
            data = response.json()
            return RevAITranscriptionResponse.model_validate(data)
    
    def _convert_response(
        self,
        transcription_response: RevAITranscriptionResponse,
        job_response: RevAIJobResponse,
    ) -> TranscribeResult:
        """Convert RevAI response to standard format.
        
        Args:
            transcription_response: RevAI transcription response
            job_response: Final job response
            
        Returns:
            Standardized transcription result
        """
        # Extract full text and segments
        full_text_parts = []
        segments: List[TranscribeSegment] = []
        duration_seconds = 0.0
        
        if transcription_response.monologues:
            for monologue in transcription_response.monologues:
                if not monologue.elements:
                    continue
                
                # Process elements to build segments
                current_segment_text = ""
                segment_start_time = 0.0
                has_started_segment = False
                
                for element in monologue.elements:
                    if not element.value:
                        continue
                        
                    # Add element value to text
                    current_segment_text += element.value
                    full_text_parts.append(element.value)
                    
                    # Handle timing for text elements
                    if element.type == "text":
                        # Update overall duration
                        if element.end_ts is not None and element.end_ts > duration_seconds:
                            duration_seconds = element.end_ts
                        
                        # Track segment start time
                        if not has_started_segment and element.ts is not None:
                            segment_start_time = element.ts
                            has_started_segment = True
                        
                        # Complete segment if we have an end timestamp
                        if (element.end_ts is not None and 
                            has_started_segment and 
                            current_segment_text.strip()):
                            
                            segments.append(TranscribeSegment(
                                text=current_segment_text.strip(),
                                start_second=segment_start_time,
                                end_second=element.end_ts,
                            ))
                            
                            # Reset for next segment
                            current_segment_text = ""
                            has_started_segment = False
                
                # Handle any remaining segment
                if has_started_segment and current_segment_text.strip():
                    end_time = duration_seconds if duration_seconds > segment_start_time else segment_start_time + 1.0
                    segments.append(TranscribeSegment(
                        text=current_segment_text.strip(),
                        start_second=segment_start_time,
                        end_second=end_time,
                    ))
        
        return TranscribeResult(
            text=" ".join(full_text_parts).strip(),
            segments=segments,
            language=job_response.language,
            duration_seconds=duration_seconds,
            warnings=[],
            response={
                "transcription": transcription_response.model_dump(),
                "job": job_response.model_dump(),
            },
        )
    
    async def _handle_error_response(self, error: httpx.HTTPStatusError) -> None:
        """Handle HTTP error response from RevAI.
        
        Args:
            error: HTTP status error
            
        Raises:
            AISDKError: With detailed error message
        """
        try:
            error_data = error.response.json()
            revai_error = RevAIError.model_validate(error_data)
            message = revai_error.error.message
        except Exception:
            message = f"RevAI API error: {error.response.status_code}"
        
        raise AISDKError(
            f"RevAI transcription failed: {message}",
            status_code=error.response.status_code,
        ) from error