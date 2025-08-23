"""Core tool definitions for AI SDK Python."""

from __future__ import annotations

import asyncio
from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Callable, Dict, Generic, List, Optional, TypeVar, Union

from pydantic import BaseModel, Field

from ..providers.types import Message

# Type variables for input/output types
INPUT = TypeVar("INPUT")
OUTPUT = TypeVar("OUTPUT")
T = TypeVar("T")


class ToolCallOptions(BaseModel):
    """Options passed to tool execution functions."""

    tool_call_id: str
    """The ID of the tool call."""

    messages: List[Message]
    """Messages that were sent to the language model."""

    experimental_context: Optional[Any] = None
    """Additional context for the tool call."""


class ToolCall(BaseModel, Generic[T]):
    """A tool call made by the language model."""

    type: str = "call"
    """Type of the tool call."""

    tool_call_id: str
    """ID of the tool call."""

    tool_name: str
    """Name of the tool being called."""

    input: T
    """Arguments for the tool call."""

    provider_executed: bool = False
    """Whether the tool call was executed by the provider."""

    dynamic: bool = False
    """Whether the tool is dynamic."""

    invalid: bool = False
    """Whether the tool call is invalid."""

    error: Optional[Exception] = None
    """Error if the tool call is invalid."""


class ToolResult(BaseModel, Generic[T]):
    """Result of a tool execution."""

    type: str  # "result" or "error"
    """Type of the result."""

    tool_call_id: str
    """ID of the tool call."""

    tool_name: str
    """Name of the tool that was called."""

    input: Any
    """Arguments that were passed to the tool."""

    output: Optional[T] = None
    """Result of the tool execution (if type is "result")."""

    error: Optional[str] = None
    """Error message (if type is "error")."""

    provider_executed: bool = False
    """Whether the tool was executed by the provider."""

    dynamic: bool = False
    """Whether the tool is dynamic."""


# Tool execute function type
ToolExecuteFunction = Callable[[INPUT, ToolCallOptions], Union[OUTPUT, AsyncGenerator[OUTPUT, None]]]


class Tool(BaseModel, Generic[INPUT, OUTPUT]):
    """A tool that can be called by the language model."""

    name: str
    """Name of the tool."""

    description: str
    """Description of what the tool does."""

    input_schema: Dict[str, Any]
    """JSON schema for the tool's input parameters."""

    execute: Optional[ToolExecuteFunction[INPUT, OUTPUT]] = None
    """Function to execute when the tool is called."""

    output_schema: Optional[Dict[str, Any]] = None
    """JSON schema for the tool's output."""

    provider_options: Optional[Dict[str, Any]] = None
    """Provider-specific options."""

    tool_type: str = "function"
    """Type of the tool ('function', 'dynamic', or 'provider-defined')."""

    # Callback functions for streaming
    on_input_start: Optional[Callable[[ToolCallOptions], Union[None, Any]]] = None
    """Called when argument streaming starts."""

    on_input_delta: Optional[Callable[[str, ToolCallOptions], Union[None, Any]]] = None
    """Called when an argument streaming delta is available."""

    on_input_available: Optional[Callable[[INPUT, ToolCallOptions], Union[None, Any]]] = None
    """Called when a tool call can be started."""

    class Config:
        arbitrary_types_allowed = True

    def to_definition(self) -> Dict[str, Any]:
        """Convert to a tool definition for the language model."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.input_schema,
        }

    async def execute_async(self, input_data: INPUT, options: ToolCallOptions) -> OUTPUT:
        """Execute the tool asynchronously."""
        if not self.execute:
            raise ValueError(f"Tool '{self.name}' does not have an execute function")

        try:
            result = self.execute(input_data, options)
            
            # Handle async generators
            if hasattr(result, '__aiter__'):
                # Collect all results from the async generator
                results = []
                async for item in result:
                    results.append(item)
                return results[-1] if results else None
            
            # Handle regular coroutines
            elif asyncio.iscoroutine(result):
                return await result
            
            # Handle sync results
            else:
                return result
                
        except Exception as e:
            raise ValueError(f"Tool execution failed: {e}") from e


def tool(
    name: str,
    description: str,
    input_schema: Dict[str, Any],
    execute: Optional[ToolExecuteFunction[INPUT, OUTPUT]] = None,
    output_schema: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Tool[INPUT, OUTPUT]:
    """Create a tool with the given parameters.
    
    Args:
        name: Name of the tool
        description: Description of what the tool does
        input_schema: JSON schema for input parameters
        execute: Function to execute when tool is called
        output_schema: JSON schema for output
        **kwargs: Additional tool options
        
    Returns:
        A configured Tool instance
    """
    return Tool[INPUT, OUTPUT](
        name=name,
        description=description,
        input_schema=input_schema,
        execute=execute,
        output_schema=output_schema,
        **kwargs,
    )


def dynamic_tool(
    description: str,
    input_schema: Dict[str, Any],
    execute: ToolExecuteFunction[Any, Any],
    name: Optional[str] = None,
    **kwargs: Any,
) -> Tool[Any, Any]:
    """Create a dynamic tool with runtime-determined types.
    
    Args:
        description: Description of what the tool does
        input_schema: JSON schema for input parameters
        execute: Function to execute when tool is called
        name: Optional name for the tool
        **kwargs: Additional tool options
        
    Returns:
        A configured dynamic Tool instance
    """
    return Tool[Any, Any](
        name=name or "dynamic_tool",
        description=description,
        input_schema=input_schema,
        execute=execute,
        tool_type="dynamic",
        **kwargs,
    )


# Utility functions for common tool patterns

def simple_tool(
    name: str,
    description: str,
    parameters: Dict[str, Any],
) -> Callable[[ToolExecuteFunction[INPUT, OUTPUT]], Tool[INPUT, OUTPUT]]:
    """Decorator to create a simple tool from a function.
    
    Args:
        name: Name of the tool
        description: Description of what the tool does
        parameters: JSON schema for parameters
        
    Returns:
        Decorator function that creates a Tool
        
    Example:
        @simple_tool("get_weather", "Get weather for a location", {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "The location to get weather for"}
            },
            "required": ["location"]
        })
        async def weather_tool(input_data: dict, options: ToolCallOptions) -> dict:
            return {"weather": f"Sunny in {input_data['location']}"}
    """
    def decorator(func: ToolExecuteFunction[INPUT, OUTPUT]) -> Tool[INPUT, OUTPUT]:
        return tool(
            name=name,
            description=description,
            input_schema=parameters,
            execute=func,
        )
    return decorator


class ToolRegistry:
    """Registry for managing multiple tools."""

    def __init__(self):
        self._tools: Dict[str, Tool] = {}

    def register(self, tool_instance: Tool) -> None:
        """Register a tool in the registry."""
        self._tools[tool_instance.name] = tool_instance

    def unregister(self, name: str) -> None:
        """Unregister a tool by name."""
        if name in self._tools:
            del self._tools[name]

    def get(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self._tools.get(name)

    def list_tools(self) -> List[Tool]:
        """Get all registered tools."""
        return list(self._tools.values())

    def to_definitions(self) -> List[Dict[str, Any]]:
        """Convert all tools to definitions for the language model."""
        return [tool.to_definition() for tool in self._tools.values()]

    def __len__(self) -> int:
        """Get the number of registered tools."""
        return len(self._tools)

    def __contains__(self, name: str) -> bool:
        """Check if a tool is registered."""
        return name in self._tools