"""Together AI provider implementation.

This module provides integration with Together AI's platform for accessing
100+ open-source AI models including LLaMA, Mixtral, and specialized models.
"""

from typing import Optional, Dict, Any, List, Union, AsyncIterator
import os
import httpx
from ..providers.base import Provider, LanguageModel, EmbeddingModel
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


class TogetherAIChatLanguageModel(LanguageModel):
    """Together AI chat language model implementation."""
    
    def __init__(
        self,
        model_id: str,
        api_key: Optional[str] = None,
        base_url: str = "https://api.together.xyz/v1",
        max_retries: int = 2,
        timeout: float = 60.0,
        extra_headers: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        """Initialize Together AI chat language model.
        
        Args:
            model_id: Model identifier (e.g., 'meta-llama/Llama-3.3-70B-Instruct-Turbo')
            api_key: Together AI API key (if not provided, will use TOGETHER_API_KEY env var)
            base_url: Base URL for Together AI API
            max_retries: Maximum number of retries for failed requests
            timeout: Request timeout in seconds
            extra_headers: Additional headers to include in requests
            **kwargs: Additional arguments
        """
        self.model_id = model_id
        self.api_key = api_key or os.getenv("TOGETHER_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self.timeout = timeout
        self.extra_headers = extra_headers or {}
        
        if not self.api_key:
            raise InvalidArgumentError("Together AI API key is required. Set TOGETHER_API_KEY environment variable or pass api_key parameter.")
        
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

    def _convert_messages_to_together_format(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Convert AI SDK messages to Together AI format."""
        together_messages = []
        
        for message in messages:
            if message.role == "system":
                together_messages.append({
                    "role": "system",
                    "content": message.content
                })
            elif message.role == "user":
                if isinstance(message.content, str):
                    together_messages.append({
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
                    
                    together_messages.append({
                        "role": "user",
                        "content": content_parts
                    })
            elif message.role == "assistant":
                together_messages.append({
                    "role": "assistant",
                    "content": message.content
                })
        
        return together_messages

    def _map_finish_reason(self, together_reason: Optional[str]) -> Optional[FinishReason]:
        """Map Together AI finish reason to AI SDK format."""
        if together_reason is None:
            return None
        
        mapping = {
            "stop": FinishReason.STOP,
            "length": FinishReason.LENGTH,
            "function_call": FinishReason.TOOL_CALLS,
            "tool_calls": FinishReason.TOOL_CALLS,
            "content_filter": FinishReason.CONTENT_FILTER,
        }
        
        return mapping.get(together_reason, FinishReason.OTHER)

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
        """Generate text using Together AI API."""
        
        # Build request payload
        payload = {
            "model": self.model_id,
            "messages": self._convert_messages_to_together_format(messages),
        }
        
        # Add optional parameters
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if temperature is not None:
            payload["temperature"] = temperature
        if top_p is not None:
            payload["top_p"] = top_p
        if top_k is not None:
            payload["top_k"] = top_k
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if stop_sequences:
            payload["stop"] = stop_sequences
        if seed is not None:
            payload["seed"] = seed
            
        # Add Together AI-specific parameters
        for key, value in kwargs.items():
            if key in ['safety_model', 'repetition_penalty', 'min_p', 'echo']:
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
                raise APIError(f"Together AI API error: {data['error']['message']}", status_code=response.status_code)
            
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
                f"Together AI API request failed: {error_detail}",
                status_code=e.response.status_code
            )
        except Exception as e:
            raise APIError(f"Together AI API request failed: {str(e)}")

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
        """Stream text generation using Together AI API."""
        
        # Build request payload
        payload = {
            "model": self.model_id,
            "messages": self._convert_messages_to_together_format(messages),
            "stream": True,
        }
        
        # Add optional parameters
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if temperature is not None:
            payload["temperature"] = temperature
        if top_p is not None:
            payload["top_p"] = top_p
        if top_k is not None:
            payload["top_k"] = top_k
        if frequency_penalty is not None:
            payload["frequency_penalty"] = frequency_penalty
        if presence_penalty is not None:
            payload["presence_penalty"] = presence_penalty
        if stop_sequences:
            payload["stop"] = stop_sequences
        if seed is not None:
            payload["seed"] = seed
            
        # Add Together AI-specific parameters
        for key, value in kwargs.items():
            if key in ['safety_model', 'repetition_penalty', 'min_p', 'echo']:
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
                                raise APIError(f"Together AI API error: {data['error']['message']}")
                            
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
                f"Together AI API streaming request failed: {error_detail}",
                status_code=e.response.status_code
            )
        except Exception as e:
            raise APIError(f"Together AI API streaming request failed: {str(e)}")


class TogetherAIEmbeddingModel(EmbeddingModel):
    """Together AI embedding model implementation."""
    
    def __init__(
        self,
        model_id: str,
        api_key: Optional[str] = None,
        base_url: str = "https://api.together.xyz/v1",
        max_retries: int = 2,
        timeout: float = 60.0,
        extra_headers: Optional[Dict[str, str]] = None,
        max_parallel: int = 4,
        max_batch_size: int = 100,
        **kwargs
    ):
        """Initialize Together AI embedding model.
        
        Args:
            model_id: Model identifier (e.g., 'togethercomputer/m2-bert-80M-8k-retrieval')
            api_key: Together AI API key
            base_url: Base URL for Together AI API
            max_retries: Maximum number of retries for failed requests
            timeout: Request timeout in seconds
            extra_headers: Additional headers to include in requests
            max_parallel: Maximum parallel requests for embed_many
            max_batch_size: Maximum batch size per request
            **kwargs: Additional arguments
        """
        self.model_id = model_id
        self.api_key = api_key or os.getenv("TOGETHER_API_KEY")
        self.base_url = base_url.rstrip("/")
        self.max_retries = max_retries
        self.timeout = timeout
        self.extra_headers = extra_headers or {}
        self.max_parallel = max_parallel
        self.max_batch_size = max_batch_size
        
        if not self.api_key:
            raise InvalidArgumentError("Together AI API key is required.")
        
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

    async def do_embed(
        self,
        values: Union[str, List[str]],
        **kwargs
    ) -> List[List[float]]:
        """Generate embeddings for input text(s).
        
        Args:
            values: Text(s) to embed
            **kwargs: Additional parameters
            
        Returns:
            List of embedding vectors
        """
        # Ensure values is a list
        if isinstance(values, str):
            values = [values]
        
        # Build request payload
        payload = {
            "model": self.model_id,
            "input": values,
        }
        
        # Add any additional parameters
        for key, value in kwargs.items():
            if key in ['encoding_format', 'dimensions']:
                payload[key] = value
        
        try:
            response = await self.client.post(
                f"{self.base_url}/embeddings",
                headers=self._get_headers(),
                json=payload
            )
            response.raise_for_status()
            
            data = response.json()
            
            if "error" in data:
                raise APIError(f"Together AI API error: {data['error']['message']}", status_code=response.status_code)
            
            # Extract embeddings
            embeddings = []
            for item in data["data"]:
                embeddings.append(item["embedding"])
            
            return embeddings
            
        except httpx.HTTPStatusError as e:
            error_detail = "Unknown error"
            try:
                error_data = e.response.json()
                if "error" in error_data:
                    error_detail = error_data["error"].get("message", str(error_data["error"]))
            except:
                error_detail = e.response.text
            
            raise APIError(
                f"Together AI embedding request failed: {error_detail}",
                status_code=e.response.status_code
            )
        except Exception as e:
            raise APIError(f"Together AI embedding request failed: {str(e)}")


class TogetherAIProvider(Provider):
    """Together AI provider."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = "https://api.together.xyz/v1",
        max_retries: int = 2,
        timeout: float = 60.0,
        extra_headers: Optional[Dict[str, str]] = None
    ):
        """Initialize Together AI provider.
        
        Args:
            api_key: Together AI API key (if not provided, will use TOGETHER_API_KEY env var)
            base_url: Base URL for Together AI API
            max_retries: Maximum number of retries for failed requests
            timeout: Request timeout in seconds
            extra_headers: Additional headers to include in requests
        """
        self.api_key = api_key or os.getenv("TOGETHER_API_KEY")
        self.base_url = base_url
        self.max_retries = max_retries
        self.timeout = timeout
        self.extra_headers = extra_headers or {}
        
        if not self.api_key:
            raise InvalidArgumentError("Together AI API key is required. Set TOGETHER_API_KEY environment variable or pass api_key parameter.")

    def language_model(self, model_id: str) -> LanguageModel:
        """Create a language model instance.
        
        Popular models:
        
        **Meta LLaMA Models:**
        - meta-llama/Llama-3.3-70B-Instruct-Turbo: Latest LLaMA 3.3 70B
        - meta-llama/Llama-3.1-8B-Instruct-Turbo: Fast LLaMA 3.1 8B
        - meta-llama/Llama-3.1-70B-Instruct-Turbo: LLaMA 3.1 70B
        - meta-llama/Llama-3.1-405B-Instruct-Turbo: Largest LLaMA model
        
        **Mistral Models:**
        - mistralai/Mixtral-8x7B-Instruct-v0.1: Mixtral 8x7B
        - mistralai/Mistral-7B-Instruct-v0.3: Mistral 7B v0.3
        - mistralai/Mixtral-8x22B-Instruct-v0.1: Large Mixtral model
        
        **Google Models:**
        - google/gemma-2-9b-it: Gemma 2 9B instruction-tuned
        - google/gemma-2-27b-it: Gemma 2 27B instruction-tuned
        
        **Other Popular Models:**
        - Qwen/Qwen2.5-7B-Instruct: Qwen 2.5 7B
        - deepseek-ai/deepseek-r1-distill-llama-70b: DeepSeek R1 distilled
        - databricks/dbrx-instruct: Databricks DBRX
        
        Args:
            model_id: The model identifier
            
        Returns:
            LanguageModel instance for text generation
        """
        return TogetherAIChatLanguageModel(
            model_id=model_id,
            api_key=self.api_key,
            base_url=self.base_url,
            max_retries=self.max_retries,
            timeout=self.timeout,
            extra_headers=self.extra_headers
        )

    def embedding_model(self, model_id: str) -> EmbeddingModel:
        """Create an embedding model instance.
        
        Supported models:
        - togethercomputer/m2-bert-80M-8k-retrieval: M2-BERT for retrieval
        - togethercomputer/m2-bert-80M-2k-retrieval: M2-BERT for shorter texts
        - BAAI/bge-large-en-v1.5: BGE large English model
        - BAAI/bge-base-en-v1.5: BGE base English model
        - WhereIsAI/UAE-Large-V1: UAE large model
        - sentence-transformers/msmarco-bert-base-dot-v5: MSMARCO BERT
        
        Args:
            model_id: The embedding model identifier
            
        Returns:
            EmbeddingModel instance for generating embeddings
        """
        return TogetherAIEmbeddingModel(
            model_id=model_id,
            api_key=self.api_key,
            base_url=self.base_url,
            max_retries=self.max_retries,
            timeout=self.timeout,
            extra_headers=self.extra_headers
        )


def create_together(
    api_key: Optional[str] = None,
    base_url: str = "https://api.together.xyz/v1",
    max_retries: int = 2,
    timeout: float = 60.0,
    extra_headers: Optional[Dict[str, str]] = None
) -> TogetherAIProvider:
    """Create a Together AI provider instance.
    
    Args:
        api_key: Together AI API key (if not provided, will use TOGETHER_API_KEY env var)
        base_url: Base URL for Together AI API
        max_retries: Maximum number of retries for failed requests
        timeout: Request timeout in seconds
        extra_headers: Additional headers to include in requests
        
    Returns:
        TogetherAIProvider instance
        
    Example:
        ```python
        from ai_sdk import create_together, generate_text
        
        # Create provider
        together = create_together(api_key="your-together-api-key")
        
        # Generate text
        result = await generate_text(
            model=together.language_model("meta-llama/Llama-3.1-8B-Instruct-Turbo"),
            prompt="Explain the benefits of open-source AI models"
        )
        print(result.text)
        
        # Generate embeddings
        embeddings = await together.embedding_model("BAAI/bge-large-en-v1.5").do_embed([
            "Hello world",
            "How are you?"
        ])
        ```
    """
    return TogetherAIProvider(
        api_key=api_key,
        base_url=base_url,
        max_retries=max_retries,
        timeout=timeout,
        extra_headers=extra_headers
    )