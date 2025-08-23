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
from .generate_image import (
    generate_image,
    generate_image_sync,
    GenerateImageResult,
    NoImageGeneratedError,
)
from .generate_speech import (
    generate_speech,
    generate_speech_sync,
    GenerateSpeechResult,
    NoSpeechGeneratedError,
)
from .transcribe import (
    transcribe,
    transcribe_sync,
    TranscriptionResult,
    NoTranscriptGeneratedError,
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
    "generate_image",
    "generate_image_sync", 
    "GenerateImageResult",
    "NoImageGeneratedError",
    "generate_speech",
    "generate_speech_sync",
    "GenerateSpeechResult", 
    "NoSpeechGeneratedError",
    "transcribe",
    "transcribe_sync",
    "TranscriptionResult",
    "NoTranscriptGeneratedError",
]