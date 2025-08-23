"""
DeepInfra Language Model implementation.

DeepInfra provides OpenAI-compatible API with access to 50+ open-source models
including Llama, Qwen, Mistral, and many other state-of-the-art models.
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
    ProviderMetadata,
    FinishReason
)
from ai_sdk.utils.http import make_request, stream_request
from ai_sdk.errors.base import AISDKError
from .types import (
    DeepInfraChatModelId,
    DeepInfraProviderSettings,
    DeepInfraChatRequest,
    DeepInfraChatResponse,
    DeepInfraStreamChunk,
    DeepInfraUsage,
    DeepInfraFinishReason
)


class DeepInfraLanguageModel(LanguageModel):
    """
    DeepInfra language model implementation.
    
    Features:
    - OpenAI-compatible API with 50+ open-source models
    - Llama, Qwen, Mistral, CodeLlama, and many other models
    - Cost-effective access to state-of-the-art models
    - Tool calling support
    - Streaming responses
    """
    
    def __init__(
        self,
        model_id: DeepInfraChatModelId,
        settings: DeepInfraProviderSettings,
    ):
        self.model_id = model_id
        self.settings = settings
        self._provider = "deepinfra"
    
    @property
    def provider(self) -> str:
        return self._provider
    
    async def generate_text(
        self,
        prompt: ChatPrompt,
        options: GenerateTextOptions,
    ) -> GenerateTextResult:
        """Generate text using DeepInfra OpenAI-compatible API."""
        
        try:
            # Convert AI SDK format to OpenAI-compatible format
            messages = self._convert_messages(prompt.messages)
            
            # Prepare request body
            request = DeepInfraChatRequest(
                model=self.model_id,
                messages=messages,
                max_tokens=options.max_output_tokens,
                temperature=options.temperature,
                top_p=options.top_p,
                frequency_penalty=options.frequency_penalty,
                presence_penalty=options.presence_penalty,
                stop=options.stop_sequences,
                seed=options.seed,
                stream=False
            )
            
            # Add tools if provided
            if options.tools:
                request.tools = self._convert_tools(options.tools)
                if options.tool_choice:
                    request.tool_choice = options.tool_choice
            
            # Add response format if specified
            if options.response_format and options.response_format.get("type") == "json":
                request.response_format = {
                    "type": "json_object",
                    "schema": options.response_format.get("schema")
                }
            
            # Make API request
            headers = self._get_headers()
            
            response_data = await make_request(
                method="POST",
                url=f"{self.settings.base_url}/openai/chat/completions",
                headers=headers,
                json=request.model_dump(exclude_none=True),
                timeout=options.request_timeout
            )
            
            response = DeepInfraChatResponse.model_validate(response_data)
            
            # Extract response content
            choice = response.choices[0] if response.choices else None
            if not choice:
                raise AISDKError("No choices returned in DeepInfra response")
                
            content = choice.get("message", {}).get("content", "") if choice else ""
            
            # Extract tool calls if present
            tool_calls = []
            if choice and choice.get("message", {}).get("tool_calls"):
                for tool_call in choice["message"]["tool_calls"]:
                    tool_calls.append({
                        "id": tool_call["id"],
                        "name": tool_call["function"]["name"],
                        "arguments": tool_call["function"]["arguments"]
                    })
            
            # Convert usage information
            usage = None
            if response.usage:
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
            
            # Create provider metadata
            provider_metadata = ProviderMetadata(
                deepinfra={
                    "finish_reason": choice.get("finish_reason") if choice else "unknown",
                    "object": response.object,
                    "created": response.created,
                    "model": response.model
                }
            )
            
            # Add warnings for unsupported parameters
            warnings = []
            if options.top_k is not None:
                warnings.append("top_k parameter is not supported by DeepInfra")
            
            return GenerateTextResult(
                text=content,
                tool_calls=tool_calls,
                usage=usage,
                finish_reason=self._map_finish_reason(choice.get("finish_reason") if choice else None),
                response_metadata=response_metadata,
                provider_metadata=provider_metadata,
                warnings=warnings if warnings else None
            )
            
        except Exception as e:
            raise AISDKError(f"DeepInfra API error: {str(e)}") from e
    
    async def stream_text(
        self,
        prompt: ChatPrompt,
        options: StreamTextOptions,
    ) -> AsyncGenerator[TextStreamPart, None]:
        """Stream text generation using DeepInfra OpenAI-compatible API."""
        
        try:
            # Convert AI SDK format to OpenAI-compatible format
            messages = self._convert_messages(prompt.messages)
            
            # Prepare request body
            request = DeepInfraChatRequest(
                model=self.model_id,
                messages=messages,
                max_tokens=options.max_output_tokens,
                temperature=options.temperature,
                top_p=options.top_p,
                frequency_penalty=options.frequency_penalty,
                presence_penalty=options.presence_penalty,
                stop=options.stop_sequences,
                seed=options.seed,
                stream=True
            )
            
            # Add tools if provided
            if options.tools:
                request.tools = self._convert_tools(options.tools)
                if options.tool_choice:
                    request.tool_choice = options.tool_choice
            
            # Add response format if specified
            if options.response_format and options.response_format.get("type") == "json":
                request.response_format = {
                    "type": "json_object", 
                    "schema": options.response_format.get("schema")
                }
            
            # Make streaming request
            headers = self._get_headers()
            
            stream_started = False
            accumulated_content = ""
            last_response_id = None
            last_usage = None
            tool_calls = []
            deepinfra_metadata = {}
            
            async for chunk in stream_request(
                method="POST",
                url=f"{self.settings.base_url}/openai/chat/completions",
                headers=headers,
                json=request.model_dump(exclude_none=True),
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
                        event = DeepInfraStreamChunk.model_validate(event_data)
                        
                        # Store response metadata
                        last_response_id = event.id
                        deepinfra_metadata.update({
                            "object": event.object,
                            "created": event.created,
                            "model": event.model
                        })
                        
                        if event.choices:
                            choice = event.choices[0]
                            
                            if not stream_started:
                                yield TextStartPart()
                                stream_started = True
                            
                            # Handle content delta
                            delta = choice.get("delta", {})
                            if delta.get("content"):
                                content_delta = delta["content"]
                                accumulated_content += content_delta
                                yield TextDeltaPart(delta=content_delta)
                            
                            # Handle tool calls
                            if delta.get("tool_calls"):
                                # Process tool calls (implementation similar to OpenAI)
                                pass
                            
                            # Handle finish reason and final metadata
                            if choice.get("finish_reason"):
                                deepinfra_metadata["finish_reason"] = choice["finish_reason"]
                                
                                # Extract usage information
                                if event.usage:
                                    last_usage = Usage(
                                        prompt_tokens=event.usage.prompt_tokens,
                                        completion_tokens=event.usage.completion_tokens,
                                        total_tokens=event.usage.total_tokens
                                    )
                                
                                # Create response metadata
                                response_metadata = ResponseMetadata(
                                    id=last_response_id or "unknown",
                                    model_id=self.model_id,
                                    timestamp=None
                                )
                                
                                provider_metadata = ProviderMetadata(
                                    deepinfra=deepinfra_metadata
                                )
                                
                                # Add warnings
                                warnings = []
                                if options.top_k is not None:
                                    warnings.append("top_k parameter is not supported by DeepInfra")
                                
                                yield FinishPart(
                                    finish_reason=self._map_finish_reason(choice.get("finish_reason")),
                                    usage=last_usage,
                                    response_metadata=response_metadata,
                                    provider_metadata=provider_metadata,
                                    warnings=warnings if warnings else None
                                )
                                
                    except json.JSONDecodeError:
                        # Skip invalid JSON
                        continue
                        
        except Exception as e:
            raise AISDKError(f"DeepInfra streaming error: {str(e)}") from e
    
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
    
    def _map_finish_reason(self, deepinfra_reason: str | None) -> FinishReason:
        """Map DeepInfra finish reason to AI SDK finish reason."""
        if not deepinfra_reason:
            return "unknown"
            
        mapping = {
            DeepInfraFinishReason.STOP: "stop",
            DeepInfraFinishReason.LENGTH: "length", 
            DeepInfraFinishReason.TOOL_CALLS: "tool-calls",
            DeepInfraFinishReason.CONTENT_FILTER: "content-filter",
            DeepInfraFinishReason.ERROR: "error"
        }
        
        return mapping.get(deepinfra_reason, "unknown")
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for DeepInfra API requests."""
        api_key = self.settings.api_key
        if not api_key:
            # Try to get from environment
            import os
            api_key = os.getenv("DEEPINFRA_API_KEY")
            
        if not api_key:
            raise AISDKError("DeepInfra API key is required. Set DEEPINFRA_API_KEY environment variable or provide api_key in settings.")
        
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
            "supports_vision": "vision" in self.model_id.lower() or "llama-3.2" in self.model_id,
            "max_tokens": self._get_max_tokens(),
            "input_modalities": ["text", "image"] if "vision" in self.model_id.lower() else ["text"],
            "output_modalities": ["text"],
            "special_capabilities": [
                "cost_effective",
                "open_source_models",
                "diverse_model_selection",
                "openai_compatible"
            ]
        }
    
    def _get_max_tokens(self) -> int | None:
        """Get max tokens for different DeepInfra models."""
        # Model context length mapping (approximate)
        model_limits = {
            # Llama 4 Models (New)
            "meta-llama/Llama-4": 128000,
            
            # Llama 3.3 Models
            "meta-llama/Llama-3.3": 128000,
            
            # Llama 3.1 Models
            "meta-llama/Meta-Llama-3.1-405B": 128000,
            "meta-llama/Meta-Llama-3.1-70B": 128000,
            "meta-llama/Meta-Llama-3.1-8B": 128000,
            
            # Qwen Models
            "Qwen/QwQ-32B": 32768,
            "Qwen/Qwen2.5": 32768,
            "Qwen/Qwen2": 32768,
            
            # Vision Models  
            "meta-llama/Llama-3.2-90B-Vision": 128000,
            "meta-llama/Llama-3.2-11B-Vision": 128000,
            
            # Code Models
            "codellama/CodeLlama": 16384,
            "bigcode/starcoder2": 16384,
            
            # Other models (default)
            "default": 4096
        }
        
        # Find matching model prefix
        for prefix, limit in model_limits.items():
            if self.model_id.startswith(prefix):
                return limit
                
        return model_limits["default"]