#!/usr/bin/env python3
"""
Test different ElevenLabs WebSocket endpoints and authentication methods
"""

import asyncio
import websockets
import json
import requests
from datetime import datetime

async def test_websocket_endpoints(api_key):
    """Test different WebSocket endpoints for ElevenLabs."""
    
    print("🔍 Testing ElevenLabs WebSocket endpoints...")
    print(f"📁 API Key: {'*' * 20}{api_key[-4:]}")
    print("=" * 60)
    
    # Different possible WebSocket URLs
    ws_urls = [
        "wss://api.elevenlabs.io/v1/conversational-ai/agent_01jydy1bkeefwsmp63xbp1kn0n/stream",
        "wss://api.elevenlabs.io/v1/stream",
        "wss://api.elevenlabs.io/v1/conversation/stream",
        "wss://api.elevenlabs.io/v1/ai-conversation/stream",
        "wss://api.elevenlabs.io/v1/real-time/stream",
        "wss://api.elevenlabs.io/v1/live-conversation/stream"
    ]
    
    # Different header configurations
    header_configs = [
        {"xi-api-key": api_key, "Content-Type": "application/json"},
        {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        {"X-API-Key": api_key, "Content-Type": "application/json"},
        {"xi-api-key": api_key}
    ]
    
    for i, ws_url in enumerate(ws_urls):
        print(f"\n🔗 Testing WebSocket URL {i+1}: {ws_url}")
        
        for j, headers in enumerate(header_configs):
            print(f"   📋 Header config {j+1}: {list(headers.keys())}")
            
            try:
                async with websockets.connect(
                    ws_url,
                    additional_headers=headers,
                    ping_interval=10,
                    ping_timeout=5
                ) as websocket:
                    print(f"   ✅ Connected successfully!")
                    
                    # Try to send a test message
                    test_message = {
                        "type": "connection",
                        "agent_id": "agent_01jydy1bkeefwsmp63xbp1kn0n",
                        "session_id": f"test_session_{datetime.now().timestamp()}"
                    }
                    
                    await websocket.send(json.dumps(test_message))
                    print(f"   ✅ Sent test message")
                    
                    # Wait for response
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                        print(f"   ✅ Received response: {response[:100]}...")
                    except asyncio.TimeoutError:
                        print(f"   ⏰ No response received (timeout)")
                    
                    break  # If we get here, this configuration works
                    
            except websockets.exceptions.InvalidURI:
                print(f"   ❌ Invalid URI")
            except websockets.exceptions.ConnectionClosed as e:
                print(f"   ❌ Connection closed: {e}")
            except Exception as e:
                print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("📝 Analysis:")
    print("   - If no connections worked, WebSocket API might not be publicly available")
    print("   - Or might require different authentication method")
    print("   - Or might be in beta/private access only")

def test_rest_endpoints(api_key):
    """Test REST endpoints to understand available features."""
    
    print("\n🔍 Testing REST endpoints for conversational AI...")
    
    headers = {"xi-api-key": api_key}
    base_url = "https://api.elevenlabs.io/v1"
    
    # Test various endpoints
    endpoints = [
        "/conversational-ai",
        "/conversational-ai/agents",
        "/conversational-ai/agent_01jydy1bkeefwsmp63xbp1kn0n",
        "/agents",
        "/agents/agent_01jydy1bkeefwsmp63xbp1kn0n",
        "/conversation",
        "/conversations",
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
                    print(f"   ✅ Available: {list(data.keys()) if isinstance(data, dict) else type(data)}")
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

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python test_elevenlabs_websocket.py <api_key>")
        sys.exit(1)
    
    api_key = sys.argv[1]
    
    # Test REST endpoints first
    test_rest_endpoints(api_key)
    
    # Then test WebSocket endpoints
    asyncio.run(test_websocket_endpoints(api_key)) 