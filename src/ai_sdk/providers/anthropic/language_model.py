"""
Anthropic language model implementation.

This module implements the language model interface for Anthropic's Claude models.
"""

import json
from typing import Dict, List, Any, Optional, AsyncIterator, Union
import httpx

from ...core.types import (
    Message,
    GenerateTextResult,
    StreamTextResult,
    TextStreamPart,
    Usage,
    FinishReason,
)
from ...providers.base import BaseLanguageModel
from ...providers.types import ProviderSettings
from ...errors.base import AISDKError, APIError
from ...utils.http import make_request, stream_request
from ...utils.json import safe_json_parse
from .api_types import AnthropicMessage, AnthropicResponse, AnthropicStreamChunk
from .message_converter import convert_messages_to_anthropic, convert_anthropic_response


class AnthropicLanguageModel(BaseLanguageModel):
    """
    Anthropic Claude language model implementation.
    """
    
    def __init__(self, model_id: str, settings: ProviderSettings):
        """
        Initialize Anthropic language model.
        
        Args:
            model_id: Model identifier (e.g., "claude-3-sonnet-20240229")
            settings: Provider settings
        """
        super().__init__(model_id, settings)
        self.model_id = model_id
        self.settings = settings
    
    def _build_headers(self) -> Dict[str, str]:
        """Build request headers for Anthropic API."""
        headers = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
            "x-api-key": self.settings.api_key,
        }
        headers.update(self.settings.headers)
        return headers
    
    def _build_request_body(
        self,
        messages: List[Message],
        max_tokens: int = 4096,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        stream: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Build request body for Anthropic Messages API.
        
        Args:
            messages: List of messages
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter  
            stop_sequences: List of stop sequences
            stream: Whether to stream the response
            **kwargs: Additional parameters
            
        Returns:
            Request body dictionary
        """
        # Convert messages to Anthropic format
        anthropic_prompt = convert_messages_to_anthropic(messages)
        
        body = {
            "model": self.model_id,
            "max_tokens": max_tokens,
            "messages": anthropic_prompt["messages"],
        }
        
        # Add system message if present
        if anthropic_prompt.get("system"):
            body["system"] = anthropic_prompt["system"]
        
        # Add optional parameters
        if temperature is not None:
            body["temperature"] = temperature
        if top_p is not None:
            body["top_p"] = top_p
        if top_k is not None:
            body["top_k"] = top_k
        if stop_sequences is not None:
            body["stop_sequences"] = stop_sequences
        if stream:
            body["stream"] = True
            
        return body
    
    async def do_generate(
        self,
        messages: List[Message],
        max_tokens: int = 4096,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> GenerateTextResult:
        """
        Generate text using Anthropic API.
        
        Args:
            messages: List of messages
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            stop_sequences: List of stop sequences
            tools: List of tools (function definitions)
            **kwargs: Additional parameters
            
        Returns:
            GenerateTextResult with generated text and metadata
            
        Raises:
            APIError: If the API request fails
            AISDKError: If there's an error in processing
        """
        try:
            # Build request body
            body = self._build_request_body(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                stop_sequences=stop_sequences,
                stream=False,
                **kwargs,
            )
            
            # Add tools if provided
            if tools:
                body["tools"] = tools
            
            # Make request
            response_data = await make_request(
                url=f"{self.settings.base_url}/messages",
                headers=self._build_headers(),
                body=body,
            )
            
            # Convert response
            return convert_anthropic_response(response_data)
            
        except httpx.HTTPStatusError as e:
            error_body = e.response.text
            error_data = safe_json_parse(error_body)
            
            if error_data and "error" in error_data:
                error_msg = error_data["error"].get("message", str(e))
                error_type = error_data["error"].get("type", "api_error")
            else:
                error_msg = f"HTTP {e.response.status_code}: {error_body}"
                error_type = "api_error"
            
            raise APIError(
                message=f"Anthropic API error: {error_msg}",
                status_code=e.response.status_code,
                error_type=error_type,
            )
        except Exception as e:
            raise AISDKError(f"Error calling Anthropic API: {str(e)}")
    
    async def do_stream(
        self,
        messages: List[Message],
        max_tokens: int = 4096,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> StreamTextResult:
        """
        Stream text generation using Anthropic API.
        
        Args:
            messages: List of messages
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            stop_sequences: List of stop sequences
            tools: List of tools (function definitions)
            **kwargs: Additional parameters
            
        Returns:
            StreamTextResult with async stream of text parts
            
        Raises:
            APIError: If the API request fails
            AISDKError: If there's an error in processing
        """
        try:
            # Build request body
            body = self._build_request_body(
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                stop_sequences=stop_sequences,
                stream=True,
                **kwargs,
            )
            
            # Add tools if provided
            if tools:
                body["tools"] = tools
            
            # Create stream
            stream = self._create_stream(body)
            
            return StreamTextResult(stream=stream)
            
        except Exception as e:
            raise AISDKError(f"Error creating Anthropic stream: {str(e)}")
    
    async def _create_stream(
        self, body: Dict[str, Any]
    ) -> AsyncIterator[TextStreamPart]:
        """
        Create async stream for Anthropic API.
        
        Args:
            body: Request body
            
        Yields:
            TextStreamPart instances
        """
        try:
            # Stream the response
            async for chunk in stream_request(
                url=f"{self.settings.base_url}/messages",
                headers=self._build_headers(),
                body=body,
            ):
                # Parse the chunk
                chunk_data = safe_json_parse(chunk)
                if not chunk_data:
                    continue
                
                # Convert chunk to stream part
                stream_part = self._convert_chunk_to_stream_part(chunk_data)
                if stream_part:
                    yield stream_part
                    
        except httpx.HTTPStatusError as e:
            error_body = e.response.text
            error_data = safe_json_parse(error_body)
            
            if error_data and "error" in error_data:
                error_msg = error_data["error"].get("message", str(e))
                error_type = error_data["error"].get("type", "api_error")
            else:
                error_msg = f"HTTP {e.response.status_code}: {error_body}"
                error_type = "api_error"
            
            raise APIError(
                message=f"Anthropic API error: {error_msg}",
                status_code=e.response.status_code,
                error_type=error_type,
            )
        except Exception as e:
            raise AISDKError(f"Error in Anthropic stream: {str(e)}")
    
    def _convert_chunk_to_stream_part(
        self, chunk_data: Dict[str, Any]
    ) -> Optional[TextStreamPart]:
        """
        Convert Anthropic API chunk to TextStreamPart.
        
        Args:
            chunk_data: Chunk data from API
            
        Returns:
            TextStreamPart or None if chunk should be ignored
        """
        chunk_type = chunk_data.get("type")
        
        if chunk_type == "content_block_delta":
            delta = chunk_data.get("delta", {})
            if delta.get("type") == "text_delta":
                return TextStreamPart(
                    type="text-delta",
                    text_delta=delta.get("text", ""),
                )
        
        elif chunk_type == "message_start":
            message = chunk_data.get("message", {})
            usage = message.get("usage", {})
            return TextStreamPart(
                type="stream-start",
                usage=Usage(
                    input_tokens=usage.get("input_tokens", 0),
                    output_tokens=usage.get("output_tokens", 0),
                    total_tokens=usage.get("input_tokens", 0) + usage.get("output_tokens", 0),
                ),
            )
        
        elif chunk_type == "message_delta":
            delta = chunk_data.get("delta", {})
            usage = chunk_data.get("usage", {})
            
            finish_reason = None
            if delta.get("stop_reason"):
                stop_reason = delta.get("stop_reason")
                if stop_reason == "end_turn":
                    finish_reason = "stop"
                elif stop_reason == "max_tokens":
                    finish_reason = "length"
                elif stop_reason == "stop_sequence":
                    finish_reason = "stop"
                else:
                    finish_reason = "unknown"
            
            return TextStreamPart(
                type="finish",
                finish_reason=finish_reason,
                usage=Usage(
                    input_tokens=0,  # Not provided in delta
                    output_tokens=usage.get("output_tokens", 0),
                    total_tokens=usage.get("output_tokens", 0),
                ),
            )
        
        # Ignore other chunk types for now
        return None