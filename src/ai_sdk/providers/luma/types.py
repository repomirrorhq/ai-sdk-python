"""
Type definitions for Luma AI Provider.
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


# Luma Image Model IDs
LumaImageModelId = Literal["photon-1", "photon-flash-1"]


class LumaProviderSettings(BaseModel):
    """Settings for configuring the Luma AI provider."""
    
    api_key: Optional[str] = Field(
        default=None,
        description="Luma API key. If not provided, uses LUMA_API_KEY environment variable."
    )
    base_url: str = Field(
        default="https://api.lumalabs.ai",
        description="Base URL for Luma API calls."
    )
    headers: Optional[dict[str, str]] = Field(
        default=None,
        description="Additional headers to include in API requests."
    )
    timeout: float = Field(
        default=120.0,
        description="Request timeout in seconds."
    )
    max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts for failed requests."
    )


class LumaImageSettings(BaseModel):
    """Configuration settings for Luma image generation polling."""
    
    poll_interval_millis: Optional[int] = Field(
        default=500,
        description="Polling interval in milliseconds (default 500). Controls how frequently the API is checked for completed images."
    )
    max_poll_attempts: Optional[int] = Field(
        default=120,
        description="Maximum number of polling attempts (default 120). Limits how long to wait for results before timing out."
    )


class LumaImageOptions(BaseModel):
    """Options for Luma image generation requests."""
    
    aspect_ratio: Optional[str] = Field(
        default=None,
        description="Aspect ratio for the generated image (e.g., '16:9', '1:1', '4:3')"
    )
    poll_interval_millis: Optional[int] = Field(
        default=None,
        description="Override the polling interval for this specific request"
    )
    max_poll_attempts: Optional[int] = Field(
        default=None,
        description="Override the maximum polling attempts for this specific request"
    )


# API Response Types
class LumaGenerationResponse(BaseModel):
    """Response from Luma generation API."""
    id: str
    state: Literal["queued", "dreaming", "completed", "failed"]
    failure_reason: Optional[str] = None
    assets: Optional["LumaAssets"] = None


class LumaAssets(BaseModel):
    """Assets returned by Luma generation."""
    image: Optional[str] = None  # URL of the generated image


class LumaErrorDetail(BaseModel):
    """Error detail from Luma API."""
    type: str
    loc: list[str]
    msg: str
    input: str
    ctx: Optional[dict] = None


class LumaError(BaseModel):
    """Error response from Luma API."""
    detail: list[LumaErrorDetail]


# Update forward references
LumaGenerationResponse.model_rebuild()