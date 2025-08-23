"""Tests for the registry system."""

import pytest
from unittest.mock import MagicMock

from ai_sdk.registry import (
    create_provider_registry,
    custom_provider,
    NoSuchProviderError,
    NoSuchModelError
)
from ai_sdk.providers.base import Provider, LanguageModel, EmbeddingModel
from ai_sdk.middleware.base import SimpleMiddleware


class MockLanguageModel:
    """Mock language model for testing."""
    
    def __init__(self, model_id: str = "test-model"):
        self.provider_id = "test"
        self.model_id = model_id


class MockEmbeddingModel:
    """Mock embedding model for testing."""
    
    def __init__(self, model_id: str = "test-embedding"):
        self.provider_id = "test"
        self.model_id = model_id


class MockProvider:
    """Mock provider for testing."""
    
    def __init__(self, provider_id: str = "test"):
        self.provider_id = provider_id
        self.provider_name = f"Test Provider ({provider_id})"
        self._language_models = {}
        self._embedding_models = {}
    
    def add_language_model(self, model_id: str, model: LanguageModel):
        """Add a language model to this mock provider."""
        self._language_models[model_id] = model
    
    def add_embedding_model(self, model_id: str, model: EmbeddingModel):
        """Add an embedding model to this mock provider."""
        self._embedding_models[model_id] = model
    
    def language_model(self, model_id: str) -> LanguageModel:
        """Get a language model by ID."""
        return self._language_models.get(model_id)
    
    def embedding_model(self, model_id: str) -> EmbeddingModel:
        """Get an embedding model by ID."""
        return self._embedding_models.get(model_id)
    
    def image_model(self, model_id: str):
        """Mock image model method."""
        return None
    
    def speech_model(self, model_id: str):
        """Mock speech model method."""
        return None
    
    def transcription_model(self, model_id: str):
        """Mock transcription model method."""
        return None


@pytest.fixture
def mock_openai_provider():
    """Mock OpenAI provider fixture."""
    provider = MockProvider("openai")
    provider.add_language_model("gpt-4", MockLanguageModel("gpt-4"))
    provider.add_language_model("gpt-3.5-turbo", MockLanguageModel("gpt-3.5-turbo"))
    provider.add_embedding_model("text-embedding-3-small", MockEmbeddingModel("text-embedding-3-small"))
    return provider


@pytest.fixture
def mock_anthropic_provider():
    """Mock Anthropic provider fixture."""
    provider = MockProvider("anthropic")
    provider.add_language_model("claude-3-sonnet", MockLanguageModel("claude-3-sonnet"))
    provider.add_language_model("claude-3-haiku", MockLanguageModel("claude-3-haiku"))
    return provider


def test_create_provider_registry(mock_openai_provider, mock_anthropic_provider):
    """Test creating a provider registry."""
    registry = create_provider_registry({
        "openai": mock_openai_provider,
        "anthropic": mock_anthropic_provider
    })
    
    assert registry is not None
    assert hasattr(registry, 'language_model')
    assert hasattr(registry, 'embedding_model')


def test_registry_language_model_access(mock_openai_provider, mock_anthropic_provider):
    """Test accessing language models through registry."""
    registry = create_provider_registry({
        "openai": mock_openai_provider,
        "anthropic": mock_anthropic_provider
    })
    
    # Test successful access
    gpt4 = registry.language_model("openai:gpt-4")
    assert gpt4 is not None
    assert gpt4.model_id == "gpt-4"
    
    claude = registry.language_model("anthropic:claude-3-sonnet")
    assert claude is not None
    assert claude.model_id == "claude-3-sonnet"


def test_registry_embedding_model_access(mock_openai_provider):
    """Test accessing embedding models through registry."""
    registry = create_provider_registry({
        "openai": mock_openai_provider
    })
    
    embedding = registry.embedding_model("openai:text-embedding-3-small")
    assert embedding is not None
    assert embedding.model_id == "text-embedding-3-small"


def test_registry_custom_separator(mock_openai_provider):
    """Test registry with custom separator."""
    registry = create_provider_registry({
        "openai": mock_openai_provider
    }, separator="/")
    
    gpt4 = registry.language_model("openai/gpt-4")
    assert gpt4 is not None
    assert gpt4.model_id == "gpt-4"


def test_registry_no_such_provider():
    """Test error when provider doesn't exist."""
    registry = create_provider_registry({})
    
    with pytest.raises(NoSuchProviderError) as exc_info:
        registry.language_model("nonexistent:gpt-4")
    
    error = exc_info.value
    assert error.provider_id == "nonexistent"
    assert error.model_id == "nonexistent:gpt-4"
    assert error.model_type == "language_model"


def test_registry_no_such_model(mock_openai_provider):
    """Test error when model doesn't exist in provider."""
    registry = create_provider_registry({
        "openai": mock_openai_provider
    })
    
    with pytest.raises(NoSuchModelError) as exc_info:
        registry.language_model("openai:nonexistent-model")
    
    error = exc_info.value
    assert error.model_id == "openai:nonexistent-model"
    assert error.model_type == "language_model"
    assert error.provider_id == "openai"


def test_registry_invalid_model_id_format():
    """Test error when model ID format is invalid."""
    registry = create_provider_registry({})
    
    with pytest.raises(NoSuchModelError) as exc_info:
        registry.language_model("invalid-format")
    
    error = exc_info.value
    assert "must be in the format 'providerId:modelId'" in str(error)


def test_registry_with_middleware(mock_openai_provider):
    """Test registry with middleware applied to language models."""
    # Create middleware that adds a test property
    middleware = SimpleMiddleware()
    
    def mock_transform_params(*, params, type, model):
        # Mock parameter transformation
        return params
    
    middleware.transformParams = mock_transform_params
    
    # Mock wrap_language_model to return a wrapped model
    def mock_wrap(model, middleware):
        wrapped_model = MagicMock()
        wrapped_model.model_id = model.model_id + "_wrapped"
        wrapped_model.provider_id = model.provider_id
        return wrapped_model
    
    # Import and patch the wrap function
    import ai_sdk.registry.provider_registry as registry_module
    original_wrap = registry_module.wrap_language_model
    registry_module.wrap_language_model = mock_wrap
    
    try:
        registry = create_provider_registry({
            "openai": mock_openai_provider
        }, language_model_middleware=middleware)
        
        model = registry.language_model("openai:gpt-4")
        assert model.model_id == "gpt-4_wrapped"
    finally:
        # Restore original function
        registry_module.wrap_language_model = original_wrap


def test_custom_provider():
    """Test creating a custom provider."""
    gpt4 = MockLanguageModel("gpt-4")
    embedding = MockEmbeddingModel("text-embedding-3-small")
    
    provider = custom_provider(
        language_models={
            "smart": gpt4,
        },
        embedding_models={
            "default": embedding
        }
    )
    
    assert provider.language_model("smart") == gpt4
    assert provider.embedding_model("default") == embedding
    assert provider.language_model("unknown") is None


def test_custom_provider_with_fallback(mock_openai_provider):
    """Test custom provider with fallback."""
    custom_model = MockLanguageModel("custom-model")
    
    provider = custom_provider(
        language_models={
            "custom": custom_model
        },
        fallback_provider=mock_openai_provider
    )
    
    # Should get custom model
    assert provider.language_model("custom") == custom_model
    
    # Should fallback to OpenAI provider
    fallback_model = provider.language_model("gpt-4")
    assert fallback_model is not None
    assert fallback_model.model_id == "gpt-4"


def test_custom_provider_dynamic_management():
    """Test dynamic model management in custom provider."""
    provider = custom_provider()
    
    # Initially no models
    assert provider.list_models("language") == []
    
    # Add model
    model = MockLanguageModel("test")
    provider.add_language_model("test", model)
    assert provider.list_models("language") == ["test"]
    assert provider.language_model("test") == model
    
    # Remove model
    assert provider.remove_model("language", "test") is True
    assert provider.list_models("language") == []
    assert provider.language_model("test") is None
    
    # Try to remove non-existent model
    assert provider.remove_model("language", "nonexistent") is False


def test_custom_provider_multiple_model_types():
    """Test custom provider with multiple model types."""
    lang_model = MockLanguageModel("lang")
    emb_model = MockEmbeddingModel("emb")
    
    provider = custom_provider(
        language_models={"lang": lang_model},
        embedding_models={"emb": emb_model}
    )
    
    assert provider.language_model("lang") == lang_model
    assert provider.embedding_model("emb") == emb_model
    assert provider.image_model("anything") is None  # Not provided
    
    # Test listing models
    assert provider.list_models("language") == ["lang"]
    assert provider.list_models("embedding") == ["emb"]
    assert provider.list_models("image") == []


def test_registry_provider_management(mock_openai_provider):
    """Test dynamic provider management in registry."""
    registry = create_provider_registry({})
    
    # Initially no providers
    assert registry.list_providers() == []
    
    # Add provider
    registry.register_provider("openai", mock_openai_provider)
    assert "openai" in registry.list_providers()
    
    # Use provider
    model = registry.language_model("openai:gpt-4")
    assert model is not None
    
    # Remove provider
    registry.unregister_provider("openai")
    assert "openai" not in registry.list_providers()
    
    # Should now fail to access models
    with pytest.raises(NoSuchProviderError):
        registry.language_model("openai:gpt-4")