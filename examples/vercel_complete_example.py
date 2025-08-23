"""
Comprehensive Vercel Provider Example
====================================

This example demonstrates the complete capabilities of the Vercel provider including:
- Framework-aware code generation (Next.js, React, Vue, Svelte)
- Auto-fix capabilities for common coding issues
- Quick edit features for inline code improvements
- Multimodal support (text and image inputs)
- Web development optimized workflows

Requirements:
    pip install ai-sdk
    export VERCEL_API_KEY=your_vercel_api_key

Vercel v0 API Features:
    - Framework Optimization: Tailored for modern web frameworks
    - Auto-fix: Identifies and corrects common coding issues
    - Quick Edit: Streams inline edits as they become available
    - Multimodal: Supports both text and image inputs
    - Developer-Focused: Optimized for web development workflows
"""

import asyncio
import os
from ai_sdk import generateText, streamText, generateObject
from ai_sdk.providers import create_vercel_provider


async def demonstrate_vercel_capabilities():
    """Demonstrate all Vercel AI provider capabilities."""
    
    print("🚀 Vercel Provider - Complete Web Development AI")
    print("=" * 60)
    
    # Create Vercel provider
    vercel_api_key = os.getenv("VERCEL_API_KEY", "your-vercel-api-key-here")
    vercel = create_vercel_provider(api_key=vercel_api_key)
    
    # 1. Framework-Aware Code Generation
    print("\n1. 🛠️ FRAMEWORK-AWARE CODE GENERATION")
    print("-" * 40)
    
    # Next.js component generation
    print("\n⚛️ Next.js Component Generation:")
    try:
        nextjs_result = await generateText(
            model=vercel.language_model("v0-1.5-lg"),
            prompt="Create a responsive navigation component with a mobile hamburger menu",
            max_tokens=500,
            provider_options={
                "vercel": {
                    "framework": "next.js",
                    "typescript": True,
                    "design_system": "tailwind",
                    "enable_auto_fix": True
                }
            }
        )
        print(f"Generated Component:\n{nextjs_result.text}")
        print(f"Tokens: {nextjs_result.usage.total_tokens}")
    except Exception as e:
        print(f"⚠️ Next.js generation error: {e}")
    
    # React component with hooks
    print("\n🎣 React Component with Hooks:")
    try:
        react_result = await generateText(
            model=vercel.language_model("v0-1.5-md"),
            prompt="Create a React component that manages a shopping cart with add/remove functionality",
            max_tokens=400,
            provider_options={
                "vercel": {
                    "framework": "react",
                    "typescript": True,
                    "enable_auto_fix": True,
                    "project_type": "web"
                }
            }
        )
        print(f"React Component:\n{react_result.text}")
        print(f"Tokens: {react_result.usage.total_tokens}")
    except Exception as e:
        print(f"⚠️ React generation error: {e}")
    
    # Vue.js component
    print("\n💚 Vue.js Component:")
    try:
        vue_result = await generateText(
            model=vercel.language_model("v0-1.5-md"),
            prompt="Create a Vue.js component for a user profile card with avatar and social links",
            max_tokens=350,
            provider_options={
                "vercel": {
                    "framework": "vue",
                    "typescript": False,
                    "design_system": "vuetify",
                    "enable_quick_edit": True
                }
            }
        )
        print(f"Vue Component:\n{vue_result.text}")
        print(f"Tokens: {vue_result.usage.total_tokens}")
    except Exception as e:
        print(f"⚠️ Vue generation error: {e}")
    
    # 2. Auto-fix Capabilities
    print("\n2. 🔧 AUTO-FIX CAPABILITIES")
    print("-" * 40)
    
    print("\n🩹 Code with Auto-fix Enabled:")
    try:
        autofix_result = await generateText(
            model=vercel.language_model("v0-1.5-lg"),
            prompt="""Fix and improve this React component:
            
            function UserCard(props) {
              const [data, setData] = useState();
              
              useEffect(() => {
                fetchUser(props.userId).then(setData);
              });
              
              return (
                <div className="card">
                  <h2>{data.name}</h2>
                  <p>{data.email}</p>
                </div>
              );
            }""",
            max_tokens=400,
            provider_options={
                "vercel": {
                    "framework": "react",
                    "typescript": True,
                    "enable_auto_fix": True,
                    "enable_quick_edit": True
                }
            }
        )
        print(f"Fixed Component:\n{autofix_result.text}")
        print("✅ Auto-fix applied common issues (dependencies, null checks, TypeScript)")
        print(f"Tokens: {autofix_result.usage.total_tokens}")
    except Exception as e:
        print(f"⚠️ Auto-fix error: {e}")
    
    # 3. Streaming Generation
    print("\n3. 🌊 STREAMING CODE GENERATION")
    print("-" * 40)
    
    print("\n⚡ Streaming API Route Generation:")
    try:
        stream = streamText(
            model=vercel.language_model("v0-1.5-lg"),
            prompt="Create a Next.js API route for user authentication with JWT tokens",
            max_tokens=400,
            provider_options={
                "vercel": {
                    "framework": "next.js",
                    "typescript": True,
                    "enable_auto_fix": True,
                    "project_type": "api"
                }
            }
        )
        
        full_code = ""
        print("Generating API route:")
        async for chunk in stream:
            if chunk.type == "text-delta":
                print(chunk.text, end="", flush=True)
                full_code += chunk.text
            elif chunk.type == "finish":
                print(f"\n\n📊 Streaming Stats: {chunk.usage.total_tokens} tokens")
                print("✅ API route generated with streaming")
    except Exception as e:
        print(f"⚠️ Streaming error: {e}")
    
    # 4. Structured Output for Web Development
    print("\n4. 🏗️  STRUCTURED WEB DEVELOPMENT")
    print("-" * 40)
    
    from pydantic import BaseModel, Field
    from typing import List, Optional
    
    class ComponentSpec(BaseModel):
        component_name: str = Field(description="Name of the React component")
        props: List[str] = Field(description="List of props the component accepts")
        hooks_used: List[str] = Field(description="React hooks used in the component")
        styling_approach: str = Field(description="Styling method used")
        accessibility_features: List[str] = Field(description="Accessibility features included")
        complexity_score: int = Field(description="Complexity score 1-10", ge=1, le=10)
        framework_specific_features: List[str] = Field(description="Framework-specific optimizations")
    
    print("\n📋 Generating structured component specification:")
    try:
        structured_result = await generateObject(
            model=vercel.language_model("v0-1.5-lg"),
            schema=ComponentSpec,
            prompt="""Analyze and create a specification for a React component that displays 
            a data table with sorting, filtering, and pagination features""",
            provider_options={
                "vercel": {
                    "framework": "react",
                    "typescript": True,
                    "design_system": "material-ui"
                }
            }
        )
        
        spec = structured_result.object
        print(f"Component: {spec.component_name}")
        print(f"Props: {', '.join(spec.props)}")
        print(f"Hooks: {', '.join(spec.hooks_used)}")
        print(f"Styling: {spec.styling_approach}")
        print(f"Accessibility: {', '.join(spec.accessibility_features)}")
        print(f"Complexity Score: {spec.complexity_score}/10")
        print(f"Framework Features: {', '.join(spec.framework_specific_features)}")
        print(f"Tokens used: {structured_result.usage.total_tokens}")
    except Exception as e:
        print(f"⚠️ Structured output error: {e}")
    
    # 5. Model Comparison
    print("\n5. ⚖️  MODEL PERFORMANCE COMPARISON")
    print("-" * 40)
    
    comparison_prompt = "Create a simple React button component with click handler"
    models_to_compare = [
        ("v0-1.0-md", "v0 1.0 Medium"),
        ("v0-1.5-md", "v0 1.5 Medium"),
        ("v0-1.5-lg", "v0 1.5 Large"),
    ]
    
    print(f"\n📊 Comparing v0 models on: '{comparison_prompt}'")
    print()
    
    for model_id, model_name in models_to_compare:
        try:
            start_time = asyncio.get_event_loop().time()
            result = await generateText(
                model=vercel.language_model(model_id),
                prompt=comparison_prompt,
                max_tokens=200,
                provider_options={
                    "vercel": {
                        "framework": "react",
                        "typescript": True
                    }
                }
            )
            end_time = asyncio.get_event_loop().time()
            
            response_time = end_time - start_time
            lines_of_code = len([line for line in result.text.split('\n') if line.strip()])
            
            print(f"🤖 {model_name}:")
            print(f"Generated Code:\n{result.text}")
            print(f"Stats: {lines_of_code} lines, {result.usage.total_tokens} tokens, {response_time:.2f}s")
            print()
        except Exception as e:
            print(f"⚠️ {model_name} error: {e}")
            print()
    
    # 6. Advanced Web Development Patterns
    print("\n6. 🔬 ADVANCED WEB DEVELOPMENT PATTERNS")
    print("-" * 40)
    
    # Full-stack application architecture
    print("\n🏢 Full-Stack Application Architecture:")
    try:
        architecture_result = await generateText(
            model=vercel.language_model("v0-1.5-lg"),
            prompt="""Design a complete Next.js application architecture for an e-commerce platform including:
            - API routes structure
            - Database schema considerations  
            - Component organization
            - State management approach
            - Authentication flow""",
            max_tokens=600,
            provider_options={
                "vercel": {
                    "framework": "next.js",
                    "typescript": True,
                    "project_type": "web",
                    "enable_auto_fix": True
                }
            }
        )
        print(f"Architecture Design:\n{architecture_result.text}")
        print(f"Tokens: {architecture_result.usage.total_tokens}")
    except Exception as e:
        print(f"⚠️ Architecture design error: {e}")
    
    # Performance optimization suggestions
    print("\n⚡ Performance Optimization:")
    try:
        perf_result = await generateText(
            model=vercel.language_model("v0-1.5-lg"),
            prompt="Analyze and optimize this React component for better performance and provide specific recommendations",
            max_tokens=400,
            provider_options={
                "vercel": {
                    "framework": "react",
                    "typescript": True,
                    "enable_auto_fix": True,
                    "enable_quick_edit": True
                }
            }
        )
        print(f"Performance Analysis:\n{perf_result.text}")
        print(f"Tokens: {perf_result.usage.total_tokens}")
    except Exception as e:
        print(f"⚠️ Performance optimization error: {e}")
    
    # 7. Design System Integration
    print("\n7. 🎨 DESIGN SYSTEM INTEGRATION")
    print("-" * 40)
    
    design_systems = [
        ("tailwind", "Tailwind CSS"),
        ("material-ui", "Material-UI"),
        ("chakra", "Chakra UI")
    ]
    
    print("\n🎨 Component Generation with Different Design Systems:")
    for system_id, system_name in design_systems:
        try:
            design_result = await generateText(
                model=vercel.language_model("v0-1.5-md"),
                prompt="Create a card component with title, description, and action button",
                max_tokens=250,
                provider_options={
                    "vercel": {
                        "framework": "react",
                        "typescript": True,
                        "design_system": system_id,
                        "enable_auto_fix": True
                    }
                }
            )
            print(f"\n{system_name} Implementation:")
            print(f"Code: {design_result.text[:200]}...")
            print(f"Tokens: {design_result.usage.total_tokens}")
        except Exception as e:
            print(f"⚠️ {system_name} error: {e}")
    
    print("\n🎉 VERCEL PROVIDER DEMONSTRATION COMPLETE!")
    print("=" * 60)
    print("\n✅ Successfully demonstrated:")
    print("   • Framework-aware code generation (Next.js, React, Vue)")
    print("   • Auto-fix capabilities for common coding issues")
    print("   • Quick edit features for inline improvements") 
    print("   • Streaming code generation")
    print("   • Structured component specifications")
    print("   • Model performance comparison")
    print("   • Full-stack architecture design")
    print("   • Performance optimization recommendations")
    print("   • Design system integration (Tailwind, Material-UI, Chakra)")
    print("   • TypeScript support and best practices")
    print("\n🌐 Vercel v0: The AI-Powered Web Development Assistant!")
    
    # Clean up
    await vercel.close()


if __name__ == "__main__":
    # Run the comprehensive demonstration
    asyncio.run(demonstrate_vercel_capabilities())