"""
Vercel Language Model implementation.
Provides access to Vercel's v0 API for framework-aware code generation.
"""

from typing import Any, Dict, List, Optional, AsyncIterator, Union
import json
from datetime import datetime
from ai_sdk.core.types import (
    LanguageModel, 
    GenerateOptions, 
    GenerateResult, 
    StreamOptions,
    Usage,
    Message,
    ChatPrompt
)
from ai_sdk.errors.base import AISDKError
from ai_sdk.utils.http import create_http_client
from ai_sdk.utils.json import parse_json_stream
from .types import VercelChatModelId, VercelLanguageModelOptions


class VercelLanguageModel(LanguageModel):
    """
    Vercel v0 Language Model implementation.
    
    The v0 API is optimized for building modern web applications with:
    - Framework-aware completions (Next.js, React, Vue, Svelte)
    - Auto-fix capabilities for common coding issues
    - Quick edit features for inline code improvements
    - Multimodal support (text and image inputs)
    """
    
    def __init__(
        self,
        model_id: VercelChatModelId,
        api_key: str,
        base_url: str = "https://api.v0.dev/v1",
        max_retries: int = 3,
        timeout: float = 60.0,
    ):
        self.model_id = model_id
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.max_retries = max_retries
        self.timeout = timeout
        self.http_client = create_http_client(timeout=timeout, max_retries=max_retries)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Vercel API requests."""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ai-sdk-python",
        }
    
    async def _prepare_messages(self, prompt: Union[str, ChatPrompt]) -> List[Dict[str, Any]]:
        """Convert AI SDK messages to Vercel API format (OpenAI-compatible)."""
        if isinstance(prompt, str):
            return [{"role": "user", "content": prompt}]
        
        messages = []
        for message in prompt:
            if message.role == "system":
                messages.append({
                    "role": "system",
                    "content": message.content
                })
            elif message.role == "user":
                if isinstance(message.content, str):
                    messages.append({
                        "role": "user", 
                        "content": message.content
                    })
                else:
                    # Handle multimodal content
                    content = []
                    for part in message.content:
                        if part.type == "text":
                            content.append({
                                "type": "text",
                                "text": part.text
                            })
                        elif part.type == "image":
                            content.append({
                                "type": "image_url",
                                "image_url": {
                                    "url": part.image if isinstance(part.image, str) else part.image.url
                                }
                            })
                    messages.append({
                        "role": "user",
                        "content": content
                    })
            elif message.role == "assistant":
                messages.append({
                    "role": "assistant",
                    "content": message.content
                })
        
        return messages
    
    async def _prepare_request_body(
        self, 
        prompt: Union[str, ChatPrompt], 
        options: Optional[GenerateOptions] = None
    ) -> Dict[str, Any]:
        """Prepare the request body for Vercel API."""
        messages = await self._prepare_messages(prompt)
        
        body = {
            "model": self.model_id,
            "messages": messages,
            "stream": False,
        }
        
        if options:
            if options.max_tokens:
                body["max_tokens"] = options.max_tokens
            if options.temperature is not None:
                body["temperature"] = options.temperature
            if options.top_p is not None:
                body["top_p"] = options.top_p
            if options.stop:
                body["stop"] = options.stop
            
            # Handle provider-specific options
            if hasattr(options, 'provider_options') and options.provider_options:
                vercel_options = options.provider_options.get('vercel', {})
                if isinstance(vercel_options, dict):
                    vercel_opts = VercelLanguageModelOptions.model_validate(vercel_options)
                    
                    # Add framework-specific context
                    if vercel_opts.framework:
                        body.setdefault("metadata", {})["framework"] = vercel_opts.framework
                    
                    if vercel_opts.enable_auto_fix:
                        body.setdefault("metadata", {})["auto_fix"] = True
                    
                    if vercel_opts.enable_quick_edit:
                        body.setdefault("metadata", {})["quick_edit"] = True
                    
                    if vercel_opts.project_type:
                        body.setdefault("metadata", {})["project_type"] = vercel_opts.project_type
                    
                    if vercel_opts.design_system:
                        body.setdefault("metadata", {})["design_system"] = vercel_opts.design_system
                    
                    if vercel_opts.typescript is not None:
                        body.setdefault("metadata", {})["typescript"] = vercel_opts.typescript
        
        return body
    
    async def generate(
        self,
        prompt: Union[str, ChatPrompt],
        options: Optional[GenerateOptions] = None
    ) -> GenerateResult:
        """
        Generate text using the Vercel v0 API.
        
        Args:
            prompt: Text prompt or chat conversation
            options: Generation options
            
        Returns:
            GenerateResult with the generated text and metadata
        """
        url = f"{self.base_url}/chat/completions"
        body = await self._prepare_request_body(prompt, options)
        headers = self._get_headers()
        
        try:
            async with self.http_client as client:
                response = await client.post(
                    url,
                    json=body,
                    headers=headers
                )
                
                if response.status_code != 200:
                    error_data = response.json() if response.content else {}
                    error_message = error_data.get('error', {}).get('message', 'Unknown error')
                    raise AISDKError(
                        f"Vercel API request failed: {response.status_code} - {error_message}"
                    )
                
                result_data = response.json()
                
                # Extract the generated text
                choice = result_data.get('choices', [{}])[0]
                message = choice.get('message', {})
                text = message.get('content', '')
                
                # Extract usage information
                usage_data = result_data.get('usage', {})
                usage = Usage(
                    input_tokens=usage_data.get('prompt_tokens', 0),
                    output_tokens=usage_data.get('completion_tokens', 0),
                    total_tokens=usage_data.get('total_tokens', 0)
                )
                
                # Extract finish reason
                finish_reason = choice.get('finish_reason', 'stop')
                
                return GenerateResult(
                    text=text,
                    usage=usage,
                    finish_reason=finish_reason,
                    response_metadata={
                        "model": result_data.get('model', self.model_id),
                        "created": result_data.get('created'),
                        "headers": dict(response.headers)
                    }
                )
                
        except Exception as e:
            if isinstance(e, AISDKError):
                raise
            raise AISDKError(f"Failed to generate text: {str(e)}") from e
    
    async def stream(
        self,
        prompt: Union[str, ChatPrompt],
        options: Optional[StreamOptions] = None
    ) -> AsyncIterator[Any]:
        """
        Stream text generation using the Vercel v0 API.
        
        Args:
            prompt: Text prompt or chat conversation
            options: Streaming options
            
        Yields:
            Stream chunks with generated text deltas
        """
        url = f"{self.base_url}/chat/completions"
        
        # Prepare body with streaming enabled
        body = await self._prepare_request_body(prompt, options)
        body["stream"] = True
        
        headers = self._get_headers()
        
        try:
            async with self.http_client as client:
                async with client.stream(
                    'POST',
                    url,
                    json=body,
                    headers=headers
                ) as response:
                    
                    if response.status_code != 200:
                        error_text = await response.aread()
                        try:
                            error_data = json.loads(error_text)
                            error_message = error_data.get('error', {}).get('message', 'Unknown error')
                        except:
                            error_message = error_text.decode() if error_text else 'Unknown error'
                        
                        raise AISDKError(
                            f"Vercel streaming request failed: {response.status_code} - {error_message}"
                        )
                    
                    # Parse the streaming response
                    async for chunk in parse_json_stream(response.aiter_lines()):
                        if chunk.get('choices'):
                            choice = chunk['choices'][0]
                            delta = choice.get('delta', {})
                            
                            if 'content' in delta and delta['content']:
                                yield {
                                    'type': 'text-delta',
                                    'text': delta['content']
                                }
                            
                            if choice.get('finish_reason'):
                                # Extract usage from final chunk if available
                                usage_data = chunk.get('usage', {})
                                usage = Usage(
                                    input_tokens=usage_data.get('prompt_tokens', 0),
                                    output_tokens=usage_data.get('completion_tokens', 0),
                                    total_tokens=usage_data.get('total_tokens', 0)
                                )
                                
                                yield {
                                    'type': 'finish',
                                    'finish_reason': choice['finish_reason'],
                                    'usage': usage
                                }
                                
        except Exception as e:
            if isinstance(e, AISDKError):
                raise
            raise AISDKError(f"Failed to stream text: {str(e)}") from e
    
    async def close(self):
        """Close the HTTP client."""
        if hasattr(self.http_client, 'aclose'):
            await self.http_client.aclose()