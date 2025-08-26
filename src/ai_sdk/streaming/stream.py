"""Stream utilities for AI SDK Python."""

from typing import Any, AsyncIterator, Iterator


class Stream:
    """Basic stream implementation."""
    
    def __init__(self, iterator):
        self._iterator = iterator
    
    def __iter__(self):
        return iter(self._iterator)
    
    def __aiter__(self):
        return aiter(self._iterator)


class AsyncStream:
    """Async stream implementation."""
    
    def __init__(self, iterator: AsyncIterator[Any]):
        self._iterator = iterator
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        return await self._iterator.__anext__()


def create_stream(iterator) -> Stream:
    """Create a stream from an iterator."""
    return Stream(iterator)


def create_async_stream(iterator: AsyncIterator[Any]) -> AsyncStream:
    """Create an async stream from an async iterator."""
    return AsyncStream(iterator)