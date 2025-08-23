"""
Smooth streaming functionality for AI SDK Python.

Provides utilities to smooth text streaming output with configurable delays
and chunking strategies for better user experience.
"""

import asyncio
import re
from typing import AsyncGenerator, Callable, Optional, Union

from ..providers.types import StreamPart


# Chunking patterns for different strategies
CHUNKING_PATTERNS = {
    "word": re.compile(r"\S+\s+", re.MULTILINE),
    "line": re.compile(r"\n+", re.MULTILINE),
}

# Type for custom chunk detection functions
ChunkDetector = Callable[[str], Optional[str]]


def smooth_stream(
    *,
    delay_ms: Optional[int] = 10,
    chunking: Union[str, re.Pattern, ChunkDetector] = "word",
) -> Callable[[AsyncGenerator[StreamPart, None]], AsyncGenerator[StreamPart, None]]:
    """
    Create a smooth streaming transform that adds delays between text chunks.
    
    This function creates a transform that can be applied to a stream of text
    to make it appear more naturally paced to users, rather than dumping
    all text at once.
    
    Args:
        delay_ms: Delay in milliseconds between chunks. Set to None to disable.
                 Defaults to 10ms for natural reading pace.
        chunking: How to split text into chunks:
                 - "word": Stream word by word (default)
                 - "line": Stream line by line
                 - re.Pattern: Custom regex pattern for chunking
                 - Callable: Custom function that returns next chunk
    
    Returns:
        A transform function that can be applied to a text stream
        
    Example:
        ```python
        from ai_sdk import stream_text
        from ai_sdk.streaming import smooth_stream
        
        # Create a smooth streaming transform
        smooth_transform = smooth_stream(delay_ms=15, chunking="word")
        
        # Apply to a text stream
        stream = stream_text(model, prompt="Tell me a story")
        smooth_stream_iter = smooth_transform(stream)
        
        async for chunk in smooth_stream_iter:
            if chunk.type == "text-delta":
                print(chunk.text_delta, end="", flush=True)
        ```
    """
    
    # Determine chunk detection strategy
    if isinstance(chunking, str):
        if chunking not in CHUNKING_PATTERNS:
            raise ValueError(f"Unknown chunking strategy: {chunking}. Use 'word', 'line', or provide custom pattern/function.")
        pattern = CHUNKING_PATTERNS[chunking]
        
        def detect_chunk(buffer: str) -> Optional[str]:
            match = pattern.search(buffer)
            if not match:
                return None
            return buffer[:match.end()]
    
    elif hasattr(chunking, 'search'):  # regex pattern
        def detect_chunk(buffer: str) -> Optional[str]:
            match = chunking.search(buffer)
            if not match:
                return None
            return buffer[:match.end()]
    
    elif callable(chunking):  # custom function
        detect_chunk = chunking
    
    else:
        raise ValueError("chunking must be 'word', 'line', a regex pattern, or a callable")
    
    async def transform_stream(stream: AsyncGenerator[StreamPart, None]) -> AsyncGenerator[StreamPart, None]:
        """Transform the stream with smooth output"""
        buffer = ""
        current_id = ""
        
        async for part in stream:
            # Handle non-text parts immediately
            if part.type != "text-delta":
                # Flush any remaining buffer first
                if buffer:
                    yield StreamPart(type="text-delta", text_delta=buffer, id=current_id)
                    buffer = ""
                
                yield part
                continue
            
            # Handle text deltas with smoothing
            text_delta = getattr(part, 'text_delta', getattr(part, 'text', ''))
            part_id = getattr(part, 'id', '')
            
            # If ID changed, flush buffer and start fresh
            if part_id != current_id and buffer:
                yield StreamPart(type="text-delta", text_delta=buffer, id=current_id)
                buffer = ""
            
            current_id = part_id
            buffer += text_delta
            
            # Extract chunks and stream them smoothly
            while True:
                chunk = detect_chunk(buffer)
                if chunk is None:
                    break
                
                # Yield the chunk
                yield StreamPart(type="text-delta", text_delta=chunk, id=current_id)
                buffer = buffer[len(chunk):]
                
                # Add delay between chunks (if specified)
                if delay_ms is not None and delay_ms > 0:
                    await asyncio.sleep(delay_ms / 1000.0)
        
        # Flush any remaining buffer
        if buffer:
            yield StreamPart(type="text-delta", text_delta=buffer, id=current_id)
    
    return transform_stream


def word_chunker(buffer: str) -> Optional[str]:
    """
    Custom chunker that extracts words with trailing whitespace.
    
    Args:
        buffer: Text buffer to extract chunk from
        
    Returns:
        Next word chunk or None if no complete word available
    """
    match = re.search(r'\S+\s+', buffer)
    if not match:
        return None
    return buffer[:match.end()]


def sentence_chunker(buffer: str) -> Optional[str]:
    """
    Custom chunker that extracts sentences ending with .!? 
    
    Args:
        buffer: Text buffer to extract chunk from
        
    Returns:
        Next sentence chunk or None if no complete sentence available
    """
    match = re.search(r'[^.!?]*[.!?]+\s*', buffer)
    if not match:
        return None
    return buffer[:match.end()]


def character_chunker(n: int = 1) -> ChunkDetector:
    """
    Create a chunker that extracts n characters at a time.
    
    Args:
        n: Number of characters per chunk
        
    Returns:
        Chunker function
    """
    def chunker(buffer: str) -> Optional[str]:
        if len(buffer) < n:
            return None
        return buffer[:n]
    
    return chunker