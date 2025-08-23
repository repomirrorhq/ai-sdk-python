"""
Integration tests for Anthropic provider.

These tests verify the Anthropic provider works correctly with mock responses.
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from ai_sdk.providers.anthropic import create_anthropic, AnthropicProvider
from ai_sdk.core.types import Message, Content


class TestAnthropicProvider:
    """Test the Anthropic provider."""
    
    def test_create_anthropic_provider(self):
        """Test creating an Anthropic provider."""
        provider = create_anthropic(api_key="test-key")
        assert isinstance(provider, AnthropicProvider)
        assert provider.name == "anthropic"
        assert provider.settings.api_key == "test-key"
        assert provider.settings.base_url == "https://api.anthropic.com/v1"
    
    def test_create_language_model(self):
        """Test creating a language model."""
        provider = create_anthropic(api_key="test-key")
        model = provider.language_model("claude-3-sonnet-20240229")
        
        assert model.model_id == "claude-3-sonnet-20240229"
        assert model.settings == provider.settings
    
    def test_model_aliases(self):
        """Test that chat() and messages() are aliases for language_model()."""
        provider = create_anthropic(api_key="test-key")
        
        model1 = provider.language_model("claude-3-sonnet-20240229")
        model2 = provider.chat("claude-3-sonnet-20240229")
        model3 = provider.messages("claude-3-sonnet-20240229")
        
        # They should be the same type and have same model_id
        assert type(model1) == type(model2) == type(model3)
        assert model1.model_id == model2.model_id == model3.model_id
    
    def test_env_api_key(self):
        """Test reading API key from environment."""
        with patch.dict('os.environ', {'ANTHROPIC_API_KEY': 'env-key'}):
            provider = create_anthropic()
            assert provider.settings.api_key == "env-key"
    
    def test_missing_api_key(self):
        """Test error when API key is missing."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Anthropic API key not found"):
                create_anthropic()


class TestAnthropicLanguageModel:
    """Test the Anthropic language model."""
    
    @pytest.fixture
    def model(self):
        """Create a test model."""
        provider = create_anthropic(api_key="test-key")
        return provider.language_model("claude-3-sonnet-20240229")
    
    def test_build_headers(self, model):
        """Test building request headers."""
        headers = model._build_headers()
        
        expected_headers = {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
            "x-api-key": "test-key",
        }
        
        for key, value in expected_headers.items():
            assert headers[key] == value
    
    def test_build_request_body_simple(self, model):
        """Test building request body for simple message."""
        messages = [
            Message(
                role="user",
                content=[Content(type="text", text="Hello")]
            )
        ]
        
        body = model._build_request_body(messages, max_tokens=100)
        
        assert body["model"] == "claude-3-sonnet-20240229"
        assert body["max_tokens"] == 100
        assert len(body["messages"]) == 1
        assert body["messages"][0]["role"] == "user"
        assert body["messages"][0]["content"] == "Hello"
    
    def test_build_request_body_with_system(self, model):
        """Test building request body with system message."""
        messages = [
            Message(
                role="system",
                content=[Content(type="text", text="You are helpful")]
            ),
            Message(
                role="user", 
                content=[Content(type="text", text="Hello")]
            )
        ]
        
        body = model._build_request_body(messages)
        
        assert body["system"] == "You are helpful"
        assert len(body["messages"]) == 1
        assert body["messages"][0]["role"] == "user"
    
    def test_build_request_body_with_params(self, model):
        """Test building request body with optional parameters."""
        messages = [
            Message(
                role="user",
                content=[Content(type="text", text="Hello")]
            )
        ]
        
        body = model._build_request_body(
            messages,
            temperature=0.7,
            top_p=0.9,
            top_k=40,
            stop_sequences=["STOP"],
            stream=True,
        )
        
        assert body["temperature"] == 0.7
        assert body["top_p"] == 0.9
        assert body["top_k"] == 40
        assert body["stop_sequences"] == ["STOP"]
        assert body["stream"] is True


class TestAnthropicMessageConversion:
    """Test message conversion utilities."""
    
    def test_simple_user_message(self):
        """Test converting simple user message."""
        from ai_sdk.providers.anthropic.message_converter import convert_messages_to_anthropic
        
        messages = [
            Message(
                role="user",
                content=[Content(type="text", text="Hello Claude")]
            )
        ]
        
        result = convert_messages_to_anthropic(messages)
        
        assert "system" not in result
        assert len(result["messages"]) == 1
        assert result["messages"][0]["role"] == "user"
        assert result["messages"][0]["content"] == "Hello Claude"
    
    def test_system_message_extraction(self):
        """Test extracting system message."""
        from ai_sdk.providers.anthropic.message_converter import convert_messages_to_anthropic
        
        messages = [
            Message(
                role="system",
                content=[Content(type="text", text="You are helpful")]
            ),
            Message(
                role="user",
                content=[Content(type="text", text="Hello")]
            )
        ]
        
        result = convert_messages_to_anthropic(messages)
        
        assert result["system"] == "You are helpful"
        assert len(result["messages"]) == 1
        assert result["messages"][0]["role"] == "user"
    
    def test_multiple_system_messages(self):
        """Test multiple system messages are combined."""
        from ai_sdk.providers.anthropic.message_converter import convert_messages_to_anthropic
        
        messages = [
            Message(
                role="system",
                content=[Content(type="text", text="You are helpful")]
            ),
            Message(
                role="system", 
                content=[Content(type="text", text="Be concise")]
            ),
            Message(
                role="user",
                content=[Content(type="text", text="Hello")]
            )
        ]
        
        result = convert_messages_to_anthropic(messages)
        
        assert result["system"] == "You are helpful\n\nBe concise"
        assert len(result["messages"]) == 1
    
    def test_conversation_flow(self):
        """Test user-assistant conversation."""
        from ai_sdk.providers.anthropic.message_converter import convert_messages_to_anthropic
        
        messages = [
            Message(
                role="user",
                content=[Content(type="text", text="Hello")]
            ),
            Message(
                role="assistant",
                content=[Content(type="text", text="Hi there!")]
            ),
            Message(
                role="user",
                content=[Content(type="text", text="How are you?")]
            )
        ]
        
        result = convert_messages_to_anthropic(messages)
        
        assert len(result["messages"]) == 3
        assert result["messages"][0]["role"] == "user"
        assert result["messages"][1]["role"] == "assistant"
        assert result["messages"][2]["role"] == "user"


class TestAnthropicResponseConversion:
    """Test response conversion utilities."""
    
    def test_simple_text_response(self):
        """Test converting simple text response."""
        from ai_sdk.providers.anthropic.message_converter import convert_anthropic_response
        
        response_data = {
            "id": "msg_123",
            "type": "message",
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "Hello! How can I help you today?"
                }
            ],
            "model": "claude-3-sonnet-20240229",
            "stop_reason": "end_turn",
            "usage": {
                "input_tokens": 10,
                "output_tokens": 20
            }
        }
        
        result = convert_anthropic_response(response_data)
        
        assert result.text == "Hello! How can I help you today?"
        assert len(result.content) == 1
        assert result.content[0].type == "text"
        assert result.content[0].text == "Hello! How can I help you today?"
        assert result.finish_reason == "stop"
        assert result.usage.input_tokens == 10
        assert result.usage.output_tokens == 20
        assert result.usage.total_tokens == 30
    
    def test_tool_use_response(self):
        """Test converting response with tool use."""
        from ai_sdk.providers.anthropic.message_converter import convert_anthropic_response
        
        response_data = {
            "id": "msg_123",
            "type": "message",
            "role": "assistant", 
            "content": [
                {
                    "type": "text",
                    "text": "I'll help you with that calculation."
                },
                {
                    "type": "tool_use",
                    "id": "call_123",
                    "name": "calculator",
                    "input": {"expression": "2 + 2"}
                }
            ],
            "model": "claude-3-sonnet-20240229",
            "stop_reason": "tool_use",
            "usage": {
                "input_tokens": 15,
                "output_tokens": 25
            }
        }
        
        result = convert_anthropic_response(response_data)
        
        assert result.text == "I'll help you with that calculation."
        assert len(result.content) == 2
        
        # Check text content
        assert result.content[0].type == "text"
        assert result.content[0].text == "I'll help you with that calculation."
        
        # Check tool call
        assert result.content[1].type == "tool-call"
        assert result.content[1].tool_call_id == "call_123"
        assert result.content[1].tool_name == "calculator"
        assert result.content[1].input == {"expression": "2 + 2"}
        
        assert result.finish_reason == "tool-calls"
    
    def test_finish_reason_mapping(self):
        """Test finish reason mapping."""
        from ai_sdk.providers.anthropic.message_converter import convert_anthropic_response
        
        test_cases = [
            ("end_turn", "stop"),
            ("max_tokens", "length"),
            ("stop_sequence", "stop"),
            ("tool_use", "tool-calls"),
            ("unknown_reason", "unknown"),
        ]
        
        base_response = {
            "content": [{"type": "text", "text": "Test"}],
            "usage": {"input_tokens": 5, "output_tokens": 5}
        }
        
        for anthropic_reason, expected_reason in test_cases:
            response_data = {**base_response, "stop_reason": anthropic_reason}
            result = convert_anthropic_response(response_data)
            assert result.finish_reason == expected_reason


@pytest.mark.asyncio
class TestAnthropicIntegration:
    """Integration tests with mocked HTTP responses."""
    
    @pytest.fixture
    def mock_anthropic_response(self):
        """Mock successful Anthropic API response."""
        return {
            "id": "msg_abc123",
            "type": "message",
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "Hello! I'm Claude, an AI assistant. How can I help you today?"
                }
            ],
            "model": "claude-3-sonnet-20240229",
            "stop_reason": "end_turn",
            "usage": {
                "input_tokens": 12,
                "output_tokens": 20
            }
        }
    
    async def test_generate_text_success(self, mock_anthropic_response):
        """Test successful text generation."""
        with patch('ai_sdk.utils.http.make_request') as mock_request:
            mock_request.return_value = mock_anthropic_response
            
            provider = create_anthropic(api_key="test-key")
            model = provider.language_model("claude-3-sonnet-20240229")
            
            messages = [
                Message(
                    role="user",
                    content=[Content(type="text", text="Hello Claude")]
                )
            ]
            
            result = await model.do_generate(messages, max_tokens=100)
            
            # Verify the request was made
            mock_request.assert_called_once()
            call_args = mock_request.call_args
            
            # Check URL
            assert call_args[1]["url"] == "https://api.anthropic.com/v1/messages"
            
            # Check headers
            headers = call_args[1]["headers"]
            assert headers["x-api-key"] == "test-key"
            assert headers["anthropic-version"] == "2023-06-01"
            
            # Check body
            body = call_args[1]["body"]
            assert body["model"] == "claude-3-sonnet-20240229"
            assert body["max_tokens"] == 100
            assert len(body["messages"]) == 1
            
            # Check result
            assert result.text == "Hello! I'm Claude, an AI assistant. How can I help you today?"
            assert result.finish_reason == "stop"
            assert result.usage.input_tokens == 12
            assert result.usage.output_tokens == 20
            assert result.usage.total_tokens == 32
    
    async def test_api_error_handling(self):
        """Test API error handling."""
        from ai_sdk.errors.base import APIError
        
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = json.dumps({
            "error": {
                "type": "authentication_error",
                "message": "Invalid API key"
            }
        })
        
        error = Exception("HTTP error")
        error.response = mock_response
        
        with patch('ai_sdk.utils.http.make_request') as mock_request:
            mock_request.side_effect = error
            
            provider = create_anthropic(api_key="invalid-key")
            model = provider.language_model("claude-3-sonnet-20240229")
            
            messages = [
                Message(
                    role="user",
                    content=[Content(type="text", text="Hello")]
                )
            ]
            
            with pytest.raises(Exception):  # Should raise some error
                await model.do_generate(messages)


if __name__ == "__main__":
    pytest.main([__file__])