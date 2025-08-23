"""Advanced Middleware and Agent Features Example

This example demonstrates the powerful new features added to ai-sdk-python:

1. Extract Reasoning Middleware - Extract XML-tagged reasoning sections
2. Simulate Streaming Middleware - Simulate streaming from any model
3. Enhanced Agent System - Multi-step reasoning with advanced patterns
4. PrepareStep functionality - Dynamic step configuration
5. Tool call repair - Automatic error recovery
6. Step finish callbacks - Monitoring and hooks
7. Active tools filtering - Dynamic tool availability

These features match the TypeScript AI SDK's advanced capabilities while maintaining
Python idioms and patterns.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional

from ai_sdk import (
    create_openai, 
    generate_text,
    stream_text,
    wrap_language_model,
    extract_reasoning_middleware,
    simulate_streaming_middleware,
    logging_middleware,
    telemetry_middleware,
    Agent,
    tool,
    step_count_is,
    has_tool_call
)
from ai_sdk.agent import StepResult, PrepareStepResult
from ai_sdk.providers.types import Message

# Set up logging to see middleware in action
logging.basicConfig(level=logging.INFO)

# Simple tools for demonstrations
@tool("calculator", "Perform mathematical calculations")
async def calculator(expression: str) -> float:
    """Safe calculator for basic arithmetic."""
    try:
        # In production, use a safe evaluator like simpleeval
        result = eval(expression.replace("^", "**"))
        return float(result)
    except Exception as e:
        raise ValueError(f"Invalid expression: {e}")

@tool("weather", "Get weather information for a location")
async def get_weather(location: str) -> str:
    """Mock weather service."""
    weather_data = {
        "new york": "Sunny, 72°F",
        "london": "Cloudy, 61°F", 
        "tokyo": "Rainy, 68°F",
        "san francisco": "Foggy, 65°F"
    }
    location_key = location.lower().strip()
    return weather_data.get(location_key, f"Weather unavailable for {location}")

@tool("search", "Search for information on the web")  
async def web_search(query: str) -> str:
    """Mock web search."""
    return f"Search results for '{query}': [Mock results would appear here]"


async def demonstrate_reasoning_extraction():
    """Demonstrate extract reasoning middleware with OpenAI o1 models."""
    print("\n🧠 REASONING EXTRACTION DEMO")
    print("=" * 50)
    
    try:
        # Create base model
        openai = create_openai()
        base_model = openai.language_model("gpt-4o-mini")  # Use available model
        
        # Wrap with reasoning extraction middleware
        reasoning_model = wrap_language_model(
            model=base_model,
            middleware=[
                logging_middleware(level="INFO"),
                extract_reasoning_middleware(
                    tag_name="thinking",
                    separator="\n---\n"
                )
            ]
        )
        
        # Test with a prompt that encourages step-by-step thinking
        result = await generate_text(
            model=reasoning_model,
            messages=[
                Message(role="system", content="Think step by step, wrapping your reasoning in <thinking></thinking> tags."),
                Message(role="user", content="What's the area of a circle with radius 5? Show your work.")
            ]
        )
        
        print("Generated response:")
        print(f"Text: {result.text}")
        print(f"Content parts: {len(result.content)}")
        
        # Show reasoning if extracted
        for part in result.content:
            if hasattr(part, 'type'):
                if part.type == "reasoning":
                    print(f"\n📝 Extracted reasoning:")
                    print(part.text)
                elif part.type == "text":
                    print(f"\n💬 Final response:")
                    print(part.text)
    
    except Exception as e:
        print(f"Reasoning extraction demo failed: {e}")


async def demonstrate_streaming_simulation():
    """Demonstrate simulate streaming middleware."""
    print("\n🌊 STREAMING SIMULATION DEMO")
    print("=" * 50)
    
    try:
        openai = create_openai()
        base_model = openai.language_model("gpt-4o-mini")
        
        # Wrap with streaming simulation
        streaming_model = wrap_language_model(
            model=base_model,
            middleware=[
                simulate_streaming_middleware(),
                telemetry_middleware(track_timing=True)
            ]
        )
        
        print("Simulating streaming from non-streaming call...")
        
        # Use stream_text which will call the simulate middleware
        async for chunk in stream_text(
            model=streaming_model,
            prompt="Write a haiku about Python programming"
        ):
            if chunk.text_delta:
                print(chunk.text_delta, end="", flush=True)
        
        print("\n✅ Streaming simulation complete!")
    
    except Exception as e:
        print(f"Streaming simulation demo failed: {e}")


async def advanced_agent_step_preparation(context: Dict[str, Any]) -> Optional[PrepareStepResult]:
    """Advanced step preparation function that adapts based on step number."""
    step_number = context["step_number"]
    steps = context["steps"]
    
    print(f"🔧 Preparing step {step_number}")
    
    # Different strategies based on step number
    if step_number == 0:
        # First step: use all tools, higher temperature for creativity
        return PrepareStepResult(
            active_tools=["calculator", "weather", "search"],
            # Could set temperature=0.9 here if supported
        )
    elif step_number == 1:
        # Second step: focus on calculation tools for accuracy
        return PrepareStepResult(
            active_tools=["calculator"],
            # temperature=0.1  # More focused
        )
    else:
        # Later steps: use search for additional information
        return PrepareStepResult(
            active_tools=["search", "weather"],
            # temperature=0.5
        )


async def step_finish_callback(step_result: StepResult) -> None:
    """Callback function called after each agent step."""
    print(f"🏁 Step {step_result.step_number} completed!")
    print(f"   Messages in conversation: {len(step_result.messages)}")
    print(f"   Tool calls made: {len(step_result.tool_calls)}")
    if step_result.result and hasattr(step_result.result, 'usage'):
        print(f"   Tokens used: {step_result.result.usage.total_tokens}")


async def tool_call_repair_function(context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Attempt to repair failed tool calls."""
    tool_call = context["toolCall"]
    error = context["error"]
    
    print(f"🔧 Attempting to repair tool call: {tool_call}")
    print(f"   Error: {error}")
    
    # Simple repair strategy: if calculator fails, try simplifying the expression
    if tool_call.get("name") == "calculator":
        try:
            args = tool_call.get("arguments", {})
            expression = args.get("expression", "")
            
            # Try to simplify common issues
            if "^" in expression:
                args["expression"] = expression.replace("^", "**")
                return {
                    **tool_call,
                    "arguments": args
                }
        except Exception:
            pass
    
    # Return None if repair is not possible
    return None


async def demonstrate_advanced_agent():
    """Demonstrate the enhanced agent system with all advanced features."""
    print("\n🤖 ADVANCED AGENT DEMO") 
    print("=" * 50)
    
    try:
        openai = create_openai()
        base_model = openai.language_model("gpt-4o-mini")
        
        # Create an advanced agent with all features
        agent = Agent(
            model=base_model,
            system="You are a helpful assistant that can use tools and thinks step by step. When calculating, show your work clearly.",
            tools={
                "calculator": calculator,
                "weather": get_weather,
                "search": web_search
            },
            
            # Advanced agent features
            max_steps=4,
            stop_when=[
                step_count_is(3),  # Stop after 3 steps max
                has_tool_call("calculator")  # Or stop when calculator is called
            ],
            
            # Dynamic step preparation
            prepare_step=advanced_agent_step_preparation,
            
            # Tool call repair
            tool_call_repair=tool_call_repair_function,
            
            # Step monitoring
            on_step_finish=step_finish_callback,
            
            # Experimental context
            experimental_context={"session_id": "demo-123"}
        )
        
        # Multi-step generation with complex reasoning
        print("🚀 Starting multi-step agent reasoning...")
        
        result = await agent.multi_step_generate(
            prompt="I need to calculate the compound interest on $1000 at 5% annual rate for 3 years, then check the weather in New York. Show all your work!"
        )
        
        print(f"\n📊 AGENT RESULTS:")
        print(f"Total steps taken: {result['total_steps']}")
        print(f"Final conversation length: {len(result['conversation'])}")
        
        # Show the conversation flow
        print("\n💬 CONVERSATION FLOW:")
        for i, message in enumerate(result["conversation"]):
            print(f"{i+1}. {message.role}: {str(message.content)[:100]}...")
        
        if result["final_result"]:
            print(f"\n🎯 FINAL RESULT:")
            print(result["final_result"].text)
    
    except Exception as e:
        print(f"Advanced agent demo failed: {e}")


async def demonstrate_middleware_composition():
    """Demonstrate composing multiple middleware together."""
    print("\n🔧 MIDDLEWARE COMPOSITION DEMO")
    print("=" * 50)
    
    try:
        openai = create_openai()
        base_model = openai.language_model("gpt-4o-mini")
        
        # Compose multiple middleware for comprehensive functionality
        enhanced_model = wrap_language_model(
            model=base_model,
            middleware=[
                # Logging for debugging
                logging_middleware(
                    level="INFO",
                    include_timing=True
                ),
                
                # Telemetry for monitoring
                telemetry_middleware(
                    track_requests=True,
                    track_tokens=True,
                    callback=lambda data: print(f"📊 Telemetry: {data['operation']} took {data.get('duration_ms', 0)}ms")
                ),
                
                # Extract reasoning if present
                extract_reasoning_middleware(
                    tag_name="analysis"
                ),
                
                # Simulate streaming for consistent interface
                simulate_streaming_middleware()
            ]
        )
        
        print("📡 Generating with full middleware stack...")
        
        # Test with streaming
        async for chunk in stream_text(
            model=enhanced_model,
            messages=[
                Message(role="system", content="Analyze the user's question in <analysis></analysis> tags, then provide a clear answer."),
                Message(role="user", content="What are the key principles of good software design?")
            ]
        ):
            if chunk.text_delta:
                print(chunk.text_delta, end="", flush=True)
        
        print("\n✅ Middleware composition demo complete!")
    
    except Exception as e:
        print(f"Middleware composition demo failed: {e}")


async def main():
    """Run all demonstration examples."""
    print("🎉 AI SDK Python - Advanced Features Demonstration")
    print("=" * 60)
    print("This demo showcases the latest advanced features:")
    print("• Extract Reasoning Middleware")
    print("• Simulate Streaming Middleware") 
    print("• Enhanced Multi-step Agent System")
    print("• Dynamic Step Preparation")
    print("• Tool Call Repair")
    print("• Step Finish Callbacks")
    print("• Middleware Composition")
    print("=" * 60)
    
    # Run all demonstrations
    await demonstrate_reasoning_extraction()
    await demonstrate_streaming_simulation()
    await demonstrate_advanced_agent()
    await demonstrate_middleware_composition()
    
    print("\n🎊 All demonstrations completed!")
    print("\nThese features bring ai-sdk-python to feature parity with")
    print("the TypeScript AI SDK's advanced capabilities while maintaining")
    print("Python idioms and providing excellent developer experience.")


if __name__ == "__main__":
    # Make sure to set your OpenAI API key:
    # export OPENAI_API_KEY="your-key-here"
    
    asyncio.run(main())