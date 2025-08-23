"""Tests for image generation functionality."""

import pytest
from unittest.mock import AsyncMock, patch, Mock
import json
import base64

from ai_sdk.core import generate_image, generate_image_sync, GenerateImageResult, NoImageGeneratedError
from ai_sdk.providers.openai import OpenAIProvider, OpenAIImageModel


class MockResponse:
    """Mock HTTP response."""
    
    def __init__(self, status_code: int, json_data: dict):
        self.status_code = status_code
        self._json_data = json_data
    
    def json(self):
        return self._json_data


@pytest.fixture
def openai_provider():
    """Create OpenAI provider for testing."""
    return OpenAIProvider(api_key="test-key")


@pytest.fixture
def image_model(openai_provider):
    """Create image model for testing."""
    return openai_provider.image_model("dall-e-3")


# Sample base64 encoded 1x1 PNG (minimal valid PNG)
SAMPLE_PNG_B64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI/hBKPQgAAAABJRU5ErkJggg=="


class TestImageGeneration:
    """Test image generation functionality."""
    
    @pytest.mark.asyncio
    async def test_basic_image_generation(self, image_model):
        """Test basic image generation."""
        
        # Mock successful API response
        mock_response_data = {
            "created": 1234567890,
            "data": [
                {"b64_json": SAMPLE_PNG_B64}
            ]
        }
        
        with patch("ai_sdk.utils.http.create_http_client") as mock_client_factory:
            mock_client = AsyncMock()
            mock_response = MockResponse(200, mock_response_data)
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client_factory.return_value = mock_client
            
            result = await generate_image(
                model=image_model,
                prompt="A test image"
            )
            
            assert isinstance(result, GenerateImageResult)
            assert len(result.images) == 1
            assert result.images[0].media_type == "image/png"
            assert len(result.images[0].data) > 0
            
            # Verify API call was made correctly
            mock_client.post.assert_called_once_with(
                "/images/generations",
                json={
                    "model": "dall-e-3",
                    "prompt": "A test image",
                    "n": 1,
                    "response_format": "b64_json"
                }
            )
    
    @pytest.mark.asyncio
    async def test_multiple_image_generation(self, image_model):
        """Test generating multiple images."""
        
        mock_response_data = {
            "created": 1234567890,
            "data": [
                {"b64_json": SAMPLE_PNG_B64},
                {"b64_json": SAMPLE_PNG_B64}
            ]
        }
        
        with patch("ai_sdk.utils.http.create_http_client") as mock_client_factory:
            mock_client = AsyncMock()
            mock_response = MockResponse(200, mock_response_data)
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client_factory.return_value = mock_client
            
            result = await generate_image(
                model=image_model,
                prompt="A test image",
                n=2
            )
            
            assert len(result.images) == 2
            for img in result.images:
                assert img.media_type == "image/png"
                assert len(img.data) > 0
    
    @pytest.mark.asyncio
    async def test_image_generation_with_parameters(self, image_model):
        """Test image generation with various parameters."""
        
        mock_response_data = {
            "created": 1234567890,
            "data": [{"b64_json": SAMPLE_PNG_B64}]
        }
        
        with patch("ai_sdk.utils.http.create_http_client") as mock_client_factory:
            mock_client = AsyncMock()
            mock_response = MockResponse(200, mock_response_data)
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client_factory.return_value = mock_client
            
            result = await generate_image(
                model=image_model,
                prompt="A test image",
                size="1024x1024",
                provider_options={
                    "openai": {
                        "style": "vivid",
                        "quality": "hd"
                    }
                }
            )
            
            assert len(result.images) == 1
            
            # Check that parameters were passed correctly
            call_args = mock_client.post.call_args
            assert call_args[1]["json"]["size"] == "1024x1024"
            assert call_args[1]["json"]["style"] == "vivid"
            assert call_args[1]["json"]["quality"] == "hd"
    
    @pytest.mark.asyncio
    async def test_aspect_ratio_conversion(self, image_model):
        """Test aspect ratio to size conversion."""
        
        mock_response_data = {
            "created": 1234567890,
            "data": [{"b64_json": SAMPLE_PNG_B64}]
        }
        
        with patch("ai_sdk.utils.http.create_http_client") as mock_client_factory:
            mock_client = AsyncMock()
            mock_response = MockResponse(200, mock_response_data)
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client_factory.return_value = mock_client
            
            # Test 16:9 aspect ratio
            await generate_image(
                model=image_model,
                prompt="A test image",
                aspect_ratio="16:9"
            )
            
            call_args = mock_client.post.call_args
            assert call_args[1]["json"]["size"] == "1792x1024"
    
    @pytest.mark.asyncio
    async def test_api_error_handling(self, image_model):
        """Test handling of API errors."""
        
        error_response_data = {
            "error": {
                "message": "Invalid prompt",
                "type": "invalid_request_error"
            }
        }
        
        with patch("ai_sdk.utils.http.create_http_client") as mock_client_factory:
            mock_client = AsyncMock()
            mock_response = MockResponse(400, error_response_data)
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client_factory.return_value = mock_client
            
            with pytest.raises(Exception) as exc_info:
                await generate_image(
                    model=image_model,
                    prompt="Bad prompt"
                )
            
            assert "Invalid prompt" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_no_images_generated_error(self, image_model):
        """Test NoImageGeneratedError when no images are returned."""
        
        mock_response_data = {
            "created": 1234567890,
            "data": []  # No images
        }
        
        with patch("ai_sdk.utils.http.create_http_client") as mock_client_factory:
            mock_client = AsyncMock()
            mock_response = MockResponse(200, mock_response_data)
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client_factory.return_value = mock_client
            
            with pytest.raises(NoImageGeneratedError):
                await generate_image(
                    model=image_model,
                    prompt="A test image"
                )
    
    def test_sync_image_generation(self, image_model):
        """Test synchronous image generation."""
        
        mock_response_data = {
            "created": 1234567890,
            "data": [{"b64_json": SAMPLE_PNG_B64}]
        }
        
        with patch("ai_sdk.utils.http.create_http_client") as mock_client_factory:
            mock_client = AsyncMock()
            mock_response = MockResponse(200, mock_response_data)
            mock_client.post.return_value = mock_response
            mock_client.__aenter__.return_value = mock_client
            mock_client_factory.return_value = mock_client
            
            result = generate_image_sync(
                model=image_model,
                prompt="A test image"
            )
            
            assert isinstance(result, GenerateImageResult)
            assert len(result.images) == 1
            assert result.images[0].media_type == "image/png"
    
    def test_dalle_2_max_images_per_call(self):
        """Test DALL-E 2 max images per call setting."""
        provider = OpenAIProvider(api_key="test")
        dalle2_model = provider.image_model("dall-e-2")
        assert dalle2_model.max_images_per_call == 10
        
        dalle3_model = provider.image_model("dall-e-3")
        assert dalle3_model.max_images_per_call == 1
    
    def test_image_model_creation(self, openai_provider):
        """Test image model creation and configuration."""
        
        # Test default model
        model = openai_provider.image_model()
        assert model.model_id == "dall-e-3"
        assert model.provider == openai_provider
        
        # Test specific model
        model = openai_provider.image_model("dall-e-2")
        assert model.model_id == "dall-e-2"
        
        # Test alias method
        model = openai_provider.image("dall-e-3")
        assert model.model_id == "dall-e-3"