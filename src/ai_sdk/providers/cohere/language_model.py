"""
Cohere Language Model implementation.
"""

import json
import asyncio
from typing import Any, AsyncGenerator, Dict, List, Optional, Union
from pydantic import BaseModel

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
    ToolCallPart,
    ToolResultPart,
    Usage,
    ResponseMetadata,
    ProviderMetadata,
    FinishReason
)
from ai_sdk.core.stream_text import TextStreamPart
from ai_sdk.utils.http import make_request, stream_request
from ai_sdk.errors.base import AISDKError
from .types import (
    CohereChatModelId,
    CohereChatRequest, 
    CohereChatResponse,
    CohereStreamEvent,
    CohereProviderSettings,
    CohereUsage
)
from .message_converter import (
    convert_to_cohere_messages,
    prepare_cohere_tools,
    map_cohere_finish_reason
)


class CohereLanguageModel(LanguageModel):
    """
    Cohere language model implementation for chat completions.
    
    Supports text generation, streaming, tool calling, and document-aware chat.
    """
    
    def __init__(
        self,
        model_id: CohereChatModelId,
        settings: CohereProviderSettings,
    ):
        self.model_id = model_id
        self.settings = settings
        self._provider = "cohere"
    
    @property
    def provider(self) -> str:
        return self._provider
    
    async def generate_text(
        self,
        prompt: ChatPrompt,
        options: GenerateTextOptions,
    ) -> GenerateTextResult:
        """Generate text using Cohere chat API."""
        
        try:
            # Convert AI SDK format to Cohere format
            messages, documents, conversion_warnings = convert_to_cohere_messages(prompt)
            tools, tool_choice, tool_warnings = prepare_cohere_tools(options.tools)
            
            # Prepare request
            request = CohereChatRequest(
                model=self.model_id,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                documents=documents if documents else None,
                max_tokens=options.max_output_tokens,
                temperature=options.temperature,
                p=options.top_p,
                k=options.top_k,
                seed=options.seed,
                stop_sequences=options.stop_sequences,
                frequency_penalty=options.frequency_penalty,
                presence_penalty=options.presence_penalty,
                stream=False
            )
            
            # Add response format if specified
            if options.response_format and options.response_format.get("type") == "json":
                request.response_format = {
                    "type": "json_object",
                    "json_schema": options.response_format.get("schema")
                }
            
            # Make API request
            headers = self._get_headers()
            
            response_data = await make_request(
                method="POST",
                url=f"{self.settings.base_url}/chat",
                headers=headers,
                json=request.model_dump(exclude_none=True),
                timeout=options.request_timeout
            )
            
            response = CohereChatResponse.model_validate(response_data)
            
            # Extract response content
            content = ""
            tool_calls = []
            
            if response.message:
                content = response.message.content or ""
                
                # Handle tool calls
                if response.message.tool_calls:
                    for tool_call in response.message.tool_calls:
                        tool_calls.append({
                            "id": tool_call["id"],
                            "name": tool_call["function"]["name"],
                            "arguments": tool_call["function"]["arguments"]
                        })
            
            # Convert usage information
            usage = None
            if response.usage:
                usage = Usage(
                    prompt_tokens=response.usage.billed_units.input_tokens,
                    completion_tokens=response.usage.billed_units.output_tokens,
                    total_tokens=response.usage.billed_units.input_tokens + response.usage.billed_units.output_tokens
                )
            
            # Create response metadata
            response_metadata = ResponseMetadata(
                id=response.id,
                model_id=self.model_id,
                timestamp=None
            )
            
            provider_metadata = ProviderMetadata(
                cohere={
                    "finish_reason": response.finish_reason,
                    "citations": response.citations,
                    "documents": response.documents,
                    "search_results": response.search_results,
                    "search_queries": response.search_queries,
                    "is_search_required": response.is_search_required
                }
            )
            
            warnings = conversion_warnings + tool_warnings
            
            return GenerateTextResult(
                text=content,
                tool_calls=tool_calls,
                usage=usage,
                finish_reason=map_cohere_finish_reason(response.finish_reason),
                response_metadata=response_metadata,
                provider_metadata=provider_metadata,
                warnings=warnings if warnings else None
            )
            
        except Exception as e:
            raise AISDKError(f"Cohere API error: {str(e)}") from e
    
    async def stream_text(
        self,
        prompt: ChatPrompt,
        options: StreamTextOptions,
    ) -> AsyncGenerator[TextStreamPart, None]:
        """Stream text generation using Cohere chat API."""
        
        try:
            # Convert AI SDK format to Cohere format
            messages, documents, conversion_warnings = convert_to_cohere_messages(prompt)
            tools, tool_choice, tool_warnings = prepare_cohere_tools(options.tools)
            
            # Prepare request
            request = CohereChatRequest(
                model=self.model_id,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                documents=documents if documents else None,
                max_tokens=options.max_output_tokens,
                temperature=options.temperature,
                p=options.top_p,
                k=options.top_k,
                seed=options.seed,
                stop_sequences=options.stop_sequences,
                frequency_penalty=options.frequency_penalty,
                presence_penalty=options.presence_penalty,
                stream=True
            )
            
            # Add response format if specified
            if options.response_format and options.response_format.get("type") == "json":
                request.response_format = {
                    "type": "json_object",
                    "json_schema": options.response_format.get("schema")
                }
            
            # Make streaming request
            headers = self._get_headers()
            
            stream_started = False
            accumulated_content = ""
            tool_calls = []
            
            async for chunk in stream_request(
                method="POST",
                url=f"{self.settings.base_url}/chat",
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
                        event = CohereStreamEvent.model_validate(event_data)
                        
                        # Handle different event types
                        if event.type == "content-start":
                            if not stream_started:
                                yield TextStartPart()
                                stream_started = True
                                
                        elif event.type == "content-delta":
                            if event.delta and "text" in event.delta:
                                text_delta = event.delta["text"]
                                accumulated_content += text_delta
                                yield TextDeltaPart(delta=text_delta)
                                
                        elif event.type == "tool-calls-chunk":
                            # Handle streaming tool calls
                            if event.delta:
                                # Process tool call delta
                                pass
                                
                        elif event.type == "stream-end":
                            # Final event with complete response
                            if "response" in event_data:
                                response_data = event_data["response"]
                                response = CohereChatResponse.model_validate(response_data)
                                
                                # Convert usage
                                usage = None
                                if response.usage:
                                    usage = Usage(
                                        prompt_tokens=response.usage.billed_units.input_tokens,
                                        completion_tokens=response.usage.billed_units.output_tokens,
                                        total_tokens=response.usage.billed_units.input_tokens + response.usage.billed_units.output_tokens
                                    )
                                
                                # Create response metadata
                                response_metadata = ResponseMetadata(
                                    id=response.id,
                                    model_id=self.model_id,
                                    timestamp=None
                                )
                                
                                provider_metadata = ProviderMetadata(
                                    cohere={
                                        "finish_reason": response.finish_reason,
                                        "citations": response.citations,
                                        "documents": response.documents,
                                        "search_results": response.search_results,
                                        "search_queries": response.search_queries,
                                        "is_search_required": response.is_search_required
                                    }
                                )
                                
                                warnings = conversion_warnings + tool_warnings
                                
                                yield FinishPart(
                                    finish_reason=map_cohere_finish_reason(response.finish_reason),
                                    usage=usage,
                                    response_metadata=response_metadata,
                                    provider_metadata=provider_metadata,
                                    warnings=warnings if warnings else None
                                )
                                
                    except json.JSONDecodeError:
                        # Skip invalid JSON
                        continue
                        
        except Exception as e:
            raise AISDKError(f"Cohere streaming error: {str(e)}") from e
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Cohere API requests."""
        api_key = self.settings.api_key
        if not api_key:
            # Try to get from environment
            import os
            api_key = os.getenv("COHERE_API_KEY")
            
        if not api_key:
            raise AISDKError("Cohere API key is required. Set COHERE_API_KEY environment variable or provide api_key in settings.")
        
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
            "supports_documents": True,
            "max_tokens": None,  # Cohere models have different limits
            "input_modalities": ["text"],
            "output_modalities": ["text"]
        }