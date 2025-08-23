"""Azure OpenAI embedding model implementation."""

from __future__ import annotations

from typing import Any, Dict, List

import httpx

from ...errors import APIError, NetworkError
from ...utils.http import create_http_client
from ...utils.json import secure_json_parse
from ..openai.embedding_model import OpenAIEmbeddingModel
from ..types import EmbeddingResult


class AzureOpenAIEmbeddingModel(OpenAIEmbeddingModel):
    """Azure OpenAI embedding model.
    
    This extends the OpenAI embedding model with Azure-specific authentication
    and URL handling.
    """
    
    def __init__(
        self,
        provider: Any,  # AzureOpenAIProvider
        deployment_id: str,
        **kwargs: Any,
    ) -> None:
        """Initialize Azure OpenAI embedding model.
        
        Args:
            provider: Azure OpenAI provider instance
            deployment_id: Azure deployment ID (deployed model name)
            **kwargs: Additional model configuration
        """
        super().__init__(provider, deployment_id, **kwargs)
        self.deployment_id = deployment_id
    
    async def _make_api_call(
        self,
        texts: List[str],
        dimensions: int | None = None,
    ) -> Dict[str, Any]:
        """Make API call to Azure OpenAI embeddings endpoint."""
        headers = {
            "api-key": self.provider.api_key,
            "Content-Type": "application/json",
        }
        
        # Build request body
        request_body = {
            "model": self.deployment_id,
            "input": texts,
        }
        
        # Add dimensions if supported and specified
        if dimensions is not None:
            request_body["dimensions"] = dimensions
        
        # Construct the URL
        url = self.provider._get_model_url(self.deployment_id, "/embeddings")
        
        client = create_http_client(
            base_url="",  # URL is complete
            headers=headers,
        )
        
        try:
            async with client:
                response = await client.post(
                    url,
                    json=request_body,
                )
                
                if response.status_code != 200:
                    raise APIError(
                        f"Azure OpenAI API error: {response.status_code}",
                        status_code=response.status_code,
                        response_body=response.text,
                        headers=dict(response.headers),
                    )
                
                return secure_json_parse(response.text, expected_type=dict)
        
        except httpx.RequestError as e:
            raise NetworkError(f"Network error calling Azure OpenAI API: {e}") from e