"""
Tests for LangChain Adapter

This test suite covers:
- LangChain message stream conversion
- String output parser support  
- Stream Events v2 compatibility
- Error handling and callbacks
- Various content formats
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from typing import List, Dict, Any

from ai_sdk.adapters.langchain import (
    LangChainAdapter,
    to_ui_message_stream,
    create_stream_callbacks,
    StreamCallbacks,
    UIMessageChunk,
    LangChainAIMessageChunk,
    LangChainStreamEvent,
    LangChainMessageContentText,
    LangChainMessageContentImageUrl
)


class TestLangChainAdapter:
    """Test suite for LangChain Adapter"""
    
    async def test_string_stream_conversion(self):
        """Test conversion of simple string streams"""
        async def string_stream():
            strings = ["Hello ", "world ", "from ", "LangChain!"]
            for s in strings:
                yield s
        
        chunks = []
        ui_stream = LangChainAdapter.to_ui_message_stream(string_stream())
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        # Should have start, deltas, and end
        assert len(chunks) == 6  # start + 4 deltas + end
        assert chunks[0].type == "text-start"
        assert chunks[-1].type == "text-end"
        
        # Check delta content
        delta_content = [c.content for c in chunks if c.type == "text-delta"]
        assert delta_content == ["Hello ", "world ", "from ", "LangChain!"]
    
    async def test_langchain_message_chunk_stream(self):
        """Test conversion of LangChain AI message chunks"""
        async def message_stream():
            messages = [
                LangChainAIMessageChunk("LangChain "),
                LangChainAIMessageChunk("provides "),
                LangChainAIMessageChunk("great integration!")
            ]
            for msg in messages:
                yield msg
        
        chunks = []
        ui_stream = LangChainAdapter.to_ui_message_stream(message_stream())
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        delta_content = [c.content for c in chunks if c.type == "text-delta"]
        assert delta_content == ["LangChain ", "provides ", "great integration!"]
    
    async def test_langchain_stream_events_v2(self):
        """Test LangChain Stream Events v2 format"""
        async def event_stream():
            events = [
                LangChainStreamEvent("on_chat_model_stream", {
                    "chunk": LangChainAIMessageChunk("Stream ")
                }),
                LangChainStreamEvent("on_chat_model_stream", {
                    "chunk": LangChainAIMessageChunk("events ")
                }),
                LangChainStreamEvent("other_event", {"data": "ignored"}),
                LangChainStreamEvent("on_chat_model_stream", {
                    "chunk": LangChainAIMessageChunk("work!")
                }),
            ]
            for event in events:
                yield event
        
        chunks = []
        ui_stream = LangChainAdapter.to_ui_message_stream(event_stream())
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        delta_content = [c.content for c in chunks if c.type == "text-delta"]
        assert delta_content == ["Stream ", "events ", "work!"]
    
    async def test_complex_message_content(self):
        """Test complex message content with text and image parts"""
        async def complex_stream():
            # Complex content with text and image parts
            complex_content = [
                LangChainMessageContentText("This is text content"),
                LangChainMessageContentImageUrl("https://example.com/image.jpg"),
                LangChainMessageContentText(" and more text")
            ]
            yield LangChainAIMessageChunk(complex_content)
        
        chunks = []
        ui_stream = LangChainAdapter.to_ui_message_stream(complex_stream())
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        # Should extract only text parts
        delta_content = [c.content for c in chunks if c.type == "text-delta"]
        assert delta_content == ["This is text content and more text"]
    
    async def test_dictionary_format_streams(self):
        """Test various dictionary-based stream formats"""
        async def dict_stream():
            formats = [
                {"content": "Content key format"},
                {"text": "Text key format"},
                {"delta": "Delta key format"},
                {"response": "Response key format"},
                {"other_key": "Should be ignored"}
            ]
            for fmt in formats:
                yield fmt
        
        chunks = []
        ui_stream = LangChainAdapter.to_ui_message_stream(dict_stream())
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        delta_content = [c.content for c in chunks if c.type == "text-delta"]
        expected = ["Content key format", "Text key format", "Delta key format"]
        assert delta_content == expected
    
    async def test_stream_callbacks(self):
        """Test stream callback functionality"""
        callback_events = []
        
        callbacks = create_stream_callbacks(
            on_start=lambda: callback_events.append("start"),
            on_text=lambda text: callback_events.append(f"text:{text}"),
            on_end=lambda: callback_events.append("end"),
            on_error=lambda error: callback_events.append(f"error:{error}")
        )
        
        async def test_stream():
            yield "Hello"
            yield "World"
        
        chunks = []
        ui_stream = LangChainAdapter.to_ui_message_stream(test_stream(), callbacks)
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        # Check callback events
        assert "start" in callback_events
        assert "text:Hello" in callback_events
        assert "text:World" in callback_events
        assert "end" in callback_events
        
        # Check stream chunks
        delta_content = [c.content for c in chunks if c.type == "text-delta"]
        assert delta_content == ["Hello", "World"]
    
    async def test_error_handling(self):
        """Test error handling in stream processing"""
        async def error_stream():
            yield "Good chunk"
            raise Exception("Stream error")
        
        error_callback_called = []
        callbacks = create_stream_callbacks(
            on_error=lambda error: error_callback_called.append(str(error))
        )
        
        chunks = []
        ui_stream = LangChainAdapter.to_ui_message_stream(error_stream(), callbacks)
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        # Should handle error gracefully
        assert len(error_callback_called) == 1
        assert "Stream error" in error_callback_called[0]
        
        # Should have error chunk
        error_chunks = [c for c in chunks if c.type == "error"]
        assert len(error_chunks) == 1
    
    async def test_chunk_error_recovery(self):
        """Test recovery from individual chunk errors"""
        async def problematic_stream():
            yield "Good chunk 1"
            yield {"malformed": "chunk"}  # Problematic but not fatal
            yield "Good chunk 2"
        
        chunks = []
        ui_stream = LangChainAdapter.to_ui_message_stream(problematic_stream())
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        # Should recover and process good chunks
        delta_content = [c.content for c in chunks if c.type == "text-delta"]
        assert "Good chunk 1" in delta_content
        assert "Good chunk 2" in delta_content
    
    async def test_convenience_function(self):
        """Test module-level convenience function"""
        async def simple_stream():
            yield "Test message"
        
        chunks = []
        ui_stream = to_ui_message_stream(simple_stream())
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        delta_content = [c.content for c in chunks if c.type == "text-delta"]
        assert delta_content == ["Test message"]
    
    async def test_from_langchain_llm(self):
        """Test LLM-specific conversion method"""
        async def llm_stream():
            yield "LLM response text"
        
        chunks = []
        ui_stream = LangChainAdapter.from_langchain_llm(llm_stream())
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        delta_content = [c.content for c in chunks if c.type == "text-delta"]
        assert delta_content == ["LLM response text"]
    
    async def test_from_langchain_runnable(self):
        """Test Runnable-specific conversion method"""
        async def runnable_stream():
            yield "Runnable output"
        
        chunks = []
        ui_stream = LangChainAdapter.from_langchain_runnable(runnable_stream())
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        delta_content = [c.content for c in chunks if c.type == "text-delta"]
        assert delta_content == ["Runnable output"]
    
    def test_ui_message_chunk_structure(self):
        """Test UIMessageChunk structure and serialization"""
        chunk = UIMessageChunk("text-delta", "Hello world", "msg-1")
        
        assert chunk.type == "text-delta"
        assert chunk.content == "Hello world"
        assert chunk.id == "msg-1"
        
        chunk_dict = chunk.to_dict()
        expected = {
            "type": "text-delta",
            "content": "Hello world",
            "id": "msg-1"
        }
        assert chunk_dict == expected
    
    def test_stream_callbacks_creation(self):
        """Test StreamCallbacks creation and attributes"""
        start_fn = lambda: None
        text_fn = lambda x: None
        end_fn = lambda: None
        error_fn = lambda x: None
        
        callbacks = create_stream_callbacks(
            on_start=start_fn,
            on_text=text_fn,
            on_end=end_fn,
            on_error=error_fn
        )
        
        assert callbacks.on_start == start_fn
        assert callbacks.on_text == text_fn
        assert callbacks.on_end == end_fn
        assert callbacks.on_error == error_fn
    
    async def test_empty_stream(self):
        """Test handling of empty streams"""
        async def empty_stream():
            return
            yield  # Never reached
        
        chunks = []
        ui_stream = LangChainAdapter.to_ui_message_stream(empty_stream())
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        # Should still have start and end
        assert len(chunks) == 2
        assert chunks[0].type == "text-start"
        assert chunks[1].type == "text-end"
    
    async def test_mixed_content_extraction(self):
        """Test extraction from mixed content formats"""
        text_content = LangChainAdapter._extract_text_from_content([
            {"type": "text", "text": "First part"},
            {"type": "image_url", "image_url": "ignored"},
            {"type": "text", "text": "Second part"}
        ])
        
        assert text_content == "First partSecond part"
        
        # Test string content
        string_content = LangChainAdapter._extract_text_from_content("Simple string")
        assert string_content == "Simple string"
        
        # Test empty/invalid content
        empty_content = LangChainAdapter._extract_text_from_content([])
        assert empty_content == ""


if __name__ == "__main__":
    pytest.main([__file__])