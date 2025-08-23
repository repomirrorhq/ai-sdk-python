#!/usr/bin/env python3
"""
Deepgram Provider Example

This example demonstrates how to use the Deepgram provider for:
1. Advanced speech-to-text transcription with AI features
2. Speaker identification and diarization
3. Sentiment analysis and topic detection
4. Entity recognition and summarization
5. Real-time and pre-recorded audio processing

Make sure to set your Deepgram API key:
export DEEPGRAM_API_KEY="your-api-key-here"
"""

import asyncio
import os
import tempfile
from pathlib import Path
from typing import Optional

from ai_sdk.providers.deepgram import DeepgramProvider


async def basic_transcription_examples():
    """Demonstrate basic Deepgram transcription capabilities."""
    print("🎧 Deepgram Basic Transcription Examples")
    print("=" * 50)
    
    # Initialize provider
    provider = DeepgramProvider()
    
    # Note: For real examples, you would need actual audio files
    # This example shows the API structure and available models
    
    print("\n1. Available Deepgram Models")
    print("-" * 30)
    
    models = [
        ("nova-3", "Latest Nova model - highest accuracy"),
        ("nova-3-general", "Nova 3 optimized for general use"),
        ("nova-3-medical", "Nova 3 optimized for medical terminology"),
        ("nova-2", "Nova 2 - balanced accuracy and speed"),
        ("nova-2-meeting", "Nova 2 optimized for meetings"),
        ("nova-2-phonecall", "Nova 2 optimized for phone calls"),
        ("nova-2-finance", "Nova 2 optimized for finance"),
        ("enhanced", "Enhanced model - good accuracy"),
        ("enhanced-meeting", "Enhanced model for meetings"),
        ("base", "Base model - fastest processing"),
        ("base-meeting", "Base model for meetings"),
        ("base-phonecall", "Base model for phone calls"),
    ]
    
    for model_id, description in models:
        print(f"✅ {model_id}: {description}")
    
    print("\n2. Basic Transcription (API structure)")
    print("-" * 30)
    print("# Example audio file transcription:")
    print("# with open('audio.mp3', 'rb') as f:")
    print("#     audio_data = f.read()")
    print("# ")
    print("# transcription_model = provider.transcription('nova-3')")
    print("# result = await transcription_model.transcribe(")
    print("#     audio=audio_data,")
    print("#     media_type='audio/mp3'")
    print("# )")
    print("# ")
    print("# print(f'Transcribed text: {result.text}')")
    print("# print(f'Duration: {result.duration_seconds}s')")
    print("# print(f'Language: {result.language}')")


async def advanced_transcription_examples():
    """Demonstrate advanced Deepgram transcription features."""
    print("\n\n🚀 Deepgram Advanced Features Examples")
    print("=" * 50)
    
    provider = DeepgramProvider()
    
    print("\n1. Speaker Diarization")
    print("-" * 30)
    print("# Identify different speakers in conversation")
    print("# result = await transcription_model.transcribe(")
    print("#     audio=audio_data,")
    print("#     media_type='audio/mp3',")
    print("#     provider_options={")
    print("#         'diarize': True,      # Enable speaker identification")
    print("#         'utterances': True,   # Segment by speakers")
    print("#     }")
    print("# )")
    print("# ")
    print("# for segment in result.segments:")
    print("#     speaker = segment.speaker_id or 'Unknown'")
    print("#     print(f'{speaker}: {segment.text}')")
    
    print("\n2. Smart Formatting & Analysis")
    print("-" * 30)
    print("# Advanced text processing and AI analysis")
    print("# result = await transcription_model.transcribe(")
    print("#     audio=audio_data,")
    print("#     media_type='audio/mp3',")
    print("#     provider_options={")
    print("#         'smart_format': True,     # Format numbers, dates, times")
    print("#         'punctuate': True,        # Add punctuation")
    print("#         'paragraphs': True,       # Format into paragraphs")
    print("#         'sentiment': True,        # Analyze sentiment")
    print("#         'topics': True,           # Detect topics")
    print("#         'summarize': 'v2',        # Generate summary")
    print("#         'detect_entities': True,  # Named entity recognition")
    print("#     }")
    print("# )")
    print("# ")
    print("# # Access AI analysis results")
    print("# if 'sentiments' in result.metadata:")
    print("#     for sentiment in result.metadata['sentiments']:")
    print("#         print(f'Sentiment: {sentiment[\"sentiment\"]} (confidence: {sentiment[\"confidence\"]})')")
    print("# ")
    print("# if 'topics' in result.metadata:")
    print("#     for topic in result.metadata['topics']:")
    print("#         print(f'Topic: {topic[\"topic\"]} (confidence: {topic[\"confidence\"]})')")
    
    print("\n3. Content Moderation & Redaction")
    print("-" * 30)
    print("# Automatically redact sensitive information")
    print("# result = await transcription_model.transcribe(")
    print("#     audio=audio_data,")
    print("#     media_type='audio/mp3',")
    print("#     provider_options={")
    print("#         'redact': ['ssn', 'credit_card', 'phone', 'email'],")
    print("#         'replace': '[REDACTED]',")
    print("#         'search': 'password',  # Search for specific terms")
    print("#     }")
    print("# )")
    
    print("\n4. Domain-Specific Models")
    print("-" * 30)
    domains = [
        ("nova-3-medical", "Medical terminology and conversations"),
        ("nova-2-finance", "Financial terms and discussions"),
        ("nova-2-meeting", "Meeting recordings and conference calls"),
        ("nova-2-phonecall", "Phone conversations"),
        ("base-conversationalai", "Conversational AI applications"),
        ("base-voicemail", "Voicemail messages"),
    ]
    
    for model_id, use_case in domains:
        print(f"✅ {model_id}: {use_case}")


async def real_time_streaming_examples():
    """Show Deepgram's real-time streaming capabilities."""
    print("\n\n⚡ Real-Time Streaming Examples")
    print("=" * 50)
    
    print("\n1. Live Audio Streaming")
    print("-" * 30)
    print("# Deepgram excels at real-time transcription")
    print("# This would typically use WebSocket connections")
    print("# ")
    print("# import asyncio")
    print("# import websockets")
    print("# ")
    print("# async def stream_audio():")
    print("#     uri = 'wss://api.deepgram.com/v1/listen'")
    print("#     params = {")
    print("#         'model': 'nova-3',")
    print("#         'language': 'en-US',")
    print("#         'smart_format': 'true',")
    print("#         'interim_results': 'true'")
    print("#     }")
    print("#     ")
    print("#     headers = {'Authorization': f'Token {api_key}'}")
    print("#     query_string = '&'.join([f'{k}={v}' for k, v in params.items()])")
    print("#     full_uri = f'{uri}?{query_string}'")
    print("#     ")
    print("#     async with websockets.connect(full_uri, extra_headers=headers) as websocket:")
    print("#         # Send audio data chunks")
    print("#         await websocket.send(audio_chunk)")
    print("#         ")
    print("#         # Receive real-time transcription")
    print("#         response = await websocket.recv()")
    print("#         result = json.loads(response)")
    print("#         print(result['channel']['alternatives'][0]['transcript'])")
    
    print("\n2. Streaming Use Cases")
    print("-" * 30)
    use_cases = [
        "Live captions for video calls",
        "Real-time voice assistants",
        "Live transcription for broadcasts",
        "Interactive voice response (IVR)",
        "Voice-controlled applications",
        "Real-time meeting notes",
        "Live language translation",
        "Voice analytics and monitoring",
    ]
    
    for i, use_case in enumerate(use_cases, 1):
        print(f"{i}. {use_case}")


async def industry_specific_examples():
    """Show industry-specific Deepgram applications."""
    print("\n\n🏢 Industry-Specific Applications")
    print("=" * 50)
    
    print("\n1. Healthcare & Medical")
    print("-" * 30)
    print("# Medical transcription with specialized terminology")
    print("# model = provider.transcription('nova-3-medical')")
    print("# result = await model.transcribe(")
    print("#     medical_audio,")
    print("#     provider_options={")
    print("#         'smart_format': True,     # Format medical terms")
    print("#         'detect_entities': True,  # Extract medical entities")
    print("#         'redact': ['patient_id', 'ssn'],  # HIPAA compliance")
    print("#         'punctuate': True,")
    print("#         'paragraphs': True,")
    print("#     }")
    print("# )")
    
    print("\n2. Financial Services")
    print("-" * 30)
    print("# Financial call transcription and compliance")
    print("# model = provider.transcription('nova-2-finance')")
    print("# result = await model.transcribe(")
    print("#     financial_call_audio,")
    print("#     provider_options={")
    print("#         'smart_format': True,     # Format financial numbers")
    print("#         'sentiment': True,        # Analyze customer sentiment")
    print("#         'detect_entities': True,  # Extract financial entities")
    print("#         'topics': True,           # Identify discussion topics")
    print("#         'redact': ['account', 'ssn', 'credit_card'],")
    print("#     }")
    print("# )")
    
    print("\n3. Call Centers & Customer Service")
    print("-" * 30)
    print("# Analyze customer calls for quality and insights")
    print("# model = provider.transcription('nova-2-phonecall')")
    print("# result = await model.transcribe(")
    print("#     customer_call_audio,")
    print("#     provider_options={")
    print("#         'diarize': True,          # Separate agent and customer")
    print("#         'sentiment': True,        # Track emotional tone")
    print("#         'intents': True,          # Understand customer intents")
    print("#         'topics': True,           # Categorize call topics")
    print("#         'summarize': 'v2',        # Generate call summary")
    print("#         'utterances': True,       # Track conversation flow")
    print("#     }")
    print("# )")
    print("# ")
    print("# # Extract insights for quality monitoring")
    print("# customer_sentiment = []")
    print("# agent_sentiment = []")
    print("# ")
    print("# for segment in result.segments:")
    print("#     if segment.speaker_id == '0':  # Customer")
    print("#         customer_sentiment.append(segment.confidence)")
    print("#     elif segment.speaker_id == '1':  # Agent")
    print("#         agent_sentiment.append(segment.confidence)")
    
    print("\n4. Media & Broadcasting")
    print("-" * 30)
    print("# Broadcast transcription and content analysis")
    print("# model = provider.transcription('enhanced-general')")
    print("# result = await model.transcribe(")
    print("#     broadcast_audio,")
    print("#     provider_options={")
    print("#         'paragraphs': True,       # Structure content")
    print("#         'topics': True,           # Identify news topics") 
    print("#         'detect_entities': True,  # Extract people, places, orgs")
    print("#         'search': 'breaking news', # Find specific content")
    print("#         'smart_format': True,     # Format names and numbers")
    print("#     }")
    print("# )")


async def integration_examples():
    """Show how to integrate Deepgram with other AI SDK features."""
    print("\n\n🔗 Integration Examples")
    print("=" * 50)
    
    print("\n1. Voice Assistant Pipeline")
    print("-" * 30)
    print("# Complete voice-to-voice assistant")
    print("from ai_sdk import OpenAI")
    print("from ai_sdk.providers.deepgram import DeepgramProvider")
    print("from ai_sdk.providers.elevenlabs import ElevenLabsProvider")
    print("")
    print("async def voice_assistant_pipeline(audio_input):")
    print("    # 1. Transcribe with Deepgram (best accuracy)")
    print("    deepgram = DeepgramProvider()")
    print("    transcription = await deepgram.transcription('nova-3').transcribe(")
    print("        audio=audio_input,")
    print("        provider_options={'smart_format': True, 'punctuate': True}")
    print("    )")
    print("    ")
    print("    # 2. Process with OpenAI")
    print("    openai = OpenAI()")
    print("    response = await openai.language_model('gpt-4').generate(")
    print("        messages=[{'role': 'user', 'content': transcription.text}]")
    print("    )")
    print("    ")
    print("    # 3. Convert to speech with ElevenLabs")
    print("    elevenlabs = ElevenLabsProvider()")
    print("    speech = await elevenlabs.speech('eleven_v3').generate(")
    print("        text=response.text")
    print("    )")
    print("    ")
    print("    return speech.audio, transcription.metadata")
    
    print("\n2. Meeting Analysis System")
    print("-" * 30)
    print("# Comprehensive meeting transcription and analysis")
    print("async def analyze_meeting(meeting_audio):")
    print("    deepgram = DeepgramProvider()")
    print("    model = deepgram.transcription('nova-2-meeting')")
    print("    ")
    print("    result = await model.transcribe(")
    print("        audio=meeting_audio,")
    print("        provider_options={")
    print("            'diarize': True,          # Identify speakers")
    print("            'summarize': 'v2',        # Generate summary")
    print("            'topics': True,           # Extract topics")
    print("            'sentiment': True,        # Track sentiment")
    print("            'detect_entities': True,  # Find action items")
    print("            'utterances': True,       # Conversation flow")
    print("            'smart_format': True,     # Clean formatting")
    print("        }")
    print("    )")
    print("    ")
    print("    # Extract structured insights")
    print("    analysis = {")
    print("        'transcript': result.text,")
    print("        'duration': result.duration_seconds,")
    print("        'speakers': len(set(s.speaker_id for s in result.segments if s.speaker_id)),")
    print("        'summary': result.metadata.get('summaries', []),")
    print("        'topics': result.metadata.get('topics', []),")
    print("        'sentiment_analysis': result.metadata.get('sentiments', []),")
    print("        'entities': result.metadata.get('entities', []),")
    print("    }")
    print("    ")
    print("    return analysis")
    
    print("\n3. Content Compliance Monitor")
    print("-" * 30)
    print("# Monitor audio content for compliance")
    print("async def compliance_monitor(audio_content, compliance_terms):")
    print("    deepgram = DeepgramProvider()")
    print("    model = deepgram.transcription('enhanced-general')")
    print("    ")
    print("    result = await model.transcribe(")
    print("        audio=audio_content,")
    print("        provider_options={")
    print("            'redact': ['ssn', 'credit_card', 'phone'],")
    print("            'search': ' | '.join(compliance_terms),")
    print("            'detect_entities': True,")
    print("            'sentiment': True,")
    print("        }")
    print("    )")
    print("    ")
    print("    # Check for compliance issues")
    print("    issues = []")
    print("    if 'entities' in result.metadata:")
    print("        for entity in result.metadata['entities']:")
    print("            if entity['label'] in ['PERSON', 'ORGANIZATION']:")
    print("                issues.append(f'Mentioned: {entity[\"value\"]}')")
    print("    ")
    print("    return {'transcript': result.text, 'compliance_issues': issues}")


async def performance_optimization_examples():
    """Show performance optimization techniques."""
    print("\n\n⚡ Performance Optimization")
    print("=" * 50)
    
    print("\n1. Model Selection Guide")
    print("-" * 30)
    
    model_performance = [
        ("base", "Fastest", "Good for real-time applications"),
        ("enhanced", "Balanced", "Good accuracy-speed balance"),
        ("nova-2", "High accuracy", "Better accuracy, slightly slower"),
        ("nova-3", "Highest accuracy", "Best accuracy, slowest"),
    ]
    
    for model, speed, use_case in model_performance:
        print(f"✅ {model}: {speed} - {use_case}")
    
    print("\n2. Optimization Tips")
    print("-" * 30)
    
    tips = [
        "Choose the right model for your use case (base for speed, nova-3 for accuracy)",
        "Use domain-specific models (medical, finance, meeting) when applicable", 
        "Enable only the features you need (sentiment, topics, etc.) to reduce processing time",
        "For real-time applications, use streaming with interim results",
        "Batch process multiple files for better throughput",
        "Use appropriate audio formats (WAV for best quality, MP3 for size)",
        "Pre-process audio to remove silence and normalize volume",
        "Cache results for repeated content analysis",
    ]
    
    for i, tip in enumerate(tips, 1):
        print(f"{i}. {tip}")
    
    print("\n3. Error Handling Best Practices")
    print("-" * 30)
    print("from ai_sdk.errors import APICallError, AISDKError")
    print("")
    print("try:")
    print("    result = await transcription_model.transcribe(audio_data)")
    print("except APICallError as e:")
    print("    print(f'API error: {e.message}')")
    print("    print(f'Status code: {e.status_code}')")
    print("    # Handle rate limiting, authentication, etc.")
    print("except AISDKError as e:")
    print("    print(f'SDK error: {e}')")
    print("    # Handle validation, processing errors")
    print("except Exception as e:")
    print("    print(f'Unexpected error: {e}')")


async def main():
    """Run all Deepgram examples."""
    print("🎙️ Deepgram AI Provider - Comprehensive Examples")
    print("=" * 60)
    
    # Check for API key
    if not os.getenv("DEEPGRAM_API_KEY"):
        print("❌ Please set your DEEPGRAM_API_KEY environment variable")
        print("   export DEEPGRAM_API_KEY='your-api-key-here'")
        print("\n   You can get your API key from: https://console.deepgram.com/")
        return
    
    try:
        # Run examples
        await basic_transcription_examples()
        await advanced_transcription_examples()
        await real_time_streaming_examples()
        await industry_specific_examples()
        await integration_examples()
        await performance_optimization_examples()
        
        print("\n\n🎉 All Deepgram examples completed!")
        print("=" * 60)
        
        print("\nNext Steps:")
        print("1. Try the examples with your own audio files")
        print("2. Experiment with domain-specific models")
        print("3. Integrate advanced AI features (sentiment, topics, entities)")
        print("4. Build real-time transcription applications")
        print("5. Explore streaming WebSocket connections")
        print("6. Create voice analytics and monitoring systems")
        
    except KeyboardInterrupt:
        print("\n👋 Examples interrupted by user")
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())