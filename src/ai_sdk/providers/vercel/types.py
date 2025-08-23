"""Type definitions for Vercel AI provider."""

from typing import Literal, Optional, Dict, Any
from pydantic import BaseModel, Field


# Vercel Chat Model IDs based on v0.dev documentation
VercelChatModelId = Literal[
    "v0-1.0-md",  # Original v0 model
    "v0-1.5-md",  # Enhanced v0 model (medium)
    "v0-1.5-lg",  # Enhanced v0 model (large)
]


class VercelProviderSettings(BaseModel):
    """Configuration settings for Vercel provider."""
    
    api_key: Optional[str] = Field(
        default=None,
        description="Vercel API key (can also be set via VERCEL_API_KEY environment variable)"
    )
    
    base_url: str = Field(
        default="https://api.v0.dev/v1",
        description="Base URL for Vercel API calls"
    )
    
    headers: Optional[Dict[str, str]] = Field(
        default=None,
        description="Additional headers to include in requests"
    )
    
    max_retries: int = Field(
        default=3,
        description="Maximum number of retry attempts"
    )
    
    timeout: float = Field(
        default=60.0,
        description="Request timeout in seconds"
    )


class VercelLanguageModelOptions(BaseModel):
    """Provider-specific options for Vercel language models."""
    
    # Framework-aware features
    framework: Optional[Literal["next.js", "react", "vue", "svelte"]] = Field(
        default=None,
        description="Target framework for code generation optimization"
    )
    
    # Auto-fix capabilities
    enable_auto_fix: Optional[bool] = Field(
        default=None,
        description="Enable automatic code fixing during generation"
    )
    
    # Quick edit features
    enable_quick_edit: Optional[bool] = Field(
        default=None,
        description="Enable inline edit suggestions"
    )
    
    # Development context
    project_type: Optional[Literal["web", "mobile", "desktop", "api"]] = Field(
        default=None,
        description="Type of project being developed"
    )
    
    # UI/UX preferences
    design_system: Optional[str] = Field(
        default=None,
        description="Preferred design system (e.g., 'tailwind', 'material-ui', 'chakra')"
    )
    
    # Code style preferences
    typescript: Optional[bool] = Field(
        default=None,
        description="Generate TypeScript code when applicable"
    )