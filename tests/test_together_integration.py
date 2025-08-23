#!/usr/bin/env python3
"""Integration tests for Together AI provider.

These tests verify the Together AI provider's functionality including:
- Text generation and streaming
- Embedding generation
- Error handling
- API parameter handling
- Response processing
- Usage tracking

Tests use mocked HTTP responses to avoid requiring real API keys during CI/CD.
"""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from ai_sdk.providers.together import TogetherAIProvider, TogetherAIChatLanguageModel, TogetherAIEmbeddingModel, create_together
from ai_sdk.providers.types import Message, Usage, FinishReason
from ai_sdk.errors import APIError, InvalidArgumentError
from ai_sdk.core.generate_text import generate_text, stream_text
from ai_sdk.core.embed import embed


class TestTogetherAIProvider:
    """Test Together AI provider initialization and configuration."""
    
    def test_create_together_with_api_key(self):
        """Test creating Together AI provider with explicit API key."""
        provider = create_together(api_key="test-key")
        assert isinstance(provider, TogetherAIProvider)
        assert provider.api_key == "test-key"
        assert provider.base_url == "https://api.together.xyz/v1"
    
    def test_create_together_with_custom_config(self):
        """Test creating Together AI provider with custom configuration."""
        provider = create_together(
            api_key="test-key",
            base_url="https://custom.together.xyz/v1", 
            max_retries=5,
            timeout=120.0,
            extra_headers={"Custom-Header": "value"}
        )
        
        assert provider.base_url == "https://custom.together.xyz/v1"
        assert provider.max_retries == 5
        assert provider.timeout == 120.0
        assert provider.extra_headers == {"Custom-Header": "value"}
    
    @patch.dict("os.environ", {"TOGETHER_API_KEY": "env-key"})
    def test_create_together_from_env_var(self):
        """Test creating Together AI provider from environment variable."""
        provider = create_together()
        assert provider.api_key == "env-key"
    
    @patch.dict("os.environ", {}, clear=True)
    def test_create_together_missing_api_key(self):
        """Test error when API key is missing."""
        with pytest.raises(InvalidArgumentError, match="Together AI API key is required"):
            create_together()
    
    def test_language_model_creation(self):
        """Test creating language models from provider."""
        provider = create_together(api_key="test-key")
        model = provider.language_model("meta-llama/Llama-3.1-8B-Instruct-Turbo")
        
        assert isinstance(model, TogetherAIChatLanguageModel)
        assert model.model_id == "meta-llama/Llama-3.1-8B-Instruct-Turbo"
        assert model.api_key == "test-key"
    
    def test_embedding_model_creation(self):
        """Test creating embedding models from provider."""
        provider = create_together(api_key="test-key")
        model = provider.embedding_model("BAAI/bge-large-en-v1.5")
        
        assert isinstance(model, TogetherAIEmbeddingModel)
        assert model.model_id == "BAAI/bge-large-en-v1.5"
        assert model.api_key == "test-key"


class TestTogetherAIChatLanguageModel:
    """Test Together AI chat language model functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.model = TogetherAIChatLanguageModel(
            model_id="meta-llama/Llama-3.1-8B-Instruct-Turbo",
            api_key="test-api-key"
        )
    
    def test_model_initialization(self):
        """Test model initialization with various parameters."""
        model = TogetherAIChatLanguageModel(
            model_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
            api_key="test-key",
            base_url="https://custom.together.xyz/v1",
            max_retries=3,
            timeout=90.0,
            extra_headers={"X-Custom": "header"}
        )
        
        assert model.model_id == "mistralai/Mixtral-8x7B-Instruct-v0.1"
        assert model.api_key == "test-key"
        assert model.base_url == "https://custom.together.xyz/v1"
        assert model.max_retries == 3
        assert model.timeout == 90.0
        assert model.extra_headers == {"X-Custom": "header"}
    
    def test_headers_generation(self):
        """Test HTTP headers generation."""
        headers = self.model._get_headers()
        
        assert headers["Authorization"] == "Bearer test-api-key"
        assert headers["Content-Type"] == "application/json"
    
    def test_message_conversion_text_only(self):
        """Test converting simple text messages to Together AI format."""
        messages = [
            Message(role="system", content="You are helpful."),
            Message(role="user", content="Hello!"),
            Message(role="assistant", content="Hi there!")
        ]
        
        together_messages = self.model._convert_messages_to_together_format(messages)
        
        expected = [
            {"role": "system", "content": "You are helpful."},
            {"role": "user", "content": "Hello!"},
            {"role": "assistant", "content": "Hi there!"}
        ]
        
        assert together_messages == expected
    
    def test_finish_reason_mapping(self):
        """Test mapping of finish reasons from Together AI to AI SDK format."""
        test_cases = [
            ("stop", FinishReason.STOP),
            ("length", FinishReason.LENGTH), 
            ("function_call", FinishReason.TOOL_CALLS),
            ("tool_calls", FinishReason.TOOL_CALLS),
            ("content_filter", FinishReason.CONTENT_FILTER),
            ("unknown", FinishReason.OTHER),
            (None, None)
        ]
        
        for together_reason, expected in test_cases:
            result = self.model._map_finish_reason(together_reason)
            assert result == expected


class TestTogetherAITextGeneration:
    """Test text generation functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.provider = create_together(api_key="test-key")
        self.model = self.provider.language_model("meta-llama/Llama-3.1-8B-Instruct-Turbo")
    
    @pytest.mark.asyncio
    async def test_successful_text_generation(self):
        """Test successful text generation with mocked response."""
        
        # Mock successful API response
        mock_response_data = {
            "id": "cmpl-test",
            "object": "chat.completion",
            "model": "meta-llama/Llama-3.1-8B-Instruct-Turbo",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": "Open-source models democratize AI access and foster innovation."
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 15,
                "completion_tokens": 12,
                "total_tokens": 27
            }
        }
        
        with patch.object(self.model, 'client') as mock_client:
            mock_response = AsyncMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = MagicMock()
            mock_client.post.return_value = mock_response
            
            messages = [Message(role="user", content="What are the benefits of open-source AI?")]
            result = await self.model.do_generate(
                messages=messages,
                max_tokens=100,
                temperature=0.7
            )
            
            assert result.text == "Open-source models democratize AI access and foster innovation."
            assert result.finish_reason == FinishReason.STOP
            assert result.usage.prompt_tokens == 15
            assert result.usage.completion_tokens == 12
            assert result.usage.total_tokens == 27
            assert len(result.response_messages) == 1
            assert result.response_messages[0].content == "Open-source models democratize AI access and foster innovation."
    
    @pytest.mark.asyncio
    async def test_text_generation_with_together_parameters(self):
        """Test text generation with Together AI-specific parameters."""
        
        mock_response_data = {
            "choices": [{
                "message": {"content": "Test response"},
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 8, "completion_tokens": 5, "total_tokens": 13}
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
                top_k=40,
                frequency_penalty=0.5,
                presence_penalty=0.3,
                stop_sequences=["END"],
                seed=42,
                repetition_penalty=1.1,
                safety_model="meta-llama/Llama-Guard-3-8B"
            )
            
            # Verify the request was made with correct parameters
            call_args = mock_client.post.call_args
            request_data = call_args.kwargs['json']
            
            assert request_data['model'] == 'meta-llama/Llama-3.1-8B-Instruct-Turbo'
            assert request_data['max_tokens'] == 100
            assert request_data['temperature'] == 0.8
            assert request_data['top_p'] == 0.9
            assert request_data['top_k'] == 40
            assert request_data['frequency_penalty'] == 0.5
            assert request_data['presence_penalty'] == 0.3
            assert request_data['stop'] == ["END"]
            assert request_data['seed'] == 42
            assert request_data['repetition_penalty'] == 1.1
            assert request_data['safety_model'] == "meta-llama/Llama-Guard-3-8B"
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """Test API error handling."""
        
        # Mock error response
        error_response_data = {
            "error": {
                "message": "Unable to access model",
                "type": "invalid_request_error"
            }
        }
        
        with patch.object(self.model, 'client') as mock_client:
            mock_response = AsyncMock()
            mock_response.json.return_value = error_response_data
            mock_response.status_code = 400
            mock_response.raise_for_status = MagicMock()
            mock_client.post.return_value = mock_response
            
            messages = [Message(role="user", content="Test")]
            
            with pytest.raises(APIError, match="Together AI API error: Unable to access model"):
                await self.model.do_generate(messages=messages)


class TestTogetherAIStreaming:
    """Test streaming functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.provider = create_together(api_key="test-key")
        self.model = self.provider.language_model("meta-llama/Llama-3.1-70B-Instruct-Turbo")
    
    @pytest.mark.asyncio
    async def test_successful_streaming(self):
        """Test successful streaming with mocked responses."""
        
        # Mock streaming response chunks
        stream_chunks = [
            'data: {"choices":[{"delta":{"content":"Open-source"}}]}\n\n',
            'data: {"choices":[{"delta":{"content":" AI"}}]}\n\n',
            'data: {"choices":[{"delta":{"content":" democratizes"}}]}\n\n',
            'data: {"choices":[{"finish_reason":"stop"}],"usage":{"prompt_tokens":10,"completion_tokens":6,"total_tokens":16}}\n\n',
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
            
            messages = [Message(role="user", content="Explain open-source AI")]
            chunks = []
            
            async for chunk in self.model.do_stream(messages=messages):
                chunks.append(chunk)
            
            # Verify we got the expected chunks
            text_chunks = [c for c in chunks if c.text_delta]
            assert len(text_chunks) == 3
            assert text_chunks[0].text_delta == "Open-source"
            assert text_chunks[1].text_delta == " AI"
            assert text_chunks[2].text_delta == " democratizes"
            
            # Check finish reason
            finish_chunks = [c for c in chunks if c.finish_reason]
            assert len(finish_chunks) == 1
            assert finish_chunks[0].finish_reason == FinishReason.STOP
    
    @pytest.mark.asyncio
    async def test_streaming_with_together_parameters(self):
        """Test streaming with Together AI-specific parameters."""
        
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
                top_k=30,
                stop_sequences=["END"],
                repetition_penalty=1.05
            ):
                chunks.append(chunk)
            
            # Verify the request parameters
            call_args = mock_client.stream.call_args
            request_data = call_args.kwargs['json']
            
            assert request_data['stream'] is True
            assert request_data['max_tokens'] == 50
            assert request_data['temperature'] == 0.5
            assert request_data['top_k'] == 30
            assert request_data['stop'] == ["END"]
            assert request_data['repetition_penalty'] == 1.05


class TestTogetherAIEmbeddingModel:
    """Test Together AI embedding model functionality."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.model = TogetherAIEmbeddingModel(
            model_id="BAAI/bge-large-en-v1.5",
            api_key="test-api-key"
        )
    
    def test_embedding_model_initialization(self):
        """Test embedding model initialization."""
        model = TogetherAIEmbeddingModel(
            model_id="togethercomputer/m2-bert-80M-8k-retrieval",
            api_key="test-key",
            base_url="https://custom.together.xyz/v1",
            max_retries=3,
            timeout=90.0,
            max_parallel=8,
            max_batch_size=50
        )
        
        assert model.model_id == "togethercomputer/m2-bert-80M-8k-retrieval"
        assert model.api_key == "test-key"
        assert model.base_url == "https://custom.together.xyz/v1"
        assert model.max_parallel == 8
        assert model.max_batch_size == 50
    
    @pytest.mark.asyncio
    async def test_successful_embedding_generation(self):
        """Test successful embedding generation with mocked response."""
        
        # Mock successful API response
        mock_response_data = {
            "object": "list",
            "data": [
                {
                    "object": "embedding",
                    "index": 0,
                    "embedding": [0.1, 0.2, 0.3, -0.1, -0.2]
                },
                {
                    "object": "embedding", 
                    "index": 1,
                    "embedding": [0.4, 0.5, 0.6, -0.3, -0.4]
                }
            ],
            "usage": {
                "prompt_tokens": 12,
                "total_tokens": 12
            }
        }
        
        with patch.object(self.model, 'client') as mock_client:
            mock_response = AsyncMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = MagicMock()
            mock_client.post.return_value = mock_response
            
            embeddings = await self.model.do_embed([
                "Together AI hosts open-source models",
                "Cost-effective inference for developers"
            ])
            
            assert len(embeddings) == 2
            assert embeddings[0] == [0.1, 0.2, 0.3, -0.1, -0.2]
            assert embeddings[1] == [0.4, 0.5, 0.6, -0.3, -0.4]
    
    @pytest.mark.asyncio
    async def test_single_text_embedding(self):
        """Test embedding generation for single text."""
        
        mock_response_data = {
            "data": [{
                "embedding": [0.1, 0.2, 0.3, -0.1, -0.2]
            }],
            "usage": {"prompt_tokens": 5, "total_tokens": 5}
        }
        
        with patch.object(self.model, 'client') as mock_client:
            mock_response = AsyncMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = MagicMock()
            mock_client.post.return_value = mock_response
            
            embeddings = await self.model.do_embed("Single text to embed")
            
            assert len(embeddings) == 1
            assert embeddings[0] == [0.1, 0.2, 0.3, -0.1, -0.2]
    
    @pytest.mark.asyncio
    async def test_embedding_error_handling(self):
        """Test embedding error handling."""
        
        # Mock error response
        error_response_data = {
            "error": {
                "message": "Invalid embedding model",
                "type": "invalid_request_error"
            }
        }
        
        with patch.object(self.model, 'client') as mock_client:
            mock_response = AsyncMock()
            mock_response.json.return_value = error_response_data
            mock_response.status_code = 400
            mock_response.raise_for_status = MagicMock()
            mock_client.post.return_value = mock_response
            
            with pytest.raises(APIError, match="Together AI API error: Invalid embedding model"):
                await self.model.do_embed("Test text")


class TestTogetherAIIntegration:
    """Integration tests using the high-level API functions."""
    
    @pytest.mark.asyncio
    async def test_generate_text_integration(self):
        """Test generate_text integration with Together AI provider."""
        
        mock_response_data = {
            "choices": [{
                "message": {"content": "Together AI integration test response"},
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 12, "completion_tokens": 6, "total_tokens": 18}
        }
        
        together = create_together(api_key="test-key")
        model = together.language_model("meta-llama/Llama-3.1-8B-Instruct-Turbo")
        
        with patch.object(model, 'client') as mock_client:
            mock_response = AsyncMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = MagicMock()
            mock_client.post.return_value = mock_response
            
            result = await generate_text(
                model=model,
                prompt="Test Together AI integration",
                max_tokens=100
            )
            
            assert result.text == "Together AI integration test response"
            assert result.finish_reason == FinishReason.STOP
            assert result.usage.total_tokens == 18
    
    @pytest.mark.asyncio
    async def test_stream_text_integration(self):
        """Test stream_text integration with Together AI provider."""
        
        stream_chunks = [
            'data: {"choices":[{"delta":{"content":"Stream"}}]}\n\n',
            'data: {"choices":[{"delta":{"content":" integration"}}]}\n\n',
            'data: {"choices":[{"finish_reason":"stop"}]}\n\n',
            'data: [DONE]\n\n'
        ]
        
        async def mock_aiter_lines():
            for chunk in stream_chunks:
                for line in chunk.strip().split('\n'):
                    if line:
                        yield line
        
        together = create_together(api_key="test-key")
        model = together.language_model("meta-llama/Llama-3.1-8B-Instruct-Turbo")
        
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
                prompt="Test Together AI stream integration"
            ):
                if chunk.text_delta:
                    text_parts.append(chunk.text_delta)
            
            assert "".join(text_parts) == "Stream integration"
    
    @pytest.mark.asyncio
    async def test_embed_integration(self):
        """Test embed integration with Together AI provider."""
        
        mock_response_data = {
            "data": [{
                "embedding": [0.1, 0.2, 0.3, -0.1, -0.2, 0.0]
            }],
            "usage": {"prompt_tokens": 6, "total_tokens": 6}
        }
        
        together = create_together(api_key="test-key")
        embedding_model = together.embedding_model("BAAI/bge-large-en-v1.5")
        
        with patch.object(embedding_model, 'client') as mock_client:
            mock_response = AsyncMock()
            mock_response.json.return_value = mock_response_data
            mock_response.raise_for_status = MagicMock()
            mock_client.post.return_value = mock_response
            
            result = await embed(
                model=embedding_model,
                value="Test Together AI embedding integration"
            )
            
            assert result.embedding == [0.1, 0.2, 0.3, -0.1, -0.2, 0.0]
            assert result.usage.total_tokens == 6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])