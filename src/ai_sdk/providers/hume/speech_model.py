"""Hume AI speech model implementation."""

from typing import Dict, Any, Optional, List
import httpx
from datetime import datetime

from ...core.generate_speech import GenerateSpeechResult, GenerateSpeechUsage
from ...errors.base import AISDKError
from .types import (
    HumeProviderSettings,
    HumeSpeechSettings,
    HumeAudioFormat,
    HumeSpeechAPIRequest,
    HumeSpeechAPIUtterance,
    HumeSpeechAPIVoice,
    HumeFormatSpec,
    HumeErrorResponse,
)


class HumeSpeechModel:
    """Hume AI speech model for emotionally expressive text-to-speech."""
    
    def __init__(self, settings: HumeProviderSettings):
        """Initialize Hume speech model.
        
        Args:
            settings: Provider configuration settings
        """
        self.settings = settings
        
        # Construct headers
        self.headers = {
            "X-Hume-Api-Key": settings.api_key or "",
            "Content-Type": "application/json",
            **(settings.headers or {}),
        }
    
    async def generate(
        self,
        text: str,
        voice: Optional[str] = None,
        output_format: str = "mp3",
        speed: Optional[float] = None,
        instructions: Optional[str] = None,
        language: Optional[str] = None,
        options: Optional[HumeSpeechSettings] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> GenerateSpeechResult:
        """Generate speech using Hume AI.
        
        Args:
            text: Text to convert to speech
            voice: Voice ID (defaults to Hume's default voice)
            output_format: Audio format ("mp3", "pcm", "wav")
            speed: Speech rate multiplier
            instructions: Instructions for how the text should be spoken
            language: Language (will be ignored with warning)
            options: Additional speech options
            headers: Additional headers
            
        Returns:
            Speech generation result with emotional expression
            
        Raises:
            AISDKError: If speech generation fails
        """
        try:
            # Combine headers
            request_headers = {**self.headers}
            if headers:
                request_headers.update(headers)
            
            # Validate and normalize output format
            audio_format = self._normalize_audio_format(output_format)
            
            # Build API request
            api_request = self._build_api_request(
                text, voice, audio_format, speed, instructions, options
            )
            
            # Generate speech
            audio_data = await self._call_api(api_request, request_headers)
            
            # Create warnings for unsupported features
            warnings = []
            if language:
                warnings.append(
                    f"Language parameter '{language}' is not supported by Hume. "
                    f"Hume automatically handles emotional expression based on text content."
                )
            if output_format not in ["mp3", "pcm", "wav"]:
                warnings.append(
                    f"Output format '{output_format}' is not supported. Using 'mp3' instead."
                )
            
            return GenerateSpeechResult(
                audio=audio_data,
                usage=GenerateSpeechUsage(
                    characters=len(text),
                    total_characters=len(text),
                ),
                warnings=warnings,
                response={
                    "format": audio_format,
                    "utterance_count": 1,
                },
            )
            
        except httpx.HTTPStatusError as e:
            await self._handle_error_response(e)
        except Exception as e:
            raise AISDKError(f"Hume speech generation failed: {str(e)}") from e
    
    def _normalize_audio_format(self, output_format: str) -> HumeAudioFormat:
        """Normalize output format to supported Hume formats.
        
        Args:
            output_format: Requested output format
            
        Returns:
            Normalized audio format
        """
        if output_format.lower() in ["mp3", "pcm", "wav"]:
            return output_format.lower()  # type: ignore
        return "mp3"  # Default fallback
    
    def _build_api_request(
        self,
        text: str,
        voice: Optional[str],
        audio_format: HumeAudioFormat,
        speed: Optional[float],
        instructions: Optional[str],
        options: Optional[HumeSpeechSettings],
    ) -> HumeSpeechAPIRequest:
        """Build the API request from parameters.
        
        Args:
            text: Text to synthesize
            voice: Voice ID
            audio_format: Audio format
            speed: Speech speed
            instructions: Speaking instructions
            options: Additional options
            
        Returns:
            API request object
        """
        # Build voice configuration
        voice_config = None
        if voice:
            voice_config = HumeSpeechAPIVoice(
                id=voice,
                provider="HUME_AI",
            )
        
        # Build utterance
        utterance = HumeSpeechAPIUtterance(
            text=text,
            description=instructions,
            speed=speed,
            voice=voice_config,
        )
        
        # Build format specification
        format_spec = HumeFormatSpec(type=audio_format)
        
        # Start with basic request
        api_request = HumeSpeechAPIRequest(
            utterances=[utterance],
            format=format_spec,
        )
        
        # Add options if provided
        if options:
            if options.context:
                # Convert context to API format
                if hasattr(options.context, 'generation_id'):
                    # Generation context
                    from .types import HumeSpeechAPIContextGeneration
                    api_request.context = HumeSpeechAPIContextGeneration(
                        generation_id=options.context.generation_id  # type: ignore
                    )
                elif hasattr(options.context, 'utterances'):
                    # Utterances context
                    from .types import HumeSpeechAPIContextUtterances
                    api_utterances = []
                    for utt in options.context.utterances:  # type: ignore
                        api_voice = None
                        if utt.voice:
                            if hasattr(utt.voice, 'id'):
                                api_voice = HumeSpeechAPIVoice(
                                    id=utt.voice.id,  # type: ignore
                                    provider=utt.voice.provider,  # type: ignore
                                )
                            else:
                                api_voice = HumeSpeechAPIVoice(
                                    name=utt.voice.name,  # type: ignore
                                    provider=utt.voice.provider,  # type: ignore
                                )
                        
                        api_utterances.append(HumeSpeechAPIUtterance(
                            text=utt.text,
                            description=utt.description,
                            speed=utt.speed,
                            trailing_silence=utt.trailing_silence,
                            voice=api_voice,
                        ))
                    
                    api_request.context = HumeSpeechAPIContextUtterances(
                        utterances=api_utterances
                    )
            
            if options.format:
                api_request.format = options.format
        
        return api_request
    
    async def _call_api(
        self, 
        api_request: HumeSpeechAPIRequest, 
        headers: Dict[str, str]
    ) -> bytes:
        """Call the Hume API and return audio data.
        
        Args:
            api_request: API request object
            headers: Request headers
            
        Returns:
            Audio data as bytes
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.settings.base_url}/v0/tts/file",
                json=api_request.model_dump(exclude_none=True),
                headers=headers,
                timeout=60.0,
            )
            response.raise_for_status()
            
            # Hume returns binary audio data directly
            return response.content
    
    async def _handle_error_response(self, error: httpx.HTTPStatusError) -> None:
        """Handle HTTP error response from Hume.
        
        Args:
            error: HTTP status error
            
        Raises:
            AISDKError: With detailed error message
        """
        try:
            error_data = error.response.json()
            hume_error = HumeErrorResponse.model_validate(error_data)
            message = hume_error.message
            if hume_error.code:
                message = f"{hume_error.code}: {message}"
        except Exception:
            message = f"Hume API error: {error.response.status_code}"
        
        raise AISDKError(
            f"Hume speech generation failed: {message}",
            status_code=error.response.status_code,
        ) from error