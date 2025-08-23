"""AI SDK Agent System - Multi-step reasoning and tool orchestration.

This module provides the Agent class for building AI agents that can:
- Perform multi-step reasoning with tools
- Handle complex conversation flows
- Orchestrate multiple tool calls
- Manage context and state across interactions

The agent system is built on top of the core generate_text and stream_text
functions but provides higher-level abstractions for agent-like behavior.

Example Usage:
    ```python
    from ai_sdk import create_openai, tool
    from ai_sdk.agent import Agent
    
    # Define tools
    @tool("get_weather", "Get weather for a city")
    def get_weather(city: str) -> str:
        return f"The weather in {city} is sunny"
    
    # Create agent
    agent = Agent(
        model=create_openai().chat("gpt-4"),
        tools={"get_weather": get_weather},
        system="You are a helpful assistant."
    )
    
    # Use agent
    result = await agent.generate("What's the weather in Paris?")
    print(result.content)
    ```
"""

from .agent import Agent, AgentSettings

__all__ = ["Agent", "AgentSettings"]