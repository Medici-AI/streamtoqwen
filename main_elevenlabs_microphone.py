#!/usr/bin/env python3
"""
Main entry point for ElevenLabs WebSocket streaming with microphone input
"""

import asyncio
import argparse
import logging
import sys
from datetime import datetime, timedelta
import json

from quen_client import QuenClient
from microphone_client import MicrophoneClient
from models import MessageEvent, StreamingChunk

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ElevenLabsMicrophoneProcessor:
    """Process real-time ElevenLabs conversation with microphone input."""
    
    def __init__(self, quen_client: QuenClient, debug_style: str = "rich"):
        self.quen_client = quen_client
        self.debug_style = debug_style
        self.session_buffers: dict = {}
        self.window_size_seconds = 10.0  # Reduced from 20.0
        self.chunk_delay = 0.05  # Reduced from 0.1
        self.chunk_type = "word"
        
        # Microphone client
        self.microphone_client = None
        
        # Performance tracking
        self.last_window_time = {}
        
    async def on_user_transcript(self, user_transcript: str):
        """Handle user transcript from ElevenLabs."""
        logger.info(f"💬 User transcript: {user_transcript}")
        
        # Create message event
        event = MessageEvent(
            session_id=f"session_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            sender="customer",
            message=user_transcript
        )
        
        # Process as streaming message
        await self._process_streaming_message(event)
    
    async def on_agent_response(self, agent_response: str):
        """Handle agent response from ElevenLabs."""
        logger.info(f"🤖 Agent response: {agent_response}")
        
        # Create message event
        event = MessageEvent(
            session_id=f"session_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            sender="rm",
            message=agent_response
        )
        
        # Process as streaming message
        await self._process_streaming_message(event)
    
    async def on_audio(self, audio_base64: str):
        """Handle audio response from ElevenLabs."""
        logger.info(f"🎵 Received audio chunk from ElevenLabs")
        # For now, we just log audio events
        # In a full implementation, you might want to play the audio
    
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
            
            # Reduced delay for faster processing
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
        
        # Also check if we have enough content for meaningful analysis
        conversation_context = self._build_conversation_context(chunks)
        has_sufficient_content = len(conversation_context.strip()) > 10  # At least 10 characters
        
        return time_diff >= self.window_size_seconds and has_sufficient_content
    
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
            
            # Get Quen analysis with timeout
            try:
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.quen_client.get_response,
                        session_id=session_id,
                        conversation_context=conversation_context,
                        is_incomplete=False
                    ),
                    timeout=60.0  # Increased from 30.0 to 60.0 seconds
                )
                
                # Display Quen response
                self._display_quen_response(response)
                
                # Display global workspace entry
                self._display_global_workspace_entry(session_id, chunks, response, window_end)
                
                # Update last window time
                self.last_window_time[session_id] = window_end
                
            except asyncio.TimeoutError:
                logger.warning("⏰ Quen analysis timed out - skipping this window")
            except Exception as e:
                logger.error(f"❌ Error in Quen analysis: {e}")
    
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
                title=f"🎤 ElevenLabs Live Conversation - Session {session_id}",
                subtitle=f"Window End: {window_end.strftime('%H:%M:%S')}",
                border_style="cyan"
            )
            console.print(panel)
        else:
            print(f"\n🎤 ElevenLabs Live Conversation - Session {session_id}")
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
    
    async def execute(self, agent_id: str, window_size_seconds: float = 10.0, chunk_type: str = "word"):
        """Execute the ElevenLabs microphone processor."""
        self.window_size_seconds = window_size_seconds
        self.chunk_type = chunk_type
        
        logger.info("🚀 Starting ElevenLabs microphone processor...")
        logger.info("📝 Instructions:")
        logger.info("   1. The system will connect to ElevenLabs")
        logger.info("   2. Microphone will be activated")
        logger.info("   3. Speak naturally - the system will analyze in real-time")
        logger.info("   4. Watch the console for window analysis and Quen advice")
        logger.info("   5. Press Ctrl+C to stop")
        logger.info(f"⚡ Optimized for speed: {window_size_seconds}s windows, {chunk_type} chunks")
        
        try:
            # Initialize microphone client
            self.microphone_client = MicrophoneClient(
                agent_id=agent_id,
                on_user_transcript=self.on_user_transcript,
                on_agent_response=self.on_agent_response,
                on_audio=self.on_audio
            )
            
            # Connect to ElevenLabs with timeout
            try:
                connected = await asyncio.wait_for(
                    self.microphone_client.connect_to_elevenlabs(),
                    timeout=10.0  # 10 second timeout
                )
                
                if connected:
                    logger.info("✅ Connected to ElevenLabs")
                    
                    # Start recording
                    self.microphone_client.start_recording()
                    logger.info("🎤 Microphone activated - start speaking!")
                    
                    # Keep the connection alive with timeout handling
                    while True:
                        await asyncio.sleep(1)
                        
                else:
                    logger.error("❌ Failed to connect to ElevenLabs")
                    return
                    
            except asyncio.TimeoutError:
                logger.error("⏰ Connection to ElevenLabs timed out")
                return
                
        except KeyboardInterrupt:
            logger.info("👋 Stopping ElevenLabs microphone processor...")
        except Exception as e:
            logger.error(f"❌ Error in ElevenLabs microphone processor: {e}")
            raise
        finally:
            if self.microphone_client:
                await self.microphone_client.disconnect()

def print_banner():
    """Print application banner."""
    print("=" * 80)
    print("🎤 ElevenLabs Real-time Conversational AI with Microphone")
    print("=" * 80)
    print("🔗 Integrates with ElevenLabs conversational AI for live analysis")
    print("🧠 Uses Quen LLM for strategic advice and cognitive analysis")
    print("⏱️  Real-time windowing with cumulative context")
    print("🎤 Live microphone input for real conversations")
    print("⚡ Optimized for speed and responsiveness")
    print("=" * 80)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="ElevenLabs WebSocket Streaming with Microphone and Quen Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main_elevenlabs_microphone.py --agent-id agent_01jydy1bkeefwsmp63xbp1kn0n --window-size 10 --debug-style rich
  python main_elevenlabs_microphone.py --agent-id agent_01jydy1bkeefwsmp63xbp1kn0n --window-size 5 --debug-style colorama
        """
    )
    
    parser.add_argument(
        "--agent-id",
        default="agent_01jydy1bkeefwsmp63xbp1kn0n",
        help="ElevenLabs agent ID (default: agent_01jydy1bkeefwsmp63xbp1kn0n)"
    )
    
    parser.add_argument(
        "--window-size",
        type=float,
        default=10.0,  # Reduced from 20.0
        help="Window size in seconds (default: 10.0)"
    )
    
    parser.add_argument(
        "--debug-style",
        choices=["rich", "colorama", "plain"],
        default="rich",
        help="Debug output style (default: rich)"
    )
    
    parser.add_argument(
        "--chunk-type",
        choices=["character", "word", "sentence"],
        default="word",
        help="Chunk type for streaming (default: word)"
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    print(f"🤖 Agent ID: {args.agent_id}")
    print(f"⏱️  Window Size: {args.window_size} seconds")
    print(f"🎨 Debug Style: {args.debug_style}")
    print(f"🔤 Chunk Type: {args.chunk_type}")
    print("=" * 80)
    
    # Initialize Quen client
    logger.info("🔧 Initializing Quen client...")
    quen_client = QuenClient()
    
    # Test Quen connection with timeout
    try:
        test_response = asyncio.run(asyncio.wait_for(
            asyncio.to_thread(
                quen_client.get_response,
                session_id="test",
                conversation_context="This is a test message to verify Quen is working.",
                is_incomplete=False
            ),
            timeout=60.0  # Increased from 15.0 to 60.0 seconds
        ))
        logger.info("✅ Quen model is available via Ollama")
    except asyncio.TimeoutError:
        logger.error("⏰ Quen connection timed out - please check if Ollama is running")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Failed to connect to Quen: {e}")
        sys.exit(1)
    
    # Initialize ElevenLabs microphone processor
    logger.info("🔧 Initializing ElevenLabs microphone processor...")
    processor = ElevenLabsMicrophoneProcessor(quen_client, debug_style=args.debug_style)
    
    # Start processing
    try:
        # Run the async processor
        asyncio.run(processor.execute(
            agent_id=args.agent_id,
            window_size_seconds=args.window_size,
            chunk_type=args.chunk_type
        ))
    except KeyboardInterrupt:
        logger.info("👋 ElevenLabs microphone processor stopped")
    except Exception as e:
        logger.error(f"❌ Error in ElevenLabs microphone processor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 