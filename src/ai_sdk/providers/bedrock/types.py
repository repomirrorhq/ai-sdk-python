"""Type definitions for Amazon Bedrock provider."""

from typing import Literal, Union, Optional, Dict, Any, List
from pydantic import BaseModel, Field


# Bedrock Chat Model IDs
BedrockChatModelId = Literal[
    # Anthropic Claude models
    "anthropic.claude-3-5-sonnet-20241022-v2:0",
    "anthropic.claude-3-5-sonnet-20240620-v1:0",
    "anthropic.claude-3-5-haiku-20241022-v1:0",
    "anthropic.claude-3-haiku-20240307-v1:0",
    "anthropic.claude-3-opus-20240229-v1:0",
    "anthropic.claude-3-sonnet-20240229-v1:0",
    # Amazon Titan models
    "amazon.titan-text-premier-v1:0",
    "amazon.titan-text-express-v1:0",
    "amazon.titan-text-lite-v1:0",
    # Meta Llama models
    "meta.llama2-13b-chat-v1:0",
    "meta.llama2-70b-chat-v1:0",
    "meta.llama3-8b-instruct-v1:0",
    "meta.llama3-70b-instruct-v1:0",
    "meta.llama3-1-8b-instruct-v1:0",
    "meta.llama3-1-70b-instruct-v1:0",
    "meta.llama3-1-405b-instruct-v1:0",
    # Cohere Command models
    "cohere.command-text-v14:0",
    "cohere.command-light-text-v14:0",
    "cohere.command-r-v1:0",
    "cohere.command-r-plus-v1:0",
    # AI21 Jurassic models
    "ai21.j2-mid-v1:0",
    "ai21.j2-ultra-v1:0",
    "ai21.jamba-instruct-v1:0",
    # Mistral models
    "mistral.mistral-7b-instruct-v0:2",
    "mistral.mixtral-8x7b-instruct-v0:1",
    "mistral.mistral-large-2402-v1:0",
    "mistral.mistral-large-2407-v1:0",
    # Nova models
    "us.amazon.nova-micro-v1:0",
    "us.amazon.nova-lite-v1:0",
    "us.amazon.nova-pro-v1:0",
]

# Bedrock Embedding Model IDs
BedrockEmbeddingModelId = Literal[
    # Amazon Titan embeddings
    "amazon.titan-embed-text-v1",
    "amazon.titan-embed-text-v2:0",
    # Cohere embeddings
    "cohere.embed-english-v3:0",
    "cohere.embed-multilingual-v3:0",
]

# Bedrock Image Model IDs  
BedrockImageModelId = Literal[
    # Amazon Titan image
    "amazon.titan-image-generator-v1",
    "amazon.titan-image-generator-v2:0",
    # Stability AI
    "stability.stable-diffusion-xl-v1:0",
    "stability.stable-image-ultra-v1:0",
    "stability.stable-image-core-v1:0",
    # Nova image models
    "us.amazon.nova-canvas-v1:0",
]


class BedrockCredentials(BaseModel):
    """AWS credentials for Bedrock API access."""
    region: str
    access_key_id: str = Field(..., alias="accessKeyId")
    secret_access_key: str = Field(..., alias="secretAccessKey")  
    session_token: Optional[str] = Field(None, alias="sessionToken")


class BedrockStopReason(BaseModel):
    """Bedrock stop reason mapping."""
    type: Literal["end_turn", "tool_use", "max_tokens", "stop_sequence", "content_filter"]


class BedrockMessage(BaseModel):
    """Bedrock message format."""
    role: Literal["user", "assistant"]
    content: List[Dict[str, Any]]


class BedrockConverseInput(BaseModel):
    """Input format for Bedrock Converse API."""
    modelId: str
    messages: List[BedrockMessage]
    system: Optional[List[Dict[str, Any]]] = None
    inferenceConfig: Optional[Dict[str, Any]] = None
    toolConfig: Optional[Dict[str, Any]] = None
    additionalModelRequestFields: Optional[Dict[str, Any]] = None
    additionalModelResponseFieldPaths: Optional[List[str]] = None


class BedrockOptions(BaseModel):
    """Provider-specific options for Bedrock models."""
    additional_model_request_fields: Optional[Dict[str, Any]] = None
    additional_model_response_field_paths: Optional[List[str]] = None


# Constants for stop reasons
BEDROCK_STOP_REASONS = [
    "end_turn",
    "tool_use", 
    "max_tokens",
    "stop_sequence",
    "content_filter",
]