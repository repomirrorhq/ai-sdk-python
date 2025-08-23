"""Groq AI provider implementation.

This module provides integration with Groq's high-speed inference platform,
supporting various open-source models with extremely fast generation speeds.
"""

from typing import Optional, Dict, Any, List, Union, AsyncIterator
import os
import httpx
from ..providers.base import Provider, LanguageModel
from ..providers.types import (
    Message, 
    Content,
    GenerateTextResult,
    StreamTextResult,
    FinishReason,
    Usage,
    ContentPart,
    TextContentPart,
    ImageContentPart
)
from ..errors import APIError, InvalidArgumentError
from ..utils.http import create_http_client
from ..utils.json import parse_json_safely


class GroqChatLanguageModel(LanguageModel):
    """Groq chat language model implementation."""
    
    def __init__(
        self,
        model_id: str,
        api_key: Optional[str] = None,
        base_url: str = "https://api.groq.com/openai/v1",
        max_retries: int = 2,
        timeout: float = 60.0,
        extra_headers: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        """Initialize Groq chat language model.
        
        Args:
            model_id: Model identifier (e.g., 'llama-3.1-8b-instant', 'mixtral-8x7b-32768')
            api_key: Groq API key (if not provided, will use GROQ_API_KEY env var)
            base_url: Base URL for Groq API
            max_retries: Maximum number of retries for failed requests
            timeout: Request timeout in seconds
            extra_headers: Additional headers to include in requests
            **kwargs: Additional arguments
        """
        self.model_id = model_id
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self.timeout = timeout
        self.extra_headers = extra_headers or {}
        
        if not self.api_key:
            raise InvalidArgumentError("Groq API key is required. Set GROQ_API_KEY environment variable or pass api_key parameter.")
        
        # Initialize HTTP client
        self.client = create_http_client(
            timeout=self.timeout,
            max_retries=self.max_retries
        )

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            **self.extra_headers
        }
        return headers

    def _convert_messages_to_groq_format(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Convert AI SDK messages to Groq API format."""
        groq_messages = []
        
        for message in messages:
            if message.role == "system":
                groq_messages.append({
                    "role": "system",
                    "content": message.content
                })
            elif message.role == "user":
                if isinstance(message.content, str):
                    groq_messages.append({
                        "role": "user", 
                        "content": message.content
                    })
                elif isinstance(message.content, list):
                    # Handle multi-modal content
                    content_parts = []
                    for part in message.content:
                        if isinstance(part, TextContentPart):
                            content_parts.append({
                                "type": "text",
                                "text": part.text
                            })
                        elif isinstance(part, ImageContentPart):
                            content_parts.append({
                                "type": "image_url",
                                "image_url": {"url": part.image}
                            })
                    
                    groq_messages.append({
                        "role": "user",
                        "content": content_parts
                    })
            elif message.role == "assistant":
                groq_messages.append({
                    "role": "assistant",
                    "content": message.content
                })
        
        return groq_messages

    def _map_finish_reason(self, groq_reason: Optional[str]) -> Optional[FinishReason]:
        """Map Groq finish reason to AI SDK format."""
        if groq_reason is None:
            return None
        
        mapping = {
            "stop": FinishReason.STOP,
            "length": FinishReason.LENGTH,
            "function_call": FinishReason.TOOL_CALLS,
            "tool_calls": FinishReason.TOOL_CALLS,
            "content_filter": FinishReason.CONTENT_FILTER,
        }
        
        return mapping.get(groq_reason, FinishReason.OTHER)

    async def do_generate(
        self,
        messages: List[Message],
        *,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
        seed: Optional[int] = None,
        **kwargs
    ) -> GenerateTextResult:
        """Generate text using Groq API."""
        
        # Build request payload
        payload = {
            "model": self.model_id,
            "messages": self._convert_messages_to_groq_format(messages),
        }
        
        # Add optional parameters
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if temperature is not None:
            payload["temperature"] = temperature
        if top_p is not None:
            payload["top_p"] = top_p
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if stop_sequences:
            payload["stop"] = stop_sequences
        if seed is not None:
            payload["seed"] = seed
            
        # Add any additional provider-specific parameters
        for key, value in kwargs.items():
            if key in ['parallel_tool_calls', 'user', 'service_tier']:
                payload[key] = value
        
        try:
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                headers=self._get_headers(),
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            
            if "error" in data:
                raise APIError(f"Groq API error: {data['error']['message']}", status_code=response.status_code)
            
            choice = data["choices"][0]
            message = choice["message"]
            
            # Extract usage information
            usage_data = data.get("usage", {})
            usage = Usage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0)
            )
            
            return GenerateTextResult(
                text=message["content"] or "",
                finish_reason=self._map_finish_reason(choice.get("finish_reason")),
                usage=usage,
                response_messages=[
                    Message(role="assistant", content=message["content"] or "")
                ]
            )
            
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                if "error" in error_data:
                    error_detail = error_data["error"].get("message", str(error_data["error"]))
            except:
                error_detail = e.response.text
            
            raise APIError(
                f"Groq API request failed: {error_detail}",
                status_code=e.response.status_code
            )
        except Exception as e:
            raise APIError(f"Groq API request failed: {str(e)}")

    async def do_stream(
        self,
        messages: List[Message],
        *,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop_sequences: Optional[List[str]] = None,
        seed: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[StreamTextResult]:
        """Stream text generation using Groq API."""
        
        # Build request payload
        payload = {
            "model": self.model_id,
            "messages": self._convert_messages_to_groq_format(messages),
            "stream": True,
        }
        
        # Add optional parameters
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if temperature is not None:
            payload["temperature"] = temperature
        if top_p is not None:
            payload["top_p"] = top_p
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if stop_sequences:
            payload["stop"] = stop_sequences
        if seed is not None:
            payload["seed"] = seed
            
        # Add any additional provider-specific parameters
        for key, value in kwargs.items():
            if key in ['parallel_tool_calls', 'user', 'service_tier']:
                payload[key] = value
        
        try:
            async with self.client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=self._get_headers(),
                json=payload
            ) as response:
                response.raise_for_status()
                
                accumulated_usage = Usage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
                
                async for line in response.aiter_lines():
                    line = line.strip()
                    if not line:
                        continue
                    
                    if line.startswith("data: "):
                        data_str = line[6:]
                        
                        if data_str == "[DONE]":
                            break
                        
                        try:
                            data = parse_json_safely(data_str)
                            if not data:
                                continue
                            
                            if "error" in data:
                                raise APIError(f"Groq API error: {data['error']['message']}")
                            
                            # Update usage if present
                            if "usage" in data:
                                usage_data = data["usage"]
                                accumulated_usage = Usage(
                                    prompt_tokens=usage_data.get("prompt_tokens", 0),
                                    completion_tokens=usage_data.get("completion_tokens", 0),
                                    total_tokens=usage_data.get("total_tokens", 0)
                                )
                            
                            if "choices" not in data or not data["choices"]:
                                continue
                            
                            choice = data["choices"][0]
                            
                            if "delta" in choice:
                                delta = choice["delta"]
                                content = delta.get("content", "")
                                
                                if content:
                                    yield StreamTextResult(
                                        text_delta=content,
                                        finish_reason=None,
                                        usage=accumulated_usage
                                    )
                                
                                # Check for finish reason
                                if choice.get("finish_reason"):
                                    yield StreamTextResult(
                                        text_delta="",
                                        finish_reason=self._map_finish_reason(choice["finish_reason"]),
                                        usage=accumulated_usage
                                    )
                        
                        except Exception as e:
                            # Log parse error but continue
                            continue
                            
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                if "error" in error_data:
                    error_detail = error_data["error"].get("message", str(error_data["error"]))
            except:
                error_detail = e.response.text
            
            raise APIError(
                f"Groq API streaming request failed: {error_detail}",
                status_code=e.response.status_code
            )
        except Exception as e:
            raise APIError(f"Groq API streaming request failed: {str(e)}")


class GroqProvider(Provider):
    """Groq AI provider."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.groq.com/openai/v1",
        max_retries: int = 2,
        timeout: float = 60.0,
        extra_headers: Optional[Dict[str, str]] = None
    ):
        """Initialize Groq provider.
        
        Args:
            api_key: Groq API key (if not provided, will use GROQ_API_KEY env var)
            base_url: Base URL for Groq API
            max_retries: Maximum number of retries for failed requests
            timeout: Request timeout in seconds
            extra_headers: Additional headers to include in requests
        """
        self.api_key = api_key or os.getenv("GROQ_API_KEY")
        self.base_url = base_url
        self.max_retries = max_retries
        self.timeout = timeout
        self.extra_headers = extra_headers or {}
        
        if not self.api_key:
            raise InvalidArgumentError("Groq API key is required. Set GROQ_API_KEY environment variable or pass api_key parameter.")

    def language_model(self, model_id: str) -> LanguageModel:
        """Create a language model instance.
        
        Supported models:
        - llama-3.1-8b-instant: Fast 8B Llama 3.1 model
        - llama-3.3-70b-versatile: Versatile 70B Llama 3.3 model  
        - mixtral-8x7b-32768: Mixtral 8x7B with 32K context
        - gemma2-9b-it: Gemma 2 9B instruction-tuned model
        - qwen-2.5-32b: Qwen 2.5 32B model
        - deepseek-r1-distill-llama-70b: DeepSeek R1 distilled model
        
        Args:
            model_id: The model identifier
            
        Returns:
            LanguageModel instance for text generation
        """
        return GroqChatLanguageModel(
            model_id=model_id,
            api_key=self.api_key,
            base_url=self.base_url,
            max_retries=self.max_retries,
            timeout=self.timeout,
            extra_headers=self.extra_headers
        )


def create_groq(
    api_key: Optional[str] = None,
    base_url: str = "https://api.groq.com/openai/v1",
    max_retries: int = 2,
    timeout: float = 60.0,
    extra_headers: Optional[Dict[str, str]] = None
) -> GroqProvider:
    """Create a Groq provider instance.
    
    Args:
        api_key: Groq API key (if not provided, will use GROQ_API_KEY env var)
        base_url: Base URL for Groq API  
        max_retries: Maximum number of retries for failed requests
        timeout: Request timeout in seconds
        extra_headers: Additional headers to include in requests
        
    Returns:
        GroqProvider instance
        
    Example:
        ```python
        from ai_sdk import create_groq, generate_text
        
        # Create provider
        groq = create_groq(api_key="your-groq-api-key")
        
        # Generate text
        result = await generate_text(
            model=groq.language_model("llama-3.1-8b-instant"),
            prompt="Explain quantum computing in simple terms"
        )
        print(result.text)
        ```
    """
    return GroqProvider(
        api_key=api_key,
        base_url=base_url,
        max_retries=max_retries,
        timeout=timeout,
        extra_headers=extra_headers
    )