# RM Conversation Streamer with Flink & Quen Integration

A lightweight, local-only Python application that simulates streaming conversations between relationship managers (RMs) and customers through Apache Flink-like processing, applies session-based windowing logic, and generates AI responses using a local Quen 32B model via Ollama.

## 🎯 Key Features

- **Local-only operation** - No cloud services or distributed clusters required
- **Session-based streaming** - Simulates Flink's `keyBy(session_id)` for concurrent conversation handling
- **Event-time windowing** - Tumbling windows aggregate conversation context
- **Quen AI integration** - Local Quen 32B model responses via Ollama
- **Real-time simulation** - Configurable speed factors for prototyping
- **Global workspace output** - Console output simulates agentic memory entries
- **Simplified architecture** - Works without complex Flink setup

## 🏗️ Architecture

```
messages.jsonl → Simple Stream Processor → keyBy(session_id) → Tumbling Windows → Quen Model → Console Output
```

### Components

- **`main.py`** - Entry point and orchestration
- **`stream_processor_simple.py`** - Simplified streaming logic with session-based windowing
- **`quen_client.py`** - Communication with local Quen model via Ollama
- **`models.py`** - Data classes for events and responses
- **`messages.jsonl`** - Sample conversation data with interleaved sessions
- **`test_app.py`** - Component testing script

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+**
2. **Ollama** (optional, for real Quen responses)
   ```bash
   # Install Ollama
   curl -fsSL https://ollama.ai/install.sh | sh
   
   # Pull Quen model
   ollama pull quen:32b
   
   # Start Ollama service
   ollama serve
   ```

### Installation

1. **Clone and setup**
   ```bash
   git clone <repository>
   cd streamllm
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

2. **Run the application**
   ```bash
   python main.py
   ```

### Usage Examples

```bash
# Basic usage with defaults
python main.py

# Custom input file
python main.py --input-file my_conversations.jsonl

# 60-second windows, real-time speed
python main.py --window-size 60 --speed-factor 1.0

# Fast demo mode
python main.py --speed-factor 10.0 --window-size 15

# Debug logging
python main.py --log-level DEBUG
```

## 📊 Input Format

The application reads JSONL files with conversation messages:

```json
{"session_id": "abc123", "timestamp": "2025-01-23T14:30:00Z", "sender": "customer", "message": "Hi, I'm interested in refinancing my loan."}
{"session_id": "def456", "timestamp": "2025-01-23T14:30:05Z", "sender": "customer", "message": "I need help with my investment portfolio."}
```

### Fields

- `session_id` - Unique identifier for conversation session
- `timestamp` - ISO 8601 timestamp
- `sender` - Either "customer" or "rm"
- `message` - The conversation message

## 🔄 Stream Processing

### KeyBy Logic (Simulated)

```python
# Partition stream by session_id to handle concurrent conversations
session_buffers[session_id].append(event)
```

### Windowing Strategy

- **Tumbling Event Time Windows** - 30-second windows by default
- **Session-based Buffering** - Messages grouped by session_id
- **Time-based Emission** - Windows emitted when time span exceeds threshold

### Window Output

Each window produces a `ConversationWindow` object:

```python
@dataclass
class ConversationWindow:
    session_id: str
    window_start: datetime
    window_end: datetime
    messages: List[dict]
```

## 🧠 Quen Integration

### Prompt Format

The application constructs prompts for Quen like:

```
The following is a conversation between a Relationship Manager and a Customer:

Customer: Hi, I'm interested in refinancing my loan.
RM: Hello! I'd be happy to help you with refinancing. What's your current loan situation?
Customer: I have a 30-year fixed mortgage at 4.5% interest rate.

Based on the above window of conversation, what should the RM say next? Please provide a natural, helpful response that continues the conversation appropriately.
```

### Fallback Behavior

If Quen is unavailable, the application uses mock responses to ensure continuous operation.

## 📝 Output Format

The application prints to console in a "global workspace" format:

```
================================================================================
🌐 GLOBAL WORKSPACE ENTRY - Session: abc123
📅 Window: 14:30:00 - 14:30:30
💬 Conversation Context (3 messages):
   Customer: Hi, I'm interested in refinancing my loan.
   RM: Hello! I'd be happy to help you with refinancing. What's your current loan situation?
   Customer: I have a 30-year fixed mortgage at 4.5% interest rate.
🤖 Quen Response: That's a good rate, but we might be able to get you a better one. What's your current home value?
================================================================================
```

## 🔧 Configuration

### Command Line Options

- `--input-file` - Input JSONL file (default: `messages.jsonl`)
- `--window-size` - Window size in seconds (default: 30)
- `--speed-factor` - Message emission speed multiplier (default: 2.0)
- `--log-level` - Logging level (default: INFO)

### Environment Variables

- `OLLAMA_BASE_URL` - Ollama API base URL (default: `http://localhost:11434`)
- `QUEN_MODEL_NAME` - Quen model name (default: `quen:32b`)

## 🐛 Troubleshooting

### Common Issues

1. **"Quen model not available"**
   - Install Ollama and pull the Quen model
   - Or use mock responses (automatic fallback)

2. **"Input file not found"**
   - Ensure `messages.jsonl` exists in the current directory
   - Or specify a custom file with `--input-file`

3. **Import errors**
   - Ensure virtual environment is activated: `source venv/bin/activate`
   - Install dependencies: `pip install -r requirements.txt`

### Logs

- Application logs are written to `streamllm.log`
- Console output shows real-time streaming progress
- Use `--log-level DEBUG` for detailed interaction logs

## 🧪 Testing

### Component Tests

```bash
# Test individual components
python test_app.py
```

### Sample Data

The included `messages.jsonl` contains:
- 2 concurrent conversation sessions (`abc123`, `def456`)
- 28 total messages over ~2 minutes
- Interleaved messages to demonstrate `keyBy` behavior

### Expected Output

With 30-second windows, you should see:
- 2-3 window outputs per session
- Quen responses for each window
- Proper session separation via `keyBy`

## 🔮 Future Enhancements

- **Full Flink Integration** - Switch to actual Apache Flink when needed
- **Multiple window types** - Sliding, session windows
- **Advanced watermarking** - Custom watermark strategies
- **Stateful processing** - Conversation history tracking
- **Multiple LLM support** - Integration with other local models
- **Web UI** - Real-time visualization of streaming
- **Metrics collection** - Performance and accuracy metrics

## 📄 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

**Built for prototyping agentic memory and interaction loops with local-only constraints.** 