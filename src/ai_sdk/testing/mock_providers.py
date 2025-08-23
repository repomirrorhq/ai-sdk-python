"""Mock providers for testing AI SDK applications."""

import asyncio
import time
from typing import Any, Dict, List, Optional, Union, Callable, AsyncIterator
from unittest.mock import AsyncMock

from ..providers.base import (
    LanguageModel,
    EmbeddingModel,
    ImageModel,
    SpeechModel,
    TranscriptionModel,
    Provider,
)
from ..providers.types import (
    Message,
    Content,
    FinishReason,
    LanguageModelUsage,
    EmbeddingUsage,
)
from ..errors.base import NoSuchModelError


class MockLanguageModel(LanguageModel):
    """Mock language model for testing."""

    def __init__(
        self,
        provider: str = "mock-provider",
        model_id: str = "mock-model",
        generate_response: Optional[Union[str, Dict[str, Any], Callable]] = None,
        stream_response: Optional[Union[List[str], AsyncIterator[str], Callable]] = None,
        usage: Optional[LanguageModelUsage] = None,
        delay: float = 0.0,
    ):
        self.provider = provider
        self.model_id = model_id
        self._generate_response = generate_response or "Mock response"
        self._stream_response = stream_response or ["Mock ", "stream ", "response"]
        self._usage = usage or LanguageModelUsage(
            prompt_tokens=10,
            completion_tokens=20,
            total_tokens=30,
        )
        self._delay = delay
        self.generate_calls: List[Dict[str, Any]] = []
        self.stream_calls: List[Dict[str, Any]] = []

    async def generate(
        self,
        messages: List[Message],
        model_config: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate text response."""
        if self._delay > 0:
            await asyncio.sleep(self._delay)

        # Record the call
        call_data = {
            "messages": messages,
            "model_config": model_config,
            **kwargs,
        }
        self.generate_calls.append(call_data)

        # Generate response
        if callable(self._generate_response):
            response_data = await self._generate_response(call_data)
        elif isinstance(self._generate_response, dict):
            response_data = self._generate_response
        else:
            response_data = {
                "text": str(self._generate_response),
                "finish_reason": "stop",
            }

        return {
            "text": response_data.get("text", "Mock response"),
            "finish_reason": response_data.get("finish_reason", "stop"),
            "usage": self._usage.model_dump() if self._usage else None,
            "provider_metadata": response_data.get("provider_metadata", {}),
        }

    async def stream(
        self,
        messages: List[Message],
        model_config: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> AsyncIterator[Dict[str, Any]]:
        """Stream text response."""
        # Record the call
        call_data = {
            "messages": messages,
            "model_config": model_config,
            **kwargs,
        }
        self.stream_calls.append(call_data)

        # Generate stream response
        if callable(self._stream_response):
            async for chunk in self._stream_response(call_data):
                if self._delay > 0:
                    await asyncio.sleep(self._delay)
                yield {"type": "text-delta", "text": chunk}
        else:
            response_chunks = (
                self._stream_response
                if isinstance(self._stream_response, list)
                else [str(self._stream_response)]
            )

            for chunk in response_chunks:
                if self._delay > 0:
                    await asyncio.sleep(self._delay)
                yield {"type": "text-delta", "text": chunk}

        # Final chunk with usage
        yield {
            "type": "finish",
            "finish_reason": "stop",
            "usage": self._usage.model_dump() if self._usage else None,
        }


class MockEmbeddingModel(EmbeddingModel):
    """Mock embedding model for testing."""

    def __init__(
        self,
        provider: str = "mock-provider",
        model_id: str = "mock-embedding",
        embedding_response: Optional[Union[List[float], Callable]] = None,
        usage: Optional[EmbeddingUsage] = None,
        delay: float = 0.0,
    ):
        self.provider = provider
        self.model_id = model_id
        self._embedding_response = embedding_response or [0.1, 0.2, 0.3, 0.4, 0.5]
        self._usage = usage or EmbeddingUsage(tokens=10)
        self._delay = delay
        self.embed_calls: List[Dict[str, Any]] = []

    async def embed(
        self,
        texts: List[str],
        model_config: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate embeddings."""
        if self._delay > 0:
            await asyncio.sleep(self._delay)

        # Record the call
        call_data = {
            "texts": texts,
            "model_config": model_config,
            **kwargs,
        }
        self.embed_calls.append(call_data)

        # Generate embeddings
        if callable(self._embedding_response):
            embeddings = await self._embedding_response(call_data)
        else:
            # Return same embedding for all texts
            embeddings = [self._embedding_response] * len(texts)

        return {
            "embeddings": embeddings,
            "usage": self._usage.model_dump() if self._usage else None,
        }


class MockImageModel(ImageModel):
    """Mock image generation model for testing."""

    def __init__(
        self,
        provider: str = "mock-provider",
        model_id: str = "mock-image",
        image_response: Optional[Union[bytes, str, Callable]] = None,
        delay: float = 0.0,
    ):
        self.provider = provider
        self.model_id = model_id
        self._image_response = image_response or b"mock-image-data"
        self._delay = delay
        self.generate_calls: List[Dict[str, Any]] = []

    async def generate_image(
        self,
        prompt: str,
        model_config: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate image."""
        if self._delay > 0:
            await asyncio.sleep(self._delay)

        # Record the call
        call_data = {
            "prompt": prompt,
            "model_config": model_config,
            **kwargs,
        }
        self.generate_calls.append(call_data)

        # Generate image
        if callable(self._image_response):
            image_data = await self._image_response(call_data)
        else:
            image_data = self._image_response

        return {
            "image": image_data,
            "metadata": {"prompt": prompt},
        }


class MockSpeechModel(SpeechModel):
    """Mock speech synthesis model for testing."""

    def __init__(
        self,
        provider: str = "mock-provider",
        model_id: str = "mock-speech",
        speech_response: Optional[Union[bytes, Callable]] = None,
        delay: float = 0.0,
    ):
        self.provider = provider
        self.model_id = model_id
        self._speech_response = speech_response or b"mock-audio-data"
        self._delay = delay
        self.generate_calls: List[Dict[str, Any]] = []

    async def generate_speech(
        self,
        text: str,
        model_config: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate speech."""
        if self._delay > 0:
            await asyncio.sleep(self._delay)

        # Record the call
        call_data = {
            "text": text,
            "model_config": model_config,
            **kwargs,
        }
        self.generate_calls.append(call_data)

        # Generate speech
        if callable(self._speech_response):
            audio_data = await self._speech_response(call_data)
        else:
            audio_data = self._speech_response

        return {
            "audio": audio_data,
            "metadata": {"text": text},
        }


class MockTranscriptionModel(TranscriptionModel):
    """Mock transcription model for testing."""

    def __init__(
        self,
        provider: str = "mock-provider",
        model_id: str = "mock-transcription",
        transcription_response: Optional[Union[str, Callable]] = None,
        delay: float = 0.0,
    ):
        self.provider = provider
        self.model_id = model_id
        self._transcription_response = transcription_response or "Mock transcription"
        self._delay = delay
        self.transcribe_calls: List[Dict[str, Any]] = []

    async def transcribe(
        self,
        audio: bytes,
        model_config: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Transcribe audio."""
        if self._delay > 0:
            await asyncio.sleep(self._delay)

        # Record the call
        call_data = {
            "audio_size": len(audio),
            "model_config": model_config,
            **kwargs,
        }
        self.transcribe_calls.append(call_data)

        # Generate transcription
        if callable(self._transcription_response):
            text = await self._transcription_response(call_data)
        else:
            text = self._transcription_response

        return {
            "text": text,
            "metadata": {"audio_duration": 10.0},
        }


class MockProvider(Provider):
    """Mock provider for testing that supports all model types."""

    def __init__(
        self,
        language_models: Optional[Dict[str, LanguageModel]] = None,
        embedding_models: Optional[Dict[str, EmbeddingModel]] = None,
        image_models: Optional[Dict[str, ImageModel]] = None,
        speech_models: Optional[Dict[str, SpeechModel]] = None,
        transcription_models: Optional[Dict[str, TranscriptionModel]] = None,
    ):
        self._language_models = language_models or {}
        self._embedding_models = embedding_models or {}
        self._image_models = image_models or {}
        self._speech_models = speech_models or {}
        self._transcription_models = transcription_models or {}

        # Add default models if none provided
        if not self._language_models:
            self._language_models["default"] = MockLanguageModel()

        if not self._embedding_models:
            self._embedding_models["default"] = MockEmbeddingModel()

        if not self._image_models:
            self._image_models["default"] = MockImageModel()

        if not self._speech_models:
            self._speech_models["default"] = MockSpeechModel()

        if not self._transcription_models:
            self._transcription_models["default"] = MockTranscriptionModel()

    def chat(self, model_id: str = "default") -> LanguageModel:
        """Get language model."""
        if model_id not in self._language_models:
            raise NoSuchModelError(f"Language model '{model_id}' not found")
        return self._language_models[model_id]

    def completion(self, model_id: str = "default") -> LanguageModel:
        """Get completion model (same as chat for mock)."""
        return self.chat(model_id)

    def embedding(self, model_id: str = "default") -> EmbeddingModel:
        """Get embedding model."""
        if model_id not in self._embedding_models:
            raise NoSuchModelError(f"Embedding model '{model_id}' not found")
        return self._embedding_models[model_id]

    def image(self, model_id: str = "default") -> ImageModel:
        """Get image model."""
        if model_id not in self._image_models:
            raise NoSuchModelError(f"Image model '{model_id}' not found")
        return self._image_models[model_id]

    def speech(self, model_id: str = "default") -> SpeechModel:
        """Get speech model."""
        if model_id not in self._speech_models:
            raise NoSuchModelError(f"Speech model '{model_id}' not found")
        return self._speech_models[model_id]

    def transcription(self, model_id: str = "default") -> TranscriptionModel:
        """Get transcription model."""
        if model_id not in self._transcription_models:
            raise NoSuchModelError(f"Transcription model '{model_id}' not found")
        return self._transcription_models[model_id]