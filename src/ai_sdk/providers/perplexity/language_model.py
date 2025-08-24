"""
Perplexity Language Model implementation.
"""

import json
from typing import Any, AsyncGenerator, Dict, List, Optional
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
    Usage,
    ResponseMetadata,
    ProviderMetadata
)
from ai_sdk.core.stream_text import TextStreamPart
from ai_sdk.utils.http import make_request, stream_request
from ai_sdk.errors.base import AISDKError
from .types import (
    PerplexityLanguageModelId,
    PerplexityChatRequest, 
    PerplexityChatResponse,
    PerplexityStreamEvent,
    PerplexityProviderSettings,
    PerplexityUsage,
    PerplexityResponseFormat
)
from .message_converter import (
    convert_to_perplexity_messages,
    map_perplexity_finish_reason,
    prepare_search_parameters
)


class PerplexityLanguageModel(LanguageModel):
    """
    Perplexity language model implementation for search-augmented chat completions.
    
    Supports real-time search, citations, and knowledge-based responses with
    access to current information and web sources.
    """
    
    def __init__(
        self,
        model_id: PerplexityLanguageModelId,
        settings: PerplexityProviderSettings,
    ):
        self.model_id = model_id
        self.settings = settings
        self._provider = "perplexity"
    
    @property
    def provider(self) -> str:
        return self._provider
    
    async def generate_text(
        self,
        prompt: ChatPrompt,
        options: GenerateTextOptions,
    ) -> GenerateTextResult:
        """Generate text using Perplexity search-augmented chat API."""
        
        try:
            # Convert AI SDK format to Perplexity format
            messages, conversion_warnings = convert_to_perplexity_messages(prompt)
            
            # Prepare search parameters
            search_params = prepare_search_parameters(getattr(options, 'provider_options', None))
            
            # Prepare request
            request = PerplexityChatRequest(
                model=self.model_id,
                messages=messages,
                max_tokens=options.max_output_tokens,
                temperature=options.temperature,
                top_p=options.top_p,
                frequency_penalty=options.frequency_penalty,
                presence_penalty=options.presence_penalty,
                stream=False,
                **search_params
            )
            
            # Add response format if specified
            if options.response_format:
                if options.response_format.get("type") == "json":
                    request.response_format = PerplexityResponseFormat(type="json")
                else:
                    request.response_format = PerplexityResponseFormat(type="text")
            
            # Add provider-specific warnings for unsupported parameters
            warnings = list(conversion_warnings)
            if options.top_k is not None:
                warnings.append("top_k parameter is not supported by Perplexity")
            if options.stop_sequences:
                warnings.append("stop_sequences parameter is not supported by Perplexity")
            if options.seed is not None:
                warnings.append("seed parameter is not supported by Perplexity")
            
            # Make API request
            headers = self._get_headers()
            
            response_data = await make_request(
                method="POST",
                url=f"{self.settings.base_url}/chat/completions",
                headers=headers,
                json=request.model_dump(exclude_none=True),
                timeout=options.request_timeout
            )
            
            response = PerplexityChatResponse.model_validate(response_data)
            
            # Extract response content
            choice = response.choices[0] if response.choices else None
            content = choice.message.content if choice else ""
            
            # Convert usage information
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
            
            # Create provider metadata with search results
            provider_metadata = ProviderMetadata(
                perplexity={
                    "citations": response.citations,
                    "related_questions": response.related_questions,
                    "finish_reason": choice.finish_reason if choice else "unknown",
                    "search_enabled": True,
                    "object": response.object,
                    "created": response.created
                }
            )
            
            return GenerateTextResult(
                text=content,
                tool_calls=[],  # Perplexity doesn't support traditional tool calls
                usage=usage,
                finish_reason=map_perplexity_finish_reason(choice.finish_reason if choice else None),
                response_metadata=response_metadata,
                provider_metadata=provider_metadata,
                warnings=warnings if warnings else None
            )
            
        except Exception as e:
            raise AISDKError(f"Perplexity API error: {str(e)}") from e
    
    async def stream_text(
        self,
        prompt: ChatPrompt,
        options: StreamTextOptions,
    ) -> AsyncGenerator[TextStreamPart, None]:
        """Stream text generation using Perplexity search-augmented chat API."""
        
        try:
            # Convert AI SDK format to Perplexity format
            messages, conversion_warnings = convert_to_perplexity_messages(prompt)
            
            # Prepare search parameters
            search_params = prepare_search_parameters(getattr(options, 'provider_options', None))
            
            # Prepare request
            request = PerplexityChatRequest(
                model=self.model_id,
                messages=messages,
                max_tokens=options.max_output_tokens,
                temperature=options.temperature,
                top_p=options.top_p,
                frequency_penalty=options.frequency_penalty,
                presence_penalty=options.presence_penalty,
                stream=True,
                **search_params
            )
            
            # Add response format if specified
            if options.response_format:
                if options.response_format.get("type") == "json":
                    request.response_format = PerplexityResponseFormat(type="json")
                else:
                    request.response_format = PerplexityResponseFormat(type="text")
            
            # Add provider-specific warnings for unsupported parameters
            warnings = list(conversion_warnings)
            if options.top_k is not None:
                warnings.append("top_k parameter is not supported by Perplexity")
            if options.stop_sequences:
                warnings.append("stop_sequences parameter is not supported by Perplexity")
            if options.seed is not None:
                warnings.append("seed parameter is not supported by Perplexity")
            
            # Make streaming request
            headers = self._get_headers()
            
            stream_started = False
            accumulated_content = ""
            last_response_id = None
            last_usage = None
            last_citations = None
            last_related_questions = None
            
            async for chunk in stream_request(
                method="POST",
                url=f"{self.settings.base_url}/chat/completions",
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
                        event = PerplexityStreamEvent.model_validate(event_data)
                        
                        # Store response metadata
                        last_response_id = event.id
                        
                        if event.choices:
                            choice = event.choices[0]
                            
                            if not stream_started:
                                yield TextStartPart()
                                stream_started = True
                            
                            # Handle content delta
                            if choice.delta.content:
                                accumulated_content += choice.delta.content
                                yield TextDeltaPart(delta=choice.delta.content)
                            
                            # Handle finish reason
                            if choice.finish_reason:
                                # Try to get citations and related questions from final response
                                # Note: These may not be available in streaming mode
                                if hasattr(event_data, 'citations'):
                                    last_citations = event_data.get('citations')
                                if hasattr(event_data, 'related_questions'):
                                    last_related_questions = event_data.get('related_questions')
                                if hasattr(event_data, 'usage'):
                                    usage_data = event_data.get('usage')
                                    if usage_data:
                                        last_usage = Usage(
                                            prompt_tokens=usage_data.get('prompt_tokens', 0),
                                            completion_tokens=usage_data.get('completion_tokens', 0),
                                            total_tokens=usage_data.get('total_tokens', 0)
                                        )
                                
                                # Create response metadata
                                response_metadata = ResponseMetadata(
                                    id=last_response_id or "unknown",
                                    model_id=self.model_id,
                                    timestamp=None
                                )
                                
                                provider_metadata = ProviderMetadata(
                                    perplexity={
                                        "citations": last_citations,
                                        "related_questions": last_related_questions,
                                        "finish_reason": choice.finish_reason,
                                        "search_enabled": True,
                                        "object": event.object,
                                        "created": event.created
                                    }
                                )
                                
                                yield FinishPart(
                                    finish_reason=map_perplexity_finish_reason(choice.finish_reason),
                                    usage=last_usage,
                                    response_metadata=response_metadata,
                                    provider_metadata=provider_metadata,
                                    warnings=warnings if warnings else None
                                )
                                
                    except json.JSONDecodeError:
                        # Skip invalid JSON
                        continue
                        
        except Exception as e:
            raise AISDKError(f"Perplexity streaming error: {str(e)}") from e
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Perplexity API requests."""
        api_key = self.settings.api_key
        if not api_key:
            # Try to get from environment
            import os
            api_key = os.getenv("PERPLEXITY_API_KEY")
            
        if not api_key:
            raise AISDKError("Perplexity API key is required. Set PERPLEXITY_API_KEY environment variable or provide api_key in settings.")
        
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
            "supports_tools": False,  # Perplexity uses search instead of traditional tools
            "supports_json_mode": True,
            "supports_search": True,
            "supports_citations": True,
            "supports_real_time_data": True,
            "max_tokens": self._get_max_tokens(),
            "input_modalities": ["text"],
            "output_modalities": ["text"],
            "search_capabilities": [
                "real_time_search",
                "web_citations",
                "domain_filtering", 
                "recency_filtering",
                "related_questions"
            ]
        }
    
    def _get_max_tokens(self) -> int | None:
        """Get max tokens for different Perplexity models."""
        # Perplexity model token limits
        model_limits = {
            "sonar-deep-research": 127072,
            "sonar-reasoning-pro": 127072,
            "sonar-reasoning": 127072,
            "sonar-pro": 127072,
            "sonar": 127072,
        }
        
        return model_limits.get(self.model_id, None)