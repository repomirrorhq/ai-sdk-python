"""
Gladia Transcription Model implementation.
"""

import asyncio
import base64
import os
from typing import Any, Dict, List, Optional, Union
import httpx
from ai_sdk.core.types import TranscriptionModel, TranscriptionResult, TranscriptionSegment
from ai_sdk.errors.base import AISDKError, APIError
from ai_sdk.utils.http import create_http_client
from .types import (
    GladiaProviderSettings, 
    GladiaTranscriptionOptions,
    GladiaUploadResponse,
    GladiaTranscriptionInitResponse,
    GladiaTranscriptionStatus
)


class GladiaTranscriptionModel(TranscriptionModel):
    """
    Gladia transcription model implementation.
    
    Provides advanced audio transcription with AI-powered features including
    speaker diarization, multi-language support, translation, and summarization.
    """
    
    def __init__(self, settings: GladiaProviderSettings):
        """
        Initialize Gladia transcription model.
        
        Args:
            settings: Provider settings including API key and configuration.
        """
        self.settings = settings
        self.api_key = settings.api_key or os.getenv("GLADIA_API_KEY")
        
        if not self.api_key:
            raise AISDKError("Gladia API key is required. Set GLADIA_API_KEY environment variable or pass api_key parameter.")
        
        self.base_url = settings.base_url.rstrip("/")
        self.client = create_http_client(
            timeout=settings.timeout,
            max_retries=settings.max_retries
        )
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            "x-gladia-key": self.api_key,
            "Content-Type": "application/json",
        }
        
        if self.settings.headers:
            headers.update(self.settings.headers)
        
        return headers
    
    def _prepare_transcription_request(
        self, 
        options: Optional[GladiaTranscriptionOptions] = None
    ) -> Dict[str, Any]:
        """Prepare the transcription request body."""
        body = {}
        
        if not options:
            return body
        
        # Basic options
        if options.context_prompt is not None:
            body["context_prompt"] = options.context_prompt
        if options.custom_vocabulary is not None:
            body["custom_vocabulary"] = options.custom_vocabulary
        if options.detect_language is not None:
            body["detect_language"] = options.detect_language
        if options.enable_code_switching is not None:
            body["enable_code_switching"] = options.enable_code_switching
        if options.language is not None:
            body["language"] = options.language
        if options.callback is not None:
            body["callback"] = options.callback
        if options.subtitles is not None:
            body["subtitles"] = options.subtitles
        if options.diarization is not None:
            body["diarization"] = options.diarization
        if options.translation is not None:
            body["translation"] = options.translation
        if options.summarization is not None:
            body["summarization"] = options.summarization
        if options.moderation is not None:
            body["moderation"] = options.moderation
        if options.named_entity_recognition is not None:
            body["named_entity_recognition"] = options.named_entity_recognition
        if options.chapterization is not None:
            body["chapterization"] = options.chapterization
        if options.name_consistency is not None:
            body["name_consistency"] = options.name_consistency
        if options.custom_spelling is not None:
            body["custom_spelling"] = options.custom_spelling
        if options.structured_data_extraction is not None:
            body["structured_data_extraction"] = options.structured_data_extraction
        if options.sentiment_analysis is not None:
            body["sentiment_analysis"] = options.sentiment_analysis
        if options.audio_to_llm is not None:
            body["audio_to_llm"] = options.audio_to_llm
        if options.custom_metadata is not None:
            body["custom_metadata"] = options.custom_metadata
        if options.sentences is not None:
            body["sentences"] = options.sentences
        if options.display_mode is not None:
            body["display_mode"] = options.display_mode
        if options.punctuation_enhanced is not None:
            body["punctuation_enhanced"] = options.punctuation_enhanced
        
        # Complex configuration objects
        if options.custom_vocabulary_config:
            config = options.custom_vocabulary_config
            body["custom_vocabulary_config"] = {
                "vocabulary": [
                    item if isinstance(item, str) else {
                        "value": item.value,
                        **({"intensity": item.intensity} if item.intensity is not None else {}),
                        **({"pronunciations": item.pronunciations} if item.pronunciations is not None else {}),
                        **({"language": item.language} if item.language is not None else {}),
                    }
                    for item in config.vocabulary
                ],
                **({"default_intensity": config.default_intensity} if config.default_intensity is not None else {})
            }
        
        if options.code_switching_config:
            body["code_switching_config"] = {
                **({"languages": options.code_switching_config.languages} 
                   if options.code_switching_config.languages is not None else {})
            }
        
        if options.callback_config:
            body["callback_config"] = {
                "url": options.callback_config.url,
                **({"method": options.callback_config.method} 
                   if options.callback_config.method is not None else {})
            }
        
        if options.subtitles_config:
            config = options.subtitles_config
            body["subtitles_config"] = {
                **({"formats": config.formats} if config.formats is not None else {}),
                **({"minimum_duration": config.minimum_duration} if config.minimum_duration is not None else {}),
                **({"maximum_duration": config.maximum_duration} if config.maximum_duration is not None else {}),
                **({"maximum_characters_per_row": config.maximum_characters_per_row} if config.maximum_characters_per_row is not None else {}),
                **({"maximum_rows_per_caption": config.maximum_rows_per_caption} if config.maximum_rows_per_caption is not None else {}),
                **({"style": config.style} if config.style is not None else {}),
            }
        
        if options.diarization_config:
            config = options.diarization_config
            body["diarization_config"] = {
                **({"number_of_speakers": config.number_of_speakers} if config.number_of_speakers is not None else {}),
                **({"min_speakers": config.min_speakers} if config.min_speakers is not None else {}),
                **({"max_speakers": config.max_speakers} if config.max_speakers is not None else {}),
                **({"enhanced": config.enhanced} if config.enhanced is not None else {}),
            }
        
        if options.translation_config:
            body["translation_config"] = {
                "target_languages": options.translation_config.target_languages,
                **({"model": options.translation_config.model} if options.translation_config.model is not None else {}),
                **({"match_original_utterances": options.translation_config.match_original_utterances} if options.translation_config.match_original_utterances is not None else {}),
            }
        
        if options.summarization_config:
            body["summarization_config"] = {
                **({"type": options.summarization_config.type} if options.summarization_config.type is not None else {})
            }
        
        if options.custom_spelling_config:
            body["custom_spelling_config"] = {
                "spelling_dictionary": options.custom_spelling_config.spelling_dictionary
            }
        
        if options.structured_data_extraction_config:
            body["structured_data_extraction_config"] = options.structured_data_extraction_config
        
        if options.audio_to_llm_config:
            body["audio_to_llm_config"] = {
                "prompts": options.audio_to_llm_config.prompts
            }
        
        return body
    
    async def _upload_audio(
        self, 
        audio: Union[bytes, str], 
        media_type: str
    ) -> str:
        """Upload audio file to Gladia and get URL."""
        
        # Prepare audio data
        if isinstance(audio, str):
            # Assume base64 encoded
            audio_bytes = base64.b64decode(audio)
        else:
            audio_bytes = audio
        
        # Create form data
        files = {
            "audio": ("audio", audio_bytes, media_type)
        }
        
        try:
            response = await self.client.post(
                f"{self.base_url}/v2/upload",
                headers={"x-gladia-key": self.api_key},
                files=files
            )
            response.raise_for_status()
            
            data = response.json()
            upload_response = GladiaUploadResponse.model_validate(data)
            return upload_response.audio_url
            
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                error_detail = error_data.get("error", {}).get("message", str(error_data))
            except:
                error_detail = e.response.text
            
            raise APIError(
                f"Gladia upload failed: {error_detail}",
                status_code=e.response.status_code
            )
        except Exception as e:
            raise APIError(f"Gladia upload failed: {str(e)}")
    
    async def _initiate_transcription(
        self, 
        audio_url: str, 
        options: Optional[GladiaTranscriptionOptions] = None
    ) -> str:
        """Initiate transcription and get result URL."""
        
        body = self._prepare_transcription_request(options)
        body["audio_url"] = audio_url
        
        try:
            response = await self.client.post(
                f"{self.base_url}/v2/pre-recorded",
                headers=self._get_headers(),
                json=body
            )
            response.raise_for_status()
            
            data = response.json()
            init_response = GladiaTranscriptionInitResponse.model_validate(data)
            return init_response.result_url
            
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                error_detail = error_data.get("error", {}).get("message", str(error_data))
            except:
                error_detail = e.response.text
            
            raise APIError(
                f"Gladia transcription initiation failed: {error_detail}",
                status_code=e.response.status_code
            )
        except Exception as e:
            raise APIError(f"Gladia transcription initiation failed: {str(e)}")
    
    async def _poll_result(self, result_url: str) -> GladiaTranscriptionStatus:
        """Poll transcription result until completion."""
        
        timeout_seconds = 300  # 5 minutes
        poll_interval = 2  # 2 seconds
        max_polls = timeout_seconds // poll_interval
        
        for _ in range(max_polls):
            try:
                response = await self.client.get(
                    result_url,
                    headers=self._get_headers()
                )
                response.raise_for_status()
                
                data = response.json()
                status = GladiaTranscriptionStatus.model_validate(data)
                
                if status.status == "done":
                    return status
                elif status.status == "error":
                    raise APIError(f"Gladia transcription failed: {status.error}")
                
                # Continue polling for "queued" or "processing"
                await asyncio.sleep(poll_interval)
                
            except httpx.HTTPStatusError as e:
                error_detail = "Unknown error"
                try:
                    error_data = e.response.json()
                    error_detail = error_data.get("error", {}).get("message", str(error_data))
                except:
                    error_detail = e.response.text
                
                raise APIError(
                    f"Gladia result polling failed: {error_detail}",
                    status_code=e.response.status_code
                )
            except Exception as e:
                raise APIError(f"Gladia result polling failed: {str(e)}")
        
        raise APIError("Gladia transcription timed out")
    
    async def transcribe(
        self,
        audio: Union[bytes, str],
        *,
        media_type: str = "audio/wav",
        options: Optional[GladiaTranscriptionOptions] = None,
        **kwargs
    ) -> TranscriptionResult:
        """
        Transcribe audio using Gladia API.
        
        Args:
            audio: Audio data as bytes or base64 string
            media_type: MIME type of the audio file
            options: Gladia-specific transcription options
            **kwargs: Additional parameters
            
        Returns:
            TranscriptionResult with text and metadata
        """
        
        try:
            # Step 1: Upload audio
            audio_url = await self._upload_audio(audio, media_type)
            
            # Step 2: Initiate transcription
            result_url = await self._initiate_transcription(audio_url, options)
            
            # Step 3: Poll for results
            status = await self._poll_result(result_url)
            
            if not status.result:
                raise APIError("Gladia transcription result is empty")
            
            # Step 4: Process results
            result = status.result
            transcription = result.transcription
            metadata = result.metadata
            
            # Convert segments
            segments: List[TranscriptionSegment] = []
            for utterance in transcription.utterances:
                segments.append(TranscriptionSegment(
                    text=utterance.text,
                    start_time=utterance.start,
                    end_time=utterance.end,
                    speaker=getattr(utterance, 'speaker', None)
                ))
            
            return TranscriptionResult(
                text=transcription.full_transcript,
                segments=segments,
                language=transcription.languages[0] if transcription.languages else None,
                duration=metadata.audio_duration,
                provider_metadata={
                    "gladia": status.model_dump()
                }
            )
            
        except APIError:
            raise
        except Exception as e:
            raise APIError(f"Gladia transcription failed: {str(e)}")