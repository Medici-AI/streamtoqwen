import json
import logging
from datetime import datetime, timedelta
from typing import Iterator, List
from pyflink.datastream import StreamExecutionEnvironment, DataStream
from pyflink.datastream.functions import SourceFunction, ProcessWindowFunction
from pyflink.datastream.window import TumblingEventTimeWindows, Time
from pyflink.common.time import Time as FlinkTime
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream.connectors.file_system import FileSource, StreamFormat

from models import MessageEvent, ConversationWindow
from quen_client import QuenClient

logger = logging.getLogger(__name__)


class MessageEventSource(SourceFunction):
    """Custom source that reads message events from a file and emits them with timestamps."""
    
    def __init__(self, file_path: str, speed_factor: float = 1.0):
        self.file_path = file_path
        self.speed_factor = speed_factor
        self.running = True
        
    def run(self, ctx):
        """Run the source function."""
        try:
            with open(self.file_path, 'r') as file:
                for line_num, line in enumerate(file):
                    if not self.running:
                        break
                        
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
                        
                        # Emit the event with timestamp
                        ctx.collect_with_timestamp(event, event.timestamp.timestamp() * 1000)
                        
                        # Simulate real-time streaming with sleep
                        import time
                        time.sleep(0.5 / self.speed_factor)  # 500ms between messages
                        
                        logger.debug(f"Emitted event: {event.session_id} - {event.sender}: {event.message[:50]}...")
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"Invalid JSON on line {line_num + 1}: {e}")
                    except Exception as e:
                        logger.error(f"Error processing line {line_num + 1}: {e}")
                        
        except FileNotFoundError:
            logger.error(f"Input file not found: {self.file_path}")
        except Exception as e:
            logger.error(f"Error reading file: {e}")
    
    def cancel(self):
        """Cancel the source function."""
        self.running = False


class ConversationWindowProcessor(ProcessWindowFunction):
    """Process window function that aggregates messages and sends to Quen."""
    
    def __init__(self, quen_client: QuenClient):
        self.quen_client = quen_client
        
    def process(self, key, context, elements):
        """Process the window of messages and generate Quen response."""
        session_id = key
        
        # Collect all messages in the window
        messages = []
        for element in elements:
            messages.append({
                'sender': element.sender,
                'message': element.message,
                'timestamp': element.timestamp.isoformat()
            })
        
        # Create conversation window
        window_start = datetime.fromtimestamp(context.window().get_start() / 1000)
        window_end = datetime.fromtimestamp(context.window().get_end() / 1000)
        
        conversation_window = ConversationWindow(
            session_id=session_id,
            window_start=window_start,
            window_end=window_end,
            messages=messages
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
            print(f"   {msg['sender'].title()}: {msg['message']}")
        print(f"🤖 Quen Response: {quen_response.response}")
        print(f"{'='*80}\n")
        
        # Return the response for potential further processing
        return quen_response


class FlinkStreamProcessor:
    """Main Flink stream processor that orchestrates the streaming pipeline."""
    
    def __init__(self, quen_client: QuenClient):
        self.quen_client = quen_client
        self.env = StreamExecutionEnvironment.get_execution_environment()
        
        # Configure local execution
        self.env.set_parallelism(1)  # Single thread for local execution
        self.env.get_config().set_auto_watermark_interval(200)  # 200ms watermark interval
        
    def create_streaming_pipeline(self, input_file: str, window_size_seconds: int = 30) -> DataStream:
        """Create the complete streaming pipeline with keyBy and windowing."""
        
        # Create source stream
        source = MessageEventSource(input_file, speed_factor=2.0)  # 2x speed for demo
        stream = self.env.add_source(source, "message-source")
        
        # Add watermark strategy for event time processing
        watermark_strategy = WatermarkStrategy.for_bounded_out_of_orderness(
            timedelta(seconds=5)  # 5 second out-of-order tolerance
        ).with_timestamp_assigner(
            lambda event, timestamp: event.timestamp.timestamp() * 1000
        )
        
        stream = stream.assign_timestamps_and_watermarks(watermark_strategy)
        
        # Apply keyBy to partition by session_id
        keyed_stream = stream.key_by(lambda event: event.session_id)
        
        # Apply tumbling event time window
        windowed_stream = keyed_stream.window(
            TumblingEventTimeWindows.of(Time.seconds(window_size_seconds))
        )
        
        # Process windows and send to Quen
        processed_stream = windowed_stream.process(
            ConversationWindowProcessor(self.quen_client)
        )
        
        return processed_stream
    
    def execute(self, input_file: str, window_size_seconds: int = 30):
        """Execute the streaming pipeline."""
        logger.info(f"Starting Flink streaming pipeline")
        logger.info(f"Input file: {input_file}")
        logger.info(f"Window size: {window_size_seconds} seconds")
        logger.info(f"KeyBy: session_id")
        logger.info(f"Sink: Quen model via Ollama")
        
        # Create and execute pipeline
        pipeline = self.create_streaming_pipeline(input_file, window_size_seconds)
        
        # Execute the job
        job_name = "RM-Conversation-Streamer"
        self.env.execute(job_name) 