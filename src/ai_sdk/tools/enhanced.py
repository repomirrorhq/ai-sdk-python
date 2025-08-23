"""Enhanced tool system with improved schema support and streaming."""

from __future__ import annotations

import asyncio
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union, Generic, Type
from pydantic import BaseModel

from .core import ToolCallOptions, ToolExecuteFunction
from .schema_enhanced import FlexibleSchema, normalize_schema, validate_schema_input, extract_schema_info

T = TypeVar("T")
INPUT = TypeVar("INPUT")
OUTPUT = TypeVar("OUTPUT")


class StreamingCallbacks:
    """Callbacks for streaming tool interactions."""
    
    def __init__(
        self,
        on_input_start: Optional[Callable[[ToolCallOptions], None]] = None,
        on_input_delta: Optional[Callable[[str, ToolCallOptions], None]] = None,
        on_input_available: Optional[Callable[[Any, ToolCallOptions], None]] = None
    ) -> None:
        """Initialize streaming callbacks.
        
        Args:
            on_input_start: Called when tool argument streaming starts
            on_input_delta: Called for each argument streaming delta
            on_input_available: Called when complete input is available
        """
        self.on_input_start = on_input_start
        self.on_input_delta = on_input_delta  
        self.on_input_available = on_input_available
    
    async def trigger_input_start(self, options: ToolCallOptions) -> None:
        """Trigger the input start callback."""
        if self.on_input_start:
            if asyncio.iscoroutinefunction(self.on_input_start):
                await self.on_input_start(options)
            else:
                self.on_input_start(options)
    
    async def trigger_input_delta(self, delta: str, options: ToolCallOptions) -> None:
        """Trigger the input delta callback."""
        if self.on_input_delta:
            if asyncio.iscoroutinefunction(self.on_input_delta):
                await self.on_input_delta(delta, options)
            else:
                self.on_input_delta(delta, options)
    
    async def trigger_input_available(self, input_data: Any, options: ToolCallOptions) -> None:
        """Trigger the input available callback."""
        if self.on_input_available:
            if asyncio.iscoroutinefunction(self.on_input_available):
                await self.on_input_available(input_data, options)
            else:
                self.on_input_available(input_data, options)


class EnhancedTool(BaseModel, Generic[INPUT, OUTPUT]):
    """Enhanced tool with flexible schema support and streaming callbacks."""
    
    name: str
    """Name of the tool."""
    
    description: str
    """Description of what the tool does."""
    
    input_schema: FlexibleSchema
    """Schema for tool input (flexible format)."""
    
    output_schema: Optional[FlexibleSchema] = None
    """Schema for tool output (optional)."""
    
    execute: Optional[ToolExecuteFunction[INPUT, OUTPUT]] = None
    """Function to execute when tool is called."""
    
    tool_type: str = "function"
    """Type of tool: 'function', 'dynamic', or 'provider-defined'."""
    
    streaming_callbacks: Optional[StreamingCallbacks] = None
    """Callbacks for streaming interactions."""
    
    provider_options: Optional[Dict[str, Any]] = None
    """Provider-specific options."""
    
    # Provider-defined tool fields
    provider_id: Optional[str] = None
    """Provider ID for provider-defined tools (format: provider.tool_name)."""
    
    provider_args: Optional[Dict[str, Any]] = None
    """Provider-specific configuration args."""
    
    # Result conversion
    result_converter: Optional[Callable[[OUTPUT], Any]] = None
    """Function to convert tool output for model consumption."""
    
    class Config:
        arbitrary_types_allowed = True
    
    def get_json_schema(self) -> Dict[str, Any]:
        """Get the JSON schema for this tool's input."""
        return normalize_schema(self.input_schema)
    
    def get_output_json_schema(self) -> Optional[Dict[str, Any]]:
        """Get the JSON schema for this tool's output."""
        if self.output_schema:
            return normalize_schema(self.output_schema)
        return None
    
    def get_tool_info(self) -> Dict[str, Any]:
        """Get comprehensive tool information."""
        info = extract_schema_info(self.input_schema)
        info.update({
            "name": self.name,
            "description": self.description,
            "type": self.tool_type,
            "json_schema": self.get_json_schema(),
        })
        
        if self.output_schema:
            info["output_schema"] = self.get_output_json_schema()
        
        if self.provider_id:
            info["provider_id"] = self.provider_id
        
        return info
    
    def validate_input(self, input_data: Any) -> Any:
        """Validate and potentially transform input data."""
        return validate_schema_input(input_data, self.input_schema)
    
    def validate_output(self, output_data: Any) -> Any:
        """Validate and potentially transform output data."""
        if self.output_schema:
            return validate_schema_input(output_data, self.output_schema)
        return output_data
    
    def convert_result_for_model(self, result: OUTPUT) -> Any:
        """Convert tool result for model consumption."""
        if self.result_converter:
            return self.result_converter(result)
        
        # Default conversion
        if isinstance(result, BaseModel):
            return result.model_dump()
        elif hasattr(result, '__dict__'):
            return result.__dict__
        else:
            return result
    
    async def execute_with_callbacks(
        self, 
        input_data: INPUT, 
        options: ToolCallOptions
    ) -> OUTPUT:
        """Execute the tool with streaming callbacks."""
        if not self.execute:
            raise ValueError(f"Tool '{self.name}' has no execute function")
        
        # Trigger input available callback
        if self.streaming_callbacks:
            await self.streaming_callbacks.trigger_input_available(input_data, options)
        
        # Execute the tool
        if asyncio.iscoroutinefunction(self.execute):
            result = await self.execute(input_data, options)
        else:
            result = self.execute(input_data, options)
        
        # Validate output if schema is provided
        if self.output_schema:
            result = self.validate_output(result)
        
        return result
    
    def to_definition(self) -> Dict[str, Any]:
        """Convert to a tool definition for language models."""
        definition = {
            "name": self.name,
            "description": self.description,
            "parameters": self.get_json_schema(),
        }
        
        if self.tool_type == "provider-defined" and self.provider_id:
            definition["provider_id"] = self.provider_id
            if self.provider_args:
                definition["provider_args"] = self.provider_args
        
        return definition


def enhanced_tool(
    name: str,
    description: str,
    input_schema: FlexibleSchema,
    output_schema: Optional[FlexibleSchema] = None,
    tool_type: str = "function",
    streaming_callbacks: Optional[StreamingCallbacks] = None,
    provider_options: Optional[Dict[str, Any]] = None,
    result_converter: Optional[Callable[[Any], Any]] = None,
) -> Callable:
    """Decorator to create an enhanced tool from a function.
    
    Args:
        name: Name of the tool
        description: Description of what the tool does
        input_schema: Schema for input validation (flexible format)
        output_schema: Schema for output validation (optional)
        tool_type: Type of tool ('function', 'dynamic', 'provider-defined')
        streaming_callbacks: Callbacks for streaming interactions
        provider_options: Provider-specific options
        result_converter: Function to convert results for model
        
    Returns:
        Decorated function that creates an EnhancedTool
    """
    def decorator(func: ToolExecuteFunction) -> EnhancedTool:
        return EnhancedTool(
            name=name,
            description=description,
            input_schema=input_schema,
            output_schema=output_schema,
            execute=func,
            tool_type=tool_type,
            streaming_callbacks=streaming_callbacks,
            provider_options=provider_options,
            result_converter=result_converter,
        )
    
    return decorator


def pydantic_tool(
    input_model: Type[BaseModel],
    output_model: Optional[Type[BaseModel]] = None,
    name: Optional[str] = None,
    description: Optional[str] = None,
    streaming_callbacks: Optional[StreamingCallbacks] = None,
) -> Callable:
    """Decorator to create a tool from Pydantic models.
    
    Args:
        input_model: Pydantic model for input validation
        output_model: Pydantic model for output validation (optional)
        name: Tool name (defaults to input_model.__name__)
        description: Tool description
        streaming_callbacks: Callbacks for streaming interactions
        
    Returns:
        Decorated function that creates an EnhancedTool
    """
    tool_name = name or input_model.__name__.lower()
    tool_description = description or input_model.__doc__ or f"Tool using {input_model.__name__}"
    
    def decorator(func: ToolExecuteFunction) -> EnhancedTool:
        return EnhancedTool(
            name=tool_name,
            description=tool_description,
            input_schema=input_model,
            output_schema=output_model,
            execute=func,
            streaming_callbacks=streaming_callbacks,
        )
    
    return decorator


def provider_defined_tool(
    provider_id: str,
    provider_args: Dict[str, Any],
    name: str,
    description: str,
) -> EnhancedTool:
    """Create a provider-defined tool.
    
    Args:
        provider_id: Provider identifier (format: provider.tool_name)  
        provider_args: Provider-specific configuration
        name: Name to use in tool set
        description: Description of the tool
        
    Returns:
        EnhancedTool configured for provider execution
    """
    return EnhancedTool(
        name=name,
        description=description,
        input_schema=provider_args.get("input_schema", {}),
        output_schema=provider_args.get("output_schema"),
        tool_type="provider-defined",
        provider_id=provider_id,
        provider_args=provider_args,
    )


def dynamic_enhanced_tool(
    description: str,
    input_schema: FlexibleSchema,
    streaming_callbacks: Optional[StreamingCallbacks] = None,
) -> Callable:
    """Create a dynamic tool that can be determined at runtime.
    
    Args:
        description: Description of what the tool does
        input_schema: Schema for input validation
        streaming_callbacks: Callbacks for streaming interactions
        
    Returns:
        Decorator function
    """
    def decorator(func: ToolExecuteFunction) -> EnhancedTool:
        return EnhancedTool(
            name=func.__name__,
            description=description,
            input_schema=input_schema,
            execute=func,
            tool_type="dynamic",
            streaming_callbacks=streaming_callbacks,
        )
    
    return decorator


# Example usage
if __name__ == "__main__":
    from pydantic import Field
    
    # Example with Pydantic model
    class WeatherInput(BaseModel):
        location: str = Field(description="The location to get weather for")
        units: str = Field(default="celsius", description="Temperature units")
    
    class WeatherOutput(BaseModel):
        temperature: float
        conditions: str
        humidity: float
    
    @pydantic_tool(
        input_model=WeatherInput,
        output_model=WeatherOutput,
        name="get_weather",
        description="Get current weather for a location"
    )
    async def get_weather(input_data: WeatherInput, options: ToolCallOptions) -> WeatherOutput:
        # Simulate weather API call
        return WeatherOutput(
            temperature=22.5,
            conditions="sunny",
            humidity=65.0
        )
    
    # Example with streaming callbacks
    def on_start(options: ToolCallOptions):
        print(f"Starting tool call {options.toolCallId}")
    
    def on_delta(delta: str, options: ToolCallOptions):
        print(f"Input delta: {delta}")
    
    callbacks = StreamingCallbacks(
        on_input_start=on_start,
        on_input_delta=on_delta
    )
    
    @enhanced_tool(
        name="calculate",
        description="Perform mathematical calculations",
        input_schema={"type": "object", "properties": {"expression": {"type": "string"}}},
        streaming_callbacks=callbacks
    )
    def calculate(input_data: Dict[str, Any], options: ToolCallOptions) -> float:
        return eval(input_data["expression"])  # Don't do this in production!
    
    print("Enhanced tools created successfully!")
    print(f"Weather tool schema: {get_weather.get_json_schema()}")
    print(f"Calculator tool info: {calculate.get_tool_info()}")