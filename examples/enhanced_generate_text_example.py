"""Example demonstrating enhanced generate_text with multi-step tool calling."""

import asyncio
from typing import Any, Dict

from ai_sdk import (
    generate_text_enhanced,
    step_count_is, 
    has_tool_call,
    create_openai,
    Tool,
)


# Example tool for getting weather
async def get_weather(location: str, **kwargs) -> str:
    """Get the current weather for a location."""
    print(f"🌤️  Getting weather for: {location}")
    # Simulate weather API call
    await asyncio.sleep(0.5)
    return f"The weather in {location} is sunny and 72°F"


# Example tool for getting time
async def get_time(timezone: str = "UTC", **kwargs) -> str:
    """Get the current time in a specific timezone."""
    print(f"⏰ Getting time for timezone: {timezone}")
    await asyncio.sleep(0.3)
    return f"The current time in {timezone} is 2:30 PM"


async def basic_example():
    """Basic example with single tool call."""
    print("🔹 Basic Tool Calling Example")
    print("=" * 50)
    
    # Create OpenAI model (requires OPENAI_API_KEY environment variable)
    try:
        model = create_openai()("gpt-3.5-turbo")
    except Exception as e:
        print(f"Failed to create OpenAI model: {e}")
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    # Define tools
    tools = {
        "get_weather": Tool(
            name="get_weather",
            description="Get the current weather for a location",
            input_schema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string", 
                        "description": "The location to get weather for"
                    }
                },
                "required": ["location"]
            },
            execute=get_weather
        )
    }
    
    result = await generate_text_enhanced(
        model=model,
        prompt="What's the weather like in San Francisco?",
        tools=tools,
        stop_when=step_count_is(2),  # Allow one tool call
    )
    
    print(f"Steps: {len(result.steps)}")
    print(f"Final text: {result.text}")
    print(f"Tool calls: {len(result.tool_calls)}")
    print(f"Tool results: {len(result.tool_results)}")
    print()


async def multi_step_example():
    """Example with multiple tool calls in sequence."""
    print("🔹 Multi-step Tool Calling Example")
    print("=" * 50)
    
    try:
        model = create_openai()("gpt-3.5-turbo")
    except Exception as e:
        print(f"Failed to create OpenAI model: {e}")
        return
    
    # Define multiple tools
    tools = {
        "get_weather": Tool(
            name="get_weather",
            description="Get the current weather for a location",
            input_schema={
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location to get weather for"
                    }
                },
                "required": ["location"]
            },
            execute=get_weather
        ),
        "get_time": Tool(
            name="get_time",
            description="Get the current time in a timezone",
            input_schema={
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "The timezone to get time for"
                    }
                },
                "required": ["timezone"]
            },
            execute=get_time
        )
    }
    
    def on_step_finish(step):
        """Callback called after each step."""
        print(f"  Step {step.step_number + 1} completed:")
        print(f"    Text: {step.text[:100]}{'...' if len(step.text) > 100 else ''}")
        print(f"    Tool calls: {len(step.tool_calls)}")
        print(f"    Tool results: {len(step.tool_results)}")
        print()
    
    result = await generate_text_enhanced(
        model=model,
        prompt="What's the weather and time in New York?",
        tools=tools,
        stop_when=step_count_is(3),  # Allow multiple steps
        on_step_finish=on_step_finish,
    )
    
    print(f"Final Result:")
    print(f"  Total steps: {len(result.steps)}")
    print(f"  Final text: {result.text}")
    print(f"  Total usage: {result.total_usage}")
    print()


async def stop_condition_example():
    """Example demonstrating stop conditions."""
    print("🔹 Stop Condition Example")
    print("=" * 50)
    
    try:
        model = create_openai()("gpt-3.5-turbo")  
    except Exception as e:
        print(f"Failed to create OpenAI model: {e}")
        return
    
    tools = {
        "get_weather": Tool(
            name="get_weather",
            description="Get weather information",
            input_schema={
                "type": "object",
                "properties": {
                    "location": {"type": "string"}
                },
                "required": ["location"]
            },
            execute=get_weather
        )
    }
    
    # Stop when weather tool is called
    result = await generate_text_enhanced(
        model=model,
        prompt="Please get me the weather for Paris",
        tools=tools,
        stop_when=has_tool_call("get_weather"),
    )
    
    print(f"Stopped after weather tool call:")
    print(f"  Steps: {len(result.steps)}")
    print(f"  Weather tool called: {'get_weather' in [tc.tool_name for tc in result.tool_calls]}")
    print()


async def main():
    """Run all examples."""
    print("🚀 Enhanced Generate Text Examples")
    print("=" * 60)
    print()
    
    await basic_example()
    await multi_step_example()
    await stop_condition_example()
    
    print("✅ All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())