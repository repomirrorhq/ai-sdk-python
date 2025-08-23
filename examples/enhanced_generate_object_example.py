"""Example demonstrating enhanced generate_object with multiple output types."""

import asyncio
from typing import List, Optional

from pydantic import BaseModel, Field

from ai_sdk import (
    generate_object_enhanced,
    create_default_repair_function,
    create_custom_repair_function,
    create_openai,
)


# Example schemas for object generation
class Person(BaseModel):
    """A person with basic information."""
    name: str = Field(description="Full name of the person")
    age: int = Field(description="Age in years", ge=0, le=150)
    email: Optional[str] = Field(description="Email address", default=None)
    occupation: str = Field(description="Job or profession")


class Company(BaseModel):
    """A company with employees."""
    name: str = Field(description="Company name")
    industry: str = Field(description="Industry sector")
    employees: List[Person] = Field(description="List of employees")
    founded_year: int = Field(description="Year the company was founded")


async def object_generation_example():
    """Example of generating a single object."""
    print("🔹 Object Generation Example")
    print("=" * 50)
    
    try:
        model = create_openai()("gpt-3.5-turbo")
    except Exception as e:
        print(f"Failed to create OpenAI model: {e}")
        return
    
    result = await generate_object_enhanced(
        model=model,
        schema=Person,
        output='object',
        prompt="Generate a profile for a software engineer in their 30s",
        schema_name="PersonProfile",
        schema_description="A professional profile for a software engineer"
    )
    
    print(f"Generated Person:")
    print(f"  Name: {result.object.name}")
    print(f"  Age: {result.object.age}")  
    print(f"  Email: {result.object.email}")
    print(f"  Occupation: {result.object.occupation}")
    print(f"  Usage: {result.usage}")
    print()


async def array_generation_example():
    """Example of generating an array of objects."""
    print("🔹 Array Generation Example")
    print("=" * 50)
    
    try:
        model = create_openai()("gpt-3.5-turbo")
    except Exception as e:
        print(f"Failed to create OpenAI model: {e}")
        return
    
    result = await generate_object_enhanced(
        model=model,
        schema=Person,
        output='array',
        prompt="Generate 3 diverse team members for a startup company",
        schema_description="Array of team member profiles"
    )
    
    print(f"Generated Team ({len(result.array)} members):")
    for i, person in enumerate(result.array, 1):
        print(f"  {i}. {person.name} - {person.occupation} (age {person.age})")
    print()


async def enum_generation_example():
    """Example of generating enum values."""
    print("🔹 Enum Generation Example") 
    print("=" * 50)
    
    try:
        model = create_openai()("gpt-3.5-turbo")
    except Exception as e:
        print(f"Failed to create OpenAI model: {e}")
        return
    
    programming_languages = [
        "Python", "JavaScript", "TypeScript", "Go", "Rust", 
        "Java", "C++", "C#", "Ruby", "PHP"
    ]
    
    result = await generate_object_enhanced(
        model=model,
        output='enum',
        enum_values=programming_languages,
        prompt="What's the best programming language for building AI applications?"
    )
    
    print(f"Selected Programming Language: {result.enum_value}")
    print(f"Available options were: {', '.join(programming_languages)}")
    print()


async def no_schema_example():
    """Example of generating without schema constraints."""
    print("🔹 No-Schema Generation Example")
    print("=" * 50)
    
    try:
        model = create_openai()("gpt-3.5-turbo")
    except Exception as e:
        print(f"Failed to create OpenAI model: {e}")
        return
    
    result = await generate_object_enhanced(
        model=model,
        output='no-schema',
        prompt="Write a short haiku about artificial intelligence",
        max_tokens=100
    )
    
    print(f"Generated Haiku:")
    print(f"{result.raw_content}")
    print()


async def text_repair_example():
    """Example demonstrating text repair functionality."""
    print("🔹 Text Repair Example")
    print("=" * 50)
    
    try:
        model = create_openai()("gpt-3.5-turbo")
    except Exception as e:
        print(f"Failed to create OpenAI model: {e}")
        return
    
    # Create a custom repair function for common issues
    custom_repairs = {
        "trailing comma": lambda text: text.rstrip(','),
        "missing quotes": lambda text: text.replace("name:", '"name":'),
    }
    
    repair_function = create_custom_repair_function(custom_repairs)
    
    result = await generate_object_enhanced(
        model=model,
        schema=Person,
        output='object',
        prompt="Generate a person profile (respond in a somewhat casual JSON format)",
        repair_function=repair_function,
        max_repair_attempts=2,
        temperature=0.8  # Higher temperature might produce malformed JSON
    )
    
    print(f"Generated Person (with repair if needed):")
    print(f"  Name: {result.object.name}")
    print(f"  Age: {result.object.age}")
    print(f"  Occupation: {result.object.occupation}")
    
    if result.repair_attempts > 0:
        print(f"  Repair attempts: {result.repair_attempts}")
        print(f"  Repaired content available: {result.repaired_content is not None}")
    
    print()


async def complex_object_example():
    """Example with complex nested objects."""
    print("🔹 Complex Object Example")
    print("=" * 50)
    
    try:
        model = create_openai()("gpt-4o-mini")  # Use a more capable model for complex objects
    except Exception as e:
        print(f"Failed to create OpenAI model: {e}")
        return
    
    result = await generate_object_enhanced(
        model=model,
        schema=Company,
        output='object',
        prompt="Generate a small tech startup with 3-4 employees in different roles",
        schema_name="TechStartup",
        schema_description="A technology startup company with diverse team",
        max_tokens=500
    )
    
    print(f"Generated Company:")
    print(f"  Name: {result.object.name}")
    print(f"  Industry: {result.object.industry}")
    print(f"  Founded: {result.object.founded_year}")
    print(f"  Employees ({len(result.object.employees)}):")
    
    for employee in result.object.employees:
        print(f"    - {employee.name}: {employee.occupation} (age {employee.age})")
    
    print(f"  Usage: {result.usage}")
    print()


async def mode_comparison_example():
    """Example comparing different generation modes."""
    print("🔹 Mode Comparison Example")
    print("=" * 50)
    
    try:
        model = create_openai()("gpt-3.5-turbo")
    except Exception as e:
        print(f"Failed to create OpenAI model: {e}")
        return
    
    prompt = "Generate a person who works in data science"
    
    # Test different modes
    modes = ['auto', 'json']  # 'tool' not implemented yet
    
    for mode in modes:
        print(f"Testing mode: {mode}")
        
        try:
            result = await generate_object_enhanced(
                model=model,
                schema=Person,
                output='object',
                prompt=prompt,
                mode=mode,
                temperature=0.3  # Lower temperature for consistency
            )
            
            print(f"  ✅ Success: {result.object.name} - {result.object.occupation}")
            print(f"     Usage: {result.usage}")
            
        except Exception as e:
            print(f"  ❌ Failed: {e}")
        
        print()


async def main():
    """Run all examples."""
    print("🚀 Enhanced Generate Object Examples")
    print("=" * 60)
    print()
    
    await object_generation_example()
    await array_generation_example()  
    await enum_generation_example()
    await no_schema_example()
    await text_repair_example()
    await complex_object_example()
    await mode_comparison_example()
    
    print("✅ All examples completed!")


if __name__ == "__main__":
    asyncio.run(main())