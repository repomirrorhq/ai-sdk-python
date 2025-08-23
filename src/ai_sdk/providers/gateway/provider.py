"""
Gateway Provider implementation

This provider integrates with Vercel's AI Gateway service for model routing,
load balancing, caching, and analytics across multiple AI providers.
"""

import asyncio
import os
import time
from typing import Optional, Dict, Any, Callable, Awaitable

from ..base import BaseProvider
from .types import (
    GatewayProviderSettings,
    GatewayModelId,
    GatewayEmbeddingModelId,
    GatewayFetchMetadataResponse,
    GatewayAuthToken,
    GatewayConfig
)
from .errors import GatewayAuthenticationError, as_gateway_error
from .language_model import GatewayLanguageModel  
from .embedding_model import GatewayEmbeddingModel
from .fetch_metadata import GatewayFetchMetadata


AI_GATEWAY_PROTOCOL_VERSION = "0.0.1"


class GatewayProvider(BaseProvider):
    """
    Provider for Vercel AI Gateway service.
    
    Supports model routing, load balancing, caching, and analytics
    across multiple AI providers through the Gateway infrastructure.
    """
    
    def __init__(self, settings: Optional[GatewayProviderSettings] = None):
        """
        Initialize Gateway provider.
        
        Args:
            settings: Gateway provider configuration settings
        """
        self.settings = settings or GatewayProviderSettings()
        self._pending_metadata: Optional[Awaitable[GatewayFetchMetadataResponse]] = None
        self._metadata_cache: Optional[GatewayFetchMetadataResponse] = None
        self._last_fetch_time = 0.0
        
    @property
    def name(self) -> str:
        return "gateway"
    
    def __call__(self, model_id: GatewayModelId) -> GatewayLanguageModel:
        """Create a language model instance (callable interface)"""
        return self.language_model(model_id)
    
    def language_model(self, model_id: GatewayModelId, **kwargs) -> GatewayLanguageModel:
        """
        Create a language model instance.
        
        Args:
            model_id: Gateway model identifier
            **kwargs: Additional model configuration
            
        Returns:
            Gateway language model instance
        """
        return GatewayLanguageModel(
            model_id=model_id,
            config=self._create_config()
        )
    
    def text_embedding_model(self, model_id: GatewayEmbeddingModelId) -> GatewayEmbeddingModel:
        """
        Create a text embedding model instance.
        
        Args:
            model_id: Gateway embedding model identifier
            
        Returns:
            Gateway embedding model instance
        """
        return GatewayEmbeddingModel(
            model_id=model_id,
            config=self._create_config()
        )
    
    async def get_available_models(self) -> GatewayFetchMetadataResponse:
        """
        Fetch available models from Gateway with caching.
        
        Returns:
            Metadata about available models
        """
        current_time = time.time()
        cache_refresh_seconds = (self.settings.metadata_cache_refresh_millis or 300000) / 1000
        
        if not self._pending_metadata or current_time - self._last_fetch_time > cache_refresh_seconds:
            self._last_fetch_time = current_time
            
            fetch_metadata = GatewayFetchMetadata(self._create_config())
            
            async def fetch_and_cache():
                try:
                    metadata = await fetch_metadata.get_available_models()
                    self._metadata_cache = metadata
                    return metadata
                except Exception as error:
                    headers = await self._get_headers()
                    auth_method = self._parse_auth_method(headers)
                    raise as_gateway_error(error, auth_method)
            
            self._pending_metadata = fetch_and_cache()
        
        if self._metadata_cache:
            return self._metadata_cache
        
        return await self._pending_metadata
    
    def _create_config(self) -> GatewayConfig:
        """Create configuration for Gateway models"""
        return GatewayConfig(
            provider="gateway",
            base_url=self._get_base_url(),
            headers=self._get_headers,
            fetch=self.settings.fetch,
            o11y_headers=self._create_o11y_headers()
        )
    
    def _get_base_url(self) -> str:
        """Get the base URL, removing trailing slash"""
        base_url = self.settings.base_url or "https://ai-gateway.vercel.sh/v1/ai"
        return base_url.rstrip('/')
    
    async def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication"""
        auth = await self._get_gateway_auth_token()
        if not auth:
            raise GatewayAuthenticationError.create_contextual_error(
                api_key_provided=bool(self.settings.api_key),
                oidc_token_provided=False,  # TODO: Implement OIDC
                status_code=401
            )
        
        headers = {
            "Authorization": f"Bearer {auth.token}",
            "ai-gateway-protocol-version": AI_GATEWAY_PROTOCOL_VERSION,
            "ai-gateway-auth-method": auth.auth_method,
        }
        
        if self.settings.headers:
            headers.update(self.settings.headers)
        
        return headers
    
    async def _create_o11y_headers(self) -> Dict[str, str]:
        """Create observability headers for Vercel integration"""
        headers = {}
        
        # Vercel deployment information
        deployment_id = os.getenv("VERCEL_DEPLOYMENT_ID")
        if deployment_id:
            headers["ai-o11y-deployment-id"] = deployment_id
            
        environment = os.getenv("VERCEL_ENV")  
        if environment:
            headers["ai-o11y-environment"] = environment
            
        region = os.getenv("VERCEL_REGION")
        if region:
            headers["ai-o11y-region"] = region
        
        # TODO: Implement request ID tracking for Vercel
        # request_id = await get_vercel_request_id()
        # if request_id:
        #     headers["ai-o11y-request-id"] = request_id
        
        return headers
    
    async def _get_gateway_auth_token(self) -> Optional[GatewayAuthToken]:
        """Get authentication token for Gateway"""
        
        # Try API key first
        api_key = self.settings.api_key or os.getenv("AI_GATEWAY_API_KEY")
        if api_key:
            return GatewayAuthToken(
                token=api_key,
                auth_method="api-key"
            )
        
        # TODO: Implement OIDC token support
        # try:
        #     oidc_token = await get_vercel_oidc_token()
        #     return GatewayAuthToken(
        #         token=oidc_token,
        #         auth_method="oidc"
        #     )
        # except Exception:
        #     pass
        
        return None
    
    def _parse_auth_method(self, headers: Dict[str, str]) -> Optional[str]:
        """Parse authentication method from headers"""
        return headers.get("ai-gateway-auth-method")


def create_gateway_provider(settings: Optional[GatewayProviderSettings] = None) -> GatewayProvider:
    """
    Create a Gateway provider instance.
    
    Args:
        settings: Gateway provider configuration settings
        
    Returns:
        Gateway provider instance
    """
    return GatewayProvider(settings)


# Default gateway provider instance
gateway = create_gateway_provider()