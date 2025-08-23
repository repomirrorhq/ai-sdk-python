#!/usr/bin/env python3
"""Comprehensive examples of tool functionality in AI SDK Python."""

import asyncio
import json
from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel, Field

from ai_sdk.core import generate_text
from ai_sdk.providers.openai import OpenAIProvider
from ai_sdk.providers.types import Message, ToolCallContent
from ai_sdk.tools import (
    Tool,
    ToolCallOptions,
    tool,
    simple_tool,
    ToolRegistry,
    execute_tools_from_messages,
    create_tool_schema,
    pydantic_to_tool_schema,
    string_parameter,
    number_parameter,
)


# Example 1: Simple function-based tools

@simple_tool(
    "get_current_time",
    "Get the current date and time",
    create_tool_schema(
        properties={
            "timezone": string_parameter("Timezone (optional)", ["UTC", "EST", "PST"])
        },
        required=[]
    )
)
async def current_time_tool(input_data: dict, options: ToolCallOptions) -> dict:
    """Get the current time, optionally in a specific timezone."""
    timezone = input_data.get("timezone", "UTC")
    now = datetime.now()
    
    return {
        "current_time": now.isoformat(),
        "timezone": timezone,
        "formatted": now.strftime("%Y-%m-%d %H:%M:%S"),
    }


@simple_tool(
    "calculate",
    "Perform basic mathematical calculations",
    create_tool_schema(
        properties={
            "expression": string_parameter("Mathematical expression to evaluate (e.g., '2 + 2', '10 * 5')"),
            "precision": number_parameter("Number of decimal places for result", minimum=0, maximum=10)
        },
        required=["expression"]
    )
)
async def calculator_tool(input_data: dict, options: ToolCallOptions) -> dict:
    """Safely evaluate mathematical expressions."""
    expression = input_data["expression"]
    precision = input_data.get("precision", 2)
    
    # Simple safe evaluation (in production, use a proper math parser)
    try:
        # Only allow basic mathematical operations
        allowed_chars = set("0123456789+-*/.(). ")
        if not all(c in allowed_chars for c in expression):
            raise ValueError("Invalid characters in expression")
        
        result = eval(expression)  # Note: Use ast.literal_eval or similar in production
        
        if isinstance(result, float):
            result = round(result, int(precision))
        
        return {
            "expression": expression,
            "result": result,
            "formatted_result": f"{result:.{int(precision)}f}" if isinstance(result, (int, float)) else str(result)
        }
        
    except Exception as e:
        return {
            "expression": expression,
            "error": f"Calculation failed: {str(e)}",
            "result": None
        }


# Example 2: Pydantic-based tool schemas

class WeatherParams(BaseModel):
    """Parameters for weather lookup."""
    location: str = Field(description="City or location to get weather for")
    units: str = Field(default="celsius", description="Temperature units (celsius or fahrenheit)")
    include_forecast: bool = Field(default=False, description="Whether to include 5-day forecast")


async def weather_tool_function(input_data: WeatherParams, options: ToolCallOptions) -> dict:
    """Mock weather tool that returns fake weather data."""
    # Simulate API call delay
    await asyncio.sleep(0.1)
    
    # Mock weather data
    weather_data = {
        "location": input_data.location,
        "current": {
            "temperature": 22 if input_data.units == "celsius" else 72,
            "units": input_data.units,
            "condition": "Partly cloudy",
            "humidity": 65,
            "wind_speed": 15,
        },
        "forecast": [] if not input_data.include_forecast else [
            {"day": f"Day {i+1}", "high": 25 + i, "low": 18 + i, "condition": "Sunny"}
            for i in range(5)
        ]
    }
    
    return weather_data


# Create tool with Pydantic schema
weather_tool = tool(
    name="get_weather",
    description="Get current weather and optional forecast for a location",
    input_schema=pydantic_to_tool_schema(WeatherParams),
    execute=weather_tool_function,
)


# Example 3: Advanced tool with callbacks

class DatabaseQuery(BaseModel):
    """Parameters for database query."""
    table: str = Field(description="Table name to query")
    columns: list = Field(description="Columns to select")
    where: str = Field(default="", description="WHERE clause (optional)")
    limit: int = Field(default=10, description="Maximum number of rows to return")


async def database_tool_function(input_data: DatabaseQuery, options: ToolCallOptions) -> dict:
    """Mock database query tool."""
    # Simulate query processing
    await asyncio.sleep(0.2)
    
    # Mock query result
    mock_data = [
        {"id": i, "name": f"Item {i}", "value": i * 10}
        for i in range(1, min(input_data.limit + 1, 6))
    ]
    
    return {
        "query": {
            "table": input_data.table,
            "columns": input_data.columns,
            "where": input_data.where,
            "limit": input_data.limit,
        },
        "results": mock_data,
        "count": len(mock_data),
    }


def on_db_input_available(input_data: DatabaseQuery, options: ToolCallOptions):
    """Called when database query input becomes available."""
    print(f"🗄️  Preparing to query table '{input_data.table}' with {len(input_data.columns)} columns")


database_tool = tool(
    name="query_database",
    description="Query a database table with specified columns and conditions",
    input_schema=pydantic_to_tool_schema(DatabaseQuery),
    execute=database_tool_function,
    on_input_available=on_db_input_available,
)


async def main():
    """Run tool examples."""
    print("🔧 Testing AI SDK Python Tool System")
    print("=" * 50)
    
    # Initialize OpenAI provider
    provider = OpenAIProvider(
        api_key="your-openai-api-key",  # Replace with your API key
        base_url="https://api.openai.com/v1"
    )
    
    # Get a language model
    model = provider.language_model("gpt-4o-mini")
    
    # Create tool registry
    registry = ToolRegistry()
    registry.register(current_time_tool)
    registry.register(calculator_tool)
    registry.register(weather_tool)
    registry.register(database_tool)
    
    print(f"📚 Registered {len(registry)} tools:")
    for tool_def in registry.to_definitions():
        print(f"   • {tool_def['name']}: {tool_def['description']}")
    
    # Example 1: Simple tool usage with time
    print("\n⏰ Example 1: Using time tool")
    print("-" * 30)
    
    try:
        # Convert tools to the format expected by generate_text
        tool_definitions = []
        tools_dict = {}
        
        for tool_instance in registry.list_tools():
            tool_definitions.append({
                "name": tool_instance.name,
                "description": tool_instance.description,
                "parameters": tool_instance.input_schema,
            })
            tools_dict[tool_instance.name] = tool_instance
        
        result = await generate_text(
            model=model,
            prompt="What time is it right now?",
            tools=[{"type": "function", "function": def_} for def_ in tool_definitions],
            tool_choice="auto",
            max_tokens=200,
        )
        
        print(f"✅ Model response: {result.text}")
        
        # Check if there are tool calls in the response
        tool_calls = []
        for content in result.content:
            if hasattr(content, 'type') and content.type == "tool-call":
                from ai_sdk.tools import ToolCall
                tool_call = ToolCall(
                    tool_call_id=content.tool_call_id,
                    tool_name=content.tool_name,
                    input=content.args,
                )
                tool_calls.append(tool_call)
        
        if tool_calls:
            print(f"🔧 Executing {len(tool_calls)} tool calls...")
            
            # Execute the tools
            from ai_sdk.tools import execute_tools
            tool_results = await execute_tools(
                tools=tools_dict,
                tool_calls=tool_calls,
                messages=[],  # Empty for this example
            )
            
            for result in tool_results:
                print(f"   📊 {result.tool_name}: {json.dumps(result.output, indent=2)}")
        
    except Exception as e:
        print(f"❌ Error in time example: {e}")
    
    # Example 2: Manual tool execution
    print("\n🧮 Example 2: Manual tool execution")
    print("-" * 35)
    
    try:
        from ai_sdk.tools import ToolCall, execute_tool_call
        
        # Create a manual tool call
        calc_call = ToolCall(
            tool_call_id="calc_001",
            tool_name="calculate",
            input={"expression": "15 * 8 + 7", "precision": 1},
        )
        
        result = await execute_tool_call(
            tools=tools_dict,
            tool_call=calc_call,
            messages=[],
        )
        
        print(f"✅ Calculation result:")
        print(f"   Expression: {result.input['expression']}")
        print(f"   Result: {result.output['result']}")
        print(f"   Formatted: {result.output['formatted_result']}")
        
    except Exception as e:
        print(f"❌ Error in calculation example: {e}")
    
    # Example 3: Weather tool with Pydantic validation
    print("\n🌤️  Example 3: Weather tool with validation")
    print("-" * 40)
    
    try:
        weather_call = ToolCall(
            tool_call_id="weather_001",
            tool_name="get_weather",
            input={
                "location": "San Francisco", 
                "units": "fahrenheit", 
                "include_forecast": True
            },
        )
        
        result = await execute_tool_call(
            tools=tools_dict,
            tool_call=weather_call,
            messages=[],
        )
        
        weather_data = result.output
        print(f"✅ Weather for {weather_data['location']}:")
        print(f"   🌡️  Temperature: {weather_data['current']['temperature']}°{weather_data['current']['units']}")
        print(f"   ☁️  Condition: {weather_data['current']['condition']}")
        print(f"   💨 Wind: {weather_data['current']['wind_speed']} mph")
        
        if weather_data['forecast']:
            print(f"   📅 5-day forecast:")
            for day in weather_data['forecast'][:3]:  # Show first 3 days
                print(f"      {day['day']}: High {day['high']}°, Low {day['low']}° - {day['condition']}")
        
    except Exception as e:
        print(f"❌ Error in weather example: {e}")
    
    # Example 4: Database tool with callbacks
    print("\n🗄️  Example 4: Database tool with callbacks")
    print("-" * 40)
    
    try:
        db_call = ToolCall(
            tool_call_id="db_001",
            tool_name="query_database",
            input={
                "table": "users",
                "columns": ["id", "name", "email"],
                "where": "age > 21",
                "limit": 5
            },
        )
        
        result = await execute_tool_call(
            tools=tools_dict,
            tool_call=db_call,
            messages=[],
        )
        
        db_result = result.output
        print(f"✅ Query executed successfully:")
        print(f"   📋 Table: {db_result['query']['table']}")
        print(f"   🔍 Columns: {', '.join(db_result['query']['columns'])}")
        print(f"   📊 Results ({db_result['count']} rows):")
        
        for row in db_result['results']:
            print(f"      ID {row['id']}: {row['name']} (value: {row['value']})")
        
    except Exception as e:
        print(f"❌ Error in database example: {e}")
    
    print("\n🎉 All tool examples completed!")


if __name__ == "__main__":
    asyncio.run(main())