"""Azure OpenAI provider implementation."""

from __future__ import annotations

import os
from typing import Any, Optional
from urllib.parse import urljoin, urlparse

from ..base import EmbeddingModel, LanguageModel, Provider
from .embedding_model import AzureOpenAIEmbeddingModel
from .language_model import AzureOpenAIChatLanguageModel


class AzureOpenAIProvider(Provider):
    """Azure OpenAI provider for language models, embeddings, and more.
    
    Azure OpenAI provides the same models as OpenAI but with Azure-specific
    authentication and URL patterns. This provider wraps the OpenAI models
    with Azure-specific configuration.
    """
    
    def __init__(
        self,
        resource_name: Optional[str] = None,
        api_key: Optional[str] = None,
        api_version: str = "2024-08-01-preview",
        base_url: Optional[str] = None,
        use_deployment_based_urls: bool = False,
        **kwargs: Any,
    ) -> None:
        """Initialize Azure OpenAI provider.
        
        Args:
            resource_name: Name of the Azure OpenAI resource. Used to construct
                          the base URL as https://{resource_name}.openai.azure.com/openai
            api_key: Azure OpenAI API key (defaults to AZURE_API_KEY env var)
            api_version: Azure API version to use
            base_url: Custom base URL for API requests. If provided, resource_name is ignored.
            use_deployment_based_urls: Whether to use deployment-based URLs
                                     ({base_url}/deployments/{deployment_id}) for compatibility
            **kwargs: Additional configuration options
        """
        # Load API key from environment if not provided
        if api_key is None:
            api_key = os.getenv("AZURE_API_KEY")
            if api_key is None:
                raise ValueError(
                    "Azure API key not found. Please provide it via the 'api_key' "
                    "parameter or set the AZURE_API_KEY environment variable."
                )
        
        # Load resource name from environment if not provided and no base_url
        if resource_name is None and base_url is None:
            resource_name = os.getenv("AZURE_RESOURCE_NAME")
            if resource_name is None:
                raise ValueError(
                    "Azure resource name or base URL not found. Please provide "
                    "'resource_name' parameter, 'base_url' parameter, or set the "
                    "AZURE_RESOURCE_NAME environment variable."
                )
        
        super().__init__(api_key=api_key, **kwargs)
        self.resource_name = resource_name
        self.api_version = api_version
        self.use_deployment_based_urls = use_deployment_based_urls
        
        # Construct base URL
        if base_url:
            self.base_url = base_url
        elif resource_name:
            self.base_url = f"https://{resource_name}.openai.azure.com/openai"
        else:
            raise ValueError("Either 'resource_name' or 'base_url' must be provided")
    
    @property
    def name(self) -> str:
        """Name of the provider."""
        return "azure"
    
    def _get_model_url(self, deployment_id: str, path: str) -> str:
        """Construct URL for Azure OpenAI API requests.
        
        Args:
            deployment_id: Azure deployment ID (model name)
            path: API path (e.g., "/chat/completions")
            
        Returns:
            Complete URL for the API request
        """
        if self.use_deployment_based_urls:
            # Legacy deployment-based format: {base_url}/deployments/{deployment_id}{path}
            url = f"{self.base_url}/deployments/{deployment_id}{path}"
        else:
            # Standard v1 format: {base_url}/v1{path}
            url = f"{self.base_url}/v1{path}"
        
        # Add API version parameter
        separator = "&" if "?" in url else "?"
        url += f"{separator}api-version={self.api_version}"
        
        return url
    
    def _get_headers(self) -> dict[str, str]:
        """Get headers for Azure OpenAI API requests.
        
        Returns:
            Dictionary of headers including Azure API key
        """
        return {
            "api-key": self.api_key,
            "Content-Type": "application/json",
        }
    
    def language_model(
        self,
        deployment_id: str,
        **kwargs: Any,
    ) -> LanguageModel:
        """Get an Azure OpenAI language model.
        
        Args:
            deployment_id: Azure deployment ID (the deployed model name)
            **kwargs: Additional model configuration
            
        Returns:
            Azure OpenAI language model instance
        """
        return AzureOpenAIChatLanguageModel(
            provider=self,
            deployment_id=deployment_id,
            **kwargs,
        )
    
    def chat(self, deployment_id: str, **kwargs: Any) -> LanguageModel:
        """Create an Azure OpenAI chat model for text generation.
        
        Args:
            deployment_id: Azure deployment ID (the deployed model name)
            **kwargs: Additional model configuration
            
        Returns:
            Azure OpenAI language model instance
        """
        return self.language_model(deployment_id=deployment_id, **kwargs)
    
    def embedding_model(
        self,
        deployment_id: str,
        **kwargs: Any,
    ) -> EmbeddingModel:
        """Get an Azure OpenAI embedding model.
        
        Args:
            deployment_id: Azure deployment ID (the deployed embedding model name)
            **kwargs: Additional model configuration
            
        Returns:
            Azure OpenAI embedding model instance
        """
        return AzureOpenAIEmbeddingModel(
            provider=self,
            deployment_id=deployment_id,
            **kwargs,
        )
    
    def embedding(self, deployment_id: str, **kwargs: Any) -> EmbeddingModel:
        """Create an Azure OpenAI model for text embeddings.
        
        Args:
            deployment_id: Azure deployment ID (the deployed embedding model name)
            **kwargs: Additional model configuration
            
        Returns:
            Azure OpenAI embedding model instance
        """
        return self.embedding_model(deployment_id=deployment_id, **kwargs)
    
    def text_embedding(self, deployment_id: str, **kwargs: Any) -> EmbeddingModel:
        """Create an Azure OpenAI model for text embeddings.
        
        Args:
            deployment_id: Azure deployment ID (the deployed embedding model name)
            **kwargs: Additional model configuration
            
        Returns:
            Azure OpenAI embedding model instance
        """
        return self.embedding_model(deployment_id=deployment_id, **kwargs)


def create_azure(
    resource_name: Optional[str] = None,
    api_key: Optional[str] = None,
    api_version: str = "2024-08-01-preview",
    base_url: Optional[str] = None,
    use_deployment_based_urls: bool = False,
    **kwargs: Any,
) -> AzureOpenAIProvider:
    """Create an Azure OpenAI provider instance.
    
    Args:
        resource_name: Name of the Azure OpenAI resource
        api_key: Azure OpenAI API key
        api_version: Azure API version to use
        base_url: Custom base URL for API requests
        use_deployment_based_urls: Whether to use deployment-based URLs
        **kwargs: Additional configuration options
        
    Returns:
        Azure OpenAI provider instance
    """
    return AzureOpenAIProvider(
        resource_name=resource_name,
        api_key=api_key,
        api_version=api_version,
        base_url=base_url,
        use_deployment_based_urls=use_deployment_based_urls,
        **kwargs,
    )


# Default Azure OpenAI provider instance (lazy initialization)
azure = None


def get_azure():
    """Get the default Azure OpenAI provider instance (lazy initialization)."""
    global azure
    if azure is None:
        azure = create_azure()
    return azure