"""
DeepSeek Language Model implementation.

DeepSeek uses an OpenAI-compatible API with additional reasoning capabilities
and custom metadata extraction for cache hit/miss tracking.
"""

import json
from typing import Any, AsyncGenerator, Dict, List, Optional

from ai_sdk.core.types import (
    LanguageModel,
    ChatPrompt, 
    GenerateTextOptions,
    GenerateTextResult,
    StreamTextOptions,
    TextStreamPart,
    TextStartPart,
    TextDeltaPart,
    FinishPart,
    Usage,
    ResponseMetadata,
    ProviderMetadata
)
from ai_sdk.core.types import TextStreamPart
from ai_sdk.utils.http import make_request, stream_request
from ai_sdk.errors.base import AISDKError
from .types import (
    DeepSeekChatModelId,
    DeepSeekProviderSettings,
    DeepSeekResponse,
    DeepSeekStreamChunk,
    DeepSeekUsage,
    DeepSeekMetadataKeys
)


class DeepSeekLanguageModel(LanguageModel):
    """
    DeepSeek language model implementation.
    
    Features:
    - OpenAI-compatible API with DeepSeek-specific enhancements  
    - Advanced reasoning capabilities with deepseek-reasoner
    - Prompt caching with hit/miss tracking
    - Tool calling support
    - Streaming responses
    """
    
    def __init__(
        self,
        model_id: DeepSeekChatModelId,
        settings: DeepSeekProviderSettings,
    ):
        self.model_id = model_id
        self.settings = settings
        self._provider = "deepseek"
    
    @property
    def provider(self) -> str:
        return self._provider
    
    async def generate_text(
        self,
        prompt: ChatPrompt,
        options: GenerateTextOptions,
    ) -> GenerateTextResult:
        """Generate text using DeepSeek OpenAI-compatible API."""
        
        try:
            # Convert AI SDK format to OpenAI-compatible format
            messages = self._convert_messages(prompt.messages)
            
            # Prepare request body
            request_body = {
                "model": self.model_id,
                "messages": messages,
                "stream": False
            }
            
            # Add optional parameters
            if options.max_output_tokens:
                request_body["max_tokens"] = options.max_output_tokens
            if options.temperature is not None:
                request_body["temperature"] = options.temperature
            if options.top_p is not None:
                request_body["top_p"] = options.top_p
            if options.frequency_penalty is not None:
                request_body["frequency_penalty"] = options.frequency_penalty
            if options.presence_penalty is not None:
                request_body["presence_penalty"] = options.presence_penalty
            if options.stop_sequences:
                request_body["stop"] = options.stop_sequences
            if options.seed is not None:
                request_body["seed"] = options.seed
            
            # Add tools if provided
            if options.tools:
                request_body["tools"] = self._convert_tools(options.tools)
                if options.tool_choice:
                    request_body["tool_choice"] = options.tool_choice
            
            # Add response format if specified
            if options.response_format:
                request_body["response_format"] = options.response_format
            
            # Make API request
            headers = self._get_headers()
            
            response_data = await make_request(
                method="POST",
                url=f"{self.settings.base_url}/chat/completions",
                headers=headers,
                json=request_body,
                timeout=options.request_timeout
            )
            
            response = DeepSeekResponse.model_validate(response_data)
            
            # Extract response content
            choice = response.choices[0] if response.choices else None
            content = choice.message.get("content", "") if choice else ""
            
            # Extract tool calls if present
            tool_calls = []
            if choice and choice.message.get("tool_calls"):
                for tool_call in choice.message["tool_calls"]:
                    tool_calls.append({
                        "id": tool_call["id"],
                        "name": tool_call["function"]["name"],
                        "arguments": tool_call["function"]["arguments"]
                    })
            
            # Convert usage information with DeepSeek-specific metadata
            usage = Usage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens
            )
            
            # Create response metadata
            response_metadata = ResponseMetadata(
                id=response.id,
                model_id=self.model_id,
                timestamp=None
            )
            
            # Create provider metadata with DeepSeek-specific information
            deepseek_metadata = {
                "finish_reason": choice.finish_reason if choice else "unknown",
                "object": response.object,
                "created": response.created,
            }
            
            # Add cache metrics if available
            if response.usage.prompt_cache_hit_tokens is not None:
                deepseek_metadata[DeepSeekMetadataKeys.PROMPT_CACHE_HIT_TOKENS] = response.usage.prompt_cache_hit_tokens
            if response.usage.prompt_cache_miss_tokens is not None:
                deepseek_metadata[DeepSeekMetadataKeys.PROMPT_CACHE_MISS_TOKENS] = response.usage.prompt_cache_miss_tokens
            
            # Extract reasoning content if present (for deepseek-reasoner)
            if self.model_id == "deepseek-reasoner" and choice and choice.message.get("reasoning_content"):
                deepseek_metadata[DeepSeekMetadataKeys.REASONING_CONTENT] = choice.message["reasoning_content"]
            
            provider_metadata = ProviderMetadata(
                deepseek=deepseek_metadata
            )
            
            # Add warnings for unsupported parameters
            warnings = []
            if options.top_k is not None:
                warnings.append("top_k parameter is not supported by DeepSeek")
            
            return GenerateTextResult(
                text=content,
                tool_calls=tool_calls,
                usage=usage,
                finish_reason=self._map_finish_reason(choice.finish_reason if choice else None),
                response_metadata=response_metadata,
                provider_metadata=provider_metadata,
                warnings=warnings if warnings else None
            )
            
        except Exception as e:
            raise AISDKError(f"DeepSeek API error: {str(e)}") from e
    
    async def stream_text(
        self,
        prompt: ChatPrompt,
        options: StreamTextOptions,
    ) -> AsyncGenerator[TextStreamPart, None]:
        """Stream text generation using DeepSeek OpenAI-compatible API."""
        
        try:
            # Convert AI SDK format to OpenAI-compatible format
            messages = self._convert_messages(prompt.messages)
            
            # Prepare request body
            request_body = {
                "model": self.model_id,
                "messages": messages,
                "stream": True
            }
            
            # Add optional parameters
            if options.max_output_tokens:
                request_body["max_tokens"] = options.max_output_tokens
            if options.temperature is not None:
                request_body["temperature"] = options.temperature
            if options.top_p is not None:
                request_body["top_p"] = options.top_p
            if options.frequency_penalty is not None:
                request_body["frequency_penalty"] = options.frequency_penalty
            if options.presence_penalty is not None:
                request_body["presence_penalty"] = options.presence_penalty
            if options.stop_sequences:
                request_body["stop"] = options.stop_sequences
            if options.seed is not None:
                request_body["seed"] = options.seed
            
            # Add tools if provided
            if options.tools:
                request_body["tools"] = self._convert_tools(options.tools)
                if options.tool_choice:
                    request_body["tool_choice"] = options.tool_choice
            
            # Add response format if specified
            if options.response_format:
                request_body["response_format"] = options.response_format
            
            # Make streaming request
            headers = self._get_headers()
            
            stream_started = False
            accumulated_content = ""
            last_response_id = None
            last_usage = None
            tool_calls = []
            deepseek_metadata = {}
            
            async for chunk in stream_request(
                method="POST",
                url=f"{self.settings.base_url}/chat/completions",
                headers=headers,
                json=request_body,
                timeout=options.request_timeout
            ):
                if not chunk.strip():
                    continue
                    
                # Parse SSE event
                if chunk.startswith("data: "):
                    data = chunk[6:]
                    
                    if data == "[DONE]":
                        break
                        
                    try:
                        event_data = json.loads(data)
                        event = DeepSeekStreamChunk.model_validate(event_data)
                        
                        # Store response metadata
                        last_response_id = event.id
                        deepseek_metadata.update({
                            "object": event.object,
                            "created": event.created
                        })
                        
                        if event.choices:
                            choice = event.choices[0]
                            
                            if not stream_started:
                                yield TextStartPart()
                                stream_started = True
                            
                            # Handle content delta
                            if choice.delta.get("content"):
                                content_delta = choice.delta["content"]
                                accumulated_content += content_delta
                                yield TextDeltaPart(delta=content_delta)
                            
                            # Handle tool calls
                            if choice.delta.get("tool_calls"):
                                # Process tool calls (implementation similar to OpenAI)
                                pass
                            
                            # Handle finish reason and final metadata
                            if choice.finish_reason:
                                deepseek_metadata["finish_reason"] = choice.finish_reason
                                
                                # Extract usage information
                                if event.usage:
                                    last_usage = Usage(
                                        prompt_tokens=event.usage.prompt_tokens,
                                        completion_tokens=event.usage.completion_tokens,
                                        total_tokens=event.usage.total_tokens
                                    )
                                    
                                    # Add cache metrics if available
                                    if event.usage.prompt_cache_hit_tokens is not None:
                                        deepseek_metadata[DeepSeekMetadataKeys.PROMPT_CACHE_HIT_TOKENS] = event.usage.prompt_cache_hit_tokens
                                    if event.usage.prompt_cache_miss_tokens is not None:
                                        deepseek_metadata[DeepSeekMetadataKeys.PROMPT_CACHE_MISS_TOKENS] = event.usage.prompt_cache_miss_tokens
                                
                                # Create final response metadata
                                response_metadata = ResponseMetadata(
                                    id=last_response_id or "unknown",
                                    model_id=self.model_id,
                                    timestamp=None
                                )
                                
                                provider_metadata = ProviderMetadata(
                                    deepseek=deepseek_metadata
                                )
                                
                                # Add warnings
                                warnings = []
                                if options.top_k is not None:
                                    warnings.append("top_k parameter is not supported by DeepSeek")
                                
                                yield FinishPart(
                                    finish_reason=self._map_finish_reason(choice.finish_reason),
                                    usage=last_usage,
                                    response_metadata=response_metadata,
                                    provider_metadata=provider_metadata,
                                    warnings=warnings if warnings else None
                                )
                                
                    except json.JSONDecodeError:
                        # Skip invalid JSON
                        continue
                        
        except Exception as e:
            raise AISDKError(f"DeepSeek streaming error: {str(e)}") from e
    
    def _convert_messages(self, messages) -> List[Dict[str, Any]]:
        """Convert AI SDK messages to OpenAI-compatible format."""
        openai_messages = []
        
        for message in messages:
            if hasattr(message, 'role') and hasattr(message, 'content'):
                msg = {
                    "role": message.role,
                    "content": message.content
                }
                
                # Handle tool calls if present
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    msg["tool_calls"] = [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.name,
                                "arguments": tc.arguments
                            }
                        }
                        for tc in message.tool_calls
                    ]
                
                openai_messages.append(msg)
        
        return openai_messages
    
    def _convert_tools(self, tools) -> List[Dict[str, Any]]:
        """Convert AI SDK tools to OpenAI-compatible format."""
        return tools  # Assuming tools are already in OpenAI format
    
    def _map_finish_reason(self, deepseek_reason: str | None) -> str:
        """Map DeepSeek finish reason to AI SDK finish reason."""
        if not deepseek_reason:
            return "unknown"
            
        mapping = {
            "stop": "stop",
            "length": "length",
            "tool_calls": "tool-calls",
            "content_filter": "content-filter",
        }
        
        return mapping.get(deepseek_reason, "unknown")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for DeepSeek API requests."""
        api_key = self.settings.api_key
        if not api_key:
            # Try to get from environment
            import os
            api_key = os.getenv("DEEPSEEK_API_KEY")
            
        if not api_key:
            raise AISDKError("DeepSeek API key is required. Set DEEPSEEK_API_KEY environment variable or provide api_key in settings.")
        
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ai-sdk-python/1.0"
        }
        
        # Add custom headers
        if self.settings.headers:
            headers.update(self.settings.headers)
            
        return headers
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about this model."""
        return {
            "provider": self.provider,
            "model_id": self.model_id,
            "supports_streaming": True,
            "supports_tools": True,
            "supports_json_mode": True,
            "supports_reasoning": self.model_id == "deepseek-reasoner",
            "supports_caching": True,
            "max_tokens": self._get_max_tokens(),
            "input_modalities": ["text"],
            "output_modalities": ["text"],
            "special_capabilities": [
                "reasoning" if self.model_id == "deepseek-reasoner" else "chat",
                "prompt_caching",
                "openai_compatible"
            ]
        }
    
    def _get_max_tokens(self) -> int | None:
        """Get max tokens for different DeepSeek models."""
        # DeepSeek model token limits
        model_limits = {
            "deepseek-chat": 32768,
            "deepseek-reasoner": 65536,  # Reasoning model may have higher limit
        }
        
        return model_limits.get(self.model_id, None)