"""
Gateway Provider for Vercel AI Gateway

This provider integrates with Vercel's AI Gateway service for model routing,
load balancing, caching, and analytics across multiple AI providers.
"""

from .provider import GatewayProvider, create_gateway_provider, gateway
from .types import (
    GatewayProviderSettings,
    GatewayLanguageModelEntry, 
    GatewayFetchMetadataResponse,
    GatewayModelId,
    GatewayEmbeddingModelId
)
from .errors import (
    GatewayError,
    GatewayAuthenticationError,
    GatewayInvalidRequestError,
    GatewayRateLimitError,
    GatewayModelNotFoundError,
    GatewayInternalServerError,
    GatewayResponseError,
)

__all__ = [
    "GatewayProvider",
    "create_gateway_provider",
    "gateway",
    "GatewayProviderSettings",
    "GatewayLanguageModelEntry",
    "GatewayFetchMetadataResponse", 
    "GatewayModelId",
    "GatewayEmbeddingModelId",
    "GatewayError",
    "GatewayAuthenticationError",
    "GatewayInvalidRequestError",
    "GatewayRateLimitError",
    "GatewayModelNotFoundError",
    "GatewayInternalServerError",
    "GatewayResponseError",
]