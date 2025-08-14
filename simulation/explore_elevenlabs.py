#!/usr/bin/env python3
"""
Explore ElevenLabs API endpoints to find conversational AI features
"""

import requests
import json

def explore_elevenlabs_api(api_key):
    """Explore available ElevenLabs API endpoints."""
    
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    
    base_url = "https://api.elevenlabs.io/v1"
    
    print("🔍 Exploring ElevenLabs API endpoints...")
    print(f"📁 API Key: {'*' * 20}{api_key[-4:]}")
    print("=" * 60)
    
    # Test various endpoints
    endpoints = [
        "/user",
        "/voices", 
        "/conversation",
        "/conversations",
        "/chat",
        "/stream",
        "/text-to-speech",
        "/speech-to-speech",
        "/conversational-ai",
        "/ai-conversation",
        "/real-time",
        "/live-conversation"
    ]
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", headers=headers)
            print(f"🔗 {endpoint}: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, dict):
                        if "voices" in data:
                            print(f"   ✅ Found {len(data['voices'])} voices")
                        elif "conversations" in data:
                            print(f"   ✅ Found {len(data['conversations'])} conversations")
                        elif "user" in data:
                            print(f"   ✅ User info available")
                        else:
                            print(f"   ✅ Available: {list(data.keys())}")
                    else:
                        print(f"   ✅ Available: {type(data)}")
                except:
                    print(f"   ✅ Available (non-JSON response)")
            elif response.status_code == 404:
                print(f"   ❌ Not Found")
            elif response.status_code == 403:
                print(f"   🔒 Forbidden (needs different permissions)")
            else:
                print(f"   ⚠️  Status: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("📝 Analysis:")
    print("   - REST API endpoints are working")
    print("   - WebSocket endpoints might need different authentication")
    print("   - Conversational AI might be in beta or require special access")
    print("   - Let's check if there are any conversational AI SDKs available")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python explore_elevenlabs.py <api_key>")
        sys.exit(1)
    
    api_key = sys.argv[1]
    explore_elevenlabs_api(api_key) 