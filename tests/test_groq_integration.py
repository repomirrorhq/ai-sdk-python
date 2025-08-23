#!/usr/bin/env python3
"""Integration tests for Groq AI provider.

These tests verify the Groq provider's functionality including:
- Text generation and streaming
- Error handling
- API parameter handling
- Response processing
- Usage tracking

Tests use mocked HTTP responses to avoid requiring real API keys during CI/CD.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from ai_sdk.providers.groq import GroqProvider, GroqChatLanguageModel, create_groq
from ai_sdk.providers.types import Message, Usage, FinishReason
from ai_sdk.errors import APIError, InvalidArgumentError
from ai_sdk.core.generate_text import generate_text
from ai_sdk.core.generate_text import stream_text


class TestGroqProvider:
    """Test Groq provider initialization and configuration."""
    
    def test_create_groq_with_api_key(self):
        """Test creating Groq provider with explicit API key."""
        provider = create_groq(api_key="test-key")
        assert isinstance(provider, GroqProvider)
        assert provider.api_key == "test-key"
        assert provider.base_url == "https://api.groq.com/openai/v1"
    
    def test_create_groq_with_custom_config(self):
        """Test creating Groq provider with custom configuration."""
        provider = create_groq(
            api_key="test-key",
            base_url="https://custom.groq.com/v1", 
            max_retries=5,
            timeout=120.0,
            extra_headers={"Custom-Header": "value"}
        )
        
        assert provider.base_url == "https://custom.groq.com/v1"
        assert provider.max_retries == 5
        assert provider.timeout == 120.0
        assert provider.extra_headers == {"Custom-Header": "value"}
    
    @patch.dict("os.environ", {"GROQ_API_KEY": "env-key"})
    def test_create_groq_from_env_var(self):
        """Test creating Groq provider from environment variable."""
        provider = create_groq()
        assert provider.api_key == "env-key"
    
    @patch.dict("os.environ", {}, clear=True)
    def test_create_groq_missing_api_key(self):
        """Test error when API key is missing."""
        with pytest.raises(InvalidArgumentError, match="Groq API key is required"):
            create_groq()
    
    def test_language_model_creation(self):
        """Test creating language models from provider."""
        provider = create_groq(api_key="test-key")
        model = provider.language_model("llama-3.1-8b-instant")
        
        assert isinstance(model, GroqChatLanguageModel)
        assert model.model_id == "llama-3.1-8b-instant"
        assert model.api_key == "test-key"


class TestGroqChatLanguageModel:
    """Test Groq chat language model functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.model = GroqChatLanguageModel(
            model_id="llama-3.1-8b-instant",
            api_key="test-api-key"
        )
    
    def test_model_initialization(self):
        """Test model initialization with various parameters."""
        model = GroqChatLanguageModel(
            model_id="mixtral-8x7b-32768",
            api_key="test-key",
            base_url="https://custom.groq.com/v1",
            max_retries=3,
            timeout=90.0,
            extra_headers={"X-Custom": "header"}
        )
        
        assert model.model_id == "mixtral-8x7b-32768"
        assert model.api_key == "test-key"
        assert model.base_url == "https://custom.groq.com/v1"
        assert model.max_retries == 3
        assert model.timeout == 90.0
        assert model.extra_headers == {"X-Custom": "header"}
    
    def test_headers_generation(self):
        """Test HTTP headers generation."""
        headers = self.model._get_headers()
        
        assert headers["Authorization"] == "Bearer test-api-key"
        assert headers["Content-Type"] == "application/json"
    
    def test_message_conversion_text_only(self):
        """Test converting simple text messages to Groq format."""
        messages = [
            Message(role="system", content="You are helpful."),
            Message(role="user", content="Hello!"),
            Message(role="assistant", content="Hi there!")
        ]
        
        groq_messages = self.model._convert_messages_to_groq_format(messages)
        
        expected = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        assert groq_messages == expected
    
    def test_finish_reason_mapping(self):
        """Test mapping of finish reasons from Groq to AI SDK format."""
        test_cases = [
            ("stop", FinishReason.STOP),
            ("length", FinishReason.LENGTH), 
            ("function_call", FinishReason.TOOL_CALLS),
            ("tool_calls", FinishReason.TOOL_CALLS),
            ("content_filter", FinishReason.CONTENT_FILTER),
            ("unknown", FinishReason.OTHER),
            (None, None)
        ]
        
        for groq_reason, expected in test_cases:
            result = self.model._map_finish_reason(groq_reason)
            assert result == expected


class TestGroqTextGeneration:
    """Test text generation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.provider = create_groq(api_key="test-key")
        self.model = self.provider.language_model("llama-3.1-8b-instant")
    
    @pytest.mark.asyncio
    async def test_successful_text_generation(self):
        """Test successful text generation with mocked response."""
        
        # Mock successful API response
        mock_response_data = {
            "id": "chatcmpl-test",
            "object": "chat.completion",
            "model": "llama-3.1-8b-instant",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Hello! How can I help you today?"
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 9,
                "total_tokens": 19
            }
        }
        
        with patch.object(self.model, 'client') as mock_client:
            mock_response = AsyncMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = MagicMock()
            mock_client.post.return_value = mock_response
            
            messages = [Message(role="user", content="Hello")]
            result = await self.model.do_generate(
                messages=messages,
                max_tokens=100,
                temperature=0.7
            )
            
            assert result.text == "Hello! How can I help you today?"
            assert result.finish_reason == FinishReason.STOP
            assert result.usage.prompt_tokens == 10
            assert result.usage.completion_tokens == 9
            assert result.usage.total_tokens == 19
            assert len(result.response_messages) == 1
            assert result.response_messages[0].content == "Hello! How can I help you today?"
    
    @pytest.mark.asyncio
    async def test_text_generation_with_all_parameters(self):
        """Test text generation with all available parameters."""
        
        mock_response_data = {
            "choices": [{
                "message": {"content": "Test response"},
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 5, "completion_tokens": 2, "total_tokens": 7}
        }
        
        with patch.object(self.model, 'client') as mock_client:
            mock_response = AsyncMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = MagicMock()
            mock_client.post.return_value = mock_response
            
            messages = [Message(role="user", content="Test")]
            await self.model.do_generate(
                messages=messages,
                max_tokens=100,
                temperature=0.8,
                top_p=0.9,
                frequency_penalty=0.5,
                presence_penalty=0.3,
                stop_sequences=["END"],
                seed=42
            )
            
            # Verify the request was made with correct parameters
            call_args = mock_client.post.call_args
            request_data = call_args.kwargs['json']
            
            assert request_data['model'] == 'llama-3.1-8b-instant'
            assert request_data['max_tokens'] == 100
            assert request_data['temperature'] == 0.8
            assert request_data['top_p'] == 0.9
            assert request_data['frequency_penalty'] == 0.5
            assert request_data['presence_penalty'] == 0.3
            assert request_data['stop'] == ["END"]
            assert request_data['seed'] == 42
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """Test API error handling."""
        
        # Mock error response
        error_response_data = {
            "error": {
                "message": "Invalid API key",
                "type": "invalid_request_error"
            }
        }
        
        with patch.object(self.model, 'client') as mock_client:
            mock_response = AsyncMock()
            mock_response.json.return_value = error_response_data
            mock_response.status_code = 401
            mock_response.raise_for_status = MagicMock()
            mock_client.post.return_value = mock_response
            
            messages = [Message(role="user", content="Test")]
            
            with pytest.raises(APIError, match="Groq API error: Invalid API key"):
                await self.model.do_generate(messages=messages)
    
    @pytest.mark.asyncio
    async def test_http_error_handling(self):
        """Test HTTP error handling."""
        
        from httpx import HTTPStatusError, Request, Response
        
        with patch.object(self.model, 'client') as mock_client:
            # Create a mock HTTP error
            request = Request("POST", "https://api.groq.com/openai/v1/chat/completions")
            response = Response(500, json={"error": {"message": "Server error"}})
            http_error = HTTPStatusError("Server error", request=request, response=response)
            
            mock_client.post.side_effect = http_error
            
            messages = [Message(role="user", content="Test")]
            
            with pytest.raises(APIError, match="Groq API request failed"):
                await self.model.do_generate(messages=messages)


class TestGroqStreaming:
    """Test streaming functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.provider = create_groq(api_key="test-key")
        self.model = self.provider.language_model("llama-3.1-8b-instant")
    
    @pytest.mark.asyncio
    async def test_successful_streaming(self):
        """Test successful streaming with mocked responses."""
        
        # Mock streaming response chunks
        stream_chunks = [
            'data: {"choices":[{"delta":{"content":"Hello"}}]}\n\n',
            'data: {"choices":[{"delta":{"content":" there"}}]}\n\n',
            'data: {"choices":[{"delta":{"content":"!"}}]}\n\n',
            'data: {"choices":[{"finish_reason":"stop"}],"usage":{"prompt_tokens":5,"completion_tokens":3,"total_tokens":8}}\n\n',
            'data: [DONE]\n\n'
        ]
        
        async def mock_aiter_lines():
            for chunk in stream_chunks:
                for line in chunk.strip().split('\n'):
                    if line:
                        yield line
        
        with patch.object(self.model, 'client') as mock_client:
            mock_response = AsyncMock()
            mock_response.aiter_lines = mock_aiter_lines
            mock_response.raise_for_status = MagicMock()
            
            mock_stream_context = AsyncMock()
            mock_stream_context.__aenter__.return_value = mock_response
            mock_client.stream.return_value = mock_stream_context
            
            messages = [Message(role="user", content="Hello")]
            chunks = []
            
            async for chunk in self.model.do_stream(messages=messages):
                chunks.append(chunk)
            
            # Verify we got the expected chunks
            assert len(chunks) >= 3  # At least text chunks
            
            # Check text deltas
            text_chunks = [c for c in chunks if c.text_delta]
            assert len(text_chunks) == 3
            assert text_chunks[0].text_delta == "Hello"
            assert text_chunks[1].text_delta == " there"
            assert text_chunks[2].text_delta == "!"
            
            # Check finish reason
            finish_chunks = [c for c in chunks if c.finish_reason]
            assert len(finish_chunks) == 1
            assert finish_chunks[0].finish_reason == FinishReason.STOP
    
    @pytest.mark.asyncio
    async def test_streaming_with_parameters(self):
        """Test streaming with various parameters."""
        
        stream_chunks = [
            'data: {"choices":[{"delta":{"content":"Test"}}]}\n\n',
            'data: [DONE]\n\n'
        ]
        
        async def mock_aiter_lines():
            for chunk in stream_chunks:
                for line in chunk.strip().split('\n'):
                    if line:
                        yield line
        
        with patch.object(self.model, 'client') as mock_client:
            mock_response = AsyncMock()
            mock_response.aiter_lines = mock_aiter_lines
            mock_response.raise_for_status = MagicMock()
            
            mock_stream_context = AsyncMock()
            mock_stream_context.__aenter__.return_value = mock_response
            mock_client.stream.return_value = mock_stream_context
            
            messages = [Message(role="user", content="Test")]
            chunks = []
            
            async for chunk in self.model.do_stream(
                messages=messages,
                max_tokens=50,
                temperature=0.5,
                stop_sequences=["END"]
            ):
                chunks.append(chunk)
            
            # Verify the request parameters
            call_args = mock_client.stream.call_args
            request_data = call_args.kwargs['json']
            
            assert request_data['stream'] is True
            assert request_data['max_tokens'] == 50
            assert request_data['temperature'] == 0.5
            assert request_data['stop'] == ["END"]
    
    @pytest.mark.asyncio
    async def test_streaming_error_handling(self):
        """Test error handling during streaming."""
        
        from httpx import HTTPStatusError, Request, Response
        
        with patch.object(self.model, 'client') as mock_client:
            # Create a mock HTTP error
            request = Request("POST", "https://api.groq.com/openai/v1/chat/completions")
            response = Response(429, json={"error": {"message": "Rate limit exceeded"}})
            http_error = HTTPStatusError("Rate limit", request=request, response=response)
            
            mock_stream_context = AsyncMock()
            mock_stream_context.__aenter__.side_effect = http_error
            mock_client.stream.return_value = mock_stream_context
            
            messages = [Message(role="user", content="Test")]
            
            with pytest.raises(APIError, match="Groq API streaming request failed"):
                async for chunk in self.model.do_stream(messages=messages):
                    pass


class TestGroqIntegration:
    """Integration tests using the high-level API functions."""
    
    @pytest.mark.asyncio
    async def test_generate_text_integration(self):
        """Test generate_text integration with Groq provider."""
        
        mock_response_data = {
            "choices": [{
                "message": {"content": "Integration test response"},
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 8, "completion_tokens": 3, "total_tokens": 11}
        }
        
        groq = create_groq(api_key="test-key")
        model = groq.language_model("llama-3.1-8b-instant")
        
        with patch.object(model, 'client') as mock_client:
            mock_response = AsyncMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = MagicMock()
            mock_client.post.return_value = mock_response
            
            result = await generate_text(
                model=model,
                prompt="Test integration",
                max_tokens=100
            )
            
            assert result.text == "Integration test response"
            assert result.finish_reason == FinishReason.STOP
            assert result.usage.total_tokens == 11
    
    @pytest.mark.asyncio
    async def test_stream_text_integration(self):
        """Test stream_text integration with Groq provider."""
        
        stream_chunks = [
            'data: {"choices":[{"delta":{"content":"Stream"}}]}\n\n',
            'data: {"choices":[{"delta":{"content":" test"}}]}\n\n',
            'data: {"choices":[{"finish_reason":"stop"}]}\n\n',
            'data: [DONE]\n\n'
        ]
        
        async def mock_aiter_lines():
            for chunk in stream_chunks:
                for line in chunk.strip().split('\n'):
                    if line:
                        yield line
        
        groq = create_groq(api_key="test-key")
        model = groq.language_model("llama-3.1-8b-instant")
        
        with patch.object(model, 'client') as mock_client:
            mock_response = AsyncMock()
            mock_response.aiter_lines = mock_aiter_lines
            mock_response.raise_for_status = MagicMock()
            
            mock_stream_context = AsyncMock()
            mock_stream_context.__aenter__.return_value = mock_response
            mock_client.stream.return_value = mock_stream_context
            
            text_parts = []
            async for chunk in stream_text(
                model=model,
                prompt="Test stream integration"
            ):
                if chunk.text_delta:
                    text_parts.append(chunk.text_delta)
            
            assert "".join(text_parts) == "Stream test"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])