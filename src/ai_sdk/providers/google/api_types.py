"""Google Generative AI API types."""

from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel


# Google Generative AI Model IDs
GoogleModelId = Union[
    # Stable models
    Literal[
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest", 
        "gemini-1.5-flash-001",
        "gemini-1.5-flash-002",
        "gemini-1.5-flash-8b",
        "gemini-1.5-flash-8b-latest",
        "gemini-1.5-flash-8b-001", 
        "gemini-1.5-pro",
        "gemini-1.5-pro-latest",
        "gemini-1.5-pro-001",
        "gemini-1.5-pro-002",
        "gemini-2.0-flash",
        "gemini-2.0-flash-001",
        "gemini-2.0-flash-live-001",
        "gemini-2.0-flash-lite",
        "gemini-2.0-pro-exp-02-05",
        "gemini-2.0-flash-thinking-exp-01-21",
        "gemini-2.0-flash-exp",
        "gemini-2.5-pro",
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        # Experimental models
        "gemini-2.5-pro-exp-03-25",
        "gemini-2.5-flash-preview-04-17",
        "gemini-exp-1206",
        "gemma-3-12b-it",
        "gemma-3-27b-it",
    ],
    str,
]


class GoogleSafetySettings(BaseModel):
    """Google safety settings for content filtering."""
    
    category: Literal[
        "HARM_CATEGORY_UNSPECIFIED",
        "HARM_CATEGORY_HATE_SPEECH", 
        "HARM_CATEGORY_DANGEROUS_CONTENT",
        "HARM_CATEGORY_HARASSMENT",
        "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "HARM_CATEGORY_CIVIC_INTEGRITY",
    ]
    threshold: Literal[
        "HARM_BLOCK_THRESHOLD_UNSPECIFIED",
        "BLOCK_LOW_AND_ABOVE",
        "BLOCK_MEDIUM_AND_ABOVE", 
        "BLOCK_ONLY_HIGH",
        "BLOCK_NONE",
        "OFF",
    ]


class GoogleThinkingConfig(BaseModel):
    """Configuration for thinking models."""
    
    thinking_budget: Optional[int] = None
    include_thoughts: Optional[bool] = None


class GoogleProviderOptions(BaseModel):
    """Google-specific provider options."""
    
    response_modalities: Optional[List[Literal["TEXT", "IMAGE"]]] = None
    thinking_config: Optional[GoogleThinkingConfig] = None
    cached_content: Optional[str] = None
    structured_outputs: Optional[bool] = None
    safety_settings: Optional[List[GoogleSafetySettings]] = None
    threshold: Optional[
        Literal[
            "HARM_BLOCK_THRESHOLD_UNSPECIFIED",
            "BLOCK_LOW_AND_ABOVE",
            "BLOCK_MEDIUM_AND_ABOVE",
            "BLOCK_ONLY_HIGH", 
            "BLOCK_NONE",
            "OFF",
        ]
    ] = None
    audio_timestamp: Optional[bool] = None
    labels: Optional[Dict[str, str]] = None


class GoogleContentPart(BaseModel):
    """A part of Google Generative AI content."""
    
    text: Optional[str] = None
    inline_data: Optional[Dict[str, Any]] = None
    file_data: Optional[Dict[str, Any]] = None
    thought: Optional[bool] = None  # Indicates if this is reasoning content
    thought_signature: Optional[str] = None  # Signature for reasoning blocks


class GoogleContent(BaseModel):
    """Google Generative AI content structure."""
    
    role: Literal["user", "model"]
    parts: List[GoogleContentPart]


class GoogleGenerationConfig(BaseModel):
    """Google generation configuration."""
    
    candidate_count: Optional[int] = None
    stop_sequences: Optional[List[str]] = None
    max_output_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    response_mime_type: Optional[str] = None
    response_schema: Optional[Dict[str, Any]] = None


class GoogleFunctionDeclaration(BaseModel):
    """Google function declaration for tool calling."""
    
    name: str
    description: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None


class GoogleTool(BaseModel):
    """Google tool definition."""
    
    function_declarations: List[GoogleFunctionDeclaration]


class GooglePromptRequest(BaseModel):
    """Google Generative AI prompt request."""
    
    contents: List[GoogleContent]
    system_instruction: Optional[Dict[str, List[Dict[str, str]]]] = None
    tools: Optional[List[GoogleTool]] = None
    tool_config: Optional[Dict[str, Any]] = None
    safety_settings: Optional[List[GoogleSafetySettings]] = None
    generation_config: Optional[GoogleGenerationConfig] = None


class GoogleUsageMetadata(BaseModel):
    """Google usage metadata."""
    
    prompt_token_count: int = 0
    candidates_token_count: int = 0
    total_token_count: int = 0
    cached_content_token_count: Optional[int] = None
    thoughts_token_count: Optional[int] = None  # Reasoning tokens for Gemini models


class GoogleCandidate(BaseModel):
    """Google response candidate."""
    
    content: GoogleContent
    finish_reason: Optional[str] = None
    index: Optional[int] = None
    safety_ratings: Optional[List[Dict[str, Any]]] = None
    

class GoogleResponse(BaseModel):
    """Google Generative AI response."""
    
    candidates: List[GoogleCandidate]
    usage_metadata: Optional[GoogleUsageMetadata] = None
    model_version: Optional[str] = None


class GoogleStreamResponse(BaseModel):
    """Google streaming response chunk."""
    
    candidates: Optional[List[GoogleCandidate]] = None
    usage_metadata: Optional[GoogleUsageMetadata] = None
    model_version: Optional[str] = None


class GoogleErrorDetail(BaseModel):
    """Google API error detail."""
    
    type: str
    reason: str
    domain: str
    metadata: Optional[Dict[str, Any]] = None


class GoogleError(BaseModel):
    """Google API error."""
    
    code: int
    message: str
    status: str
    details: Optional[List[GoogleErrorDetail]] = None


class GoogleErrorResponse(BaseModel):
    """Google API error response."""
    
    error: GoogleError