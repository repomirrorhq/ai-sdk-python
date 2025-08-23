"""Bedrock language model implementation."""

import json
from typing import AsyncGenerator, Dict, Any, List, Optional, Union, Callable
from pydantic import BaseModel

from ...providers.base import LanguageModel
from ...providers.types import (
    Message, Content, TextContent, ImageContent, ToolCallContent, ToolResultContent,
    FinishReason, Usage
)
from ...errors import APIError
from .types import BedrockChatModelId, BedrockConverseInput, BedrockOptions, BEDROCK_STOP_REASONS
from .utils import convert_to_bedrock_messages, map_bedrock_finish_reason, prepare_bedrock_tools


class BedrockLanguageModel(LanguageModel):
    """Amazon Bedrock language model implementation."""
    
    def __init__(
        self,
        model_id: BedrockChatModelId,
        base_url: str,
        fetch_fn: Callable,
        headers: Optional[Dict[str, str]] = None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.model_id = model_id
        self.base_url = base_url.rstrip('/')
        self.fetch_fn = fetch_fn
        self.headers = headers or {}
        self.provider = "bedrock"
        
    async def _prepare_request(
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
        stream: bool = False,
        provider_options: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare request for Bedrock Converse API."""
        
        # Parse provider options
        bedrock_options = BedrockOptions(**(provider_options or {}))
        
        # Convert messages to Bedrock format
        bedrock_messages = convert_to_bedrock_messages(messages)
        
        # Prepare system message if present
        system_message = None
        if bedrock_messages and bedrock_messages[0].role == "system":
            system_content = bedrock_messages.pop(0).content
            if isinstance(system_content, str):
                system_message = [{"text": system_content}]
            elif isinstance(system_content, list):
                system_message = system_content
                
        # Build inference config
        inference_config = {}
        if max_tokens is not None:
            inference_config["maxTokens"] = max_tokens
        if temperature is not None:
            inference_config["temperature"] = temperature  
        if top_p is not None:
            inference_config["topP"] = top_p
        if stop:
            stop_sequences = [stop] if isinstance(stop, str) else stop
            inference_config["stopSequences"] = stop_sequences
            
        # Build tool config
        tool_config = None
        if tools:
            bedrock_tools = prepare_bedrock_tools(tools)
            tool_config = {
                "tools": bedrock_tools
            }
            if tool_choice:
                if tool_choice == "auto":
                    tool_config["toolChoice"] = {"auto": {}}
                elif tool_choice == "required":
                    tool_config["toolChoice"] = {"any": {}}
                elif isinstance(tool_choice, dict) and "function" in tool_choice:
                    tool_config["toolChoice"] = {
                        "tool": {"name": tool_choice["function"]["name"]}
                    }
        
        # Build converse input
        converse_input = {
            "modelId": self.model_id,
            "messages": [msg.model_dump() for msg in bedrock_messages],
        }
        
        if system_message:
            converse_input["system"] = system_message
        if inference_config:
            converse_input["inferenceConfig"] = inference_config  
        if tool_config:
            converse_input["toolConfig"] = tool_config
        if bedrock_options.additional_model_request_fields:
            converse_input["additionalModelRequestFields"] = bedrock_options.additional_model_request_fields
        if bedrock_options.additional_model_response_field_paths:
            converse_input["additionalModelResponseFieldPaths"] = bedrock_options.additional_model_response_field_paths
            
        return converse_input
        
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
        """Generate a single response using Bedrock Converse API."""
        
        request_data = await self._prepare_request(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            stop=stop,
            tools=tools,
            tool_choice=tool_choice,
            response_format=response_format,
            stream=False,
            provider_options=provider_options,
            **kwargs
        )
        
        # Make API call
        url = f"{self.base_url}/model/{self.model_id}/converse"
        
        try:
            response = await self.fetch_fn(
                method="POST",
                url=url,
                headers={**self.headers, "Content-Type": "application/json"},
                body=json.dumps(request_data)
            )
            
            if response.status_code != 200:
                error_text = response.text
                try:
                    error_data = response.json()
                    message = error_data.get("message", error_text)
                except:
                    message = error_text
                raise APIError(f"Bedrock API error: {message}", status_code=response.status_code)
                
            result = response.json()
            
            # Parse response
            output = result.get("output", {})
            message_output = output.get("message", {})
            content = message_output.get("content", [])
            
            # Extract text and tool calls
            text_content = ""
            tool_calls = []
            
            for item in content:
                if "text" in item:
                    text_content += item["text"]
                elif "toolUse" in item:
                    tool_use = item["toolUse"]
                    tool_calls.append({
                        "id": tool_use.get("toolUseId", ""),
                        "type": "function",
                        "function": {
                            "name": tool_use.get("name", ""),
                            "arguments": json.dumps(tool_use.get("input", {}))
                        }
                    })
            
            # Map finish reason
            stop_reason = output.get("stopReason", "end_turn")
            finish_reason = map_bedrock_finish_reason(stop_reason)
            
            # Extract usage
            usage_info = result.get("usage", {})
            usage = Usage(
                prompt_tokens=usage_info.get("inputTokens", 0),
                completion_tokens=usage_info.get("outputTokens", 0),
                total_tokens=usage_info.get("totalTokens", 0)
            )
            
            return {
                "content": text_content,
                "tool_calls": tool_calls,
                "finish_reason": finish_reason,
                "usage": usage,
                "raw_response": result
            }
            
        except Exception as e:
            if isinstance(e, APIError):
                raise
            raise APIError(f"Bedrock request failed: {str(e)}")
    
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
        """Stream responses using Bedrock Converse API."""
        
        request_data = await self._prepare_request(
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            stop=stop,
            tools=tools,
            tool_choice=tool_choice,
            response_format=response_format,
            stream=True,
            provider_options=provider_options,
            **kwargs
        )
        
        # Make streaming API call
        url = f"{self.base_url}/model/{self.model_id}/converse-stream"
        
        try:
            # For streaming, we'll need to implement SSE parsing
            # This is a simplified implementation - a full implementation would need proper SSE parsing
            response = await self.fetch_fn(
                method="POST",
                url=url,
                headers={**self.headers, "Content-Type": "application/json"},
                body=json.dumps(request_data)
            )
            
            if response.status_code != 200:
                error_text = response.text
                try:
                    error_data = response.json()
                    message = error_data.get("message", error_text)
                except:
                    message = error_text
                raise APIError(f"Bedrock API error: {message}", status_code=response.status_code)
            
            # Parse SSE stream (simplified - real implementation needs proper SSE parsing)
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        
                        # Handle different event types
                        if "contentBlockStart" in data:
                            yield {"type": "content_block_start"}
                        elif "contentBlockDelta" in data:
                            delta = data["contentBlockDelta"]
                            if "text" in delta:
                                yield {
                                    "type": "content_delta",
                                    "delta": {"text": delta["text"]}
                                }
                            elif "toolUse" in delta:
                                yield {
                                    "type": "tool_use_delta", 
                                    "delta": delta["toolUse"]
                                }
                        elif "contentBlockStop" in data:
                            yield {"type": "content_block_end"}
                        elif "messageStop" in data:
                            # Final message with usage
                            usage_info = data.get("usage", {})
                            usage = Usage(
                                prompt_tokens=usage_info.get("inputTokens", 0),
                                completion_tokens=usage_info.get("outputTokens", 0),
                                total_tokens=usage_info.get("totalTokens", 0)
                            )
                            finish_reason = map_bedrock_finish_reason(data.get("stopReason", "end_turn"))
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
            raise APIError(f"Bedrock streaming request failed: {str(e)}")