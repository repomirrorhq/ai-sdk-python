"""xAI language model implementation."""

import json
import uuid
from typing import Any, AsyncGenerator, Dict, List, Optional, Union

import httpx

from ...core.types import (
    GenerateTextOptions,
    GenerateTextResult,
    GenerateTextStreamResult,
    LanguageModel,
    Message,
    StreamTextOptions,
    TextContent,
    ToolCallContent,
    SourceContent,
    ReasoningContent,
)
from ...errors.base import AISDKError
from ...tools.core import Tool
from ...utils.http import create_http_client
from .message_converter import convert_to_xai_messages, map_finish_reason
from .types import XAIChatModelId, XAIProviderOptions


class XAILanguageModel(LanguageModel):
    """xAI language model implementation."""

    def __init__(
        self,
        model_id: Union[XAIChatModelId, str],
        api_key: str,
        base_url: str = "https://api.x.ai/v1",
        http_client: Optional[httpx.AsyncClient] = None,
    ):
        """
        Initialize xAI language model.
        
        Args:
            model_id: The model identifier
            api_key: xAI API key
            base_url: Base URL for API requests
            http_client: Optional HTTP client
        """
        self.model_id = model_id
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.http_client = http_client or create_http_client()

    @property
    def provider(self) -> str:
        """Get the provider name."""
        return "xai"

    def _get_headers(self) -> Dict[str, str]:
        """Get request headers."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def _prepare_tools(self, tools: Optional[List[Tool]]) -> Optional[List[Dict[str, Any]]]:
        """Convert AI SDK tools to xAI format."""
        if not tools:
            return None

        xai_tools = []
        for tool in tools:
            xai_tools.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.parameters,
                }
            })

        return xai_tools

    def _prepare_request_body(
        self,
        messages: List[Message],
        options: Union[GenerateTextOptions, StreamTextOptions],
        stream: bool = False,
    ) -> Dict[str, Any]:
        """Prepare the request body for xAI API."""
        # Convert messages
        xai_messages = convert_to_xai_messages(messages)

        # Base request body
        body = {
            "model": self.model_id,
            "messages": xai_messages,
            "stream": stream,
        }

        # Add generation parameters
        if options.max_tokens:
            body["max_tokens"] = options.max_tokens
        if options.temperature is not None:
            body["temperature"] = options.temperature
        if options.top_p is not None:
            body["top_p"] = options.top_p
        if options.seed is not None:
            body["seed"] = options.seed

        # Add tools
        if options.tools:
            body["tools"] = self._prepare_tools(options.tools)
            if options.tool_choice:
                if options.tool_choice == "auto":
                    body["tool_choice"] = "auto"
                elif options.tool_choice == "required":
                    body["tool_choice"] = "required"
                elif isinstance(options.tool_choice, dict):
                    body["tool_choice"] = {
                        "type": "function",
                        "function": {"name": options.tool_choice["function"]["name"]}
                    }

        # Add response format
        if hasattr(options, 'response_format') and options.response_format:
            if options.response_format.get('type') == 'json':
                schema = options.response_format.get('schema')
                if schema:
                    body["response_format"] = {
                        "type": "json_schema",
                        "json_schema": {
                            "name": options.response_format.get('name', 'response'),
                            "schema": schema,
                            "strict": True,
                        }
                    }
                else:
                    body["response_format"] = {"type": "json_object"}

        # Add provider options
        if hasattr(options, 'provider_options') and options.provider_options:
            provider_opts = XAIProviderOptions.model_validate(options.provider_options)
            
            if provider_opts.reasoning_effort:
                body["reasoning_effort"] = provider_opts.reasoning_effort
            
            if provider_opts.search_parameters:
                search_params = {}
                sp = provider_opts.search_parameters
                
                search_params["mode"] = sp.mode
                if sp.return_citations is not None:
                    search_params["return_citations"] = sp.return_citations
                if sp.from_date:
                    search_params["from_date"] = sp.from_date
                if sp.to_date:
                    search_params["to_date"] = sp.to_date
                if sp.max_search_results:
                    search_params["max_search_results"] = sp.max_search_results
                
                if sp.sources:
                    search_params["sources"] = []
                    for source in sp.sources:
                        source_dict = {"type": source.type}
                        
                        if hasattr(source, 'country') and source.country:
                            source_dict["country"] = source.country
                        if hasattr(source, 'excluded_websites') and source.excluded_websites:
                            source_dict["excluded_websites"] = source.excluded_websites
                        if hasattr(source, 'allowed_websites') and source.allowed_websites:
                            source_dict["allowed_websites"] = source.allowed_websites
                        if hasattr(source, 'safe_search') and source.safe_search is not None:
                            source_dict["safe_search"] = source.safe_search
                        if hasattr(source, 'x_handles') and source.x_handles:
                            source_dict["x_handles"] = source.x_handles
                        if hasattr(source, 'links') and source.links:
                            source_dict["links"] = source.links
                        
                        search_params["sources"].append(source_dict)
                
                body["search_parameters"] = search_params

        # Add streaming options
        if stream:
            body["stream_options"] = {"include_usage": True}

        return body

    async def generate_text(
        self, messages: List[Message], options: GenerateTextOptions
    ) -> GenerateTextResult:
        """Generate text using xAI API."""
        body = self._prepare_request_body(messages, options, stream=False)

        try:
            response = await self.http_client.post(
                f"{self.base_url}/chat/completions",
                headers=self._get_headers(),
                json=body,
            )
            response.raise_for_status()
            data = response.json()

            choice = data["choices"][0]
            message = choice["message"]

            # Extract content
            content = []

            # Add text content
            if message.get("content"):
                content.append(TextContent(text=message["content"]))

            # Add reasoning content (xAI specific)
            if message.get("reasoning_content"):
                content.append(ReasoningContent(text=message["reasoning_content"]))

            # Add tool calls
            if message.get("tool_calls"):
                for tool_call in message["tool_calls"]:
                    content.append(
                        ToolCallContent(
                            tool_call_id=tool_call["id"],
                            tool_name=tool_call["function"]["name"],
                            input=tool_call["function"]["arguments"],
                        )
                    )

            # Add citations
            if data.get("citations"):
                for url in data["citations"]:
                    content.append(
                        SourceContent(
                            source_type="url",
                            id=str(uuid.uuid4()),
                            url=url,
                        )
                    )

            usage = data["usage"]
            
            return GenerateTextResult(
                text=message.get("content", ""),
                content=content,
                finish_reason=map_finish_reason(choice.get("finish_reason", "stop")),
                usage={
                    "prompt_tokens": usage["prompt_tokens"],
                    "completion_tokens": usage["completion_tokens"],
                    "total_tokens": usage["total_tokens"],
                    "reasoning_tokens": usage.get("completion_tokens_details", {}).get("reasoning_tokens"),
                },
                response_metadata={
                    "id": data.get("id"),
                    "model": data.get("model"),
                    "created": data.get("created"),
                },
                raw_response=data,
            )

        except httpx.HTTPStatusError as e:
            error_data = e.response.json() if e.response.content else {}
            error_message = error_data.get("error", {}).get("message", str(e))
            raise AISDKError(f"xAI API error: {error_message}") from e
        except Exception as e:
            raise AISDKError(f"xAI request failed: {str(e)}") from e

    async def stream_text(
        self, messages: List[Message], options: StreamTextOptions
    ) -> AsyncGenerator[GenerateTextStreamResult, None]:
        """Stream text generation using xAI API."""
        body = self._prepare_request_body(messages, options, stream=True)

        try:
            async with self.http_client.stream(
                "POST",
                f"{self.base_url}/chat/completions",
                headers=self._get_headers(),
                json=body,
            ) as response:
                response.raise_for_status()

                content_blocks = {}
                finish_reason = "unknown"
                usage = {}
                is_first_chunk = True
                last_reasoning_deltas = {}

                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue

                    line = line[6:]  # Remove "data: " prefix
                    if line.strip() == "[DONE]":
                        break

                    try:
                        chunk = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # Emit response metadata on first chunk
                    if is_first_chunk:
                        yield GenerateTextStreamResult(
                            type="response-metadata",
                            id=chunk.get("id"),
                            model=chunk.get("model"),
                            created=chunk.get("created"),
                        )
                        is_first_chunk = False

                    # Handle citations
                    if chunk.get("citations"):
                        for url in chunk["citations"]:
                            source_id = str(uuid.uuid4())
                            yield GenerateTextStreamResult(
                                type="source",
                                source_type="url",
                                id=source_id,
                                url=url,
                            )

                    # Update usage
                    if chunk.get("usage"):
                        usage.update(chunk["usage"])

                    choice = chunk.get("choices", [{}])[0]
                    delta = choice.get("delta", {})

                    # Update finish reason
                    if choice.get("finish_reason"):
                        finish_reason = map_finish_reason(choice["finish_reason"])

                    # Handle text content
                    if delta.get("content"):
                        text_content = delta["content"]
                        block_id = f"text-{chunk.get('id', choice.get('index', 0))}"

                        if block_id not in content_blocks:
                            content_blocks[block_id] = {"type": "text"}
                            yield GenerateTextStreamResult(type="text-start", id=block_id)

                        yield GenerateTextStreamResult(
                            type="text-delta", id=block_id, delta=text_content
                        )

                    # Handle reasoning content (xAI specific)
                    if delta.get("reasoning_content"):
                        reasoning_content = delta["reasoning_content"]
                        block_id = f"reasoning-{chunk.get('id', choice.get('index', 0))}"

                        # Skip duplicate reasoning content
                        if last_reasoning_deltas.get(block_id) == reasoning_content:
                            continue
                        last_reasoning_deltas[block_id] = reasoning_content

                        if block_id not in content_blocks:
                            content_blocks[block_id] = {"type": "reasoning"}
                            yield GenerateTextStreamResult(type="reasoning-start", id=block_id)

                        yield GenerateTextStreamResult(
                            type="reasoning-delta", id=block_id, delta=reasoning_content
                        )

                    # Handle tool calls
                    if delta.get("tool_calls"):
                        for tool_call in delta["tool_calls"]:
                            tool_call_id = tool_call["id"]

                            yield GenerateTextStreamResult(
                                type="tool-input-start",
                                id=tool_call_id,
                                tool_name=tool_call["function"]["name"],
                            )

                            yield GenerateTextStreamResult(
                                type="tool-input-delta",
                                id=tool_call_id,
                                delta=tool_call["function"]["arguments"],
                            )

                            yield GenerateTextStreamResult(
                                type="tool-input-end", id=tool_call_id
                            )

                            yield GenerateTextStreamResult(
                                type="tool-call",
                                tool_call_id=tool_call_id,
                                tool_name=tool_call["function"]["name"],
                                input=tool_call["function"]["arguments"],
                            )

                # End all content blocks
                for block_id, block in content_blocks.items():
                    if block["type"] == "text":
                        yield GenerateTextStreamResult(type="text-end", id=block_id)
                    elif block["type"] == "reasoning":
                        yield GenerateTextStreamResult(type="reasoning-end", id=block_id)

                # Final result
                yield GenerateTextStreamResult(
                    type="finish",
                    finish_reason=finish_reason,
                    usage={
                        "prompt_tokens": usage.get("prompt_tokens"),
                        "completion_tokens": usage.get("completion_tokens"),
                        "total_tokens": usage.get("total_tokens"),
                        "reasoning_tokens": usage.get("completion_tokens_details", {}).get("reasoning_tokens"),
                    },
                )

        except httpx.HTTPStatusError as e:
            error_data = e.response.json() if e.response.content else {}
            error_message = error_data.get("error", {}).get("message", str(e))
            raise AISDKError(f"xAI API error: {error_message}") from e
        except Exception as e:
            raise AISDKError(f"xAI streaming request failed: {str(e)}") from e