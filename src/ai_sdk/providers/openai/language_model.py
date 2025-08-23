"""OpenAI language model implementation."""

from __future__ import annotations

import json
from typing import Any, AsyncGenerator, Dict, List, Optional

import httpx

from ...errors import APIError, InvalidResponseError, NetworkError
from ...utils.http import create_http_client
from ...utils.json import secure_json_parse
from ..base import LanguageModel, Provider
from ..types import (
    Content,
    FinishReason,
    GenerateOptions,
    GenerateResult,
    Message,
    ProviderMetadata,
    StreamOptions,
    StreamPart,
    TextContent,
    TextDelta,
    Usage,
)


class OpenAIChatLanguageModel(LanguageModel):
    """OpenAI Chat Completion language model."""
    
    def __init__(
        self,
        provider: Provider,
        model_id: str,
        **kwargs: Any,
    ) -> None:
        """Initialize OpenAI language model.
        
        Args:
            provider: OpenAI provider instance
            model_id: OpenAI model ID
            **kwargs: Additional model configuration
        """
        super().__init__(provider, model_id, **kwargs)
    
    async def generate(self, options: GenerateOptions) -> GenerateResult:
        """Generate text using OpenAI Chat Completions API.
        
        Args:
            options: Generation options
            
        Returns:
            Generation result
        """
        # Convert options to OpenAI format
        request_body = self._convert_options_to_request(options, stream=False)
        
        # Make API call
        response_data = await self._make_api_call(request_body)
        
        # Convert response to our format
        return self._convert_response_to_result(response_data)
    
    async def stream(self, options: StreamOptions) -> AsyncGenerator[StreamPart, None]:
        """Stream text generation using OpenAI Chat Completions API.
        
        Args:
            options: Streaming options
            
        Yields:
            Stream parts
        """
        # Convert options to OpenAI format
        request_body = self._convert_options_to_request(options, stream=True)
        
        # Make streaming API call
        async for part in self._make_streaming_api_call(request_body):
            yield part
    
    def _convert_options_to_request(
        self,
        options: GenerateOptions,
        stream: bool = False,
    ) -> Dict[str, Any]:
        """Convert GenerateOptions to OpenAI request format."""
        # Convert messages
        messages = []
        for msg in options.messages:
            if isinstance(msg.content, str):
                messages.append({
                    "role": msg.role,
                    "content": msg.content,
                })
            else:
                # Handle multi-content messages (images, etc.)
                content_parts = []
                for content_part in msg.content:
                    if content_part.type == "text":
                        content_parts.append({
                            "type": "text",
                            "text": content_part.text,
                        })
                    elif content_part.type == "image":
                        content_parts.append({
                            "type": "image_url",
                            "image_url": {
                                "url": content_part.image,
                            },
                        })
                messages.append({
                    "role": msg.role,
                    "content": content_parts,
                })
        
        # Build request body
        request_body = {
            "model": self.model_id,
            "messages": messages,
            "stream": stream,
        }
        
        # Add optional parameters
        if options.max_tokens is not None:
            request_body["max_tokens"] = options.max_tokens
        if options.temperature is not None:
            request_body["temperature"] = options.temperature
        if options.top_p is not None:
            request_body["top_p"] = options.top_p
        if options.frequency_penalty is not None:
            request_body["frequency_penalty"] = options.frequency_penalty
        if options.presence_penalty is not None:
            request_body["presence_penalty"] = options.presence_penalty
        if options.stop is not None:
            request_body["stop"] = options.stop
        if options.seed is not None:
            request_body["seed"] = options.seed
        
        # Handle tools if provided
        if options.tools:
            request_body["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters,
                    },
                }
                for tool in options.tools
            ]
            if options.tool_choice:
                request_body["tool_choice"] = options.tool_choice
        
        # Add extra body parameters
        if options.extra_body:
            request_body.update(options.extra_body)
        
        return request_body
    
    async def _make_api_call(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """Make API call to OpenAI."""
        headers = {
            "Authorization": f"Bearer {self.provider.api_key}",
        }
        
        if hasattr(self.provider, 'organization') and self.provider.organization:
            headers["OpenAI-Organization"] = self.provider.organization
        
        client = create_http_client(
            base_url=getattr(self.provider, 'base_url', 'https://api.openai.com/v1'),
            headers=headers,
        )
        
        try:
            async with client:
                response = await client.post(
                    "/chat/completions",
                    json=request_body,
                )
                
                if response.status_code != 200:
                    raise APIError(
                        f"OpenAI API error: {response.status_code}",
                        status_code=response.status_code,
                        response_body=response.text,
                        headers=dict(response.headers),
                    )
                
                return secure_json_parse(response.text, expected_type=dict)
        
        except httpx.RequestError as e:
            raise NetworkError(f"Network error calling OpenAI API: {e}") from e
    
    async def _make_streaming_api_call(
        self,
        request_body: Dict[str, Any],
    ) -> AsyncGenerator[StreamPart, None]:
        """Make streaming API call to OpenAI."""
        headers = {
            "Authorization": f"Bearer {self.provider.api_key}",
        }
        
        if hasattr(self.provider, 'organization') and self.provider.organization:
            headers["OpenAI-Organization"] = self.provider.organization
        
        client = create_http_client(
            base_url=getattr(self.provider, 'base_url', 'https://api.openai.com/v1'),
            headers=headers,
        )
        
        try:
            async with client:
                async with client.stream(
                    "POST",
                    "/chat/completions",
                    json=request_body,
                ) as response:
                    if response.status_code != 200:
                        response_text = await response.aread()
                        raise APIError(
                            f"OpenAI API error: {response.status_code}",
                            status_code=response.status_code,
                            response_body=response_text.decode(),
                            headers=dict(response.headers),
                        )
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data_part = line[6:]  # Remove "data: " prefix
                            
                            if data_part.strip() == "[DONE]":
                                break
                            
                            try:
                                chunk_data = json.loads(data_part)
                                stream_part = self._convert_chunk_to_stream_part(chunk_data)
                                if stream_part:
                                    yield stream_part
                            except json.JSONDecodeError:
                                # Skip invalid JSON chunks
                                continue
        
        except httpx.RequestError as e:
            raise NetworkError(f"Network error calling OpenAI API: {e}") from e
    
    def _convert_response_to_result(self, response_data: Dict[str, Any]) -> GenerateResult:
        """Convert OpenAI response to GenerateResult."""
        choice = response_data["choices"][0]
        message = choice["message"]
        
        # Extract content
        content = []
        if "content" in message and message["content"]:
            content.append(TextContent(text=message["content"]))
        
        # Handle tool calls
        if "tool_calls" in message and message["tool_calls"]:
            # TODO: Implement tool call content parsing
            pass
        
        # Extract usage
        usage_data = response_data.get("usage", {})
        usage = Usage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            completion_tokens=usage_data.get("completion_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
        )
        
        # Extract finish reason
        finish_reason_map = {
            "stop": FinishReason.STOP,
            "length": FinishReason.LENGTH,
            "content_filter": FinishReason.CONTENT_FILTER,
            "tool_calls": FinishReason.TOOL_CALLS,
        }
        finish_reason = finish_reason_map.get(
            choice.get("finish_reason"),
            FinishReason.UNKNOWN,
        )
        
        return GenerateResult(
            content=content,
            finish_reason=finish_reason,
            usage=usage,
            provider_metadata=ProviderMetadata(data=response_data),
        )
    
    def _convert_chunk_to_stream_part(
        self,
        chunk_data: Dict[str, Any],
    ) -> Optional[StreamPart]:
        """Convert OpenAI streaming chunk to StreamPart."""
        if "choices" not in chunk_data or not chunk_data["choices"]:
            return None
        
        choice = chunk_data["choices"][0]
        delta = choice.get("delta", {})
        
        # Handle text delta
        if "content" in delta and delta["content"]:
            return TextDelta(text_delta=delta["content"])
        
        # Handle finish
        if choice.get("finish_reason"):
            # TODO: Extract final usage information if available
            return None  # For now, don't yield finish parts
        
        return None