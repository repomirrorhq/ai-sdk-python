# Testing Guide for AI SDK Python

This guide explains how to test applications built with AI SDK Python using the built-in testing utilities.

## Overview

AI SDK Python provides comprehensive testing utilities that allow you to:
- Mock AI providers without making real API calls
- Create predictable responses for testing
- Simulate streaming and async behavior
- Make assertions about AI interactions
- Build comprehensive test suites

## Quick Start

### Basic Mock Provider

```python
import asyncio
from ai_sdk import generate_text, MockProvider

async def test_basic_generation():
    # Create a mock provider
    mock_provider = MockProvider()
    
    # Use it like any real provider
    response = await generate_text(
        model=mock_provider.chat("default"),
        messages=[{"role": "user", "content": "Hello"}],
    )
    
    # The mock returns predictable responses
    assert response.text == "Mock response"
    assert response.finish_reason == "stop"
```

### Custom Mock Responses

```python
from ai_sdk.testing import MockLanguageModel, ResponseBuilder

# Create custom response
custom_response = ResponseBuilder() \
    .with_text("Custom AI response") \
    .with_usage(15, 25) \
    .build()

mock_model = MockLanguageModel(generate_response=custom_response)

response = await generate_text(
    model=mock_model,
    messages=[{"role": "user", "content": "What is AI?"}]
)

assert response.text == "Custom AI response"
assert response.usage.prompt_tokens == 15
```

## Mock Providers

### MockLanguageModel

Mock language models for text generation:

```python
from ai_sdk.testing import MockLanguageModel

# Basic mock with static response
mock = MockLanguageModel(
    provider="test-provider",
    model_id="test-model",
    generate_response="Static response",
)

# Mock with dynamic responses
async def dynamic_response(call_data):
    user_message = call_data["messages"][-1]["content"]
    return {"text": f"You said: {user_message}", "finish_reason": "stop"}

mock = MockLanguageModel(generate_response=dynamic_response)

# Mock with streaming
mock = MockLanguageModel(
    stream_response=["Hello ", "world", "!"]
)
```

### MockEmbeddingModel

Mock embedding models:

```python
from ai_sdk.testing import MockEmbeddingModel
from ai_sdk import embed

mock = MockEmbeddingModel(
    embedding_response=[0.1, 0.2, 0.3, 0.4, 0.5]
)

result = await embed(
    model=mock,
    values=["text1", "text2"]
)

assert len(result.embeddings) == 2
assert len(result.embeddings[0]) == 5
```

### MockProvider

Mock provider that supports all model types:

```python
from ai_sdk.testing import MockProvider, MockLanguageModel

# Use default mocks
provider = MockProvider()

# Or customize specific models
custom_model = MockLanguageModel(generate_response="Custom response")
provider = MockProvider(
    language_models={"gpt-4": custom_model}
)

# Access models like normal providers
model = provider.chat("gpt-4")
response = await generate_text(model=model, messages=messages)
```

## Stream Simulation

### Basic Stream Simulation

```python
from ai_sdk.testing import simulate_readable_stream

# Simulate streaming from a list
items = ["chunk1", "chunk2", "chunk3"]

async for item in simulate_readable_stream(items, delay=0.1):
    print(f"Received: {item}")
```

### Stream Utilities

```python
from ai_sdk.testing import (
    convert_array_to_async_iterable,
    convert_async_iterable_to_array
)

# Convert array to async iterator
async_iter = convert_array_to_async_iterable([1, 2, 3])

# Convert async iterator back to array
result = await convert_async_iterable_to_array(async_iter)
assert result == [1, 2, 3]
```

### Mock Streaming

```python
from ai_sdk.testing import MockLanguageModel
from ai_sdk import stream_text

mock = MockLanguageModel(
    stream_response=["AI ", "is ", "amazing"]
)

stream = await stream_text(
    model=mock,
    messages=[{"role": "user", "content": "Tell me about AI"}]
)

chunks = []
async for chunk in stream:
    if chunk.type == "text-delta":
        chunks.append(chunk.text)

assert chunks == ["AI ", "is ", "amazing"]
```

## Test Helpers

### Creating Test Data

```python
from ai_sdk.testing import create_test_messages, create_test_content

# Create conversation messages
messages = create_test_messages(
    user_message="Hello AI",
    assistant_message="Hello human!",
    system_message="You are helpful"
)

# Create multimodal content
content = create_test_content(
    text="Analyze this image",
    image_url="https://example.com/image.jpg"
)
```

### Assertions

```python
from ai_sdk.testing import assert_generation_result, assert_tool_calls

# Assert generation results
assert_generation_result(
    response,
    expected_text="Hello there!",
    expected_finish_reason="stop",
    should_have_usage=True,
    should_have_tool_calls=False
)

# Assert tool calls
assert_tool_calls(
    response,
    expected_tool_names=["calculator", "weather"],
    expected_count=2
)
```

## Response Builders

### ResponseBuilder

Build complex test responses:

```python
from ai_sdk.testing import ResponseBuilder

response = ResponseBuilder() \
    .with_text("I'll help you calculate that.") \
    .with_tool_call("calculator", {"operation": "add", "a": 2, "b": 3}) \
    .with_finish_reason("tool_calls") \
    .with_usage(20, 30) \
    .with_metadata({"model": "gpt-4"}) \
    .build()

mock = MockLanguageModel(generate_response=response)
```

### StreamBuilder

Build streaming responses:

```python
from ai_sdk.testing import StreamBuilder

chunks = StreamBuilder() \
    .add_text_chunk("Hello") \
    .add_text_chunk(" world") \
    .add_finish_chunk("stop") \
    .build()

# Use as async iterator
async for chunk in StreamBuilder().add_text_chunk("test").build_async_iterator():
    print(chunk)
```

## Testing Patterns

### Testing with Real vs Mock Providers

```python
import os
import pytest
from ai_sdk import generate_text, create_openai, MockProvider

@pytest.fixture
def ai_provider():
    """Use real provider in CI, mock in local tests."""
    if os.getenv("OPENAI_API_KEY"):
        return create_openai()
    else:
        return MockProvider()

async def test_ai_generation(ai_provider):
    response = await generate_text(
        model=ai_provider.chat("gpt-4o-mini"),
        messages=[{"role": "user", "content": "Hello"}]
    )
    
    # Works with both real and mock providers
    assert len(response.text) > 0
```

### Testing Tool Calls

```python
from ai_sdk.testing import MockLanguageModel, ResponseBuilder
from ai_sdk.tools import tool

# Define tool
@tool
def calculator(operation: str, a: int, b: int) -> int:
    if operation == "add":
        return a + b
    return 0

# Mock tool call response
response = ResponseBuilder() \
    .with_text("I'll calculate that for you.") \
    .with_tool_call("calculator", {"operation": "add", "a": 5, "b": 3}) \
    .build()

mock = MockLanguageModel(generate_response=response)

result = await generate_text(
    model=mock,
    messages=[{"role": "user", "content": "What is 5 + 3?"}],
    tools=[calculator]
)

assert len(result.tool_calls) == 1
assert result.tool_calls[0].result == 8
```

### Testing Streaming

```python
async def test_streaming():
    mock = MockLanguageModel(
        stream_response=["Streaming ", "response ", "works!"]
    )
    
    chunks = []
    stream = await stream_text(
        model=mock,
        messages=[{"role": "user", "content": "Stream test"}]
    )
    
    async for chunk in stream:
        if chunk.type == "text-delta":
            chunks.append(chunk.text)
    
    assert "".join(chunks) == "Streaming response works!"
```

### Testing Error Handling

```python
from ai_sdk.testing import ResponseBuilder

# Mock error response
error_response = ResponseBuilder() \
    .with_error("Rate limit exceeded", "rate_limit") \
    .build()

mock = MockLanguageModel(generate_response=error_response)

with pytest.raises(Exception) as exc_info:
    await generate_text(
        model=mock,
        messages=[{"role": "user", "content": "Test"}]
    )

assert "rate_limit" in str(exc_info.value)
```

## Advanced Testing

### Recording and Replaying Calls

```python
class RecordingMock(MockLanguageModel):
    def __init__(self):
        super().__init__()
        self.recorded_calls = []
    
    async def generate(self, messages, **kwargs):
        # Record all calls for analysis
        self.recorded_calls.append({
            "messages": messages,
            "kwargs": kwargs,
            "timestamp": time.time()
        })
        return await super().generate(messages, **kwargs)

mock = RecordingMock()
# ... use mock in tests ...

# Analyze recorded calls
assert len(mock.recorded_calls) == 3
assert "Hello" in mock.recorded_calls[0]["messages"][0]["content"]
```

### Testing with Multiple Models

```python
async def test_model_comparison():
    """Test that different models produce different responses."""
    
    model_a = MockLanguageModel(generate_response="Response A")
    model_b = MockLanguageModel(generate_response="Response B")
    
    provider = MockProvider(language_models={
        "model-a": model_a,
        "model-b": model_b,
    })
    
    response_a = await generate_text(
        model=provider.chat("model-a"),
        messages=[{"role": "user", "content": "Test"}]
    )
    
    response_b = await generate_text(
        model=provider.chat("model-b"), 
        messages=[{"role": "user", "content": "Test"}]
    )
    
    assert response_a.text != response_b.text
```

### Performance Testing

```python
import time
from ai_sdk.testing import MockLanguageModel

async def test_response_time():
    """Test that responses come back quickly."""
    
    mock = MockLanguageModel(delay=0.1)  # 100ms delay
    
    start = time.time()
    response = await generate_text(
        model=mock,
        messages=[{"role": "user", "content": "Fast test"}]
    )
    duration = time.time() - start
    
    assert 0.1 <= duration <= 0.2  # Should be around 100ms
    assert response.text == "Mock response"
```

## Integration with Testing Frameworks

### pytest Integration

```python
# conftest.py
import pytest
from ai_sdk.testing import MockProvider

@pytest.fixture
def mock_ai():
    return MockProvider()

@pytest.fixture
async def ai_response(mock_ai):
    response = await generate_text(
        model=mock_ai.chat(),
        messages=[{"role": "user", "content": "Test message"}]
    )
    return response

# test_my_app.py
def test_ai_response_structure(ai_response):
    assert hasattr(ai_response, 'text')
    assert hasattr(ai_response, 'usage')
    assert hasattr(ai_response, 'finish_reason')
```

### unittest Integration

```python
import unittest
from ai_sdk.testing import MockProvider, assert_generation_result

class TestAIIntegration(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mock_provider = MockProvider()
    
    async def test_generate_text(self):
        response = await generate_text(
            model=self.mock_provider.chat(),
            messages=[{"role": "user", "content": "Hello"}]
        )
        
        assert_generation_result(
            response,
            should_have_usage=True,
            should_have_tool_calls=False
        )
```

## Best Practices

1. **Use Mock Providers for Unit Tests**: Don't make real API calls in unit tests
2. **Test Both Success and Error Cases**: Use error response builders
3. **Validate Call Arguments**: Check that mocks receive expected inputs
4. **Test Streaming and Non-Streaming**: Both modes should work
5. **Use Realistic Test Data**: Create test messages that resemble real usage
6. **Assert on Multiple Properties**: Check text, usage, finish_reason, etc.
7. **Test Tool Integration**: Mock tool calls and verify execution
8. **Performance Test with Delays**: Simulate real-world latency

## Common Testing Scenarios

### Testing a Chatbot

```python
async def test_chatbot_conversation():
    # Mock conversational responses
    responses = [
        "Hello! How can I help you?",
        "I can help with that.",
        "Is there anything else?"
    ]
    
    mock = MockLanguageModel()
    conversation = []
    
    for i, user_msg in enumerate(["Hi", "Help me", "No thanks"]):
        mock.generate_response = responses[i]
        
        conversation.append({"role": "user", "content": user_msg})
        
        response = await generate_text(
            model=mock,
            messages=conversation.copy()
        )
        
        conversation.append({
            "role": "assistant", 
            "content": response.text
        })
        
        assert response.text == responses[i]
```

### Testing RAG Applications

```python
async def test_rag_system():
    # Mock retrieval and generation
    mock_embedding = MockEmbeddingModel(
        embedding_response=[0.1, 0.2, 0.3]
    )
    
    mock_llm = MockLanguageModel(
        generate_response="Based on the context, the answer is..."
    )
    
    # Simulate RAG workflow
    query = "What is AI?"
    
    # 1. Embed query
    query_embedding = await embed(model=mock_embedding, values=[query])
    
    # 2. Generate with context
    context = "AI is artificial intelligence..."
    response = await generate_text(
        model=mock_llm,
        messages=[
            {"role": "system", "content": f"Context: {context}"},
            {"role": "user", "content": query}
        ]
    )
    
    assert "Based on the context" in response.text
```

This comprehensive testing framework makes it easy to build reliable AI applications with thorough test coverage.