#!/usr/bin/env python3
"""
LlamaIndex Adapter Example

This example demonstrates how to integrate AI SDK with LlamaIndex components
using the LlamaIndex adapter for seamless stream conversion.

Requirements:
- pip install llama-index llama-index-llms-openai
- Set OPENAI_API_KEY environment variable
"""

import asyncio
import os
from ai_sdk.adapters.llamaindex import (
    to_ui_message_stream,
    LlamaIndexAdapter,
    EngineResponse,
    trim_start_of_stream
)
from ai_sdk.adapters.langchain import create_stream_callbacks


async def main():
    print("=== LlamaIndex Adapter Examples ===\n")
    
    # Example 1: Basic LlamaIndex Engine Response Stream
    print("1. Basic LlamaIndex Engine Response Stream")
    
    async def mock_engine_stream():
        """Mock LlamaIndex engine response stream"""
        response_text = "   LlamaIndex provides powerful RAG capabilities for building context-aware AI applications."
        
        # Simulate streaming engine responses
        words = response_text.split()
        for word in words:
            yield EngineResponse(word + " ")
            await asyncio.sleep(0.1)
    
    # Convert to AI SDK format
    engine_stream = mock_engine_stream()
    ui_stream = to_ui_message_stream(engine_stream)
    
    print("Engine response stream (note automatic whitespace trimming):")
    async for chunk in ui_stream:
        if chunk.type == "text-delta":
            print(chunk.content, end="", flush=True)
    print("\n")
    
    # Example 2: LlamaIndex ChatEngine Stream
    print("2. LlamaIndex ChatEngine Stream Conversion")
    
    class MockChatResponse:
        """Mock LlamaIndex chat response"""
        def __init__(self, delta: str):
            self.delta = delta
            self.response = delta  # Alternative attribute
    
    async def mock_chat_engine_stream():
        """Mock LlamaIndex chat engine stream"""
        responses = [
            "LlamaIndex chat engines ",
            "enable conversational ",
            "interactions with ",
            "your data sources."
        ]
        
        for response_text in responses:
            yield MockChatResponse(response_text)
            await asyncio.sleep(0.15)
    
    chat_stream = mock_chat_engine_stream()
    ui_stream = LlamaIndexAdapter.from_chat_engine(chat_stream)
    
    print("ChatEngine stream:")
    async for chunk in ui_stream:
        if chunk.type == "text-delta":
            print(chunk.content, end="", flush=True)
    print("\n")
    
    # Example 3: LlamaIndex QueryEngine Stream
    print("3. LlamaIndex QueryEngine Stream Conversion")
    
    class MockQueryResponse:
        """Mock LlamaIndex query response"""
        def __init__(self, text: str):
            self.text = text
            self.content = text  # Alternative attribute
    
    async def mock_query_engine_stream():
        """Mock LlamaIndex query engine stream"""
        query_parts = [
            "QueryEngines in LlamaIndex ",
            "provide structured access ",
            "to indexed documents ",
            "and knowledge bases."
        ]
        
        for part in query_parts:
            yield MockQueryResponse(part)
            await asyncio.sleep(0.12)
    
    query_stream = mock_query_engine_stream()
    
    # Use callbacks to track progress
    query_text = []
    callbacks = create_stream_callbacks(
        on_start=lambda: print("Query processing started..."),
        on_text=lambda text: query_text.append(text),
        on_end=lambda: print(f"\nQuery completed. Total length: {len(''.join(query_text))} characters")
    )
    
    ui_stream = LlamaIndexAdapter.from_query_engine(query_stream, callbacks)
    
    async for chunk in ui_stream:
        if chunk.type == "text-delta":
            print(chunk.content, end="", flush=True)
    print()
    
    # Example 4: Whitespace Trimming Functionality
    print("4. Whitespace Trimming at Stream Start")
    
    async def whitespace_heavy_stream():
        """Stream with significant leading whitespace"""
        responses = [
            "   \n\t  ",  # Only whitespace - should be trimmed
            "  LlamaIndex",  # Leading whitespace - should be trimmed
            " handles",  # Normal content
            " various",
            " data formats."
        ]
        
        for response in responses:
            yield EngineResponse(response)
            await asyncio.sleep(0.1)
    
    trimmer = trim_start_of_stream()
    
    print("Raw stream with whitespace trimming:")
    stream = whitespace_heavy_stream()
    async for response in stream:
        trimmed = trimmer(response.delta)
        if trimmed:
            print(f"'{trimmed}'", end="")
    print("\n")
    
    # Example 5: Error Handling with Different Response Formats
    print("5. Handling Various LlamaIndex Response Formats")
    
    async def mixed_format_stream():
        """Stream with various LlamaIndex response formats"""
        responses = [
            {"response": "Dictionary with response key"},
            {"text": "Dictionary with text key"},
            {"delta": "Dictionary with delta key"},
            {"content": "Dictionary with content key"},
            {"message": "Dictionary with message key"},
            "Plain string response",
            EngineResponse("EngineResponse object"),
        ]
        
        for resp in responses:
            yield resp
            await asyncio.sleep(0.1)
    
    mixed_stream = mixed_format_stream()
    ui_stream = LlamaIndexAdapter.to_ui_message_stream(mixed_stream)
    
    print("Mixed format responses:")
    async for chunk in ui_stream:
        if chunk.type == "text-delta":
            print(f"• {chunk.content}")
    print()
    
    # Example 6: Real LlamaIndex Integration (requires llama-index)
    print("6. Real LlamaIndex Integration Example")
    
    try:
        # This would work with real LlamaIndex installation
        # from llama_index.llms.openai import OpenAI
        # from llama_index.core.chat_engine import SimpleChatEngine
        # from llama_index.core.memory import ChatMemoryBuffer
        
        # llm = OpenAI(model="gpt-3.5-turbo", streaming=True)
        # memory = ChatMemoryBuffer.from_defaults(token_limit=2000)
        # chat_engine = SimpleChatEngine.from_defaults(llm=llm, memory=memory)
        # 
        # response_stream = chat_engine.astream_chat("What are the key features of LlamaIndex?")
        # ui_stream = LlamaIndexAdapter.from_chat_engine(response_stream)
        # 
        # print("Real LlamaIndex ChatEngine response:")
        # async for chunk in ui_stream:
        #     if chunk.type == "text-delta":
        #         print(chunk.content, end="", flush=True)
        # print()
        
        print("Skipped - requires llama-index and OpenAI API key")
        
    except ImportError:
        print("LlamaIndex not installed - install with: pip install llama-index llama-index-llms-openai")
    except Exception as e:
        print(f"Error with real LlamaIndex: {e}")
    
    # Example 7: Performance Considerations
    print("\n7. Performance and Memory Considerations")
    
    async def large_response_stream():
        """Simulate processing a large response"""
        # Simulate processing a large document
        chunk_size = 50
        large_text = "LlamaIndex excels at handling large documents and provides efficient indexing mechanisms. " * 20
        
        for i in range(0, len(large_text), chunk_size):
            chunk = large_text[i:i + chunk_size]
            yield EngineResponse(chunk)
            await asyncio.sleep(0.01)  # Fast streaming
    
    print("Processing large response stream:")
    start_time = asyncio.get_event_loop().time()
    chunk_count = 0
    
    large_stream = large_response_stream()
    ui_stream = LlamaIndexAdapter.to_ui_message_stream(large_stream)
    
    async for chunk in ui_stream:
        if chunk.type == "text-delta":
            chunk_count += 1
            if chunk_count % 20 == 0:
                print(".", end="", flush=True)
    
    end_time = asyncio.get_event_loop().time()
    print(f"\nProcessed {chunk_count} chunks in {end_time - start_time:.2f} seconds")
    
    print("\n=== LlamaIndex Adapter Examples Complete ===")
    print("\nKey Benefits:")
    print("✅ Native LlamaIndex integration")
    print("✅ Automatic whitespace trimming")
    print("✅ Multiple response format support")
    print("✅ Efficient streaming processing")
    print("✅ RAG-optimized stream handling")


if __name__ == "__main__":
    print("LlamaIndex Adapter provides:")
    print("🦙 LlamaIndex engine stream conversion")
    print("💬 ChatEngine and QueryEngine support")
    print("✂️ Automatic whitespace trimming")
    print("🔄 Multiple response format handling")
    print("⚡ High-performance streaming")
    print("")
    
    asyncio.run(main())