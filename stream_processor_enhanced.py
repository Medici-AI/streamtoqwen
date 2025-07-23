import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Iterator, Tuple
from collections import defaultdict
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.box import ROUNDED
from colorama import init, Fore, Back, Style

from models import MessageEvent, ConversationWindow, QuenResponse, SpeakerStream
from quen_client import QuenClient

# Initialize colorama for cross-platform colored output
init()

logger = logging.getLogger(__name__)
console = Console()


class EnhancedStreamProcessor:
    """Enhanced stream processor with parallel speaker streams and cognitive analysis."""
    
    def __init__(self, quen_client: QuenClient, debug_style: str = "rich"):
        self.quen_client = quen_client
        self.debug_style = debug_style
        
        # Separate streams for each speaker per session
        self.speaker_streams: Dict[str, Dict[str, SpeakerStream]] = defaultdict(
            lambda: {
                "customer": SpeakerStream(session_id="", speaker="customer", messages=[]),
                "rm": SpeakerStream(session_id="", speaker="rm", messages=[])
            }
        )
        
        self.window_size_seconds: float = 30.0
        
    def process_message(self, event: MessageEvent) -> None:
        """Process a single message event into the appropriate speaker stream."""
        session_id = event.session_id
        speaker = event.sender
        
        # Initialize speaker streams for this session if needed
        if session_id not in self.speaker_streams:
            self.speaker_streams[session_id] = {
                "customer": SpeakerStream(session_id=session_id, speaker="customer", messages=[]),
                "rm": SpeakerStream(session_id=session_id, speaker="rm", messages=[])
            }
        
        # Add message to the appropriate speaker stream
        self.speaker_streams[session_id][speaker].add_message(event)
        
        logger.debug(f"Added {speaker} message to session {session_id}: {event.message[:50]}...")
        
        # Check if we should emit a window for this session
        self._check_and_emit_window(session_id)
    
    def _check_and_emit_window(self, session_id: str) -> None:
        """Check if a window should be emitted for the given session."""
        customer_stream = self.speaker_streams[session_id]["customer"]
        rm_stream = self.speaker_streams[session_id]["rm"]
        
        # Get all messages from both streams
        all_messages = customer_stream.messages + rm_stream.messages
        
        if not all_messages:
            return
            
        # Get the time range of all messages in this session
        timestamps = [msg.timestamp for msg in all_messages]
        min_time = min(timestamps)
        max_time = max(timestamps)
        
        # Check if we have a complete window
        time_span = (max_time - min_time).total_seconds()
        
        if time_span >= self.window_size_seconds:
            # Emit the window
            self._emit_window(session_id, all_messages, min_time, max_time)
            
            # Clear the buffers for this session
            customer_stream.clear_messages_before(max_time)
            rm_stream.clear_messages_before(max_time)
    
    def _emit_window(self, session_id: str, messages: List[MessageEvent], 
                    window_start: datetime, window_end: datetime) -> None:
        """Emit a conversation window and send to Quen with enhanced visualization."""
        
        # Sort messages by timestamp to maintain chronological order
        sorted_messages = sorted(messages, key=lambda x: x.timestamp)
        
        # Convert messages to dict format
        message_dicts = []
        for msg in sorted_messages:
            message_dicts.append({
                'sender': msg.sender,
                'message': msg.message,
                'timestamp': msg.timestamp.isoformat()
            })
        
        # Create conversation window
        conversation_window = ConversationWindow(
            session_id=session_id,
            window_start=window_start,
            window_end=window_end,
            messages=message_dicts
        )
        
        logger.info(f"Processing window for session {session_id}: {len(messages)} messages")
        logger.info(f"Window time: {window_start.strftime('%H:%M:%S')} - {window_end.strftime('%H:%M:%S')}")
        
        # Display conversation window with enhanced visualization
        self._display_conversation_window(conversation_window)
        
        # Generate Quen response
        quen_response = self.quen_client.generate_response(conversation_window)
        
        # Display Quen response with cognitive analysis
        self._display_quen_response(quen_response)
        
        # Display final global workspace entry
        self._display_global_workspace_entry(conversation_window, quen_response)
    
    def _display_conversation_window(self, window: ConversationWindow) -> None:
        """Display the conversation window with color-coded speakers."""
        if self.debug_style == "rich":
            # Rich console output
            table = Table(title=f"🟦 Conversation Window - Session {window.session_id}", box=ROUNDED)
            table.add_column("Time", style="cyan")
            table.add_column("Speaker", style="bold")
            table.add_column("Message", style="white")
            
            for msg in window.messages:
                time_str = datetime.fromisoformat(msg['timestamp']).strftime('%H:%M:%S')
                speaker_color = "blue" if msg['sender'] == 'customer' else "green"
                speaker_icon = "👤" if msg['sender'] == 'customer' else "👨‍💼"
                
                table.add_row(
                    time_str,
                    f"{speaker_icon} {msg['sender'].title()}",
                    msg['message']
                )
            
            console.print(table)
            console.print(f"📅 Window: {window.window_start.strftime('%H:%M:%S')} - {window.window_end.strftime('%H:%M:%S')}")
        else:
            # Colorama output
            print(f"\n{Fore.CYAN}{'='*80}")
            print(f"🟦 CONVERSATION WINDOW - Session: {window.session_id}")
            print(f"📅 Window: {window.window_start.strftime('%H:%M:%S')} - {window.window_end.strftime('%H:%M:%S')}")
            print(f"{'='*80}{Style.RESET_ALL}")
            
            for msg in window.messages:
                time_str = datetime.fromisoformat(msg['timestamp']).strftime('%H:%M:%S')
                if msg['sender'] == 'customer':
                    print(f"{Fore.BLUE}👤 {time_str} Customer: {msg['message']}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.GREEN}👨‍💼 {time_str} RM: {msg['message']}{Style.RESET_ALL}")
    
    def _display_quen_response(self, response: QuenResponse) -> None:
        """Display Quen response with cognitive analysis."""
        if self.debug_style == "rich":
            # Rich console output
            console.print(Panel(
                f"[bold yellow]🤖 Quen Raw Response[/bold yellow]\n\n"
                f"[white]{response.response}[/white]",
                title="🟨 Quen Response",
                border_style="yellow"
            ))
            
            if response.analysis:
                analysis_table = Table(title="🧠 Cognitive Analysis", box=ROUNDED)
                analysis_table.add_column("Dimension", style="bold cyan")
                analysis_table.add_column("Value", style="white")
                
                analysis_table.add_row("Customer Intent", response.analysis.customer_intent)
                analysis_table.add_row("RM Strategy", response.analysis.rm_strategy)
                analysis_table.add_row("Urgency Level", response.analysis.urgency_level)
                analysis_table.add_row("Emotion", response.analysis.emotion)
                analysis_table.add_row("Next Action", response.analysis.next_action)
                
                console.print(analysis_table)
        else:
            # Colorama output
            print(f"\n{Fore.YELLOW}{'='*80}")
            print(f"🟨 QUEN RAW RESPONSE")
            print(f"{'='*80}{Style.RESET_ALL}")
            print(f"{response.response}")
            
            if response.analysis:
                print(f"\n{Fore.MAGENTA}{'='*80}")
                print(f"🧠 COGNITIVE ANALYSIS")
                print(f"{'='*80}{Style.RESET_ALL}")
                print(f"Customer Intent: {response.analysis.customer_intent}")
                print(f"RM Strategy: {response.analysis.rm_strategy}")
                print(f"Urgency Level: {response.analysis.urgency_level}")
                print(f"Emotion: {response.analysis.emotion}")
                print(f"Next Action: {response.analysis.next_action}")
    
    def _display_global_workspace_entry(self, window: ConversationWindow, response: QuenResponse) -> None:
        """Display the final global workspace entry."""
        if self.debug_style == "rich":
            # Rich console output
            content = f"""
[bold cyan]🌐 GLOBAL WORKSPACE ENTRY - Session: {window.session_id}[/bold cyan]
[cyan]📅 Window: {window.window_start.strftime('%H:%M:%S')} - {window.window_end.strftime('%H:%M:%S')}[/cyan]

[bold green]💬 Conversation Context ({len(window.messages)} messages):[/bold green]
"""
            
            for msg in window.messages:
                speaker_color = "blue" if msg['sender'] == 'customer' else "green"
                content += f"   [{speaker_color}]{msg['sender'].title()}: {msg['message']}[/{speaker_color}]\n"
            
            content += f"\n[bold yellow]🤖 Quen Response:[/bold yellow] {response.response}"
            
            if response.analysis:
                content += f"\n\n[bold magenta]🧠 Analysis:[/bold magenta]"
                content += f"\n   Intent: {response.analysis.customer_intent}"
                content += f"\n   Strategy: {response.analysis.rm_strategy}"
                content += f"\n   Urgency: {response.analysis.urgency_level}"
                content += f"\n   Emotion: {response.analysis.emotion}"
                content += f"\n   Next Action: {response.analysis.next_action}"
            
            console.print(Panel(
                content,
                title="🌐 Global Workspace Entry",
                border_style="cyan",
                box=ROUNDED
            ))
        else:
            # Colorama output
            print(f"\n{Fore.CYAN}{'='*80}")
            print(f"🌐 GLOBAL WORKSPACE ENTRY - Session: {window.session_id}")
            print(f"📅 Window: {window.window_start.strftime('%H:%M:%S')} - {window.window_end.strftime('%H:%M:%S')}")
            print(f"💬 Conversation Context ({len(window.messages)} messages):")
            
            for msg in window.messages:
                if msg['sender'] == 'customer':
                    print(f"   {Fore.BLUE}{msg['sender'].title()}: {msg['message']}{Style.RESET_ALL}")
                else:
                    print(f"   {Fore.GREEN}{msg['sender'].title()}: {msg['message']}{Style.RESET_ALL}")
            
            print(f"🤖 Quen Response: {response.response}")
            
            if response.analysis:
                print(f"🧠 Analysis: Intent={response.analysis.customer_intent}, "
                      f"Strategy={response.analysis.rm_strategy}, "
                      f"Urgency={response.analysis.urgency_level}, "
                      f"Emotion={response.analysis.emotion}, "
                      f"Next={response.analysis.next_action}")
            
            print(f"{'='*80}{Style.RESET_ALL}\n")
    
    def flush_remaining_windows(self) -> None:
        """Flush any remaining messages in buffers as final windows."""
        for session_id, streams in self.speaker_streams.items():
            customer_stream = streams["customer"]
            rm_stream = streams["rm"]
            
            all_messages = customer_stream.messages + rm_stream.messages
            
            if all_messages:
                timestamps = [msg.timestamp for msg in all_messages]
                min_time = min(timestamps)
                max_time = max(timestamps)
                self._emit_window(session_id, all_messages, min_time, max_time)
        
        # Clear all buffers
        self.speaker_streams.clear()
    
    def execute(self, input_file: str, window_size_seconds: float = 30.0, speed_factor: float = 2.0):
        """Execute the enhanced streaming pipeline."""
        self.window_size_seconds = window_size_seconds
        
        logger.info(f"Starting enhanced streaming pipeline")
        logger.info(f"Input file: {input_file}")
        logger.info(f"Window size: {window_size_seconds} seconds")
        logger.info(f"Speed factor: {speed_factor}x")
        logger.info(f"Debug style: {self.debug_style}")
        logger.info(f"KeyBy: session_id (parallel speaker streams)")
        logger.info(f"Sink: Quen model via Ollama with cognitive analysis")
        
        # Create message source
        source = EnhancedMessageSource(input_file, speed_factor)
        
        # Process messages
        message_count = 0
        for event in source.read_messages():
            message_count += 1
            
            # Process the message (simulates keyBy and parallel speaker streams)
            self.process_message(event)
            
            # Simulate real-time streaming with sleep
            time.sleep(0.5 / speed_factor)  # 500ms between messages
            
            logger.debug(f"Processed message {message_count}: {event.session_id} - {event.sender}: {event.message[:50]}...")
        
        # Flush any remaining windows
        self.flush_remaining_windows()
        
        logger.info(f"Streaming completed. Processed {message_count} messages.")


class EnhancedMessageSource:
    """Enhanced message source that reads from file and simulates streaming."""
    
    def __init__(self, file_path: str, speed_factor: float = 1.0):
        self.file_path = file_path
        self.speed_factor = speed_factor
        
    def read_messages(self) -> Iterator[MessageEvent]:
        """Read messages from file and yield them as events."""
        try:
            with open(self.file_path, 'r') as file:
                for line_num, line in enumerate(file):
                    line = line.strip()
                    if not line:
                        continue
                        
                    try:
                        # Parse JSON message
                        data = json.loads(line)
                        event = MessageEvent(
                            session_id=data['session_id'],
                            timestamp=datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00')),
                            sender=data['sender'],
                            message=data['message']
                        )
                        
                        yield event
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON on line {line_num + 1}: {e}")
                    except Exception as e:
                        logger.error(f"Error processing line {line_num + 1}: {e}")
                        
        except FileNotFoundError:
            logger.error(f"Input file not found: {self.file_path}")
        except Exception as e:
            logger.error(f"Error reading file: {e}")


 