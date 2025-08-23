"""Integration tests for LMNT provider."""

import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch

from ai_sdk.providers.lmnt import create_lmnt, LMNTProvider
from ai_sdk.providers.lmnt.types import LMNTSpeechOptions
from ai_sdk.errors import AISDKError, APICallError


class TestLMNTProvider:
    """Test LMNT provider functionality."""
    
    def test_create_lmnt_with_api_key(self):
        """Test creating LMNT provider with API key."""
        provider = create_lmnt(api_key="test-key")
        assert isinstance(provider, LMNTProvider)
        assert provider.api_key == "test-key"
        assert provider.base_url == "https://api.lmnt.com/v1"

    def test_create_lmnt_with_env_var(self):
        """Test creating LMNT provider with environment variable."""
        with patch.dict(os.environ, {"LMNT_API_KEY": "env-key"}):
            provider = create_lmnt()
            assert provider.api_key == "env-key"

    def test_create_lmnt_no_api_key_raises_error(self):
        """Test that creating LMNT provider without API key raises error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(AISDKError, match="LMNT API key is required"):
                create_lmnt()

    def test_create_lmnt_with_custom_options(self):
        """Test creating LMNT provider with custom options."""
        provider = create_lmnt(
            api_key="test-key",
            base_url="https://custom.lmnt.api",
            headers={"x-custom": "value"}
        )
        assert provider.base_url == "https://custom.lmnt.api"
        assert provider.headers["x-custom"] == "value"

    def test_speech_model_creation(self):
        """Test creating speech models."""
        provider = create_lmnt(api_key="test-key")
        
        # Test Aurora model
        aurora_model = provider.speech("aurora")
        assert aurora_model.model_id == "aurora"
        
        # Test Blizzard model
        blizzard_model = provider.speech("blizzard")
        assert blizzard_model.model_id == "blizzard"


class TestLMNTSpeechModel:
    """Test LMNT speech model functionality."""
    
    @pytest.fixture
    def mock_response(self):
        """Mock successful LMNT API response."""
        response = MagicMock()
        response.status_code = 200
        response.content = b"fake_audio_data"
        response.headers = {"content-type": "audio/mp3"}
        response.json.return_value = {"status": "success"}
        return response
    
    @pytest.fixture
    def provider(self):
        """Create test provider."""
        return create_lmnt(api_key="test-key")
    
    async def test_basic_speech_generation(self, provider, mock_response):
        """Test basic speech generation."""
        model = provider.speech("aurora")
        
        with patch.object(model, 'client') as mock_client:
            mock_client.post = AsyncMock(return_value=mock_response)
            
            result = await model.generate(
                text="Hello, world!",
                voice="ava"
            )
            
            assert result.audio.data == b"fake_audio_data"
            assert result.audio.format == "mp3"
            assert result.audio.sample_rate == 24000
            
            # Verify API call
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            assert call_args[0][0] == "https://api.lmnt.com/v1/ai/speech/bytes"
            
            # Check request payload
            payload = call_args[1]["json"]
            assert payload["text"] == "Hello, world!"
            assert payload["voice"] == "ava"
            assert payload["model"] == "aurora"

    async def test_speech_generation_with_options(self, provider, mock_response):
        """Test speech generation with provider options."""
        model = provider.speech("aurora")
        
        with patch.object(model, 'client') as mock_client:
            mock_client.post = AsyncMock(return_value=mock_response)
            
            result = await model.generate(
                text="Testing with options",
                voice="narrator",
                speed=1.2,
                language="en",
                provider_options={
                    "conversational": True,
                    "temperature": 0.8,
                    "top_p": 0.7,
                    "format": "wav",
                    "sample_rate": 16000,
                }
            )
            
            # Verify API call
            payload = mock_client.post.call_args[1]["json"]
            assert payload["speed"] == 1.2
            assert payload["language"] == "en"
            assert payload["conversational"] is True
            assert payload["temperature"] == 0.8
            assert payload["top_p"] == 0.7
            assert payload["format"] == "wav"
            assert payload["sample_rate"] == 16000

    async def test_blizzard_model_ignores_advanced_options(self, provider, mock_response):
        """Test that Blizzard model ignores advanced options."""
        model = provider.speech("blizzard")
        
        with patch.object(model, 'client') as mock_client:
            mock_client.post = AsyncMock(return_value=mock_response)
            
            await model.generate(
                text="Testing Blizzard",
                voice="ava",
                provider_options={
                    "conversational": True,  # Should be ignored
                    "length": 30.0,         # Should be ignored
                }
            )
            
            # Verify advanced options are not sent
            payload = mock_client.post.call_args[1]["json"]
            assert "conversational" not in payload
            assert "length" not in payload

    async def test_text_too_long_error(self, provider):
        """Test error handling for text that's too long."""
        model = provider.speech("aurora")
        
        long_text = "x" * 5001  # Over 5000 character limit
        
        with pytest.raises(AISDKError, match="Text must be 5000 characters or less"):
            await model.generate(text=long_text, voice="ava")

    async def test_api_error_handling(self, provider):
        """Test handling of API errors."""
        model = provider.speech("aurora")
        
        # Mock error response
        error_response = MagicMock()
        error_response.status_code = 400
        error_response.json.return_value = {
            "error": "Invalid voice ID",
            "code": "invalid_voice"
        }
        error_response.headers = {}
        error_response.text = '{"error": "Invalid voice ID"}'
        
        with patch.object(model, 'client') as mock_client:
            mock_client.post = AsyncMock(return_value=error_response)
            
            with pytest.raises(APICallError, match="Invalid voice ID"):
                await model.generate(text="Hello", voice="invalid_voice")

    async def test_warnings_in_response(self, provider):
        """Test handling of warnings in API response."""
        model = provider.speech("aurora")
        
        # Mock response with warnings
        response = MagicMock()
        response.status_code = 200
        response.content = b"fake_audio_data"
        response.headers = {
            "x-lmnt-warnings": '[{"message": "Voice not optimized for this language"}]'
        }
        
        with patch.object(model, 'client') as mock_client:
            mock_client.post = AsyncMock(return_value=response)
            
            result = await model.generate(text="Hello", voice="ava")
            
            assert len(result.warnings) == 1
            assert "Voice not optimized" in result.warnings[0]

    async def test_deterministic_generation_with_seed(self, provider, mock_response):
        """Test deterministic generation with seed."""
        model = provider.speech("aurora")
        
        with patch.object(model, 'client') as mock_client:
            mock_client.post = AsyncMock(return_value=mock_response)
            
            await model.generate(
                text="Deterministic test",
                voice="ava",
                provider_options={"seed": 12345}
            )
            
            payload = mock_client.post.call_args[1]["json"]
            assert payload["seed"] == 12345

    def test_speech_options_validation(self):
        """Test validation of speech options."""
        # Valid options
        options = LMNTSpeechOptions(
            model="aurora",
            speed=1.5,
            top_p=0.8,
            temperature=0.7
        )
        assert options.speed == 1.5
        
        # Invalid speed (too high)
        with pytest.raises(ValueError):
            LMNTSpeechOptions(speed=3.0)
        
        # Invalid top_p (too high)  
        with pytest.raises(ValueError):
            LMNTSpeechOptions(top_p=1.5)
        
        # Invalid temperature (negative)
        with pytest.raises(ValueError):
            LMNTSpeechOptions(temperature=-0.5)


@pytest.mark.skipif(
    not os.getenv("LMNT_API_KEY"),
    reason="LMNT_API_KEY environment variable not set"
)
class TestLMNTIntegration:
    """Integration tests with real LMNT API (requires API key)."""
    
    async def test_real_api_basic_generation(self):
        """Test basic generation with real API."""
        provider = create_lmnt()
        model = provider.speech("aurora")
        
        result = await model.generate(
            text="This is a test of LMNT integration.",
            voice="ava"
        )
        
        assert len(result.audio.data) > 0
        assert result.audio.format == "mp3"
        assert result.response["model_id"] == "aurora"
    
    async def test_real_api_conversational_style(self):
        """Test conversational style with real API."""
        provider = create_lmnt()
        model = provider.speech("aurora")
        
        result = await model.generate(
            text="Hey there! How's it going?",
            voice="ava",
            provider_options={
                "conversational": True,
                "speed": 1.1
            }
        )
        
        assert len(result.audio.data) > 0
        
    async def test_real_api_different_formats(self):
        """Test different audio formats with real API."""
        provider = create_lmnt()
        model = provider.speech("aurora")
        
        formats = ["mp3", "wav"]
        
        for fmt in formats:
            result = await model.generate(
                text=f"Testing {fmt} format.",
                voice="ava",
                output_format=fmt
            )
            
            assert len(result.audio.data) > 0
            assert result.audio.format == fmt