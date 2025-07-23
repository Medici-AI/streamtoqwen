import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.layout import Layout
import colorama
from colorama import Fore, Back, Style

from models import MessageEvent, QuenResponse, CognitiveAnalysis
from quen_client import QuenClient

# Initialize colorama for cross-platform colored output
colorama.init()

@dataclass
class StreamingChunk:
    """Represents a streaming chunk of text."""
    session_id: str
    speaker: str
    content: str
    timestamp: datetime
    is_complete: bool = False
    chunk_type: str = "word"  # "character", "word", "sentence"

class TrueStreamingProcessor:
    """
    True streaming processor that simulates real-time character/word streaming.
    Maintains CUMULATIVE session buffers for proper conversation context.
    """
    
    def __init__(self, debug_style: str = "rich"):
        self.console = Console() if debug_style == "rich" else None
        self.debug_style = debug_style
        self.quen_client = QuenClient()
        
        # Streaming configuration
        self.chunk_type = "word"  # "character", "word", "sentence"
        self.chunk_delay = 0.1  # seconds between chunks
        self.window_size_seconds: float = 30.0
        
        # CUMULATIVE session buffers - maintains full conversation history
        self.session_buffers: Dict[str, List[StreamingChunk]] = {}
        self.session_last_window_end: Dict[str, datetime] = {}
        
        self.logger = logging.getLogger(__name__)
    
    def split_message_into_chunks(self, message: str, chunk_type: str = "word") -> List[str]:
        """Split a message into streaming chunks."""
        if chunk_type == "character":
            return list(message)
        elif chunk_type == "word":
            return message.split()
        elif chunk_type == "sentence":
            # Simple sentence splitting
            sentences = message.replace('!', '.').replace('?', '.').split('.')
            return [s.strip() + '.' for s in sentences if s.strip()]
        else:
            return [message]
    
    def process_streaming_message(self, event: MessageEvent) -> None:
        """Process a message by streaming it chunk by chunk."""
        session_id = event.session_id
        
        self.logger.debug(f"Processing message: {event.message[:50]}...")
        
        # Initialize session buffer if needed
        if session_id not in self.session_buffers:
            self.session_buffers[session_id] = []
            self.session_last_window_end[session_id] = event.timestamp
        
        # Split message into chunks
        chunks = self.split_message_into_chunks(event.message, self.chunk_type)
        self.logger.debug(f"Split into {len(chunks)} chunks")
        
        # Stream each chunk with delay
        for i, chunk in enumerate(chunks):
            self.logger.debug(f"Processing chunk {i+1}/{len(chunks)}: '{chunk}'")
            is_complete = (i == len(chunks) - 1)
            
            streaming_chunk = StreamingChunk(
                session_id=session_id,
                speaker=event.sender,
                content=chunk,
                timestamp=event.timestamp + timedelta(seconds=float(i * self.chunk_delay)),
                is_complete=is_complete,
                chunk_type=self.chunk_type
            )
            
            # Add to CUMULATIVE session buffer
            self.session_buffers[session_id].append(streaming_chunk)
            
            # Check if window should trigger
            self._check_window_trigger(session_id, streaming_chunk)
            
            # Simulate streaming delay
            time.sleep(self.chunk_delay)
    
    def _check_window_trigger(self, session_id: str, chunk: StreamingChunk) -> None:
        """Check if a window should trigger based on the new chunk."""
        last_window_end = self.session_last_window_end[session_id]
        window_start = last_window_end
        window_end = window_start + timedelta(seconds=self.window_size_seconds)
        
        # Check if chunk is within current window
        if chunk.timestamp >= window_end:
            # Process the window with CUMULATIVE context
            self._process_window(session_id, window_start, window_end)
            
            # Update window end for next window
            self.session_last_window_end[session_id] = window_end
    
    def _process_window(self, session_id: str, window_start: datetime, window_end: datetime) -> None:
        """Process a window with CUMULATIVE conversation context."""
        # Get ALL chunks from session buffer up to window end (CUMULATIVE)
        all_chunks = self.session_buffers[session_id]
        window_chunks = [chunk for chunk in all_chunks if chunk.timestamp <= window_end]
        
        if not window_chunks:
            return
        
        # Check if this is a complete window (no more chunks expected soon)
        latest_chunk = max(window_chunks, key=lambda x: x.timestamp)
        # Handle timezone-aware datetime comparison
        now = datetime.now(latest_chunk.timestamp.tzinfo) if latest_chunk.timestamp.tzinfo else datetime.now()
        is_complete = (now - latest_chunk.timestamp).total_seconds() > self.window_size_seconds
        
        # Build CUMULATIVE conversation context
        conversation_context = self._build_conversation_context(window_chunks)
        
        self.logger.info(f"Processing CUMULATIVE window for session {session_id}: {len(window_chunks)} total chunks")
        self.logger.info(f"Window time: {window_start.strftime('%H:%M:%S')} - {window_end.strftime('%H:%M:%S')}")
        
        # Display streaming window with CUMULATIVE content
        self._display_streaming_window(session_id, window_chunks, window_start, window_end, is_complete)
        
        # Get Quen response with FULL CUMULATIVE context
        try:
            quen_response = self.quen_client.get_response(
                session_id=session_id,
                conversation_context=conversation_context,
                is_incomplete=not is_complete
            )
            
            # Display response
            self._display_quen_response(quen_response, is_complete)
            
            # Display global workspace entry with CUMULATIVE context
            self._display_global_workspace_entry(
                session_id, window_start, window_end, 
                conversation_context, quen_response, is_complete
            )
            
        except Exception as e:
            self.logger.error(f"Error getting Quen response: {e}")
    
    def _build_conversation_context(self, chunks: List[StreamingChunk]) -> str:
        """Build CUMULATIVE conversation context from streaming chunks."""
        if not chunks:
            return ""
        
        # Group chunks by speaker and concatenate their content (CUMULATIVE)
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
    
    def _display_streaming_window(self, session_id: str, chunks: List[StreamingChunk], 
                                window_start: datetime, window_end: datetime, is_complete: bool) -> None:
        """Display the streaming window with CUMULATIVE content."""
        if self.debug_style == "rich":
            # Rich display
            table = Table(title=f"🟦 CUMULATIVE Streaming Window - Session {session_id} {'✅' if is_complete else '⏳'}")
            table.add_column("Time", style="cyan")
            table.add_column("Speaker", style="magenta")
            table.add_column("Chunk", style="white")
            table.add_column("Type", style="yellow")
            table.add_column("Complete", style="green")
            table.add_column("Cumulative", style="blue")
            
            for i, chunk in enumerate(chunks):
                speaker_icon = "👨‍💼" if chunk.speaker == "rm" else "👤"
                speaker_name = "Rm" if chunk.speaker == "rm" else "Customer"
                complete_status = "✅" if chunk.is_complete else "⏳"
                cumulative_marker = "📈" if i == len(chunks) - 1 else ""  # Mark latest chunk
                
                table.add_row(
                    chunk.timestamp.strftime('%H:%M:%S.%f')[:-3],
                    f"{speaker_icon} {speaker_name}",
                    chunk.content,
                    chunk.chunk_type,
                    complete_status,
                    cumulative_marker
                )
            
            self.console.print(table)
            self.console.print(f"📅 Window: {window_start.strftime('%H:%M:%S')} - {window_end.strftime('%H:%M:%S')}")
            self.console.print(f"📊 Total Chunks in Session: {len(chunks)} (CUMULATIVE)")
            
        else:
            # Plain text display
            print(f"{Fore.BLUE}=== CUMULATIVE Streaming Window - Session {session_id} {'(COMPLETE)' if is_complete else '(INCOMPLETE)'} ===")
            print(f"Window: {window_start.strftime('%H:%M:%S')} - {window_end.strftime('%H:%M:%S')}")
            print(f"Total Chunks in Session: {len(chunks)} (CUMULATIVE)")
            
            for chunk in chunks:
                speaker_name = "Rm" if chunk.speaker == "rm" else "Customer"
                complete_status = "✓" if chunk.is_complete else "~"
                print(f"{chunk.timestamp.strftime('%H:%M:%S.%f')[:-3]} | {speaker_name} | {chunk.content} | {chunk.chunk_type} | {complete_status}")
            print(f"{Style.RESET_ALL}")
    
    def _display_quen_response(self, response: QuenResponse, is_complete: bool) -> None:
        """Display Quen response with completion status."""
        if self.debug_style == "rich":
            panel = Panel(
                f"🎯 Quen Strategic Advice {'✅' if is_complete else '⏳'}\n\n{response.response}",
                title="🟨 Quen Strategic Advice",
                border_style="yellow"
            )
            self.console.print(panel)
            
            if response.analysis:
                self._display_cognitive_analysis_rich(response.analysis)
        else:
            print(f"{Fore.YELLOW}=== Quen Strategic Advice {'(COMPLETE)' if is_complete else '(INCOMPLETE)'} ===")
            print(response.response)
            if response.analysis:
                self._display_cognitive_analysis_plain(response.analysis)
            print(f"{Style.RESET_ALL}")
    
    def _display_cognitive_analysis_rich(self, analysis: CognitiveAnalysis) -> None:
        """Display cognitive analysis using Rich."""
        table = Table(title="🧠 Cognitive Analysis")
        table.add_column("Dimension", style="cyan")
        table.add_column("Value", style="white")
        
        table.add_row("Customer Intent", analysis.customer_intent)
        table.add_row("RM Strategy", analysis.rm_strategy)
        table.add_row("Urgency Level", analysis.urgency_level)
        table.add_row("Emotion", analysis.emotion)
        table.add_row("Next Action", analysis.next_action)
        
        self.console.print(table)
    
    def _display_cognitive_analysis_plain(self, analysis: CognitiveAnalysis) -> None:
        """Display cognitive analysis using plain text."""
        print(f"{Fore.CYAN}=== Cognitive Analysis ===")
        print(f"Customer Intent: {analysis.customer_intent}")
        print(f"RM Strategy: {analysis.rm_strategy}")
        print(f"Urgency Level: {analysis.urgency_level}")
        print(f"Emotion: {analysis.emotion}")
        print(f"Next Action: {analysis.next_action}")
        print(f"{Style.RESET_ALL}")
    
    def _display_global_workspace_entry(self, session_id: str, window_start: datetime, 
                                      window_end: datetime, conversation_context: str, 
                                      response: QuenResponse, is_complete: bool) -> None:
        """Display global workspace entry with CUMULATIVE context."""
        if self.debug_style == "rich":
            panel = Panel(
                f"🌐 GLOBAL WORKSPACE ENTRY - Session: {session_id}\n"
                f"📅 Window: {window_start.strftime('%H:%M:%S')} - {window_end.strftime('%H:%M:%S')}\n\n"
                f"💬 CUMULATIVE Conversation Context ({'COMPLETE' if is_complete else 'INCOMPLETE'}):\n{conversation_context}\n\n"
                f"🎯 Quen Strategic Advice: {response.response}\n\n"
                f"🧠 Analysis:\n"
                f"   Intent: {response.analysis.customer_intent if response.analysis else 'N/A'}\n"
                f"   Strategy: {response.analysis.rm_strategy if response.analysis else 'N/A'}\n"
                f"   Urgency: {response.analysis.urgency_level if response.analysis else 'N/A'}\n"
                f"   Emotion: {response.analysis.emotion if response.analysis else 'N/A'}\n"
                f"   Next Action: {response.analysis.next_action if response.analysis else 'N/A'}",
                title="🌐 Global Workspace Entry (CUMULATIVE)",
                border_style="blue"
            )
            self.console.print(panel)
        else:
            print(f"{Fore.BLUE}{'='*80}")
            print(f"🌐 GLOBAL WORKSPACE ENTRY - Session: {session_id}")
            print(f"📅 Window: {window_start.strftime('%H:%M:%S')} - {window_end.strftime('%H:%M:%S')}")
            print(f"💬 CUMULATIVE Conversation Context ({'COMPLETE' if is_complete else 'INCOMPLETE'}):")
            print(f"   {conversation_context}")
            print(f"🎯 Quen Strategic Advice: {response.response}")
            if response.analysis:
                print(f"🧠 Analysis:")
                print(f"   Intent: {response.analysis.customer_intent}")
                print(f"   Strategy: {response.analysis.rm_strategy}")
                print(f"   Urgency: {response.analysis.urgency_level}")
                print(f"   Emotion: {response.analysis.emotion}")
                print(f"   Next Action: {response.analysis.next_action}")
            print(f"{'='*80}{Style.RESET_ALL}")
    
    def execute(self, input_file: str, window_size_seconds: float = 30.0, 
                speed_factor: float = 2.0, chunk_type: str = "word") -> None:
        """Execute the true streaming pipeline with CUMULATIVE session buffers."""
        self.window_size_seconds = window_size_seconds
        self.chunk_type = chunk_type
        self.chunk_delay = 0.1 / speed_factor  # Adjust delay based on speed factor
        
        self.logger.info(f"Starting CUMULATIVE true streaming pipeline with {chunk_type} chunks")
        self.logger.info(f"Window size: {window_size_seconds} seconds")
        self.logger.info(f"Speed factor: {speed_factor}x")
        self.logger.info(f"Chunk delay: {self.chunk_delay} seconds")
        
        # Load messages from file
        messages = []
        with open(input_file, 'r') as f:
            for line in f:
                data = json.loads(line.strip())
                # Parse timestamp string to datetime
                if isinstance(data['timestamp'], str):
                    data['timestamp'] = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                messages.append(MessageEvent(**data))
        
        # Sort messages by timestamp
        messages.sort(key=lambda x: x.timestamp)
        
        # Process each message
        for message in messages:
            self.process_streaming_message(message)
        
        # Process any remaining windows
        for session_id in self.session_buffers:
            if self.session_buffers[session_id]:
                last_chunk = max(self.session_buffers[session_id], key=lambda x: x.timestamp)
                window_end = self.session_last_window_end[session_id] + timedelta(seconds=self.window_size_seconds)
                
                if last_chunk.timestamp < window_end:
                    self._process_window(session_id, self.session_last_window_end[session_id], window_end)
        
        self.logger.info(f"CUMULATIVE streaming completed. Processed {len(messages)} messages across {len(self.session_buffers)} sessions.") 