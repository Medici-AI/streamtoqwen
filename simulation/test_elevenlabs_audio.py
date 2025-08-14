#!/usr/bin/env python3
"""
Test sending audio data to ElevenLabs WebSocket
"""

import asyncio
import websockets
import json
import base64
import numpy as np
from datetime import datetime

async def test_audio_connection(agent_id):
    """Test sending audio data to ElevenLabs WebSocket."""
    
    print("🔍 Testing ElevenLabs WebSocket with audio data...")
    print(f"🤖 Agent ID: {agent_id}")
    print("=" * 60)
    
    # WebSocket URL
    ws_url = f"wss://api.elevenlabs.io/v1/convai/conversation?agent_id={agent_id}"
    
    try:
        async with websockets.connect(
            ws_url,
            ping_interval=20,
            ping_timeout=10
        ) as websocket:
            print("✅ Connected to ElevenLabs WebSocket")
            
            # Send conversation initiation
            await websocket.send(json.dumps({
                "type": "conversation_initiation_client_data"
            }))
            print("📤 Sent conversation initiation")
            
            # Listen for initial response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                print(f"📨 Received: {data.get('type', 'unknown')}")
            except asyncio.TimeoutError:
                print("⏰ No initial response received")
            
            # Generate some test audio data (silence)
            print("🎵 Generating test audio data...")
            
            # Create 1 second of silence (16kHz, 16-bit)
            sample_rate = 16000
            duration = 1.0  # 1 second
            samples = int(sample_rate * duration)
            
            # Generate silence (zeros)
            audio_data = np.zeros(samples, dtype=np.int16)
            
            # Convert to base64
            audio_bytes = audio_data.tobytes()
            audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
            
            # Send audio chunk
            audio_message = {
                "user_audio_chunk": audio_base64
            }
            
            print("📤 Sending audio chunk...")
            await websocket.send(json.dumps(audio_message))
            
            # Listen for responses
            print("👂 Listening for responses...")
            timeout_count = 0
            max_timeouts = 10
            
            while timeout_count < max_timeouts:
                try:
                    response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    data = json.loads(response)
                    event_type = data.get('type', 'unknown')
                    
                    print(f"📨 Received: {event_type}")
                    
                    if event_type == "user_transcript":
                        user_transcription_event = data.get('user_transcription_event', {})
                        user_transcript = user_transcription_event.get('user_transcript', '')
                        print(f"   💬 User transcript: {user_transcript}")
                        
                    elif event_type == "agent_response":
                        agent_response_event = data.get('agent_response_event', {})
                        agent_response = agent_response_event.get('agent_response', '')
                        print(f"   🤖 Agent response: {agent_response}")
                        
                    elif event_type == "audio":
                        audio_event = data.get('audio_event', {})
                        event_id = audio_event.get('event_id', 0)
                        print(f"   🎵 Audio chunk: event_id={event_id}")
                        
                    elif event_type == "interruption":
                        interruption_event = data.get('interruption_event', {})
                        reason = interruption_event.get('reason', 'unknown')
                        print(f"   ⚠️  Interruption: {reason}")
                        
                    elif event_type == "ping":
                        ping_event = data.get('ping_event', {})
                        event_id = ping_event.get('event_id', 0)
                        print(f"   🏓 Ping: event_id={event_id}")
                        
                    else:
                        print(f"   📋 Unknown event: {data}")
                        
                except asyncio.TimeoutError:
                    timeout_count += 1
                    print(f"⏰ Timeout {timeout_count}/{max_timeouts}")
                    
                    # Send another audio chunk to keep conversation going
                    if timeout_count % 3 == 0:  # Every 3rd timeout
                        print("📤 Sending another audio chunk...")
                        await websocket.send(json.dumps(audio_message))
                        
            print(f"🛑 Stopped after {max_timeouts} timeouts")
                    
    except websockets.exceptions.ConnectionClosed as e:
        print(f"❌ WebSocket connection closed: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    import sys
    
    agent_id = "agent_01jydy1bkeefwsmp63xbp1kn0n"
    if len(sys.argv) > 1:
        agent_id = sys.argv[1]
    
    asyncio.run(test_audio_connection(agent_id)) 