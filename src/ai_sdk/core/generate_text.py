"""Core text generation functions for AI SDK Python."""

from __future__ import annotations

from typing import Any, AsyncGenerator, Dict, List, Optional, Union

from ..errors import InvalidArgumentError
from ..providers.base import LanguageModel
from ..providers.types import (
    Content,
    FinishReason,
    GenerateOptions,
    GenerateResult,
    Message,
    StreamOptions,
    StreamPart,
    ToolDefinition,
    Usage,
)


class GenerateTextOptions:
    """Options for generating text."""
    
    def __init__(
        self,
        model: LanguageModel,
        *,
        system: Optional[str] = None,
        prompt: Optional[str] = None,
        messages: Optional[List[Message]] = None,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        top_k: Optional[int] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        seed: Optional[int] = None,
        tools: Optional[List[ToolDefinition]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        max_retries: int = 2,
        headers: Optional[Dict[str, str]] = None,
        extra_body: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize generate text options.
        
        Args:
            model: Language model to use
            system: System message
            prompt: Simple text prompt (mutually exclusive with messages)
            messages: List of messages (mutually exclusive with prompt)
            max_tokens: Maximum number of tokens to generate
            temperature: Temperature setting (0.0 to 2.0)
            top_p: Nucleus sampling parameter (0.0 to 1.0)
            top_k: Top-k sampling parameter
            frequency_penalty: Frequency penalty (-2.0 to 2.0)
            presence_penalty: Presence penalty (-2.0 to 2.0)
            stop: Stop sequences
            seed: Random seed for deterministic output
            tools: Available tools for the model to call
            tool_choice: How the model should choose tools
            max_retries: Maximum number of retries
            headers: Additional HTTP headers
            extra_body: Additional request body parameters
        """
        self.model = model
        self.system = system
        self.prompt = prompt
        self.messages = messages
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.top_p = top_p
        self.top_k = top_k
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.stop = stop
        self.seed = seed
        self.tools = tools
        self.tool_choice = tool_choice
        self.max_retries = max_retries
        self.headers = headers
        self.extra_body = extra_body
        
        # Validate mutually exclusive options
        if prompt is not None and messages is not None:
            raise InvalidArgumentError(
                "Cannot specify both 'prompt' and 'messages'. Use one or the other."
            )
        
        if prompt is None and messages is None:
            raise InvalidArgumentError(
                "Must specify either 'prompt' or 'messages'."
            )


class GenerateTextResult:
    """Result from text generation."""
    
    def __init__(
        self,
        text: str,
        content: List[Content],
        finish_reason: FinishReason,
        usage: Usage,
        provider_metadata: Optional[Dict[str, Any]] = None,
        request_metadata: Optional[Dict[str, Any]] = None,
        response_metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize generate text result.
        
        Args:
            text: Generated text content
            content: Generated content parts
            finish_reason: Reason why generation stopped
            usage: Token usage information
            provider_metadata: Provider-specific metadata
            request_metadata: Request metadata
            response_metadata: Response metadata
        """
        self.text = text
        self.content = content
        self.finish_reason = finish_reason
        self.usage = usage
        self.provider_metadata = provider_metadata
        self.request_metadata = request_metadata
        self.response_metadata = response_metadata


async def generate_text(
    model: LanguageModel,
    *,
    system: Optional[str] = None,
    prompt: Optional[str] = None,
    messages: Optional[List[Message]] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    top_k: Optional[int] = None,
    frequency_penalty: Optional[float] = None,
    presence_penalty: Optional[float] = None,
    stop: Optional[Union[str, List[str]]] = None,
    seed: Optional[int] = None,
    tools: Optional[List[ToolDefinition]] = None,
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
    max_retries: int = 2,
    headers: Optional[Dict[str, str]] = None,
    extra_body: Optional[Dict[str, Any]] = None,
) -> GenerateTextResult:
    """Generate text using a language model.
    
    Args:
        model: Language model to use for generation
        system: System message that will be part of the prompt
        prompt: Simple text prompt (mutually exclusive with messages)
        messages: List of messages (mutually exclusive with prompt)
        max_tokens: Maximum number of tokens to generate
        temperature: Temperature setting for randomness (0.0 to 2.0)
        top_p: Nucleus sampling parameter (0.0 to 1.0)
        top_k: Top-k sampling parameter
        frequency_penalty: Frequency penalty (-2.0 to 2.0)
        presence_penalty: Presence penalty (-2.0 to 2.0)
        stop: Stop sequences (string or list of strings)
        seed: Random seed for deterministic output
        tools: Available tools for the model to call
        tool_choice: How the model should choose tools ("auto", "none", or specific tool)
        max_retries: Maximum number of retries on failure
        headers: Additional HTTP headers
        extra_body: Additional request body parameters
        
    Returns:
        GenerateTextResult containing the generated text and metadata
        
    Raises:
        InvalidArgumentError: If arguments are invalid
        APIError: If the API call fails
        NetworkError: If there are network issues
    """
    # Create options and validate
    options = GenerateTextOptions(
        model=model,
        system=system,
        prompt=prompt,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        stop=stop,
        seed=seed,
        tools=tools,
        tool_choice=tool_choice,
        max_retries=max_retries,
        headers=headers,
        extra_body=extra_body,
    )
    
    # Convert to provider-specific format
    provider_options = _convert_to_provider_options(options)
    
    # Call the model
    result = await model.generate(provider_options)
    
    # Convert result to our format
    return _convert_from_provider_result(result)


async def stream_text(
    model: LanguageModel,
    *,
    system: Optional[str] = None,
    prompt: Optional[str] = None,
    messages: Optional[List[Message]] = None,
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    top_k: Optional[int] = None,
    frequency_penalty: Optional[float] = None,
    presence_penalty: Optional[float] = None,
    stop: Optional[Union[str, List[str]]] = None,
    seed: Optional[int] = None,
    tools: Optional[List[ToolDefinition]] = None,
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
    max_retries: int = 2,
    headers: Optional[Dict[str, str]] = None,
    extra_body: Optional[Dict[str, Any]] = None,
) -> AsyncGenerator[StreamPart, None]:
    """Stream text generation using a language model.
    
    Args:
        Same as generate_text()
        
    Yields:
        StreamPart objects containing incremental generation results
        
    Raises:
        Same as generate_text()
    """
    # Create options and validate
    options = GenerateTextOptions(
        model=model,
        system=system,
        prompt=prompt,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        frequency_penalty=frequency_penalty,
        presence_penalty=presence_penalty,
        stop=stop,
        seed=seed,
        tools=tools,
        tool_choice=tool_choice,
        max_retries=max_retries,
        headers=headers,
        extra_body=extra_body,
    )
    
    # Convert to provider-specific format
    provider_options = _convert_to_stream_options(options)
    
    # Stream from the model
    async for part in model.stream(provider_options):
        yield part


def _convert_to_provider_options(options: GenerateTextOptions) -> GenerateOptions:
    """Convert GenerateTextOptions to provider GenerateOptions."""
    # Build messages list
    messages = []
    
    # Add system message if provided
    if options.system:
        messages.append(Message(role="system", content=options.system))
    
    # Add prompt or messages
    if options.prompt:
        messages.append(Message(role="user", content=options.prompt))
    elif options.messages:
        messages.extend(options.messages)
    
    # Create provider options
    return GenerateOptions(
        messages=messages,
        max_tokens=options.max_tokens,
        temperature=options.temperature,
        top_p=options.top_p,
        top_k=options.top_k,
        frequency_penalty=options.frequency_penalty,
        presence_penalty=options.presence_penalty,
        stop=options.stop,
        seed=options.seed,
        tools=options.tools,
        tool_choice=options.tool_choice,
        headers=options.headers,
        extra_body=options.extra_body,
    )


def _convert_to_stream_options(options: GenerateTextOptions) -> StreamOptions:
    """Convert GenerateTextOptions to provider StreamOptions."""
    provider_options = _convert_to_provider_options(options)
    return StreamOptions(**provider_options.model_dump())


def _convert_from_provider_result(result: GenerateResult) -> GenerateTextResult:
    """Convert provider GenerateResult to GenerateTextResult."""
    # Extract text from content
    text_parts = []
    for content_item in result.content:
        if hasattr(content_item, 'text') and content_item.text:
            text_parts.append(content_item.text)
    
    text = ''.join(text_parts)
    
    return GenerateTextResult(
        text=text,
        content=result.content,
        finish_reason=result.finish_reason,
        usage=result.usage,
        provider_metadata=result.provider_metadata.data if result.provider_metadata else None,
        request_metadata=result.request_metadata,
        response_metadata=result.response_metadata,
    )