#!/usr/bin/env python3

"""
UI Message Stream Example for AI SDK Python

This example demonstrates how to use the UI message streaming functionality
for building modern chat interfaces with real-time streaming updates.

UI message streams provide:
- Real-time streaming of message parts (text, reasoning, tool calls, etc.)
- Framework-agnostic streaming interface
- Server-Sent Events (SSE) compatibility  
- Tool execution visibility and status updates
- Error handling with graceful fallbacks
"""

import asyncio
import json
from typing import AsyncIterator, Dict, Any, List

from ai_sdk import (
    create_openai,
    generate_text,
    tool,
    UIMessage, 
    TextUIPart,
    ReasoningUIPart,
    ToolUIPart,
    create_ui_message_stream,
    UIMessageChunk,
    UIMessageStreamWriter,
    JsonToSseTransformStream,
)


# Example tool for demonstration
@tool("calculator", "Perform mathematical calculations")
def calculator(expression: str) -> float:
    """Simple calculator tool."""
    try:
        # In production, use a safe expression evaluator
        return eval(expression)
    except Exception as e:
        raise ValueError(f"Invalid expression: {expression}")


async def simple_ui_message_stream_example():
    """Simple example of UI message streaming."""
    print("=== Simple UI Message Stream Example ===")
    
    def execute_stream(writer: UIMessageStreamWriter) -> None:
        """Execute function that writes chunks to the stream."""
        # Write a text part
        text_chunk = TextUIPart(
            type="text",
            text="Hello, I'm processing your request...",
            state="streaming"
        )
        writer.write(text_chunk)
        
        # Write reasoning part
        reasoning_chunk = ReasoningUIPart(
            type="reasoning", 
            text="Let me think about this step by step.",
            state="done"
        )
        writer.write(reasoning_chunk)
        
        # Write final text
        final_text = TextUIPart(
            type="text",
            text=" Here's my response!",
            state="done"
        )
        writer.write(final_text)
    
    # Create and consume stream
    stream = create_ui_message_stream(execute=execute_stream)
    
    print("Streaming chunks:")
    async for chunk in stream:
        chunk_data = {
            "type": chunk.type,
            "content": getattr(chunk, 'text', getattr(chunk, 'error_text', 'N/A'))
        }
        print(f"  Chunk: {json.dumps(chunk_data, indent=2)}")


async def tool_execution_stream_example():
    """Example showing tool execution in UI message stream."""
    print("\n=== Tool Execution Stream Example ===")
    
    # Initialize OpenAI provider
    openai = create_openai(api_key="your-openai-key")  # Replace with actual key
    model = openai.chat("gpt-3.5-turbo")
    
    async def execute_with_tools(writer: UIMessageStreamWriter) -> None:
        """Execute generation with tool calling visualization."""
        try:
            # Show initial processing
            writer.write(TextUIPart(
                type="text",
                text="I'll help you with that calculation.",
                state="streaming"
            ))
            
            # Show tool call
            writer.write(ToolUIPart(
                type="tool-calculator",
                tool_call_id="call_001", 
                state="input-streaming",
                input={"expression": "15 * 24 + 7"}
            ))
            
            # Execute the actual tool
            result = calculator("15 * 24 + 7")
            
            # Show tool result
            writer.write(ToolUIPart(
                type="tool-calculator",
                tool_call_id="call_001",
                state="output-available", 
                input={"expression": "15 * 24 + 7"},
                output=result
            ))
            
            # Show final response
            writer.write(TextUIPart(
                type="text",
                text=f"The calculation result is {result}.",
                state="done"
            ))
            
        except Exception as e:
            # Show error in stream
            writer.write(TextUIPart(
                type="text", 
                text=f"Error occurred: {str(e)}",
                state="done"
            ))
    
    # Create and consume stream
    stream = create_ui_message_stream(execute=execute_with_tools)
    
    print("Tool execution stream:")
    async for chunk in stream:
        if hasattr(chunk, 'type'):
            print(f"  Chunk type: {chunk.type}")
            if hasattr(chunk, 'text'):
                print(f"    Text: {chunk.text}")
            elif hasattr(chunk, 'input') and chunk.input:
                print(f"    Tool input: {chunk.input}")
            elif hasattr(chunk, 'output') and chunk.output:
                print(f"    Tool output: {chunk.output}")


async def async_tool_stream_example():
    """Example with async tool execution."""
    print("\n=== Async Tool Stream Example ===")
    
    @tool("async_timer", "Wait for specified seconds")
    async def async_timer(seconds: float) -> str:
        """Async tool that waits."""
        await asyncio.sleep(seconds)
        return f"Waited for {seconds} seconds"
    
    async def execute_async_tools(writer: UIMessageStreamWriter) -> None:
        """Execute with async tools."""
        writer.write(TextUIPart(
            type="text",
            text="Starting async operation...",
            state="streaming"
        ))
        
        # Show tool execution
        writer.write(ToolUIPart(
            type="tool-async_timer",
            tool_call_id="call_002",
            state="input-available",
            input={"seconds": 1.0}
        ))
        
        # Execute async tool
        result = await async_timer(1.0)
        
        writer.write(ToolUIPart(
            type="tool-async_timer", 
            tool_call_id="call_002",
            state="output-available",
            input={"seconds": 1.0},
            output=result
        ))
        
        writer.write(TextUIPart(
            type="text",
            text="Async operation completed!",
            state="done"
        ))
    
    # Create and consume stream
    stream = create_ui_message_stream(execute=execute_async_tools)
    
    print("Async tool stream:")
    async for chunk in stream:
        if hasattr(chunk, 'type'):
            print(f"  Chunk: {chunk.type}")


async def sse_transformation_example():
    """Example of transforming UI message stream to SSE format."""
    print("\n=== SSE Transformation Example ===")
    
    def execute_for_sse(writer: UIMessageStreamWriter) -> None:
        """Generate chunks for SSE transformation."""
        writer.write(TextUIPart(
            type="text",
            text="This is a streaming message",
            state="streaming"
        ))
        
        writer.write(TextUIPart(
            type="text", 
            text=" that will be converted to SSE format.",
            state="done"
        ))
    
    # Create stream and transform to SSE
    stream = create_ui_message_stream(execute=execute_for_sse)
    transformer = JsonToSseTransformStream()
    
    print("SSE formatted output:")
    async for sse_data in transformer.transform(stream):
        print(f"  {sse_data.strip()}")


async def error_handling_example():
    """Example showing error handling in UI message streams."""
    print("\n=== Error Handling Example ===")
    
    def execute_with_error(writer: UIMessageStreamWriter) -> None:
        """Execute function that intentionally raises an error."""
        writer.write(TextUIPart(
            type="text",
            text="Processing request...",
            state="streaming"
        ))
        
        # This will trigger the error handler
        raise ValueError("Simulated error for demonstration")
    
    def custom_error_handler(error: Exception) -> str:
        """Custom error handler."""
        return f"Custom error: {str(error)}"
    
    # Create stream with error handler
    stream = create_ui_message_stream(
        execute=execute_with_error,
        on_error=custom_error_handler
    )
    
    print("Stream with error:")
    async for chunk in stream:
        if hasattr(chunk, 'type'):
            print(f"  Chunk type: {chunk.type}")
            if hasattr(chunk, 'error_text'):
                print(f"    Error: {chunk.error_text}")


async def main():
    """Run all UI message stream examples."""
    print("UI Message Stream Examples for AI SDK Python")
    print("=" * 50)
    
    # Run examples
    await simple_ui_message_stream_example()
    await tool_execution_stream_example()
    await async_tool_stream_example() 
    await sse_transformation_example()
    await error_handling_example()
    
    print("\n" + "=" * 50)
    print("All examples completed!")


if __name__ == "__main__":
    # Note: You'll need to set OPENAI_API_KEY environment variable or 
    # replace the API key in the examples above
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nExamples interrupted by user")
    except Exception as e:
        print(f"Error running examples: {e}")