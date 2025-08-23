"""Stream simulation utilities for testing."""

import asyncio
from typing import AsyncIterator, List, TypeVar, Iterable, Any

T = TypeVar('T')

async def simulate_readable_stream(
    items: List[T],
    delay: float = 0.01
) -> AsyncIterator[T]:
    """Simulate a readable stream from a list of items.
    
    This is useful for testing streaming functionality by converting
    a list of items into an async iterator with optional delays.
    
    Args:
        items: List of items to stream
        delay: Delay between items in seconds
        
    Yields:
        Items from the list with optional delays
        
    Example:
        ```python
        chunks = ["Hello", " ", "world", "!"]
        async for chunk in simulate_readable_stream(chunks):
            print(chunk, end="")
        # Output: Hello world!
        ```
    """
    for item in items:
        if delay > 0:
            await asyncio.sleep(delay)
        yield item


async def convert_array_to_async_iterable(items: List[T]) -> AsyncIterator[T]:
    """Convert a regular list to an async iterator.
    
    Args:
        items: List to convert
        
    Yields:
        Items from the list
    """
    for item in items:
        yield item


async def convert_async_iterable_to_array(stream: AsyncIterator[T]) -> List[T]:
    """Convert an async iterator to a list.
    
    Args:
        stream: Async iterator to convert
        
    Returns:
        List of all items from the stream
    """
    result = []
    async for item in stream:
        result.append(item)
    return result


class MockReadableStream:
    """Mock readable stream for testing."""
    
    def __init__(self, chunks: List[str], delay: float = 0.0):
        self.chunks = chunks
        self.delay = delay
        self.index = 0
        self.closed = False
    
    def __aiter__(self):
        return self
    
    async def __anext__(self):
        if self.index >= len(self.chunks) or self.closed:
            raise StopAsyncIteration
        
        if self.delay > 0:
            await asyncio.sleep(self.delay)
        
        chunk = self.chunks[self.index]
        self.index += 1
        return chunk
    
    async def close(self):
        """Close the stream."""
        self.closed = True
    
    async def read(self, size: int = -1) -> str:
        """Read data from stream."""
        if self.index >= len(self.chunks) or self.closed:
            return ""
        
        chunk = self.chunks[self.index]
        self.index += 1
        
        if self.delay > 0:
            await asyncio.sleep(self.delay)
        
        return chunk


class StreamCollector:
    """Utility to collect items from an async stream."""
    
    def __init__(self):
        self.items: List[Any] = []
        self.errors: List[Exception] = []
        self.finished = False
    
    async def collect(self, stream: AsyncIterator[T]) -> List[T]:
        """Collect all items from a stream.
        
        Args:
            stream: Stream to collect from
            
        Returns:
            List of all items
            
        Raises:
            Exception: If stream raises an exception
        """
        try:
            async for item in stream:
                self.items.append(item)
        except Exception as e:
            self.errors.append(e)
            raise
        finally:
            self.finished = True
        
        return self.items
    
    def assert_items(self, expected: List[Any]):
        """Assert collected items match expected."""
        assert self.items == expected, f"Expected {expected}, got {self.items}"
    
    def assert_no_errors(self):
        """Assert no errors occurred."""
        assert not self.errors, f"Expected no errors, got {self.errors}"


def create_mock_text_stream(text: str, chunk_size: int = 1) -> AsyncIterator[str]:
    """Create a mock text stream by splitting text into chunks.
    
    Args:
        text: Text to split into chunks
        chunk_size: Size of each chunk
        
    Returns:
        Async iterator of text chunks
    """
    chunks = [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]
    return convert_array_to_async_iterable(chunks)


async def create_mock_json_stream(objects: List[dict]) -> AsyncIterator[str]:
    """Create a mock JSON stream from objects.
    
    Args:
        objects: List of objects to serialize
        
    Returns:
        Async iterator of JSON strings
    """
    import json
    for obj in objects:
        yield json.dumps(obj) + '\n'


class MockStreamResponse:
    """Mock response that supports streaming."""
    
    def __init__(self, content: str, chunks: Optional[List[str]] = None):
        self.content = content
        self.chunks = chunks or list(content)
        self.headers = {"content-type": "text/plain"}
        self.status_code = 200
    
    async def aiter_text(self, chunk_size: int = 1024) -> AsyncIterator[str]:
        """Iterate over response text."""
        for chunk in self.chunks:
            yield chunk
    
    async def text(self) -> str:
        """Get full response text."""
        return self.content
    
    async def json(self) -> dict:
        """Parse response as JSON."""
        import json
        return json.loads(self.content)


def assert_stream_equals(actual_stream: List[T], expected: List[T]):
    """Assert that a collected stream equals expected items."""
    assert actual_stream == expected, f"Stream mismatch:\nExpected: {expected}\nActual: {actual_stream}"


def assert_stream_contains(actual_stream: List[T], expected_item: T):
    """Assert that a stream contains a specific item."""
    assert expected_item in actual_stream, f"Item {expected_item} not found in stream {actual_stream}"