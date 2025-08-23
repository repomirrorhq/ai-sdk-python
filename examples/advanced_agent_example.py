#!/usr/bin/env python3
"""
Advanced AI SDK Agent Example - Sophisticated agent patterns and workflows.

This example demonstrates advanced agent patterns including:
- Multi-step reasoning with stopping conditions
- Agent orchestration and delegation
- Context sharing between agents
- Error handling and recovery
- Custom middleware integration

Run with:
    python examples/advanced_agent_example.py
"""

import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

# Mock imports for demonstration - in real usage:
# from ai_sdk import create_openai, Agent, tool, wrap_language_model, logging_middleware

class TaskStatus(Enum):
    """Status of an agent task."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class AgentTask:
    """Represents a task for an agent."""
    id: str
    description: str
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Any] = None
    error: Optional[str] = None
    agent_id: Optional[str] = None

class TaskManager:
    """Manages tasks across multiple agents."""
    
    def __init__(self):
        self.tasks: Dict[str, AgentTask] = {}
        self.task_counter = 0
    
    def create_task(self, description: str) -> str:
        """Create a new task and return its ID."""
        self.task_counter += 1
        task_id = f"task_{self.task_counter}"
        self.tasks[task_id] = AgentTask(id=task_id, description=description)
        return task_id
    
    def update_task(self, task_id: str, status: TaskStatus, result: Any = None, error: str = None):
        """Update task status."""
        if task_id in self.tasks:
            self.tasks[task_id].status = status
            if result is not None:
                self.tasks[task_id].result = result
            if error:
                self.tasks[task_id].error = error
    
    def get_task(self, task_id: str) -> Optional[AgentTask]:
        """Get task by ID."""
        return self.tasks.get(task_id)
    
    def list_tasks(self, status: Optional[TaskStatus] = None) -> List[AgentTask]:
        """List tasks, optionally filtered by status."""
        if status is None:
            return list(self.tasks.values())
        return [task for task in self.tasks.values() if task.status == status]

# Mock classes for demonstration
class MockOpenAI:
    def chat(self, model: str):
        class MockModel:
            def __init__(self):
                self.provider_id = "openai"
                self.model_id = model
        return MockModel()

def create_openai():
    return MockOpenAI()

def tool(name: str, description: str):
    def decorator(func):
        func.name = name
        func.description = description
        func.parameters = {"type": "object", "properties": {}, "required": []}
        return func
    return decorator

class Agent:
    def __init__(self, **kwargs):
        self.settings = kwargs
        self.agent_id = kwargs.get('agent_id', 'default_agent')
        print(f"Agent {self.agent_id} initialized")
    
    async def generate(self, prompt: str = None, **kwargs):
        print(f"Agent {self.agent_id} generating: {prompt}")
        return {"text": f"Mock response from {self.agent_id}"}
    
    def stream(self, prompt: str = None, **kwargs):
        print(f"Agent {self.agent_id} streaming: {prompt}")
        return {"stream": "mock_stream"}

def wrap_language_model(model, middleware):
    print(f"Wrapping model with middleware: {middleware}")
    return model

def logging_middleware(**kwargs):
    return {"type": "logging_middleware", **kwargs}


async def demonstrate_multi_agent_system():
    """Demonstrate a multi-agent system with task delegation."""
    print("=" * 60)
    print("Multi-Agent System Example")
    print("=" * 60)
    
    # Initialize task manager
    task_manager = TaskManager()
    
    # Define specialized tools
    @tool("research_topic", "Research information about a topic")
    def research_topic(topic: str, depth: str = "basic") -> str:
        """Research a topic with specified depth."""
        knowledge_db = {
            "quantum computing": "Quantum computing uses quantum mechanics for computation...",
            "machine learning": "Machine learning is a method of data analysis...",
            "blockchain": "Blockchain is a distributed ledger technology..."
        }
        
        info = knowledge_db.get(topic.lower(), f"Research data for {topic}")
        if depth == "detailed":
            return f"DETAILED: {info} [Additional technical details would be here]"
        return f"BASIC: {info}"
    
    @tool("analyze_content", "Analyze and summarize content")
    def analyze_content(content: str, analysis_type: str = "summary") -> str:
        """Analyze content and provide insights."""
        if analysis_type == "summary":
            return f"SUMMARY: {content[:100]}... [Key points extracted]"
        elif analysis_type == "sentiment":
            return f"SENTIMENT: Positive tone detected in content"
        elif analysis_type == "complexity":
            return f"COMPLEXITY: Medium complexity level, suitable for general audience"
        return f"ANALYSIS: {content[:50]}..."
    
    @tool("create_report", "Create formatted reports")
    def create_report(title: str, sections: str, format_type: str = "markdown") -> str:
        """Create a formatted report."""
        if format_type == "markdown":
            return f"# {title}\\n\\n{sections}\\n\\n---\\nGenerated by AI Agent"
        elif format_type == "html":
            return f"<h1>{title}</h1><div>{sections}</div><hr><i>Generated by AI Agent</i>"
        return f"{title}\\n{sections}\\n\\nGenerated by AI Agent"
    
    # Create specialized agents
    researcher_agent = Agent(
        agent_id="researcher",
        model=create_openai().chat("gpt-4"),
        tools={"research_topic": research_topic},
        system="""You are a research specialist. Your job is to:
1. Research topics thoroughly using available tools
2. Gather comprehensive information
3. Provide well-structured research results
4. Always cite when you use the research tool""",
        temperature=0.2
    )
    
    analyst_agent = Agent(
        agent_id="analyst",
        model=create_openai().chat("gpt-4"),
        tools={"analyze_content": analyze_content},
        system="""You are an analysis specialist. Your job is to:
1. Analyze content provided to you
2. Extract key insights and patterns
3. Provide different types of analysis as requested
4. Be thorough and objective in your analysis""",
        temperature=0.3
    )
    
    writer_agent = Agent(
        agent_id="writer",
        model=create_openai().chat("gpt-3.5-turbo"),
        tools={"create_report": create_report},
        system="""You are a report writing specialist. Your job is to:
1. Take analyzed information and create professional reports
2. Structure information clearly and logically
3. Use appropriate formatting for the requested output type
4. Ensure reports are comprehensive and well-organized""",
        temperature=0.5
    )
    
    # Orchestrator agent that delegates tasks
    orchestrator_agent = Agent(
        agent_id="orchestrator",
        model=create_openai().chat("gpt-4"),
        tools={
            "research_topic": research_topic,
            "analyze_content": analyze_content, 
            "create_report": create_report
        },
        system="""You are a task orchestrator. You manage complex workflows by:
1. Breaking down complex requests into subtasks
2. Delegating tasks to specialized agents when available
3. Coordinating results from multiple agents
4. Ensuring quality and completeness of final output
5. Managing the overall workflow efficiently""",
        temperature=0.1
    )
    
    # Simulate a complex workflow
    print("\\n🎯 Starting Complex Workflow: Comprehensive Quantum Computing Report")
    
    # Step 1: Research phase
    print("\\n📚 Phase 1: Research")
    research_task = task_manager.create_task("Research quantum computing in depth")
    task_manager.update_task(research_task, TaskStatus.IN_PROGRESS)
    
    research_result = await researcher_agent.generate(
        "Research quantum computing in detail. Focus on current applications, "
        "challenges, and future prospects. Use depth='detailed' for comprehensive information."
    )
    print(f"Research completed: {research_result['text']}")
    task_manager.update_task(research_task, TaskStatus.COMPLETED, research_result)
    
    # Step 2: Analysis phase  
    print("\\n🔍 Phase 2: Analysis")
    analysis_task = task_manager.create_task("Analyze research content")
    task_manager.update_task(analysis_task, TaskStatus.IN_PROGRESS)
    
    analysis_result = await analyst_agent.generate(
        f"Analyze this research content and provide summary, sentiment, and complexity analysis: "
        f"{research_result['text']}"
    )
    print(f"Analysis completed: {analysis_result['text']}")
    task_manager.update_task(analysis_task, TaskStatus.COMPLETED, analysis_result)
    
    # Step 3: Report writing phase
    print("\\n📝 Phase 3: Report Generation")
    report_task = task_manager.create_task("Generate comprehensive report")
    task_manager.update_task(report_task, TaskStatus.IN_PROGRESS)
    
    report_result = await writer_agent.generate(
        f"Create a comprehensive markdown report titled 'Quantum Computing: Current State and Future' "
        f"using this research and analysis: Research: {research_result['text']} "
        f"Analysis: {analysis_result['text']}"
    )
    print(f"Report completed: {report_result['text']}")
    task_manager.update_task(report_task, TaskStatus.COMPLETED, report_result)
    
    # Step 4: Show task manager status
    print("\\n📋 Task Manager Status:")
    for task in task_manager.list_tasks():
        print(f"  {task.id}: {task.description} - {task.status.value}")
    
    print(f"\\n✅ Workflow completed! Tasks completed: {len(task_manager.list_tasks(TaskStatus.COMPLETED))}")


async def demonstrate_agent_with_middleware():
    """Demonstrate agent integration with middleware."""
    print("\\n" + "=" * 60)
    print("Agent with Middleware Integration")
    print("=" * 60)
    
    # Create base model
    base_model = create_openai().chat("gpt-4")
    
    # Wrap with middleware for enhanced capabilities
    enhanced_model = wrap_language_model(
        model=base_model,
        middleware=[
            logging_middleware(level="INFO", include_params=True),
            # In real usage: caching_middleware(ttl=300),
            # rate_limiting_middleware(requests_per_minute=60)
        ]
    )
    
    # Create agent with enhanced model
    enhanced_agent = Agent(
        model=enhanced_model,
        agent_id="enhanced_agent",
        system="You are an enhanced agent with middleware capabilities.",
        temperature=0.6
    )
    
    print("🔧 Enhanced agent created with middleware:")
    print("  - Request/response logging")
    print("  - Caching for performance") 
    print("  - Rate limiting for safety")
    
    # Use the enhanced agent
    response = await enhanced_agent.generate(
        "Explain the benefits of using middleware in AI applications."
    )
    print(f"\\n🤖 Enhanced agent response: {response['text']}")


async def demonstrate_error_handling_and_recovery():
    """Demonstrate error handling and recovery patterns."""
    print("\\n" + "=" * 60)
    print("Error Handling and Recovery")
    print("=" * 60)
    
    @tool("unreliable_service", "A service that sometimes fails")
    def unreliable_service(data: str) -> str:
        """Simulate an unreliable external service."""
        import random
        if random.random() < 0.3:  # 30% chance of failure
            raise Exception("Service temporarily unavailable")
        return f"Processed: {data}"
    
    # Create agent with error handling
    resilient_agent = Agent(
        agent_id="resilient_agent",
        model=create_openai().chat("gpt-4"),
        tools={"unreliable_service": unreliable_service},
        system="""You are a resilient agent that handles errors gracefully. When a tool fails:
1. Acknowledge the failure
2. Suggest alternative approaches
3. Retry if appropriate
4. Provide partial results when possible""",
        max_retries=3
    )
    
    print("🛡️ Testing error handling with unreliable service...")
    
    try:
        response = await resilient_agent.generate(
            "Process this important data: 'mission critical information'. "
            "Use the unreliable_service tool and handle any failures gracefully."
        )
        print(f"✅ Agent handled request: {response['text']}")
    except Exception as e:
        print(f"❌ Agent failed: {e}")
        
    print("\\n🔄 Implementing retry logic with exponential backoff...")
    
    # Simulate retry logic
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            print(f"  Attempt {attempt + 1}/{max_attempts}")
            # In real usage, this would be the actual agent call
            print("  ✅ Request succeeded!")
            break
        except Exception as e:
            if attempt == max_attempts - 1:
                print(f"  ❌ All attempts failed: {e}")
            else:
                wait_time = 2 ** attempt
                print(f"  ⏳ Waiting {wait_time}s before retry...")
                await asyncio.sleep(0.1)  # Shortened for demo


async def demonstrate_contextual_agents():
    """Demonstrate agents with shared context and memory."""
    print("\\n" + "=" * 60)
    print("Contextual Agents with Shared Memory")
    print("=" * 60)
    
    # Shared context between agents
    shared_context = {
        "conversation_history": [],
        "user_preferences": {
            "language": "English",
            "detail_level": "moderate",
            "format": "structured"
        },
        "session_data": {
            "topics_discussed": [],
            "tools_used": [],
            "interaction_count": 0
        }
    }
    
    @tool("update_context", "Update shared context information")
    def update_context(key: str, value: str) -> str:
        """Update the shared context."""
        keys = key.split(".")
        target = shared_context
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        target[keys[-1]] = value
        return f"Context updated: {key} = {value}"
    
    @tool("get_context", "Retrieve shared context information")  
    def get_context(key: str = None) -> str:
        """Get information from shared context."""
        if key is None:
            return f"Full context: {shared_context}"
        
        keys = key.split(".")
        target = shared_context
        try:
            for k in keys:
                target = target[k]
            return f"Context value for {key}: {target}"
        except KeyError:
            return f"Context key {key} not found"
    
    # Create context-aware agents
    memory_agent = Agent(
        agent_id="memory_agent",
        model=create_openai().chat("gpt-4"),
        tools={"update_context": update_context, "get_context": get_context},
        context=shared_context,
        system="""You are a memory-aware agent. You:
1. Remember previous interactions using shared context
2. Update context with new information learned
3. Reference past conversations when relevant
4. Maintain user preferences and session state""",
        temperature=0.4
    )
    
    print("🧠 Memory agent created with shared context")
    print(f"   Initial context: {shared_context}")
    
    # Simulate a conversation with memory
    conversation_steps = [
        "Hello! I'm interested in learning about Python programming.",
        "I prefer detailed explanations. Can you tell me about decorators?", 
        "That was helpful! What were we talking about earlier?",
        "What's my preferred detail level again?"
    ]
    
    for i, user_input in enumerate(conversation_steps):
        print(f"\\n👤 User: {user_input}")
        
        # Update interaction count
        shared_context["session_data"]["interaction_count"] = i + 1
        
        response = await memory_agent.generate(user_input)
        print(f"🧠 Memory Agent: {response['text']}")
        
        # Simulate context updates
        if i == 1:  # After preferences mentioned
            print("   📝 Context updated with user preferences")
        elif i == 2:  # After asking about previous topic
            shared_context["topics_discussed"].append("Python decorators")
            print("   📝 Added topic to discussion history")


async def main():
    """Run all advanced agent demonstrations."""
    print("Advanced AI SDK Agent Examples")
    print("=" * 60)
    print("Demonstrating sophisticated agent patterns and workflows")
    print()
    
    await demonstrate_multi_agent_system()
    await demonstrate_agent_with_middleware()
    await demonstrate_error_handling_and_recovery()
    await demonstrate_contextual_agents()
    
    print("\\n" + "=" * 60)
    print("Advanced Agent Examples Complete!")
    print("=" * 60)
    print("""
🎯 Advanced Patterns Demonstrated:

1. Multi-Agent Systems
   - Task delegation and orchestration
   - Specialized agents for different roles
   - Coordinated workflows with task management

2. Middleware Integration
   - Enhanced model capabilities
   - Logging, caching, and rate limiting
   - Transparent middleware composition

3. Error Handling & Recovery
   - Graceful error handling
   - Retry logic with exponential backoff
   - Resilient agent behaviors

4. Contextual Agents
   - Shared context and memory
   - Session state management
   - Context-aware responses

🚀 These patterns enable building production-ready
   AI agent systems with enterprise capabilities!
    """)


if __name__ == "__main__":
    asyncio.run(main())