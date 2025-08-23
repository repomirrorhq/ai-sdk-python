"""Tests for Flask integration with AI SDK Python."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List

# Test Flask availability
try:
    from flask import Flask, g
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False

from ai_sdk.integrations.flask import (
    AIFlask,
    ai_blueprint,
    streaming_response_wrapper,
    async_route,
    create_chat_app
)
from ai_sdk.providers.base import LanguageModel
from ai_sdk.schemas import jsonschema_schema


# Mock objects for testing
class MockLanguageModel:
    """Mock language model for testing."""
    def __init__(self):
        self.provider_name = "mock"
    
    async def generate(self, messages, **kwargs):
        return MagicMock(text="Mock response")


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
class TestAIFlask:
    """Test AIFlask class."""
    
    def test_aiflask_creation(self):
        """Test creating AIFlask instance."""
        provider = MockLanguageModel()
        ai_app = AIFlask(default_provider=provider)
        
        assert ai_app.default_provider == provider
        assert isinstance(ai_app.app, Flask)
    
    def test_aiflask_with_custom_app(self):
        """Test creating AIFlask with custom Flask app."""
        custom_app = Flask("custom_app")
        provider = MockLanguageModel()
        
        ai_app = AIFlask(app=custom_app, default_provider=provider)
        assert ai_app.app == custom_app
        assert ai_app.app.name == "custom_app"
    
    def test_aiflask_without_flask_raises_error(self):
        """Test that AIFlask raises error when Flask not available."""
        with patch('ai_sdk.integrations.flask.FLASK_AVAILABLE', False):
            with pytest.raises(ImportError, match="Flask is required"):
                from ai_sdk.integrations.flask import AIFlask
                AIFlask()
    
    def test_chat_route_decorator(self):
        """Test chat route decorator."""
        ai_app = AIFlask()
        
        @ai_app.chat_route("/test-chat")
        def test_chat():
            return {"response": "test"}
        
        # Check that route was added
        with ai_app.app.app_context():
            assert "/test-chat" in [rule.rule for rule in ai_app.app.url_map.iter_rules()]
    
    def test_streaming_route_decorator(self):
        """Test streaming route decorator."""
        ai_app = AIFlask()
        
        @ai_app.streaming_route("/test-stream")
        def test_stream():
            def generate():
                yield "test stream"
            return streaming_response_wrapper(generate)
        
        # Check that route was added
        assert "/test-stream" in [rule.rule for rule in ai_app.app.url_map.iter_rules()]
    
    def test_object_route_decorator(self):
        """Test object route decorator."""
        ai_app = AIFlask()
        
        # Create a simple JSON schema
        schema = jsonschema_schema({
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"]
        })
        
        @ai_app.object_route("/test-object", schema=schema)
        def test_object():
            return {"object": {"name": "test"}}
        
        # Check that route was added
        assert "/test-object" in [rule.rule for rule in ai_app.app.url_map.iter_rules()]


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
class TestFlaskBlueprints:
    """Test Flask blueprints with AI integration."""
    
    def test_ai_blueprint_creation(self):
        """Test creating AI blueprint."""
        provider = MockLanguageModel()
        bp = ai_blueprint("test_ai", __name__, default_provider=provider)
        
        assert bp.name == "test_ai"
        # Blueprint should have before_request function registered
        assert len(bp.before_request_funcs) > 0
    
    def test_ai_blueprint_without_flask_raises_error(self):
        """Test that ai_blueprint raises error when Flask not available."""
        with patch('ai_sdk.integrations.flask.FLASK_AVAILABLE', False):
            with pytest.raises(ImportError, match="Flask is required"):
                ai_blueprint("test", __name__)
    
    def test_blueprint_integration(self):
        """Test blueprint integration with Flask app."""
        app = Flask(__name__)
        provider = MockLanguageModel()
        bp = ai_blueprint("ai", __name__, default_provider=provider)
        
        @bp.route("/test")
        def test_route():
            return {"status": "ok"}
        
        app.register_blueprint(bp, url_prefix="/ai")
        
        with app.test_client() as client:
            response = client.get("/ai/test")
            assert response.status_code == 200


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
class TestFlaskIntegration:
    """Test complete Flask integration."""
    
    def setup_method(self):
        """Set up test client."""
        self.provider = MockLanguageModel()
        self.ai_app = AIFlask(default_provider=self.provider)
        self.client = self.ai_app.app.test_client()
    
    def test_chat_route_functionality(self):
        """Test actual chat route functionality."""
        @self.ai_app.chat_route("/chat")
        def chat_handler():
            from flask import request, g
            data = request.get_json()
            messages = data.get("messages", [])
            return {"response": f"Received {len(messages)} messages"}
        
        response = self.client.post(
            "/chat",
            json={"messages": [{"role": "user", "content": "Hello"}]},
            content_type="application/json"
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert "response" in data
        assert "Received 1 messages" in data["response"]
    
    def test_chat_route_with_system_prompt(self):
        """Test chat route with system prompt."""
        @self.ai_app.chat_route("/chat-system", system_prompt="You are helpful")
        def chat_with_system():
            from flask import request
            data = request.get_json()
            messages = data.get("messages", [])
            system_messages = [m for m in messages if m.get("role") == "system"]
            return {"system_messages_count": len(system_messages)}
        
        response = self.client.post(
            "/chat-system",
            json={"messages": [{"role": "user", "content": "Hello"}]},
            content_type="application/json"
        )
        
        assert response.status_code == 200
        # System prompt should have been added
        data = response.get_json()
        assert data["system_messages_count"] == 1
    
    def test_object_route_functionality(self):
        """Test object route functionality."""
        schema = jsonschema_schema({
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "value": {"type": "number"}
            },
            "required": ["name", "value"]
        })
        
        @self.ai_app.object_route("/generate-object", schema=schema)
        def object_handler():
            return {"object": {"name": "test", "value": 42}}
        
        response = self.client.post(
            "/generate-object",
            json={"prompt": "Generate a test object"},
            content_type="application/json"
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert "object" in data
        assert data["object"]["name"] == "test"
        assert data["object"]["value"] == 42
    
    def test_object_route_missing_prompt(self):
        """Test object route with missing prompt."""
        schema = jsonschema_schema({"type": "object", "properties": {}})
        
        @self.ai_app.object_route("/generate-object-missing", schema=schema)
        def object_handler():
            return {}
        
        response = self.client.post(
            "/generate-object-missing",
            json={},
            content_type="application/json"
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert "error" in data
        assert "Prompt is required" in data["error"]


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
class TestStreamingResponseWrapper:
    """Test streaming response wrapper."""
    
    def test_streaming_response_wrapper_with_generator(self):
        """Test streaming response wrapper with generator."""
        def test_generator():
            for i in range(3):
                yield f"chunk {i} "
        
        response = streaming_response_wrapper(test_generator)
        
        assert hasattr(response, 'mimetype')
        assert response.mimetype == "text/event-stream"
        assert "Cache-Control" in response.headers
        assert response.headers["Cache-Control"] == "no-cache"
    
    def test_streaming_response_wrapper_without_flask_raises_error(self):
        """Test streaming wrapper raises error when Flask not available."""
        with patch('ai_sdk.integrations.flask.FLASK_AVAILABLE', False):
            with pytest.raises(ImportError, match="Flask is required"):
                streaming_response_wrapper(lambda: None)
    
    def test_streaming_response_content(self):
        """Test streaming response content format."""
        def test_generator():
            yield "hello"
            yield "world"
        
        response = streaming_response_wrapper(test_generator)
        
        # Get response data
        data = b''.join(response.response).decode()
        
        # Should contain SSE formatted data
        assert "data:" in data
        assert "hello" in data
        assert "world" in data
        assert "[DONE]" in data


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
class TestAsyncRoute:
    """Test async route decorator."""
    
    def test_async_route_decorator(self):
        """Test async route decorator functionality."""
        app = Flask(__name__)
        
        @app.route("/async-test")
        @async_route
        async def async_handler():
            await asyncio.sleep(0.01)  # Simulate async work
            return {"status": "async_complete"}
        
        with app.test_client() as client:
            response = client.get("/async-test")
            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "async_complete"
    
    def test_async_route_with_sync_function(self):
        """Test async route decorator with sync function."""
        app = Flask(__name__)
        
        @app.route("/sync-test") 
        @async_route
        def sync_handler():
            return {"status": "sync_complete"}
        
        with app.test_client() as client:
            response = client.get("/sync-test")
            assert response.status_code == 200
            data = response.get_json()
            assert data["status"] == "sync_complete"


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
class TestCreateChatApp:
    """Test create_chat_app utility function."""
    
    def test_create_chat_app(self):
        """Test creating a chat app with utility function."""
        provider = MockLanguageModel()
        app = create_chat_app(provider, system_prompt="You are helpful")
        
        assert isinstance(app, Flask)
        
        # Test chat endpoint exists
        with app.test_client() as client:
            response = client.post(
                "/chat",
                json={"messages": [{"role": "user", "content": "Hello"}]},
                content_type="application/json"
            )
            assert response.status_code == 200
    
    def test_create_chat_app_without_flask_raises_error(self):
        """Test create_chat_app raises error when Flask not available."""
        with patch('ai_sdk.integrations.flask.FLASK_AVAILABLE', False):
            with pytest.raises(ImportError, match="Flask is required"):
                create_chat_app(MockLanguageModel())


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
class TestErrorHandling:
    """Test error handling in Flask integration."""
    
    def test_no_provider_configured_error(self):
        """Test error when no provider is configured."""
        ai_app = AIFlask()  # No default provider
        
        @ai_app.chat_route("/no-provider")
        def no_provider_handler():
            return {"response": "This shouldn't work"}
        
        response = ai_app.app.test_client().post(
            "/no-provider",
            json={"messages": [{"role": "user", "content": "Hello"}]},
            content_type="application/json"
        )
        
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data
        assert "No AI provider configured" in data["error"]
    
    def test_invalid_json_handling(self):
        """Test handling of invalid JSON requests."""
        ai_app = AIFlask(default_provider=MockLanguageModel())
        
        @ai_app.chat_route("/invalid-json")
        def json_handler():
            from flask import request
            data = request.get_json()
            return {"received": data}
        
        # Send invalid JSON
        response = ai_app.app.test_client().post(
            "/invalid-json",
            data="invalid json",
            content_type="application/json"
        )
        
        # Flask should handle this gracefully, request.get_json() returns None
        assert response.status_code == 200
        data = response.get_json()
        assert data["received"] is None
    
    def test_exception_in_route_handler(self):
        """Test exception handling in route handlers."""
        ai_app = AIFlask(default_provider=MockLanguageModel())
        
        @ai_app.chat_route("/error-route")
        def error_handler():
            raise ValueError("Test error")
        
        response = ai_app.app.test_client().post(
            "/error-route",
            json={"messages": [{"role": "user", "content": "Hello"}]},
            content_type="application/json"
        )
        
        assert response.status_code == 500
        data = response.get_json()
        assert "error" in data
        assert "Test error" in data["error"]


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
class TestContextAndState:
    """Test Flask context and state management."""
    
    def test_ai_provider_in_context(self):
        """Test AI provider availability in Flask context."""
        provider = MockLanguageModel()
        ai_app = AIFlask(default_provider=provider)
        
        @ai_app.chat_route("/context-test")
        def context_handler():
            from flask import g
            return {"provider_available": g.ai_provider is not None}
        
        response = ai_app.app.test_client().post(
            "/context-test",
            json={"messages": []},
            content_type="application/json"
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["provider_available"] is True
    
    def test_ai_sdk_utilities_in_context(self):
        """Test AI SDK utilities in Flask context."""
        ai_app = AIFlask()
        
        @ai_app.app.route("/utilities-test")
        def utilities_handler():
            from flask import g
            utilities = g.get('ai_sdk', {})
            return {"utilities_count": len(utilities)}
        
        response = ai_app.app.test_client().get("/utilities-test")
        
        assert response.status_code == 200
        data = response.get_json()
        assert data["utilities_count"] > 0  # Should have generate_text, etc.
    
    def test_headers_added_by_middleware(self):
        """Test that AI SDK headers are added to responses."""
        ai_app = AIFlask()
        
        @ai_app.app.route("/headers-test")
        def headers_handler():
            return {"status": "ok"}
        
        response = ai_app.app.test_client().get("/headers-test")
        
        assert response.status_code == 200
        assert "x-ai-sdk" in response.headers
        assert response.headers["x-ai-sdk"] == "python"


@pytest.mark.skipif(not FLASK_AVAILABLE, reason="Flask not available")
class TestPerformance:
    """Test performance aspects of Flask integration."""
    
    def test_multiple_sequential_requests(self):
        """Test handling multiple sequential requests."""
        import time
        
        ai_app = AIFlask(default_provider=MockLanguageModel())
        
        @ai_app.chat_route("/performance")
        def performance_handler():
            from flask import request
            data = request.get_json()
            messages = data.get("messages", [])
            return {"response": f"Processed {len(messages)} messages"}
        
        client = ai_app.app.test_client()
        
        start_time = time.time()
        
        # Make multiple sequential requests
        responses = []
        for i in range(5):
            response = client.post(
                "/performance",
                json={"messages": [{"role": "user", "content": f"Message {i}"}]},
                content_type="application/json"
            )
            responses.append(response)
        
        end_time = time.time()
        
        # All requests should succeed
        for response in responses:
            assert response.status_code == 200
        
        # Should complete in reasonable time
        assert end_time - start_time < 2.0  # Should be much faster than 2 seconds