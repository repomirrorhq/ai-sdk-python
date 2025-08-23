"""
Gateway Embedding Model implementation
"""

from typing import Dict, List, Any, Optional, Union
import aiohttp

from ...core.embed import EmbedOptions, EmbedResult
from .types import GatewayEmbeddingModelId, GatewayConfig
from .errors import as_gateway_error


class GatewayEmbeddingModel:
    """Embedding model implementation for Gateway Provider"""
    
    def __init__(self, model_id: GatewayEmbeddingModelId, config: GatewayConfig):
        self.model_id = model_id
        self.config = config
        self.specification_version = "v2"
        
    @property
    def provider(self) -> str:
        return self.config.provider
    
    async def embed(
        self,
        values: Union[str, List[str]],
        options: Optional[EmbedOptions] = None,
        **kwargs
    ) -> EmbedResult:
        """
        Generate embeddings using the Gateway model.
        
        Args:
            values: Text string or list of strings to embed
            options: Embedding options
            **kwargs: Additional options
            
        Returns:
            Embedding result with vectors
        """
        options = options or EmbedOptions()
        
        # Normalize input to list format
        if isinstance(values, str):
            input_values = [values]
        else:
            input_values = values
        
        args = {
            "values": input_values,
            **options.model_dump(exclude_none=True),
            **kwargs
        }
        
        headers = await self.config.headers()
        headers.update(self._get_model_config_headers())
        headers.update(await self.config.o11y_headers())
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self._get_url(),
                    json=args,
                    headers=headers
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"HTTP {response.status}: {error_text}")
                    
                    response_data = await response.json()
                    
                    return EmbedResult(
                        embeddings=response_data.get("embeddings", []),
                        usage=response_data.get("usage", {}),
                        request={"body": args},
                        response={
                            "headers": dict(response.headers),
                            "body": response_data
                        }
                    )
                    
        except Exception as error:
            auth_method = self._parse_auth_method(headers)
            raise as_gateway_error(error, auth_method)
    
    def _get_url(self) -> str:
        """Get the embedding model endpoint URL"""
        return f"{self.config.base_url}/embedding-model"
    
    def _get_model_config_headers(self) -> Dict[str, str]:
        """Get model configuration headers"""
        return {
            "ai-embedding-model-specification-version": "2",
            "ai-embedding-model-id": self.model_id
        }
    
    def _parse_auth_method(self, headers: Dict[str, str]) -> Optional[str]:
        """Parse authentication method from headers"""
        return headers.get("ai-gateway-auth-method")