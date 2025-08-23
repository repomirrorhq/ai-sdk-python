"""Google Vertex AI language model implementation."""

import json
from typing import Any, Dict, List, Optional, AsyncIterator, Union

import httpx
from pydantic import BaseModel

from ...providers.base import LanguageModel
from ...providers.types import (
    GenerateOptions,
    StreamOptions,
    GenerateResult,
    StreamResult,
    Usage,
    FinishReason,
    Content,
    Message,
)
from ...errors.base import AISDKError
from ...utils.http import make_request
from .config import GoogleVertexConfig, GoogleVertexAuth
from .types import GoogleVertexModelId
from .message_converter import convert_to_vertex_messages, convert_from_vertex_response
from .utils import map_vertex_finish_reason


class GoogleVertexLanguageModel(LanguageModel):
    """Google Vertex AI language model implementation."""
    
    def __init__(
        self,
        model_id: GoogleVertexModelId,
        config: GoogleVertexConfig,
        auth: GoogleVertexAuth,
        **kwargs: Any,
    ):
        """
        Initialize Google Vertex AI language model.
        
        Args:
            model_id: The Vertex AI model ID
            config: Configuration object
            auth: Authentication handler
            **kwargs: Additional model options
        """
        super().__init__()
        self.model_id = model_id
        self.config = config
        self.auth = auth
        self.model_options = kwargs
    
    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "google-vertex"
    
    async def generate(
        self,
        messages: List[Message],
        options: Optional[GenerateOptions] = None,
        **kwargs: Any,
    ) -> GenerateResult:
        """
        Generate text response.
        
        Args:
            messages: List of conversation messages
            options: Generation options
            **kwargs: Additional options
            
        Returns:
            GenerateResult with response
        """
        # Get authentication headers
        headers = await self.auth.get_auth_headers()
        
        # Convert messages to Vertex AI format
        vertex_messages = convert_to_vertex_messages(messages)
        
        # Build request payload
        request_body = self._build_request_body(vertex_messages, options, **kwargs)
        
        # Make API request
        url = f"{self.config.base_url}/models/{self.model_id}:generateContent"
        
        try:
            response = await make_request(
                method="POST",
                url=url,
                headers=headers,
                json=request_body,
                http_client=self.config.http_client,
            )
            
            # Parse response
            return self._parse_generate_response(response)
            
        except Exception as e:
            raise AISDKError(f"Google Vertex AI generation failed: {e}")
    
    async def stream(
        self,
        messages: List[Message],
        options: Optional[StreamOptions] = None,
        **kwargs: Any,
    ) -> AsyncIterator[StreamResult]:
        """
        Stream text response.
        
        Args:
            messages: List of conversation messages
            options: Streaming options
            **kwargs: Additional options
            
        Yields:
            StreamResult chunks
        """
        # Get authentication headers
        headers = await self.auth.get_auth_headers()
        
        # Convert messages to Vertex AI format
        vertex_messages = convert_to_vertex_messages(messages)
        
        # Build request payload (with streaming enabled)
        request_body = self._build_request_body(vertex_messages, options, **kwargs)
        
        # Make streaming API request
        url = f"{self.config.base_url}/models/{self.model_id}:streamGenerateContent"
        
        try:
            http_client = self.config.http_client or httpx.AsyncClient()
            
            async with http_client.stream(
                method="POST",
                url=url,
                headers=headers,
                json=request_body,
            ) as response:
                response.raise_for_status()
                
                async for chunk in self._parse_stream_response(response):
                    yield chunk
                    
        except Exception as e:
            raise AISDKError(f"Google Vertex AI streaming failed: {e}")
    
    def _build_request_body(
        self,
        messages: List[Dict[str, Any]],
        options: Optional[Union[GenerateOptions, StreamOptions]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Build request body for Vertex AI API."""
        body = {
            "contents": messages,
        }
        
        # Add generation config if options provided
        generation_config = {}
        
        if options:
            if hasattr(options, 'max_tokens') and options.max_tokens:
                generation_config["maxOutputTokens"] = options.max_tokens
            if hasattr(options, 'temperature') and options.temperature is not None:
                generation_config["temperature"] = options.temperature
            if hasattr(options, 'top_p') and options.top_p is not None:
                generation_config["topP"] = options.top_p
            if hasattr(options, 'top_k') and options.top_k is not None:
                generation_config["topK"] = options.top_k
            if hasattr(options, 'stop') and options.stop:
                generation_config["stopSequences"] = options.stop
        
        # Add any additional kwargs to generation config
        for key, value in kwargs.items():
            if key in ["max_tokens", "temperature", "top_p", "top_k", "stop"]:
                continue  # Already handled above
            if key == "response_format" and value:
                generation_config["responseMimeType"] = "application/json"
            else:
                generation_config[key] = value
        
        if generation_config:
            body["generationConfig"] = generation_config
        
        # Add safety settings (optional)
        body["safetySettings"] = [
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT", 
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
        
        return body
    
    def _parse_generate_response(self, response: Dict[str, Any]) -> GenerateResult:
        """Parse non-streaming generation response."""
        try:
            candidates = response.get("candidates", [])
            if not candidates:
                raise AISDKError("No candidates in response")
            
            candidate = candidates[0]
            content = candidate.get("content", {})
            parts = content.get("parts", [])
            
            # Extract text content
            text_parts = []
            for part in parts:
                if "text" in part:
                    text_parts.append(part["text"])
            
            text = "".join(text_parts)
            
            # Extract usage information
            usage_metadata = response.get("usageMetadata", {})
            usage = Usage(
                prompt_tokens=usage_metadata.get("promptTokenCount", 0),
                completion_tokens=usage_metadata.get("candidatesTokenCount", 0),
                total_tokens=usage_metadata.get("totalTokenCount", 0),
            )
            
            # Extract finish reason
            finish_reason_str = candidate.get("finishReason", "STOP")
            finish_reason = map_vertex_finish_reason(finish_reason_str)
            
            return GenerateResult(
                text=text,
                usage=usage,
                finish_reason=finish_reason,
                response_data=response,
            )
            
        except Exception as e:
            raise AISDKError(f"Failed to parse Vertex AI response: {e}")
    
    async def _parse_stream_response(self, response) -> AsyncIterator[StreamResult]:
        """Parse streaming response."""
        try:
            async for line in response.aiter_lines():
                if not line or not line.strip():
                    continue
                
                # Remove 'data: ' prefix if present
                if line.startswith("data: "):
                    line = line[6:]
                
                try:
                    chunk_data = json.loads(line)
                except json.JSONDecodeError:
                    continue
                
                candidates = chunk_data.get("candidates", [])
                if not candidates:
                    continue
                
                candidate = candidates[0]
                content = candidate.get("content", {})
                parts = content.get("parts", [])
                
                # Extract text content from parts
                text_parts = []
                for part in parts:
                    if "text" in part:
                        text_parts.append(part["text"])
                
                text = "".join(text_parts)
                
                if text:
                    yield StreamResult(
                        delta=text,
                        response_data=chunk_data,
                    )
                
                # Check for finish reason in final chunk
                finish_reason_str = candidate.get("finishReason")
                if finish_reason_str:
                    finish_reason = map_vertex_finish_reason(finish_reason_str)
                    yield StreamResult(
                        delta="",
                        finish_reason=finish_reason,
                        response_data=chunk_data,
                    )
                    break
                    
        except Exception as e:
            raise AISDKError(f"Failed to parse Vertex AI stream: {e}")