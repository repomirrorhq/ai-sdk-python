"""Google Vertex AI embedding model implementation."""

from typing import Any, Dict, List, Optional, Union

from ...providers.base import EmbeddingModel
from ...providers.types import Usage
from ...errors.base import AISDKError
from ...utils.http import make_request
from .config import GoogleVertexConfig, GoogleVertexAuth
from .types import GoogleVertexEmbeddingModelId, EmbeddingTaskType


class GoogleVertexEmbeddingModel(EmbeddingModel):
    """Google Vertex AI embedding model implementation."""
    
    def __init__(
        self,
        model_id: GoogleVertexEmbeddingModelId,
        config: GoogleVertexConfig,
        auth: GoogleVertexAuth,
        **kwargs: Any,
    ):
        """
        Initialize Google Vertex AI embedding model.
        
        Args:
            model_id: The Vertex AI embedding model ID
            config: Configuration object
            auth: Authentication handler
            **kwargs: Additional model options
        """
        super().__init__()
        self.model_id = model_id
        self.config = config
        self.auth = auth
        self.model_options = kwargs
        self.max_embeddings_per_call = 250  # Vertex AI limit
    
    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "google-vertex"
    
    async def embed(
        self,
        values: List[str],
        task_type: Optional[EmbeddingTaskType] = None,
        output_dimensionality: Optional[int] = None,
        auto_truncate: Optional[bool] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Generate embeddings for input texts.
        
        Args:
            values: List of texts to embed
            task_type: Task type for the embeddings
            output_dimensionality: Desired output dimensionality
            auto_truncate: Whether to auto-truncate inputs
            **kwargs: Additional options
            
        Returns:
            Dictionary containing embeddings and metadata
        """
        if len(values) > self.max_embeddings_per_call:
            raise AISDKError(
                f"Too many values for single call. Maximum {self.max_embeddings_per_call}, "
                f"got {len(values)}. Use embed_many for larger batches."
            )
        
        # Get authentication headers
        headers = await self.auth.get_auth_headers()
        
        # Build request payload
        request_body = self._build_embedding_request(
            values,
            task_type=task_type,
            output_dimensionality=output_dimensionality,
            auto_truncate=auto_truncate,
            **kwargs
        )
        
        # Make API request
        url = f"{self.config.base_url}/models/{self.model_id}:predict"
        
        try:
            response = await make_request(
                method="POST",
                url=url,
                headers=headers,
                json=request_body,
                http_client=self.config.http_client,
            )
            
            # Parse response
            return self._parse_embedding_response(response, len(values))
            
        except Exception as e:
            raise AISDKError(f"Google Vertex AI embedding failed: {e}")
    
    async def embed_many(
        self,
        values: List[str],
        batch_size: Optional[int] = None,
        task_type: Optional[EmbeddingTaskType] = None,
        output_dimensionality: Optional[int] = None,
        auto_truncate: Optional[bool] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Generate embeddings for many texts using batching.
        
        Args:
            values: List of texts to embed
            batch_size: Batch size for processing (defaults to max per call)
            task_type: Task type for the embeddings
            output_dimensionality: Desired output dimensionality
            auto_truncate: Whether to auto-truncate inputs
            **kwargs: Additional options
            
        Returns:
            Dictionary containing embeddings and metadata
        """
        if not batch_size:
            batch_size = self.max_embeddings_per_call
        
        all_embeddings = []
        total_tokens = 0
        
        # Process in batches
        for i in range(0, len(values), batch_size):
            batch = values[i:i + batch_size]
            
            result = await self.embed(
                values=batch,
                task_type=task_type,
                output_dimensionality=output_dimensionality,
                auto_truncate=auto_truncate,
                **kwargs
            )
            
            all_embeddings.extend(result["embeddings"])
            total_tokens += result.get("usage", {}).get("tokens", 0)
        
        return {
            "embeddings": all_embeddings,
            "usage": {"tokens": total_tokens},
        }
    
    def _build_embedding_request(
        self,
        values: List[str],
        task_type: Optional[EmbeddingTaskType] = None,
        output_dimensionality: Optional[int] = None,
        auto_truncate: Optional[bool] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Build request body for embedding API."""
        instances = []
        
        for value in values:
            instance = {"content": value}
            if task_type:
                instance["taskType"] = task_type
            instances.append(instance)
        
        body = {"instances": instances}
        
        # Add parameters
        parameters = {}
        if output_dimensionality:
            parameters["outputDimensionality"] = output_dimensionality
        if auto_truncate is not None:
            parameters["autoTruncate"] = auto_truncate
        
        # Add any additional kwargs to parameters
        for key, value in kwargs.items():
            if key not in ["task_type", "output_dimensionality", "auto_truncate"]:
                parameters[key] = value
        
        if parameters:
            body["parameters"] = parameters
        
        return body
    
    def _parse_embedding_response(
        self, 
        response: Dict[str, Any], 
        num_inputs: int
    ) -> Dict[str, Any]:
        """Parse embedding response."""
        try:
            predictions = response.get("predictions", [])
            if len(predictions) != num_inputs:
                raise AISDKError(
                    f"Expected {num_inputs} predictions, got {len(predictions)}"
                )
            
            embeddings = []
            total_tokens = 0
            
            for prediction in predictions:
                embedding_data = prediction.get("embeddings", {})
                values = embedding_data.get("values", [])
                
                if not values:
                    raise AISDKError("No embedding values in prediction")
                
                embeddings.append(values)
                
                # Sum token counts
                statistics = embedding_data.get("statistics", {})
                total_tokens += statistics.get("token_count", 0)
            
            return {
                "embeddings": embeddings,
                "usage": {"tokens": total_tokens},
                "response_data": response,
            }
            
        except Exception as e:
            raise AISDKError(f"Failed to parse Vertex AI embedding response: {e}")