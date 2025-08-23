"""
Gateway Language Model implementation
"""

import asyncio
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional, AsyncGenerator, Union, Tuple
from urllib.parse import urlencode

import aiohttp

from ...core.generate_text import GenerateTextOptions, GenerateTextResult
from ...core.step import StreamPart
from ...streaming.stream import AsyncIterator
from .types import GatewayModelId, GatewayConfig  
from .errors import as_gateway_error


class GatewayLanguageModel:
    """Language model implementation for Gateway Provider"""
    
    def __init__(self, model_id: GatewayModelId, config: GatewayConfig):
        self.model_id = model_id
        self.config = config
        self.specification_version = "v2"
        self.supported_urls = {"*/*": [r".*"]}
        
    @property
    def provider(self) -> str:
        return self.config.provider
    
    async def generate_text(
        self,
        prompt: Union[str, List[Dict[str, Any]]],
        options: Optional[GenerateTextOptions] = None,
        **kwargs
    ) -> GenerateTextResult:
        """
        Generate text using the Gateway model.
        
        Args:
            prompt: Text prompt or message list
            options: Generation options
            **kwargs: Additional options
            
        Returns:
            Generated text result
        """
        options = options or GenerateTextOptions()
        args = await self._prepare_args(prompt, options, **kwargs)
        
        headers = await self.config.headers()
        headers.update(self._get_model_config_headers(streaming=False))
        headers.update(await self.config.o11y_headers())
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self._get_url(),
                    json=args,
                    headers=headers
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"HTTP {response.status}: {error_text}")
                    
                    response_data = await response.json()
                    
                    return GenerateTextResult(
                        text=response_data.get("text", ""),
                        finish_reason=response_data.get("finishReason", "unknown"),
                        usage=response_data.get("usage", {}),
                        response_messages=response_data.get("responseMessages", []),
                        tool_calls=response_data.get("toolCalls", []),
                        tool_results=response_data.get("toolResults", []),
                        request={"body": args},
                        response={
                            "headers": dict(response.headers),
                            "body": response_data
                        },
                        warnings=[]
                    )
                    
        except Exception as error:
            auth_method = self._parse_auth_method(headers)
            raise as_gateway_error(error, auth_method)
    
    async def stream_text(
        self,
        prompt: Union[str, List[Dict[str, Any]]], 
        options: Optional[GenerateTextOptions] = None,
        **kwargs
    ) -> AsyncGenerator[StreamPart, None]:
        """
        Stream text generation using the Gateway model.
        
        Args:
            prompt: Text prompt or message list
            options: Generation options  
            **kwargs: Additional options
            
        Yields:
            Stream parts containing incremental updates
        """
        options = options or GenerateTextOptions()
        args = await self._prepare_args(prompt, options, **kwargs)
        
        headers = await self.config.headers()
        headers.update(self._get_model_config_headers(streaming=True))
        headers.update(await self.config.o11y_headers())
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self._get_url(),
                    json=args,
                    headers=headers
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"HTTP {response.status}: {error_text}")
                    
                    # Emit stream start with warnings if any
                    warnings = []  # TODO: Extract warnings from args preparation
                    if warnings:
                        yield StreamPart(type="stream-start", warnings=warnings)
                    
                    # Process Server-Sent Events
                    async for line in response.content:
                        line_str = line.decode('utf-8').strip()
                        
                        if line_str.startswith("data: "):
                            data_str = line_str[6:]  # Remove "data: " prefix
                            
                            if data_str == "[DONE]":
                                break
                                
                            try:
                                import json
                                stream_part_data = json.loads(data_str)
                                
                                # Handle raw chunks - skip if not requested
                                if (stream_part_data.get("type") == "raw" and 
                                    not kwargs.get("include_raw_chunks", False)):
                                    continue
                                
                                # Convert timestamp strings to datetime objects
                                if (stream_part_data.get("type") == "response-metadata" and
                                    stream_part_data.get("timestamp") and
                                    isinstance(stream_part_data["timestamp"], str)):
                                    stream_part_data["timestamp"] = datetime.fromisoformat(
                                        stream_part_data["timestamp"].replace('Z', '+00:00')
                                    )
                                
                                # Yield the stream part
                                yield StreamPart(**stream_part_data)
                                
                            except json.JSONDecodeError:
                                continue  # Skip malformed JSON
                                
        except Exception as error:
            auth_method = self._parse_auth_method(headers)
            raise as_gateway_error(error, auth_method)
    
    async def _prepare_args(
        self,
        prompt: Union[str, List[Dict[str, Any]]],
        options: GenerateTextOptions,
        **kwargs
    ) -> Dict[str, Any]:
        """Prepare arguments for API call"""
        
        # Convert string prompt to message format
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        else:
            messages = prompt
        
        # Encode file parts to base64 if present
        messages = await self._maybe_encode_file_parts(messages)
        
        args = {
            "prompt": messages,
            **options.model_dump(exclude_none=True),
            **kwargs
        }
        
        return args
    
    async def _maybe_encode_file_parts(
        self, 
        messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Encode file parts in messages to base64"""
        
        for message in messages:
            if "content" in message and isinstance(message["content"], list):
                for part in message["content"]:
                    if isinstance(part, dict) and part.get("type") == "file":
                        data = part.get("data")
                        
                        # Convert binary data to base64 data URL
                        if isinstance(data, (bytes, bytearray)):
                            media_type = part.get("mediaType", "application/octet-stream")
                            base64_data = base64.b64encode(data).decode('utf-8')
                            part["data"] = f"data:{media_type};base64,{base64_data}"
        
        return messages
    
    def _get_url(self) -> str:
        """Get the language model endpoint URL"""
        return f"{self.config.base_url}/language-model"
    
    def _get_model_config_headers(self, streaming: bool) -> Dict[str, str]:
        """Get model configuration headers"""
        return {
            "ai-language-model-specification-version": "2",
            "ai-language-model-id": self.model_id,
            "ai-language-model-streaming": str(streaming).lower()
        }
    
    def _parse_auth_method(self, headers: Dict[str, str]) -> Optional[str]:
        """Parse authentication method from headers"""
        return headers.get("ai-gateway-auth-method")