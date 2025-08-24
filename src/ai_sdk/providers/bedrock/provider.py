"""Amazon Bedrock provider implementation."""

import os
from typing import Optional, Dict, Any, Callable, Awaitable, Union
from pydantic import BaseModel

import httpx

from ...providers.base import Provider, LanguageModel, EmbeddingModel, ImageModel
from ...utils.http import create_http_client
from .types import BedrockChatModelId, BedrockEmbeddingModelId, BedrockImageModelId, BedrockCredentials
from .auth import create_sigv4_fetch_function, create_api_key_fetch_function
from .language_model import BedrockLanguageModel


class BedrockProviderSettings(BaseModel):
    """Settings for Amazon Bedrock provider."""
    
    # Authentication options
    region: Optional[str] = None
    api_key: Optional[str] = None
    access_key_id: Optional[str] = None
    secret_access_key: Optional[str] = None
    session_token: Optional[str] = None
    
    # Custom settings
    base_url: Optional[str] = None
    headers: Optional[Dict[str, str]] = None
    
    # Custom credential provider
    credential_provider: Optional[Callable[[], Union[BedrockCredentials, Awaitable[BedrockCredentials]]]] = None
    
    # HTTP client settings
    timeout: Optional[int] = 60
    max_retries: Optional[int] = 3


class BedrockProvider(Provider):
    """Amazon Bedrock AI provider."""
    
    def __init__(self, settings: BedrockProviderSettings):
        self.settings = settings
        self._http_client = None
        self._fetch_fn = None
    
    @property
    def name(self) -> str:
        """Name of the provider."""
        return "bedrock"
        
    async def _get_http_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._http_client is None:
            self._http_client = create_http_client(
                timeout=self.settings.timeout,
                max_retries=self.settings.max_retries
            )
        return self._http_client
        
    async def _get_fetch_function(self):
        """Get or create fetch function with appropriate authentication."""
        if self._fetch_fn is None:
            http_client = await self._get_http_client()
            
            # Check for API key authentication first
            api_key = self.settings.api_key or os.getenv("AWS_BEARER_TOKEN_BEDROCK")
            
            if api_key and api_key.strip():
                # Use API key authentication
                self._fetch_fn = await create_api_key_fetch_function(api_key.strip(), http_client)
            else:
                # Use SigV4 authentication
                async def get_credentials() -> BedrockCredentials:
                    # Use custom credential provider if available
                    if self.settings.credential_provider:
                        try:
                            creds = self.settings.credential_provider()
                            if hasattr(creds, '__await__'):
                                creds = await creds
                            
                            # Get region
                            region = self.settings.region or os.getenv("AWS_REGION")
                            if not region:
                                raise ValueError("AWS region is required")
                                
                            return BedrockCredentials(
                                region=region,
                                access_key_id=creds.access_key_id,
                                secret_access_key=creds.secret_access_key,
                                session_token=creds.session_token
                            )
                        except Exception as e:
                            raise ValueError(
                                f"AWS credential provider failed: {e}. "
                                "Please ensure your credential provider returns valid AWS credentials."
                            )
                    
                    # Use explicit credentials or environment variables
                    region = self.settings.region or os.getenv("AWS_REGION")
                    access_key_id = self.settings.access_key_id or os.getenv("AWS_ACCESS_KEY_ID")  
                    secret_access_key = self.settings.secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")
                    session_token = self.settings.session_token or os.getenv("AWS_SESSION_TOKEN")
                    
                    if not region:
                        raise ValueError(
                            "AWS region is required. Set AWS_REGION environment variable or provide region in settings."
                        )
                    if not access_key_id:
                        raise ValueError(
                            "AWS access key ID is required. Set AWS_ACCESS_KEY_ID environment variable or provide access_key_id in settings."
                        )
                    if not secret_access_key:
                        raise ValueError(
                            "AWS secret access key is required. Set AWS_SECRET_ACCESS_KEY environment variable or provide secret_access_key in settings."
                        )
                        
                    return BedrockCredentials(
                        region=region,
                        access_key_id=access_key_id,
                        secret_access_key=secret_access_key,
                        session_token=session_token
                    )
                
                self._fetch_fn = await create_sigv4_fetch_function(get_credentials, http_client)
                
        return self._fetch_fn
    
    def _get_base_url(self) -> str:
        """Get base URL for Bedrock API."""
        if self.settings.base_url:
            return self.settings.base_url.rstrip('/')
            
        region = self.settings.region or os.getenv("AWS_REGION", "us-east-1")
        return f"https://bedrock-runtime.{region}.amazonaws.com"
    
    async def language_model(self, model_id: BedrockChatModelId, **kwargs) -> LanguageModel:
        """Create a Bedrock language model."""
        fetch_fn = await self._get_fetch_function()
        base_url = self._get_base_url()
        headers = self.settings.headers or {}
        
        return BedrockLanguageModel(
            model_id=model_id,
            base_url=base_url,
            fetch_fn=fetch_fn,
            headers=headers,
            **kwargs
        )
    
    async def _get_auth(self):
        """Create BedrockAuth instance."""
        from .auth import BedrockAuth
        
        # Check for API key authentication first
        api_key = self.settings.api_key or os.getenv("AWS_BEARER_TOKEN_BEDROCK")
        
        if api_key and api_key.strip():
            # For API key auth, we still need region info
            region = self.settings.region or os.getenv("AWS_REGION", "us-east-1")
            credentials = BedrockCredentials(
                region=region,
                access_key_id="", 
                secret_access_key="",
                session_token=None
            )
            return BedrockAuth(credentials, api_key=api_key.strip())
        else:
            # Get credentials for SigV4 auth
            region = self.settings.region or os.getenv("AWS_REGION")
            access_key_id = self.settings.access_key_id or os.getenv("AWS_ACCESS_KEY_ID")  
            secret_access_key = self.settings.secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")
            session_token = self.settings.session_token or os.getenv("AWS_SESSION_TOKEN")
            
            if not region:
                raise ValueError(
                    "AWS region is required. Set AWS_REGION environment variable or provide region in settings."
                )
            if not access_key_id:
                raise ValueError(
                    "AWS access key ID is required. Set AWS_ACCESS_KEY_ID environment variable or provide access_key_id in settings."
                )
            if not secret_access_key:
                raise ValueError(
                    "AWS secret access key is required. Set AWS_SECRET_ACCESS_KEY environment variable or provide secret_access_key in settings."
                )
                
            credentials = BedrockCredentials(
                region=region,
                access_key_id=access_key_id,
                secret_access_key=secret_access_key,
                session_token=session_token
            )
            return BedrockAuth(credentials)

    async def embedding_model(self, model_id: BedrockEmbeddingModelId, **kwargs) -> EmbeddingModel:
        """Create a Bedrock embedding model."""
        from .embedding_model import BedrockEmbeddingModel
        
        auth = await self._get_auth()
        region = self.settings.region or os.getenv("AWS_REGION", "us-east-1")
        base_url = self._get_base_url()
        
        return BedrockEmbeddingModel(
            model_id=model_id,
            auth=auth,
            region=region,
            base_url=base_url,
            **kwargs
        )
        
    async def image_model(self, model_id: BedrockImageModelId, **kwargs) -> ImageModel:
        """Create a Bedrock image model."""
        from .image_model import BedrockImageModel
        
        auth = await self._get_auth()
        region = self.settings.region or os.getenv("AWS_REGION", "us-east-1")
        base_url = self._get_base_url()
        
        return BedrockImageModel(
            model_id=model_id,
            auth=auth,
            region=region,
            base_url=base_url,
            **kwargs
        )
    
    async def close(self):
        """Close the HTTP client."""
        if self._http_client:
            await self._http_client.aclose()
            self._http_client = None


def create_bedrock(settings: Optional[BedrockProviderSettings] = None) -> BedrockProvider:
    """Create a Bedrock provider instance."""
    if settings is None:
        settings = BedrockProviderSettings()
    return BedrockProvider(settings)


# Default instance
bedrock = create_bedrock()