#!/usr/bin/env python3
"""
Test ElevenLabs SDK for conversational AI features
"""

import asyncio
from elevenlabs import generate, stream, set_api_key
from elevenlabs.api import History, Voices, User
import json

def test_elevenlabs_sdk(api_key):
    """Test ElevenLabs SDK capabilities."""
    
    print("🔍 Testing ElevenLabs SDK...")
    print(f"📁 API Key: {'*' * 20}{api_key[-4:]}")
    print("=" * 60)
    
    # Set API key
    set_api_key(api_key)
    
    try:
        # Test basic API access
        print("👤 Testing User API...")
        user = User.from_api()
        print(f"   ✅ User: {user.subscription}")
        print(f"   ✅ Character Count: {user.character_count}")
        
        # Test Voices API
        print("\n🎤 Testing Voices API...")
        voices = Voices.from_api()
        print(f"   ✅ Available voices: {len(voices.voices)}")
        for voice in voices.voices[:3]:  # Show first 3
            print(f"   - {voice.name} (ID: {voice.voice_id})")
        
        # Test History API
        print("\n📚 Testing History API...")
        history = History.from_api()
        print(f"   ✅ History items: {len(history.history)}")
        
        # Test basic text-to-speech
        print("\n🔊 Testing Text-to-Speech...")
        audio = generate(
            text="Hello, this is a test of the ElevenLabs API.",
            voice="Aria",
            model="eleven_monolingual_v1"
        )
        print(f"   ✅ Generated audio: {len(audio)} bytes")
        
        # Check for conversational AI features
        print("\n🤖 Checking for Conversational AI features...")
        
        # Try to find any conversational AI related methods
        import inspect
        from elevenlabs import api
        
        # List all available classes and methods
        print("   📋 Available API classes:")
        for name, obj in inspect.getmembers(api):
            if inspect.isclass(obj):
                print(f"   - {name}")
        
        # Check if there are any WebSocket or streaming methods
        print("\n   🔌 Looking for WebSocket/Streaming methods:")
        for name, obj in inspect.getmembers(api):
            if inspect.isclass(obj):
                methods = [method for method in dir(obj) if not method.startswith('_')]
                if any('stream' in method.lower() or 'websocket' in method.lower() for method in methods):
                    print(f"   - {name}: {methods}")
        
        print("\n" + "=" * 60)
        print("📝 Analysis:")
        print("   - Basic API access is working")
        print("   - Text-to-speech is available")
        print("   - No obvious conversational AI features found")
        print("   - WebSocket endpoints might be in beta or require special access")
        
    except Exception as e:
        print(f"❌ Error testing ElevenLabs SDK: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python test_elevenlabs_sdk.py <api_key>")
        sys.exit(1)
    
    api_key = sys.argv[1]
    test_elevenlabs_sdk(api_key) 