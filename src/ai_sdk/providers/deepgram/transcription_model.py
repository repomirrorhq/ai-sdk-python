"""Deepgram transcription model implementation."""

import json
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from urllib.parse import urlencode

import httpx
from pydantic import ValidationError

from ...core.transcribe import TranscriptionResult, TranscriptionSegment
from ...errors import AISDKError, APICallError
from ...schemas import AudioData
from .types import (
    DeepgramTranscriptionModelId,
    DeepgramTranscriptionOptions,
    DeepgramTranscriptionResponse,
    DeepgramError,
    DeepgramTranscriptionAPIRequest,
)


class DeepgramTranscriptionModel:
    """
    Deepgram transcription model.
    
    Provides advanced speech-to-text transcription using Deepgram's AI models
    with features like speaker diarization, sentiment analysis, topic detection,
    entity recognition, and more.
    
    Example:
        ```python
        from ai_sdk.providers.deepgram import DeepgramProvider
        
        provider = DeepgramProvider(api_key="your-api-key")
        model = provider.transcription("nova-3")
        
        # Basic transcription
        with open("audio.mp3", "rb") as f:
            audio_data = f.read()
        
        result = await model.transcribe(
            audio=audio_data,
            media_type="audio/mp3"
        )
        
        # Advanced transcription with AI features
        result = await model.transcribe(
            audio=audio_data,
            media_type="audio/mp3",
            provider_options={
                "diarize": True,          # Speaker identification
                "smart_format": True,     # Smart number/date formatting
                "sentiment": True,        # Sentiment analysis
                "topics": True,           # Topic detection
                "summarize": "v2",        # Generate summary
                "detect_entities": True,  # Named entity recognition
                "punctuate": True,        # Add punctuation
                "paragraphs": True,       # Format into paragraphs
                "utterances": True,       # Segment by utterances
            }
        )
        ```
    """
    
    def __init__(
        self,
        model_id: DeepgramTranscriptionModelId,
        provider: "DeepgramProvider",
        **kwargs: Any,
    ):
        """
        Initialize Deepgram transcription model.
        
        Args:
            model_id: The Deepgram model ID
            provider: The Deepgram provider instance
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
        provider_options: Optional[Union[Dict[str, Any], DeepgramTranscriptionOptions]] = None,
        headers: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> TranscriptionResult:
        """
        Transcribe audio to text using Deepgram.
        
        Args:
            audio: Audio data as bytes or AudioData object
            media_type: MIME type of the audio (e.g., 'audio/mp3', 'audio/wav')
            language: Language code hint for transcription (e.g., 'en-US', 'es', 'fr')
            provider_options: Deepgram-specific options
            headers: Additional HTTP headers
            **kwargs: Additional options
            
        Returns:
            TranscriptionResult with transcribed text and advanced metadata
            
        Raises:
            APICallError: If the API request fails
            AISDKError: If there's a validation or processing error
        """
        try:
            # Parse provider options
            if provider_options:
                if isinstance(provider_options, dict):
                    try:
                        options = DeepgramTranscriptionOptions(**provider_options)
                    except ValidationError as e:
                        raise AISDKError(f"Invalid provider options: {e}")
                else:
                    options = provider_options
            else:
                options = DeepgramTranscriptionOptions()
            
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
            
            # Build request parameters
            request_params = DeepgramTranscriptionAPIRequest(
                model=self.model_id,
                language=language or options.language,
                diarize=True,  # Default to enable diarization
            )
            
            # Add provider-specific options
            if options.smart_format is not None:
                request_params.smart_format = options.smart_format
            if options.punctuate is not None:
                request_params.punctuate = options.punctuate
            if options.paragraphs is not None:
                request_params.paragraphs = options.paragraphs
            if options.summarize is not None:
                request_params.summarize = options.summarize
            if options.topics is not None:
                request_params.topics = options.topics
            if options.intents is not None:
                request_params.intents = options.intents
            if options.sentiment is not None:
                request_params.sentiment = options.sentiment
            if options.detect_entities is not None:
                request_params.detect_entities = options.detect_entities
            if options.redact is not None:
                request_params.redact = options.redact
            if options.replace is not None:
                request_params.replace = options.replace
            if options.search is not None:
                request_params.search = options.search
            if options.keyterm is not None:
                request_params.keyterm = options.keyterm
            if options.diarize is not None:
                request_params.diarize = options.diarize
            if options.utterances is not None:
                request_params.utterances = options.utterances
            if options.utt_split is not None:
                request_params.utt_split = options.utt_split
            if options.filler_words is not None:
                request_params.filler_words = options.filler_words
            
            # Convert to query parameters
            query_params = {}
            param_dict = request_params.model_dump(exclude_none=True)
            for key, value in param_dict.items():
                if value is not None:
                    if isinstance(value, list):
                        query_params[key] = ",".join(str(v) for v in value)
                    elif isinstance(value, bool):
                        query_params[key] = str(value).lower()
                    else:
                        query_params[key] = str(value)
            
            # Build URL with query parameters
            base_url = self.provider._get_base_url("/v1/listen")
            if query_params:
                url = f"{base_url}?{urlencode(query_params)}"
            else:
                url = base_url
            
            # Prepare headers
            request_headers = self.provider._get_headers()
            request_headers["Content-Type"] = media_type
            
            if headers:
                request_headers.update(headers)
            
            # Make API request
            async with self.provider.http_client as client:
                response = await client.post(
                    url,
                    content=audio_bytes,
                    headers=request_headers,
                )
                
                if response.status_code != 200:
                    await self._handle_error_response(response)
                
                # Parse response
                response_data = response.json()
                deepgram_response = DeepgramTranscriptionResponse(**response_data)
                
                # Extract main transcript
                text = ""
                if (deepgram_response.results and 
                    deepgram_response.results.channels and 
                    deepgram_response.results.channels[0].alternatives):
                    text = deepgram_response.results.channels[0].alternatives[0].transcript
                
                # Extract word-level segments
                segments = []
                if (deepgram_response.results and 
                    deepgram_response.results.channels and 
                    deepgram_response.results.channels[0].alternatives and
                    deepgram_response.results.channels[0].alternatives[0].words):
                    
                    words = deepgram_response.results.channels[0].alternatives[0].words
                    for word in words:
                        segment = TranscriptionSegment(
                            text=word.word,
                            start_time=word.start,
                            end_time=word.end,
                            speaker_id=str(word.speaker) if word.speaker is not None else None,
                            confidence=word.confidence,
                        )
                        segments.append(segment)
                
                # Extract duration
                duration = None
                if deepgram_response.metadata and deepgram_response.metadata.duration:
                    duration = deepgram_response.metadata.duration
                
                # Build metadata with advanced features
                metadata = {}
                
                if deepgram_response.metadata:
                    metadata["request_id"] = deepgram_response.metadata.request_id
                    metadata["transaction_key"] = deepgram_response.metadata.transaction_key
                    metadata["models"] = deepgram_response.metadata.models
                    metadata["channels"] = deepgram_response.metadata.channels
                
                # Add analysis results
                if (deepgram_response.results and 
                    deepgram_response.results.channels and 
                    deepgram_response.results.channels[0].alternatives):
                    
                    alternative = deepgram_response.results.channels[0].alternatives[0]
                    
                    if alternative.summaries:
                        metadata["summaries"] = [
                            {
                                "summary": summary.summary,
                                "start_word": summary.start_word,
                                "end_word": summary.end_word,
                            } 
                            for summary in alternative.summaries
                        ]
                    
                    if alternative.topics:
                        metadata["topics"] = [
                            {
                                "topic": topic.topic,
                                "confidence": topic.confidence,
                            }
                            for topic in alternative.topics
                        ]
                    
                    if alternative.intents:
                        metadata["intents"] = [
                            {
                                "intent": intent.intent,
                                "confidence": intent.confidence,
                            }
                            for intent in alternative.intents
                        ]
                    
                    if alternative.sentiments:
                        metadata["sentiments"] = [
                            {
                                "sentiment": sentiment.sentiment,
                                "confidence": sentiment.confidence,
                                "start_word": sentiment.start_word,
                                "end_word": sentiment.end_word,
                            }
                            for sentiment in alternative.sentiments
                        ]
                    
                    if alternative.entities:
                        metadata["entities"] = [
                            {
                                "label": entity.label,
                                "value": entity.value,
                                "confidence": entity.confidence,
                                "start_word": entity.start_word,
                                "end_word": entity.end_word,
                            }
                            for entity in alternative.entities
                        ]
                
                # Add utterance information
                if deepgram_response.results and deepgram_response.results.utterances:
                    metadata["utterances"] = [
                        {
                            "start": utterance.start,
                            "end": utterance.end,
                            "confidence": utterance.confidence,
                            "transcript": utterance.transcript,
                            "speaker": utterance.speaker,
                        }
                        for utterance in deepgram_response.results.utterances
                    ]
                
                return TranscriptionResult(
                    text=text,
                    segments=segments,
                    language=deepgram_response.metadata.models[0] if deepgram_response.metadata and deepgram_response.metadata.models else None,
                    duration_seconds=duration,
                    model_id=self.model_id,
                    provider="deepgram",
                    timestamp=datetime.now(),
                    usage=None,  # Deepgram doesn't provide usage info in response
                    response_headers=dict(response.headers),
                    metadata=metadata,
                )
                
        except httpx.RequestError as e:
            raise APICallError(
                f"Deepgram API request failed: {str(e)}",
                provider="deepgram",
                model_id=self.model_id,
            )
        except ValidationError as e:
            raise AISDKError(f"Response validation failed: {str(e)}")
        except Exception as e:
            if isinstance(e, (APICallError, AISDKError)):
                raise
            raise AISDKError(f"Unexpected error in Deepgram transcription: {str(e)}")
    
    async def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses from Deepgram API."""
        try:
            error_data = response.json()
            if isinstance(error_data, dict) and "error" in error_data:
                error_info = DeepgramError(**error_data)
                error_message = error_info.error.message
                error_code = error_info.error.code
            else:
                error_message = f"HTTP {response.status_code}: {response.text}"
                error_code = response.status_code
        except (json.JSONDecodeError, ValidationError, KeyError):
            error_message = f"HTTP {response.status_code}: {response.text}"
            error_code = response.status_code
        
        raise APICallError(
            message=f"Deepgram API error: {error_message}",
            status_code=response.status_code,
            provider="deepgram",
            model_id=self.model_id,
            response_body=response.text,
        )