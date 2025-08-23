"""
Cohere provider types and model definitions.
"""

from typing import Literal, Union
from pydantic import BaseModel

# Cohere Chat Model IDs based on https://docs.cohere.com/docs/models
CohereChatModelId = Union[
    Literal[
        "command-a-03-2025",
        "command-r7b-12-2024", 
        "command-r-plus-04-2024",
        "command-r-plus",
        "command-r-08-2024", 
        "command-r-03-2024",
        "command-r",
        "command",
        "command-nightly",
        "command-light",
        "command-light-nightly",
    ],
    str,  # Allow custom model IDs
]

# Cohere Embedding Model IDs
CohereEmbeddingModelId = Union[
    Literal[
        "embed-english-v3.0",
        "embed-multilingual-v3.0",
        "embed-english-v2.0",
        "embed-multilingual-v2.0",
        "embed-english-light-v3.0",
        "embed-multilingual-light-v3.0",
        "embed-english-light-v2.0", 
        "embed-multilingual-light-v2.0",
    ],
    str,  # Allow custom model IDs
]


class CohereProviderSettings(BaseModel):
    """Configuration settings for Cohere provider."""
    
    base_url: str = "https://api.cohere.com/v2"
    """Base URL for Cohere API calls. Defaults to https://api.cohere.com/v2"""
    
    api_key: str | None = None
    """API key for Cohere. If not provided, will try COHERE_API_KEY environment variable."""
    
    headers: dict[str, str] | None = None
    """Additional headers to include in requests."""


class CohereFinishReason:
    """Cohere-specific finish reasons."""
    COMPLETE = "COMPLETE"
    ERROR_LIMIT = "ERROR_LIMIT"
    ERROR_TOXIC = "ERROR_TOXIC"
    ERROR = "ERROR"
    USER_CANCEL = "USER_CANCEL"
    MAX_TOKENS = "MAX_TOKENS"


class CohereResponseFormat(BaseModel):
    """Cohere response format configuration."""
    type: Literal["json_object"] 
    json_schema: dict | None = None


class CohereDocument(BaseModel):
    """Document for Cohere chat with documents."""
    id: str | None = None
    snippet: str
    title: str | None = None
    url: str | None = None


class CohereTool(BaseModel):
    """Cohere tool definition."""
    name: str
    description: str
    parameter_definitions: dict


class CohereToolChoice(BaseModel):
    """Cohere tool choice configuration."""
    type: Literal["auto", "any", "required"] = "auto"


class CohereMessage(BaseModel):
    """Cohere message format."""
    role: Literal["system", "user", "assistant", "tool"]
    content: str | list[dict] | None = None
    tool_calls: list[dict] | None = None
    tool_plan: str | None = None


class CohereChatRequest(BaseModel):
    """Cohere chat API request format."""
    model: str
    messages: list[CohereMessage]
    tools: list[CohereTool] | None = None
    tool_choice: CohereToolChoice | None = None
    documents: list[CohereDocument] | None = None
    max_tokens: int | None = None
    temperature: float | None = None
    p: float | None = None  # top_p
    k: int | None = None    # top_k
    seed: int | None = None
    stop_sequences: list[str] | None = None
    frequency_penalty: float | None = None
    presence_penalty: float | None = None
    response_format: CohereResponseFormat | None = None
    stream: bool = False


class CohereEmbeddingRequest(BaseModel):
    """Cohere embedding API request format."""
    model: str
    texts: list[str]
    input_type: Literal["search_document", "search_query", "classification", "clustering"] = "search_document"
    embedding_types: list[Literal["float", "int8", "uint8", "binary", "ubinary"]] = ["float"]
    truncate: Literal["none", "start", "end"] = "end"


class CohereBilledUnits(BaseModel):
    """Cohere billing information."""
    input_tokens: int = 0
    output_tokens: int = 0
    search_units: int = 0
    classifications: int = 0


class CohereUsage(BaseModel):
    """Cohere usage statistics."""
    billed_units: CohereBilledUnits
    tokens: dict | None = None


class CohereStreamEvent(BaseModel):
    """Cohere streaming event."""
    type: str
    index: int | None = None
    delta: dict | None = None
    finish_reason: str | None = None
    
    
class CohereCitations(BaseModel):
    """Cohere citations information."""
    start: int
    end: int 
    text: str
    document_ids: list[str]


class CohereSearchQuery(BaseModel):
    """Cohere search query."""
    text: str
    generation_id: str | None = None


class CohereSearchResults(BaseModel):
    """Cohere search results."""
    search_results: list[dict] | None = None
    documents: list[CohereDocument] | None = None


class CohereChatResponse(BaseModel):
    """Cohere chat response format."""
    id: str
    message: CohereMessage | None = None
    finish_reason: str
    usage: CohereUsage | None = None
    citations: list[CohereCitations] | None = None
    documents: list[CohereDocument] | None = None
    search_results: CohereSearchResults | None = None
    search_queries: list[CohereSearchQuery] | None = None
    is_search_required: bool | None = None


class CohereEmbeddingResponse(BaseModel):
    """Cohere embedding response format."""
    id: str
    embeddings: list[list[float]]
    texts: list[str]
    usage: CohereUsage | None = None