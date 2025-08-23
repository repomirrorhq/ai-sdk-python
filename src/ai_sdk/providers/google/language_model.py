"""Google Generative AI Language Model implementation."""

import json
import asyncio
from typing import Any, Dict, List, Optional, AsyncIterator, Union, Type, TypeVar
from urllib.parse import urljoin

import httpx

from ...providers.base import LanguageModel
from ...providers.types import (
    GenerateOptions,
    StreamOptions,
    GenerateResult,
    StreamResult,
    Usage,
    FinishReason,
    Message,
    StreamPart,
    TextStreamPart,
    UsageStreamPart,
    FinishStreamPart,
)
from ...errors.base import APIError, AISDKError
from ...utils.http import create_http_client
from ...utils.json import extract_json_from_text
from .api_types import (
    GoogleModelId,
    GoogleProviderOptions,
    GooglePromptRequest,
    GoogleResponse,
    GoogleStreamResponse,
    GoogleGenerationConfig,
    GoogleErrorResponse,
    GoogleUsageMetadata,
)
from .message_converter import convert_to_google_messages, convert_google_response_to_message

T = TypeVar("T")


def _map_finish_reason(google_reason: Optional[str]) -> FinishReason:
    """Map Google finish reason to AI SDK format."""
    if not google_reason:
        return "stop"
    
    reason_map = {
        "STOP": "stop",
        "MAX_TOKENS": "length", 
        "SAFETY": "content-filter",
        "RECITATION": "content-filter",
        "OTHER": "other",
        "FINISH_REASON_UNSPECIFIED": "other",
    }
    
    return reason_map.get(google_reason, "other")


def _convert_usage(usage: Optional[GoogleUsageMetadata]) -> Usage:
    """Convert Google usage metadata to AI SDK format."""
    if not usage:
        return Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
    
    return Usage(
        prompt_tokens=usage.prompt_token_count,
        completion_tokens=usage.candidates_token_count, 
        total_tokens=usage.total_token_count,
        reasoning_tokens=usage.thoughts_token_count,
        cached_input_tokens=usage.cached_content_token_count,
    )


class GoogleLanguageModel(LanguageModel):
    """Google Generative AI language model implementation."""
    
    def __init__(
        self,
        model_id: GoogleModelId,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        http_client: Optional[httpx.AsyncClient] = None,
        **kwargs: Any,
    ):
        """
        Initialize Google Generative AI language model.
        
        Args:
            model_id: The Google model ID
            api_key: Google API key (defaults to GOOGLE_GENERATIVE_AI_API_KEY env var)
            base_url: Base URL for API (defaults to official Google API)
            http_client: Optional HTTP client
            **kwargs: Additional arguments
        """
        self.model_id = model_id
        self.api_key = api_key
        self.base_url = base_url or "https://generativelanguage.googleapis.com/v1beta"
        self.http_client = http_client
        self.provider_id = "google"
        
        # Check if this is a Gemma model (affects message handling)
        self.is_gemma_model = "gemma" in model_id.lower()
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        headers = {"Content-Type": "application/json"}
        
        if self.api_key:
            headers["x-goog-api-key"] = self.api_key
        
        return headers
    
    def _get_model_path(self, model_id: str) -> str:
        """Get the model path for API requests.""" 
        if "/" in model_id:
            return model_id  # Already a full path
        return f"models/{model_id}"
    
    def _prepare_request(
        self,
        messages: List[Message],
        options: Union[GenerateOptions, StreamOptions],
    ) -> GooglePromptRequest:
        """Prepare the request payload for Google API."""
        
        # Convert messages to Google format
        contents, system_instruction = convert_to_google_messages(messages)
        
        # Build generation config
        generation_config = GoogleGenerationConfig()
        
        if options.max_tokens is not None:
            generation_config.max_output_tokens = options.max_tokens
        if options.temperature is not None:
            generation_config.temperature = options.temperature
        if options.top_p is not None:
            generation_config.top_p = options.top_p
        if hasattr(options, "top_k") and options.top_k is not None:
            generation_config.top_k = options.top_k
        if options.stop is not None:
            if isinstance(options.stop, str):
                generation_config.stop_sequences = [options.stop]
            else:
                generation_config.stop_sequences = list(options.stop)
        
        # Handle structured outputs for generate_object
        if hasattr(options, "response_format") and options.response_format:
            if options.response_format.get("type") == "json_object":
                generation_config.response_mime_type = "application/json"
                if "schema" in options.response_format:
                    generation_config.response_schema = options.response_format["schema"]
        
        # Build the request
        request = GooglePromptRequest(
            contents=contents,
            generation_config=generation_config,
        )
        
        # Add system instruction if present
        if system_instruction:
            request.system_instruction = {
                "parts": [{"text": system_instruction}]
            }
        
        # Handle provider-specific options
        if hasattr(options, "provider_options") and options.provider_options:
            google_options = options.provider_options.get("google", {})
            if isinstance(google_options, dict):
                # Apply Google-specific options
                if "safety_settings" in google_options:
                    request.safety_settings = google_options["safety_settings"]
        
        return request
    
    async def do_generate(self, options: GenerateOptions) -> GenerateResult:
        """Generate text using Google Generative AI."""
        try:
            # Prepare request
            request = self._prepare_request(options.messages, options)
            
            # Get model path
            model_path = self._get_model_path(self.model_id)
            url = urljoin(self.base_url.rstrip("/") + "/", f"{model_path}:generateContent")
            
            # Create HTTP client
            async with create_http_client(self.http_client) as client:
                # Make request
                response = await client.post(
                    url,
                    json=request.model_dump(exclude_none=True),
                    headers=self._get_headers(),
                )
                
                if not response.is_success:
                    await self._handle_error_response(response)
                
                # Parse response
                response_data = response.json()
                google_response = GoogleResponse.model_validate(response_data)
                
                # Extract result
                if not google_response.candidates:
                    raise APIError("No candidates returned by Google API")
                
                candidate = google_response.candidates[0]
                if not candidate.content or not candidate.content.parts:
                    raise APIError("No content in Google API response")
                
                # Extract text from parts
                text_parts = []
                for part in candidate.content.parts:
                    if part.text:
                        text_parts.append(part.text)
                
                text = "".join(text_parts)
                
                # Convert usage
                usage = _convert_usage(google_response.usage_metadata)
                
                # Map finish reason
                finish_reason = _map_finish_reason(candidate.finish_reason)
                
                return GenerateResult(
                    text=text,
                    usage=usage,
                    finish_reason=finish_reason,
                    response_messages=[
                        convert_google_response_to_message(candidate.content)
                    ],
                )
                
        except Exception as e:
            if isinstance(e, AISDKError):
                raise
            raise APIError(f"Google API error: {str(e)}") from e
    
    async def do_stream(self, options: StreamOptions) -> AsyncIterator[StreamResult]:
        """Stream text generation using Google Generative AI."""
        try:
            # Prepare request
            request = self._prepare_request(options.messages, options) 
            
            # Get model path
            model_path = self._get_model_path(self.model_id)
            url = urljoin(self.base_url.rstrip("/") + "/", f"{model_path}:streamGenerateContent")
            
            # Create HTTP client
            async with create_http_client(self.http_client) as client:
                
                # Make streaming request
                async with client.stream(
                    "POST",
                    url,
                    json=request.model_dump(exclude_none=True),
                    headers=self._get_headers(),
                ) as response:
                    
                    if not response.is_success:
                        await self._handle_error_response(response)
                    
                    # Process streaming response
                    accumulated_text = ""
                    
                    async for line in response.aiter_lines():
                        if not line or not line.strip():
                            continue
                        
                        # Parse JSON from line (Google uses raw JSON streaming)
                        try:
                            chunk_data = json.loads(line)
                            chunk = GoogleStreamResponse.model_validate(chunk_data)
                            
                            # Process candidates
                            if chunk.candidates:
                                for candidate in chunk.candidates:
                                    if candidate.content and candidate.content.parts:
                                        # Extract text from parts
                                        for part in candidate.content.parts:
                                            if part.text:
                                                accumulated_text += part.text
                                                
                                                # Yield text delta
                                                yield StreamResult(
                                                    stream_parts=[
                                                        TextStreamPart(
                                                            type="text-delta",
                                                            text_delta=part.text
                                                        )
                                                    ]
                                                )
                                    
                                    # Check for finish
                                    if candidate.finish_reason:
                                        finish_reason = _map_finish_reason(candidate.finish_reason)
                                        
                                        # Yield finish event
                                        yield StreamResult(
                                            stream_parts=[
                                                FinishStreamPart(
                                                    type="finish",
                                                    finish_reason=finish_reason,
                                                    usage=_convert_usage(chunk.usage_metadata) if chunk.usage_metadata else None,
                                                )
                                            ]
                                        )
                            
                            # Handle usage updates
                            if chunk.usage_metadata:
                                usage = _convert_usage(chunk.usage_metadata)
                                yield StreamResult(
                                    stream_parts=[
                                        UsageStreamPart(
                                            type="usage",
                                            usage=usage
                                        )
                                    ]
                                )
                                
                        except json.JSONDecodeError as e:
                            # Skip invalid JSON lines
                            continue
                        except Exception as e:
                            # Log but continue processing
                            continue
                            
        except Exception as e:
            if isinstance(e, AISDKError):
                raise
            raise APIError(f"Google streaming error: {str(e)}") from e
    
    async def _handle_error_response(self, response: httpx.Response) -> None:
        """Handle error responses from Google API."""
        try:
            error_data = response.json()
            google_error = GoogleErrorResponse.model_validate(error_data)
            error = google_error.error
            
            # Map Google error codes to our error types
            if error.code == 400:
                raise APIError(f"Bad request to Google API: {error.message}")
            elif error.code == 401:
                raise APIError(f"Authentication failed with Google API: {error.message}")
            elif error.code == 403:
                raise APIError(f"Access forbidden to Google API: {error.message}")
            elif error.code == 429:
                raise APIError(f"Rate limit exceeded for Google API: {error.message}")
            elif error.code >= 500:
                raise APIError(f"Google API server error: {error.message}")
            else:
                raise APIError(f"Google API error ({error.code}): {error.message}")
                
        except Exception as e:
            if isinstance(e, APIError):
                raise
            # Fallback error message
            raise APIError(
                f"Google API error: {response.status_code} {response.reason_phrase}"
            )