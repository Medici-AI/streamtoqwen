#!/usr/bin/env python3
"""
Main entry point for ElevenLabs WebSocket streaming with Multi-Agent Analysis
"""

import asyncio
import argparse
import logging
import sys
from datetime import datetime
import json

from langgraph_flow import MultiAgentFlow
from microphone_client import MicrophoneClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ElevenLabsMultiAgentProcessor:
    """Process real-time ElevenLabs conversation with multi-agent analysis."""
    
    def __init__(self, debug_style: str = "rich"):
        self.debug_style = debug_style
        self.session_buffers: dict = {}
        self.window_size_seconds = 10.0
        self.chunk_delay = 0.05
        self.chunk_type = "word"
        
        # Multi-agent flow
        self.multi_agent_flow = MultiAgentFlow()
        
        # Microphone client
        self.microphone_client = None
        
        # Performance tracking
        self.last_window_time = {}
        self.analysis_count = 0
        
    async def on_user_transcript(self, user_transcript: str):
        """Handle user transcript from ElevenLabs."""
        logger.info(f"💬 User transcript: {user_transcript}")
        
        # Create message event
        event = {
            "session_id": f"session_{datetime.now().timestamp()}",
            "timestamp": datetime.now(),
            "sender": "customer",
            "message": user_transcript
        }
        
        # Process as streaming message
        await self._process_streaming_message(event)
    
    async def on_agent_response(self, agent_response: str):
        """Handle agent response from ElevenLabs."""
        logger.info(f"🤖 Agent response: {agent_response}")
        
        # Create message event
        event = {
            "session_id": f"session_{datetime.now().timestamp()}",
            "timestamp": datetime.now(),
            "sender": "rm",
            "message": agent_response
        }
        
        # Process as streaming message
        await self._process_streaming_message(event)
    
    async def on_audio(self, audio_base64: str):
        """Handle audio response from ElevenLabs."""
        logger.info(f"🎵 Received audio chunk from ElevenLabs")
        # For now, we just log audio events
    
    async def _process_streaming_message(self, event: dict):
        """Process streaming message with chunking."""
        # Add message to session buffer
        session_id = event["session_id"]
        if session_id not in self.session_buffers:
            self.session_buffers[session_id] = []
        
        self.session_buffers[session_id].append(event)
        
        # Check if window should be processed
        if self._check_window_trigger(session_id, event["timestamp"]):
            await self._process_window(session_id, event["timestamp"])
        
        # Reduced delay for faster processing
        await asyncio.sleep(self.chunk_delay)
    
    def _check_window_trigger(self, session_id: str, current_timestamp: datetime) -> bool:
        """Check if a window should be processed."""
        if session_id not in self.session_buffers:
            return False
        
        messages = self.session_buffers[session_id]
        if not messages:
            return False
        
        # Check if enough time has passed since last window
        latest_message = messages[-1]
        now = datetime.now()
        
        time_diff = (now - latest_message["timestamp"]).total_seconds()
        
        # Also check if we have enough content for meaningful analysis
        conversation_context = self._build_conversation_context(messages)
        has_sufficient_content = len(conversation_context.strip()) > 20  # At least 20 characters
        
        return time_diff >= self.window_size_seconds and has_sufficient_content
    
    async def _process_window(self, session_id: str, window_end: datetime):
        """Process a window of messages with multi-agent analysis."""
        if session_id not in self.session_buffers:
            return
        
        # Get all messages up to the window end
        messages = self.session_buffers[session_id]
        
        # Build conversation context
        conversation_context = self._build_conversation_context(messages)
        
        if conversation_context.strip():
            # Display the window
            self._display_conversation_window(session_id, messages, window_end)
            
            # Run multi-agent analysis
            try:
                analysis_result = await asyncio.wait_for(
                    self.multi_agent_flow.execute_flow(conversation_context, session_id),
                    timeout=120.0  # 2 minute timeout for multi-agent analysis
                )
                
                # Update analysis count
                self.analysis_count += 1
                
                # Display final summary
                self._display_analysis_summary(analysis_result, window_end)
                
                # Update last window time
                self.last_window_time[session_id] = window_end
                
            except asyncio.TimeoutError:
                logger.warning("⏰ Multi-agent analysis timed out - skipping this window")
            except Exception as e:
                logger.error(f"❌ Error in multi-agent analysis: {e}")
    
    def _build_conversation_context(self, messages: list) -> str:
        """Build conversation context from messages."""
        if not messages:
            return ""

        # Group messages by speaker and concatenate their content
        speaker_messages = {}

        for message in messages:
            speaker = message["sender"]
            if speaker not in speaker_messages:
                speaker_messages[speaker] = ""

            # Add space between messages from the same speaker
            if speaker_messages[speaker] and not speaker_messages[speaker].endswith(" "):
                speaker_messages[speaker] += " "
            speaker_messages[speaker] += message["message"]

        # Build conversation context
        context_parts = []
        for speaker, message in speaker_messages.items():
            if message.strip():  # Only add non-empty messages
                context_parts.append(f"{speaker}: {message.strip()}")

        return "\n".join(context_parts)
    
    def _display_conversation_window(self, session_id: str, messages: list, window_end: datetime):
        """Display conversation window with rich formatting."""
        if self.debug_style == "rich":
            from rich.console import Console
            from rich.panel import Panel
            from rich.text import Text
            
            console = Console()
            
            # Build conversation text
            conversation_text = self._build_conversation_context(messages)
            
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
                subtitle=f"Window End: {window_end.strftime('%H:%M:%S')} | Analysis #{self.analysis_count + 1}",
                border_style="cyan"
            )
            console.print(panel)
        else:
            print(f"\n🎤 ElevenLabs Live Conversation - Session {session_id}")
            print(f"⏰ Window End: {window_end.strftime('%H:%M:%S')}")
            print(f"📊 Analysis #{self.analysis_count + 1}")
            print("=" * 60)
            print(self._build_conversation_context(messages))
            print("=" * 60)
    
    def _display_analysis_summary(self, analysis_result: dict, window_end: datetime):
        """Display analysis summary."""
        if self.debug_style == "rich":
            from rich.console import Console
            from rich.panel import Panel
            from rich.text import Text
            
            console = Console()
            
            # Create summary text
            text = Text()
            text.append(f"🎯 Multi-Agent Analysis Complete\n", style="bold green")
            text.append(f"📊 Analysis #{self.analysis_count}\n", style="green")
            text.append(f"⏰ Timestamp: {window_end.strftime('%H:%M:%S')}\n", style="green")
            
            # Add key insights from consolidation
            consolidation = analysis_result.get("consolidation", {})
            assessment = consolidation.get("overall_assessment", {})
            
            text.append(f"\n🎯 Overall Assessment:\n", style="bold")
            text.append(f"   Confidence: {assessment.get('overall_confidence', 'low')}\n", style="white")
            text.append(f"   Risk Level: {assessment.get('risk_level', 'low')}\n", style="white")
            text.append(f"   Opportunity Level: {assessment.get('opportunity_level', 'low')}\n", style="white")
            
            # Add top recommendations
            recommendations = consolidation.get("strategic_recommendations", [])
            if recommendations:
                text.append(f"\n📋 Top Recommendations:\n", style="bold")
                for i, rec in enumerate(recommendations[:3], 1):
                    text.append(f"   {i}. {rec}\n", style="white")
            
            panel = Panel(
                text,
                title="🎯 Multi-Agent Analysis Summary",
                border_style="green",
                padding=(1, 2)
            )
            console.print(panel)
        else:
            print(f"\n🎯 Multi-Agent Analysis Complete")
            print(f"📊 Analysis #{self.analysis_count}")
            print(f"⏰ Timestamp: {window_end.strftime('%H:%M:%S')}")
            
            consolidation = analysis_result.get("consolidation", {})
            assessment = consolidation.get("overall_assessment", {})
            print(f"🎯 Confidence: {assessment.get('overall_confidence', 'low')}")
            print(f"🎯 Risk Level: {assessment.get('risk_level', 'low')}")
            print(f"🎯 Opportunity Level: {assessment.get('opportunity_level', 'low')}")
    
    async def execute(self, agent_id: str, window_size_seconds: float = 10.0, chunk_type: str = "word"):
        """Execute the ElevenLabs multi-agent processor."""
        self.window_size_seconds = window_size_seconds
        self.chunk_type = chunk_type
        
        logger.info("🚀 Starting ElevenLabs Multi-Agent Processor...")
        logger.info("📝 Instructions:")
        logger.info("   1. The system will connect to ElevenLabs")
        logger.info("   2. Microphone will be activated")
        logger.info("   3. Speak naturally - 5 agents will analyze in real-time")
        logger.info("   4. Watch the console for multi-agent analysis")
        logger.info("   5. Press Ctrl+C to stop")
        logger.info(f"⚡ Multi-Agent Analysis: {window_size_seconds}s windows, {chunk_type} chunks")
        
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
                    logger.info("🤖 5 Agents ready: Intent, Strategy, Sentiment, Learning, Decision")
                    
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
            logger.info("👋 Stopping ElevenLabs multi-agent processor...")
        except Exception as e:
            logger.error(f"❌ Error in ElevenLabs multi-agent processor: {e}")
            raise
        finally:
            if self.microphone_client:
                await self.microphone_client.disconnect()

def print_banner():
    """Print application banner."""
    print("=" * 80)
    print("🎤 ElevenLabs Multi-Agent Conversational AI")
    print("=" * 80)
    print("🔗 Integrates with ElevenLabs conversational AI for live analysis")
    print("🤖 5 Specialized Agents: Intent, Strategy, Sentiment, Learning, Decision")
    print("🧠 Mem0 Consolidation for intelligent insight extraction")
    print("⏱️  Real-time multi-agent analysis with cumulative context")
    print("🎤 Live microphone input for real conversations")
    print("⚡ Optimized for speed and responsiveness")
    print("=" * 80)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="ElevenLabs Multi-Agent WebSocket Streaming with Microphone",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main_elevenlabs_microphone_multi_agent.py --agent-id agent_01jydy1bkeefwsmp63xbp1kn0n --window-size 10 --debug-style rich
  python main_elevenlabs_microphone_multi_agent.py --agent-id agent_01jydy1bkeefwsmp63xbp1kn0n --window-size 5 --debug-style colorama
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
        default=10.0,
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
    
    # Initialize multi-agent processor
    logger.info("🔧 Initializing ElevenLabs multi-agent processor...")
    processor = ElevenLabsMultiAgentProcessor(debug_style=args.debug_style)
    
    # Start processing
    try:
        # Run the async processor
        asyncio.run(processor.execute(
            agent_id=args.agent_id,
            window_size_seconds=args.window_size,
            chunk_type=args.chunk_type
        ))
    except KeyboardInterrupt:
        logger.info("👋 ElevenLabs multi-agent processor stopped")
    except Exception as e:
        logger.error(f"❌ Error in ElevenLabs multi-agent processor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 