"""Types and constants for Google Vertex AI provider."""

from typing import Literal, Union

# Google Vertex AI model identifiers based on the TypeScript implementation
GoogleVertexModelId = Union[
    # Stable models
    Literal["gemini-2.0-flash-001"],
    Literal["gemini-1.5-flash"],
    Literal["gemini-1.5-flash-001"],
    Literal["gemini-1.5-flash-002"],
    Literal["gemini-1.5-pro"],
    Literal["gemini-1.5-pro-001"], 
    Literal["gemini-1.5-pro-002"],
    Literal["gemini-1.0-pro-001"],
    Literal["gemini-1.0-pro-vision-001"],
    Literal["gemini-1.0-pro"],
    Literal["gemini-1.0-pro-001"],
    Literal["gemini-1.0-pro-002"],
    # Preview models
    Literal["gemini-2.0-flash-lite-preview-02-05"],
    # Experimental models
    Literal["gemini-2.0-pro-exp-02-05"],
    Literal["gemini-2.0-flash-exp"],
    str,  # Allow custom model IDs
]

# Google Vertex AI embedding model identifiers
GoogleVertexEmbeddingModelId = Union[
    Literal["text-embedding-004"],
    Literal["text-embedding-005"],
    Literal["text-multilingual-embedding-002"],
    Literal["textembedding-gecko"],
    Literal["textembedding-gecko-001"],
    Literal["textembedding-gecko-002"],
    Literal["textembedding-gecko-003"],
    Literal["textembedding-gecko-multilingual-001"],
    str,  # Allow custom model IDs
]

# Google Vertex AI image model identifiers
GoogleVertexImageModelId = Union[
    Literal["imagen-3.0-generate-001"],
    Literal["imagen-3.0-capability-001"],
    Literal["imagegeneration-005"], 
    str,  # Allow custom model IDs
]

# Embedding task types
EmbeddingTaskType = Union[
    Literal["RETRIEVAL_QUERY"],
    Literal["RETRIEVAL_DOCUMENT"],
    Literal["SEMANTIC_SIMILARITY"],
    Literal["CLASSIFICATION"],
    Literal["CLUSTERING"],
    Literal["QUESTION_ANSWERING"],
    Literal["FACT_VERIFICATION"],
    str,
]