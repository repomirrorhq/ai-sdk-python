"""
Tests for LlamaIndex Adapter

This test suite covers:
- LlamaIndex engine response conversion
- Whitespace trimming functionality
- Multiple response format handling
- ChatEngine and QueryEngine support
- Error handling and callbacks
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from typing import List, Dict, Any

from ai_sdk.adapters.llamaindex import (
    LlamaIndexAdapter,
    to_ui_message_stream,
    trim_start_of_stream,
    EngineResponse
)
from ai_sdk.adapters.langchain import create_stream_callbacks, StreamCallbacks


class TestLlamaIndexAdapter:
    """Test suite for LlamaIndex Adapter"""
    
    async def test_engine_response_stream(self):
        """Test basic EngineResponse stream conversion"""
        async def engine_stream():
            responses = [
                EngineResponse("LlamaIndex "),
                EngineResponse("provides "),
                EngineResponse("RAG capabilities.")
            ]
            for response in responses:
                yield response
        
        chunks = []
        ui_stream = LlamaIndexAdapter.to_ui_message_stream(engine_stream())
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        # Should have start, deltas, and end
        assert len(chunks) == 5  # start + 3 deltas + end
        assert chunks[0].type == "text-start"
        assert chunks[-1].type == "text-end"
        
        # Check delta content
        delta_content = [c.content for c in chunks if c.type == "text-delta"]
        assert delta_content == ["LlamaIndex ", "provides ", "RAG capabilities."]
    
    async def test_whitespace_trimming(self):
        """Test automatic whitespace trimming at stream start"""
        async def whitespace_stream():
            responses = [
                EngineResponse("   \n\t  "),  # Only whitespace - should be trimmed
                EngineResponse("  Hello "),   # Leading whitespace - should be trimmed  
                EngineResponse("world "),     # Normal content
                EngineResponse(" from LlamaIndex")
            ]
            for response in responses:
                yield response
        
        chunks = []
        ui_stream = LlamaIndexAdapter.to_ui_message_stream(whitespace_stream())
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        # Should trim initial whitespace but preserve later spaces
        delta_content = [c.content for c in chunks if c.type == "text-delta"]
        assert delta_content == ["Hello ", "world ", " from LlamaIndex"]
    
    async def test_string_response_handling(self):
        """Test handling of plain string responses"""
        async def string_stream():
            yield "Plain string response"
            yield "Another string"
        
        chunks = []
        ui_stream = LlamaIndexAdapter.to_ui_message_stream(string_stream())
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        delta_content = [c.content for c in chunks if c.type == "text-delta"]
        assert delta_content == ["Plain string response", "Another string"]
    
    async def test_dictionary_response_formats(self):
        """Test various dictionary response formats from LlamaIndex"""
        async def dict_stream():
            formats = [
                {"delta": "Delta format"},
                {"response": "Response format"},
                {"text": "Text format"},
                {"content": "Content format"},
                {"message": "Message format"},
                {"unknown_key": "Should fallback to string"}
            ]
            for fmt in formats:
                yield fmt
        
        chunks = []
        ui_stream = LlamaIndexAdapter.to_ui_message_stream(dict_stream())
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        delta_content = [c.content for c in chunks if c.type == "text-delta"]
        expected = [
            "Delta format",
            "Response format", 
            "Text format",
            "Content format",
            "Message format",
            "{'unknown_key': 'Should fallback to string'}"  # String repr fallback
        ]
        assert delta_content == expected
    
    async def test_object_response_attributes(self):
        """Test extraction from objects with various attributes"""
        class MockResponse:
            def __init__(self, **kwargs):
                for k, v in kwargs.items():
                    setattr(self, k, v)
        
        async def object_stream():
            responses = [
                MockResponse(response="Response attribute"),
                MockResponse(text="Text attribute"),
                MockResponse(content="Content attribute"),
                MockResponse(message="Message attribute"),
                MockResponse(delta="Delta attribute"),
                MockResponse(other="Other attribute")  # Should fallback
            ]
            for resp in responses:
                yield resp
        
        chunks = []
        ui_stream = LlamaIndexAdapter.to_ui_message_stream(object_stream())
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        delta_content = [c.content for c in chunks if c.type == "text-delta"]
        expected = [
            "Response attribute",
            "Text attribute",
            "Content attribute", 
            "Message attribute",
            "Delta attribute"
        ]
        # Last one should be string representation of object
        assert delta_content[:5] == expected
        assert "other" in delta_content[5].lower()
    
    async def test_chat_engine_conversion(self):
        """Test ChatEngine-specific conversion method"""
        async def chat_stream():
            yield EngineResponse("ChatEngine response")
        
        chunks = []
        ui_stream = LlamaIndexAdapter.from_chat_engine(chat_stream())
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        delta_content = [c.content for c in chunks if c.type == "text-delta"]
        assert delta_content == ["ChatEngine response"]
    
    async def test_query_engine_conversion(self):
        """Test QueryEngine-specific conversion method"""
        async def query_stream():
            yield EngineResponse("QueryEngine response")
        
        chunks = []
        ui_stream = LlamaIndexAdapter.from_query_engine(query_stream())
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        delta_content = [c.content for c in chunks if c.type == "text-delta"]
        assert delta_content == ["QueryEngine response"]
    
    async def test_llm_predictor_conversion(self):
        """Test LLMPredictor-specific conversion method"""
        async def llm_stream():
            yield EngineResponse("LLMPredictor response")
        
        chunks = []
        ui_stream = LlamaIndexAdapter.from_llm_predictor(llm_stream())
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        delta_content = [c.content for c in chunks if c.type == "text-delta"]
        assert delta_content == ["LLMPredictor response"]
    
    async def test_stream_callbacks(self):
        """Test callback functionality with LlamaIndex streams"""
        callback_events = []
        
        callbacks = create_stream_callbacks(
            on_start=lambda: callback_events.append("start"),
            on_text=lambda text: callback_events.append(f"text:{text}"),
            on_end=lambda: callback_events.append("end"),
            on_error=lambda error: callback_events.append(f"error:{error}")
        )
        
        async def test_stream():
            yield EngineResponse("Hello")
            yield EngineResponse("LlamaIndex")
        
        chunks = []
        ui_stream = LlamaIndexAdapter.to_ui_message_stream(test_stream(), callbacks)
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        # Check callback events
        assert "start" in callback_events
        assert "text:Hello" in callback_events
        assert "text:LlamaIndex" in callback_events
        assert "end" in callback_events
    
    async def test_error_handling(self):
        """Test error handling in stream processing"""
        async def error_stream():
            yield EngineResponse("Good response")
            raise Exception("LlamaIndex error")
        
        error_callback_called = []
        callbacks = create_stream_callbacks(
            on_error=lambda error: error_callback_called.append(str(error))
        )
        
        chunks = []
        ui_stream = LlamaIndexAdapter.to_ui_message_stream(error_stream(), callbacks)
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        # Should handle error gracefully
        assert len(error_callback_called) == 1
        assert "LlamaIndex error" in error_callback_called[0]
        
        # Should have error chunk
        error_chunks = [c for c in chunks if c.type == "error"]
        assert len(error_chunks) == 1
    
    async def test_chunk_error_recovery(self):
        """Test recovery from individual chunk errors"""
        class ProblematicResponse:
            def __init__(self):
                pass
            
            def __getattr__(self, name):
                if name == "delta":
                    raise AttributeError("Simulated error")
                return super().__getattribute__(name)
        
        async def problematic_stream():
            yield EngineResponse("Good response 1")
            yield ProblematicResponse()  # Should cause error but not stop stream
            yield EngineResponse("Good response 2")
        
        chunks = []
        ui_stream = LlamaIndexAdapter.to_ui_message_stream(problematic_stream())
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        # Should recover and process good responses
        delta_content = [c.content for c in chunks if c.type == "text-delta"]
        assert "Good response 1" in delta_content
        assert "Good response 2" in delta_content
    
    async def test_convenience_function(self):
        """Test module-level convenience function"""
        async def simple_stream():
            yield EngineResponse("Test response")
        
        chunks = []
        ui_stream = to_ui_message_stream(simple_stream())
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        delta_content = [c.content for c in chunks if c.type == "text-delta"]
        assert delta_content == ["Test response"]
    
    def test_trim_start_of_stream_function(self):
        """Test whitespace trimming utility function"""
        trimmer = trim_start_of_stream()
        
        # First calls should trim whitespace
        assert trimmer("   \n\t  ") == ""
        assert trimmer("  Hello") == "Hello"
        
        # After non-whitespace, should preserve spaces
        assert trimmer("  World") == "  World"
        assert trimmer(" !") == " !"
    
    def test_text_extraction_from_response(self):
        """Test text extraction from various response types"""
        # Test with object attributes
        class MockObj:
            response = "response text"
        
        text = LlamaIndexAdapter._extract_text_from_response(MockObj())
        assert text == "response text"
        
        # Test with dictionary
        dict_resp = {"text": "dictionary text"}
        text = LlamaIndexAdapter._extract_text_from_response(dict_resp)
        assert text == "dictionary text"
        
        # Test fallback to string
        text = LlamaIndexAdapter._extract_text_from_response("plain string")
        assert text == "plain string"
        
        # Test empty response
        text = LlamaIndexAdapter._extract_text_from_response(None)
        assert text == ""
    
    async def test_empty_stream(self):
        """Test handling of empty streams"""
        async def empty_stream():
            return
            yield  # Never reached
        
        chunks = []
        ui_stream = LlamaIndexAdapter.to_ui_message_stream(empty_stream())
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        # Should still have start and end
        assert len(chunks) == 2
        assert chunks[0].type == "text-start"
        assert chunks[1].type == "text-end"
    
    async def test_large_response_handling(self):
        """Test handling of large responses efficiently"""
        async def large_stream():
            # Generate many small chunks
            for i in range(100):
                yield EngineResponse(f"Chunk {i} ")
        
        chunks = []
        ui_stream = LlamaIndexAdapter.to_ui_message_stream(large_stream())
        
        chunk_count = 0
        async for chunk in ui_stream:
            chunks.append(chunk)
            if chunk.type == "text-delta":
                chunk_count += 1
        
        # Should process all chunks
        assert chunk_count == 100
        assert len(chunks) == 102  # start + 100 deltas + end
    
    async def test_mixed_response_types(self):
        """Test handling of mixed response types in single stream"""
        async def mixed_stream():
            yield "String response"
            yield EngineResponse("EngineResponse")
            yield {"delta": "Dict response"}
            
            class ObjResponse:
                text = "Object response"
            
            yield ObjResponse()
        
        chunks = []
        ui_stream = LlamaIndexAdapter.to_ui_message_stream(mixed_stream())
        
        async for chunk in ui_stream:
            chunks.append(chunk)
        
        delta_content = [c.content for c in chunks if c.type == "text-delta"]
        expected = [
            "String response",
            "EngineResponse", 
            "Dict response",
            "Object response"
        ]
        assert delta_content == expected


if __name__ == "__main__":
    pytest.main([__file__])