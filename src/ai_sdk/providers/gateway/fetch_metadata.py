"""
Gateway Metadata Fetching implementation
"""

from typing import Dict, Any
import aiohttp

from .types import GatewayConfig, GatewayFetchMetadataResponse
from .errors import as_gateway_error


class GatewayFetchMetadata:
    """Handles fetching metadata about available models from Gateway"""
    
    def __init__(self, config: GatewayConfig):
        self.config = config
    
    async def get_available_models(self) -> GatewayFetchMetadataResponse:
        """
        Fetch available models from Gateway config endpoint.
        
        Returns:
            Metadata response with available models
        """
        headers = await self.config.headers()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.config.base_url}/config",
                    headers=headers
                ) as response:
                    
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"HTTP {response.status}: {error_text}")
                    
                    response_data = await response.json()
                    
                    # Parse and validate response using Pydantic
                    return GatewayFetchMetadataResponse.model_validate(response_data)
                    
        except Exception as error:
            raise as_gateway_error(error)