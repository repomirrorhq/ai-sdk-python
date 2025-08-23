"""Integration tests for Azure OpenAI provider."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from ai_sdk import generate_text, stream_text, embed
from ai_sdk.providers.azure import AzureOpenAIProvider, create_azure
from ai_sdk.providers.types import TextDelta, FinishEvent, FinishReason


class TestAzureOpenAIProvider:
    """Test Azure OpenAI provider functionality."""
    
    def test_create_provider_with_resource_name(self):
        """Test creating provider with resource name."""
        provider = create_azure(
            resource_name="test-resource",
            api_key="test-key",
        )
        
        assert provider.name == "azure"
        assert provider.resource_name == "test-resource"
        assert provider.api_key == "test-key"
        assert provider.api_version == "2024-08-01-preview"
        assert provider.base_url == "https://test-resource.openai.azure.com/openai"
    
    def test_create_provider_with_base_url(self):
        """Test creating provider with custom base URL."""
        provider = create_azure(
            base_url="https://custom.example.com/openai",
            api_key="test-key",
        )
        
        assert provider.base_url == "https://custom.example.com/openai"
        assert provider.resource_name is None
    
    def test_create_provider_missing_credentials(self):
        """Test creating provider without credentials raises error."""
        with pytest.raises(ValueError, match="Azure API key not found"):
            create_azure()
    
    def test_create_provider_missing_resource_info(self):
        """Test creating provider without resource name or base URL."""
        with pytest.raises(ValueError, match="Azure resource name or base URL not found"):
            create_azure(api_key="test-key")
    
    def test_url_generation_standard_format(self):
        """Test URL generation with standard v1 format."""
        provider = create_azure(
            resource_name="test-resource",
            api_key="test-key",
            use_deployment_based_urls=False,
        )
        
        url = provider._get_model_url("gpt-35-turbo", "/chat/completions")
        expected = "https://test-resource.openai.azure.com/openai/v1/chat/completions?api-version=2024-08-01-preview"
        assert url == expected
    
    def test_url_generation_deployment_based_format(self):
        """Test URL generation with deployment-based format."""
        provider = create_azure(
            resource_name="test-resource", 
            api_key="test-key",
            use_deployment_based_urls=True,
        )
        
        url = provider._get_model_url("gpt-35-turbo", "/chat/completions")
        expected = "https://test-resource.openai.azure.com/openai/deployments/gpt-35-turbo/chat/completions?api-version=2024-08-01-preview"
        assert url == expected
    
    def test_custom_api_version(self):
        """Test using custom API version."""
        provider = create_azure(
            resource_name="test-resource",
            api_key="test-key",
            api_version="2023-12-01-preview",
        )
        
        url = provider._get_model_url("gpt-35-turbo", "/chat/completions")
        assert "api-version=2023-12-01-preview" in url
    
    def test_language_model_creation(self):
        """Test creating language model."""
        provider = create_azure(
            resource_name="test-resource",
            api_key="test-key",
        )
        
        model = provider.language_model("gpt-35-turbo")
        assert model.deployment_id == "gpt-35-turbo"
        assert model.provider == provider
    
    def test_chat_model_alias(self):
        """Test chat() alias for language_model()."""
        provider = create_azure(
            resource_name="test-resource",
            api_key="test-key",
        )
        
        model = provider.chat("gpt-35-turbo")
        assert model.deployment_id == "gpt-35-turbo"
    
    def test_embedding_model_creation(self):
        """Test creating embedding model."""
        provider = create_azure(
            resource_name="test-resource",
            api_key="test-key",
        )
        
        model = provider.embedding_model("text-embedding-ada-002")
        assert model.deployment_id == "text-embedding-ada-002"
        assert model.provider == provider
    
    def test_embedding_aliases(self):
        """Test embedding model aliases."""
        provider = create_azure(
            resource_name="test-resource",
            api_key="test-key",
        )
        
        model1 = provider.embedding("text-embedding-ada-002")
        model2 = provider.text_embedding("text-embedding-ada-002")
        
        assert model1.deployment_id == "text-embedding-ada-002"
        assert model2.deployment_id == "text-embedding-ada-002"
    
    @pytest.mark.asyncio
    async def test_generate_text_success(self):
        """Test successful text generation."""
        # Mock response
        mock_response = {
            "choices": [{
                "message": {"content": "Hello, Azure!"},
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15
            },
            "model": "gpt-35-turbo"
        }
        
        with patch('ai_sdk.providers.azure.language_model.create_http_client') as mock_client:
            # Setup mock client
            mock_http_client = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.status_code = 200
            mock_response_obj.text = str(mock_response).replace("'", '"')
            mock_response_obj.headers = {}
            
            mock_http_client.__aenter__.return_value = mock_http_client
            mock_http_client.post.return_value = mock_response_obj
            mock_client.return_value = mock_http_client
            
            # Test generation
            provider = create_azure(
                resource_name="test-resource",
                api_key="test-key",
            )
            
            result = await generate_text(
                model=provider.chat("gpt-35-turbo"),
                prompt="Hello, Azure!",
            )
            
            assert result.text == "Hello, Azure!"
            assert result.usage.total_tokens == 15
            assert result.provider_metadata.provider_name == "azure"
    
    @pytest.mark.asyncio
    async def test_streaming_text_success(self):
        """Test successful streaming text generation."""
        # Mock streaming response chunks
        mock_chunks = [
            'data: {"choices":[{"delta":{"content":"Hello"}}]}\n\n',
            'data: {"choices":[{"delta":{"content":", Azure"}}]}\n\n',
            'data: {"choices":[{"delta":{"content":"!"}}]}\n\n',
            'data: {"choices":[{"finish_reason":"stop"}],"usage":{"total_tokens":10}}\n\n',
            'data: [DONE]\n\n'
        ]
        
        with patch('ai_sdk.providers.azure.language_model.create_http_client') as mock_client:
            # Setup mock streaming client
            mock_http_client = AsyncMock()
            mock_response_obj = AsyncMock()
            mock_response_obj.status_code = 200
            mock_response_obj.aiter_lines.return_value = iter(mock_chunks)
            
            mock_http_client.__aenter__.return_value = mock_http_client
            mock_http_client.stream.return_value.__aenter__.return_value = mock_response_obj
            mock_client.return_value = mock_http_client
            
            # Test streaming
            provider = create_azure(
                resource_name="test-resource", 
                api_key="test-key",
            )
            
            parts = []
            async for part in stream_text(
                model=provider.chat("gpt-35-turbo"),
                prompt="Hello!",
            ):
                parts.append(part)
            
            # Should have text deltas and finish event
            text_deltas = [p for p in parts if isinstance(p, TextDelta)]
            finish_events = [p for p in parts if isinstance(p, FinishEvent)]
            
            assert len(text_deltas) == 3
            assert text_deltas[0].text == "Hello"
            assert text_deltas[1].text == ", Azure"
            assert text_deltas[2].text == "!"
            
            assert len(finish_events) == 1
            assert finish_events[0].finish_reason == FinishReason.STOP
    
    @pytest.mark.asyncio
    async def test_embeddings_success(self):
        """Test successful embeddings generation."""
        # Mock embeddings response
        mock_response = {
            "data": [
                {"embedding": [0.1, 0.2, 0.3]},
                {"embedding": [0.4, 0.5, 0.6]}
            ],
            "usage": {
                "prompt_tokens": 10,
                "total_tokens": 10
            },
            "model": "text-embedding-ada-002"
        }
        
        with patch('ai_sdk.providers.azure.embedding_model.create_http_client') as mock_client:
            # Setup mock client
            mock_http_client = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.status_code = 200
            mock_response_obj.text = str(mock_response).replace("'", '"')
            mock_response_obj.headers = {}
            
            mock_http_client.__aenter__.return_value = mock_http_client
            mock_http_client.post.return_value = mock_response_obj
            mock_client.return_value = mock_http_client
            
            # Test embeddings
            provider = create_azure(
                resource_name="test-resource",
                api_key="test-key",
            )
            
            result = await embed(
                model=provider.embedding("text-embedding-ada-002"),
                values=["Hello", "World"],
            )
            
            assert len(result.embeddings) == 2
            assert result.embeddings[0] == [0.1, 0.2, 0.3]
            assert result.embeddings[1] == [0.4, 0.5, 0.6]
            assert result.usage.total_tokens == 10
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self):
        """Test API error handling."""
        with patch('ai_sdk.providers.azure.language_model.create_http_client') as mock_client:
            # Setup mock client to return error
            mock_http_client = AsyncMock()
            mock_response_obj = MagicMock()
            mock_response_obj.status_code = 401
            mock_response_obj.text = '{"error": {"message": "Unauthorized"}}'
            mock_response_obj.headers = {}
            
            mock_http_client.__aenter__.return_value = mock_http_client
            mock_http_client.post.return_value = mock_response_obj
            mock_client.return_value = mock_http_client
            
            # Test that error is raised
            provider = create_azure(
                resource_name="test-resource",
                api_key="test-key",
            )
            
            with pytest.raises(Exception):  # Should raise APIError
                await generate_text(
                    model=provider.chat("gpt-35-turbo"),
                    prompt="Test",
                )
    
    def test_environment_variable_loading(self):
        """Test loading credentials from environment variables.""" 
        with patch.dict('os.environ', {
            'AZURE_API_KEY': 'env-api-key',
            'AZURE_RESOURCE_NAME': 'env-resource'
        }):
            provider = create_azure()
            
            assert provider.api_key == 'env-api-key'
            assert provider.resource_name == 'env-resource'
            assert provider.base_url == 'https://env-resource.openai.azure.com/openai'