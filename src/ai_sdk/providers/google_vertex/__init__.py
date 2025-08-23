"""Google Vertex AI provider for AI SDK Python."""

from .provider import GoogleVertexProvider, create_vertex
from .language_model import GoogleVertexLanguageModel
from .embedding_model import GoogleVertexEmbeddingModel
from .config import GoogleVertexAuth, GoogleVertexConfig
from .types import (
    GoogleVertexModelId,
    GoogleVertexEmbeddingModelId,
    GoogleVertexImageModelId,
    EmbeddingTaskType,
)

__all__ = [
    "GoogleVertexProvider",
    "create_vertex",
    "GoogleVertexLanguageModel",
    "GoogleVertexEmbeddingModel",
    "GoogleVertexAuth",
    "GoogleVertexConfig",
    "GoogleVertexModelId",
    "GoogleVertexEmbeddingModelId",
    "GoogleVertexImageModelId", 
    "EmbeddingTaskType",
]