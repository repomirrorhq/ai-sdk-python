"""Tests for FastAPI integration with AI SDK Python."""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, List

# Test FastAPI availability
try:
    from fastapi import FastAPI
    from fastapi.testclient import TestClient
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from ai_sdk.integrations.fastapi import (
    AIFastAPI, 
    AIFastAPIMiddleware,
    fastapi_ai_middleware,
    streaming_chat_endpoint,
    websocket_chat_endpoint
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


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
class TestAIFastAPIMiddleware:
    """Test AI FastAPI middleware."""
    
    def test_middleware_creation(self):
        """Test creating AI FastAPI middleware."""
        app = FastAPI()
        provider = MockLanguageModel()
        
        # Should not raise an error
        middleware = AIFastAPIMiddleware(app, provider)
        assert middleware.default_provider == provider
    
    def test_middleware_without_fastapi_raises_error(self):
        """Test that middleware raises error when FastAPI not available."""
        with patch('ai_sdk.integrations.fastapi.FASTAPI_AVAILABLE', False):
            with pytest.raises(ImportError, match="FastAPI is required"):
                from ai_sdk.integrations.fastapi import AIFastAPIMiddleware
                AIFastAPIMiddleware(None)


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
class TestAIFastAPI:
    """Test AIFastAPI class."""
    
    def test_aifastapi_creation(self):
        """Test creating AIFastAPI instance."""
        provider = MockLanguageModel()
        ai_app = AIFastAPI(default_provider=provider)
        
        assert ai_app.default_provider == provider
        assert isinstance(ai_app.app, FastAPI)
        assert ai_app.app.title == "AI SDK FastAPI App"
    
    def test_aifastapi_with_custom_app(self):
        """Test creating AIFastAPI with custom FastAPI app."""
        custom_app = FastAPI(title="Custom App")
        provider = MockLanguageModel()
        
        ai_app = AIFastAPI(app=custom_app, default_provider=provider)
        assert ai_app.app == custom_app
        assert ai_app.app.title == "Custom App"
    
    def test_chat_endpoint_decorator(self):
        """Test chat endpoint decorator."""
        ai_app = AIFastAPI()
        
        @ai_app.chat_endpoint("/test-chat")
        async def test_chat(model, messages):
            return f"Processed {len(messages)} messages"
        
        # Check that route was added
        routes = [route for route in ai_app.app.routes if hasattr(route, 'path')]
        chat_routes = [route for route in routes if route.path == "/test-chat"]
        assert len(chat_routes) == 1
    
    def test_streaming_chat_endpoint_decorator(self):
        """Test streaming chat endpoint decorator."""
        ai_app = AIFastAPI()
        
        @ai_app.streaming_chat_endpoint("/test-stream")
        async def test_stream(model, messages):
            for i in range(3):
                yield f"chunk {i} "
        
        # Check that route was added
        routes = [route for route in ai_app.app.routes if hasattr(route, 'path')]
        stream_routes = [route for route in routes if route.path == "/test-stream"]
        assert len(stream_routes) == 1
    
    def test_object_endpoint_decorator(self):
        """Test object endpoint decorator."""
        ai_app = AIFastAPI()
        
        # Create a simple JSON schema
        schema = jsonschema_schema({
            "type": "object",
            "properties": {"name": {"type": "string"}},
            "required": ["name"]
        })
        
        @ai_app.object_endpoint("/test-object", schema=schema)
        async def test_object(model, prompt, schema):
            return {"name": "Test Object"}
        
        # Check that route was added
        routes = [route for route in ai_app.app.routes if hasattr(route, 'path')]
        object_routes = [route for route in routes if route.path == "/test-object"]
        assert len(object_routes) == 1
    
    def test_websocket_chat_decorator(self):
        """Test WebSocket chat decorator."""
        ai_app = AIFastAPI()
        
        @ai_app.websocket_chat("/test-ws")
        async def test_websocket(websocket, model, messages):
            await websocket.send_json({"response": "test"})
        
        # Check that WebSocket route was added
        websocket_routes = [route for route in ai_app.app.routes 
                          if hasattr(route, 'path') and route.path == "/test-ws"]
        assert len(websocket_routes) == 1


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
class TestFastAPIIntegration:
    """Test complete FastAPI integration."""
    
    def setup_method(self):
        """Set up test client."""
        self.provider = MockLanguageModel()
        self.ai_app = AIFastAPI(default_provider=self.provider)
        self.client = TestClient(self.ai_app.app)
    
    def test_chat_endpoint_functionality(self):
        """Test actual chat endpoint functionality."""
        @self.ai_app.chat_endpoint("/chat")
        async def chat_handler(model, messages):
            return f"Received {len(messages)} messages from {model.provider_name}"
        
        response = self.client.post(
            "/chat",
            json={"messages": [{"role": "user", "content": "Hello"}]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "1 messages from mock" in data["response"]
    
    def test_chat_endpoint_with_system_prompt(self):
        """Test chat endpoint with system prompt."""
        @self.ai_app.chat_endpoint("/chat-system", system_prompt="You are helpful")
        async def chat_with_system(model, messages):
            # Check if system prompt was added
            system_messages = [m for m in messages if m.get("role") == "system"]
            return f"System messages: {len(system_messages)}"
        
        response = self.client.post(
            "/chat-system",
            json={"messages": [{"role": "user", "content": "Hello"}]}
        )
        
        assert response.status_code == 200
        # System prompt should have been added
        assert "System messages: 1" in response.json()["response"]
    
    def test_chat_endpoint_error_handling(self):
        """Test chat endpoint error handling."""
        @self.ai_app.chat_endpoint("/chat-error")
        async def chat_error(model, messages):
            raise ValueError("Test error")
        
        response = self.client.post(
            "/chat-error",
            json={"messages": [{"role": "user", "content": "Hello"}]}
        )
        
        assert response.status_code == 500
        assert "error" in response.json()
    
    def test_object_endpoint_functionality(self):
        """Test object endpoint functionality."""
        schema = jsonschema_schema({
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "value": {"type": "number"}
            },
            "required": ["name", "value"]
        })
        
        @self.ai_app.object_endpoint("/generate-object", schema=schema)
        async def object_handler(model, prompt, schema_obj):
            return {"name": "test", "value": 42}
        
        response = self.client.post(
            "/generate-object",
            json={"prompt": "Generate a test object"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "object" in data
        assert data["object"]["name"] == "test"
        assert data["object"]["value"] == 42
    
    def test_object_endpoint_missing_prompt(self):
        """Test object endpoint with missing prompt."""
        schema = jsonschema_schema({"type": "object", "properties": {}})
        
        @self.ai_app.object_endpoint("/generate-object-missing", schema=schema)
        async def object_handler(model, prompt, schema_obj):
            return {}
        
        response = self.client.post("/generate-object-missing", json={})
        
        assert response.status_code == 400
        assert "Prompt is required" in response.json()["detail"]


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available") 
class TestStandaloneFunctions:
    """Test standalone FastAPI utility functions."""
    
    def test_fastapi_ai_middleware_function(self):
        """Test fastapi_ai_middleware utility function."""
        app = FastAPI()
        provider = MockLanguageModel()
        
        # Should not raise an error
        fastapi_ai_middleware(app, provider)
        
        # Middleware should have been added
        assert len(app.user_middleware) > 0
    
    @pytest.mark.asyncio
    async def test_streaming_chat_endpoint_function(self):
        """Test streaming_chat_endpoint utility function."""
        messages = [{"role": "user", "content": "Hello"}]
        model = MockLanguageModel()
        
        response = await streaming_chat_endpoint(messages, model)
        
        # Should return a StreamingResponse
        assert hasattr(response, 'media_type')
        assert response.media_type == "text/event-stream"
    
    def test_streaming_chat_endpoint_without_fastapi_raises_error(self):
        """Test streaming endpoint raises error when FastAPI not available."""
        with patch('ai_sdk.integrations.fastapi.FASTAPI_AVAILABLE', False):
            with pytest.raises(ImportError, match="FastAPI is required"):
                asyncio.run(streaming_chat_endpoint([], MockLanguageModel()))
    
    def test_websocket_chat_endpoint_without_fastapi_raises_error(self):
        """Test WebSocket endpoint raises error when FastAPI not available."""
        with patch('ai_sdk.integrations.fastapi.FASTAPI_AVAILABLE', False):
            with pytest.raises(ImportError, match="FastAPI is required"):
                asyncio.run(websocket_chat_endpoint(None, MockLanguageModel(), []))


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
class TestWebSocketIntegration:
    """Test WebSocket integration."""
    
    def test_websocket_chat_endpoint(self):
        """Test WebSocket chat endpoint setup."""
        ai_app = AIFastAPI()
        
        @ai_app.websocket_chat("/ws/test")
        async def ws_handler(websocket, model, messages):
            await websocket.send_json({"test": "response"})
        
        # Check WebSocket route exists
        ws_routes = [route for route in ai_app.app.routes 
                    if hasattr(route, 'path') and route.path == "/ws/test"]
        assert len(ws_routes) == 1


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
class TestErrorHandling:
    """Test error handling in FastAPI integration."""
    
    def test_no_provider_configured_error(self):
        """Test error when no provider is configured."""
        ai_app = AIFastAPI()  # No default provider
        
        @ai_app.chat_endpoint("/no-provider")
        async def no_provider_handler(model, messages):
            return "This shouldn't work"
        
        client = TestClient(ai_app.app)
        response = client.post(
            "/no-provider",
            json={"messages": [{"role": "user", "content": "Hello"}]}
        )
        
        assert response.status_code == 500
        assert "No AI provider configured" in response.json()["detail"]
    
    def test_invalid_json_handling(self):
        """Test handling of invalid JSON requests."""
        ai_app = AIFastAPI(default_provider=MockLanguageModel())
        
        @ai_app.chat_endpoint("/invalid-json")
        async def json_handler(model, messages):
            return "Valid response"
        
        client = TestClient(ai_app.app)
        
        # Send invalid JSON
        response = client.post(
            "/invalid-json",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        # Should return 422 for invalid JSON
        assert response.status_code == 422


@pytest.mark.skipif(not FASTAPI_AVAILABLE, reason="FastAPI not available")
class TestPerformance:
    """Test performance aspects of FastAPI integration."""
    
    def test_multiple_concurrent_requests(self):
        """Test handling multiple concurrent requests."""
        import threading
        import time
        
        ai_app = AIFastAPI(default_provider=MockLanguageModel())
        
        @ai_app.chat_endpoint("/concurrent")
        async def concurrent_handler(model, messages):
            # Simulate some processing time
            await asyncio.sleep(0.1)
            return f"Processed {len(messages)} messages"
        
        client = TestClient(ai_app.app)
        
        def make_request():
            return client.post(
                "/concurrent",
                json={"messages": [{"role": "user", "content": "Hello"}]}
            )
        
        # Make multiple concurrent requests
        threads = []
        results = []
        
        start_time = time.time()
        
        for _ in range(5):
            thread = threading.Thread(target=lambda: results.append(make_request()))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        
        # All requests should succeed
        assert len(results) == 5
        for result in results:
            if result is not None:  # Some results might be None due to threading
                assert result.status_code == 200
        
        # Should complete in reasonable time (less than 1 second for concurrent execution)
        assert end_time - start_time < 1.0