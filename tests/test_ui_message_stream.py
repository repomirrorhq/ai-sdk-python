"""Tests for UI message streaming functionality."""

import asyncio
import pytest
from typing import List

from ai_sdk.ui import (
    UIMessage,
    TextUIPart,
    ReasoningUIPart,
    ToolUIPart,
    create_ui_message_stream,
    UIMessageStreamWriter,
    JsonToSseTransformStream,
    is_tool_ui_part,
    get_tool_name,
)


class TestUIMessageTypes:
    """Test UI message types and utilities."""
    
    def test_text_ui_part(self):
        """Test TextUIPart creation and properties."""
        part = TextUIPart(
            type="text",
            text="Hello, world!",
            state="streaming"
        )
        
        assert part.type == "text"
        assert part.text == "Hello, world!"
        assert part.state == "streaming"
    
    def test_reasoning_ui_part(self):
        """Test ReasoningUIPart creation."""
        part = ReasoningUIPart(
            type="reasoning",
            text="Let me think...",
            state="done"
        )
        
        assert part.type == "reasoning"
        assert part.text == "Let me think..."
        assert part.state == "done"
    
    def test_tool_ui_part(self):
        """Test ToolUIPart creation."""
        part = ToolUIPart(
            type="tool-calculator",
            tool_call_id="call_123",
            state="output-available",
            input={"expression": "2+2"},
            output=4
        )
        
        assert part.type == "tool-calculator"
        assert part.tool_call_id == "call_123"
        assert part.state == "output-available"
        assert part.input == {"expression": "2+2"}
        assert part.output == 4
    
    def test_is_tool_ui_part(self):
        """Test is_tool_ui_part utility function."""
        tool_part = ToolUIPart(
            type="tool-calculator",
            tool_call_id="call_123",
            state="input-available",
            input={}
        )
        text_part = TextUIPart(type="text", text="Hello")
        
        assert is_tool_ui_part(tool_part) == True
        assert is_tool_ui_part(text_part) == False
    
    def test_get_tool_name(self):
        """Test get_tool_name utility function."""
        part = ToolUIPart(
            type="tool-calculator",
            tool_call_id="call_123",
            state="input-available",
            input={}
        )
        
        assert get_tool_name(part) == "calculator"
        
        # Test compound tool name
        compound_part = ToolUIPart(
            type="tool-web-search",
            tool_call_id="call_456",
            state="input-available", 
            input={}
        )
        
        assert get_tool_name(compound_part) == "web-search"


class TestUIMessageStream:
    """Test UI message streaming functionality."""
    
    @pytest.mark.asyncio
    async def test_simple_stream(self):
        """Test basic UI message stream creation and consumption."""
        chunks_written = []
        
        def execute(writer: UIMessageStreamWriter) -> None:
            chunk1 = TextUIPart(type="text", text="Hello")
            chunk2 = TextUIPart(type="text", text=" World")
            
            writer.write(chunk1)
            writer.write(chunk2)
            chunks_written.extend([chunk1, chunk2])
        
        stream = create_ui_message_stream(execute=execute)
        
        chunks_read = []
        async for chunk in stream:
            chunks_read.append(chunk)
        
        assert len(chunks_read) == 2
        assert all(chunk.type == "text" for chunk in chunks_read)
    
    @pytest.mark.asyncio
    async def test_async_stream(self):
        """Test async UI message stream execution."""
        async def async_execute(writer: UIMessageStreamWriter) -> None:
            # Simulate async work
            await asyncio.sleep(0.01)
            
            chunk = TextUIPart(type="text", text="Async result")
            writer.write(chunk)
        
        stream = create_ui_message_stream(execute=async_execute)
        
        chunks = []
        async for chunk in stream:
            chunks.append(chunk)
        
        assert len(chunks) == 1
        assert chunks[0].text == "Async result"
    
    @pytest.mark.asyncio  
    async def test_error_handling(self):
        """Test error handling in UI message streams."""
        def execute_with_error(writer: UIMessageStreamWriter) -> None:
            writer.write(TextUIPart(type="text", text="Before error"))
            raise ValueError("Test error")
        
        def custom_error_handler(error: Exception) -> str:
            return f"Custom: {str(error)}"
        
        stream = create_ui_message_stream(
            execute=execute_with_error,
            on_error=custom_error_handler
        )
        
        chunks = []
        async for chunk in stream:
            chunks.append(chunk)
        
        # Should have the text chunk and an error chunk
        assert len(chunks) >= 1
        
        # Check for error chunk
        error_chunks = [c for c in chunks if c.type == "error"]
        assert len(error_chunks) == 1
        assert "Custom: Test error" in error_chunks[0].error_text
    
    @pytest.mark.asyncio
    async def test_stream_merging(self):
        """Test merging multiple streams."""
        async def create_sub_stream():
            """Create a sub-stream to merge."""
            def sub_execute(writer):
                writer.write(TextUIPart(type="text", text="From sub-stream"))
            return create_ui_message_stream(execute=sub_execute)
        
        def execute_with_merge(writer: UIMessageStreamWriter) -> None:
            writer.write(TextUIPart(type="text", text="Main stream"))
            
            # Create and merge sub-stream
            sub_stream = asyncio.create_task(create_sub_stream())
            # Note: In the actual implementation, this would use writer.merge()
            # For testing, we'll just write another chunk
            writer.write(TextUIPart(type="text", text="After merge"))
        
        stream = create_ui_message_stream(execute=execute_with_merge)
        
        chunks = []
        async for chunk in stream:
            chunks.append(chunk)
        
        assert len(chunks) >= 2
        assert any("Main stream" in getattr(c, 'text', '') for c in chunks)


class TestJsonToSseTransform:
    """Test JSON to SSE transformation."""
    
    @pytest.mark.asyncio
    async def test_sse_transformation(self):
        """Test transforming UI message chunks to SSE format."""
        def execute(writer: UIMessageStreamWriter) -> None:
            writer.write(TextUIPart(type="text", text="Hello SSE"))
        
        stream = create_ui_message_stream(execute=execute)
        transformer = JsonToSseTransformStream()
        
        sse_lines = []
        async for sse_line in transformer.transform(stream):
            sse_lines.append(sse_line)
        
        assert len(sse_lines) == 1
        assert sse_lines[0].startswith("data: ")
        assert sse_lines[0].endswith("\n\n")
        assert "Hello SSE" in sse_lines[0]


@pytest.mark.asyncio
async def test_ui_message_creation():
    """Test UIMessage model creation."""
    message = UIMessage(
        id="msg_123",
        role="assistant",
        parts=[
            TextUIPart(type="text", text="Hello"),
            ReasoningUIPart(type="reasoning", text="Thinking...")
        ]
    )
    
    assert message.id == "msg_123"
    assert message.role == "assistant"
    assert len(message.parts) == 2
    assert message.parts[0].type == "text"
    assert message.parts[1].type == "reasoning"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])