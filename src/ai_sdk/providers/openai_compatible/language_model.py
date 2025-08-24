"""
OpenAI-Compatible Language Model implementation

Supports both chat completions and legacy text completions
"""

import json
from typing import Dict, Any, List, AsyncIterator, Optional, Union
from urllib.parse import urljoin, urlencode

from ..base import LanguageModel
from ...core.generate_text import GenerateTextResult
from ...core.step import Step, StepResult
from ...streaming.base import StreamingTextResult, TextStreamChunk
from ...utils.http import make_request
from .types import OpenAICompatibleConfig, OpenAICompatibleChatModelId
from .errors import as_openai_compatible_error


class OpenAICompatibleChatLanguageModel(LanguageModel):
    """OpenAI-Compatible chat language model"""
    
    def __init__(self, model_id: OpenAICompatibleChatModelId, config: OpenAICompatibleConfig):
        self.model_id = model_id
        self.config = config
    
    @property
    def provider(self) -> str:
        return self.config.provider
    
    def _get_url(self, path: str) -> str:
        """Build full URL with query parameters"""
        base_url = f"{self.config.base_url.rstrip('/')}{path}"
        if self.config.fetch is None:  # Only add query params for default HTTP client
            query_params = getattr(self.config, 'query_params', None)
            if query_params:
                separator = '&' if '?' in base_url else '?'
                return f"{base_url}{separator}{urlencode(query_params)}"
        return base_url
    
    def _prepare_request_body(self, step: Step, stream: bool = False) -> Dict[str, Any]:
        """Prepare OpenAI-compatible request body"""
        
        # Convert step messages to OpenAI format
        messages = []
        for message in step.messages:
            if message.role == "user":
                if isinstance(message.content, str):
                    messages.append({"role": "user", "content": message.content})
                else:
                    # Handle multimodal content
                    content = []
                    for part in message.content:
                        if part.get("type") == "text":
                            content.append({"type": "text", "text": part["text"]})
                        elif part.get("type") == "image":
                            content.append({
                                "type": "image_url",
                                "image_url": {"url": part["image"]}
                            })
                    messages.append({"role": "user", "content": content})
            else:
                messages.append({
                    "role": message.role,
                    "content": message.content
                })
        
        # Build request body
        body = {
            "model": self.model_id,
            "messages": messages,
            "stream": stream
        }
        
        # Add optional parameters
        if step.max_tokens is not None:
            body["max_tokens"] = step.max_tokens
        if step.temperature is not None:
            body["temperature"] = step.temperature
        if step.top_p is not None:
            body["top_p"] = step.top_p
        if step.frequency_penalty is not None:
            body["frequency_penalty"] = step.frequency_penalty
        if step.presence_penalty is not None:
            body["presence_penalty"] = step.presence_penalty
        if step.stop_sequences:
            body["stop"] = step.stop_sequences
        
        # Add tools if present
        if step.tools:
            tools = []
            for tool in step.tools:
                tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters
                    }
                })
            body["tools"] = tools
            
        return body
    
    async def generate(self, step: Step) -> StepResult:
        """Generate text using OpenAI-compatible API"""
        try:
            url = self._get_url("/v1/chat/completions")
            headers = self.config.headers()
            headers.update({
                "Content-Type": "application/json",
            })
            
            body = self._prepare_request_body(step, stream=False)
            
            response_data = await make_request(
                url=url,
                method="POST",
                headers=headers,
                json=body,
                http_client=self.config.fetch
            )
            
            # Extract response
            choice = response_data["choices"][0]
            message = choice["message"]
            
            result = StepResult(
                text=message.get("content", ""),
                finish_reason=choice.get("finish_reason"),
                usage=response_data.get("usage", {}),
                response_metadata={
                    "model": response_data.get("model", self.model_id),
                    "id": response_data.get("id"),
                    "created": response_data.get("created"),
                }
            )
            
            # Handle tool calls
            if message.get("tool_calls"):
                result.tool_calls = []
                for tool_call in message["tool_calls"]:
                    result.tool_calls.append({
                        "id": tool_call["id"],
                        "name": tool_call["function"]["name"],
                        "arguments": json.loads(tool_call["function"]["arguments"])
                    })
            
            return result
            
        except Exception as error:
            raise as_openai_compatible_error(error, self.config.provider)
    
    async def stream(self, step: Step) -> AsyncIterator[TextStreamChunk]:
        """Stream text generation using OpenAI-compatible API"""
        try:
            url = self._get_url("/v1/chat/completions")
            headers = self.config.headers()
            headers.update({
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache",
            })
            
            body = self._prepare_request_body(step, stream=True)
            
            async for chunk_data in self._stream_request(url, headers, body):
                if chunk_data.get("choices"):
                    choice = chunk_data["choices"][0]
                    delta = choice.get("delta", {})
                    
                    if delta.get("content"):
                        yield TextStreamChunk(
                            type="text-delta",
                            text_delta=delta["content"]
                        )
                    
                    if choice.get("finish_reason"):
                        yield TextStreamChunk(
                            type="finish",
                            finish_reason=choice["finish_reason"]
                        )
                    
                    # Handle streaming tool calls
                    if delta.get("tool_calls"):
                        for tool_call in delta["tool_calls"]:
                            if tool_call.get("function", {}).get("name"):
                                yield TextStreamChunk(
                                    type="tool-call-start",
                                    tool_call_id=tool_call["id"],
                                    tool_name=tool_call["function"]["name"]
                                )
                            
                            if tool_call.get("function", {}).get("arguments"):
                                yield TextStreamChunk(
                                    type="tool-call-delta",
                                    tool_call_id=tool_call["id"],
                                    arguments_delta=tool_call["function"]["arguments"]
                                )
            
        except Exception as error:
            raise as_openai_compatible_error(error, self.config.provider)
    
    async def _stream_request(self, url: str, headers: Dict[str, str], body: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        """Handle streaming HTTP request with SSE parsing"""
        
        # For now, use a simplified streaming implementation
        # In a full implementation, this would handle SSE parsing properly
        response_data = await make_request(
            url=url,
            method="POST", 
            headers=headers,
            json=body,
            http_client=self.config.fetch
        )
        
        # Simulate streaming from non-streaming response
        if response_data.get("choices"):
            choice = response_data["choices"][0]
            message = choice["message"]
            content = message.get("content", "")
            
            # Yield content in chunks
            chunk_size = 20
            for i in range(0, len(content), chunk_size):
                chunk = content[i:i + chunk_size]
                yield {
                    "choices": [{
                        "delta": {"content": chunk},
                        "finish_reason": None
                    }]
                }
            
            # Final chunk with finish reason
            yield {
                "choices": [{
                    "delta": {},
                    "finish_reason": choice.get("finish_reason", "stop")
                }]
            }


class OpenAICompatibleCompletionLanguageModel(LanguageModel):
    """OpenAI-Compatible completion language model (legacy text completion)"""
    
    def __init__(self, model_id: str, config: OpenAICompatibleConfig):
        self.model_id = model_id
        self.config = config
    
    @property  
    def provider(self) -> str:
        return self.config.provider
    
    def _get_url(self, path: str) -> str:
        """Build full URL with query parameters"""
        base_url = f"{self.config.base_url.rstrip('/')}{path}"
        if self.config.fetch is None:
            query_params = getattr(self.config, 'query_params', None)
            if query_params:
                separator = '&' if '?' in base_url else '?'
                return f"{base_url}{separator}{urlencode(query_params)}"
        return base_url
    
    def _prepare_request_body(self, step: Step, stream: bool = False) -> Dict[str, Any]:
        """Prepare completion request body"""
        
        # Convert messages to prompt text
        prompt = ""
        for message in step.messages:
            if message.role == "user":
                prompt += f"User: {message.content}\n"
            elif message.role == "assistant":
                prompt += f"Assistant: {message.content}\n"
            elif message.role == "system":
                prompt = f"System: {message.content}\n{prompt}"
        
        prompt += "Assistant: "
        
        body = {
            "model": self.model_id,
            "prompt": prompt,
            "stream": stream
        }
        
        # Add optional parameters
        if step.max_tokens is not None:
            body["max_tokens"] = step.max_tokens
        if step.temperature is not None:
            body["temperature"] = step.temperature
        if step.top_p is not None:
            body["top_p"] = step.top_p
        if step.frequency_penalty is not None:
            body["frequency_penalty"] = step.frequency_penalty
        if step.presence_penalty is not None:
            body["presence_penalty"] = step.presence_penalty
        if step.stop_sequences:
            body["stop"] = step.stop_sequences
            
        return body
    
    async def generate(self, step: Step) -> StepResult:
        """Generate text using legacy completions endpoint"""
        try:
            url = self._get_url("/v1/completions")
            headers = self.config.headers()
            headers.update({
                "Content-Type": "application/json",
            })
            
            body = self._prepare_request_body(step, stream=False)
            
            response_data = await make_request(
                url=url,
                method="POST",
                headers=headers,
                json=body,
                http_client=self.config.fetch
            )
            
            # Extract response
            choice = response_data["choices"][0]
            
            return StepResult(
                text=choice.get("text", ""),
                finish_reason=choice.get("finish_reason"),
                usage=response_data.get("usage", {}),
                response_metadata={
                    "model": response_data.get("model", self.model_id),
                    "id": response_data.get("id"),
                    "created": response_data.get("created"),
                }
            )
            
        except Exception as error:
            raise as_openai_compatible_error(error, self.config.provider)
    
    async def stream(self, step: Step) -> AsyncIterator[TextStreamChunk]:
        """Stream text completion"""
        try:
            url = self._get_url("/v1/completions")
            headers = self.config.headers()
            headers.update({
                "Content-Type": "application/json",
                "Accept": "text/event-stream",
                "Cache-Control": "no-cache",
            })
            
            body = self._prepare_request_body(step, stream=True)
            
            async for chunk_data in self._stream_request(url, headers, body):
                if chunk_data.get("choices"):
                    choice = chunk_data["choices"][0]
                    
                    if choice.get("text"):
                        yield TextStreamChunk(
                            type="text-delta",
                            text_delta=choice["text"]
                        )
                    
                    if choice.get("finish_reason"):
                        yield TextStreamChunk(
                            type="finish",
                            finish_reason=choice["finish_reason"]
                        )
            
        except Exception as error:
            raise as_openai_compatible_error(error, self.config.provider)
    
    async def _stream_request(self, url: str, headers: Dict[str, str], body: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        """Handle streaming HTTP request with SSE parsing"""
        
        # Simplified implementation - in practice would handle proper SSE
        response_data = await make_request(
            url=url,
            method="POST",
            headers=headers,
            json=body,
            http_client=self.config.fetch
        )
        
        # Simulate streaming
        if response_data.get("choices"):
            choice = response_data["choices"][0]
            text = choice.get("text", "")
            
            # Yield content in chunks
            chunk_size = 20
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i + chunk_size]
                yield {
                    "choices": [{
                        "text": chunk,
                        "finish_reason": None
                    }]
                }
            
            # Final chunk
            yield {
                "choices": [{
                    "text": "",
                    "finish_reason": choice.get("finish_reason", "stop")
                }]
            }