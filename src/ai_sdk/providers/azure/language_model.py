"""Azure OpenAI language model implementation."""

from __future__ import annotations

from typing import Any, AsyncGenerator, Dict

import httpx

from ...errors import APIError, NetworkError
from ...utils.http import create_http_client
from ...utils.json import secure_json_parse
from ..openai.language_model import OpenAIChatLanguageModel
from ..types import StreamPart


class AzureOpenAIChatLanguageModel(OpenAIChatLanguageModel):
    """Azure OpenAI Chat Completion language model.
    
    This extends the OpenAI chat model with Azure-specific authentication
    and URL handling.
    """
    
    def __init__(
        self,
        provider: Any,  # AzureOpenAIProvider
        deployment_id: str,
        **kwargs: Any,
    ) -> None:
        """Initialize Azure OpenAI language model.
        
        Args:
            provider: Azure OpenAI provider instance
            deployment_id: Azure deployment ID (deployed model name)
            **kwargs: Additional model configuration
        """
        super().__init__(provider, deployment_id, **kwargs)
        self.deployment_id = deployment_id
    
    async def _make_api_call(self, request_body: Dict[str, Any]) -> Dict[str, Any]:
        """Make API call to Azure OpenAI."""
        headers = {
            "api-key": self.provider.api_key,
            "Content-Type": "application/json",
        }
        
        # Construct the URL
        url = self.provider._get_model_url(self.deployment_id, "/chat/completions")
        
        client = create_http_client(
            base_url="",  # URL is complete
            headers=headers,
        )
        
        try:
            async with client:
                response = await client.post(
                    url,
                    json=request_body,
                )
                
                if response.status_code != 200:
                    raise APIError(
                        f"Azure OpenAI API error: {response.status_code}",
                        status_code=response.status_code,
                        response_body=response.text,
                        headers=dict(response.headers),
                    )
                
                return secure_json_parse(response.text, expected_type=dict)
        
        except httpx.RequestError as e:
            raise NetworkError(f"Network error calling Azure OpenAI API: {e}") from e
    
    async def _make_streaming_api_call(
        self,
        request_body: Dict[str, Any],
    ) -> AsyncGenerator[StreamPart, None]:
        """Make streaming API call to Azure OpenAI."""
        headers = {
            "api-key": self.provider.api_key,
            "Content-Type": "application/json",
        }
        
        # Construct the URL  
        url = self.provider._get_model_url(self.deployment_id, "/chat/completions")
        
        client = create_http_client(
            base_url="",  # URL is complete
            headers=headers,
        )
        
        try:
            async with client:
                async with client.stream(
                    "POST",
                    url,
                    json=request_body,
                ) as response:
                    if response.status_code != 200:
                        response_text = await response.aread()
                        raise APIError(
                            f"Azure OpenAI API error: {response.status_code}",
                            status_code=response.status_code,
                            response_body=response_text.decode("utf-8"),
                            headers=dict(response.headers),
                        )
                    
                    # Process SSE stream
                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        
                        if line.startswith("data: "):
                            data = line[6:]  # Remove "data: " prefix
                            
                            if data == "[DONE]":
                                break
                            
                            try:
                                chunk_data = secure_json_parse(data, expected_type=dict)
                                
                                # Process chunk similar to OpenAI format
                                if "choices" in chunk_data and chunk_data["choices"]:
                                    choice = chunk_data["choices"][0]
                                    
                                    if "delta" in choice:
                                        delta = choice["delta"]
                                        
                                        if "content" in delta and delta["content"]:
                                            from ..types import TextDelta
                                            yield TextDelta(text=delta["content"])
                                        
                                        # Handle finish reason
                                        if choice.get("finish_reason"):
                                            from ..types import FinishEvent, FinishReason, Usage, ProviderMetadata
                                            
                                            # Map finish reasons
                                            finish_reason_map = {
                                                "stop": FinishReason.STOP,
                                                "length": FinishReason.LENGTH,
                                                "tool_calls": FinishReason.TOOL_CALLS,
                                                "content_filter": FinishReason.CONTENT_FILTER,
                                            }
                                            
                                            finish_reason = finish_reason_map.get(
                                                choice["finish_reason"],
                                                FinishReason.OTHER,
                                            )
                                            
                                            # Extract usage if available
                                            usage = None
                                            if "usage" in chunk_data:
                                                usage_data = chunk_data["usage"]
                                                usage = Usage(
                                                    prompt_tokens=usage_data.get("prompt_tokens", 0),
                                                    completion_tokens=usage_data.get("completion_tokens", 0),
                                                    total_tokens=usage_data.get("total_tokens", 0),
                                                )
                                            
                                            yield FinishEvent(
                                                finish_reason=finish_reason,
                                                usage=usage,
                                                provider_metadata=ProviderMetadata(
                                                    provider_name="azure",
                                                    model_id=self.deployment_id,
                                                ),
                                            )
                                            
                            except Exception:
                                # Skip invalid JSON chunks
                                continue
        
        except httpx.RequestError as e:
            raise NetworkError(f"Network error calling Azure OpenAI API: {e}") from e