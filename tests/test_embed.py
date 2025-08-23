"""Tests for embedding functionality."""

import pytest
from unittest.mock import AsyncMock, MagicMock

from ai_sdk import embed, embed_many, cosine_similarity
from ai_sdk.core.embed import EmbedResult, EmbedManyResult, EmbeddingUsage
from ai_sdk.errors import InvalidArgumentError
from ai_sdk.providers.base import EmbeddingModel


class MockEmbeddingModel(EmbeddingModel):
    """Mock embedding model for testing."""
    
    def __init__(self, embeddings_response=None, usage_tokens=10):
        # Create a mock provider
        provider = MagicMock()
        provider.name = "mock"
        
        super().__init__(provider=provider, model_id="mock-embedding")
        
        # Set up response
        self.embeddings_response = embeddings_response or [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        self.usage_tokens = usage_tokens
    
    async def do_embed(self, *, values, headers=None, extra_body=None):
        """Mock embedding implementation."""
        # Return embeddings matching the number of values
        embeddings = self.embeddings_response[:len(values)]
        
        return {
            "embeddings": embeddings,
            "usage": {"tokens": self.usage_tokens},
            "provider_metadata": {"model": self.model_id},
            "response": {"headers": {}, "body": {}},
        }


@pytest.mark.asyncio
class TestEmbed:
    """Test single embedding functionality."""
    
    async def test_embed_single_text(self):
        """Test embedding a single text."""
        model = MockEmbeddingModel()
        
        result = await embed(model=model, value="test text")
        
        assert isinstance(result, EmbedResult)
        assert result.value == "test text"
        assert result.embedding == [0.1, 0.2, 0.3]
        assert result.usage.tokens == 10
        
    async def test_embed_with_none_value(self):
        """Test that embedding None raises error."""
        model = MockEmbeddingModel()
        
        with pytest.raises(InvalidArgumentError, match="Value cannot be None"):
            await embed(model=model, value=None)
    
    async def test_embed_with_headers_and_extra_body(self):
        """Test embedding with additional parameters."""
        model = MockEmbeddingModel()
        
        result = await embed(
            model=model,
            value="test",
            headers={"Custom-Header": "value"},
            extra_body={"param": "value"},
        )
        
        assert result.embedding == [0.1, 0.2, 0.3]


@pytest.mark.asyncio
class TestEmbedMany:
    """Test multiple embedding functionality."""
    
    async def test_embed_many_texts(self):
        """Test embedding multiple texts."""
        model = MockEmbeddingModel()
        
        texts = ["text one", "text two"]
        result = await embed_many(model=model, values=texts)
        
        assert isinstance(result, EmbedManyResult)
        assert result.values == texts
        assert len(result.embeddings) == 2
        assert result.embeddings[0] == [0.1, 0.2, 0.3]
        assert result.embeddings[1] == [0.4, 0.5, 0.6]
        assert result.usage.tokens == 10
    
    async def test_embed_many_empty_list(self):
        """Test that embedding empty list raises error."""
        model = MockEmbeddingModel()
        
        with pytest.raises(InvalidArgumentError, match="Values list cannot be empty"):
            await embed_many(model=model, values=[])
    
    async def test_embed_many_with_none_values(self):
        """Test that list with None values raises error."""
        model = MockEmbeddingModel()
        
        with pytest.raises(InvalidArgumentError, match="Values cannot contain None"):
            await embed_many(model=model, values=["text", None, "other text"])
    
    async def test_embed_many_batching(self):
        """Test that large batches are handled correctly."""
        # Create model with small batch size
        model = MockEmbeddingModel()
        model.max_embeddings_per_call = 2
        
        # Mock the do_embed method to track calls
        original_do_embed = model.do_embed
        call_count = 0
        
        async def tracking_do_embed(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            return await original_do_embed(*args, **kwargs)
        
        model.do_embed = tracking_do_embed
        
        # Embed 5 values (should require 3 batches: 2, 2, 1)
        values = ["text 1", "text 2", "text 3", "text 4", "text 5"]
        
        # Mock response to have enough embeddings
        model.embeddings_response = [
            [0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9], 
            [1.0, 1.1, 1.2], [1.3, 1.4, 1.5]
        ]
        
        result = await embed_many(model=model, values=values)
        
        assert len(result.embeddings) == 5
        assert result.values == values
        assert call_count >= 3  # Should have made at least 3 calls


class TestCosineSimilarity:
    """Test cosine similarity utility function."""
    
    def test_cosine_similarity_identical_vectors(self):
        """Test cosine similarity of identical vectors."""
        vector = [1.0, 2.0, 3.0]
        similarity = cosine_similarity(vector, vector)
        assert abs(similarity - 1.0) < 1e-6
    
    def test_cosine_similarity_orthogonal_vectors(self):
        """Test cosine similarity of orthogonal vectors."""
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [0.0, 1.0, 0.0]
        similarity = cosine_similarity(vec1, vec2)
        assert abs(similarity - 0.0) < 1e-6
    
    def test_cosine_similarity_opposite_vectors(self):
        """Test cosine similarity of opposite vectors."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [-1.0, -2.0, -3.0]
        similarity = cosine_similarity(vec1, vec2)
        assert abs(similarity - (-1.0)) < 1e-6
    
    def test_cosine_similarity_different_lengths(self):
        """Test that different length vectors raise error."""
        vec1 = [1.0, 2.0, 3.0]
        vec2 = [1.0, 2.0]
        
        with pytest.raises(ValueError, match="Vector dimensions must match"):
            cosine_similarity(vec1, vec2)
    
    def test_cosine_similarity_empty_vectors(self):
        """Test that empty vectors raise error."""
        with pytest.raises(ValueError, match="Vectors cannot be empty"):
            cosine_similarity([], [])
    
    def test_cosine_similarity_zero_vectors(self):
        """Test cosine similarity with zero vectors."""
        vec1 = [0.0, 0.0, 0.0]
        vec2 = [1.0, 2.0, 3.0]
        similarity = cosine_similarity(vec1, vec2)
        assert similarity == 0.0


class TestEmbeddingUsage:
    """Test embedding usage tracking."""
    
    def test_embedding_usage_initialization(self):
        """Test that usage objects are created correctly."""
        usage = EmbeddingUsage(tokens=42)
        assert usage.tokens == 42


class TestEmbedResult:
    """Test embed result objects."""
    
    def test_embed_result_initialization(self):
        """Test that result objects are created correctly."""
        embedding = [0.1, 0.2, 0.3]
        usage = EmbeddingUsage(tokens=10)
        
        result = EmbedResult(
            value="test text",
            embedding=embedding,
            usage=usage,
        )
        
        assert result.value == "test text"
        assert result.embedding == embedding
        assert result.usage == usage
        assert result.provider_metadata is None
        assert result.response is None


class TestEmbedManyResult:
    """Test embed many result objects."""
    
    def test_embed_many_result_initialization(self):
        """Test that result objects are created correctly."""
        values = ["text 1", "text 2"]
        embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        usage = EmbeddingUsage(tokens=20)
        
        result = EmbedManyResult(
            values=values,
            embeddings=embeddings,
            usage=usage,
        )
        
        assert result.values == values
        assert result.embeddings == embeddings
        assert result.usage == usage
        assert result.provider_metadata is None
        assert result.response is None