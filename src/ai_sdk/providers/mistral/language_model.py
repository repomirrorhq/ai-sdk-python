"""Mistral language model implementation."""

import json
from typing import AsyncGenerator, Dict, Any, List, Optional, Union, Callable
from pydantic import BaseModel

from ...providers.base import LanguageModel
from ...providers.types import (
    Message, Content, TextContent, ImageContent, ToolCallContent, ToolResultContent,
    FinishReason, Usage
)
from ...errors import APIError
from .types import MistralChatModelId, MistralLanguageModelOptions
from .utils import (
    convert_to_mistral_messages, 
    convert_mistral_finish_reason,
    convert_to_mistral_tools
)


class MistralLanguageModel(LanguageModel):
    """Mistral AI language model implementation."""
    
    def __init__(
        self,
        model_id: MistralChatModelId,
        base_url: str,
        headers: Dict[str, str],
        http_client: Any,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.model_id = model_id
        self.base_url = base_url.rstrip('/')
        self.headers = headers
        self.http_client = http_client
        self.provider = "mistral"
        
    async def generate(
        self,
        messages: List[Message],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        stop: Optional[Union[str, List[str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        response_format: Optional[Dict[str, Any]] = None,
        provider_options: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a single response using Mistral API."""
        
        # Parse provider options
        mistral_options = MistralLanguageModelOptions(**(provider_options or {}))
        
        # Convert messages to Mistral format (OpenAI-compatible)
        mistral_messages = convert_to_mistral_messages(messages)
        
        # Build request payload
        payload = {
            "model": self.model_id,
            "messages": [msg.model_dump() for msg in mistral_messages],
        }
        
        # Add optional parameters
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if temperature is not None:
            payload["temperature"] = temperature
        if top_p is not None:
            payload["top_p"] = top_p
        if stop is not None:
            payload["stop"] = stop if isinstance(stop, list) else [stop]
            
        # Add tools if provided
        if tools:
            mistral_tools = convert_to_mistral_tools(tools)
            payload["tools"] = mistral_tools
            
            if tool_choice:
                if tool_choice == "auto":
                    payload["tool_choice"] = "auto"
                elif tool_choice == "required":
                    payload["tool_choice"] = "any"
                elif tool_choice == "none":
                    payload["tool_choice"] = "none"
                elif isinstance(tool_choice, dict):
                    payload["tool_choice"] = tool_choice
                    
        # Add response format if provided
        if response_format:
            # Check if we should use Mistral's json_schema format
            if (response_format.get("type") == "json" and 
                response_format.get("schema") is not None):
                # Use Mistral's json_schema response format
                payload["response_format"] = {
                    "type": "json_schema",
                    "json_schema": {
                        "schema": response_format["schema"],
                        "strict": response_format.get("strict", False),
                        "name": response_format.get("name", "response"),
                        "description": response_format.get("description")
                    }
                }
            else:
                payload["response_format"] = response_format
            
        # Add Mistral-specific options
        if mistral_options.safe_prompt is not None:
            payload["safe_prompt"] = mistral_options.safe_prompt
        if mistral_options.document_image_limit is not None:
            payload["document_image_limit"] = mistral_options.document_image_limit
        if mistral_options.document_page_limit is not None:
            payload["document_page_limit"] = mistral_options.document_page_limit
            
        # Make API request
        try:
            response = await self.http_client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=self.headers
            )
            
            if response.status_code != 200:
                error_text = response.text
                try:
                    error_data = response.json()
                    message = error_data.get("error", {}).get("message", error_text)
                except:
                    message = error_text
                raise APIError(f"Mistral API error: {message}", status_code=response.status_code)
                
            result = response.json()
            
            # Extract response data
            choice = result["choices"][0]
            message = choice["message"]
            
            content = message.get("content", "")
            tool_calls = []
            
            # Handle tool calls
            if message.get("tool_calls"):
                for tool_call in message["tool_calls"]:
                    tool_calls.append({
                        "id": tool_call["id"],
                        "type": tool_call["type"],
                        "function": {
                            "name": tool_call["function"]["name"],
                            "arguments": tool_call["function"]["arguments"]
                        }
                    })
            
            # Map finish reason
            finish_reason = convert_mistral_finish_reason(choice.get("finish_reason"))
            
            # Extract usage
            usage_info = result.get("usage", {})
            usage = Usage(
                prompt_tokens=usage_info.get("prompt_tokens", 0),
                completion_tokens=usage_info.get("completion_tokens", 0),
                total_tokens=usage_info.get("total_tokens", 0)
            )
            
            return {
                "content": content,
                "tool_calls": tool_calls,
                "finish_reason": finish_reason,
                "usage": usage,
                "raw_response": result
            }
            
        except Exception as e:
            if isinstance(e, APIError):
                raise
            raise APIError(f"Mistral request failed: {str(e)}")
    
    async def stream(
        self,
        messages: List[Message],
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        stop: Optional[Union[str, List[str]]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        response_format: Optional[Dict[str, Any]] = None,
        provider_options: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Stream responses using Mistral API."""
        
        # Parse provider options
        mistral_options = MistralLanguageModelOptions(**(provider_options or {}))
        
        # Convert messages to Mistral format
        mistral_messages = convert_to_mistral_messages(messages)
        
        # Build request payload
        payload = {
            "model": self.model_id,
            "messages": [msg.model_dump() for msg in mistral_messages],
            "stream": True,
        }
        
        # Add optional parameters
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if temperature is not None:
            payload["temperature"] = temperature
        if top_p is not None:
            payload["top_p"] = top_p
        if stop is not None:
            payload["stop"] = stop if isinstance(stop, list) else [stop]
            
        # Add tools if provided
        if tools:
            mistral_tools = convert_to_mistral_tools(tools)
            payload["tools"] = mistral_tools
            
            if tool_choice:
                if tool_choice == "auto":
                    payload["tool_choice"] = "auto"
                elif tool_choice == "required":
                    payload["tool_choice"] = "any"
                elif tool_choice == "none":
                    payload["tool_choice"] = "none"
                elif isinstance(tool_choice, dict):
                    payload["tool_choice"] = tool_choice
                    
        # Add response format if provided
        if response_format:
            # Check if we should use Mistral's json_schema format
            if (response_format.get("type") == "json" and 
                response_format.get("schema") is not None):
                # Use Mistral's json_schema response format
                payload["response_format"] = {
                    "type": "json_schema",
                    "json_schema": {
                        "schema": response_format["schema"],
                        "strict": response_format.get("strict", False),
                        "name": response_format.get("name", "response"),
                        "description": response_format.get("description")
                    }
                }
            else:
                payload["response_format"] = response_format
            
        # Add Mistral-specific options
        if mistral_options.safe_prompt is not None:
            payload["safe_prompt"] = mistral_options.safe_prompt
        if mistral_options.document_image_limit is not None:
            payload["document_image_limit"] = mistral_options.document_image_limit
        if mistral_options.document_page_limit is not None:
            payload["document_page_limit"] = mistral_options.document_page_limit
            
        # Make streaming API request
        try:
            async with self.http_client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=self.headers
            ) as response:
                
                if response.status_code != 200:
                    error_text = await response.aread()
                    try:
                        error_data = json.loads(error_text)
                        message = error_data.get("error", {}).get("message", error_text.decode())
                    except:
                        message = error_text.decode()
                    raise APIError(f"Mistral API error: {message}", status_code=response.status_code)
                
                async for line in response.aiter_lines():
                    line = line.strip()
                    if line.startswith("data: "):
                        data_str = line[6:]
                        
                        if data_str == "[DONE]":
                            break
                            
                        try:
                            data = json.loads(data_str)
                            
                            if "choices" in data and data["choices"]:
                                choice = data["choices"][0]
                                delta = choice.get("delta", {})
                                
                                # Handle content delta
                                if "content" in delta and delta["content"]:
                                    yield {
                                        "type": "content_delta",
                                        "delta": {"text": delta["content"]}
                                    }
                                
                                # Handle tool call deltas
                                if "tool_calls" in delta:
                                    for tool_call in delta["tool_calls"]:
                                        yield {
                                            "type": "tool_call_delta",
                                            "delta": tool_call
                                        }
                                
                                # Handle finish reason
                                if choice.get("finish_reason"):
                                    finish_reason = convert_mistral_finish_reason(choice["finish_reason"])
                                    usage_info = data.get("usage", {})
                                    usage = Usage(
                                        prompt_tokens=usage_info.get("prompt_tokens", 0),
                                        completion_tokens=usage_info.get("completion_tokens", 0),
                                        total_tokens=usage_info.get("total_tokens", 0)
                                    )
                                    yield {
                                        "type": "done",
                                        "finish_reason": finish_reason,
                                        "usage": usage
                                    }
                                    
                        except json.JSONDecodeError:
                            continue
                            
        except Exception as e:
            if isinstance(e, APIError):
                raise
            raise APIError(f"Mistral streaming request failed: {str(e)}")