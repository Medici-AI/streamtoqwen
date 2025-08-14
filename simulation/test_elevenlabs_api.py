#!/usr/bin/env python3
"""
Test script for ElevenLabs API integration
"""

import requests
import json

def test_elevenlabs_api(api_key):
    """Test ElevenLabs API endpoints."""
    
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    base_url = "https://api.elevenlabs.io/v1"
    
    print("🔍 Testing ElevenLabs API...")
    print(f"📁 API Key: {'*' * 20}{api_key[-4:]}")
    print("=" * 50)
    
    # Test 1: Get user info
    try:
        response = requests.get(f"{base_url}/user", headers=headers)
        print(f"👤 User Info: {response.status_code}")
        if response.status_code == 200:
            user_data = response.json()
            print(f"   Subscription: {user_data.get('subscription', {}).get('tier', 'Unknown')}")
            print(f"   Character Count: {user_data.get('subscription', {}).get('character_count', 0)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Test 2: Get voices
    try:
        response = requests.get(f"{base_url}/voices", headers=headers)
        print(f"🎤 Voices: {response.status_code}")
        if response.status_code == 200:
            voices_data = response.json()
            print(f"   Available voices: {len(voices_data.get('voices', []))}")
            for voice in voices_data.get('voices', [])[:3]:  # Show first 3
                print(f"   - {voice.get('name', 'Unknown')} (ID: {voice.get('voice_id', 'Unknown')})")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Test 3: Check for streaming endpoints
    try:
        response = requests.get(f"{base_url}/conversation", headers=headers)
        print(f"💬 Conversations: {response.status_code}")
        if response.status_code == 200:
            conv_data = response.json()
            print(f"   Available conversations: {len(conv_data.get('conversations', []))}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print()
    
    # Test 4: Check for WebSocket endpoints
    print("🔌 WebSocket Endpoints:")
    print("   Note: WebSocket endpoints might require different authentication")
    print("   or might not be publicly documented")
    
    print()
    print("=" * 50)
    print("📝 Next Steps:")
    print("   1. If API key works, we can use REST API instead of WebSocket")
    print("   2. Or we need to find the correct WebSocket endpoint")
    print("   3. Or use ElevenLabs SDK for easier integration")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python test_elevenlabs_api.py <api_key>")
        sys.exit(1)
    
    api_key = sys.argv[1]
    test_elevenlabs_api(api_key) 