"""FAL.ai speech model implementation."""

from typing import Dict, Any, Optional, List
import httpx
from datetime import datetime

from ...core.generate_speech import GenerateSpeechResult, GenerateSpeechUsage
from ...errors.base import AISDKError
from .types import (
    FalSpeechModelId,
    FalProviderSettings, 
    FalSpeechSettings,
    FalSpeechResponse,
    FalValidationErrorResponse,
    FalHttpErrorResponse,
)


class FalSpeechModel:
    """FAL.ai speech model for text-to-speech synthesis."""
    
    def __init__(
        self,
        model_id: FalSpeechModelId,
        settings: FalProviderSettings,
    ):
        """Initialize FAL speech model.
        
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
    
    async def generate(
        self,
        text: str,
        voice: Optional[str] = None,
        output_format: str = "url",
        speed: Optional[float] = None,
        language: Optional[str] = None,
        options: Optional[FalSpeechSettings] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> GenerateSpeechResult:
        """Generate speech using FAL.ai.
        
        Args:
            text: Text to convert to speech
            voice: Voice identifier
            output_format: Output format ("url" or "hex")
            speed: Speech speed
            language: Language (will be ignored with warning)
            options: Additional speech options
            headers: Additional headers
            
        Returns:
            Speech generation result
            
        Raises:
            AISDKError: If speech generation fails
        """
        try:
            # Combine headers
            request_headers = {**self.headers}
            if headers:
                request_headers.update(headers)
            
            # Build request body
            body = {
                "text": text,
                "output_format": output_format if output_format in ["url", "hex"] else "url",
            }
            
            # Add basic parameters
            if voice:
                body["voice"] = voice
            if speed is not None:
                body["speed"] = speed
            
            # Add additional options
            if options:
                options_dict = options.model_dump(exclude_none=True, exclude={"output_format"})
                body.update(options_dict)
            
            # Generate speech
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.settings.base_url}/{self.model_id}",
                    json=body,
                    headers=request_headers,
                    timeout=60.0,
                )
                response.raise_for_status()
                
                data = response.json()
                fal_response = FalSpeechResponse.model_validate(data)
            
            # Download audio from URL
            audio_data = await self._download_audio(fal_response.audio["url"])
            
            # Create warnings for unsupported features
            warnings = []
            if language:
                warnings.append(
                    f"Language parameter '{language}' is not directly supported by FAL. "
                    f"Consider using options.language_boost instead."
                )
            if output_format not in ["url", "hex"]:
                warnings.append(
                    f"Output format '{output_format}' is not supported. Using 'url' instead."
                )
            
            return GenerateSpeechResult(
                audio=audio_data,
                usage=GenerateSpeechUsage(
                    characters=len(text),
                    total_characters=len(text),
                ),
                warnings=warnings,
                response=fal_response.model_dump(),
            )
            
        except httpx.HTTPStatusError as e:
            await self._handle_error_response(e)
        except Exception as e:
            raise AISDKError(f"FAL speech generation failed: {str(e)}") from e
    
    async def _download_audio(self, audio_url: str) -> bytes:
        """Download audio from FAL URL.
        
        Args:
            audio_url: URL to download audio from
            
        Returns:
            Audio data as bytes
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(audio_url, timeout=30.0)
            response.raise_for_status()
            return response.content
    
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
            f"FAL speech generation failed: {message}",
            status_code=error.response.status_code,
        ) from error