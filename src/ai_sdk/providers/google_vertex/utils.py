"""Utility functions for Google Vertex AI provider."""

from typing import Optional

from ...providers.types import FinishReason


def map_vertex_finish_reason(vertex_reason: str) -> FinishReason:
    """
    Map Google Vertex AI finish reason to AI SDK format.
    
    Args:
        vertex_reason: Vertex AI finish reason
        
    Returns:
        AI SDK finish reason
    """
    reason_mapping = {
        "STOP": "stop",
        "MAX_TOKENS": "length", 
        "SAFETY": "content_filter",
        "RECITATION": "content_filter",
        "OTHER": "other",
        "FINISH_REASON_UNSPECIFIED": "other",
    }
    
    return reason_mapping.get(vertex_reason, "other")


def get_model_display_name(model_id: str) -> str:
    """
    Get display name for a model ID.
    
    Args:
        model_id: Model identifier
        
    Returns:
        Human-readable model name
    """
    model_names = {
        # Stable models
        "gemini-2.0-flash-001": "Gemini 2.0 Flash 001",
        "gemini-1.5-flash": "Gemini 1.5 Flash", 
        "gemini-1.5-flash-001": "Gemini 1.5 Flash 001",
        "gemini-1.5-flash-002": "Gemini 1.5 Flash 002",
        "gemini-1.5-pro": "Gemini 1.5 Pro",
        "gemini-1.5-pro-001": "Gemini 1.5 Pro 001",
        "gemini-1.5-pro-002": "Gemini 1.5 Pro 002",
        "gemini-1.0-pro-001": "Gemini 1.0 Pro 001",
        "gemini-1.0-pro-vision-001": "Gemini 1.0 Pro Vision 001",
        "gemini-1.0-pro": "Gemini 1.0 Pro",
        "gemini-1.0-pro-001": "Gemini 1.0 Pro 001",
        "gemini-1.0-pro-002": "Gemini 1.0 Pro 002",
        # Preview models
        "gemini-2.0-flash-lite-preview-02-05": "Gemini 2.0 Flash Lite (Preview)",
        # Experimental models
        "gemini-2.0-pro-exp-02-05": "Gemini 2.0 Pro (Experimental)",
        "gemini-2.0-flash-exp": "Gemini 2.0 Flash (Experimental)",
    }
    
    return model_names.get(model_id, model_id.title())


def validate_project_and_location(project: str, location: str) -> None:
    """
    Validate Google Cloud project and location.
    
    Args:
        project: Google Cloud project ID
        location: Google Cloud location/region
        
    Raises:
        ValueError: If project or location is invalid
    """
    if not project or not project.strip():
        raise ValueError("Google Cloud project ID cannot be empty")
    
    if not location or not location.strip():
        raise ValueError("Google Cloud location cannot be empty")
    
    # Basic validation for common location formats
    valid_location_patterns = [
        "us-central1", "us-east1", "us-west1", "us-west2",
        "europe-west1", "europe-west2", "europe-west3", "europe-west4",
        "asia-east1", "asia-southeast1", "asia-northeast1",
        "global"
    ]
    
    # Allow the location if it matches common patterns or is custom
    if location not in valid_location_patterns and not location.count("-") >= 1:
        import warnings
        warnings.warn(
            f"Location '{location}' may not be a valid Google Cloud region. "
            "Please ensure it's correct for your use case."
        )


def format_vertex_error(error_response: dict) -> str:
    """
    Format Google Vertex AI error response for display.
    
    Args:
        error_response: Error response from Vertex AI API
        
    Returns:
        Formatted error message
    """
    if isinstance(error_response, dict):
        error = error_response.get("error", {})
        if isinstance(error, dict):
            code = error.get("code", "Unknown")
            message = error.get("message", "Unknown error")
            status = error.get("status", "")
            
            if status:
                return f"Google Vertex AI Error {code} ({status}): {message}"
            else:
                return f"Google Vertex AI Error {code}: {message}"
    
    return f"Google Vertex AI Error: {error_response}"