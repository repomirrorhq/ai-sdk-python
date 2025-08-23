"""Core functionality for AI SDK Python."""

from .generate_text import generate_text, stream_text
from .generate_object import (
    generate_object,
    generate_object_sync,
    stream_object,
    stream_object_sync,
    collect_stream_object,
    GenerateObjectResult,
    StreamObjectResult,
    ObjectStreamPart,
    ObjectPart,
    TextDeltaPart,
    FinishPart,
    ErrorPart,
)

__all__ = [
    "generate_text",
    "stream_text",
    "generate_object", 
    "generate_object_sync",
    "stream_object",
    "stream_object_sync", 
    "collect_stream_object",
    "GenerateObjectResult",
    "StreamObjectResult",
    "ObjectStreamPart",
    "ObjectPart",
    "TextDeltaPart",
    "FinishPart",
    "ErrorPart",
]