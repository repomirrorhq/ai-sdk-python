"""
OpenAI-Compatible Embedding Model implementation
"""

from typing import List, Dict, Any, Union, Optional
from urllib.parse import urlencode

from ...core.embed import EmbeddingModel, EmbedResult
from ...utils.http import make_request
from .types import OpenAICompatibleConfig, OpenAICompatibleEmbeddingModelId
from .errors import as_openai_compatible_error


class OpenAICompatibleEmbeddingModel(EmbeddingModel):
    """OpenAI-Compatible embedding model"""
    
    def __init__(self, model_id: OpenAICompatibleEmbeddingModelId, config: OpenAICompatibleConfig):
        self.model_id = model_id
        self.config = config
    
    @property
    def provider(self) -> str:
        return self.config.provider
    
    @property
    def max_values_per_call(self) -> Optional[int]:
        # Most OpenAI-compatible APIs support batched embeddings
        return 100
    
    def _get_url(self, path: str) -> str:
        """Build full URL with query parameters"""
        base_url = f"{self.config.base_url.rstrip('/')}{path}"
        if self.config.fetch is None:
            query_params = getattr(self.config, 'query_params', None)
            if query_params:
                separator = '&' if '?' in base_url else '?'
                return f"{base_url}{separator}{urlencode(query_params)}"
        return base_url
    
    async def embed(self, values: List[str]) -> EmbedResult:
        """Generate embeddings for input values"""
        try:
            url = self._get_url("/v1/embeddings")
            headers = self.config.headers()
            headers.update({
                "Content-Type": "application/json",
            })
            
            # Prepare request body
            body = {
                "model": self.model_id,
                "input": values,
            }
            
            response_data = await make_request(
                url=url,
                method="POST",
                headers=headers,
                json=body,
                http_client=self.config.fetch
            )
            
            # Extract embeddings
            embeddings = []
            for item in response_data["data"]:
                embeddings.append(item["embedding"])
            
            return EmbedResult(
                embeddings=embeddings,
                usage=response_data.get("usage", {}),
                response_metadata={
                    "model": response_data.get("model", self.model_id),
                    "object": response_data.get("object"),
                }
            )
            
        except Exception as error:
            raise as_openai_compatible_error(error, self.config.provider)
    
    async def embed_single(self, value: str) -> List[float]:
        """Generate embedding for a single value"""
        result = await self.embed([value])
        return result.embeddings[0]