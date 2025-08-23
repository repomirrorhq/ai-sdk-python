"""
Type definitions for Gateway Provider
"""

from typing import Dict, List, Optional, Union, Callable, Any, Awaitable
from pydantic import BaseModel, Field
from typing_extensions import TypeAlias
from .model_settings import GatewayModelId

# Type aliases
GatewayEmbeddingModelId: TypeAlias = str

# HTTP types  
FetchFunction: TypeAlias = Callable[..., Awaitable[Any]]


class GatewayProviderSettings(BaseModel):
    """Settings for configuring the Gateway Provider"""
    
    base_url: Optional[str] = Field(
        default="https://ai-gateway.vercel.sh/v1/ai",
        description="The base URL prefix for API calls"
    )
    
    api_key: Optional[str] = Field(
        default=None,
        description="API key sent using the Authorization header"
    )
    
    headers: Optional[Dict[str, str]] = Field(
        default_factory=dict,
        description="Custom headers to include in requests"
    )
    
    fetch: Optional[FetchFunction] = Field(
        default=None,
        description="Custom fetch implementation for testing/middleware"
    )
    
    metadata_cache_refresh_millis: Optional[int] = Field(
        default=300000,  # 5 minutes
        description="How frequently to refresh the metadata cache in milliseconds"
    )
    
    class Config:
        extra = "forbid"


class GatewayLanguageModelSpecification(BaseModel):
    """Language model specification returned by Gateway"""
    
    specification_version: str = Field(alias="specificationVersion")
    provider: str
    model_id: str = Field(alias="modelId")

    class Config:
        populate_by_name = True


class GatewayLanguageModelPricing(BaseModel):
    """Pricing information for a Gateway model"""
    
    input: str
    output: str


class GatewayLanguageModelEntry(BaseModel):
    """Model entry returned by Gateway metadata API"""
    
    id: str
    name: str
    description: Optional[str] = None
    pricing: Optional[GatewayLanguageModelPricing] = None
    specification: GatewayLanguageModelSpecification
    model_type: Optional[str] = Field(default=None, alias="modelType")
    
    class Config:
        populate_by_name = True


class GatewayFetchMetadataResponse(BaseModel):
    """Response from Gateway metadata fetch"""
    
    models: List[GatewayLanguageModelEntry]


class GatewayAuthToken(BaseModel):
    """Authentication token for Gateway"""
    
    token: str
    auth_method: str  # 'api-key' or 'oidc'


class GatewayConfig(BaseModel):
    """Internal configuration for Gateway models"""
    
    provider: str
    base_url: str
    headers: Callable[[], Awaitable[Dict[str, str]]]
    fetch: Optional[FetchFunction] = None
    o11y_headers: Callable[[], Awaitable[Dict[str, str]]]