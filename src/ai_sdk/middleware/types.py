"""Type definitions for the middleware system.

This module defines type aliases and interfaces that align with the
existing AI SDK type system while providing the necessary abstractions
for middleware functionality.
"""

from typing import Dict, Any, List, Optional, Union
from typing_extensions import TypedDict

from ..providers.types import Message, Usage, FinishReason


class GenerateTextParams(TypedDict, total=False):
    """Parameters for text generation that middleware can transform."""
    
    messages: List[Message]
    system: Optional[str]
    max_tokens: Optional[int]
    temperature: Optional[float]
    top_p: Optional[float]
    top_k: Optional[int]
    frequency_penalty: Optional[float]
    presence_penalty: Optional[float]
    stop: Optional[Union[str, List[str]]]
    seed: Optional[int]
    tools: Optional[List[Dict[str, Any]]]
    tool_choice: Optional[Union[str, Dict[str, Any]]]
    headers: Optional[Dict[str, str]]
    extra_body: Optional[Dict[str, Any]]


class GenerateTextResult:
    """Result from text generation that middleware can process."""
    
    def __init__(
        self,
        text: str,
        usage: Optional[Usage] = None,
        finish_reason: Optional[FinishReason] = None,
        response_id: Optional[str] = None,
        **kwargs: Any
    ):
        self.text = text
        self.usage = usage
        self.finish_reason = finish_reason
        self.response_id = response_id
        self.__dict__.update(kwargs)


class StreamTextResult:
    """Result from streaming text generation."""
    
    def __init__(self, stream: Any):
        self.stream = stream
    
    def __aiter__(self):
        return self.stream.__aiter__()
    
    async def __anext__(self):
        return await self.stream.__anext__()