# Flink Windowing Logic in RM Conversation Streamer

## 🔍 Overview

The application implements **Apache Flink-style windowing logic** to process streaming conversation data. This document explains both the original Flink implementation and the simplified simulation approach.

---

## 🏗️ Original Flink Implementation (`stream_processor.py`)

### **1. Flink Pipeline Architecture**

```python
# Complete Flink streaming pipeline
def create_streaming_pipeline(self, input_file: str, window_size_seconds: int = 30) -> DataStream:
    
    # 1. Create source stream
    source = MessageEventSource(input_file, speed_factor=2.0)
    stream = self.env.add_source(source, "message-source")
    
    # 2. Add watermark strategy for event time processing
    watermark_strategy = WatermarkStrategy.for_bounded_out_of_orderness(
        timedelta(seconds=5)  # 5 second out-of-order tolerance
    ).with_timestamp_assigner(
        lambda event, timestamp: event.timestamp.timestamp() * 1000
    )
    stream = stream.assign_timestamps_and_watermarks(watermark_strategy)
    
    # 3. Apply keyBy to partition by session_id
    keyed_stream = stream.key_by(lambda event: event.session_id)
    
    # 4. Apply tumbling event time window
    windowed_stream = keyed_stream.window(
        TumblingEventTimeWindows.of(Time.seconds(window_size_seconds))
    )
    
    # 5. Process windows and send to Quen
    processed_stream = windowed_stream.process(
        ConversationWindowProcessor(self.quen_client)
    )
    
    return processed_stream
```

### **2. Key Flink Concepts Implemented**

#### **🔑 KeyBy Operation**
```python
# Partition stream by session_id (equivalent to keyBy(session_id))
keyed_stream = stream.key_by(lambda event: event.session_id)
```
- **Purpose**: Groups messages by session_id for parallel processing
- **Effect**: Each session_id gets its own processing partition
- **Flink Equivalent**: `stream.keyBy(event -> event.getSessionId())`

#### **⏰ Event Time Processing**
```python
# Watermark strategy for handling out-of-order events
watermark_strategy = WatermarkStrategy.for_bounded_out_of_orderness(
    timedelta(seconds=5)  # 5 second tolerance
).with_timestamp_assigner(
    lambda event, timestamp: event.timestamp.timestamp() * 1000
)
stream = stream.assign_timestamps_and_watermarks(watermark_strategy)
```
- **Purpose**: Handles event time semantics and out-of-order events
- **Watermark**: Advances time based on event timestamps
- **Tolerance**: Allows 5-second out-of-order events

#### **🪟 Tumbling Event Time Windows**
```python
# Create tumbling windows based on event time
windowed_stream = keyed_stream.window(
    TumblingEventTimeWindows.of(Time.seconds(window_size_seconds))
)
```
- **Window Type**: Tumbling (non-overlapping, fixed-size windows)
- **Time Basis**: Event time (not processing time)
- **Size**: Configurable (default 30 seconds)
- **Flink Equivalent**: `TumblingEventTimeWindows.of(Time.seconds(30))`

#### **⚙️ Window Processing**
```python
class ConversationWindowProcessor(ProcessWindowFunction):
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
        
        # Process with Quen and emit result
        conversation_window = ConversationWindow(...)
        quen_response = self.quen_client.generate_response(conversation_window)
        return quen_response
```

---

## 🎯 Simplified Flink Simulation (`stream_processor_enhanced.py`)

### **1. Simulated KeyBy with Parallel Speaker Streams**

```python
class EnhancedStreamProcessor:
    def __init__(self, quen_client: QuenClient, debug_style: str = "rich"):
        # Separate streams for each speaker per session (simulates keyBy)
        self.speaker_streams: Dict[str, Dict[str, SpeakerStream]] = defaultdict(
            lambda: {
                "customer": SpeakerStream(session_id="", speaker="customer", messages=[]),
                "rm": SpeakerStream(session_id="", speaker="rm", messages=[])
            }
        )
        self.window_size_seconds: int = 30
```

**KeyBy Simulation:**
- **Session Partitioning**: Each `session_id` gets its own processing context
- **Speaker Separation**: Within each session, customer and RM messages are separated
- **Parallel Processing**: Messages are routed to appropriate speaker streams

### **2. Simulated Event Time Windowing**

```python
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
    
    # Check if we have a complete window (simulates tumbling window)
    time_span = (max_time - min_time).total_seconds()
    
    if time_span >= self.window_size_seconds:
        # Emit the window
        self._emit_window(session_id, all_messages, min_time, max_time)
        
        # Clear the buffers (simulates window advancement)
        customer_stream.clear_messages_before(max_time)
        rm_stream.clear_messages_before(max_time)
```

**Windowing Simulation:**
- **Event Time Basis**: Uses actual message timestamps
- **Tumbling Logic**: Fixed-size windows based on time span
- **Window Emission**: Triggers when time span reaches window size
- **Buffer Management**: Clears processed messages to simulate window advancement

### **3. Timestamp-based Message Merging**

```python
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
```

**Merging Logic:**
- **Chronological Ordering**: Messages sorted by timestamp
- **Cross-Stream Aggregation**: Combines customer and RM messages
- **Time Window Boundaries**: Defines window start/end times
- **Session Isolation**: Each session processed independently

---

## 🔄 Flink vs Simplified Comparison

| **Flink Concept** | **Original Flink Implementation** | **Simplified Simulation** |
|-------------------|-----------------------------------|---------------------------|
| **KeyBy** | `stream.key_by(lambda event: event.session_id)` | Separate `SpeakerStream` objects per session |
| **Event Time** | `WatermarkStrategy.for_bounded_out_of_orderness()` | Direct timestamp comparison |
| **Tumbling Windows** | `TumblingEventTimeWindows.of(Time.seconds(30))` | Time span calculation with threshold |
| **Window Processing** | `ProcessWindowFunction.process()` | `_emit_window()` method |
| **Watermarks** | Automatic watermark advancement | Manual buffer clearing |
| **Parallelism** | Flink-managed parallelism | Single-threaded simulation |

---

## 🎯 Windowing Logic Flow

### **1. Message Ingestion**
```
Input Message → Route to Speaker Stream → Check Window Conditions
```

### **2. Window Detection**
```
Time Span = max_timestamp - min_timestamp
IF time_span >= window_size_seconds:
    EMIT_WINDOW()
    CLEAR_BUFFERS()
```

### **3. Window Processing**
```
Collect Messages → Sort by Timestamp → Create Window → Send to Quen → Display Results
```

### **4. Buffer Management**
```
After Window Emission:
- Clear messages before max_timestamp
- Maintain messages for next window
- Reset time span calculation
```

---

## 🚀 Usage Examples

### **30-Second Tumbling Windows:**
```python
processor = EnhancedStreamProcessor(quen_client)
processor.window_size_seconds = 30  # 30-second windows
```

### **20-Second Windows with Fast Processing:**
```bash
python main.py --window-size 20 --speed-factor 10.0
```

### **60-Second Windows for Longer Conversations:**
```bash
python main.py --window-size 60 --speed-factor 2.0
```

---

## 🎯 Key Benefits of This Approach

1. **Session Isolation**: Each conversation session processed independently
2. **Event Time Semantics**: Respects actual message timestamps
3. **Parallel Speaker Streams**: Separate processing for customer and RM
4. **Configurable Windows**: Adjustable window size for different use cases
5. **Chronological Ordering**: Maintains conversation flow within windows
6. **Real-time Processing**: Simulates streaming behavior with configurable speed

---

## 🔧 Technical Implementation Notes

- **Memory Management**: Buffers are cleared after window emission to prevent memory growth
- **Timestamp Handling**: Uses Python `datetime` objects for precise time calculations
- **Error Handling**: Graceful handling of missing timestamps or malformed data
- **Performance**: Single-threaded simulation suitable for development and testing
- **Scalability**: Can be extended to multi-threaded processing for production use

---

**This implementation successfully simulates Apache Flink's windowing concepts while providing the flexibility and simplicity needed for local development and testing.** 