#!/usr/bin/env python3
"""
LangChain Adapter Example

This example demonstrates how to integrate AI SDK with LangChain components
using the LangChain adapter for seamless stream conversion.

Requirements:
- pip install langchain langchain-openai
- Set OPENAI_API_KEY environment variable
"""

import asyncio
import os
from ai_sdk.adapters.langchain import (
    to_ui_message_stream,
    create_stream_callbacks,
    LangChainAdapter
)

# Mock LangChain classes for demonstration
# In real usage, import these from langchain packages


class MockLangChainMessage:
    """Mock LangChain message for demonstration"""
    def __init__(self, content: str):
        self.content = content


class MockLangChainChatModel:
    """Mock LangChain chat model for demonstration"""
    
    async def astream(self, messages):
        """Mock streaming method"""
        response_text = "LangChain integration with AI SDK provides seamless interoperability between the two frameworks."
        
        # Simulate streaming chunks
        words = response_text.split()
        for i, word in enumerate(words):
            chunk_text = word + (" " if i < len(words) - 1 else "")
            yield MockLangChainMessage(chunk_text)
            await asyncio.sleep(0.1)  # Simulate network delay


class MockStringOutputParser:
    """Mock LangChain string output parser"""
    
    async def atransform(self, stream):
        """Transform message stream to string stream"""
        async for message in stream:
            yield message.content


async def main():
    print("=== LangChain Adapter Examples ===\n")
    
    # Example 1: Basic LangChain to AI SDK stream conversion
    print("1. Basic LangChain Message Stream Conversion")
    
    # Create mock LangChain model and stream
    model = MockLangChainChatModel()
    messages = [{"role": "user", "content": "Explain LangChain integration benefits"}]
    
    # Convert LangChain stream to AI SDK format
    langchain_stream = model.astream(messages)
    
    # Create callbacks for monitoring
    full_text = []
    
    callbacks = create_stream_callbacks(
        on_start=lambda: print("Stream started..."),
        on_text=lambda text: full_text.append(text),
        on_end=lambda: print("\nStream completed."),
        on_error=lambda error: print(f"Error: {error}")
    )
    
    # Convert and display stream
    ui_stream = to_ui_message_stream(langchain_stream, callbacks)
    
    async for chunk in ui_stream:
        if chunk.type == "text-delta":
            print(chunk.content, end="", flush=True)
    
    print(f"\nFull text: {''.join(full_text)}\n")
    
    # Example 2: LangChain String Parser Stream
    print("2. LangChain String Output Parser Stream")
    
    model = MockLangChainChatModel()
    parser = MockStringOutputParser()
    
    # Create a chain: model -> parser
    message_stream = model.astream(messages)
    string_stream = parser.atransform(message_stream)
    
    # Convert to AI SDK format
    ui_stream = LangChainAdapter.to_ui_message_stream(string_stream)
    
    print("Parsed string stream:")
    async for chunk in ui_stream:
        if chunk.type == "text-delta":
            print(chunk.content, end="", flush=True)
    print("\n")
    
    # Example 3: Handling LangChain Stream Events v2
    print("3. LangChain Stream Events v2 Format")
    
    async def mock_stream_events():
        """Mock LangChain stream events v2"""
        from ai_sdk.adapters.langchain import LangChainStreamEvent, LangChainAIMessageChunk
        
        # Simulate stream events
        events = [
            LangChainStreamEvent("on_chat_model_stream", {
                "chunk": LangChainAIMessageChunk("Stream events provide ")
            }),
            LangChainStreamEvent("on_chat_model_stream", {
                "chunk": LangChainAIMessageChunk("detailed information about ")
            }),
            LangChainStreamEvent("on_chat_model_stream", {
                "chunk": LangChainAIMessageChunk("the streaming process.")
            }),
        ]
        
        for event in events:
            yield event
            await asyncio.sleep(0.2)
    
    print("Stream events format:")
    stream_events = mock_stream_events()
    ui_stream = LangChainAdapter.to_ui_message_stream(stream_events)
    
    async for chunk in ui_stream:
        if chunk.type == "text-delta":
            print(chunk.content, end="", flush=True)
    print("\n")
    
    # Example 4: Error Handling
    print("4. Error Handling in Stream Conversion")
    
    async def problematic_stream():
        """Stream that encounters errors"""
        yield "Normal text chunk"
        yield {"invalid": "format"}  # This might cause issues
        raise Exception("Simulated stream error")
    
    error_callbacks = create_stream_callbacks(
        on_error=lambda error: print(f"Handled error: {error}")
    )
    
    ui_stream = LangChainAdapter.to_ui_message_stream(
        problematic_stream(), 
        error_callbacks
    )
    
    try:
        async for chunk in ui_stream:
            if chunk.type == "text-delta":
                print(f"Received: {chunk.content}")
            elif chunk.type == "error":
                print(f"Error chunk: {chunk.content}")
    except Exception as e:
        print(f"Stream error: {e}")
    
    print()
    
    # Example 5: Real LangChain Integration (requires langchain package)
    print("5. Real LangChain Integration Example")
    
    try:
        # This would work with real LangChain installation
        # from langchain_openai import ChatOpenAI
        # from langchain.schema import HumanMessage
        
        # chat = ChatOpenAI(
        #     model="gpt-3.5-turbo",
        #     streaming=True,
        #     temperature=0.7
        # )
        # 
        # messages = [HumanMessage(content="What are the benefits of using AI SDK with LangChain?")]
        # stream = chat.astream(messages)
        # 
        # ui_stream = to_ui_message_stream(stream)
        # 
        # print("Real LangChain response:")
        # async for chunk in ui_stream:
        #     if chunk.type == "text-delta":
        #         print(chunk.content, end="", flush=True)
        # print()
        
        print("Skipped - requires langchain and OpenAI API key")
        
    except ImportError:
        print("LangChain not installed - install with: pip install langchain langchain-openai")
    except Exception as e:
        print(f"Error with real LangChain: {e}")
    
    print("\n=== LangChain Adapter Examples Complete ===")
    print("\nKey Benefits:")
    print("✅ Seamless LangChain integration")
    print("✅ Multiple stream format support")
    print("✅ Comprehensive error handling")
    print("✅ Flexible callback system")
    print("✅ Compatible with LangChain LCEL")


if __name__ == "__main__":
    print("LangChain Adapter provides:")
    print("🔗 LangChain message stream conversion")
    print("📝 String output parser support")
    print("📡 Stream Events v2 compatibility")
    print("🛡️ Robust error handling")
    print("⚡ Async/await native support")
    print("")
    
    asyncio.run(main())