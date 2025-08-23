"""Utility functions for AI SDK Python."""

from .api_key import load_api_key, load_optional_setting
from .cosine_similarity import cosine_similarity
from .delay import delay
from .dict_utils import merge_dicts, remove_none_entries
from .headers import clean_headers, combine_headers
from .http import create_http_client
from .id_generator import IdGenerator, create_id_generator, generate_id
from .json import secure_json_parse
from .partial_json import fix_json, parse_partial_json
from .secure_json import secure_json_parse as secure_json_parse_strict
from .text_utils import get_potential_start_index

__all__ = [
    # HTTP utilities
    "create_http_client",
    
    # JSON utilities  
    "secure_json_parse",
    "secure_json_parse_strict",
    "parse_partial_json",
    "fix_json",
    
    # Text utilities
    "get_potential_start_index",
    
    # ID generation
    "generate_id", 
    "create_id_generator",
    "IdGenerator",
    
    # API key loading
    "load_api_key",
    "load_optional_setting",
    
    # Header manipulation
    "combine_headers",
    "clean_headers",
    
    # Dictionary utilities
    "remove_none_entries",
    "merge_dicts",
    
    # Mathematical utilities
    "cosine_similarity",
    
    # Async utilities
    "delay",
]