"""Type definitions for Mistral AI provider."""

from typing import Literal, Union, Optional
from pydantic import BaseModel


# Mistral Chat Model IDs based on their official documentation
MistralChatModelId = Literal[
    # Premier models
    "ministral-3b-latest",
    "ministral-8b-latest", 
    "mistral-large-latest",
    "mistral-medium-latest",
    "mistral-medium-2508",
    "mistral-medium-2505",
    "mistral-small-latest",
    "pixtral-large-latest",
    # Reasoning models
    "magistral-small-2507",
    "magistral-medium-2507",
    "magistral-small-2506",
    "magistral-medium-2506",
    # Free models
    "pixtral-12b-2409",
    # Legacy open source models
    "open-mistral-7b",
    "open-mixtral-8x7b", 
    "open-mixtral-8x22b",
]

# Mistral Embedding Model IDs
MistralEmbeddingModelId = Literal[
    "mistral-embed",
]


class MistralLanguageModelOptions(BaseModel):
    """Provider-specific options for Mistral language models."""
    
    # Whether to inject a safety prompt before all conversations
    safe_prompt: Optional[bool] = None
    
    # Document processing limits
    document_image_limit: Optional[int] = None
    document_page_limit: Optional[int] = None
    
    # Structured output options
    structured_outputs: Optional[bool] = None
    strict_json_schema: Optional[bool] = None


class MistralEmbeddingOptions(BaseModel):
    """Provider-specific options for Mistral embedding models."""
    
    # Encoding format for embeddings
    encoding_format: Optional[Literal["float", "base64"]] = None