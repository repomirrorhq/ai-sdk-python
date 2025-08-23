"""
Cerebras Language Model implementation.
"""

import json
import asyncio
from typing import Any, Dict, List, Optional, AsyncIterator, Union
import httpx
from pydantic import BaseModel

from ...providers.types import (
    Message, 
    Content,
    FinishReason,
    Usage,
    StreamPart,
    TextPart,
    ToolCallPart,
    ToolResultPart,
    FinishPart
)
from ...providers.base import LanguageModel
from ...utils.http import create_http_client
from ...utils.json import parse_json_chunk
from ...errors.base import APIError, InvalidArgumentError
from .types import CerebrasChatModelId, CerebrasProviderSettings, get_model_info


class CerebrasLanguageModel(LanguageModel):
    """
    Cerebras language model implementation using OpenAI-compatible API.
    
    Features:
    - Ultra-fast inference with Cerebras specialized hardware
    - Streaming support for real-time responses  
    - Tool calling capabilities
    - JSON mode support
    - Llama models optimized for speed
    """
    
    def __init__(self, model_id: CerebrasChatModelId, settings: CerebrasProviderSettings):
        self.model_id = model_id
        self.settings = settings
        self.model_info = get_model_info(model_id)
        self._provider_name = "cerebras"
    
    @property
    def provider(self) -> str:
        return self._provider_name
    
    def _prepare_headers(self) -> Dict[str, str]:
        """Prepare headers for API requests."""
        headers = {
            "Authorization": f"Bearer {self.settings.api_key}",
            "Content-Type": "application/json",
        }
        headers.update(self.settings.headers)
        return headers
    
    def _convert_messages(self, messages: List[Message]) -> List[Dict[str, Any]]:
        """Convert AI SDK messages to OpenAI format."""
        converted = []
        
        for msg in messages:
            if msg.role == "system":
                converted.append({
                    "role": "system",
                    "content": self._convert_content(msg.content)
                })
            elif msg.role == "user":
                converted.append({
                    "role": "user", 
                    "content": self._convert_content(msg.content)
                })
            elif msg.role == "assistant":
                assistant_msg = {"role": "assistant"}
                
                if isinstance(msg.content, str):
                    assistant_msg["content"] = msg.content
                elif isinstance(msg.content, list):
                    # Handle mixed content with text and tool calls
                    text_parts = []
                    tool_calls = []
                    
                    for content in msg.content:
                        if isinstance(content, dict):
                            if content.get("type") == "text":
                                text_parts.append(content.get("text", ""))
                            elif content.get("type") == "tool-call":
                                tool_calls.append({
                                    "id": content.get("toolCallId"),
                                    "type": "function",
                                    "function": {
                                        "name": content.get("toolName"),
                                        "arguments": json.dumps(content.get("args", {}))
                                    }
                                })
                    
                    if text_parts:
                        assistant_msg["content"] = " ".join(text_parts)
                    if tool_calls:
                        assistant_msg["tool_calls"] = tool_calls
                
                converted.append(assistant_msg)
            elif msg.role == "tool":
                # Handle tool result messages
                converted.append({
                    "role": "tool",
                    "content": str(msg.content),
                    "tool_call_id": getattr(msg, "toolCallId", "unknown")
                })
        
        return converted
    
    def _convert_content(self, content: Union[str, List[Content]]) -> str:
        """Convert content to string format."""
        if isinstance(content, str):
            return content
        elif isinstance(content, list):
            text_parts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                elif isinstance(item, str):
                    text_parts.append(item)
            return " ".join(text_parts)
        return str(content)
    
    def _parse_tool_calls(self, tool_calls: List[Dict[str, Any]]) -> List[ToolCallPart]:
        """Parse tool calls from API response."""
        result = []
        
        for tool_call in tool_calls:
            function = tool_call.get("function", {})
            try:
                args = json.loads(function.get("arguments", "{}"))
            except json.JSONDecodeError:
                args = {}
            
            result.append(ToolCallPart(
                type="tool-call",
                toolCallId=tool_call.get("id", ""),
                toolName=function.get("name", ""),
                args=args
            ))
        
        return result
    
    def _map_finish_reason(self, reason: Optional[str]) -> FinishReason:
        """Map OpenAI finish reason to AI SDK format."""
        if reason == "stop":
            return "stop"
        elif reason == "length":
            return "length"
        elif reason == "tool_calls":
            return "tool-calls"
        elif reason == "content_filter":
            return "content-filter"
        else:
            return "unknown"
    
    async def generate(
        self,
        messages: List[Message],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        seed: Optional[int] = None,
        response_format: Optional[Dict[str, Any]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        **kwargs
    ) -> AsyncIterator[StreamPart]:
        """Generate text using Cerebras API."""
        
        # Prepare request payload
        payload = {
            "model": self.model_id,
            "messages": self._convert_messages(messages),
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
        if seed is not None:
            payload["seed"] = seed
        if response_format is not None:
            payload["response_format"] = response_format
        if tools is not None:
            payload["tools"] = tools
        if tool_choice is not None:
            payload["tool_choice"] = tool_choice
        
        # Add any additional provider-specific options
        payload.update(kwargs)
        
        try:
            async with create_http_client(
                timeout=self.settings.timeout,
                max_retries=self.settings.max_retries
            ) as client:
                async with client.stream(
                    "POST",
                    f"{self.settings.base_url}/chat/completions",
                    headers=self._prepare_headers(),
                    json=payload
                ) as response:
                    if response.status_code != 200:
                        error_text = await response.aread()
                        raise APIError(
                            f"Cerebras API error {response.status_code}: {error_text.decode()}"
                        )
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            chunk = line[6:]  # Remove "data: " prefix
                            
                            if chunk.strip() == "[DONE]":
                                break
                            
                            try:
                                data = json.loads(chunk)
                                async for result in self._process_chunk(data):
                                    yield result
                            except json.JSONDecodeError:
                                continue  # Skip invalid JSON chunks
        
        except httpx.HTTPError as e:
            raise APIError(f"HTTP error occurred: {str(e)}")
        except Exception as e:
            raise APIError(f"Unexpected error: {str(e)}")
    
    def _process_chunk(self, data: Dict[str, Any]) -> AsyncIterator[StreamPart]:
        """Process a single chunk from the streaming response."""
        choices = data.get("choices", [])
        
        for choice in choices:
            delta = choice.get("delta", {})
            finish_reason = choice.get("finish_reason")
            
            # Handle text content
            if "content" in delta and delta["content"] is not None:
                yield TextPart(
                    type="text-delta",
                    textDelta=delta["content"]
                )
            
            # Handle tool calls
            if "tool_calls" in delta:
                tool_calls = self._parse_tool_calls(delta["tool_calls"])
                for tool_call in tool_calls:
                    yield tool_call
            
            # Handle finish
            if finish_reason is not None:
                # Extract usage information
                usage_info = data.get("usage", {})
                usage = Usage(
                    promptTokens=usage_info.get("prompt_tokens", 0),
                    completionTokens=usage_info.get("completion_tokens", 0),
                    totalTokens=usage_info.get("total_tokens", 0)
                )
                
                # Extract model information
                response_model = data.get("model", self.model_id)
                
                # Create provider metadata
                provider_metadata = {
                    "cerebras": {
                        "model": response_model,
                        "finish_reason": finish_reason,
                        "hardware": "cerebras_wse",
                        "inference_speed": self.model_info.get("inference_speed", "ultra_fast")
                    }
                }
                
                yield FinishPart(
                    type="finish",
                    finishReason=self._map_finish_reason(finish_reason),
                    usage=usage,
                    providerMetadata=provider_metadata
                )
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about this model."""
        return {
            "model_id": self.model_id,
            "provider": self.provider,
            **self.model_info
        }