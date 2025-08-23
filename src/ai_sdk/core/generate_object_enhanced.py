"""Enhanced object generation with advanced features."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Literal, Optional, Type, TypeVar, Union

from pydantic import BaseModel, ValidationError

from ..errors.base import AISDKError, NoObjectGeneratedError
from ..providers.base import LanguageModel
from ..providers.types import Message, Usage, FinishReason, ToolDefinition
from .generate_text import generate_text
from .object_repair import TextRepairFunction, parse_with_repair, create_default_repair_function

T = TypeVar("T", bound=BaseModel)


class EnhancedGenerateObjectResult(BaseModel, Generic[T]):
    """Enhanced result from object generation."""
    
    object: Optional[T] = None
    """The generated object (for object output)."""
    
    array: Optional[List[T]] = None
    """The generated array (for array output)."""
    
    enum_value: Optional[str] = None
    """The selected enum value (for enum output)."""
    
    raw_content: Optional[str] = None
    """Raw content from model (for no-schema output)."""
    
    reasoning: Optional[str] = None
    """Reasoning used to generate the object."""
    
    finish_reason: FinishReason
    """Why the generation finished."""
    
    usage: Usage
    """Token usage information."""
    
    provider_metadata: Optional[Dict[str, Any]] = None
    """Provider-specific metadata."""
    
    request_metadata: Optional[Dict[str, Any]] = None
    """Request metadata."""
    
    response_metadata: Optional[Dict[str, Any]] = None
    """Response metadata."""
    
    repair_attempts: int = 0
    """Number of repair attempts made."""
    
    repaired_content: Optional[str] = None
    """Content after repair attempts."""


async def generate_object_enhanced(
    model: LanguageModel,
    *,
    # Schema and output configuration
    schema: Optional[Type[T]] = None,
    output: Literal['object', 'array', 'enum', 'no-schema'] = 'object',
    enum_values: Optional[List[str]] = None,
    
    # Prompt configuration
    prompt: Optional[str] = None,
    messages: Optional[List[Message]] = None,
    system: Optional[str] = None,
    
    # Schema metadata
    schema_name: Optional[str] = None,
    schema_description: Optional[str] = None,
    
    # Generation mode
    mode: Literal['auto', 'json', 'tool'] = 'auto',
    
    # Model parameters
    max_tokens: Optional[int] = None,
    temperature: Optional[float] = None,
    top_p: Optional[float] = None,
    top_k: Optional[int] = None,
    frequency_penalty: Optional[float] = None,
    presence_penalty: Optional[float] = None,
    stop: Optional[Union[str, List[str]]] = None,
    seed: Optional[int] = None,
    
    # Repair and error handling
    repair_function: Optional[TextRepairFunction] = None,
    max_repair_attempts: int = 3,
    max_retries: int = 2,
    
    # Additional options
    tools: Optional[List[ToolDefinition]] = None,
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
    headers: Optional[Dict[str, str]] = None,
    extra_body: Optional[Dict[str, Any]] = None,
) -> EnhancedGenerateObjectResult[T]:
    """Generate structured objects with enhanced features.
    
    Args:
        model: Language model to use
        schema: Pydantic model for object/array output
        output: Type of output ('object', 'array', 'enum', 'no-schema')
        enum_values: Available values for enum output
        prompt: Simple text prompt
        messages: List of messages
        system: System message
        schema_name: Name of the output schema
        schema_description: Description of the output
        mode: Generation mode ('auto', 'json', 'tool')
        repair_function: Function to repair malformed JSON
        max_repair_attempts: Maximum repair attempts
        ...: Other generation parameters
        
    Returns:
        EnhancedGenerateObjectResult with the generated output
        
    Raises:
        AISDKError: If generation fails
        ValidationError: If output doesn't match schema
    """
    # Validate inputs
    if prompt is not None and messages is not None:
        raise AISDKError("Cannot specify both 'prompt' and 'messages'")
    if prompt is None and messages is None:
        raise AISDKError("Must specify either 'prompt' or 'messages'")
    
    if output in ['object', 'array'] and schema is None:
        raise AISDKError(f"Schema is required for output type '{output}'")
    
    if output == 'enum' and not enum_values:
        raise AISDKError("enum_values is required for output type 'enum'")
    
    # Set up repair function
    repair_func = repair_function or create_default_repair_function()
    
    # Handle different output types
    if output == 'object':
        return await _generate_object(
            model=model, schema=schema, mode=mode, repair_func=repair_func,
            max_repair_attempts=max_repair_attempts, prompt=prompt, messages=messages,
            system=system, schema_name=schema_name, schema_description=schema_description,
            max_tokens=max_tokens, temperature=temperature, top_p=top_p, top_k=top_k,
            frequency_penalty=frequency_penalty, presence_penalty=presence_penalty,
            stop=stop, seed=seed, max_retries=max_retries, tools=tools, 
            tool_choice=tool_choice, headers=headers, extra_body=extra_body
        )
    
    elif output == 'array':
        return await _generate_array(
            model=model, schema=schema, mode=mode, repair_func=repair_func,
            max_repair_attempts=max_repair_attempts, prompt=prompt, messages=messages,
            system=system, schema_name=schema_name, schema_description=schema_description,
            max_tokens=max_tokens, temperature=temperature, top_p=top_p, top_k=top_k,
            frequency_penalty=frequency_penalty, presence_penalty=presence_penalty,
            stop=stop, seed=seed, max_retries=max_retries, tools=tools,
            tool_choice=tool_choice, headers=headers, extra_body=extra_body
        )
    
    elif output == 'enum':
        return await _generate_enum(
            model=model, enum_values=enum_values, mode=mode,
            prompt=prompt, messages=messages, system=system,
            max_tokens=max_tokens, temperature=temperature, top_p=top_p, top_k=top_k,
            frequency_penalty=frequency_penalty, presence_penalty=presence_penalty,
            stop=stop, seed=seed, max_retries=max_retries, tools=tools,
            tool_choice=tool_choice, headers=headers, extra_body=extra_body
        )
    
    elif output == 'no-schema':
        return await _generate_no_schema(
            model=model, mode=mode,
            prompt=prompt, messages=messages, system=system,
            max_tokens=max_tokens, temperature=temperature, top_p=top_p, top_k=top_k,
            frequency_penalty=frequency_penalty, presence_penalty=presence_penalty,
            stop=stop, seed=seed, max_retries=max_retries, tools=tools,
            tool_choice=tool_choice, headers=headers, extra_body=extra_body
        )
    
    else:
        raise AISDKError(f"Unsupported output type: {output}")


async def _generate_object(
    model: LanguageModel,
    schema: Type[T],
    mode: str,
    repair_func: TextRepairFunction,
    max_repair_attempts: int,
    **kwargs
) -> EnhancedGenerateObjectResult[T]:
    """Generate a single object."""
    json_schema = schema.model_json_schema()
    schema_name = kwargs.get('schema_name') or schema.__name__
    schema_description = kwargs.get('schema_description') or schema.__doc__ or f"Generate a {schema_name}"
    
    # Prepare prompt based on mode
    if mode in ['json', 'auto']:
        instruction = f"""You must respond with valid JSON that matches this schema:
{json.dumps(json_schema, indent=2)}

Schema name: {schema_name}
Description: {schema_description}

The response must be a valid JSON object. Only return the JSON object, no additional text."""
        
        final_prompt, final_messages = _prepare_prompt_with_instruction(
            kwargs.get('prompt'), kwargs.get('messages'), instruction
        )
        
        # Generate text
        result = await generate_text(
            model=model,
            prompt=final_prompt,
            messages=final_messages,
            system=kwargs.get('system'),
            max_tokens=kwargs.get('max_tokens'),
            temperature=kwargs.get('temperature'),
            top_p=kwargs.get('top_p'),
            top_k=kwargs.get('top_k'),
            frequency_penalty=kwargs.get('frequency_penalty'),
            presence_penalty=kwargs.get('presence_penalty'),
            stop=kwargs.get('stop'),
            seed=kwargs.get('seed'),
            max_retries=kwargs.get('max_retries', 2),
            tools=kwargs.get('tools'),
            tool_choice=kwargs.get('tool_choice'),
            headers=kwargs.get('headers'),
            extra_body=kwargs.get('extra_body'),
        )
        
        # Parse and validate with repair
        try:
            obj = await parse_with_repair(
                result.text,
                schema,
                repair_func,
                max_repair_attempts
            )
            
            return EnhancedGenerateObjectResult(
                object=obj,
                reasoning=None,  # Could extract from result if available
                finish_reason=result.finish_reason,
                usage=result.usage,
                provider_metadata=result.provider_metadata,
                request_metadata=result.request_metadata,
                response_metadata=result.response_metadata,
                repair_attempts=0  # Would need to track this in parse_with_repair
            )
            
        except Exception as e:
            raise NoObjectGeneratedError(f"Failed to generate valid object: {e}")
    
    elif mode == 'tool':
        # TODO: Implement tool-based generation
        raise AISDKError("Tool mode not yet implemented")
    
    else:
        raise AISDKError(f"Unsupported mode: {mode}")


async def _generate_array(
    model: LanguageModel,
    schema: Type[T],
    mode: str,
    repair_func: TextRepairFunction,
    max_repair_attempts: int,
    **kwargs
) -> EnhancedGenerateObjectResult[T]:
    """Generate an array of objects."""
    json_schema = schema.model_json_schema()
    schema_name = kwargs.get('schema_name') or schema.__name__
    schema_description = kwargs.get('schema_description') or f"Array of {schema_name}"
    
    # Create array schema
    array_schema = {
        "type": "array",
        "items": json_schema,
        "description": schema_description
    }
    
    instruction = f"""You must respond with a valid JSON array where each item matches this schema:
{json.dumps(json_schema, indent=2)}

Array schema: {json.dumps(array_schema, indent=2)}
Description: {schema_description}

The response must be a valid JSON array. Only return the JSON array, no additional text."""
    
    final_prompt, final_messages = _prepare_prompt_with_instruction(
        kwargs.get('prompt'), kwargs.get('messages'), instruction
    )
    
    # Generate text
    result = await generate_text(
        model=model,
        prompt=final_prompt,
        messages=final_messages,
        system=kwargs.get('system'),
        max_tokens=kwargs.get('max_tokens'),
        temperature=kwargs.get('temperature'),
        top_p=kwargs.get('top_p'),
        top_k=kwargs.get('top_k'),
        frequency_penalty=kwargs.get('frequency_penalty'),
        presence_penalty=kwargs.get('presence_penalty'),
        stop=kwargs.get('stop'),
        seed=kwargs.get('seed'),
        max_retries=kwargs.get('max_retries', 2),
        tools=kwargs.get('tools'),
        tool_choice=kwargs.get('tool_choice'),
        headers=kwargs.get('headers'),
        extra_body=kwargs.get('extra_body'),
    )
    
    # Parse JSON array and validate each item
    try:
        # First repair the JSON if needed
        repaired_text = repair_func.repair(result.text, None, schema)
        text_to_parse = repaired_text if repaired_text else result.text
        
        array_data = json.loads(text_to_parse)
        if not isinstance(array_data, list):
            raise ValidationError("Response is not an array")
        
        # Validate each item
        validated_items = [schema.model_validate(item) for item in array_data]
        
        return EnhancedGenerateObjectResult(
            array=validated_items,
            finish_reason=result.finish_reason,
            usage=result.usage,
            provider_metadata=result.provider_metadata,
            request_metadata=result.request_metadata,
            response_metadata=result.response_metadata,
            repaired_content=repaired_text
        )
        
    except Exception as e:
        raise NoObjectGeneratedError(f"Failed to generate valid array: {e}")


async def _generate_enum(
    model: LanguageModel,
    enum_values: List[str],
    mode: str,
    **kwargs
) -> EnhancedGenerateObjectResult:
    """Generate an enum value."""
    instruction = f"""You must respond with exactly one of these values:
{', '.join(f'"{v}"' for v in enum_values)}

Only return the value itself, no additional text or formatting."""
    
    final_prompt, final_messages = _prepare_prompt_with_instruction(
        kwargs.get('prompt'), kwargs.get('messages'), instruction
    )
    
    # Generate text
    result = await generate_text(
        model=model,
        prompt=final_prompt,
        messages=final_messages,
        system=kwargs.get('system'),
        max_tokens=kwargs.get('max_tokens'),
        temperature=kwargs.get('temperature'),
        top_p=kwargs.get('top_p'),
        top_k=kwargs.get('top_k'),
        frequency_penalty=kwargs.get('frequency_penalty'),
        presence_penalty=kwargs.get('presence_penalty'),
        stop=kwargs.get('stop'),
        seed=kwargs.get('seed'),
        max_retries=kwargs.get('max_retries', 2),
        tools=kwargs.get('tools'),
        tool_choice=kwargs.get('tool_choice'),
        headers=kwargs.get('headers'),
        extra_body=kwargs.get('extra_body'),
    )
    
    # Find the matching enum value
    response_text = result.text.strip().strip('"\'')
    matching_value = None
    
    for value in enum_values:
        if value.lower() == response_text.lower():
            matching_value = value
            break
    
    if matching_value is None:
        # Try partial matching
        for value in enum_values:
            if value.lower() in response_text.lower() or response_text.lower() in value.lower():
                matching_value = value
                break
    
    if matching_value is None:
        raise NoObjectGeneratedError(
            f"Generated value '{response_text}' does not match any of the allowed enum values: {enum_values}"
        )
    
    return EnhancedGenerateObjectResult(
        enum_value=matching_value,
        finish_reason=result.finish_reason,
        usage=result.usage,
        provider_metadata=result.provider_metadata,
        request_metadata=result.request_metadata,
        response_metadata=result.response_metadata,
    )


async def _generate_no_schema(
    model: LanguageModel,
    mode: str,
    **kwargs
) -> EnhancedGenerateObjectResult:
    """Generate without schema validation."""
    # Just generate text normally
    result = await generate_text(
        model=model,
        prompt=kwargs.get('prompt'),
        messages=kwargs.get('messages'),
        system=kwargs.get('system'),
        max_tokens=kwargs.get('max_tokens'),
        temperature=kwargs.get('temperature'),
        top_p=kwargs.get('top_p'),
        top_k=kwargs.get('top_k'),
        frequency_penalty=kwargs.get('frequency_penalty'),
        presence_penalty=kwargs.get('presence_penalty'),
        stop=kwargs.get('stop'),
        seed=kwargs.get('seed'),
        max_retries=kwargs.get('max_retries', 2),
        tools=kwargs.get('tools'),
        tool_choice=kwargs.get('tool_choice'),
        headers=kwargs.get('headers'),
        extra_body=kwargs.get('extra_body'),
    )
    
    return EnhancedGenerateObjectResult(
        raw_content=result.text,
        finish_reason=result.finish_reason,
        usage=result.usage,
        provider_metadata=result.provider_metadata,
        request_metadata=result.request_metadata,
        response_metadata=result.response_metadata,
    )


def _prepare_prompt_with_instruction(
    prompt: Optional[str],
    messages: Optional[List[Message]],
    instruction: str
) -> tuple[Optional[str], Optional[List[Message]]]:
    """Prepare prompt with JSON generation instruction."""
    if prompt:
        return f"{prompt}\n\n{instruction}", None
    
    if messages:
        final_messages = messages.copy()
        if final_messages and final_messages[-1].role == "user":
            final_messages[-1] = Message(
                role="user",
                content=f"{final_messages[-1].content}\n\n{instruction}",
            )
        else:
            final_messages.append(Message(role="user", content=instruction))
        return None, final_messages
    
    return instruction, None