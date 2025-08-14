import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Iterator
from collections import defaultdict

from models import MessageEvent, ConversationWindow
from quen_client import QuenClient

logger = logging.getLogger(__name__)


class SimpleStreamProcessor:
    """Simplified stream processor that simulates Flink behavior locally."""
    
    def __init__(self, quen_client: QuenClient):
        self.quen_client = quen_client
        self.session_buffers: Dict[str, List[MessageEvent]] = defaultdict(list)
        self.window_size_seconds: int = 30
        
    def process_message(self, event: MessageEvent) -> None:
        """Process a single message event (simulates keyBy behavior)."""
        session_id = event.session_id
        
        # Add message to session buffer (simulates keyBy)
        self.session_buffers[session_id].append(event)
        
        logger.debug(f"Added message to session {session_id}: {event.sender}: {event.message[:50]}...")
        
        # Check if we should emit a window for this session
        self._check_and_emit_window(session_id)
    
    def _check_and_emit_window(self, session_id: str) -> None:
        """Check if a window should be emitted for the given session."""
        messages = self.session_buffers[session_id]
        
        if not messages:
            return
            
        # Get the time range of messages in this session
        timestamps = [msg.timestamp for msg in messages]
        min_time = min(timestamps)
        max_time = max(timestamps)
        
        # Check if we have a complete window
        time_span = (max_time - min_time).total_seconds()
        
        if time_span >= self.window_size_seconds:
            # Emit the window
            self._emit_window(session_id, messages, min_time, max_time)
            
            # Clear the buffer for this session
            self.session_buffers[session_id] = []
    
    def _emit_window(self, session_id: str, messages: List[MessageEvent], 
                    window_start: datetime, window_end: datetime) -> None:
        """Emit a conversation window and send to Quen."""
        
        # Convert messages to dict format
        message_dicts = []
        for msg in messages:
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
        
        # Generate Quen response
        quen_response = self.quen_client.generate_response(conversation_window)
        
        # Print to console as if entering global workspace
        print(f"\n{'='*80}")
        print(f"🌐 GLOBAL WORKSPACE ENTRY - Session: {session_id}")
        print(f"📅 Window: {window_start.strftime('%H:%M:%S')} - {window_end.strftime('%H:%M:%S')}")
        print(f"💬 Conversation Context ({len(messages)} messages):")
        for msg in messages:
            print(f"   {msg.sender.title()}: {msg.message}")
        print(f"🤖 Quen Response: {quen_response.response}")
        print(f"{'='*80}\n")
    
    def flush_remaining_windows(self) -> None:
        """Flush any remaining messages in buffers as final windows."""
        for session_id, messages in self.session_buffers.items():
            if messages:
                timestamps = [msg.timestamp for msg in messages]
                min_time = min(timestamps)
                max_time = max(timestamps)
                self._emit_window(session_id, messages, min_time, max_time)
        
        # Clear all buffers
        self.session_buffers.clear()


class SimpleMessageSource:
    """Simple message source that reads from file and simulates streaming."""
    
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


class SimpleStreamProcessor:
    """Main simplified stream processor that orchestrates the streaming pipeline."""
    
    def __init__(self, quen_client: QuenClient):
        self.quen_client = quen_client
        self.session_buffers: Dict[str, List[MessageEvent]] = defaultdict(list)
        self.window_size_seconds: int = 30
        
    def execute(self, input_file: str, window_size_seconds: int = 30, speed_factor: float = 2.0):
        """Execute the simplified streaming pipeline."""
        self.window_size_seconds = window_size_seconds
        
        logger.info(f"Starting simplified streaming pipeline")
        logger.info(f"Input file: {input_file}")
        logger.info(f"Window size: {window_size_seconds} seconds")
        logger.info(f"Speed factor: {speed_factor}x")
        logger.info(f"KeyBy: session_id (simulated)")
        logger.info(f"Sink: Quen model via Ollama")
        
        # Create message source
        source = SimpleMessageSource(input_file, speed_factor)
        
        # Process messages
        message_count = 0
        for event in source.read_messages():
            message_count += 1
            
            # Process the message (simulates keyBy and windowing)
            self.process_message(event)
            
            # Simulate real-time streaming with sleep
            time.sleep(0.5 / speed_factor)  # 500ms between messages
            
            logger.debug(f"Processed message {message_count}: {event.session_id} - {event.sender}: {event.message[:50]}...")
        
        # Flush any remaining windows
        self.flush_remaining_windows()
        
        logger.info(f"Streaming completed. Processed {message_count} messages.")
    
    def process_message(self, event: MessageEvent) -> None:
        """Process a single message event (simulates keyBy behavior)."""
        session_id = event.session_id
        
        # Add message to session buffer (simulates keyBy)
        self.session_buffers[session_id].append(event)
        
        logger.debug(f"Added message to session {session_id}: {event.sender}: {event.message[:50]}...")
        
        # Check if we should emit a window for this session
        self._check_and_emit_window(session_id)
    
    def _check_and_emit_window(self, session_id: str) -> None:
        """Check if a window should be emitted for the given session."""
        messages = self.session_buffers[session_id]
        
        if not messages:
            return
            
        # Get the time range of messages in this session
        timestamps = [msg.timestamp for msg in messages]
        min_time = min(timestamps)
        max_time = max(timestamps)
        
        # Check if we have a complete window
        time_span = (max_time - min_time).total_seconds()
        
        if time_span >= self.window_size_seconds:
            # Emit the window
            self._emit_window(session_id, messages, min_time, max_time)
            
            # Clear the buffer for this session
            self.session_buffers[session_id] = []
    
    def _emit_window(self, session_id: str, messages: List[MessageEvent], 
                    window_start: datetime, window_end: datetime) -> None:
        """Emit a conversation window and send to Quen."""
        
        # Convert messages to dict format
        message_dicts = []
        for msg in messages:
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
        
        # Generate Quen response
        quen_response = self.quen_client.generate_response(conversation_window)
        
        # Print to console as if entering global workspace
        print(f"\n{'='*80}")
        print(f"🌐 GLOBAL WORKSPACE ENTRY - Session: {session_id}")
        print(f"📅 Window: {window_start.strftime('%H:%M:%S')} - {window_end.strftime('%H:%M:%S')}")
        print(f"💬 Conversation Context ({len(messages)} messages):")
        for msg in messages:
            print(f"   {msg.sender.title()}: {msg.message}")
        print(f"🤖 Quen Response: {quen_response.response}")
        print(f"{'='*80}\n")
    
    def flush_remaining_windows(self) -> None:
        """Flush any remaining messages in buffers as final windows."""
        for session_id, messages in self.session_buffers.items():
            if messages:
                timestamps = [msg.timestamp for msg in messages]
                min_time = min(timestamps)
                max_time = max(timestamps)
                self._emit_window(session_id, messages, min_time, max_time)
        
        # Clear all buffers
        self.session_buffers.clear() 