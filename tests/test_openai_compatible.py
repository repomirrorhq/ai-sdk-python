"""
Tests for OpenAI-Compatible Provider

This test suite covers:
- Provider initialization and configuration
- Language model creation (chat and completion)
- Embedding model functionality
- Image model creation
- Authentication and headers handling
- Error handling
- Integration with various OpenAI-compatible APIs
"""

import pytest
import asyncio
import os
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, Any

from ai_sdk.providers.openai_compatible import (
    OpenAICompatibleProvider,
    create_openai_compatible,
    OpenAICompatibleProviderSettings,
    OpenAICompatibleError,
)


class TestOpenAICompatibleProvider:
    """Test suite for OpenAI-Compatible Provider"""
    
    def test_provider_initialization(self):
        """Test basic provider initialization"""
        settings = OpenAICompatibleProviderSettings(
            name="test-provider",
            base_url="http://localhost:8080/v1"
        )
        provider = OpenAICompatibleProvider(settings)
        assert provider.name == "test-provider"
        assert provider.settings.base_url == "http://localhost:8080/v1"
        
    def test_provider_with_authentication(self):
        """Test provider with API key authentication"""
        settings = OpenAICompatibleProviderSettings(
            name="auth-provider",
            base_url="https://api.example.com/v1",
            api_key="test-key-123",
            headers={"X-Custom": "header"},
            query_params={"version": "v1"}
        )
        
        provider = OpenAICompatibleProvider(settings)
        assert provider.settings.api_key == "test-key-123"
        assert provider.settings.headers == {"X-Custom": "header"}
        assert provider.settings.query_params == {"version": "v1"}
        
    def test_create_openai_compatible(self):
        """Test factory function"""
        settings = OpenAICompatibleProviderSettings(
            name="factory-test",
            base_url="http://localhost:9000/v1"
        )
        provider = create_openai_compatible(settings)
        assert isinstance(provider, OpenAICompatibleProvider)
        assert provider.name == "factory-test"


class TestOpenAICompatibleLanguageModels:
    """Test suite for OpenAI-Compatible Language Models"""
    
    @pytest.fixture
    def mock_provider(self):
        """Create a mock provider for testing"""
        settings = OpenAICompatibleProviderSettings(
            name="test-provider",
            base_url="http://localhost:8080/v1",
            api_key="test-key"
        )
        return OpenAICompatibleProvider(settings)
    
    def test_chat_model_creation(self, mock_provider):
        """Test chat model creation"""
        model = mock_provider.chat_model("llama3.2")
        assert model.model_id == "llama3.2"
        assert model.provider == "test-provider.chat"
        
    def test_language_model_creation(self, mock_provider):
        """Test language model creation (alias for chat)"""
        model = mock_provider.language_model("gpt-3.5-turbo")
        assert model.model_id == "gpt-3.5-turbo"
        assert model.provider == "test-provider.chat"
        
    def test_callable_interface(self, mock_provider):
        """Test provider callable interface"""
        model = mock_provider("claude-3-sonnet")
        assert model.model_id == "claude-3-sonnet"
        assert model.provider == "test-provider.chat"
    
    def test_completion_model_creation(self, mock_provider):
        """Test completion model creation"""
        model = mock_provider.completion_model("text-davinci-003")
        assert model.model_id == "text-davinci-003"
        assert model.provider == "test-provider.completion"
    
    @patch('aiohttp.ClientSession.post')
    async def test_generate_text(self, mock_post, mock_provider):
        """Test text generation"""
        # Mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "choices": [{
                "message": {
                    "content": "OpenAI-compatible APIs provide great flexibility for developers."
                },
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 15, "completion_tokens": 12, "total_tokens": 27}
        })
        mock_response.headers = {}
        
        mock_post.return_value.__aenter__.return_value = mock_response
        
        model = mock_provider.chat_model("llama3.2")
        result = await model.generate_text("What are OpenAI-compatible APIs?")
        
        assert result.text == "OpenAI-compatible APIs provide great flexibility for developers."
        assert result.finish_reason == "stop"
        assert result.usage["prompt_tokens"] == 15
    
    @patch('aiohttp.ClientSession.post')
    async def test_stream_text(self, mock_post, mock_provider):
        """Test streaming text generation"""
        # Mock SSE response
        mock_response = MagicMock()
        mock_response.status = 200
        
        # Mock async iterator for SSE
        async def mock_content():
            yield b'data: {"choices": [{"delta": {"content": "Local "}}]}\n'
            yield b'data: {"choices": [{"delta": {"content": "models "}}]}\n'
            yield b'data: {"choices": [{"delta": {"content": "are great!"}}]}\n'
            yield b'data: [DONE]\n'
        
        mock_response.content = mock_content()
        mock_post.return_value.__aenter__.return_value = mock_response
        
        model = mock_provider.chat_model("llama3.2")
        chunks = []
        async for chunk in model.stream_text("Tell me about local models"):
            chunks.append(chunk)
        
        # Verify we got the expected chunks
        assert len(chunks) == 3
        text_chunks = [chunk.text_delta for chunk in chunks if hasattr(chunk, 'text_delta')]
        assert text_chunks == ["Local ", "models ", "are great!"]


class TestOpenAICompatibleEmbeddingModel:
    """Test suite for OpenAI-Compatible Embedding Model"""
    
    @pytest.fixture
    def mock_provider(self):
        """Create a mock provider for testing"""
        settings = OpenAICompatibleProviderSettings(
            name="embedding-provider",
            base_url="http://localhost:8080/v1",
            api_key="test-key"
        )
        return OpenAICompatibleProvider(settings)
    
    def test_embedding_model_creation(self, mock_provider):
        """Test embedding model creation"""
        model = mock_provider.text_embedding_model("text-embedding-ada-002")
        assert model.model_id == "text-embedding-ada-002"
        assert model.provider == "embedding-provider.embedding"
    
    @patch('aiohttp.ClientSession.post')
    async def test_embed_single_text(self, mock_post, mock_provider):
        """Test single text embedding"""
        # Mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "data": [
                {"embedding": [0.1, 0.2, 0.3, 0.4]}
            ],
            "usage": {"prompt_tokens": 6, "total_tokens": 6}
        })
        mock_response.headers = {}
        
        mock_post.return_value.__aenter__.return_value = mock_response
        
        model = mock_provider.text_embedding_model("nomic-embed-text")
        result = await model.embed("Hello world")
        
        assert len(result.embeddings) == 1
        assert result.embeddings[0] == [0.1, 0.2, 0.3, 0.4]
        assert result.usage["prompt_tokens"] == 6
    
    @patch('aiohttp.ClientSession.post')
    async def test_embed_multiple_texts(self, mock_post, mock_provider):
        """Test multiple text embeddings"""
        # Mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "data": [
                {"embedding": [0.1, 0.2]},
                {"embedding": [0.3, 0.4]},
                {"embedding": [0.5, 0.6]}
            ],
            "usage": {"prompt_tokens": 18, "total_tokens": 18}
        })
        mock_response.headers = {}
        
        mock_post.return_value.__aenter__.return_value = mock_response
        
        model = mock_provider.text_embedding_model("sentence-transformers")
        result = await model.embed([
            "First text",
            "Second text", 
            "Third text"
        ])
        
        assert len(result.embeddings) == 3
        assert result.embeddings[0] == [0.1, 0.2]
        assert result.embeddings[1] == [0.3, 0.4]
        assert result.embeddings[2] == [0.5, 0.6]
        assert result.usage["prompt_tokens"] == 18


class TestOpenAICompatibleImageModel:
    """Test suite for OpenAI-Compatible Image Model"""
    
    @pytest.fixture
    def mock_provider(self):
        """Create a mock provider for testing"""
        settings = OpenAICompatibleProviderSettings(
            name="image-provider",
            base_url="http://localhost:8080/v1",
            api_key="test-key"
        )
        return OpenAICompatibleProvider(settings)
    
    def test_image_model_creation(self, mock_provider):
        """Test image model creation"""
        model = mock_provider.image_model("dall-e-3")
        assert model.model_id == "dall-e-3"
        assert model.provider == "image-provider.image"
    
    @patch('aiohttp.ClientSession.post')
    async def test_generate_image(self, mock_post, mock_provider):
        """Test image generation"""
        # Mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "data": [
                {
                    "url": "https://example.com/generated-image.png",
                    "b64_json": None
                }
            ]
        })
        mock_response.headers = {}
        
        mock_post.return_value.__aenter__.return_value = mock_response
        
        model = mock_provider.image_model("stable-diffusion")
        result = await model.generate_image("A beautiful sunset over mountains")
        
        assert len(result.images) == 1
        assert result.images[0].url == "https://example.com/generated-image.png"


class TestOpenAICompatibleProviderConfiguration:
    """Test suite for Provider Configuration"""
    
    def test_ollama_configuration(self):
        """Test Ollama-specific configuration"""
        settings = OpenAICompatibleProviderSettings(
            name="ollama",
            base_url="http://localhost:11434/v1",
            # Ollama typically doesn't need API key for local use
        )
        
        provider = create_openai_compatible(settings)
        assert provider.name == "ollama"
        assert provider.settings.api_key is None
        
        # Test headers without API key
        headers = provider._get_headers()
        assert "Authorization" not in headers
    
    def test_lmstudio_configuration(self):
        """Test LMStudio-specific configuration"""
        settings = OpenAICompatibleProviderSettings(
            name="lmstudio",
            base_url="http://localhost:1234/v1",
            headers={"User-Agent": "AI-SDK-Python/1.0"}
        )
        
        provider = create_openai_compatible(settings)
        headers = provider._get_headers()
        assert headers["User-Agent"] == "AI-SDK-Python/1.0"
        assert "Authorization" not in headers
    
    def test_vllm_configuration(self):
        """Test vLLM-specific configuration"""
        settings = OpenAICompatibleProviderSettings(
            name="vllm",
            base_url="http://localhost:8000/v1",
            include_usage=True
        )
        
        provider = create_openai_compatible(settings)
        assert provider.settings.include_usage is True
    
    def test_custom_api_configuration(self):
        """Test custom API configuration"""
        settings = OpenAICompatibleProviderSettings(
            name="custom-api",
            base_url="https://api.custom-service.com/v1",
            api_key="sk-custom-key-123",
            headers={
                "X-Custom-Header": "custom-value",
                "X-API-Version": "2024-01"
            },
            query_params={
                "model_version": "latest",
                "temperature": "0.7"
            }
        )
        
        provider = create_openai_compatible(settings)
        
        # Test authentication headers
        headers = provider._get_headers()
        assert headers["Authorization"] == "Bearer sk-custom-key-123"
        assert headers["X-Custom-Header"] == "custom-value"
        assert headers["X-API-Version"] == "2024-01"
        
        # Test base URL processing
        assert provider._get_base_url() == "https://api.custom-service.com/v1"


class TestOpenAICompatibleErrorHandling:
    """Test suite for Error Handling"""
    
    @pytest.fixture
    def mock_provider(self):
        """Create a mock provider for testing"""
        settings = OpenAICompatibleProviderSettings(
            name="error-test",
            base_url="http://localhost:8080/v1",
            api_key="test-key"
        )
        return OpenAICompatibleProvider(settings)
    
    @patch('aiohttp.ClientSession.post')
    async def test_authentication_error(self, mock_post, mock_provider):
        """Test authentication error handling"""
        # Mock 401 response
        mock_response = MagicMock()
        mock_response.status = 401
        mock_response.json = AsyncMock(return_value={
            "error": {
                "message": "Invalid API key",
                "type": "authentication_error"
            }
        })
        
        mock_post.return_value.__aenter__.return_value = mock_response
        
        model = mock_provider.chat_model("test-model")
        
        with pytest.raises(Exception) as exc_info:
            await model.generate_text("Test prompt")
        
        assert "401" in str(exc_info.value)
    
    @patch('aiohttp.ClientSession.post')
    async def test_model_not_found_error(self, mock_post, mock_provider):
        """Test model not found error handling"""
        # Mock 404 response
        mock_response = MagicMock()
        mock_response.status = 404
        mock_response.json = AsyncMock(return_value={
            "error": {
                "message": "Model not found",
                "type": "invalid_request_error"
            }
        })
        
        mock_post.return_value.__aenter__.return_value = mock_response
        
        model = mock_provider.chat_model("nonexistent-model")
        
        with pytest.raises(Exception) as exc_info:
            await model.generate_text("Test prompt")
        
        assert "404" in str(exc_info.value)
    
    @patch('aiohttp.ClientSession.post')
    async def test_rate_limit_error(self, mock_post, mock_provider):
        """Test rate limit error handling"""
        # Mock 429 response
        mock_response = MagicMock()
        mock_response.status = 429
        mock_response.json = AsyncMock(return_value={
            "error": {
                "message": "Rate limit exceeded",
                "type": "rate_limit_error"
            }
        })
        mock_response.headers = {"Retry-After": "60"}
        
        mock_post.return_value.__aenter__.return_value = mock_response
        
        model = mock_provider.chat_model("test-model")
        
        with pytest.raises(Exception) as exc_info:
            await model.generate_text("Test prompt")
        
        assert "429" in str(exc_info.value)
    
    @patch('aiohttp.ClientSession.post')
    async def test_server_error(self, mock_post, mock_provider):
        """Test server error handling"""
        # Mock 500 response
        mock_response = MagicMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal Server Error")
        
        mock_post.return_value.__aenter__.return_value = mock_response
        
        model = mock_provider.chat_model("test-model")
        
        with pytest.raises(Exception) as exc_info:
            await model.generate_text("Test prompt")
        
        assert "500" in str(exc_info.value)


class TestOpenAICompatibleRealWorldScenarios:
    """Test suite for Real World Usage Scenarios"""
    
    def test_ollama_llama_setup(self):
        """Test typical Ollama + Llama setup"""
        ollama = create_openai_compatible(
            OpenAICompatibleProviderSettings(
                name="ollama",
                base_url="http://localhost:11434/v1"
            )
        )
        
        llama_model = ollama.chat_model("llama3.2")
        assert llama_model.model_id == "llama3.2"
        assert llama_model.provider == "ollama.chat"
        
        # Test embedding model
        embed_model = ollama.text_embedding_model("nomic-embed-text")
        assert embed_model.model_id == "nomic-embed-text"
    
    def test_lmstudio_setup(self):
        """Test typical LMStudio setup"""
        lmstudio = create_openai_compatible(
            OpenAICompatibleProviderSettings(
                name="lmstudio",
                base_url="http://localhost:1234/v1"
            )
        )
        
        model = lmstudio.chat_model("local-model")
        assert model.model_id == "local-model"
        assert model.provider == "lmstudio.chat"
    
    def test_vllm_multi_model_setup(self):
        """Test vLLM with multiple models"""
        vllm = create_openai_compatible(
            OpenAICompatibleProviderSettings(
                name="vllm",
                base_url="http://localhost:8000/v1",
                include_usage=True
            )
        )
        
        # Test different model types
        chat_model = vllm.chat_model("meta-llama/Llama-2-7b-chat-hf")
        completion_model = vllm.completion_model("meta-llama/Llama-2-7b-hf")
        
        assert chat_model.provider == "vllm.chat"
        assert completion_model.provider == "vllm.completion"
    
    def test_custom_hosted_service(self):
        """Test custom hosted OpenAI-compatible service"""
        custom = create_openai_compatible(
            OpenAICompatibleProviderSettings(
                name="custom-hosted",
                base_url="https://my-api.example.com/v1",
                api_key="sk-custom-123",
                headers={
                    "X-Client": "AI-SDK-Python",
                    "X-Version": "1.0"
                },
                query_params={
                    "timeout": "30"
                }
            )
        )
        
        model = custom.chat_model("gpt-4-compatible")
        assert model.model_id == "gpt-4-compatible"
        
        # Verify configuration
        headers = custom._get_headers()
        assert headers["Authorization"] == "Bearer sk-custom-123"
        assert headers["X-Client"] == "AI-SDK-Python"
        assert headers["X-Version"] == "1.0"


if __name__ == "__main__":
    pytest.main([__file__])