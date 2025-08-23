"""
Tests for smooth streaming functionality

This test suite covers:
- Basic smooth streaming transforms
- Different chunking strategies (word, line, custom)
- Delay timing and behavior
- Edge cases and error handling
- Performance characteristics
"""

import asyncio
import pytest
import time
from typing import AsyncGenerator
from unittest.mock import patch

from ai_sdk.streaming import smooth_stream, word_chunker, sentence_chunker, character_chunker
from ai_sdk.providers.types import StreamPart


class TestSmoothStream:
    """Test suite for smooth streaming functionality"""
    
    async def create_mock_stream(self, text_chunks: list[str]) -> AsyncGenerator[StreamPart, None]:
        """Create a mock text stream for testing"""
        for chunk in text_chunks:
            yield StreamPart(type="text-delta", text_delta=chunk, id="test-id")
    
    async def create_mock_mixed_stream(self) -> AsyncGenerator[StreamPart, None]:
        """Create a mock stream with mixed part types"""
        yield StreamPart(type="stream-start")
        yield StreamPart(type="text-delta", text_delta="Hello ", id="1")
        yield StreamPart(type="text-delta", text_delta="world!", id="1")
        yield StreamPart(type="finish-reason", reason="stop")
        yield StreamPart(type="usage", prompt_tokens=5, completion_tokens=2)
    
    @pytest.mark.asyncio
    async def test_word_chunking_basic(self):
        """Test basic word-by-word chunking"""
        transform = smooth_stream(delay_ms=None, chunking="word")
        
        input_stream = self.create_mock_stream(["Hello world! ", "This is ", "a test."])
        output_chunks = []
        
        async for chunk in transform(input_stream):
            if chunk.type == "text-delta":
                output_chunks.append(chunk.text_delta)
        
        # Should split into words with spaces
        expected = ["Hello ", "world! ", "This ", "is ", "a ", "test."]
        assert output_chunks == expected
    
    @pytest.mark.asyncio
    async def test_line_chunking(self):
        """Test line-by-line chunking"""
        transform = smooth_stream(delay_ms=None, chunking="line")
        
        input_stream = self.create_mock_stream(["Line 1\nLine 2\n", "Line 3"])
        output_chunks = []
        
        async for chunk in transform(input_stream):
            if chunk.type == "text-delta":
                output_chunks.append(chunk.text_delta)
        
        expected = ["Line 1\n", "Line 2\n", "Line 3"]
        assert output_chunks == expected
    
    @pytest.mark.asyncio
    async def test_character_chunking(self):
        """Test character-by-character chunking"""
        char_chunker = character_chunker(1)
        transform = smooth_stream(delay_ms=None, chunking=char_chunker)
        
        input_stream = self.create_mock_stream(["Hello"])
        output_chunks = []
        
        async for chunk in transform(input_stream):
            if chunk.type == "text-delta":
                output_chunks.append(chunk.text_delta)
        
        expected = ["H", "e", "l", "l", "o"]
        assert output_chunks == expected
    
    @pytest.mark.asyncio
    async def test_character_chunking_multi_char(self):
        """Test multi-character chunking"""
        char_chunker = character_chunker(3)
        transform = smooth_stream(delay_ms=None, chunking=char_chunker)
        
        input_stream = self.create_mock_stream(["Hello World"])
        output_chunks = []
        
        async for chunk in transform(input_stream):
            if chunk.type == "text-delta":
                output_chunks.append(chunk.text_delta)
        
        expected = ["Hel", "lo ", "Wor", "ld"]
        assert output_chunks == expected
    
    @pytest.mark.asyncio
    async def test_sentence_chunking(self):
        """Test sentence-based chunking"""
        transform = smooth_stream(delay_ms=None, chunking=sentence_chunker)
        
        input_stream = self.create_mock_stream(["Hello world! ", "How are you? ", "I'm fine."])
        output_chunks = []
        
        async for chunk in transform(input_stream):
            if chunk.type == "text-delta":
                output_chunks.append(chunk.text_delta)
        
        expected = ["Hello world! ", "How are you? ", "I'm fine."]
        assert output_chunks == expected
    
    @pytest.mark.asyncio
    async def test_mixed_stream_parts(self):
        """Test that non-text parts pass through unchanged"""
        transform = smooth_stream(delay_ms=None, chunking="word")
        
        input_stream = self.create_mock_mixed_stream()
        output_parts = []
        
        async for chunk in transform(input_stream):
            output_parts.append((chunk.type, getattr(chunk, 'text_delta', None)))
        
        # Non-text parts should pass through, text should be chunked
        expected_types = ["stream-start", "text-delta", "text-delta", "finish-reason", "usage"]
        actual_types = [part[0] for part in output_parts]
        assert actual_types == expected_types
        
        # Check text was properly chunked
        text_parts = [part[1] for part in output_parts if part[0] == "text-delta"]
        expected_text = ["Hello ", "world!"]
        assert text_parts == expected_text
    
    @pytest.mark.asyncio
    async def test_delay_timing(self):
        """Test that delays are actually applied"""
        transform = smooth_stream(delay_ms=50, chunking="word")
        
        input_stream = self.create_mock_stream(["word1 word2 word3 "])
        
        start_time = time.time()
        chunks = []
        
        async for chunk in transform(input_stream):
            if chunk.type == "text-delta":
                chunks.append(chunk.text_delta)
        
        elapsed = time.time() - start_time
        
        # Should have 3 words, so 2 delays between them (50ms each)
        # Allow some tolerance for timing variations
        assert elapsed >= 0.08  # At least 80ms (2 * 50ms - tolerance)
        assert len(chunks) == 3
    
    @pytest.mark.asyncio 
    async def test_no_delay(self):
        """Test that None delay works immediately"""
        transform = smooth_stream(delay_ms=None, chunking="word")
        
        input_stream = self.create_mock_stream(["word1 word2 word3 "])
        
        start_time = time.time()
        chunks = []
        
        async for chunk in transform(input_stream):
            if chunk.type == "text-delta":
                chunks.append(chunk.text_delta)
        
        elapsed = time.time() - start_time
        
        # Should be very fast without delays
        assert elapsed < 0.05  # Less than 50ms
        assert len(chunks) == 3
    
    @pytest.mark.asyncio
    async def test_id_consistency(self):
        """Test that IDs are preserved through chunking"""
        transform = smooth_stream(delay_ms=None, chunking="word")
        
        # Create stream with different IDs
        async def mixed_id_stream():
            yield StreamPart(type="text-delta", text_delta="Hello ", id="id1")
            yield StreamPart(type="text-delta", text_delta="world ", id="id1") 
            yield StreamPart(type="text-delta", text_delta="from ", id="id2")
            yield StreamPart(type="text-delta", text_delta="Python!", id="id2")
        
        output_parts = []
        async for chunk in transform(mixed_id_stream()):
            if chunk.type == "text-delta":
                output_parts.append((chunk.text_delta, chunk.id))
        
        expected = [("Hello ", "id1"), ("world ", "id1"), ("from ", "id2"), ("Python!", "id2")]
        assert output_parts == expected
    
    @pytest.mark.asyncio
    async def test_buffer_flushing_on_id_change(self):
        """Test that buffer is flushed when ID changes"""
        transform = smooth_stream(delay_ms=None, chunking="word")
        
        # Create stream where partial word spans ID change
        async def id_change_stream():
            yield StreamPart(type="text-delta", text_delta="Hel", id="id1")
            yield StreamPart(type="text-delta", text_delta="lo", id="id2")  # ID change mid-word
        
        output_parts = []
        async for chunk in transform(id_change_stream()):
            if chunk.type == "text-delta":
                output_parts.append((chunk.text_delta, chunk.id))
        
        # Should flush "Hel" when ID changes, then output "lo"
        expected = [("Hel", "id1"), ("lo", "id2")]
        assert output_parts == expected
    
    @pytest.mark.asyncio
    async def test_custom_regex_chunking(self):
        """Test custom regex pattern chunking"""
        import re
        # Custom pattern that splits on punctuation
        custom_pattern = re.compile(r'[^.!?]*[.!?]+')
        
        transform = smooth_stream(delay_ms=None, chunking=custom_pattern)
        
        input_stream = self.create_mock_stream(["Hello! How are you? I'm fine."])
        output_chunks = []
        
        async for chunk in transform(input_stream):
            if chunk.type == "text-delta":
                output_chunks.append(chunk.text_delta)
        
        expected = ["Hello!", " How are you?", " I'm fine."]
        assert output_chunks == expected
    
    @pytest.mark.asyncio
    async def test_invalid_chunking_strategy(self):
        """Test error handling for invalid chunking strategy"""
        with pytest.raises(ValueError, match="Unknown chunking strategy"):
            smooth_stream(chunking="invalid")
    
    @pytest.mark.asyncio
    async def test_empty_stream(self):
        """Test handling of empty stream"""
        transform = smooth_stream(delay_ms=None, chunking="word")
        
        async def empty_stream():
            return
            yield  # unreachable
        
        output_chunks = []
        async for chunk in transform(empty_stream()):
            output_chunks.append(chunk)
        
        assert output_chunks == []
    
    @pytest.mark.asyncio
    async def test_final_buffer_flush(self):
        """Test that final buffer content is flushed"""
        transform = smooth_stream(delay_ms=None, chunking="word")
        
        # Stream ending with incomplete word (no trailing space)
        input_stream = self.create_mock_stream(["Hello world final"])
        output_chunks = []
        
        async for chunk in transform(input_stream):
            if chunk.type == "text-delta":
                output_chunks.append(chunk.text_delta)
        
        # Should get complete words plus final incomplete word
        expected = ["Hello ", "world ", "final"]
        assert output_chunks == expected


class TestChunkDetectors:
    """Test suite for chunk detector functions"""
    
    def test_word_chunker(self):
        """Test word chunker function"""
        result = word_chunker("Hello world test")
        assert result == "Hello "
        
        result = word_chunker("NoSpace")
        assert result is None
        
        result = word_chunker("")
        assert result is None
    
    def test_sentence_chunker(self):
        """Test sentence chunker function"""
        result = sentence_chunker("Hello world! How are you?")
        assert result == "Hello world! "
        
        result = sentence_chunker("No sentence ending")
        assert result is None
        
        result = sentence_chunker("Question? ")
        assert result == "Question? "
    
    def test_character_chunker_factory(self):
        """Test character chunker factory function"""
        chunker = character_chunker(3)
        
        result = chunker("Hello")
        assert result == "Hel"
        
        result = chunker("Hi")
        assert result is None  # Not enough characters
        
        # Test single character
        single_chunker = character_chunker(1)
        result = single_chunker("A")
        assert result == "A"


if __name__ == "__main__":
    pytest.main([__file__])