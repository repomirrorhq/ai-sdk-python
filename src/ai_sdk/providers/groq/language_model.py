"""
Groq Chat Language Model Implementation

Implements the LanguageModel interface for Groq's high-speed chat models.
"""

from __future__ import annotations

import json
import asyncio
from typing import Dict, List, Optional, AsyncIterator, Any, Callable, Union

import httpx

from ...errors import APIError, InvalidArgumentError
from ..base import LanguageModel, StreamingLanguageModel
from ..types import (
    GenerateTextResult, 
    StreamTextResult,
    Message, 
    ToolCall,
    ToolResult,
    FinishReason,
    Usage,
    ProviderMetadata
)
from .types import GroqChatModelId, GroqProviderOptions
from .message_converter import convert_to_groq_messages, convert_from_groq_response
from .api_types import GroqChatCompletionRequest, GroqChatCompletionResponse


class GroqChatLanguageModel(LanguageModel, StreamingLanguageModel):
    """Groq chat language model implementation."""
    
    def __init__(
        self,
        model_id: GroqChatModelId,
        api_key: str,
        base_url: str = "https://api.groq.com/openai/v1",
        headers: Optional[Dict[str, str]] = None,
        fetch_implementation: Optional[Callable] = None,
    ):
        """Initialize Groq chat language model.
        
        Args:
            model_id: The Groq model identifier
            api_key: Groq API key
            base_url: Base URL for Groq API
            headers: Additional headers for requests
            fetch_implementation: Custom fetch implementation
        """
        self.model_id = model_id
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.fetch_implementation = fetch_implementation
        
        # Set up HTTP client
        self._client = httpx.AsyncClient(
            headers=self.headers,
            timeout=httpx.Timeout(60.0)  # 60 second timeout
        )
        
    @property
    def provider_id(self) -> str:
        return "groq"
        
    async def generate_text(
        self,
        messages: List[Message],
        *,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        response_format: Optional[Dict[str, Any]] = None,
        seed: Optional[int] = None,
        user: Optional[str] = None,
        provider_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> GenerateTextResult:
        """Generate text using Groq API.
        
        Args:
            messages: List of conversation messages
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0.0 to 2.0)
            top_p: Nucleus sampling parameter
            frequency_penalty: Frequency penalty (-2.0 to 2.0)
            presence_penalty: Presence penalty (-2.0 to 2.0)
            stop: Stop sequences
            tools: Available tools for function calling
            tool_choice: Tool choice strategy
            response_format: Response format specification
            seed: Random seed for reproducible outputs
            user: User identifier
            **kwargs: Additional provider-specific arguments
            
        Returns:
            GenerateTextResult with the generated text and metadata
        """
        # Parse provider options
        groq_options = GroqProviderOptions(**(provider_options or {}))
        
        # Convert messages to Groq format
        groq_messages = convert_to_groq_messages(messages)
        
        # Build request payload
        request_data = GroqChatCompletionRequest(
            model=self.model_id,
            messages=groq_messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            tools=tools,
            tool_choice=tool_choice,
            response_format=response_format,
            seed=seed,
            user=user or groq_options.user,  # Allow provider option override
            stream=False,
            # Groq-specific provider options
            reasoning_format=groq_options.reasoning_format,
            reasoning_effort=groq_options.reasoning_effort,
            parallel_tool_calls=groq_options.parallel_tool_calls,
            structured_outputs=groq_options.structured_outputs,
            service_tier=groq_options.service_tier,
            **kwargs
        )
        
        # Make API call
        try:
            response = await self._client.post(
                f"{self.base_url}/chat/completions",
                json=request_data.model_dump(exclude_none=True),
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
            response.raise_for_status()
            
            # Parse response
            response_data = GroqChatCompletionResponse.model_validate(response.json())
            
            # Convert to our format
            return convert_from_groq_response(response_data, self.model_id)
            
        except httpx.HTTPStatusError as e:
            error_data = {}
            try:
                error_data = e.response.json()
            except:
                pass
                
            raise APIError(
                f"Groq API error: {e.response.status_code} - {error_data.get('error', {}).get('message', str(e))}",
                status_code=e.response.status_code,
                response_data=error_data
            )
            
        except Exception as e:
            raise APIError(f"Unexpected error calling Groq API: {str(e)}")
            
    async def stream_text(
        self,
        messages: List[Message],
        *,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        response_format: Optional[Dict[str, Any]] = None,
        seed: Optional[int] = None,
        user: Optional[str] = None,
        provider_options: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> StreamTextResult:
        """Stream text generation using Groq API.
        
        Returns:
            StreamTextResult with async iterator of text chunks
        """
        # Parse provider options
        groq_options = GroqProviderOptions(**(provider_options or {}))
        
        # Convert messages to Groq format
        groq_messages = convert_to_groq_messages(messages)
        
        # Build request payload
        request_data = GroqChatCompletionRequest(
            model=self.model_id,
            messages=groq_messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop,
            tools=tools,
            tool_choice=tool_choice,
            response_format=response_format,
            seed=seed,
            user=user or groq_options.user,  # Allow provider option override
            stream=True,
            # Groq-specific provider options
            reasoning_format=groq_options.reasoning_format,
            reasoning_effort=groq_options.reasoning_effort,
            parallel_tool_calls=groq_options.parallel_tool_calls,
            structured_outputs=groq_options.structured_outputs,
            service_tier=groq_options.service_tier,
            **kwargs
        )
        
        async def stream_generator() -> AsyncIterator[str]:
            """Generate streaming text chunks."""
            try:
                async with self._client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    json=request_data.model_dump(exclude_none=True),
                    headers={"Authorization": f"Bearer {self.api_key}"}
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]  # Remove "data: " prefix
                            
                            if data.strip() == "[DONE]":
                                break
                                
                            try:
                                chunk_data = json.loads(data)
                                if "choices" in chunk_data and chunk_data["choices"]:
                                    choice = chunk_data["choices"][0]
                                    if "delta" in choice and "content" in choice["delta"]:
                                        content = choice["delta"]["content"]
                                        if content:
                                            yield content
                            except json.JSONDecodeError:
                                # Skip invalid JSON chunks
                                continue
                                
            except httpx.HTTPStatusError as e:
                error_data = {}
                try:
                    error_data = await e.response.json()
                except:
                    pass
                    
                raise APIError(
                    f"Groq API error: {e.response.status_code} - {error_data.get('error', {}).get('message', str(e))}",
                    status_code=e.response.status_code,
                    response_data=error_data
                )
                
            except Exception as e:
                raise APIError(f"Unexpected error streaming from Groq API: {str(e)}")
        
        return StreamTextResult(
            text_stream=stream_generator(),
            metadata=ProviderMetadata(
                provider_id="groq",
                model_id=self.model_id,
            )
        )
        
    async def __aenter__(self):
        """Async context manager entry."""
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self._client.aclose()