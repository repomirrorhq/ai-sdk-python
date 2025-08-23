"""Example demonstrating AI SDK Python testing utilities.

This example shows how to use the testing utilities for:
1. Creating mock providers
2. Testing AI SDK functions with mocks
3. Using stream simulation utilities
4. Building test responses
5. Making assertions about results
"""

import asyncio
from ai_sdk import generate_text, stream_text, embed
from ai_sdk.testing import (
    MockProvider,
    MockLanguageModel,
    MockEmbeddingModel,
    simulate_readable_stream,
    create_test_messages,
    assert_generation_result,
    assert_tool_calls,
    ResponseBuilder,
    StreamBuilder,
)


async def example_mock_provider():
    """Example using mock providers."""
    print("🧪 Mock Provider Example")
    print("=" * 40)
    
    # Create a mock provider with custom responses
    mock_provider = MockProvider()
    
    # Test text generation with mock
    response = await generate_text(
        model=mock_provider.chat("default"),
        messages=create_test_messages("What is AI?"),
    )
    
    print(f"Generated text: {response.text}")
    print(f"Finish reason: {response.finish_reason}")
    print(f"Usage: {response.usage}")
    
    # Assert the response
    assert_generation_result(
        response,
        should_have_usage=True,
        should_have_tool_calls=False,
    )
    print("✅ Assertions passed!")


async def example_custom_mock():
    """Example with customized mock responses."""
    print("\n🎭 Custom Mock Example")
    print("=" * 40)
    
    # Create mock with custom response
    custom_response = ResponseBuilder() \
        .with_text("The meaning of life is 42") \
        .with_finish_reason("stop") \
        .with_usage(15, 25) \
        .with_metadata({"model": "custom-mock"}) \
        .build()
    
    mock_model = MockLanguageModel(
        generate_response=custom_response,
    )
    
    response = await generate_text(
        model=mock_model,
        messages=[{"role": "user", "content": "What is the meaning of life?"}],
    )
    
    print(f"Custom response: {response.text}")
    assert response.text == "The meaning of life is 42"
    print("✅ Custom response works!")


async def example_streaming_mock():
    """Example with streaming mock."""
    print("\n🌊 Streaming Mock Example")
    print("=" * 40)
    
    # Create streaming response
    stream_chunks = ["AI ", "is ", "artificial ", "intelligence"]
    
    mock_model = MockLanguageModel(
        stream_response=stream_chunks,
    )
    
    # Test streaming
    print("Streaming response: ", end="")
    stream = await stream_text(
        model=mock_model,
        messages=[{"role": "user", "content": "What is AI?"}],
    )
    
    async for chunk in stream:
        if chunk.type == "text-delta":
            print(chunk.text, end="", flush=True)
    
    print("\n✅ Streaming works!")


async def example_stream_simulation():
    """Example with stream simulation utilities."""
    print("\n🔄 Stream Simulation Example")
    print("=" * 40)
    
    # Simulate a stream from list
    items = ["chunk1", "chunk2", "chunk3"]
    
    print("Simulated stream: ")
    async for item in simulate_readable_stream(items, delay=0.1):
        print(f"  Received: {item}")
    
    print("✅ Stream simulation works!")


async def example_embedding_mock():
    """Example with embedding mock."""
    print("\n🔢 Embedding Mock Example")
    print("=" * 40)
    
    # Create mock embedding model
    mock_embeddings = MockEmbeddingModel(
        embedding_response=[0.1, 0.2, 0.3, 0.4, 0.5]
    )
    
    result = await embed(
        model=mock_embeddings,
        values=["test text", "another text"],
    )
    
    print(f"Embeddings: {result.embeddings}")
    print(f"Usage: {result.usage}")
    
    assert len(result.embeddings) == 2
    assert len(result.embeddings[0]) == 5
    print("✅ Embedding mock works!")


async def example_tool_testing():
    """Example testing tool calls."""
    print("\n🔧 Tool Call Testing Example")
    print("=" * 40)
    
    # Create a mock that returns tool calls
    tool_call_response = ResponseBuilder() \
        .with_text("I'll help you with that calculation.") \
        .with_tool_call("calculator", {"operation": "add", "a": 2, "b": 3}) \
        .with_finish_reason("tool_calls") \
        .build()
    
    mock_model = MockLanguageModel(
        generate_response=tool_call_response,
    )
    
    # Simulate tool
    def calculator(operation: str, a: int, b: int) -> int:
        if operation == "add":
            return a + b
        return 0
    
    from ai_sdk.tools import tool
    calc_tool = tool("calculator", calculator, "Calculator tool")
    
    response = await generate_text(
        model=mock_model,
        messages=[{"role": "user", "content": "What is 2 + 3?"}],
        tools=[calc_tool],
    )
    
    print(f"Response: {response.text}")
    print(f"Tool calls: {len(response.tool_calls)}")
    
    # Assert tool calls
    assert_tool_calls(
        response,
        expected_tool_names=["calculator"],
        expected_count=1,
    )
    print("✅ Tool call testing works!")


async def example_test_helpers():
    """Example using test helpers."""
    print("\n🛠️  Test Helpers Example")
    print("=" * 40)
    
    # Create test messages
    messages = create_test_messages(
        user_message="Hello AI",
        assistant_message="Hello human!",
        system_message="You are helpful",
    )
    
    print(f"Created {len(messages)} test messages:")
    for i, msg in enumerate(messages):
        print(f"  {i+1}. {msg['role']}: {msg['content']}")
    
    # Test with mock
    mock_provider = MockProvider()
    response = await generate_text(
        model=mock_provider.chat("default"),
        messages=messages,
    )
    
    # Use assertion helpers
    from ai_sdk.testing import assert_non_empty_string, assert_positive_number
    
    assert_non_empty_string(response.text, "response text")
    assert_positive_number(response.usage.total_tokens, "total tokens")
    
    print("✅ Test helpers work!")


async def example_advanced_mocking():
    """Example with advanced mocking scenarios."""
    print("\n🎓 Advanced Mocking Example")
    print("=" * 40)
    
    call_count = 0
    
    async def dynamic_response(call_data):
        """Dynamic response based on call data."""
        nonlocal call_count
        call_count += 1
        
        user_message = call_data["messages"][-1]["content"]
        
        if "hello" in user_message.lower():
            return {"text": f"Hello! (call #{call_count})", "finish_reason": "stop"}
        else:
            return {"text": f"I heard: {user_message} (call #{call_count})", "finish_reason": "stop"}
    
    mock_model = MockLanguageModel(
        generate_response=dynamic_response,
    )
    
    # Test multiple calls
    for message in ["Hello there!", "How are you?", "Hello again!"]:
        response = await generate_text(
            model=mock_model,
            messages=[{"role": "user", "content": message}],
        )
        print(f"Input: '{message}' -> Output: '{response.text}'")
    
    # Check that all calls were recorded
    print(f"Total calls made: {len(mock_model.generate_calls)}")
    assert len(mock_model.generate_calls) == 3
    print("✅ Advanced mocking works!")


async def main():
    """Run all examples."""
    await example_mock_provider()
    await example_custom_mock()
    await example_streaming_mock()
    await example_stream_simulation()
    await example_embedding_mock()
    await example_tool_testing()
    await example_test_helpers()
    await example_advanced_mocking()
    
    print("\n🎉 All testing examples completed successfully!")
    print("=" * 50)
    print("💡 These utilities make it easy to:")
    print("   - Test AI SDK functions without real API calls")
    print("   - Create predictable responses for testing")
    print("   - Simulate streaming and async behavior")
    print("   - Make assertions about AI interactions")
    print("   - Build comprehensive test suites")


if __name__ == "__main__":
    asyncio.run(main())