"""Object generation functionality for AI SDK Python."""

import asyncio
import json
from typing import Any, Dict, List, Optional, TypeVar, Union, Generic, Type

from pydantic import BaseModel, ValidationError

from ..errors.base import AISDKError, NoObjectGeneratedError
from ..providers.base import LanguageModel
from ..providers.types import (
    Message,
    Usage,
    FinishReason,
    ToolDefinition,
    Content,
)
from .generate_text import generate_text, GenerateTextResult

T = TypeVar("T", bound=BaseModel)


class GenerateObjectResult(BaseModel, Generic[T]):
    """Result of a generate_object call."""

    object: T
    """The generated object (typed according to the schema)."""

    reasoning: Optional[str] = None
    """The reasoning that was used to generate the object."""

    finish_reason: FinishReason
    """The reason why the generation finished."""

    usage: Usage
    """The token usage of the generated object generation."""

    provider_metadata: Optional[Dict[str, Any]] = None
    """Additional provider-specific metadata."""

    request_metadata: Optional[Dict[str, Any]] = None
    """Additional request metadata."""

    response_metadata: Optional[Dict[str, Any]] = None
    """Additional response metadata."""

    def model_dump_json(self, **kwargs) -> str:
        """Convert the result to JSON, making the object serializable."""
        data = self.model_dump(**kwargs)
        # Convert the object to a dictionary if it's a Pydantic model
        if hasattr(data["object"], "model_dump"):
            data["object"] = data["object"].model_dump()
        return json.dumps(data)


async def generate_object(
    model: LanguageModel,
    *,
    schema: Type[T],
    prompt: Optional[str] = None,
    messages: Optional[List[Message]] = None,
    system: Optional[str] = None,
    schema_name: Optional[str] = None,
    schema_description: Optional[str] = None,
    mode: str = "json",
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    top_k: Optional[int] = None,
    frequency_penalty: Optional[float] = None,
    presence_penalty: Optional[float] = None,
    stop_sequences: Optional[List[str]] = None,
    seed: Optional[int] = None,
    max_retries: int = 2,
    tools: Optional[List[ToolDefinition]] = None,
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
    headers: Optional[Dict[str, str]] = None,
    extra_body: Optional[Dict[str, Any]] = None,
) -> GenerateObjectResult[T]:
    """Generate a structured, typed object for a given prompt and schema using a language model.

    This function does not stream the output. If you want to stream the output, use `stream_object` instead.

    Args:
        model: The language model to use.
        schema: The Pydantic model class that defines the structure of the object to generate.
        prompt: A simple text prompt. You can either use `prompt` or `messages` but not both.
        messages: A list of messages. You can either use `prompt` or `messages` but not both.
        system: A system message that will be part of the prompt.
        schema_name: Optional name of the output that should be generated.
        schema_description: Optional description of the output that should be generated.
        mode: The mode to use for object generation ('json', 'tool', or 'auto').
        max_tokens: Maximum number of tokens to generate.
        temperature: Temperature setting (0.0 to 2.0).
        top_p: Nucleus sampling parameter (0.0 to 1.0).
        top_k: Top-k sampling parameter.
        frequency_penalty: Frequency penalty setting.
        presence_penalty: Presence penalty setting.
        stop_sequences: Stop sequences to end generation.
        seed: Random seed for deterministic generation.
        max_retries: Maximum number of retries on failure.
        timeout_seconds: Timeout for the request in seconds.
        tools: Tools available to the model.
        **kwargs: Additional keyword arguments passed to the provider.

    Returns:
        A GenerateObjectResult containing the generated object and metadata.

    Raises:
        AISDKError: If object generation fails.
        NoObjectGeneratedError: If no valid object could be generated.
        ValidationError: If the generated object doesn't match the schema.
    """
    # Validate input
    if prompt is not None and messages is not None:
        raise AISDKError("Cannot specify both 'prompt' and 'messages'")
    if prompt is None and messages is None:
        raise AISDKError("Must specify either 'prompt' or 'messages'")

    # Configuration will be passed directly to generate_text

    # Generate JSON schema from Pydantic model
    json_schema = schema.model_json_schema()
    schema_name = schema_name or schema.__name__
    schema_description = schema_description or schema.__doc__ or f"Generate a {schema_name}"

    # Prepare the prompt for JSON generation
    if mode == "json":
        json_instruction = f"""You must respond with valid JSON that matches this schema:
{json.dumps(json_schema, indent=2)}

The response must be a valid JSON object that can be parsed and validated against the schema.
Only return the JSON object, no additional text or formatting."""

        if prompt:
            final_prompt = f"{prompt}\n\n{json_instruction}"
        else:
            # Add instruction to last user message
            final_messages = messages.copy() if messages else []
            if final_messages and final_messages[-1].role == "user":
                final_messages[-1] = Message(
                    role="user",
                    content=f"{final_messages[-1].content}\n\n{json_instruction}",
                )
            else:
                final_messages.append(Message(role="user", content=json_instruction))
            messages = final_messages
            prompt = None

    elif mode == "tool":
        # TODO: Implement tool-based object generation
        raise AISDKError("Tool mode is not yet implemented")
    elif mode == "auto":
        # For now, default to JSON mode
        mode = "json"
        return await generate_object(
            model=model,
            schema=schema,
            prompt=prompt,
            messages=messages,
            system=system,
            schema_name=schema_name,
            schema_description=schema_description,
            mode="json",
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop_sequences=stop_sequences,
            seed=seed,
            max_retries=max_retries,
            timeout_seconds=timeout_seconds,
            tools=tools,
            **kwargs,
        )

    # Generate text using the underlying generate_text function
    try:
        text_result = await generate_text(
            model=model,
            prompt=final_prompt if prompt else None,
            messages=messages,
            system=system,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            frequency_penalty=frequency_penalty,
            presence_penalty=presence_penalty,
            stop=stop_sequences,
            seed=seed,
            max_retries=max_retries,
            tools=tools,
            tool_choice=tool_choice,
            headers=headers,
            extra_body=extra_body,
        )
    except Exception as e:
        raise AISDKError(f"Failed to generate text for object: {e}") from e

    # Extract JSON from the response
    response_text = text_result.text.strip()
    
    # Try to find JSON in the response (in case there's additional text)
    json_text = _extract_json(response_text)
    
    if not json_text:
        raise NoObjectGeneratedError(
            f"No valid JSON found in response: {response_text[:200]}..."
        )

    # Parse and validate the JSON against the schema
    try:
        json_data = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise NoObjectGeneratedError(
            f"Invalid JSON in response: {e}. Response: {json_text[:200]}..."
        ) from e

    # Validate against Pydantic schema
    try:
        validated_object = schema.model_validate(json_data)
    except ValidationError as e:
        raise NoObjectGeneratedError(
            f"Generated object doesn't match schema: {e}. Object: {json_data}"
        ) from e

    # Extract reasoning if available (for models that support it)
    reasoning = None
    if hasattr(text_result, "reasoning"):
        reasoning = text_result.reasoning

    return GenerateObjectResult[T](
        object=validated_object,
        reasoning=reasoning,
        finish_reason=text_result.finish_reason,
        usage=text_result.usage,
        provider_metadata=text_result.provider_metadata,
        request_metadata=text_result.request_metadata,
        response_metadata=text_result.response_metadata,
    )


def _extract_json(text: str) -> Optional[str]:
    """Extract JSON from text, handling common cases where models include extra text."""
    text = text.strip()
    
    # If the entire text is JSON, return it
    if text.startswith(("{", "[")):
        return text
    
    # Look for JSON blocks in markdown
    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        if end != -1:
            return text[start:end].strip()
    
    # Look for JSON blocks without markdown
    if "```" in text:
        start = text.find("```") + 3
        end = text.find("```", start)
        if end != -1:
            json_candidate = text[start:end].strip()
            if json_candidate.startswith(("{", "[")):
                return json_candidate
    
    # Look for JSON objects/arrays in the text
    brace_start = text.find("{")
    bracket_start = text.find("[")
    
    start_pos = -1
    is_object = True
    
    if brace_start != -1 and bracket_start != -1:
        start_pos = min(brace_start, bracket_start)
        is_object = brace_start < bracket_start
    elif brace_start != -1:
        start_pos = brace_start
        is_object = True
    elif bracket_start != -1:
        start_pos = bracket_start
        is_object = False
    
    if start_pos == -1:
        return None
    
    # Find the matching closing brace/bracket
    text_from_start = text[start_pos:]
    open_char = "{" if is_object else "["
    close_char = "}" if is_object else "]"
    
    count = 0
    end_pos = -1
    
    for i, char in enumerate(text_from_start):
        if char == open_char:
            count += 1
        elif char == close_char:
            count -= 1
            if count == 0:
                end_pos = start_pos + i + 1
                break
    
    if end_pos != -1:
        return text[start_pos:end_pos]
    
    return None


# Convenience function for synchronous usage
def generate_object_sync(
    model: LanguageModel,
    *,
    schema: Type[T],
    **kwargs: Any,
) -> GenerateObjectResult[T]:
    """Synchronous wrapper for generate_object."""
    return asyncio.run(generate_object(model, schema=schema, **kwargs))