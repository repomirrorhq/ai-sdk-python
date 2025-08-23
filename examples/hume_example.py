"""Hume AI provider examples for emotionally expressive speech synthesis."""

import asyncio
from pathlib import Path
from ai_sdk.providers.hume import (
    create_hume,
    HumeSpeechSettings,
    HumeUtterance,
    HumeVoiceById,
    HumeVoiceByName,
    HumeContextUtterances,
    HumeContextGeneration,
    HumeFormatSpec,
)


async def basic_emotional_speech_example():
    """Basic emotional speech synthesis with Hume."""
    print("=== Basic Hume Emotional Speech ===")
    
    # Create provider (requires HUME_API_KEY environment variable)
    provider = create_hume()
    
    try:
        # Create speech model
        model = provider.speech_model()
        
        # Generate emotionally expressive speech
        print("Generating emotional speech...")
        result = await model.generate("I'm absolutely thrilled about this amazing breakthrough in AI!")
        
        # Save audio file
        output_path = Path("hume_excited.mp3")
        with open(output_path, "wb") as f:
            f.write(result.audio)
        
        print(f"Saved emotional speech to: {output_path}")
        
        # Show usage information
        if result.usage:
            print(f"Characters processed: {result.usage.characters}")
        
        # Show any warnings
        for warning in result.warnings:
            print(f"Warning: {warning}")
        
    except Exception as e:
        print(f"Emotional speech generation error: {e}")


async def advanced_voice_control_example():
    """Advanced speech with specific voice and emotional instructions."""
    print("\n=== Advanced Hume Voice Control ===")
    
    provider = create_hume()
    
    try:
        model = provider.speech_model()
        
        # Generate with specific voice and detailed instructions
        print("Generating speech with specific voice and emotional instruction...")
        result = await model.generate(
            text="The sunset over the mountains was breathtaking, with colors I had never seen before.",
            voice="d8ab67c6-953d-4bd8-9370-8fa53a0f1453",  # Hume's default voice ID
            instructions="Express deep awe and wonder, speaking slowly with reverence for nature's beauty",
            speed=0.85,  # Slightly slower for contemplative effect
            output_format="wav",  # High quality format
        )
        
        # Save high-quality audio
        output_path = Path("hume_sunset_awe.wav")
        with open(output_path, "wb") as f:
            f.write(result.audio)
        
        print(f"Saved emotionally nuanced speech to: {output_path}")
        
    except Exception as e:
        print(f"Advanced voice control error: {e}")


async def multi_utterance_conversation_example():
    """Multiple utterances with different emotional expressions."""
    print("\n=== Hume Multi-Utterance Conversation ===")
    
    provider = create_hume()
    
    try:
        model = provider.speech_model()
        
        # Create a conversation with varying emotions
        utterances = [
            HumeUtterance(
                text="Good morning! How wonderful to see you today!",
                description="Warm, enthusiastic greeting with genuine happiness",
                speed=1.1,
                voice=HumeVoiceById(id="d8ab67c6-953d-4bd8-9370-8fa53a0f1453"),
            ),
            HumeUtterance(
                text="I hope you're feeling well.",
                description="Caring and empathetic concern for the listener's wellbeing",
                speed=0.95,
                trailing_silence=0.8,
            ),
            HumeUtterance(
                text="Is there anything exciting happening in your life lately?",
                description="Curious and interested, inviting the person to share good news",
                speed=1.0,
                trailing_silence=1.0,
            ),
        ]
        
        # Configure context for multi-utterance synthesis
        context = HumeContextUtterances(utterances=utterances)
        options = HumeSpeechSettings(
            context=context,
            format=HumeFormatSpec(type="mp3")
        )
        
        print("Generating emotional conversation...")
        result = await model.generate(
            text="This text will be replaced by the context utterances",
            options=options
        )
        
        # Save conversation
        output_path = Path("hume_conversation.mp3")
        with open(output_path, "wb") as f:
            f.write(result.audio)
        
        print(f"Saved emotional conversation to: {output_path}")
        print(f"Generated conversation with {len(utterances)} emotionally distinct utterances")
        
    except Exception as e:
        print(f"Multi-utterance conversation error: {e}")


async def emotional_storytelling_example():
    """Emotional storytelling with different moods."""
    print("\n=== Hume Emotional Storytelling ===")
    
    provider = create_hume()
    
    try:
        model = provider.speech_model()
        
        # Story segments with different emotional tones
        story_segments = [
            {
                "text": "Once upon a time, in a magical forest filled with wonder...",
                "emotion": "Begin with enchantment and mystery, drawing the listener into a magical world",
            },
            {
                "text": "A brave little rabbit discovered something extraordinary.",
                "emotion": "Build excitement and anticipation about the discovery",
            },
            {
                "text": "But dark clouds gathered overhead, and danger was near.",
                "emotion": "Shift to tension and concern, creating suspense",
            },
            {
                "text": "With courage in her heart, she found the strength to overcome.",
                "emotion": "Inspire with determination and hope, building to triumph",
            },
            {
                "text": "And they all lived happily ever after.",
                "emotion": "End with warm satisfaction and contentment",
            },
        ]
        
        # Generate each segment with appropriate emotion
        print("Generating emotional story segments...")
        
        for i, segment in enumerate(story_segments):
            result = await model.generate(
                text=segment["text"],
                instructions=segment["emotion"],
                speed=0.9,  # Storytelling pace
            )
            
            # Save each segment
            output_path = Path(f"hume_story_segment_{i+1}.mp3")
            with open(output_path, "wb") as f:
                f.write(result.audio)
            
            print(f"Saved story segment {i+1} to: {output_path}")
        
        print(f"Generated {len(story_segments)} emotionally varied story segments")
        
    except Exception as e:
        print(f"Emotional storytelling error: {e}")


async def voice_comparison_example():
    """Compare different voices and emotional expressions."""
    print("\n=== Hume Voice Comparison ===")
    
    provider = create_hume()
    
    try:
        model = provider.speech_model()
        
        # Test text
        test_text = "This is a demonstration of emotional voice synthesis."
        
        # Different voice configurations
        voice_configs = [
            {
                "name": "Default Voice - Neutral",
                "voice": None,
                "instructions": "Speak in a clear, neutral tone",
            },
            {
                "name": "Happy Expression",
                "voice": "d8ab67c6-953d-4bd8-9370-8fa53a0f1453",
                "instructions": "Express joy and enthusiasm",
            },
            {
                "name": "Contemplative Mood",
                "voice": "d8ab67c6-953d-4bd8-9370-8fa53a0f1453",
                "instructions": "Thoughtful and reflective, as if pondering something profound",
            },
            {
                "name": "Excited Discovery",
                "voice": "d8ab67c6-953d-4bd8-9370-8fa53a0f1453",
                "instructions": "Convey the excitement of making an amazing discovery",
            },
        ]
        
        print("Generating voice comparisons...")
        
        for i, config in enumerate(voice_configs):
            result = await model.generate(
                text=test_text,
                voice=config["voice"],
                instructions=config["instructions"],
            )
            
            # Save comparison
            filename = config["name"].lower().replace(" ", "_")
            output_path = Path(f"hume_{filename}.mp3")
            with open(output_path, "wb") as f:
                f.write(result.audio)
            
            print(f"Saved '{config['name']}' to: {output_path}")
        
    except Exception as e:
        print(f"Voice comparison error: {e}")


async def generation_reuse_example():
    """Example of reusing previous generation context."""
    print("\n=== Hume Generation Reuse ===")
    
    provider = create_hume()
    
    try:
        # Note: This example shows the concept but would need
        # a real generation ID from a previous Hume API call
        
        print("This example demonstrates how to reuse previous generations.")
        print("In practice, you would save generation IDs from previous API calls.")
        
        # Example of how you would reuse a generation
        example_generation_id = "gen_123456789"  # This would be from a real API response
        
        model = provider.speech_model()
        
        # Configure to reuse previous generation
        context = HumeContextGeneration(generation_id=example_generation_id)
        options = HumeSpeechSettings(context=context)
        
        print(f"Would reuse generation: {example_generation_id}")
        print("This allows building on previous emotional expressions and maintaining consistency")
        
    except Exception as e:
        print(f"Generation reuse error: {e}")


async def format_comparison_example():
    """Compare different audio formats."""
    print("\n=== Hume Format Comparison ===")
    
    provider = create_hume()
    
    try:
        model = provider.speech_model()
        
        text = "This is a test of different audio formats in Hume AI."
        formats = ["mp3", "wav", "pcm"]
        
        print("Generating audio in different formats...")
        
        for format_type in formats:
            options = HumeSpeechSettings(
                format=HumeFormatSpec(type=format_type)  # type: ignore
            )
            
            result = await model.generate(
                text=text,
                instructions="Clear and professional delivery",
                options=options
            )
            
            # Save with appropriate extension
            ext = format_type if format_type != "pcm" else "raw"
            output_path = Path(f"hume_format_test.{ext}")
            
            with open(output_path, "wb") as f:
                f.write(result.audio)
            
            print(f"Saved {format_type.upper()} format to: {output_path}")
        
    except Exception as e:
        print(f"Format comparison error: {e}")


async def emotional_range_demo():
    """Demonstrate the full range of emotional expressions."""
    print("\n=== Hume Emotional Range Demo ===")
    
    provider = create_hume()
    
    try:
        model = provider.speech_model()
        
        # Different emotional scenarios
        emotional_expressions = [
            {
                "text": "Congratulations on your amazing achievement!",
                "emotion": "Pure excitement and celebration, as if cheering for a friend's success",
                "filename": "celebration",
            },
            {
                "text": "I understand this must be really difficult for you.",
                "emotion": "Deep empathy and compassion, offering gentle support",
                "filename": "empathy", 
            },
            {
                "text": "The view from the mountaintop was absolutely magnificent.",
                "emotion": "Awe and wonder at natural beauty, breathtaken by the scene",
                "filename": "wonder",
            },
            {
                "text": "Let's work together to solve this challenging problem.",
                "emotion": "Determined collaboration, confident and encouraging",
                "filename": "determination",
            },
            {
                "text": "Once upon a time, in a land far, far away...",
                "emotion": "Gentle storytelling voice, creating magical atmosphere for children",
                "filename": "storytelling",
            },
        ]
        
        print("Generating full emotional range demonstration...")
        
        for expr in emotional_expressions:
            result = await model.generate(
                text=expr["text"],
                instructions=expr["emotion"],
                speed=0.95,
            )
            
            output_path = Path(f"hume_emotion_{expr['filename']}.mp3")
            with open(output_path, "wb") as f:
                f.write(result.audio)
            
            print(f"Generated {expr['filename']} emotion: {output_path}")
        
        print(f"\nCreated {len(emotional_expressions)} examples of emotional expression")
        print("These demonstrate Hume's ability to convey nuanced human emotions through speech")
        
    except Exception as e:
        print(f"Emotional range demo error: {e}")


if __name__ == "__main__":
    print("Hume AI Provider Examples")
    print("=========================")
    print("Make sure to set HUME_API_KEY environment variable before running.\n")
    
    # Run examples
    asyncio.run(basic_emotional_speech_example())
    asyncio.run(advanced_voice_control_example())
    asyncio.run(multi_utterance_conversation_example())
    asyncio.run(emotional_storytelling_example())
    asyncio.run(voice_comparison_example())
    asyncio.run(generation_reuse_example())
    asyncio.run(format_comparison_example())
    asyncio.run(emotional_range_demo())