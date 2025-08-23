"""Tests for xAI provider implementation."""

import pytest
from unittest.mock import AsyncMock, Mock, patch

from ai_sdk.providers.xai import XAIProvider
from ai_sdk.providers.xai.types import XAIChatModelId, SearchMode, ReasoningEffort
from ai_sdk.providers.xai.message_converter import convert_to_xai_messages, map_finish_reason
from ai_sdk.core.generate_text import Message, TextContent, FileContent


class TestXAIProvider:
    """Test xAI provider initialization and configuration."""

    def test_provider_init_with_api_key(self):
        """Test provider initialization with API key."""
        provider = XAIProvider(api_key="test-key")
        assert provider.api_key == "test-key"
        assert provider.base_url == "https://api.x.ai/v1"
        assert provider.provider_name == "xai"

    def test_provider_init_with_env_var(self):
        """Test provider initialization with environment variable."""
        with patch.dict("os.environ", {"XAI_API_KEY": "env-key"}):
            provider = XAIProvider()
            assert provider.api_key == "env-key"

    def test_provider_init_no_api_key_raises_error(self):
        """Test provider initialization without API key raises error."""
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValueError, match="xAI API key is required"):
                XAIProvider()

    def test_language_model_creation(self):
        """Test language model creation."""
        provider = XAIProvider(api_key="test-key")
        model = provider.language_model(XAIChatModelId.GROK_4)
        
        assert model.model_id == XAIChatModelId.GROK_4
        assert model.api_key == "test-key"
        assert model.provider == "xai"

    def test_chat_model_alias(self):
        """Test chat model creation (alias for language_model)."""
        provider = XAIProvider(api_key="test-key")
        model = provider.chat("grok-3")
        
        assert model.model_id == "grok-3"
        assert model.provider == "xai"

    def test_convenience_methods(self):
        """Test convenience methods for popular models."""
        provider = XAIProvider(api_key="test-key")
        
        assert provider.grok_4().model_id == XAIChatModelId.GROK_4
        assert provider.grok_3().model_id == XAIChatModelId.GROK_3
        assert provider.grok_3_mini().model_id == XAIChatModelId.GROK_3_MINI
        assert provider.grok_2_vision().model_id == XAIChatModelId.GROK_2_VISION

    def test_provider_callable(self):
        """Test provider direct calling."""
        provider = XAIProvider(api_key="test-key")
        model = provider("grok-4")
        
        assert model.model_id == "grok-4"
        assert model.provider == "xai"


class TestXAIMessageConverter:
    """Test message conversion utilities."""

    def test_convert_simple_messages(self):
        """Test conversion of simple text messages."""
        messages = [
            Message(role="system", content="You are a helpful assistant"),
            Message(role="user", content="Hello"),
            Message(role="assistant", content="Hi there!"),
        ]
        
        xai_messages = convert_to_xai_messages(messages)
        
        assert len(xai_messages) == 3
        assert xai_messages[0] == {"role": "system", "content": "You are a helpful assistant"}
        assert xai_messages[1] == {"role": "user", "content": "Hello"}
        assert xai_messages[2] == {"role": "assistant", "content": "Hi there!"}

    def test_convert_multimodal_user_message(self):
        """Test conversion of multimodal user message."""
        message = Message(
            role="user",
            content=[
                TextContent(text="What's in this image?"),
                FileContent(
                    data=b"fake_image_data",
                    media_type="image/jpeg"
                )
            ]
        )
        
        xai_messages = convert_to_xai_messages([message])
        
        assert len(xai_messages) == 1
        assert xai_messages[0]["role"] == "user"
        assert len(xai_messages[0]["content"]) == 2
        assert xai_messages[0]["content"][0]["type"] == "text"
        assert xai_messages[0]["content"][1]["type"] == "image_url"

    def test_convert_tool_message(self):
        """Test conversion of tool message."""
        message = Message(
            role="tool",
            content="Weather is sunny",
            tool_call_id="call_123"
        )
        
        xai_messages = convert_to_xai_messages([message])
        
        assert len(xai_messages) == 1
        assert xai_messages[0] == {
            "role": "tool",
            "tool_call_id": "call_123",
            "content": "Weather is sunny"
        }

    def test_map_finish_reason(self):
        """Test finish reason mapping."""
        assert map_finish_reason("stop") == "stop"
        assert map_finish_reason("length") == "length"
        assert map_finish_reason("tool_calls") == "tool-calls"
        assert map_finish_reason("function_call") == "tool-calls"
        assert map_finish_reason("content_filter") == "content-filter"
        assert map_finish_reason("unknown_reason") == "other"


class TestXAILanguageModel:
    """Test xAI language model functionality."""

    @pytest.fixture
    def mock_http_client(self):
        """Create mock HTTP client."""
        client = Mock()
        client.post = AsyncMock()
        client.stream = AsyncMock()
        return client

    @pytest.fixture
    def language_model(self, mock_http_client):
        """Create xAI language model with mocked HTTP client."""
        from ai_sdk.providers.xai.language_model import XAILanguageModel
        return XAILanguageModel(
            model_id="grok-4",
            api_key="test-key",
            http_client=mock_http_client
        )

    def test_model_properties(self, language_model):
        """Test model properties."""
        assert language_model.model_id == "grok-4"
        assert language_model.provider == "xai"

    def test_headers_generation(self, language_model):
        """Test request headers generation."""
        headers = language_model._get_headers()
        
        assert headers["Authorization"] == "Bearer test-key"
        assert headers["Content-Type"] == "application/json"

    def test_prepare_tools(self, language_model):
        """Test tool preparation."""
        from ai_sdk.tools.core import Tool
        
        tools = [
            Tool(
                name="get_weather",
                description="Get weather info",
                parameters={
                    "type": "object",
                    "properties": {"location": {"type": "string"}},
                    "required": ["location"]
                }
            )
        ]
        
        xai_tools = language_model._prepare_tools(tools)
        
        assert len(xai_tools) == 1
        assert xai_tools[0]["type"] == "function"
        assert xai_tools[0]["function"]["name"] == "get_weather"
        assert xai_tools[0]["function"]["description"] == "Get weather info"

    @patch('httpx.AsyncClient')
    async def test_generate_text_success(self, mock_client_class, language_model):
        """Test successful text generation."""
        # Mock response
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "test-id",
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": "Test response"
                },
                "finish_reason": "stop"
            }],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15
            }
        }
        mock_response.raise_for_status = Mock()
        
        language_model.http_client.post.return_value = mock_response
        
        # Test generation
        from ai_sdk.core.generate_text import GenerateTextOptions, Message
        
        messages = [Message(role="user", content="Hello")]
        options = GenerateTextOptions(max_tokens=100)
        
        result = await language_model.generate_text(messages, options)
        
        assert result.text == "Test response"
        assert result.finish_reason == "stop"
        assert result.usage["prompt_tokens"] == 10
        assert result.usage["completion_tokens"] == 5

    def test_prepare_request_body_basic(self, language_model):
        """Test basic request body preparation."""
        from ai_sdk.core.generate_text import GenerateTextOptions, Message
        
        messages = [Message(role="user", content="Hello")]
        options = GenerateTextOptions(
            max_tokens=100,
            temperature=0.7,
            top_p=0.9,
            seed=42
        )
        
        body = language_model._prepare_request_body(messages, options)
        
        assert body["model"] == "grok-4"
        assert body["max_tokens"] == 100
        assert body["temperature"] == 0.7
        assert body["top_p"] == 0.9
        assert body["seed"] == 42
        assert len(body["messages"]) == 1
        assert body["messages"][0]["role"] == "user"
        assert body["messages"][0]["content"] == "Hello"

    def test_prepare_request_body_with_provider_options(self, language_model):
        """Test request body preparation with provider options."""
        from ai_sdk.core.generate_text import GenerateTextOptions, Message
        
        messages = [Message(role="user", content="Solve this math problem")]
        options = GenerateTextOptions(
            provider_options={
                "reasoning_effort": "high",
                "search_parameters": {
                    "mode": "on",
                    "return_citations": True,
                    "max_search_results": 5
                }
            }
        )
        
        body = language_model._prepare_request_body(messages, options)
        
        assert body["reasoning_effort"] == "high"
        assert body["search_parameters"]["mode"] == "on"
        assert body["search_parameters"]["return_citations"] is True
        assert body["search_parameters"]["max_search_results"] == 5


class TestXAITypes:
    """Test xAI type definitions."""

    def test_model_ids(self):
        """Test model ID enumeration."""
        assert XAIChatModelId.GROK_4.value == "grok-4"
        assert XAIChatModelId.GROK_3_MINI.value == "grok-3-mini"
        assert XAIChatModelId.GROK_2_VISION.value == "grok-2-vision"

    def test_search_mode(self):
        """Test search mode enumeration."""
        assert SearchMode.OFF.value == "off"
        assert SearchMode.AUTO.value == "auto"
        assert SearchMode.ON.value == "on"

    def test_reasoning_effort(self):
        """Test reasoning effort enumeration."""
        assert ReasoningEffort.LOW.value == "low"
        assert ReasoningEffort.HIGH.value == "high"

    def test_provider_options_validation(self):
        """Test provider options validation."""
        from ai_sdk.providers.xai.types import XAIProviderOptions, SearchParameters
        
        # Valid options
        options = XAIProviderOptions(
            reasoning_effort=ReasoningEffort.HIGH,
            search_parameters=SearchParameters(
                mode=SearchMode.ON,
                max_search_results=10
            )
        )
        
        assert options.reasoning_effort == ReasoningEffort.HIGH
        assert options.search_parameters.mode == SearchMode.ON
        assert options.search_parameters.max_search_results == 10


@pytest.mark.integration
class TestXAIIntegration:
    """Integration tests for xAI provider (requires API key)."""

    @pytest.fixture
    def provider(self):
        """Create xAI provider for integration tests."""
        import os
        api_key = os.getenv("XAI_API_KEY")
        if not api_key:
            pytest.skip("XAI_API_KEY environment variable not set")
        return XAIProvider(api_key=api_key)

    @pytest.mark.asyncio
    async def test_basic_generation(self, provider):
        """Test basic text generation."""
        model = provider.grok_3_mini()
        
        from ai_sdk.core.generate_text import GenerateTextOptions, Message
        
        messages = [Message(role="user", content="Say hello in exactly 5 words")]
        options = GenerateTextOptions(max_tokens=20)
        
        result = await model.generate_text(messages, options)
        
        assert isinstance(result.text, str)
        assert len(result.text) > 0
        assert result.finish_reason in ["stop", "length"]
        assert result.usage["prompt_tokens"] > 0
        assert result.usage["completion_tokens"] > 0

    @pytest.mark.asyncio
    async def test_reasoning_model(self, provider):
        """Test reasoning capabilities."""
        model = provider.grok_3_mini()
        
        from ai_sdk.core.generate_text import GenerateTextOptions, Message
        
        messages = [Message(role="user", content="What is 2+2? Show your reasoning.")]
        options = GenerateTextOptions(
            max_tokens=100,
            provider_options={"reasoning_effort": "high"}
        )
        
        result = await model.generate_text(messages, options)
        
        assert isinstance(result.text, str)
        assert "4" in result.text
        
        # Check for reasoning content
        has_reasoning = any(
            hasattr(content, 'type') and content.type == 'reasoning' 
            for content in result.content
        )
        # Note: Reasoning content may not always be present depending on the query


if __name__ == "__main__":
    pytest.main([__file__, "-v"])