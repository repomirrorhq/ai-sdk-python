"""Tests for AI SDK testing utilities."""

import asyncio
import pytest
from unittest.mock import AsyncMock

from ai_sdk.testing import (
    MockProvider,
    MockLanguageModel,
    MockEmbeddingModel,
    MockImageModel,
    MockSpeechModel,
    MockTranscriptionModel,
    simulate_readable_stream,
    convert_array_to_async_iterable,
    convert_async_iterable_to_array,
    create_test_messages,
    create_test_content,
    assert_tool_calls,
    assert_generation_result,
    build_text_response,
    build_tool_call_response,
    ResponseBuilder,
    StreamBuilder,
)


class TestMockProviders:
    """Test mock provider functionality."""
    
    @pytest.mark.asyncio
    async def test_mock_language_model_basic(self):
        """Test basic mock language model functionality."""
        mock_model = MockLanguageModel(
            provider="test-provider",
            model_id="test-model",
            generate_response="Test response",
        )
        
        result = await mock_model.generate(
            messages=[{"role": "user", "content": "Hello"}],
        )
        
        assert result["text"] == "Test response"
        assert result["finish_reason"] == "stop"
        assert len(mock_model.generate_calls) == 1
        assert mock_model.generate_calls[0]["messages"][0]["content"] == "Hello"
    
    @pytest.mark.asyncio
    async def test_mock_language_model_streaming(self):
        """Test mock language model streaming."""
        mock_model = MockLanguageModel(
            stream_response=["Hello ", "world", "!"],
        )
        
        chunks = []
        async for chunk in mock_model.stream(
            messages=[{"role": "user", "content": "Hi"}],
        ):
            chunks.append(chunk)
        
        # Should have 3 text chunks + 1 finish chunk
        assert len(chunks) == 4
        assert chunks[0]["text"] == "Hello "
        assert chunks[1]["text"] == "world"
        assert chunks[2]["text"] == "!"
        assert chunks[3]["type"] == "finish"
    
    @pytest.mark.asyncio
    async def test_mock_language_model_callable_response(self):
        """Test mock language model with callable response."""
        async def dynamic_response(call_data):
            user_msg = call_data["messages"][-1]["content"]
            return {"text": f"Echo: {user_msg}", "finish_reason": "stop"}
        
        mock_model = MockLanguageModel(generate_response=dynamic_response)
        
        result = await mock_model.generate(
            messages=[{"role": "user", "content": "Test message"}],
        )
        
        assert result["text"] == "Echo: Test message"
    
    @pytest.mark.asyncio
    async def test_mock_embedding_model(self):
        """Test mock embedding model."""
        mock_model = MockEmbeddingModel(
            embedding_response=[0.1, 0.2, 0.3],
        )
        
        result = await mock_model.embed(["text1", "text2"])
        
        assert len(result["embeddings"]) == 2
        assert result["embeddings"][0] == [0.1, 0.2, 0.3]
        assert result["embeddings"][1] == [0.1, 0.2, 0.3]
        assert len(mock_model.embed_calls) == 1
    
    @pytest.mark.asyncio
    async def test_mock_image_model(self):
        """Test mock image model."""
        mock_model = MockImageModel(
            image_response=b"fake-image-data",
        )
        
        result = await mock_model.generate_image("A cat")
        
        assert result["image"] == b"fake-image-data"
        assert result["metadata"]["prompt"] == "A cat"
        assert len(mock_model.generate_calls) == 1
    
    @pytest.mark.asyncio
    async def test_mock_speech_model(self):
        """Test mock speech model."""
        mock_model = MockSpeechModel(
            speech_response=b"fake-audio-data",
        )
        
        result = await mock_model.generate_speech("Hello world")
        
        assert result["audio"] == b"fake-audio-data"
        assert result["metadata"]["text"] == "Hello world"
        assert len(mock_model.generate_calls) == 1
    
    @pytest.mark.asyncio
    async def test_mock_transcription_model(self):
        """Test mock transcription model."""
        mock_model = MockTranscriptionModel(
            transcription_response="Hello world",
        )
        
        result = await mock_model.transcribe(b"fake-audio-data")
        
        assert result["text"] == "Hello world"
        assert result["metadata"]["audio_duration"] == 10.0
        assert len(mock_model.transcribe_calls) == 1
    
    def test_mock_provider(self):
        """Test mock provider with multiple models."""
        # Create custom models
        custom_lang_model = MockLanguageModel(generate_response="Custom response")
        custom_embed_model = MockEmbeddingModel(embedding_response=[1.0, 2.0])
        
        provider = MockProvider(
            language_models={"custom": custom_lang_model},
            embedding_models={"custom": custom_embed_model},
        )
        
        # Test language model access
        lang_model = provider.chat("custom")
        assert lang_model == custom_lang_model
        
        # Test embedding model access
        embed_model = provider.embedding("custom")
        assert embed_model == custom_embed_model
        
        # Test default models exist
        default_lang = provider.chat("default")
        assert isinstance(default_lang, MockLanguageModel)
    
    def test_mock_provider_no_such_model(self):
        """Test mock provider error handling."""
        provider = MockProvider()
        
        with pytest.raises(Exception):  # Should be NoSuchModelError
            provider.chat("nonexistent")


class TestStreamUtils:
    """Test stream simulation utilities."""
    
    @pytest.mark.asyncio
    async def test_simulate_readable_stream(self):
        """Test readable stream simulation."""
        items = ["a", "b", "c"]
        
        result = []
        async for item in simulate_readable_stream(items):
            result.append(item)
        
        assert result == ["a", "b", "c"]
    
    @pytest.mark.asyncio
    async def test_simulate_readable_stream_with_delay(self):
        """Test readable stream simulation with delay."""
        import time
        
        items = ["x", "y"]
        start_time = time.time()
        
        result = []
        async for item in simulate_readable_stream(items, delay=0.01):
            result.append(item)
        
        elapsed = time.time() - start_time
        assert result == ["x", "y"]
        assert elapsed >= 0.02  # Should take at least 20ms
    
    @pytest.mark.asyncio
    async def test_convert_array_to_async_iterable(self):
        """Test array to async iterable conversion."""
        items = [1, 2, 3]
        
        result = []
        async for item in convert_array_to_async_iterable(items):
            result.append(item)
        
        assert result == [1, 2, 3]
    
    @pytest.mark.asyncio
    async def test_convert_async_iterable_to_array(self):
        """Test async iterable to array conversion."""
        async def async_gen():
            for i in range(3):
                yield i
        
        result = await convert_async_iterable_to_array(async_gen())
        assert result == [0, 1, 2]


class TestHelpers:
    """Test helper functions."""
    
    def test_create_test_messages(self):
        """Test test message creation."""
        messages = create_test_messages(
            user_message="Hello",
            assistant_message="Hi there",
            system_message="Be helpful",
        )
        
        assert len(messages) == 3
        assert messages[0]["role"] == "system"
        assert messages[0]["content"] == "Be helpful"
        assert messages[1]["role"] == "user" 
        assert messages[1]["content"] == "Hello"
        assert messages[2]["role"] == "assistant"
        assert messages[2]["content"] == "Hi there"
    
    def test_create_test_messages_minimal(self):
        """Test minimal test message creation."""
        messages = create_test_messages()
        
        assert len(messages) == 2  # user + assistant
        assert messages[0]["role"] == "user"
        assert messages[1]["role"] == "assistant"
    
    def test_create_test_content(self):
        """Test test content creation."""
        content = create_test_content(
            text="Hello",
            image_url="https://example.com/image.jpg",
        )
        
        assert len(content) == 2
        assert content[0]["type"] == "text"
        assert content[0]["text"] == "Hello"
        assert content[1]["type"] == "image"
        assert content[1]["image"]["url"] == "https://example.com/image.jpg"
    
    def test_assert_generation_result(self):
        """Test generation result assertions."""
        # Mock result object
        class MockResult:
            text = "Hello"
            finish_reason = "stop"
            usage = {"tokens": 10}
            tool_calls = []
        
        result = MockResult()
        
        # Should not raise
        assert_generation_result(
            result,
            expected_text="Hello",
            expected_finish_reason="stop",
            should_have_usage=True,
            should_have_tool_calls=False,
        )
    
    def test_assert_tool_calls(self):
        """Test tool call assertions."""
        # Mock result with tool calls
        class MockToolCall:
            tool_name = "test_tool"
        
        class MockResult:
            tool_calls = [MockToolCall()]
        
        result = MockResult()
        
        # Should not raise
        assert_tool_calls(
            result,
            expected_tool_names=["test_tool"],
            expected_count=1,
        )


class TestResponseBuilders:
    """Test response builder utilities."""
    
    def test_build_text_response(self):
        """Test text response builder."""
        response = build_text_response(
            text="Hello world",
            finish_reason="stop",
            usage_prompt_tokens=5,
            usage_completion_tokens=10,
        )
        
        assert response["text"] == "Hello world"
        assert response["finish_reason"] == "stop"
        assert response["usage"]["prompt_tokens"] == 5
        assert response["usage"]["completion_tokens"] == 10
        assert response["usage"]["total_tokens"] == 15
    
    def test_build_tool_call_response(self):
        """Test tool call response builder."""
        tool_calls = [{
            "id": "call_1",
            "type": "function",
            "function": {
                "name": "test_tool",
                "arguments": {"param": "value"}
            }
        }]
        
        response = build_tool_call_response(tool_calls)
        
        assert response["tool_calls"] == tool_calls
        assert response["finish_reason"] == "tool_calls"
    
    def test_response_builder(self):
        """Test ResponseBuilder class."""
        response = ResponseBuilder() \
            .with_text("Hello") \
            .with_tool_call("test_tool", {"param": "value"}) \
            .with_finish_reason("tool_calls") \
            .with_usage(10, 20) \
            .build()
        
        assert response["text"] == "Hello"
        assert len(response["tool_calls"]) == 1
        assert response["tool_calls"][0]["function"]["name"] == "test_tool"
        assert response["finish_reason"] == "tool_calls"
        assert response["usage"]["prompt_tokens"] == 10
    
    def test_stream_builder(self):
        """Test StreamBuilder class."""
        chunks = StreamBuilder() \
            .add_text_chunk("Hello") \
            .add_text_chunk(" world") \
            .add_finish_chunk() \
            .build()
        
        assert len(chunks) == 3
        assert chunks[0]["text_delta"] == "Hello"
        assert chunks[1]["text_delta"] == " world"
        assert chunks[2]["type"] == "finish"
    
    @pytest.mark.asyncio
    async def test_stream_builder_async(self):
        """Test StreamBuilder async iterator."""
        builder = StreamBuilder() \
            .add_text_chunk("test") \
            .add_finish_chunk()
        
        chunks = []
        async for chunk in builder.build_async_iterator():
            chunks.append(chunk)
        
        assert len(chunks) == 2
        assert chunks[0]["text_delta"] == "test"
        assert chunks[1]["type"] == "finish"


if __name__ == "__main__":
    pytest.main([__file__])