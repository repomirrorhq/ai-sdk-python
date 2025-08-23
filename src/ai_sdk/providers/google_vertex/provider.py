"""Google Vertex AI provider implementation."""

import os
from typing import Any, Dict, Optional

import httpx

from ...providers.base import Provider, LanguageModel, EmbeddingModel
from .config import GoogleVertexAuth, create_vertex_config
from .language_model import GoogleVertexLanguageModel
from .embedding_model import GoogleVertexEmbeddingModel
from .types import GoogleVertexModelId, GoogleVertexEmbeddingModelId
from .utils import get_model_display_name, validate_project_and_location


class GoogleVertexProvider(Provider):
    """Google Vertex AI provider for enterprise Google Cloud integration."""
    
    def __init__(
        self,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[Any] = None,
        service_account_path: Optional[str] = None,
        base_url: Optional[str] = None,
        http_client: Optional[httpx.AsyncClient] = None,
        **kwargs: Any,
    ):
        """
        Initialize Google Vertex AI provider.
        
        Args:
            project: Google Cloud project ID (defaults to GOOGLE_VERTEX_PROJECT env var)
            location: Google Cloud location/region (defaults to GOOGLE_VERTEX_LOCATION env var)
            credentials: Google Cloud credentials object
            service_account_path: Path to service account JSON file
            base_url: Base URL override for API calls
            http_client: Optional HTTP client to use
            **kwargs: Additional provider options
        """
        super().__init__()
        
        # Initialize authentication
        self.auth = GoogleVertexAuth(
            project=project,
            location=location,
            credentials=credentials,
            service_account_path=service_account_path,
        )
        
        # Validate project and location
        validate_project_and_location(self.auth.project, self.auth.location)
        
        self.base_url_override = base_url
        self.http_client = http_client
        self.provider_id = "google-vertex"
        self.provider_name = "Google Vertex AI"
        
        # Store additional options
        self.provider_options = kwargs
    
    def language_model(
        self, 
        model_id: GoogleVertexModelId, 
        **kwargs: Any
    ) -> LanguageModel:
        """
        Create a Google Vertex AI language model.
        
        Args:
            model_id: The Vertex AI model ID (e.g., 'gemini-1.5-pro')
            **kwargs: Additional model options
            
        Returns:
            GoogleVertexLanguageModel instance
        """
        config = create_vertex_config(
            name="chat",
            auth=self.auth,
            base_url=self.base_url_override,
            http_client=self.http_client,
        )
        
        return GoogleVertexLanguageModel(
            model_id=model_id,
            config=config,
            auth=self.auth,
            **kwargs,
        )
    
    def embedding_model(
        self, 
        model_id: GoogleVertexEmbeddingModelId, 
        **kwargs: Any
    ) -> EmbeddingModel:
        """
        Create a Google Vertex AI embedding model.
        
        Args:
            model_id: The Vertex AI embedding model ID
            **kwargs: Additional model options
            
        Returns:
            GoogleVertexEmbeddingModel instance
        """
        config = create_vertex_config(
            name="embedding",
            auth=self.auth,
            base_url=self.base_url_override,
            http_client=self.http_client,
        )
        
        return GoogleVertexEmbeddingModel(
            model_id=model_id,
            config=config,
            auth=self.auth,
            **kwargs,
        )
    
    def chat(self, model_id: GoogleVertexModelId, **kwargs: Any) -> LanguageModel:
        """
        Create a Google Vertex AI chat model (alias for language_model).
        
        Args:
            model_id: The Vertex AI model ID
            **kwargs: Additional model options
            
        Returns:
            GoogleVertexLanguageModel instance
        """
        return self.language_model(model_id, **kwargs)
    
    def __call__(
        self, 
        model_id: GoogleVertexModelId, 
        **kwargs: Any
    ) -> LanguageModel:
        """
        Create a Google Vertex AI language model (callable interface).
        
        Args:
            model_id: The Vertex AI model ID
            **kwargs: Additional model options
            
        Returns:
            GoogleVertexLanguageModel instance
        """
        return self.language_model(model_id, **kwargs)
    
    @property
    def supported_models(self) -> Dict[str, str]:
        """Get supported Google Vertex AI models."""
        return {
            # Stable Gemini models
            "gemini-2.0-flash-001": "Gemini 2.0 Flash 001",
            "gemini-1.5-flash": "Gemini 1.5 Flash",
            "gemini-1.5-flash-001": "Gemini 1.5 Flash 001",
            "gemini-1.5-flash-002": "Gemini 1.5 Flash 002",
            "gemini-1.5-pro": "Gemini 1.5 Pro",
            "gemini-1.5-pro-001": "Gemini 1.5 Pro 001",
            "gemini-1.5-pro-002": "Gemini 1.5 Pro 002",
            "gemini-1.0-pro": "Gemini 1.0 Pro",
            "gemini-1.0-pro-001": "Gemini 1.0 Pro 001",
            "gemini-1.0-pro-002": "Gemini 1.0 Pro 002",
            "gemini-1.0-pro-vision-001": "Gemini 1.0 Pro Vision 001",
            
            # Preview models
            "gemini-2.0-flash-lite-preview-02-05": "Gemini 2.0 Flash Lite (Preview)",
            
            # Experimental models
            "gemini-2.0-pro-exp-02-05": "Gemini 2.0 Pro (Experimental)",
            "gemini-2.0-flash-exp": "Gemini 2.0 Flash (Experimental)",
        }
    
    @property
    def supported_embedding_models(self) -> Dict[str, str]:
        """Get supported Google Vertex AI embedding models."""
        return {
            "text-embedding-004": "Text Embedding 004",
            "text-embedding-005": "Text Embedding 005",
            "text-multilingual-embedding-002": "Text Multilingual Embedding 002",
            "textembedding-gecko": "TextEmbedding Gecko",
            "textembedding-gecko-001": "TextEmbedding Gecko 001",
            "textembedding-gecko-002": "TextEmbedding Gecko 002",
            "textembedding-gecko-003": "TextEmbedding Gecko 003",
            "textembedding-gecko-multilingual-001": "TextEmbedding Gecko Multilingual 001",
        }


def create_vertex(
    project: Optional[str] = None,
    location: Optional[str] = None,
    credentials: Optional[Any] = None,
    service_account_path: Optional[str] = None,
    base_url: Optional[str] = None,
    http_client: Optional[httpx.AsyncClient] = None,
    **kwargs: Any,
) -> GoogleVertexProvider:
    """
    Create a Google Vertex AI provider instance.
    
    Args:
        project: Google Cloud project ID (defaults to GOOGLE_VERTEX_PROJECT env var)
        location: Google Cloud location/region (defaults to GOOGLE_VERTEX_LOCATION env var)
        credentials: Google Cloud credentials object
        service_account_path: Path to service account JSON file
        base_url: Base URL override for API calls
        http_client: Optional HTTP client to use
        **kwargs: Additional provider options
        
    Returns:
        GoogleVertexProvider instance
        
    Example:
        ```python
        import os
        from ai_sdk import create_vertex, generate_text
        
        # Set up Google Cloud credentials
        os.environ["GOOGLE_VERTEX_PROJECT"] = "your-project-id"
        os.environ["GOOGLE_VERTEX_LOCATION"] = "us-central1"
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/path/to/service-account.json"
        
        # Create provider
        vertex = create_vertex()
        
        # Create model
        model = vertex.language_model("gemini-1.5-pro")
        
        # Generate text
        result = await generate_text(
            model=model,
            messages=[{"role": "user", "content": "Hello from Vertex AI!"}]
        )
        print(result.text)
        ```
        
        ```python
        # Or with explicit parameters
        from google.oauth2 import service_account
        
        credentials = service_account.Credentials.from_service_account_file(
            "/path/to/service-account.json",
            scopes=['https://www.googleapis.com/auth/cloud-platform']
        )
        
        vertex = create_vertex(
            project="your-project-id",
            location="us-central1", 
            credentials=credentials
        )
        ```
    """
    return GoogleVertexProvider(
        project=project,
        location=location,
        credentials=credentials,
        service_account_path=service_account_path,
        base_url=base_url,
        http_client=http_client,
        **kwargs,
    )