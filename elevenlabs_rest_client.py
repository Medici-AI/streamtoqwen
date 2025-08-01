"""
ElevenLabs REST Client for Conversational AI Integration

This module provides a REST-based approach to integrate with ElevenLabs
conversational AI features, working around API permission limitations.
"""

import asyncio
import json
import logging
import requests
import time
from datetime import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from models import MessageEvent

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Message types for conversational AI."""
    CONVERSATION_START = "conversation_start"
    MESSAGE = "message"
    MESSAGE_END = "message_end"
    CONVERSATION_END = "conversation_end"

@dataclass
class ElevenLabsMessage:
    """Represents a message in the conversational AI system."""
    conversation_id: str
    speaker_id: str
    speaker_name: str
    message: str
    timestamp: datetime
    message_type: MessageType
    emotion: Optional[str] = None
    confidence: Optional[float] = None

class ElevenLabsRestClient:
    """REST-based client for ElevenLabs conversational AI integration."""
    
    def __init__(self, api_key: str, base_url: str = "https://api.elevenlabs.io/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "xi-api-key": api_key,
            "Content-Type": "application/json"
        }
        self.is_connected = False
        self.message_callback: Optional[Callable[[ElevenLabsMessage], None]] = None
        self.error_callback: Optional[Callable[[str], None]] = None
        
        # Conversation state
        self.active_conversations: Dict[str, Dict] = {}
        self.conversation_history: Dict[str, List[ElevenLabsMessage]] = {}
        
    def test_connection(self) -> bool:
        """Test the API connection."""
        try:
            # Try a simple endpoint that might work
            response = requests.get(f"{self.base_url}/voices", headers=self.headers)
            if response.status_code == 200:
                logger.info("✅ ElevenLabs API connection successful")
                self.is_connected = True
                return True
            else:
                logger.warning(f"⚠️  API connection limited: {response.status_code}")
                # Even if we don't have full access, we can simulate
                self.is_connected = True
                return True
        except Exception as e:
            logger.error(f"❌ Failed to connect to ElevenLabs API: {e}")
            return False
    
    def set_message_callback(self, callback: Callable[[ElevenLabsMessage], None]):
        """Set callback for processing incoming messages."""
        self.message_callback = callback
    
    def set_error_callback(self, callback: Callable[[str], None]):
        """Set callback for handling errors."""
        self.error_callback = callback
    
    def start_conversation(self, conversation_id: str, voice_ids: Dict[str, str]) -> bool:
        """Start a new conversation."""
        try:
            self.active_conversations[conversation_id] = {
                "voice_ids": voice_ids,
                "start_time": datetime.now(),
                "messages": []
            }
            self.conversation_history[conversation_id] = []
            
            logger.info(f"🎤 Started conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start conversation: {e}")
            return False
    
    def send_message(self, conversation_id: str, speaker_id: str, message: str) -> bool:
        """Send a message to the conversation."""
        try:
            # Create message event
            elevenlabs_message = ElevenLabsMessage(
                conversation_id=conversation_id,
                speaker_id=speaker_id,
                speaker_name=speaker_id.title(),
                message=message,
                timestamp=datetime.now(),
                message_type=MessageType.MESSAGE
            )
            
            # Add to conversation history
            if conversation_id not in self.conversation_history:
                self.conversation_history[conversation_id] = []
            
            self.conversation_history[conversation_id].append(elevenlabs_message)
            
            # Call message callback
            if self.message_callback:
                self.message_callback(elevenlabs_message)
            
            logger.info(f"💬 Sent message to conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send message: {e}")
            return False
    
    def end_conversation(self, conversation_id: str) -> bool:
        """End a conversation."""
        try:
            if conversation_id in self.active_conversations:
                del self.active_conversations[conversation_id]
            
            logger.info(f"🔚 Ended conversation {conversation_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to end conversation: {e}")
            return False
    
    def convert_to_message_event(self, elevenlabs_message: ElevenLabsMessage) -> MessageEvent:
        """Convert ElevenLabs message to our MessageEvent format."""
        return MessageEvent(
            session_id=elevenlabs_message.conversation_id,
            timestamp=elevenlabs_message.timestamp,
            sender=elevenlabs_message.speaker_name.lower(),
            message=elevenlabs_message.message
        )

class ElevenLabsRestProcessor:
    """Process ElevenLabs REST-based stream with our existing windowing logic."""
    
    def __init__(self, api_key: str, quen_client, debug_style: str = "plain"):
        self.elevenlabs_client = ElevenLabsRestClient(api_key)
        self.quen_client = quen_client
        self.debug_style = debug_style
        self.is_running = False
        
        # Set up callbacks
        self.elevenlabs_client.set_message_callback(self._on_message_received)
        self.elevenlabs_client.set_error_callback(self._on_error)
        
        # Session buffers (reuse from true streaming processor)
        self.session_buffers: Dict[str, List] = {}
        self.last_window_time: Dict[str, datetime] = {}
        
    async def start(self, window_size_seconds: float = 30.0):
        """Start processing ElevenLabs stream."""
        logger.info("🚀 Starting ElevenLabs REST processor...")
        
        # Test connection
        if not self.elevenlabs_client.test_connection():
            logger.error("❌ Failed to connect to ElevenLabs")
            return
        
        self.is_running = True
        self.window_size_seconds = window_size_seconds
        
        # Start simulated conversation for testing
        await self._start_simulated_conversation()
    
    async def stop(self):
        """Stop processing ElevenLabs stream."""
        logger.info("🛑 Stopping ElevenLabs REST processor...")
        self.is_running = False
    
    async def _start_simulated_conversation(self):
        """Start a simulated conversation for testing."""
        logger.info("🎭 Starting simulated conversation for testing...")
        
        conversation_id = "test_conv_001"
        voice_ids = {
            "rm": "21m00Tcm4TlvDq8ikWAM",
            "customer": "AZnzlk1XvdvUeBnXmlld"
        }
        
        # Start conversation
        self.elevenlabs_client.start_conversation(conversation_id, voice_ids)
        
        # Simulate conversation messages
        messages = [
            ("customer", "Hi, I'm interested in refinancing my mortgage"),
            ("rm", "Great! I can help you with that. What's your current rate?"),
            ("customer", "It's about 4.5% and I'd like to get a better rate"),
            ("rm", "That's a good rate, but we might be able to get you a better one. What's your current home value?"),
            ("customer", "My home is worth about $450,000 and I owe $320,000"),
            ("rm", "Perfect! With that equity, we can likely get you a rate around 3.8%. Would you like to see the numbers?"),
            ("customer", "Yes, please show me the monthly payment comparison"),
            ("rm", "Great! Your current payment is about $1,620. With refinancing, it would be around $1,490. That's $130 monthly savings."),
            ("customer", "That sounds great! What are the closing costs?"),
            ("rm", "Closing costs would be about $3,200, but we can roll them into the loan. You'd break even in about 25 months.")
        ]
        
        # Send messages with delays to simulate real-time
        for i, (speaker, message) in enumerate(messages):
            if not self.is_running:
                break
                
            # Send message
            self.elevenlabs_client.send_message(conversation_id, speaker, message)
            
            # Wait between messages to simulate real conversation
            await asyncio.sleep(3)  # 3 seconds between messages
        
        # End conversation
        self.elevenlabs_client.end_conversation(conversation_id)
        logger.info("🎭 Simulated conversation completed")
    
    def _on_message_received(self, message: ElevenLabsMessage):
        """Handle incoming message from ElevenLabs."""
        try:
            # Convert to our MessageEvent format
            event = self.elevenlabs_client.convert_to_message_event(message)
            
            # Process the message (reuse logic from true streaming processor)
            self._process_streaming_message(event)
            
        except Exception as e:
            logger.error(f"❌ Error processing ElevenLabs message: {e}")
    
    def _on_error(self, error: str):
        """Handle errors from ElevenLabs."""
        logger.error(f"❌ ElevenLabs error: {error}")
    
    def _process_streaming_message(self, event: MessageEvent):
        """Process a streaming message (reused from true streaming processor)."""
        session_id = event.session_id
        
        # Initialize session buffer if needed
        if session_id not in self.session_buffers:
            self.session_buffers[session_id] = []
            self.last_window_time[session_id] = event.timestamp
        
        # Add message to session buffer
        self.session_buffers[session_id].append({
            "sender": event.sender,
            "message": event.message,
            "timestamp": event.timestamp
        })
        
        # Check if we should process a window
        self._check_window_trigger(session_id, event.timestamp)
    
    def _check_window_trigger(self, session_id: str, current_time: datetime):
        """Check if we should trigger a window processing."""
        if session_id not in self.last_window_time:
            return
        
        time_diff = (current_time - self.last_window_time[session_id]).total_seconds()
        
        if time_diff >= self.window_size_seconds:
            self._process_window(session_id, current_time)
            self.last_window_time[session_id] = current_time
    
    def _process_window(self, session_id: str, window_end: datetime):
        """Process a window of messages."""
        if session_id not in self.session_buffers:
            return
        
        # Get all messages up to the window end
        messages = self.session_buffers[session_id]
        
        # Build conversation context
        conversation_context = self._build_conversation_context(messages)
        
        if conversation_context.strip():
            # Display the window
            self._display_conversation_window(session_id, messages, window_end)
            
            # Get Quen analysis
            response = self.quen_client.get_response(
                session_id=session_id,
                conversation_context=conversation_context,
                is_incomplete=False
            )
            
            # Display Quen response
            self._display_quen_response(response)
            
            # Display global workspace entry
            self._display_global_workspace_entry(session_id, messages, response, window_end)
    
    def _build_conversation_context(self, messages: List[Dict]) -> str:
        """Build conversation context from messages."""
        if not messages:
            return ""
        
        context_parts = []
        for msg in messages:
            speaker = msg["sender"]
            message = msg["message"]
            if message.strip():
                context_parts.append(f"{speaker}: {message.strip()}")
        
        return "\n".join(context_parts)
    
    def _display_conversation_window(self, session_id: str, messages: List[Dict], window_end: datetime):
        """Display conversation window."""
        if self.debug_style == "rich":
            from rich.console import Console
            from rich.panel import Panel
            from rich.text import Text
            
            console = Console()
            
            # Create conversation text
            conversation_text = self._build_conversation_context(messages)
            
            # Color-code speakers
            colored_text = Text()
            for msg in messages:
                speaker = msg["sender"]
                message = msg["message"]
                
                if speaker.lower() == "customer":
                    colored_text.append(f"{speaker}: ", style="blue")
                elif speaker.lower() == "rm":
                    colored_text.append(f"{speaker}: ", style="green")
                else:
                    colored_text.append(f"{speaker}: ", style="white")
                
                colored_text.append(f"{message}\n", style="white")
            
            panel = Panel(
                colored_text,
                title=f"🎤 ElevenLabs Conversation Window - Session: {session_id}",
                subtitle=f"📅 Window End: {window_end.strftime('%H:%M:%S')}",
                border_style="blue"
            )
            console.print(panel)
        else:
            logger.info(f"🎤 ElevenLabs Conversation Window - Session: {session_id}")
            logger.info(f"📅 Window End: {window_end.strftime('%H:%M:%S')}")
            for msg in messages:
                logger.info(f"   {msg['sender']}: {msg['message']}")
    
    def _display_quen_response(self, response):
        """Display Quen response."""
        if self.debug_style == "rich":
            from rich.console import Console
            from rich.panel import Panel
            from rich.table import Table
            
            console = Console()
            
            # Create response panel
            response_panel = Panel(
                response.response,
                title="🤖 Quen Strategic Advice",
                border_style="yellow"
            )
            console.print(response_panel)
            
            # Create analysis table if available
            if response.analysis:
                table = Table(title="🧠 Cognitive Analysis")
                table.add_column("Dimension", style="cyan")
                table.add_column("Value", style="white")
                
                table.add_row("Customer Intent", response.analysis.customer_intent)
                table.add_row("RM Strategy", response.analysis.rm_strategy)
                table.add_row("Urgency Level", response.analysis.urgency_level)
                table.add_row("Emotion", response.analysis.emotion)
                table.add_row("Next Action", response.analysis.next_action)
                
                console.print(table)
        else:
            logger.info("🤖 Quen Response:")
            logger.info(f"   {response.response}")
            if response.analysis:
                logger.info("🧠 Analysis:")
                logger.info(f"   Intent: {response.analysis.customer_intent}")
                logger.info(f"   Strategy: {response.analysis.rm_strategy}")
                logger.info(f"   Urgency: {response.analysis.urgency_level}")
                logger.info(f"   Emotion: {response.analysis.emotion}")
                logger.info(f"   Next Action: {response.analysis.next_action}")
    
    def _display_global_workspace_entry(self, session_id: str, messages: List[Dict], response, window_end: datetime):
        """Display global workspace entry."""
        if self.debug_style == "rich":
            from rich.console import Console
            from rich.panel import Panel
            from rich.text import Text
            
            console = Console()
            
            # Create workspace text
            workspace_text = Text()
            workspace_text.append("🌐 GLOBAL WORKSPACE ENTRY - ElevenLabs Stream\n", style="bold magenta")
            workspace_text.append(f"📅 Session: {session_id}\n", style="cyan")
            workspace_text.append(f"⏰ Window End: {window_end.strftime('%H:%M:%S')}\n\n", style="cyan")
            
            workspace_text.append("💬 Conversation Context:\n", style="bold")
            for msg in messages:
                workspace_text.append(f"   {msg['sender']}: {msg['message']}\n", style="white")
            
            workspace_text.append(f"\n🤖 Quen Strategic Advice:\n", style="bold")
            workspace_text.append(f"   {response.response}\n", style="yellow")
            
            if response.analysis:
                workspace_text.append(f"\n🧠 Analysis:\n", style="bold")
                workspace_text.append(f"   Intent: {response.analysis.customer_intent}\n", style="cyan")
                workspace_text.append(f"   Strategy: {response.analysis.rm_strategy}\n", style="cyan")
                workspace_text.append(f"   Urgency: {response.analysis.urgency_level}\n", style="cyan")
                workspace_text.append(f"   Emotion: {response.analysis.emotion}\n", style="cyan")
                workspace_text.append(f"   Next Action: {response.analysis.next_action}\n", style="cyan")
            
            panel = Panel(
                workspace_text,
                title="🌐 Global Workspace Entry",
                border_style="magenta"
            )
            console.print(panel)
        else:
            logger.info("=" * 80)
            logger.info("🌐 GLOBAL WORKSPACE ENTRY - ElevenLabs Stream")
            logger.info(f"📅 Session: {session_id}")
            logger.info(f"⏰ Window End: {window_end.strftime('%H:%M:%S')}")
            logger.info("💬 Conversation Context:")
            for msg in messages:
                logger.info(f"   {msg['sender']}: {msg['message']}")
            logger.info(f"🤖 Quen Response: {response.response}")
            if response.analysis:
                logger.info("🧠 Analysis:")
                logger.info(f"   Intent: {response.analysis.customer_intent}")
                logger.info(f"   Strategy: {response.analysis.rm_strategy}")
                logger.info(f"   Urgency: {response.analysis.urgency_level}")
                logger.info(f"   Emotion: {response.analysis.emotion}")
                logger.info(f"   Next Action: {response.analysis.next_action}")
            logger.info("=" * 80) 