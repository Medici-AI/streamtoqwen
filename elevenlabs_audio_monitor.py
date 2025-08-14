#!/usr/bin/env python3
"""
ElevenLabs Audio Monitor for Multi-GPU System
Real-time audio output monitoring with system influence feedback
"""

import asyncio
import logging
import time
import json
import base64
import wave
import pyaudio
import threading
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime

import websockets
import aiohttp
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from multi_gpu_agent_system import MultiGPUAgentSystem

console = Console()
logger = logging.getLogger(__name__)

@dataclass
class AudioEvent:
    """Audio event data structure."""
    session_id: str
    timestamp: float
    audio_data: bytes
    text_content: str
    agent_response: str
    influence_level: str  # "high", "medium", "low"
    processing_time: float

class ElevenLabsAudioMonitor:
    """Real-time audio monitoring for ElevenLabs with system influence feedback."""
    
    def __init__(self, api_key: str, voice_id_rm: str = "21m00Tcm4TlvDq8ikWAM", 
                 voice_id_customer: str = "AZnzlk1XvdvUeBnXmlld"):
        self.api_key = api_key
        self.voice_id_rm = voice_id_rm
        self.voice_id_customer = voice_id_customer
        self.websocket_url = "wss://api.elevenlabs.io/v1/text-to-speech/stream-input"
        
        # Audio playback
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.chunk_size = 1024
        self.pyaudio_instance = pyaudio.PyAudio()
        
        # Multi-GPU system integration
        self.agent_system = MultiGPUAgentSystem(num_gpus=4, max_rms=3)
        self.audio_events: List[AudioEvent] = []
        
        # Real-time monitoring
        self.is_monitoring = False
        self.current_session = None
        self.audio_buffer = []
        self.influence_metrics = {}
        
    async def start_monitoring(self):
        """Start real-time audio monitoring with system influence."""
        console.print("🎵 Starting ElevenLabs Audio Monitor with Multi-GPU System")
        
        try:
            # Start multi-GPU agent system
            await self.agent_system.start()
            
            # Start audio monitoring
            self.is_monitoring = True
            await self._monitor_audio_stream()
            
        except Exception as e:
            logger.error(f"Error starting audio monitor: {e}")
            raise
    
    async def stop_monitoring(self):
        """Stop audio monitoring."""
        console.print("🛑 Stopping ElevenLabs Audio Monitor")
        self.is_monitoring = False
        await self.agent_system.stop()
        
        # Clean up audio
        if self.pyaudio_instance:
            self.pyaudio_instance.terminate()
    
    async def _monitor_audio_stream(self):
        """Monitor ElevenLabs audio stream with real-time influence feedback."""
        async with websockets.connect(self.websocket_url) as websocket:
            console.print("🔗 Connected to ElevenLabs WebSocket")
            
            # Send connection message
            connection_msg = {
                "text": "Hello, I'm ready to assist you.",
                "voice_id": self.voice_id_rm,
                "model_id": "eleven_monolingual_v1",
                "output_format": "pcm_16000"
            }
            
            await websocket.send(json.dumps(connection_msg))
            
            # Start audio playback stream
            audio_stream = self.pyaudio_instance.open(
                format=self.audio_format,
                channels=self.channels,
                rate=self.rate,
                output=True,
                frames_per_buffer=self.chunk_size
            )
            
            try:
                while self.is_monitoring:
                    # Receive audio data
                    message = await websocket.recv()
                    data = json.loads(message)
                    
                    if data.get("type") == "audio":
                        # Process audio with system influence
                        await self._process_audio_with_influence(data, audio_stream)
                    elif data.get("type") == "text":
                        # Process text input
                        await self._process_text_input(data)
                        
            except Exception as e:
                logger.error(f"Error in audio stream monitoring: {e}")
            finally:
                audio_stream.close()
    
    async def _process_audio_with_influence(self, audio_data: Dict[str, Any], audio_stream):
        """Process audio with real-time system influence feedback."""
        try:
            # Decode audio data
            audio_bytes = base64.b64decode(audio_data.get("audio", ""))
            
            # Get current session context
            session_id = audio_data.get("session_id", "default")
            text_content = audio_data.get("text", "")
            
            # Process with multi-GPU system
            start_time = time.time()
            analysis_result = await self.agent_system.process_rm_session(
                session_id, text_content
            )
            processing_time = time.time() - start_time
            
            # Determine influence level based on analysis
            influence_level = self._calculate_influence_level(analysis_result)
            
            # Create audio event
            audio_event = AudioEvent(
                session_id=session_id,
                timestamp=time.time(),
                audio_data=audio_bytes,
                text_content=text_content,
                agent_response=analysis_result.get("agent_response", ""),
                influence_level=influence_level,
                processing_time=processing_time
            )
            
            self.audio_events.append(audio_event)
            
            # Play audio with influence feedback
            await self._play_audio_with_feedback(audio_bytes, audio_stream, influence_level)
            
            # Display real-time influence metrics
            self._display_influence_metrics(audio_event)
            
        except Exception as e:
            logger.error(f"Error processing audio with influence: {e}")
    
    async def _process_text_input(self, text_data: Dict[str, Any]):
        """Process text input and generate influenced response."""
        try:
            session_id = text_data.get("session_id", "default")
            text_content = text_data.get("text", "")
            
            # Process with multi-GPU system
            analysis_result = await self.agent_system.process_rm_session(
                session_id, text_content
            )
            
            # Generate influenced response
            influenced_response = self._generate_influenced_response(analysis_result)
            
            # Send influenced response back to ElevenLabs
            response_msg = {
                "text": influenced_response,
                "voice_id": self.voice_id_rm,
                "model_id": "eleven_monolingual_v1",
                "output_format": "pcm_16000"
            }
            
            console.print(f"🤖 Influenced Response: {influenced_response}")
            
        except Exception as e:
            logger.error(f"Error processing text input: {e}")
    
    def _calculate_influence_level(self, analysis_result: Dict[str, Any]) -> str:
        """Calculate influence level based on agent analysis."""
        try:
            # Extract confidence scores from agents
            intent_confidence = analysis_result.get("intent_agent", {}).get("confidence", 0)
            sentiment_confidence = analysis_result.get("sentiment_agent", {}).get("confidence", 0)
            strategy_confidence = analysis_result.get("strategy_agent", {}).get("confidence", 0)
            
            # Calculate average confidence
            avg_confidence = (intent_confidence + sentiment_confidence + strategy_confidence) / 3
            
            if avg_confidence > 0.8:
                return "high"
            elif avg_confidence > 0.6:
                return "medium"
            else:
                return "low"
                
        except Exception as e:
            logger.error(f"Error calculating influence level: {e}")
            return "medium"
    
    async def _play_audio_with_feedback(self, audio_bytes: bytes, audio_stream, influence_level: str):
        """Play audio with visual influence feedback."""
        try:
            # Play audio
            audio_stream.write(audio_bytes)
            
            # Visual feedback based on influence level
            if influence_level == "high":
                console.print("🟢 [HIGH INFLUENCE] Audio playing with strong system influence", style="bold green")
            elif influence_level == "medium":
                console.print("🟡 [MEDIUM INFLUENCE] Audio playing with moderate system influence", style="bold yellow")
            else:
                console.print("🔴 [LOW INFLUENCE] Audio playing with minimal system influence", style="bold red")
                
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
    
    def _generate_influenced_response(self, analysis_result: Dict[str, Any]) -> str:
        """Generate response influenced by multi-GPU system analysis."""
        try:
            # Extract insights from agents
            intent_analysis = analysis_result.get("intent_agent", {})
            sentiment_analysis = analysis_result.get("sentiment_agent", {})
            strategy_analysis = analysis_result.get("strategy_agent", {})
            
            # Build influenced response
            response_parts = []
            
            # Intent-based response
            if intent_analysis.get("intent"):
                response_parts.append(f"I understand you're interested in {intent_analysis['intent']}.")
            
            # Sentiment-based response
            if sentiment_analysis.get("emotion"):
                response_parts.append(f"I sense you're feeling {sentiment_analysis['emotion']} about this.")
            
            # Strategy-based response
            if strategy_analysis.get("recommendation"):
                response_parts.append(f"Based on your situation, I recommend {strategy_analysis['recommendation']}.")
            
            # Combine response
            if response_parts:
                return " ".join(response_parts)
            else:
                return "I'm here to help you with your financial needs. How can I assist you today?"
                
        except Exception as e:
            logger.error(f"Error generating influenced response: {e}")
            return "I'm here to help you with your financial needs."
    
    def _display_influence_metrics(self, audio_event: AudioEvent):
        """Display real-time influence metrics."""
        # Create metrics table
        table = Table(title=f"🎵 Audio Influence Metrics - Session {audio_event.session_id}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")
        table.add_column("Status", style="green")
        
        table.add_row("Influence Level", audio_event.influence_level.upper(), 
                     "🟢" if audio_event.influence_level == "high" else "🟡" if audio_event.influence_level == "medium" else "🔴")
        table.add_row("Processing Time", f"{audio_event.processing_time:.2f}s", 
                     "✅" if audio_event.processing_time < 3.0 else "⚠️")
        table.add_row("Text Length", f"{len(audio_event.text_content)} chars", "✅")
        table.add_row("Audio Size", f"{len(audio_event.audio_data)} bytes", "✅")
        
        console.print(table)
        
        # Display agent response if available
        if audio_event.agent_response:
            console.print(f"🤖 Agent Response: {audio_event.agent_response}", style="italic blue")
    
    async def get_audio_statistics(self) -> Dict[str, Any]:
        """Get audio monitoring statistics."""
        if not self.audio_events:
            return {"error": "No audio events recorded"}
        
        # Calculate statistics
        total_events = len(self.audio_events)
        avg_processing_time = sum(e.processing_time for e in self.audio_events) / total_events
        
        influence_counts = {}
        for event in self.audio_events:
            influence_counts[event.influence_level] = influence_counts.get(event.influence_level, 0) + 1
        
        return {
            "total_audio_events": total_events,
            "average_processing_time": avg_processing_time,
            "influence_distribution": influence_counts,
            "total_audio_duration": sum(len(e.audio_data) for e in self.audio_events) / 16000,  # seconds
            "timestamp": time.time()
        }
    
    def print_audio_report(self):
        """Print comprehensive audio monitoring report."""
        console.print("\n" + "="*80)
        console.print("🎵 ELEVENLABS AUDIO MONITORING REPORT", style="bold cyan")
        console.print("="*80)
        
        if not self.audio_events:
            console.print("No audio events recorded.")
            return
        
        # Statistics table
        stats = asyncio.run(self.get_audio_statistics())
        
        table = Table(title="Audio Monitoring Statistics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")
        
        table.add_row("Total Audio Events", str(stats.get("total_audio_events", 0)))
        table.add_row("Average Processing Time", f"{stats.get('average_processing_time', 0):.2f}s")
        table.add_row("Total Audio Duration", f"{stats.get('total_audio_duration', 0):.1f}s")
        
        console.print(table)
        
        # Influence distribution
        influence_dist = stats.get("influence_distribution", {})
        if influence_dist:
            console.print("\n📊 Influence Level Distribution:")
            for level, count in influence_dist.items():
                percentage = (count / stats.get("total_audio_events", 1)) * 100
                console.print(f"  {level.upper()}: {count} events ({percentage:.1f}%)")
        
        console.print("\n" + "="*80)

# Example usage
async def main():
    """Example usage of ElevenLabs Audio Monitor."""
    # You'll need to provide your ElevenLabs API key
    api_key = "your_elevenlabs_api_key_here"
    
    monitor = ElevenLabsAudioMonitor(api_key=api_key)
    
    try:
        console.print("🎵 Starting ElevenLabs Audio Monitor with Multi-GPU System")
        console.print("This will allow you to hear the system's influence in real-time...")
        
        await monitor.start_monitoring()
        
        # Run for 60 seconds
        await asyncio.sleep(60)
        
    except KeyboardInterrupt:
        console.print("\n🛑 Stopping audio monitor...")
    finally:
        await monitor.stop_monitoring()
        monitor.print_audio_report()

if __name__ == "__main__":
    asyncio.run(main()) 