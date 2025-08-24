"""Core types - compatibility shim with independent type definitions."""

from typing import Any, Dict, List, Optional, Union
from abc import ABC, abstractmethod
from enum import Enum


# Core Enum Types
class FinishReason(str, Enum):
    """Reason why the model stopped generating."""
    
    STOP = "stop"
    LENGTH = "length"
    CONTENT_FILTER = "content-filter"
    TOOL_CALLS = "tool-calls"
    ERROR = "error"
    OTHER = "other"
    UNKNOWN = "unknown"


class MessageRole(str, Enum):
    """Message role in a conversation."""
    
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


# Core Data Classes
class Usage:
    """Usage statistics for a model call."""
    
    def __init__(self, prompt_tokens: int = 0, completion_tokens: int = 0, total_tokens: int = 0, **kwargs):
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens
        self.total_tokens = total_tokens
        for key, value in kwargs.items():
            setattr(self, key, value)


class ProviderMetadata:
    """Provider-specific metadata."""
    
    def __init__(self, data: Dict[str, Any] = None):
        self.data = data or {}


# Content Types
class TextContent:
    """Text content in a message."""
    
    def __init__(self, text: str):
        self.type = "text"
        self.text = text


class ImageContent:
    """Image content in a message."""
    
    def __init__(self, image: Union[str, bytes], mime_type: Optional[str] = None):
        self.type = "image"
        self.image = image
        self.mime_type = mime_type


class ToolCallContent:
    """Tool call content in a message."""
    
    def __init__(self, tool_call_id: str, tool_name: str, args: Dict[str, Any]):
        self.type = "tool-call"
        self.tool_call_id = tool_call_id
        self.tool_name = tool_name
        self.args = args


class ToolResultContent:
    """Tool result content in a message."""
    
    def __init__(self, tool_call_id: str, result: Any, is_error: bool = False):
        self.type = "tool-result"
        self.tool_call_id = tool_call_id
        self.result = result
        self.is_error = is_error


# Union of all content types
Content = Union[TextContent, ImageContent, ToolCallContent, ToolResultContent]

# Alias for ContentPart
ContentPart = Content


# Message Types
class Message:
    """A message in a conversation."""
    
    def __init__(self, role: str, content: Union[str, List[Content]], name: Optional[str] = None, tool_call_id: Optional[str] = None):
        self.role = role
        self.content = content
        self.name = name
        self.tool_call_id = tool_call_id


# Base Provider Classes - Abstract definitions
class Provider(ABC):
    """Base class for AI providers."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs: Any) -> None:
        self.api_key = api_key
        self.config = kwargs
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Name of the provider."""
        pass
    
    @abstractmethod
    def language_model(self, model_id: str, **kwargs: Any) -> 'LanguageModel':
        """Get a language model instance."""
        pass


class LanguageModel(ABC):
    """Base class for language models."""
    pass


class EmbeddingModel(ABC):
    """Base class for embedding models."""
    pass


class ImageModel(ABC):
    """Base class for image models."""
    pass


class TranscriptionModel(ABC):
    """Base class for transcription models."""
    pass


class SpeechModel(ABC):
    """Base class for speech models."""
    pass


# Define core result types directly to avoid circular imports
class GenerateTextResult:
    """Result from text generation."""
    
    def __init__(
        self,
        text: str,
        content: List[Any],
        finish_reason: Any,
        usage: Any,
        provider_metadata: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
        response_metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.text = text
        self.content = content
        self.finish_reason = finish_reason
        self.usage = usage
        self.provider_metadata = provider_metadata
        self.request_metadata = request_metadata
        self.response_metadata = response_metadata


class StreamTextResult:
    """Result from streaming text generation."""
    
    def __init__(self, stream: Any):
        self.stream = stream
    
    def __aiter__(self):
        return self.stream.__aiter__()
    
    async def __anext__(self):
        return await self.stream.__anext__()


class TextStreamPart:
    """Text stream part."""
    
    def __init__(self, text_delta: Optional[str] = None, **kwargs):
        self.text_delta = text_delta
        for key, value in kwargs.items():
            setattr(self, key, value)


# Chat Prompt and Message Types (Higher-level API)
class ChatPrompt:
    """Chat prompt containing a list of messages."""
    
    def __init__(self, messages: List['BaseMessage']):
        self.messages = messages


class BaseMessage:
    """Base message class."""
    
    def __init__(self, content: Union[str, List[Any]], role: str, **kwargs):
        self.content = content
        self.role = role
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_message(self) -> Message:
        """Convert to providers.types.Message format."""
        return Message(
            role=self.role,
            content=self.content
        )


class SystemMessage(BaseMessage):
    """System message."""
    
    def __init__(self, content: Union[str, List[Any]], **kwargs):
        super().__init__(content=content, role="system", **kwargs)


class UserMessage(BaseMessage):
    """User message."""
    
    def __init__(self, content: Union[str, List[Any]], **kwargs):
        super().__init__(content=content, role="user", **kwargs)


class AssistantMessage(BaseMessage):
    """Assistant message."""
    
    def __init__(self, content: Union[str, List[Any]], **kwargs):
        super().__init__(content=content, role="assistant", **kwargs)


class ToolMessage(BaseMessage):
    """Tool message."""
    
    def __init__(self, content: Union[str, List[Any]], tool_call_id: Optional[str] = None, **kwargs):
        super().__init__(content=content, role="tool", **kwargs)
        self.tool_call_id = tool_call_id


# Additional Result Types
class GenerateEmbeddingResult:
    """Result from embedding generation."""
    
    def __init__(
        self,
        embedding: List[float],
        usage: Any,
        provider_metadata: Optional[Dict[str, Any]] = None,
    ):
        self.embedding = embedding
        self.usage = usage
        self.provider_metadata = provider_metadata


class GenerateEmbeddingOptions:
    """Options for embedding generation."""
    
    def __init__(
        self,
        value: Any,
        headers: Optional[Dict[str, str]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        self.value = value
        self.headers = headers
        self.extra_body = extra_body
        for key, val in kwargs.items():
            setattr(self, key, val)


class GenerateImageOptions:
    """Options for image generation."""
    
    def __init__(
        self,
        prompt: str,
        n: int = 1,
        size: Optional[str] = None,
        aspect_ratio: Optional[str] = None,
        seed: Optional[int] = None,
        **kwargs
    ):
        self.prompt = prompt
        self.n = n
        self.size = size
        self.aspect_ratio = aspect_ratio
        self.seed = seed
        for key, val in kwargs.items():
            setattr(self, key, val)


class GenerateImageResult:
    """Result from image generation."""
    
    def __init__(
        self,
        images: List[bytes],
        warnings: Optional[List[Any]] = None,
        provider_metadata: Optional[Dict[str, Any]] = None,
    ):
        self.images = images
        self.warnings = warnings or []
        self.provider_metadata = provider_metadata


class ImageResult:
    """Single image result."""
    
    def __init__(self, data: bytes, format: Optional[str] = None):
        self.data = data
        self.format = format


class TranscriptionSegment:
    """Transcription segment with timing information."""
    
    def __init__(self, text: str, start: float, end: float):
        self.text = text
        self.start = start
        self.end = end


# Alias for compatibility - BaseLanguageModel should be imported from providers.base
BaseLanguageModel = LanguageModel


# Additional types needed by providers
class GenerateTextOptions:
    """Options for text generation."""
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class StreamTextOptions:
    """Options for streaming text generation."""
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class TextStartPart:
    """Start of text streaming."""
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


class TextDeltaPart:
    """Text delta in streaming."""
    
    def __init__(self, text_delta: str, **kwargs):
        self.text_delta = text_delta
        for key, value in kwargs.items():
            setattr(self, key, value)


class FinishPart:
    """Finish part in streaming."""
    
    def __init__(self, finish_reason: FinishReason, **kwargs):
        self.finish_reason = finish_reason
        for key, value in kwargs.items():
            setattr(self, key, value)


class ToolCallPart:
    """Tool call part in streaming."""
    
    def __init__(self, tool_call_id: str, tool_name: str, args: Dict[str, Any], **kwargs):
        self.tool_call_id = tool_call_id
        self.tool_name = tool_name
        self.args = args
        for key, value in kwargs.items():
            setattr(self, key, value)


class ToolResultPart:
    """Tool result part in streaming."""
    
    def __init__(self, tool_call_id: str, result: Any, **kwargs):
        self.tool_call_id = tool_call_id
        self.result = result
        for key, value in kwargs.items():
            setattr(self, key, value)


class ResponseMetadata:
    """Response metadata."""
    
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)