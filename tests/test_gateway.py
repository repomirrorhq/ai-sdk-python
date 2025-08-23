"""
Tests for Gateway Provider

This test suite covers:
- Gateway provider initialization
- Authentication handling  
- Language model generation
- Embedding model functionality
- Metadata fetching
- Error handling
"""

import pytest
import asyncio
import os
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, Any

from ai_sdk.providers.gateway import (
    GatewayProvider,
    create_gateway_provider,
    gateway,
    GatewayProviderSettings,
    GatewayFetchMetadataResponse,
    GatewayLanguageModelEntry,
    GatewayLanguageModelSpecification,
    GatewayError,
    GatewayAuthenticationError,
)


class TestGatewayProvider:
    """Test suite for Gateway Provider"""
    
    def test_provider_initialization(self):
        """Test basic provider initialization"""
        provider = GatewayProvider()
        assert provider.name == "gateway"
        assert provider.settings.base_url == "https://ai-gateway.vercel.sh/v1/ai"
        
    def test_provider_custom_settings(self):
        """Test provider with custom settings"""
        settings = GatewayProviderSettings(
            base_url="https://custom-gateway.example.com/v1/ai",
            api_key="test-key",
            headers={"custom": "header"},
            metadata_cache_refresh_millis=60000
        )
        
        provider = GatewayProvider(settings)
        assert provider.settings.base_url == "https://custom-gateway.example.com/v1/ai"
        assert provider.settings.api_key == "test-key"
        assert provider.settings.headers == {"custom": "header"}
        assert provider.settings.metadata_cache_refresh_millis == 60000
        
    def test_create_gateway_provider(self):
        """Test factory function"""
        provider = create_gateway_provider()
        assert isinstance(provider, GatewayProvider)
        
        custom_provider = create_gateway_provider(
            GatewayProviderSettings(api_key="test-key")
        )
        assert custom_provider.settings.api_key == "test-key"
        
    def test_default_gateway_instance(self):
        """Test default gateway instance"""
        assert isinstance(gateway, GatewayProvider)
        assert gateway.name == "gateway"


class TestGatewayLanguageModel:
    """Test suite for Gateway Language Model"""
    
    @pytest.fixture
    def mock_provider(self):
        """Create a mock provider for testing"""
        settings = GatewayProviderSettings(api_key="test-key")
        return GatewayProvider(settings)
    
    @pytest.fixture 
    def mock_language_model(self, mock_provider):
        """Create a mock language model"""
        return mock_provider.language_model("gpt-4-turbo")
    
    def test_language_model_creation(self, mock_provider):
        """Test language model creation"""
        model = mock_provider.language_model("gpt-4-turbo")
        assert model.model_id == "gpt-4-turbo"
        assert model.provider == "gateway"
        assert model.specification_version == "v2"
    
    def test_callable_interface(self, mock_provider):
        """Test provider callable interface"""
        model = mock_provider("claude-3-sonnet-20240229")
        assert model.model_id == "claude-3-sonnet-20240229"
        assert model.provider == "gateway"
    
    @patch('aiohttp.ClientSession.post')
    async def test_generate_text(self, mock_post, mock_language_model):
        """Test text generation"""
        # Mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "text": "AI Gateway provides model routing and load balancing.",
            "finishReason": "stop",
            "usage": {"promptTokens": 10, "completionTokens": 15},
            "responseMessages": []
        })
        mock_response.headers = {}
        
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Mock provider methods
        with patch.object(mock_language_model, '_prepare_args', return_value={"prompt": "test"}):
            with patch.object(mock_language_model.config, 'headers', return_value={"Authorization": "Bearer test"}):
                with patch.object(mock_language_model.config, 'o11y_headers', return_value={}):
                    
                    result = await mock_language_model.generate_text("What is AI Gateway?")
                    
                    assert result.text == "AI Gateway provides model routing and load balancing."
                    assert result.finish_reason == "stop"
                    assert result.usage["promptTokens"] == 10
    
    @patch('aiohttp.ClientSession.post')
    async def test_stream_text(self, mock_post, mock_language_model):
        """Test streaming text generation"""
        # Mock SSE response
        mock_response = MagicMock()
        mock_response.status = 200
        
        # Mock async iterator for SSE
        async def mock_content():
            yield b'data: {"type": "text-delta", "textDelta": "AI "}\n'
            yield b'data: {"type": "text-delta", "textDelta": "Gateway "}\n'
            yield b'data: {"type": "text-delta", "textDelta": "rocks!"}\n'
            yield b'data: [DONE]\n'
        
        mock_response.content = mock_content()
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Mock provider methods
        with patch.object(mock_language_model, '_prepare_args', return_value={"prompt": "test"}):
            with patch.object(mock_language_model.config, 'headers', return_value={"Authorization": "Bearer test"}):
                with patch.object(mock_language_model.config, 'o11y_headers', return_value={}):
                    
                    chunks = []
                    async for chunk in mock_language_model.stream_text("What is AI Gateway?"):
                        chunks.append(chunk)
                    
                    assert len(chunks) == 3
                    assert all(chunk.type == "text-delta" for chunk in chunks)
                    text_deltas = [chunk.textDelta for chunk in chunks]
                    assert text_deltas == ["AI ", "Gateway ", "rocks!"]


class TestGatewayEmbeddingModel:
    """Test suite for Gateway Embedding Model"""
    
    @pytest.fixture
    def mock_provider(self):
        """Create a mock provider for testing"""
        settings = GatewayProviderSettings(api_key="test-key")
        return GatewayProvider(settings)
    
    @pytest.fixture
    def mock_embedding_model(self, mock_provider):
        """Create a mock embedding model"""
        return mock_provider.text_embedding_model("text-embedding-ada-002")
    
    def test_embedding_model_creation(self, mock_provider):
        """Test embedding model creation"""
        model = mock_provider.text_embedding_model("text-embedding-ada-002")
        assert model.model_id == "text-embedding-ada-002"
        assert model.provider == "gateway"
    
    @patch('aiohttp.ClientSession.post')
    async def test_embed_single_text(self, mock_post, mock_embedding_model):
        """Test single text embedding"""
        # Mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "embeddings": [[0.1, 0.2, 0.3]],
            "usage": {"promptTokens": 5}
        })
        mock_response.headers = {}
        
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Mock provider methods
        with patch.object(mock_embedding_model.config, 'headers', return_value={"Authorization": "Bearer test"}):
            with patch.object(mock_embedding_model.config, 'o11y_headers', return_value={}):
                
                result = await mock_embedding_model.embed("Hello world")
                
                assert len(result.embeddings) == 1
                assert result.embeddings[0] == [0.1, 0.2, 0.3]
                assert result.usage["promptTokens"] == 5
    
    @patch('aiohttp.ClientSession.post')
    async def test_embed_multiple_texts(self, mock_post, mock_embedding_model):
        """Test multiple text embeddings"""
        # Mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "embeddings": [[0.1, 0.2], [0.3, 0.4]],
            "usage": {"promptTokens": 10}
        })
        mock_response.headers = {}
        
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Mock provider methods  
        with patch.object(mock_embedding_model.config, 'headers', return_value={"Authorization": "Bearer test"}):
            with patch.object(mock_embedding_model.config, 'o11y_headers', return_value={}):
                
                result = await mock_embedding_model.embed(["Hello", "World"])
                
                assert len(result.embeddings) == 2
                assert result.embeddings[0] == [0.1, 0.2]
                assert result.embeddings[1] == [0.3, 0.4]


class TestGatewayMetadata:
    """Test suite for Gateway Metadata Fetching"""
    
    @pytest.fixture
    def mock_provider(self):
        """Create a mock provider for testing"""
        settings = GatewayProviderSettings(api_key="test-key")
        return GatewayProvider(settings)
    
    @patch('aiohttp.ClientSession.get')
    async def test_get_available_models(self, mock_get, mock_provider):
        """Test fetching available models"""
        # Mock response
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.json = AsyncMock(return_value={
            "models": [
                {
                    "id": "gpt-4-turbo",
                    "name": "GPT-4 Turbo",
                    "description": "Advanced GPT-4 model",
                    "specification": {
                        "specificationVersion": "v2",
                        "provider": "openai",
                        "modelId": "gpt-4-turbo"
                    }
                },
                {
                    "id": "claude-3-sonnet-20240229", 
                    "name": "Claude 3 Sonnet",
                    "specification": {
                        "specificationVersion": "v2",
                        "provider": "anthropic",
                        "modelId": "claude-3-sonnet-20240229"
                    }
                }
            ]
        })
        
        mock_get.return_value.__aenter__.return_value = mock_response
        
        # Mock provider methods
        with patch.object(mock_provider, '_get_headers', return_value={"Authorization": "Bearer test"}):
            
            metadata = await mock_provider.get_available_models()
            
            assert len(metadata.models) == 2
            assert metadata.models[0].id == "gpt-4-turbo"
            assert metadata.models[0].name == "GPT-4 Turbo"
            assert metadata.models[0].description == "Advanced GPT-4 model"
            assert metadata.models[1].id == "claude-3-sonnet-20240229"


class TestGatewayAuthentication:
    """Test suite for Gateway Authentication"""
    
    def test_api_key_from_settings(self):
        """Test API key from settings"""
        provider = GatewayProvider(
            GatewayProviderSettings(api_key="test-key")
        )
        assert provider.settings.api_key == "test-key"
    
    @patch.dict(os.environ, {'AI_GATEWAY_API_KEY': 'env-key'})
    async def test_api_key_from_environment(self):
        """Test API key from environment variable"""
        provider = GatewayProvider()
        token = await provider._get_gateway_auth_token()
        
        assert token is not None
        assert token.token == "env-key"
        assert token.auth_method == "api-key"
    
    async def test_no_authentication(self):
        """Test behavior when no authentication is provided"""
        provider = GatewayProvider()
        token = await provider._get_gateway_auth_token()
        assert token is None
    
    async def test_authentication_error(self):
        """Test authentication error handling"""
        provider = GatewayProvider()
        
        with pytest.raises(GatewayAuthenticationError):
            await provider._get_headers()


class TestGatewayErrors:
    """Test suite for Gateway Error Handling"""
    
    def test_gateway_authentication_error_contextual(self):
        """Test contextual authentication error creation"""
        error = GatewayAuthenticationError.create_contextual_error(
            api_key_provided=False,
            oidc_token_provided=False
        )
        
        assert "AI Gateway authentication failed" in str(error)
        assert "AI_GATEWAY_API_KEY" in str(error)
    
    def test_gateway_error_conversion(self):
        """Test error conversion"""
        from ai_sdk.providers.gateway.errors import as_gateway_error
        
        # Test generic exception
        generic_error = Exception("Generic error")
        gateway_error = as_gateway_error(generic_error)
        assert isinstance(gateway_error, GatewayError)
        assert str(gateway_error) == "Generic error"
    
    def test_gateway_error_with_status_code(self):
        """Test error handling with status codes"""
        from ai_sdk.providers.gateway.errors import create_gateway_error_from_response
        
        # Test 401 error
        auth_error = create_gateway_error_from_response(401, "Unauthorized")
        assert isinstance(auth_error, GatewayAuthenticationError)
        
        # Test 404 error
        not_found_error = create_gateway_error_from_response(404, "Model not found")
        assert hasattr(not_found_error, 'status_code')
        assert not_found_error.status_code == 404


if __name__ == "__main__":
    pytest.main([__file__])