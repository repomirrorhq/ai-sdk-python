"""
Bedrock Embedding Model implementation.
Provides embedding capabilities for Amazon Bedrock embedding models.
"""

import asyncio
from typing import Any, Dict, List, Optional, Union
from ai_sdk.core.types import EmbeddingModel, GenerateEmbeddingOptions, GenerateEmbeddingResult
from ai_sdk.providers.types import Usage
from ai_sdk.errors.base import AISDKError
from ai_sdk.utils.http import create_http_client
from pydantic import BaseModel, Field
from .types import BedrockEmbeddingModelId
from .auth import BedrockAuth


class BedrockEmbeddingOptions(BaseModel):
    """Bedrock-specific embedding options."""
    
    dimensions: Optional[Union[int, None]] = Field(
        default=None,
        description="The number of dimensions for the output embeddings (256, 512, or 1024). Only supported by amazon.titan-embed-text-v2:0."
    )
    
    normalize: Optional[bool] = Field(
        default=None,
        description="Flag indicating whether to normalize the output embeddings. Defaults to true. Only supported by amazon.titan-embed-text-v2:0."
    )


class BedrockEmbeddingResponse(BaseModel):
    """Response schema for Bedrock embedding API."""
    embedding: List[float]
    inputTextTokenCount: int


class BedrockEmbeddingModel(EmbeddingModel):
    """
    Amazon Bedrock Embedding Model implementation.
    
    Supports various embedding models available on Amazon Bedrock including:
    - Amazon Titan Text Embedding models (v1 and v2)
    - Cohere Embed models (English and Multilingual v3)
    """
    
    def __init__(
        self,
        model_id: BedrockEmbeddingModelId,
        auth: BedrockAuth,
        region: str = "us-east-1",
        base_url: Optional[str] = None,
        max_retries: int = 3,
        timeout: float = 30.0,
    ):
        self.model_id = model_id
        self.auth = auth
        self.region = region
        self.base_url = base_url or f"https://bedrock-runtime.{region}.amazonaws.com"
        self.max_retries = max_retries
        self.timeout = timeout
        self.http_client = create_http_client(timeout=timeout, max_retries=max_retries)
        
        # Model capabilities
        self.max_embeddings_per_call = 1  # Bedrock embedding models process one text at a time
        self.supports_parallel_calls = True
    
    def _get_url(self) -> str:
        """Get the API URL for the embedding model."""
        encoded_model_id = self.model_id.replace(":", "%3A")
        return f"{self.base_url}/model/{encoded_model_id}/invoke"
    
    async def _prepare_request_body(
        self, 
        text: str, 
        options: Optional[BedrockEmbeddingOptions] = None
    ) -> Dict[str, Any]:
        """Prepare the request body for the Bedrock embedding API."""
        body = {
            "inputText": text
        }
        
        if options:
            if options.dimensions is not None:
                body["dimensions"] = options.dimensions
            if options.normalize is not None:
                body["normalize"] = options.normalize
        
        return body
    
    async def generate_embedding(
        self,
        text: str,
        options: Optional[GenerateEmbeddingOptions] = None
    ) -> GenerateEmbeddingResult:
        """
        Generate a single embedding for the given text.
        
        Args:
            text: The input text to embed
            options: Optional generation options
            
        Returns:
            GenerateEmbeddingResult with the embedding and usage information
        """
        # Parse Bedrock-specific options
        bedrock_options = None
        if options and hasattr(options, 'provider_options') and options.provider_options:
            bedrock_options = BedrockEmbeddingOptions.model_validate(
                options.provider_options.get('bedrock', {})
            )
        
        url = self._get_url()
        body = await self._prepare_request_body(text, bedrock_options)
        
        try:
            # Prepare headers with authentication
            headers = await self.auth.get_headers(
                method="POST",
                url=url,
                body=body
            )
            headers["Content-Type"] = "application/json"
            
            # Make the API request
            async with self.http_client as client:
                response = await client.post(
                    url,
                    json=body,
                    headers=headers
                )
                
                if response.status_code != 200:
                    error_data = response.json() if response.content else {}
                    raise AISDKError(
                        f"Bedrock embedding request failed: {response.status_code} - {error_data}"
                    )
                
                result_data = response.json()
                bedrock_response = BedrockEmbeddingResponse.model_validate(result_data)
                
                return GenerateEmbeddingResult(
                    embedding=bedrock_response.embedding,
                    usage=Usage(
                        input_tokens=bedrock_response.inputTextTokenCount,
                        output_tokens=0,
                        total_tokens=bedrock_response.inputTextTokenCount
                    )
                )
                
        except Exception as e:
            if isinstance(e, AISDKError):
                raise
            raise AISDKError(f"Failed to generate embedding: {str(e)}") from e
    
    async def generate_embeddings(
        self,
        texts: List[str],
        options: Optional[GenerateEmbeddingOptions] = None
    ) -> List[GenerateEmbeddingResult]:
        """
        Generate embeddings for multiple texts.
        
        Since Bedrock embedding models process one text at a time,
        this method processes them concurrently.
        
        Args:
            texts: List of input texts to embed
            options: Optional generation options
            
        Returns:
            List of GenerateEmbeddingResult objects
        """
        if not texts:
            return []
        
        # Process all texts concurrently since Bedrock supports parallel calls
        tasks = [
            self.generate_embedding(text, options)
            for text in texts
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Check for exceptions and re-raise them
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                raise AISDKError(
                    f"Failed to generate embedding for text {i}: {str(result)}"
                ) from result
            final_results.append(result)
        
        return final_results
    
    async def close(self):
        """Close the HTTP client."""
        if hasattr(self.http_client, 'aclose'):
            await self.http_client.aclose()