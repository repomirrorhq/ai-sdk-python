"""
Test cases for enhanced TogetherAI provider functionality.

Tests the custom image model implementation and improved API handling.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from ai_sdk.providers.togetherai import (
    TogetherAIProvider,
    TogetherAIImageModel,
    create_together,
    TogetherAIProviderSettings
)


class TestTogetherAIImageModel:
    """Test the custom TogetherAI image model."""
    
    def test_image_model_creation(self):
        """Test creating a TogetherAI image model."""
        config = {
            'provider': 'togetherai.image',
            'base_url': 'https://api.together.xyz/v1',
            'headers': lambda: {'Authorization': 'Bearer test-key'},
            'fetch': None,
        }
        
        model = TogetherAIImageModel("black-forest-labs/FLUX.1-schnell-Free", config)
        
        assert model.model_id == "black-forest-labs/FLUX.1-schnell-Free"
        assert model.provider == "togetherai.image"
    
    def test_size_parsing(self):
        """Test size string parsing for TogetherAI format."""
        config = {'provider': 'togetherai.image'}
        model = TogetherAIImageModel("test-model", config)
        
        # Test valid size formats
        assert model._parse_size("1024x768") == {"width": 1024, "height": 768}
        assert model._parse_size("512x512") == {"width": 512, "height": 512}
        assert model._parse_size("1920X1080") == {"width": 1920, "height": 1080}
        
        # Test invalid formats
        assert model._parse_size("1024") is None
        assert model._parse_size("invalid") is None
        assert model._parse_size(None) is None
        assert model._parse_size("") is None
    
    def test_supported_sizes(self):
        """Test getting supported image sizes."""
        config = {'provider': 'togetherai.image'}
        model = TogetherAIImageModel("test-model", config)
        
        sizes = model.get_supported_sizes()
        
        assert isinstance(sizes, list)
        assert "1024x1024" in sizes
        assert "512x512" in sizes
        assert "768x768" in sizes
        assert len(sizes) > 0
    
    def test_max_images_per_call(self):
        """Test getting maximum images per call."""
        config = {'provider': 'togetherai.image'}
        model = TogetherAIImageModel("test-model", config)
        
        max_images = model.get_max_images_per_call()
        
        assert isinstance(max_images, int)
        assert max_images > 0
        assert max_images <= 4  # TogetherAI typical limit
    
    @patch('ai_sdk.providers.togetherai.image_model.make_request')
    async def test_generate_image(self, mock_request):
        """Test image generation with proper API format."""
        mock_request.return_value = {
            "data": [
                {
                    "b64_json": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQV",
                }
            ],
            "usage": {"total_tokens": 100}
        }
        
        config = {
            'provider': 'togetherai.image',
            'base_url': 'https://api.together.xyz/v1',
            'headers': lambda: {'Authorization': 'Bearer test-key'},
            'fetch': None,
        }
        
        model = TogetherAIImageModel("black-forest-labs/FLUX.1-schnell-Free", config)
        
        result = await model.generate_image(
            prompt="A test image",
            size="1024x768",
            n=1,
            seed=42
        )
        
        # Verify API call was made with correct format
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        
        assert call_args[1]['url'] == 'https://api.together.xyz/v1/images/generations'
        assert call_args[1]['method'] == 'POST'
        
        # Check request body format
        body = call_args[1]['json']
        assert body['model'] == "black-forest-labs/FLUX.1-schnell-Free"
        assert body['prompt'] == "A test image"
        assert body['response_format'] == "base64"
        assert body['width'] == 1024
        assert body['height'] == 768
        assert body['n'] == 1
        assert body['seed'] == 42
        
        # Check result format
        assert len(result.images) == 1
        assert result.images[0]['b64_json'] == "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQV"
        assert result.response_metadata['model_id'] == "black-forest-labs/FLUX.1-schnell-Free"
        assert result.response_metadata['provider'] == "togetherai.image"


class TestTogetherAIProvider:
    """Test the enhanced TogetherAI provider."""
    
    def test_provider_creation_with_custom_settings(self):
        """Test creating provider with custom settings."""
        settings = TogetherAIProviderSettings(
            api_key="test-key",
            base_url="https://custom.api.url",
            headers={"Custom-Header": "value"},
            include_usage=False
        )
        
        provider = TogetherAIProvider(settings)
        
        assert provider.name == "togetherai"
        assert provider.settings.api_key == "test-key"
        assert provider.settings.base_url == "https://custom.api.url"
        assert provider.settings.headers == {"Custom-Header": "value"}
        assert provider.settings.include_usage is False
    
    def test_provider_uses_custom_image_model(self):
        """Test that provider uses custom TogetherAI image model."""
        provider = create_together()
        
        image_model = provider.image_model("black-forest-labs/FLUX.1-schnell-Free")
        
        assert isinstance(image_model, TogetherAIImageModel)
        assert image_model.model_id == "black-forest-labs/FLUX.1-schnell-Free"
        assert image_model.provider == "togetherai.image"
    
    @patch.dict('os.environ', {'TOGETHER_AI_API_KEY': 'env-test-key'})
    def test_api_key_from_environment(self):
        """Test that API key is read from environment."""
        provider = TogetherAIProvider()
        
        api_key = provider._get_api_key()
        assert api_key == "env-test-key"
    
    @patch.dict('os.environ', {'TOGETHER_API_KEY': 'alt-env-test-key'})
    def test_alternative_api_key_from_environment(self):
        """Test that alternative API key environment variable works."""
        provider = TogetherAIProvider()
        
        api_key = provider._get_api_key()
        assert api_key == "alt-env-test-key"
    
    def test_get_headers(self):
        """Test header generation with API key and custom headers."""
        settings = TogetherAIProviderSettings(
            api_key="test-key",
            headers={"Custom-Header": "value", "Another": "header"}
        )
        
        provider = TogetherAIProvider(settings)
        headers = provider._get_headers()
        
        expected_headers = {
            "Authorization": "Bearer test-key",
            "Custom-Header": "value",
            "Another": "header"
        }
        
        assert headers == expected_headers
    
    def test_image_model_config(self):
        """Test that image model receives correct configuration."""
        settings = TogetherAIProviderSettings(
            api_key="test-key",
            base_url="https://custom.api.url",
            headers={"Custom": "header"}
        )
        
        provider = TogetherAIProvider(settings)
        image_model = provider.image_model("test-model")
        
        # Verify config is passed correctly
        assert image_model.config['provider'] == 'togetherai.image'
        assert image_model.config['base_url'] == 'https://custom.api.url'
        assert callable(image_model.config['headers'])
        
        # Test headers function
        headers = image_model.config['headers']()
        assert headers['Authorization'] == 'Bearer test-key'
        assert headers['Custom'] == 'header'


@pytest.mark.integration
class TestTogetherAIIntegration:
    """Integration tests for TogetherAI provider (require API key)."""
    
    @pytest.mark.skip(reason="Requires actual API key")
    async def test_real_image_generation(self):
        """Test real image generation (skipped by default)."""
        provider = create_together()
        model = provider.image_model("black-forest-labs/FLUX.1-schnell-Free")
        
        result = await model.generate_image(
            prompt="A simple test image",
            size="512x512",
            n=1
        )
        
        assert len(result.images) == 1
        assert result.images[0].get('b64_json') is not None