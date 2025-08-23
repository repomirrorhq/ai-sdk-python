"""Example demonstrating enhanced tool system with flexible schemas and streaming."""

import asyncio
from typing import List, Optional
from pydantic import BaseModel, Field

from ai_sdk.tools.enhanced import (
    EnhancedTool,
    StreamingCallbacks,
    enhanced_tool,
    pydantic_tool,
    dynamic_enhanced_tool,
    provider_defined_tool,
)
from ai_sdk.tools.schema_enhanced import FlexibleSchema, normalize_schema
from ai_sdk.tools.core import ToolCallOptions


# Example Pydantic models for tool schemas
class WeatherQuery(BaseModel):
    """Query for weather information."""
    location: str = Field(description="The location to get weather for")
    units: str = Field(default="celsius", description="Temperature units (celsius/fahrenheit)")
    include_forecast: bool = Field(default=False, description="Include 5-day forecast")


class WeatherResult(BaseModel):
    """Weather information result."""
    location: str
    temperature: float
    conditions: str
    humidity: float
    forecast: Optional[List[str]] = None


class MathOperation(BaseModel):
    """Mathematical operation input."""
    operation: str = Field(description="The operation: 'add', 'subtract', 'multiply', 'divide'")
    a: float = Field(description="First number")
    b: float = Field(description="Second number")


class MathResult(BaseModel):
    """Mathematical operation result."""
    operation: str
    a: float
    b: float
    result: float


async def pydantic_tool_example():
    """Example using Pydantic models for tool schemas."""
    print("🔹 Pydantic Tool Example")
    print("=" * 50)
    
    @pydantic_tool(
        input_model=WeatherQuery,
        output_model=WeatherResult,
        name="get_weather",
        description="Get current weather and optional forecast for a location"
    )
    async def get_weather(query: WeatherQuery, options: ToolCallOptions) -> WeatherResult:
        """Get weather information for a location."""
        print(f"🌤️  Getting weather for {query.location} in {query.units}")
        
        # Simulate weather API call
        await asyncio.sleep(0.5)
        
        temp = 22.5 if query.units == "celsius" else 72.5
        forecast = None
        if query.include_forecast:
            forecast = ["Sunny", "Partly Cloudy", "Rainy", "Sunny", "Clear"]
        
        return WeatherResult(
            location=query.location,
            temperature=temp,
            conditions="sunny",
            humidity=65.0,
            forecast=forecast
        )
    
    # Test the tool
    options = ToolCallOptions(
        toolCallId="test-1",
        messages=[],
        experimental_context=None
    )
    
    # Test input validation
    try:
        input_data = WeatherQuery(location="San Francisco", units="celsius", include_forecast=True)
        result = await get_weather.execute_with_callbacks(input_data, options)
        
        print(f"Tool Name: {get_weather.name}")
        print(f"Input Schema: {get_weather.get_json_schema()}")
        print(f"Result: {result}")
        print(f"Forecast: {result.forecast}")
    except Exception as e:
        print(f"Error: {e}")
    
    print()


async def streaming_callbacks_example():
    """Example with streaming callbacks for real-time interaction."""
    print("🔹 Streaming Callbacks Example")
    print("=" * 50)
    
    # Define streaming callbacks
    def on_input_start(options: ToolCallOptions):
        print(f"🚀 Starting tool execution for call {options.toolCallId}")
    
    def on_input_delta(delta: str, options: ToolCallOptions):
        print(f"📝 Input delta: {delta}")
    
    async def on_input_available(input_data, options: ToolCallOptions):
        print(f"✅ Complete input available: {input_data}")
    
    callbacks = StreamingCallbacks(
        on_input_start=on_input_start,
        on_input_delta=on_input_delta,
        on_input_available=on_input_available
    )
    
    @enhanced_tool(
        name="calculate",
        description="Perform mathematical operations with streaming feedback",
        input_schema=MathOperation,
        output_schema=MathResult,
        streaming_callbacks=callbacks
    )
    async def calculate(operation: MathOperation, options: ToolCallOptions) -> MathResult:
        """Perform mathematical calculations with streaming updates."""
        print(f"🔢 Computing {operation.a} {operation.operation} {operation.b}")
        
        # Simulate streaming input deltas
        if callbacks:
            await callbacks.trigger_input_delta(f"operation: {operation.operation}", options)
            await callbacks.trigger_input_delta(f"a: {operation.a}", options)
            await callbacks.trigger_input_delta(f"b: {operation.b}", options)
        
        await asyncio.sleep(0.3)  # Simulate processing time
        
        # Perform calculation
        operations = {
            "add": operation.a + operation.b,
            "subtract": operation.a - operation.b,
            "multiply": operation.a * operation.b,
            "divide": operation.a / operation.b if operation.b != 0 else float('inf')
        }
        
        result_value = operations.get(operation.operation, 0)
        
        return MathResult(
            operation=operation.operation,
            a=operation.a,
            b=operation.b,
            result=result_value
        )
    
    # Test the tool with streaming
    options = ToolCallOptions(
        toolCallId="calc-1", 
        messages=[],
        experimental_context={"streaming": True}
    )
    
    # Trigger callbacks
    await callbacks.trigger_input_start(options)
    
    # Execute tool
    input_data = calculate.validate_input({
        "operation": "multiply",
        "a": 15.5,
        "b": 2.0
    })
    
    result = await calculate.execute_with_callbacks(input_data, options)
    
    print(f"Final result: {result.a} {result.operation} {result.b} = {result.result}")
    print()


async def flexible_schema_example():
    """Example showing flexible schema support."""
    print("🔹 Flexible Schema Example")  
    print("=" * 50)
    
    # Test different schema types
    schema_examples = [
        # JSON Schema
        {
            "type": "object",
            "properties": {
                "message": {"type": "string", "description": "Message to echo"},
                "repeat": {"type": "integer", "minimum": 1, "maximum": 5}
            },
            "required": ["message"]
        },
        # Pydantic model
        WeatherQuery,
        # Python types
        str,
        List[str],
    ]
    
    for i, schema in enumerate(schema_examples):
        print(f"Schema {i + 1}: {type(schema)}")
        try:
            json_schema = normalize_schema(schema)
            print(f"  Normalized: {json_schema}")
        except Exception as e:
            print(f"  Error: {e}")
        print()


async def dynamic_tool_example():
    """Example with dynamic tools determined at runtime."""
    print("🔹 Dynamic Tool Example")
    print("=" * 50)
    
    @dynamic_enhanced_tool(
        description="Execute dynamic operations based on runtime configuration",
        input_schema={
            "type": "object",
            "properties": {
                "operation": {"type": "string", "description": "Operation name"},
                "parameters": {"type": "object", "description": "Operation parameters"}
            },
            "required": ["operation"]
        }
    )
    async def dynamic_executor(input_data: dict, options: ToolCallOptions):
        """Execute operations dynamically based on input."""
        operation = input_data.get("operation")
        params = input_data.get("parameters", {})
        
        print(f"🔄 Executing dynamic operation: {operation}")
        print(f"📊 Parameters: {params}")
        
        # Simulate different operations
        if operation == "greet":
            name = params.get("name", "World")
            return f"Hello, {name}!"
        elif operation == "calculate_sum":
            numbers = params.get("numbers", [])
            return sum(numbers)
        elif operation == "analyze_text":
            text = params.get("text", "")
            return {
                "length": len(text),
                "words": len(text.split()),
                "uppercase": text.upper(),
            }
        else:
            return f"Unknown operation: {operation}"
    
    # Test dynamic tool
    options = ToolCallOptions(toolCallId="dynamic-1", messages=[])
    
    test_cases = [
        {
            "operation": "greet",
            "parameters": {"name": "AI Assistant"}
        },
        {
            "operation": "calculate_sum", 
            "parameters": {"numbers": [1, 2, 3, 4, 5]}
        },
        {
            "operation": "analyze_text",
            "parameters": {"text": "Hello World from AI SDK Python!"}
        }
    ]
    
    for test_case in test_cases:
        result = await dynamic_executor.execute_with_callbacks(test_case, options)
        print(f"Input: {test_case}")
        print(f"Result: {result}")
        print()


async def provider_defined_tool_example():
    """Example with provider-defined tools."""
    print("🔹 Provider-Defined Tool Example")
    print("=" * 50)
    
    # Create provider-defined tools (these would typically be created by providers)
    web_search_tool = provider_defined_tool(
        provider_id="search.web_search",
        provider_args={
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "max_results": {"type": "integer", "default": 10}
                },
                "required": ["query"]
            },
            "max_results": 10,
            "safe_search": True
        },
        name="web_search",
        description="Search the web for information"
    )
    
    image_generator_tool = provider_defined_tool(
        provider_id="ai.image_generator",
        provider_args={
            "input_schema": {
                "type": "object", 
                "properties": {
                    "prompt": {"type": "string", "description": "Image generation prompt"},
                    "style": {"type": "string", "enum": ["realistic", "cartoon", "abstract"]},
                    "size": {"type": "string", "enum": ["512x512", "1024x1024"]}
                },
                "required": ["prompt"]
            },
            "model": "dalle-3",
            "quality": "hd"
        },
        name="generate_image",
        description="Generate images from text prompts"
    )
    
    print(f"Web Search Tool:")
    print(f"  Provider ID: {web_search_tool.provider_id}")
    print(f"  Schema: {web_search_tool.get_json_schema()}")
    print(f"  Provider Args: {web_search_tool.provider_args}")
    print()
    
    print(f"Image Generator Tool:")
    print(f"  Provider ID: {image_generator_tool.provider_id}")
    print(f"  Schema: {image_generator_tool.get_json_schema()}")  
    print(f"  Provider Args: {image_generator_tool.provider_args}")
    print()


async def main():
    """Run all enhanced tool examples."""
    print("🚀 Enhanced Tool System Examples")
    print("=" * 60)
    print()
    
    await pydantic_tool_example()
    await streaming_callbacks_example()
    await flexible_schema_example()
    await dynamic_tool_example()
    await provider_defined_tool_example()
    
    print("✅ All enhanced tool examples completed!")


if __name__ == "__main__":
    asyncio.run(main())