"""Tests for Google Generative AI provider integration."""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json

from ai_sdk import generate_text, stream_text
from ai_sdk.providers.google import create_google, GoogleProvider, GoogleLanguageModel
from ai_sdk.providers.types import Message
from ai_sdk.errors import APIError


class TestGoogleProvider:
    """Test Google provider creation and configuration."""
    
    def test_create_google_with_api_key(self):
        """Test creating Google provider with API key."""
        provider = create_google(api_key="test-key")
        
        assert isinstance(provider, GoogleProvider)
        assert provider.api_key == "test-key"
        assert provider.provider_id == "google"
        assert provider.base_url == "https://generativelanguage.googleapis.com/v1beta"
    
    def test_create_google_with_custom_base_url(self):
        """Test creating Google provider with custom base URL."""
        provider = create_google(
            api_key="test-key",
            base_url="https://custom-google-api.com/v1"
        )
        
        assert provider.base_url == "https://custom-google-api.com/v1"
    
    @patch.dict("os.environ", {"GOOGLE_GENERATIVE_AI_API_KEY": "env-key"})
    def test_create_google_from_env(self):
        """Test creating Google provider from environment variable."""
        provider = create_google()
        assert provider.api_key == "env-key"
    
    def test_create_google_missing_api_key(self):
        """Test creating Google provider without API key raises error."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="Google API key is required"):
                create_google()
    
    def test_language_model_creation(self):
        """Test creating language models."""
        provider = create_google(api_key="test-key")
        
        model = provider.language_model("gemini-1.5-pro")
        assert isinstance(model, GoogleLanguageModel)
        assert model.model_id == "gemini-1.5-pro"
        
        # Test aliases
        chat_model = provider.chat("gemini-1.5-flash")
        assert isinstance(chat_model, GoogleLanguageModel)
        
        callable_model = provider("gemini-1.5-pro")  
        assert isinstance(callable_model, GoogleLanguageModel)
    
    def test_supported_models(self):
        """Test supported models list."""
        provider = create_google(api_key="test-key")
        models = provider.supported_models
        
        assert "gemini-1.5-pro" in models
        assert "gemini-1.5-flash" in models
        assert "gemini-2.0-flash" in models
        assert "gemma-3-12b-it" in models


class TestGoogleLanguageModel:
    """Test Google language model functionality."""
    
    @pytest.fixture
    def mock_http_client(self):
        """Mock HTTP client."""
        client = AsyncMock()
        client.__aenter__ = AsyncMock(return_value=client)
        client.__aexit__ = AsyncMock(return_value=None)
        return client
    
    def test_model_initialization(self):
        """Test model initialization."""
        model = GoogleLanguageModel(
            model_id="gemini-1.5-pro",
            api_key="test-key"
        )
        
        assert model.model_id == "gemini-1.5-pro"
        assert model.api_key == "test-key"
        assert model.provider_id == "google"
        assert not model.is_gemma_model
        
        # Test Gemma detection
        gemma_model = GoogleLanguageModel(
            model_id="gemma-3-12b-it",
            api_key="test-key"
        )
        assert gemma_model.is_gemma_model
    
    def test_headers_generation(self):
        """Test request headers."""
        model = GoogleLanguageModel(
            model_id="gemini-1.5-pro",
            api_key="test-api-key"
        )
        
        headers = model._get_headers()
        assert headers["Content-Type"] == "application/json"
        assert headers["x-goog-api-key"] == "test-api-key"
    
    def test_model_path_generation(self):
        """Test model path generation."""
        model = GoogleLanguageModel(
            model_id="gemini-1.5-pro",
            api_key="test-key"
        )
        
        # Simple model ID
        path = model._get_model_path("gemini-1.5-pro")
        assert path == "models/gemini-1.5-pro"
        
        # Full path
        full_path = model._get_model_path("models/gemini-1.5-pro")
        assert full_path == "models/gemini-1.5-pro"
    
    @pytest.mark.asyncio
    async def test_generate_success(self, mock_http_client):
        """Test successful text generation."""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.is_success = True
        mock_response.json.return_value = {
            "candidates": [{
                "content": {
                    "role": "model",
                    "parts": [{"text": "Hello! How can I help you?"}]
                },
                "finishReason": "STOP"
            }],
            "usageMetadata": {
                "promptTokenCount": 10,
                "candidatesTokenCount": 8,
                "totalTokenCount": 18
            }
        }
        
        mock_http_client.post = AsyncMock(return_value=mock_response)
        
        with patch("ai_sdk.providers.google.language_model.create_http_client") as mock_create:
            mock_create.return_value = mock_http_client
            
            model = GoogleLanguageModel(
                model_id="gemini-1.5-pro",
                api_key="test-key"
            )
            
            from ai_sdk.providers.types import GenerateOptions
            
            options = GenerateOptions(
                messages=[Message(role="user", content="Hello")],
                max_tokens=100,
                temperature=0.7
            )
            
            result = await model.do_generate(options)
            
            assert result.text == "Hello! How can I help you?"
            assert result.usage.prompt_tokens == 10
            assert result.usage.completion_tokens == 8
            assert result.usage.total_tokens == 18
            assert result.finish_reason == "stop"
    
    @pytest.mark.asyncio
    async def test_generate_error_handling(self, mock_http_client):
        """Test error handling in generation."""
        # Mock error response
        mock_response = MagicMock()
        mock_response.is_success = False
        mock_response.status_code = 400
        mock_response.reason_phrase = "Bad Request"
        mock_response.json.return_value = {
            "error": {
                "code": 400,
                "message": "Invalid request",
                "status": "INVALID_ARGUMENT"
            }
        }
        
        mock_http_client.post = AsyncMock(return_value=mock_response)
        
        with patch("ai_sdk.providers.google.language_model.create_http_client") as mock_create:
            mock_create.return_value = mock_http_client
            
            model = GoogleLanguageModel(
                model_id="gemini-1.5-pro",
                api_key="test-key"
            )
            
            from ai_sdk.providers.types import GenerateOptions
            
            options = GenerateOptions(
                messages=[Message(role="user", content="Hello")],
            )
            
            with pytest.raises(APIError, match="Bad request to Google API"):
                await model.do_generate(options)
    
    @pytest.mark.asyncio
    async def test_stream_success(self, mock_http_client):
        """Test successful streaming."""
        # Mock streaming response
        stream_data = [
            '{"candidates":[{"content":{"role":"model","parts":[{"text":"Hello"}]}}]}',
            '{"candidates":[{"content":{"role":"model","parts":[{"text":" there!"}]}}]}',
            '{"candidates":[{"content":{"role":"model","parts":[{"text":""}]},"finishReason":"STOP"}],"usageMetadata":{"promptTokenCount":5,"candidatesTokenCount":3,"totalTokenCount":8}}'
        ]
        
        async def mock_aiter_lines():
            for line in stream_data:
                yield line
        
        mock_stream_response = MagicMock()
        mock_stream_response.is_success = True
        mock_stream_response.aiter_lines = mock_aiter_lines
        mock_stream_response.__aenter__ = AsyncMock(return_value=mock_stream_response)
        mock_stream_response.__aexit__ = AsyncMock(return_value=None)
        
        mock_http_client.stream = MagicMock(return_value=mock_stream_response)
        
        with patch("ai_sdk.providers.google.language_model.create_http_client") as mock_create:
            mock_create.return_value = mock_http_client
            
            model = GoogleLanguageModel(
                model_id="gemini-1.5-pro",
                api_key="test-key"
            )
            
            from ai_sdk.providers.types import StreamOptions
            
            options = StreamOptions(
                messages=[Message(role="user", content="Hello")],
            )
            
            results = []
            async for result in model.do_stream(options):
                results.append(result)
            
            # Should have text deltas and finish
            assert len(results) >= 2
            
            # Check for text delta parts
            text_parts = [r for r in results if r.stream_parts and r.stream_parts[0].type == "text-delta"]
            assert len(text_parts) >= 2
            assert text_parts[0].stream_parts[0].text_delta == "Hello"
            assert text_parts[1].stream_parts[0].text_delta == " there!"


class TestGoogleIntegration:
    """Test Google provider integration with core functions."""
    
    @pytest.mark.asyncio
    async def test_generate_text_integration(self):
        """Test generate_text with Google provider."""
        
        with patch("ai_sdk.providers.google.language_model.create_http_client") as mock_create:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            
            mock_response = MagicMock()
            mock_response.is_success = True
            mock_response.json.return_value = {
                "candidates": [{
                    "content": {
                        "role": "model",
                        "parts": [{"text": "I'm Gemini, Google's AI assistant."}]
                    },
                    "finishReason": "STOP"
                }],
                "usageMetadata": {
                    "promptTokenCount": 15,
                    "candidatesTokenCount": 12, 
                    "totalTokenCount": 27
                }
            }
            
            mock_client.post = AsyncMock(return_value=mock_response)
            mock_create.return_value = mock_client
            
            # Create Google provider and model
            google = create_google(api_key="test-key")
            model = google.language_model("gemini-1.5-pro")
            
            # Generate text
            result = await generate_text(
                model=model,
                messages=[{"role": "user", "content": "Who are you?"}]
            )
            
            assert result.text == "I'm Gemini, Google's AI assistant."
            assert result.usage.total_tokens == 27
            assert result.finish_reason == "stop"
    
    @pytest.mark.asyncio
    async def test_stream_text_integration(self):
        """Test stream_text with Google provider."""
        
        with patch("ai_sdk.providers.google.language_model.create_http_client") as mock_create:
            mock_client = AsyncMock()
            mock_client.__aenter__ = AsyncMock(return_value=mock_client)
            mock_client.__aexit__ = AsyncMock(return_value=None)
            
            # Mock streaming response
            stream_data = [
                '{"candidates":[{"content":{"role":"model","parts":[{"text":"Google"}]}}]}',
                '{"candidates":[{"content":{"role":"model","parts":[{"text":" AI"}]}}]}',
                '{"candidates":[{"content":{"role":"model","parts":[{"text":" rocks!"}]},"finishReason":"STOP"}]}'
            ]
            
            async def mock_aiter_lines():
                for line in stream_data:
                    yield line
            
            mock_stream_response = MagicMock()
            mock_stream_response.is_success = True
            mock_stream_response.aiter_lines = mock_aiter_lines
            mock_stream_response.__aenter__ = AsyncMock(return_value=mock_stream_response)
            mock_stream_response.__aexit__ = AsyncMock(return_value=None)
            
            mock_client.stream = MagicMock(return_value=mock_stream_response)
            mock_create.return_value = mock_client
            
            # Create Google provider and model
            google = create_google(api_key="test-key")
            model = google.language_model("gemini-1.5-flash")
            
            # Stream text
            collected_text = ""
            async for chunk in stream_text(
                model=model,
                messages=[{"role": "user", "content": "What do you think about Google AI?"}]
            ):
                for part in chunk.stream_parts:
                    if part.type == "text-delta":
                        collected_text += part.text_delta
            
            assert collected_text == "Google AI rocks!"


if __name__ == "__main__":
    pytest.main([__file__])