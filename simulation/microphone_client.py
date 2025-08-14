#!/usr/bin/env python3
"""
Microphone client for capturing audio and sending to ElevenLabs WebSocket
"""

import asyncio
import websockets
import json
import base64
import logging
import numpy as np
import pyaudio
import wave
from datetime import datetime
from typing import Optional, Callable

logger = logging.getLogger(__name__)

class MicrophoneClient:
    """Captures audio from microphone and sends to ElevenLabs WebSocket."""
    
    def __init__(self, agent_id: str, on_user_transcript: Optional[Callable] = None, 
                 on_agent_response: Optional[Callable] = None, on_audio: Optional[Callable] = None):
        self.agent_id = agent_id
        self.on_user_transcript = on_user_transcript
        self.on_agent_response = on_agent_response
        self.on_audio = on_audio
        
        # Audio configuration - optimized for speed
        self.sample_rate = 16000  # 16kHz
        self.chunk_size = 512     # Reduced from 1024 for faster processing
        self.channels = 1         # Mono
        self.format = pyaudio.paInt16
        
        # PyAudio instance
        self.pyaudio = pyaudio.PyAudio()
        self.stream = None
        self.is_recording = False
        
        # WebSocket
        self.websocket = None
        
    async def connect_to_elevenlabs(self):
        """Connect to ElevenLabs WebSocket."""
        ws_url = f"wss://api.elevenlabs.io/v1/convai/conversation?agent_id={self.agent_id}"
        
        logger.info(f"🔗 Connecting to ElevenLabs: {ws_url}")
        
        try:
            self.websocket = await websockets.connect(
                ws_url,
                ping_interval=20,
                ping_timeout=10
            )
            
            logger.info("✅ Connected to ElevenLabs WebSocket")
            
            # Send conversation initiation
            await self.websocket.send(json.dumps({
                "type": "conversation_initiation_client_data"
            }))
            
            logger.info("📤 Sent conversation initiation")
            
            # Start listening for responses
            asyncio.create_task(self._listen_for_responses())
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to connect to ElevenLabs: {e}")
            return False
    
    async def _listen_for_responses(self):
        """Listen for responses from ElevenLabs."""
        try:
            async for message in self.websocket:
                data = json.loads(message)
                event_type = data.get('type', 'unknown')
                
                logger.info(f"📨 Received: {event_type}")
                
                if event_type == "user_transcript":
                    user_transcription_event = data.get('user_transcription_event', {})
                    user_transcript = user_transcription_event.get('user_transcript', '')
                    logger.info(f"💬 User transcript: {user_transcript}")
                    
                    if self.on_user_transcript:
                        await self.on_user_transcript(user_transcript)
                        
                elif event_type == "agent_response":
                    agent_response_event = data.get('agent_response_event', {})
                    agent_response = agent_response_event.get('agent_response', '')
                    logger.info(f"🤖 Agent response: {agent_response}")
                    
                    if self.on_agent_response:
                        await self.on_agent_response(agent_response)
                        
                elif event_type == "audio":
                    audio_event = data.get('audio_event', {})
                    event_id = audio_event.get('event_id', 0)
                    audio_base64 = audio_event.get('audio_base_64', '')
                    logger.info(f"🎵 Audio chunk: event_id={event_id}")
                    
                    if self.on_audio and audio_base64:
                        await self.on_audio(audio_base64)
                        
                elif event_type == "interruption":
                    interruption_event = data.get('interruption_event', {})
                    reason = interruption_event.get('reason', 'unknown')
                    logger.warning(f"⚠️  Interruption: {reason}")
                    
                elif event_type == "ping":
                    ping_event = data.get('ping_event', {})
                    event_id = ping_event.get('event_id', 0)
                    logger.debug(f"🏓 Ping: event_id={event_id}")
                    
                else:
                    logger.info(f"📋 Unknown event: {event_type}")
                    
        except websockets.exceptions.ConnectionClosed as e:
            logger.error(f"❌ WebSocket connection closed: {e}")
        except Exception as e:
            logger.error(f"❌ Error listening for responses: {e}")
    
    def start_recording(self):
        """Start recording from microphone."""
        if self.is_recording:
            logger.warning("⚠️  Already recording")
            return
        
        try:
            self.stream = self.pyaudio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            self.is_recording = True
            logger.info("🎤 Started recording from microphone")
            
            # Start audio processing in background
            asyncio.create_task(self._process_audio())
            
        except Exception as e:
            logger.error(f"❌ Failed to start recording: {e}")
    
    def stop_recording(self):
        """Stop recording from microphone."""
        if not self.is_recording:
            return
        
        self.is_recording = False
        
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        logger.info("🛑 Stopped recording from microphone")
    
    async def _process_audio(self):
        """Process audio chunks and send to ElevenLabs."""
        while self.is_recording and self.websocket:
            try:
                # Read audio chunk
                audio_data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                
                # Convert to base64
                audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                
                # Send to ElevenLabs
                message = {
                    "user_audio_chunk": audio_base64
                }
                
                await self.websocket.send(json.dumps(message))
                
                # Reduced delay for faster processing
                await asyncio.sleep(0.05)  # Reduced from 0.1
                
            except Exception as e:
                logger.error(f"❌ Error processing audio: {e}")
                break
    
    async def disconnect(self):
        """Disconnect from ElevenLabs."""
        self.stop_recording()
        
        if self.websocket:
            await self.websocket.close()
            self.websocket = None
        
        if self.pyaudio:
            self.pyaudio.terminate()
        
        logger.info("🔌 Disconnected from ElevenLabs")
    
    def __del__(self):
        """Cleanup on destruction."""
        if hasattr(self, 'pyaudio') and self.pyaudio:
            self.pyaudio.terminate()

async def test_microphone():
    """Test microphone functionality."""
    print("🎤 Testing microphone connection...")
    
    # Test PyAudio
    try:
        p = pyaudio.PyAudio()
        
        # List available devices
        print("📋 Available audio devices:")
        for i in range(p.get_device_count()):
            device_info = p.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:  # Input device
                print(f"   {i}: {device_info['name']}")
        
        p.terminate()
        
    except Exception as e:
        print(f"❌ PyAudio error: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # Test microphone
    asyncio.run(test_microphone()) 