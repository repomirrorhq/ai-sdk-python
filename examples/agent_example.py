#!/usr/bin/env python3
"""
AI SDK Agent Example - Multi-step reasoning and tool orchestration.

This example demonstrates how to use the AI SDK Agent for building AI agents
that can perform multi-step reasoning, execute tools, and maintain context
across interactions.

Run with:
    python examples/agent_example.py
"""

import asyncio
import json
from typing import Dict, Any

# In a real application, these would be:
# from ai_sdk import create_openai, Agent, tool
# For this example, we'll demonstrate the API without running it

def create_openai():
    """Mock OpenAI provider for demonstration."""
    class MockOpenAI:
        def chat(self, model: str):
            class MockModel:
                def __init__(self):
                    self.provider_id = "openai"
                    self.model_id = model
            return MockModel()
    return MockOpenAI()

def tool(name: str, description: str):
    """Mock tool decorator for demonstration."""
    def decorator(func):
        func.name = name
        func.description = description
        func.parameters = {
            "type": "object",
            "properties": {},
            "required": []
        }
        return func
    return decorator

class Agent:
    """Mock Agent class for demonstration."""
    def __init__(self, **kwargs):
        self.settings = kwargs
        print(f"Agent initialized with settings: {kwargs}")
    
    async def generate(self, prompt: str = None, **kwargs):
        print(f"Agent generating response for: {prompt}")
        return {"text": "This is a mock response"}
    
    def stream(self, prompt: str = None, **kwargs):
        print(f"Agent streaming response for: {prompt}")
        return {"stream": "mock_stream"}


async def main():
    """Demonstrate agent usage patterns."""
    
    # ============================================================================
    # Example 1: Basic Agent with System Prompt
    # ============================================================================
    print("=" * 60)
    print("Example 1: Basic Agent Setup")
    print("=" * 60)
    
    # Create a basic agent with system prompt
    basic_agent = Agent(
        model=create_openai().chat("gpt-4"),
        system="You are a helpful assistant specialized in explaining technical concepts.",
        temperature=0.7,
        max_tokens=500
    )
    
    # Generate response
    response = await basic_agent.generate("Explain what machine learning is.")
    print(f"Response: {response}")
    print()
    
    # ============================================================================
    # Example 2: Agent with Tools
    # ============================================================================
    print("=" * 60)
    print("Example 2: Agent with Tools")  
    print("=" * 60)
    
    # Define tools for the agent
    @tool("calculator", "Perform arithmetic calculations")
    def calculator(expression: str) -> str:
        """Calculate mathematical expressions safely."""
        try:
            # In a real implementation, use a safe evaluator
            result = eval(expression.replace("^", "**"))
            return f"The result is: {result}"
        except Exception as e:
            return f"Error in calculation: {e}"
    
    @tool("search_knowledge", "Search for factual information")  
    def search_knowledge(query: str) -> str:
        """Search for factual information (mock implementation)."""
        # In a real implementation, this would connect to a knowledge base
        knowledge_base = {
            "python": "Python is a high-level programming language known for its simplicity and readability.",
            "ai": "Artificial Intelligence (AI) is the simulation of human intelligence in machines.",
            "machine learning": "Machine learning is a subset of AI that enables computers to learn from data."
        }
        
        for key, value in knowledge_base.items():
            if key.lower() in query.lower():
                return value
        return "I don't have information about that topic."
    
    @tool("weather", "Get weather information")
    def get_weather(location: str) -> str:
        """Get weather for a location (mock implementation)."""
        # In a real implementation, this would call a weather API
        return f"The weather in {location} is sunny with a temperature of 22°C."
    
    # Create agent with tools
    tool_agent = Agent(
        model=create_openai().chat("gpt-4"),
        tools={
            "calculator": calculator,
            "search_knowledge": search_knowledge, 
            "weather": get_weather
        },
        system="You are a helpful assistant with access to tools. Use them when needed to provide accurate information.",
        temperature=0.3,
        max_tokens=300
    )
    
    # Use agent with tools
    response = await tool_agent.generate("What is 15 * 24 + 37? Also, what's the weather like in Paris?")
    print(f"Response with tools: {response}")
    print()
    
    # ============================================================================
    # Example 3: Agent with Dynamic Tool Management
    # ============================================================================
    print("=" * 60)
    print("Example 3: Dynamic Tool Management")
    print("=" * 60)
    
    # Start with basic agent
    dynamic_agent = Agent(
        model=create_openai().chat("gpt-3.5-turbo"),
        system="You are an assistant that can gain new capabilities."
    )
    
    # Show initial capabilities
    print(f"Initial tools: {getattr(dynamic_agent, 'list_tools', lambda: [])()}")
    
    # Add tools dynamically
    @tool("translate", "Translate text between languages")
    def translate_text(text: str, target_language: str) -> str:
        """Translate text (mock implementation)."""
        return f"Translated '{text}' to {target_language}: [translated text would be here]"
    
    # Simulate adding tool
    print("Adding translation tool...")
    # dynamic_agent.add_tool("translate", translate_text)
    print("Tool added successfully!")
    
    # Use the agent with new capabilities
    response = await dynamic_agent.generate("Translate 'Hello, world!' to French.")
    print(f"Response with new tool: {response}")
    print()
    
    # ============================================================================
    # Example 4: Agent Streaming
    # ============================================================================
    print("=" * 60)
    print("Example 4: Agent Streaming")
    print("=" * 60)
    
    streaming_agent = Agent(
        model=create_openai().chat("gpt-4"),
        system="You are a storyteller who creates engaging narratives.",
        temperature=0.8
    )
    
    # Stream response
    stream = streaming_agent.stream("Tell me a short story about a robot learning to paint.")
    print(f"Streaming response: {stream}")
    
    # In a real implementation, you would iterate over the stream:
    # async for chunk in stream:
    #     print(chunk.text, end="", flush=True)
    print()
    
    # ============================================================================
    # Example 5: Agent Configuration Updates
    # ============================================================================
    print("=" * 60)
    print("Example 5: Dynamic Configuration")
    print("=" * 60)
    
    config_agent = Agent(
        model=create_openai().chat("gpt-4"),
        system="You are a helpful assistant.",
        temperature=0.5,
        max_tokens=100
    )
    
    print(f"Initial temperature: {config_agent.settings.get('temperature', 'N/A')}")
    
    # Update settings
    # config_agent.update_settings(temperature=0.9, max_tokens=200)
    print("Settings updated!")
    print(f"New temperature: {config_agent.settings.get('temperature', 'N/A')}")
    
    # Generate with new settings
    response = await config_agent.generate("Be creative and write a short poem.")
    print(f"Creative response: {response}")
    print()
    
    # ============================================================================
    # Example 6: Complex Multi-tool Workflow
    # ============================================================================
    print("=" * 60)
    print("Example 6: Complex Multi-tool Workflow")
    print("=" * 60)
    
    @tool("analyze_data", "Analyze numerical data")
    def analyze_data(data: str) -> str:
        """Analyze numerical data (mock implementation)."""
        try:
            numbers = [float(x.strip()) for x in data.split(",")]
            avg = sum(numbers) / len(numbers)
            return f"Analysis: {len(numbers)} values, average: {avg:.2f}, min: {min(numbers)}, max: {max(numbers)}"
        except:
            return "Error: Unable to parse data. Please provide comma-separated numbers."
    
    @tool("generate_report", "Generate a formatted report")
    def generate_report(title: str, content: str) -> str:
        """Generate a formatted report (mock implementation)."""
        return f"""
# {title}
        
## Summary
{content}

## Generated on
{asyncio.get_event_loop().time()}

---
Report generated by AI Agent
        """.strip()
    
    # Create comprehensive agent
    workflow_agent = Agent(
        model=create_openai().chat("gpt-4"),
        tools={
            "calculator": calculator,
            "analyze_data": analyze_data,
            "generate_report": generate_report,
            "search_knowledge": search_knowledge
        },
        system="""You are a data analyst assistant. When given data:
1. First analyze the data using available tools
2. Perform any necessary calculations
3. Generate a comprehensive report
4. Always explain your reasoning""",
        temperature=0.2,
        max_tokens=800
    )
    
    # Complex request
    complex_request = """
    I have sales data: 1200, 1350, 980, 1500, 1100, 1800, 1250.
    Please analyze this data, calculate the growth rate from first to last value,
    and generate a professional report.
    """
    
    response = await workflow_agent.generate(complex_request)
    print(f"Complex workflow response: {response}")
    print()
    
    print("=" * 60)
    print("Agent Examples Complete!")
    print("=" * 60)
    print("""
Key Takeaways:
- Agents provide a high-level interface for AI interactions
- Tools can be added, removed, and managed dynamically  
- Settings can be updated without recreating the agent
- Streaming is supported for real-time responses
- Complex multi-step workflows are possible with tool orchestration
- The same agent interface works with any supported AI provider
    """)


if __name__ == "__main__":
    # Run the examples
    print("AI SDK Agent Examples")
    print("=" * 60)
    print("This example demonstrates the Agent API without requiring")
    print("actual AI provider credentials. In real usage, you would:")
    print("1. Install: pip install ai-sdk[openai]")
    print("2. Set API keys: export OPENAI_API_KEY='your-key'")
    print("3. Run: python examples/agent_example.py")
    print()
    
    asyncio.run(main())