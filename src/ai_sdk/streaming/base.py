"""Base streaming utilities for AI SDK Python."""

from typing import Any, AsyncIterator, Iterator, TypeVar, Generic

T = TypeVar('T')


class BaseStream(Generic[T]):
    """Base stream class."""
    
    def __init__(self, iterator: Iterator[T]):
        self._iterator = iterator
    
    def __iter__(self):
        return iter(self._iterator)


class BaseAsyncStream(Generic[T]):
    """Base async stream class."""
    
    def __init__(self, iterator: AsyncIterator[T]):
        self._iterator = iterator
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        return await self._iterator.__anext__()


class StreamableValue(Generic[T]):
    """A value that can be streamed."""
    
    def __init__(self, value: T):
        self.value = value
    
    def __str__(self):
        return str(self.value)
    
    def __repr__(self):
        return f"StreamableValue({self.value!r})"


class StreamingTextResult(BaseAsyncStream[str]):
    """Streaming text result."""
    
    def __init__(self, iterator: AsyncIterator[str]):
        super().__init__(iterator)
        self._full_text = ""
    
    async def __anext__(self):
        chunk = await super().__anext__()
        self._full_text += chunk
        return chunk
    
    @property
    def text_so_far(self) -> str:
        """Get accumulated text so far."""
        return self._full_text


class TextStreamChunk:
    """A chunk of text from a stream."""
    
    def __init__(self, text: str, chunk_type: str = "text"):
        self.text = text
        self.chunk_type = chunk_type
    
    def __str__(self):
        return self.text
    
    def __repr__(self):
        return f"TextStreamChunk(text={self.text!r}, chunk_type={self.chunk_type!r})"