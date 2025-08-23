"""Response builders for creating test responses."""

import json
import time
from typing import Any, Dict, List, Optional, Union


def build_text_response(
    text: str = "Test response",
    finish_reason: str = "stop",
    usage_prompt_tokens: int = 10,
    usage_completion_tokens: int = 20,
    provider_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a text generation response for testing.
    
    Args:
        text: Generated text
        finish_reason: Reason generation finished
        usage_prompt_tokens: Number of prompt tokens
        usage_completion_tokens: Number of completion tokens
        provider_metadata: Additional provider metadata
        
    Returns:
        Response dictionary
    """
    return {
        "text": text,
        "finish_reason": finish_reason,
        "usage": {
            "prompt_tokens": usage_prompt_tokens,
            "completion_tokens": usage_completion_tokens,
            "total_tokens": usage_prompt_tokens + usage_completion_tokens,
        },
        "provider_metadata": provider_metadata or {},
        "response_id": f"test-response-{int(time.time())}",
    }


def build_object_response(
    obj: Any,
    finish_reason: str = "stop",
    usage_prompt_tokens: int = 10,
    usage_completion_tokens: int = 15,
    provider_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a structured object response for testing.
    
    Args:
        obj: The generated object
        finish_reason: Reason generation finished
        usage_prompt_tokens: Number of prompt tokens
        usage_completion_tokens: Number of completion tokens
        provider_metadata: Additional provider metadata
        
    Returns:
        Response dictionary
    """
    return {
        "object": obj,
        "finish_reason": finish_reason,
        "usage": {
            "prompt_tokens": usage_prompt_tokens,
            "completion_tokens": usage_completion_tokens,
            "total_tokens": usage_prompt_tokens + usage_completion_tokens,
        },
        "provider_metadata": provider_metadata or {},
        "response_id": f"test-object-response-{int(time.time())}",
    }


def build_tool_call_response(
    tool_calls: List[Dict[str, Any]],
    text: str = "",
    finish_reason: str = "tool_calls",
    usage_prompt_tokens: int = 15,
    usage_completion_tokens: int = 25,
    provider_metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a tool call response for testing.
    
    Args:
        tool_calls: List of tool calls
        text: Any text content
        finish_reason: Reason generation finished
        usage_prompt_tokens: Number of prompt tokens
        usage_completion_tokens: Number of completion tokens
        provider_metadata: Additional provider metadata
        
    Returns:
        Response dictionary
    """
    return {
        "text": text,
        "tool_calls": tool_calls,
        "finish_reason": finish_reason,
        "usage": {
            "prompt_tokens": usage_prompt_tokens,
            "completion_tokens": usage_completion_tokens,
            "total_tokens": usage_prompt_tokens + usage_completion_tokens,
        },
        "provider_metadata": provider_metadata or {},
        "response_id": f"test-tool-response-{int(time.time())}",
    }


def build_error_response(
    error_message: str,
    error_code: Optional[str] = None,
    error_type: str = "api_error",
) -> Dict[str, Any]:
    """Build an error response for testing.
    
    Args:
        error_message: Error message
        error_code: Optional error code
        error_type: Type of error
        
    Returns:
        Error response dictionary
    """
    return {
        "error": {
            "message": error_message,
            "type": error_type,
            "code": error_code,
        },
        "response_id": f"test-error-{int(time.time())}",
    }


def build_stream_chunk(
    chunk_type: str = "text",
    content: str = "chunk",
    index: int = 0,
    delta: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a streaming chunk for testing.
    
    Args:
        chunk_type: Type of chunk (text, tool_call, etc.)
        content: Chunk content
        index: Chunk index
        delta: Delta information
        
    Returns:
        Stream chunk dictionary
    """
    chunk = {
        "type": chunk_type,
        "index": index,
        "timestamp": time.time(),
    }
    
    if chunk_type == "text":
        chunk["text"] = content
    elif chunk_type == "text_delta":
        chunk["text_delta"] = content
    elif chunk_type == "tool_call_delta":
        chunk["tool_call_delta"] = delta or {"arguments": content}
    elif chunk_type == "finish":
        chunk["finish_reason"] = content
        chunk["usage"] = {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30,
        }
    
    return chunk


class ResponseBuilder:
    """Builder class for creating complex test responses."""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """Reset the builder to initial state."""
        self._text = ""
        self._tool_calls = []
        self._finish_reason = "stop"
        self._usage_prompt_tokens = 10
        self._usage_completion_tokens = 20
        self._provider_metadata = {}
        self._error = None
        return self
    
    def with_text(self, text: str):
        """Add text to the response."""
        self._text = text
        return self
    
    def with_tool_call(
        self,
        name: str,
        arguments: Dict[str, Any],
        call_id: Optional[str] = None,
    ):
        """Add a tool call to the response."""
        self._tool_calls.append({
            "id": call_id or f"call_{len(self._tool_calls)}",
            "type": "function",
            "function": {
                "name": name,
                "arguments": arguments,
            }
        })
        if self._finish_reason == "stop":
            self._finish_reason = "tool_calls"
        return self
    
    def with_finish_reason(self, reason: str):
        """Set the finish reason."""
        self._finish_reason = reason
        return self
    
    def with_usage(
        self,
        prompt_tokens: int,
        completion_tokens: int,
    ):
        """Set usage information."""
        self._usage_prompt_tokens = prompt_tokens
        self._usage_completion_tokens = completion_tokens
        return self
    
    def with_metadata(self, metadata: Dict[str, Any]):
        """Add provider metadata."""
        self._provider_metadata.update(metadata)
        return self
    
    def with_error(self, message: str, code: Optional[str] = None):
        """Add an error to the response."""
        self._error = {
            "message": message,
            "code": code,
            "type": "api_error",
        }
        return self
    
    def build(self) -> Dict[str, Any]:
        """Build the final response."""
        if self._error:
            return build_error_response(
                self._error["message"],
                self._error["code"],
                self._error["type"],
            )
        
        response = {
            "text": self._text,
            "finish_reason": self._finish_reason,
            "usage": {
                "prompt_tokens": self._usage_prompt_tokens,
                "completion_tokens": self._usage_completion_tokens,
                "total_tokens": self._usage_prompt_tokens + self._usage_completion_tokens,
            },
            "provider_metadata": self._provider_metadata,
            "response_id": f"test-builder-{int(time.time())}",
        }
        
        if self._tool_calls:
            response["tool_calls"] = self._tool_calls
        
        return response


class StreamBuilder:
    """Builder for creating streaming responses."""
    
    def __init__(self):
        self.chunks = []
    
    def add_text_chunk(self, text: str, index: Optional[int] = None):
        """Add a text chunk."""
        self.chunks.append(build_stream_chunk(
            "text_delta",
            text,
            index or len(self.chunks),
        ))
        return self
    
    def add_tool_call_chunk(
        self,
        name: str,
        arguments: Dict[str, Any],
        call_id: Optional[str] = None,
        index: Optional[int] = None,
    ):
        """Add a tool call chunk."""
        self.chunks.append(build_stream_chunk(
            "tool_call_delta",
            "",
            index or len(self.chunks),
            {
                "id": call_id or f"call_{len(self.chunks)}",
                "function": {
                    "name": name,
                    "arguments": json.dumps(arguments),
                }
            }
        ))
        return self
    
    def add_finish_chunk(self, reason: str = "stop"):
        """Add a finish chunk."""
        self.chunks.append(build_stream_chunk(
            "finish",
            reason,
            len(self.chunks),
        ))
        return self
    
    def build(self) -> List[Dict[str, Any]]:
        """Build the chunk list."""
        return self.chunks.copy()
    
    async def build_async_iterator(self):
        """Build an async iterator of chunks."""
        for chunk in self.chunks:
            yield chunk