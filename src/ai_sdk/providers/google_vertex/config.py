"""Configuration for Google Vertex AI provider."""

import os
from typing import Optional, Dict, Any, Callable, Union
from dataclasses import dataclass

import httpx


@dataclass
class GoogleVertexConfig:
    """Configuration for Google Vertex AI."""
    
    provider: str
    base_url: str
    headers: Dict[str, Optional[str]]
    http_client: Optional[httpx.AsyncClient] = None
    fetch: Optional[Callable] = None


class GoogleVertexAuth:
    """Google Vertex AI authentication handler."""
    
    def __init__(
        self,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[Any] = None,
        service_account_path: Optional[str] = None,
    ):
        """
        Initialize Google Vertex AI authentication.
        
        Args:
            project: Google Cloud project ID (defaults to GOOGLE_VERTEX_PROJECT env var)
            location: Google Cloud location/region (defaults to GOOGLE_VERTEX_LOCATION env var)
            credentials: Google Cloud credentials object
            service_account_path: Path to service account JSON file
        """
        self.project = project or os.getenv("GOOGLE_VERTEX_PROJECT")
        self.location = location or os.getenv("GOOGLE_VERTEX_LOCATION", "us-central1")
        self.credentials = credentials
        self.service_account_path = service_account_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
        
        if not self.project:
            raise ValueError(
                "Google Cloud project is required. Set GOOGLE_VERTEX_PROJECT environment variable "
                "or pass project parameter."
            )
    
    def get_base_url(self, base_url_override: Optional[str] = None) -> str:
        """
        Get the base URL for Google Vertex AI API.
        
        Args:
            base_url_override: Optional override for the base URL
            
        Returns:
            Base URL for API calls
        """
        if base_url_override:
            return base_url_override.rstrip("/")
        
        # For global region, use aiplatform.googleapis.com directly
        # For other regions, use region-aiplatform.googleapis.com
        if self.location == "global":
            base_host = "aiplatform.googleapis.com"
        else:
            base_host = f"{self.location}-aiplatform.googleapis.com"
        
        return f"https://{base_host}/v1/projects/{self.project}/locations/{self.location}/publishers/google"
    
    async def get_access_token(self) -> str:
        """
        Get Google Cloud access token for authentication.
        
        Returns:
            Access token string
        """
        try:
            from google.auth import default
            from google.auth.transport.requests import Request
        except ImportError:
            raise ImportError(
                "google-auth library is required for Google Vertex AI authentication. "
                "Install with: pip install google-auth"
            )
        
        # Get default credentials
        if self.credentials:
            credentials = self.credentials
        else:
            if self.service_account_path:
                from google.oauth2 import service_account
                credentials = service_account.Credentials.from_service_account_file(
                    self.service_account_path,
                    scopes=['https://www.googleapis.com/auth/cloud-platform']
                )
            else:
                credentials, _ = default(scopes=['https://www.googleapis.com/auth/cloud-platform'])
        
        # Refresh the token if needed
        if not credentials.token or credentials.expired:
            credentials.refresh(Request())
        
        return credentials.token
    
    async def get_auth_headers(self) -> Dict[str, str]:
        """
        Get authentication headers for API requests.
        
        Returns:
            Dictionary of headers for authentication
        """
        try:
            token = await self.get_access_token()
            return {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            }
        except Exception as e:
            raise ValueError(f"Failed to get Google Cloud credentials: {e}")


def create_vertex_config(
    name: str,
    auth: GoogleVertexAuth,
    base_url: Optional[str] = None,
    http_client: Optional[httpx.AsyncClient] = None,
) -> GoogleVertexConfig:
    """
    Create Google Vertex AI configuration.
    
    Args:
        name: Configuration name (e.g., 'chat', 'embedding')
        auth: Authentication handler
        base_url: Optional base URL override
        http_client: Optional HTTP client
        
    Returns:
        GoogleVertexConfig instance
    """
    return GoogleVertexConfig(
        provider=f"google.vertex.{name}",
        base_url=auth.get_base_url(base_url),
        headers={},  # Headers will be set dynamically via auth
        http_client=http_client,
    )