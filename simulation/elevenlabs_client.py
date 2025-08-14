#!/usr/bin/env python3
"""
ElevenLabs WebSocket Client for Real-time Conversational AI
"""

import asyncio
import json
import logging
import websockets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass

from models import MessageEvent, StreamingChunk
from quen_client import QuenClient

logger = logging.getLogger(__name__)

@dataclass
class ElevenLabsMessage:
    """ElevenLabs message structure."""
    session_id: str
    timestamp: datetime
    sender: str
    message: str
    agent_id: str

class ElevenLabsStreamProcessor:
    """Process real-time ElevenLabs conversational AI stream."""
    
    def __init__(self, quen_client: QuenClient, debug_style: str = "rich"):
        self.quen_client = quen_client
        self.debug_style = debug_style
        self.session_buffers: Dict[str, list] = {}
        self.window_size_seconds = 20.0
        self.chunk_delay = 0.1
        self.chunk_type = "word"
        
        # ElevenLabs configuration
        self.agent_id = "agent_01jydy1bkeefwsmp63xbp1kn0n"
        
    async def connect_to_stream(self, api_key: str):
        """Connect to ElevenLabs WebSocket stream using the correct endpoint."""
        # Use the correct WebSocket URL from the documentation
        ws_url = f"wss://api.elevenlabs.io/v1/convai/conversation?agent_id={self.agent_id}"
        
        logger.info(f"🔗 Connecting to ElevenLabs WebSocket: {ws_url}")
        logger.info(f"🤖 Agent ID: {self.agent_id}")
        
        try:
            async with websockets.connect(
                ws_url,
                ping_interval=20,
                ping_timeout=10
            ) as websocket:
                logger.info("✅ Connected to ElevenLabs WebSocket")
                
                # Send conversation initiation message
                await websocket.send(json.dumps({
                    "type": "conversation_initiation_client_data"
                }))
                
                # Listen for messages
                async for message in websocket:
                    await self._process_elevenlabs_message(message)
                    
        except websockets.exceptions.ConnectionClosed as e:
            logger.error(f"❌ WebSocket connection closed: {e}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to ElevenLabs: {e}")
            raise
    
    async def _process_elevenlabs_message(self, message_data: str):
        """Process incoming ElevenLabs message based on the documented event types."""
        try:
            data = json.loads(message_data)
            event_type = data.get('type', 'unknown')
            logger.info(f"📨 Received ElevenLabs message: {event_type}")
            
            if event_type == "user_transcript":
                # Handle user transcript event
                user_transcription_event = data.get('user_transcription_event', {})
                user_transcript = user_transcription_event.get('user_transcript', '')
                
                if user_transcript:
                    # Create message event for user transcript
                    event = MessageEvent(
                        session_id=f"session_{datetime.now().timestamp()}",
                        timestamp=datetime.now(),
                        sender="customer",
                        message=user_transcript
                    )
                    
                    # Process as streaming message
                    await self._process_streaming_message(event)
                    
            elif event_type == "agent_response":
                # Handle agent response event
                agent_response_event = data.get('agent_response_event', {})
                agent_response = agent_response_event.get('agent_response', '')
                
                if agent_response:
                    # Create message event for agent response
                    event = MessageEvent(
                        session_id=f"session_{datetime.now().timestamp()}",
                        timestamp=datetime.now(),
                        sender="rm",
                        message=agent_response
                    )
                    
                    # Process as streaming message
                    await self._process_streaming_message(event)
                    
            elif event_type == "audio":
                # Handle audio event (we can log this but don't process for text analysis)
                audio_event = data.get('audio_event', {})
                event_id = audio_event.get('event_id', 0)
                logger.info(f"🎵 Received audio chunk: event_id={event_id}")
                
            elif event_type == "interruption":
                # Handle interruption event
                interruption_event = data.get('interruption_event', {})
                reason = interruption_event.get('reason', 'unknown')
                logger.info(f"⚠️  Interruption: {reason}")
                
            elif event_type == "ping":
                # Handle ping event to keep connection alive
                ping_event = data.get('ping_event', {})
                event_id = ping_event.get('event_id', 0)
                ping_ms = ping_event.get('ping_ms', 0)
                
                # Send pong response
                logger.info(f"🏓 Received ping: event_id={event_id}, ping_ms={ping_ms}")
                
            else:
                logger.info(f"📨 Unknown event type: {event_type}")
                
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse message: {e}")
        except Exception as e:
            logger.error(f"❌ Error processing message: {e}")
    
    async def _process_streaming_message(self, event: MessageEvent):
        """Process streaming message with chunking."""
        # Split message into chunks
        chunks = self._split_message_into_chunks(event)
        
        for i, chunk in enumerate(chunks):
            # Add chunk to session buffer
            if event.session_id not in self.session_buffers:
                self.session_buffers[event.session_id] = []
            
            self.session_buffers[event.session_id].append(chunk)
            
            # Check if window should be processed
            if self._check_window_trigger(event.session_id, chunk.timestamp):
                await self._process_window(event.session_id, chunk.timestamp)
            
            # Simulate streaming delay
            await asyncio.sleep(self.chunk_delay)
    
    def _split_message_into_chunks(self, event: MessageEvent) -> list:
        """Split message into streaming chunks."""
        chunks = []
        content = event.message
        
        if self.chunk_type == "character":
            for i, char in enumerate(content):
                chunk = StreamingChunk(
                    session_id=event.session_id,
                    speaker=event.sender,
                    content=char,
                    chunk_type="character",
                    timestamp=event.timestamp + timedelta(seconds=float(i * self.chunk_delay))
                )
                chunks.append(chunk)
                
        elif self.chunk_type == "word":
            words = content.split()
            for i, word in enumerate(words):
                chunk = StreamingChunk(
                    session_id=event.session_id,
                    speaker=event.sender,
                    content=word,
                    chunk_type="word",
                    timestamp=event.timestamp + timedelta(seconds=float(i * self.chunk_delay))
                )
                chunks.append(chunk)
                
        else:  # sentence
            sentences = content.split('.')
            for i, sentence in enumerate(sentences):
                if sentence.strip():
                    chunk = StreamingChunk(
                        session_id=event.session_id,
                        speaker=event.sender,
                        content=sentence.strip() + ".",
                        chunk_type="sentence",
                        timestamp=event.timestamp + timedelta(seconds=float(i * self.chunk_delay))
                    )
                    chunks.append(chunk)
        
        return chunks
    
    def _check_window_trigger(self, session_id: str, current_timestamp: datetime) -> bool:
        """Check if a window should be processed."""
        if session_id not in self.session_buffers:
            return False
        
        chunks = self.session_buffers[session_id]
        if not chunks:
            return False
        
        # Check if enough time has passed since last window
        latest_chunk = chunks[-1]
        now = datetime.now(latest_chunk.timestamp.tzinfo) if latest_chunk.timestamp.tzinfo else datetime.now()
        
        time_diff = (now - latest_chunk.timestamp).total_seconds()
        return time_diff >= self.window_size_seconds
    
    async def _process_window(self, session_id: str, window_end: datetime):
        """Process a window of messages."""
        if session_id not in self.session_buffers:
            return
        
        # Get all messages up to the window end
        chunks = self.session_buffers[session_id]
        
        # Build conversation context
        conversation_context = self._build_conversation_context(chunks)
        
        if conversation_context.strip():
            # Display the window
            self._display_conversation_window(session_id, chunks, window_end)
            
            # Get Quen analysis
            response = self.quen_client.get_response(
                session_id=session_id,
                conversation_context=conversation_context,
                is_incomplete=False
            )
            
            # Display Quen response
            self._display_quen_response(response)
            
            # Display global workspace entry
            self._display_global_workspace_entry(session_id, chunks, response, window_end)
    
    def _build_conversation_context(self, chunks: list) -> str:
        """Build conversation context from streaming chunks."""
        if not chunks:
            return ""

        # Group chunks by speaker and concatenate their content
        speaker_messages = {}

        for chunk in chunks:
            if chunk.speaker not in speaker_messages:
                speaker_messages[chunk.speaker] = ""

            # Concatenate content based on chunk type
            if chunk.chunk_type == "character":
                speaker_messages[chunk.speaker] += str(chunk.content)
            else:
                # For word/sentence chunks, add space between chunks
                if speaker_messages[chunk.speaker] and not speaker_messages[chunk.speaker].endswith(" "):
                    speaker_messages[chunk.speaker] += " "
                speaker_messages[chunk.speaker] += str(chunk.content)

        # Build conversation context
        context_parts = []
        for speaker, message in speaker_messages.items():
            if message.strip():  # Only add non-empty messages
                context_parts.append(f"{speaker}: {message.strip()}")

        return "\n".join(context_parts)
    
    def _display_conversation_window(self, session_id: str, chunks: list, window_end: datetime):
        """Display conversation window with rich formatting."""
        if self.debug_style == "rich":
            from rich.console import Console
            from rich.panel import Panel
            from rich.text import Text
            
            console = Console()
            
            # Build conversation text
            conversation_text = self._build_conversation_context(chunks)
            
            # Create colored text
            text = Text()
            lines = conversation_text.split('\n')
            for line in lines:
                if line.startswith('customer:'):
                    text.append(line + '\n', style="blue")
                elif line.startswith('rm:'):
                    text.append(line + '\n', style="green")
                else:
                    text.append(line + '\n')
            
            panel = Panel(
                text,
                title=f"🎤 ElevenLabs Conversation Window - Session {session_id}",
                subtitle=f"Window End: {window_end.strftime('%H:%M:%S')}",
                border_style="cyan"
            )
            console.print(panel)
        else:
            print(f"\n🎤 ElevenLabs Conversation Window - Session {session_id}")
            print(f"⏰ Window End: {window_end.strftime('%H:%M:%S')}")
            print("=" * 60)
            print(self._build_conversation_context(chunks))
            print("=" * 60)
    
    def _display_quen_response(self, response):
        """Display Quen response with rich formatting."""
        if self.debug_style == "rich":
            from rich.console import Console
            from rich.panel import Panel
            from rich.json import JSON
            
            console = Console()
            
            # Display strategic advice
            advice_panel = Panel(
                response.response,
                title="🤖 Quen Strategic Advice",
                border_style="yellow"
            )
            console.print(advice_panel)
            
            # Display cognitive analysis
            if response.analysis:
                analysis_json = JSON(json.dumps(response.analysis.__dict__, indent=2))
                analysis_panel = Panel(
                    analysis_json,
                    title="🧠 Cognitive Analysis",
                    border_style="magenta"
                )
                console.print(analysis_panel)
        else:
            print(f"\n🤖 Quen Strategic Advice:")
            print(f"💬 {response.response}")
            if response.analysis:
                print(f"\n🧠 Cognitive Analysis:")
                print(f"   Customer Intent: {response.analysis.customer_intent}")
                print(f"   RM Strategy: {response.analysis.rm_strategy}")
                print(f"   Urgency Level: {response.analysis.urgency_level}")
                print(f"   Emotion: {response.analysis.emotion}")
                print(f"   Next Action: {response.analysis.next_action}")
    
    def _display_global_workspace_entry(self, session_id: str, chunks: list, response, window_end: datetime):
        """Display global workspace entry."""
        if self.debug_style == "rich":
            from rich.console import Console
            from rich.panel import Panel
            from rich.text import Text
            
            console = Console()
            
            # Build workspace entry
            workspace_text = Text()
            workspace_text.append("🌐 Global Workspace Entry\n", style="bold cyan")
            workspace_text.append(f"Session: {session_id}\n", style="cyan")
            workspace_text.append(f"Timestamp: {window_end.strftime('%Y-%m-%d %H:%M:%S')}\n", style="cyan")
            workspace_text.append(f"Advice: {response.response}\n", style="yellow")
            
            if response.analysis:
                workspace_text.append(f"Analysis: {response.analysis.customer_intent} | {response.analysis.rm_strategy}\n", style="magenta")
            
            panel = Panel(
                workspace_text,
                title="🌐 Global Workspace",
                border_style="cyan",
                padding=(1, 2)
            )
            console.print(panel)
        else:
            print(f"\n🌐 Global Workspace Entry")
            print(f"Session: {session_id}")
            print(f"Timestamp: {window_end.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Advice: {response.response}")
            if response.analysis:
                print(f"Analysis: {response.analysis.customer_intent} | {response.analysis.rm_strategy}")
    
    async def execute(self, api_key: str, window_size_seconds: float = 20.0, chunk_type: str = "word"):
        """Execute the ElevenLabs stream processor."""
        self.window_size_seconds = window_size_seconds
        self.chunk_type = chunk_type
        
        logger.info("🚀 Starting ElevenLabs stream processor...")
        logger.info("📝 Instructions:")
        logger.info("   1. The system will connect to ElevenLabs")
        logger.info("   2. Start a conversation in ElevenLabs")
        logger.info("   3. Speak naturally - the system will analyze in real-time")
        logger.info("   4. Watch the console for window analysis and Quen advice")
        logger.info("   5. Press Ctrl+C to stop")
        
        try:
            await self.connect_to_stream(api_key)
        except KeyboardInterrupt:
            logger.info("👋 ElevenLabs stream processor stopped")
        except Exception as e:
            logger.error(f"❌ Error in ElevenLabs stream processor: {e}")
            raise 