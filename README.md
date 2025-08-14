# RM Conversation Streamer with Flink & Quen Integration

A real-time streaming conversation analysis system that simulates Apache Flink windowing for relationship manager (RM) and customer conversations, with AI-powered strategic advice using the Quen local language model.

## 🚀 Features

- **True Streaming Processing**: Character/word-level streaming with cumulative session buffers
- **Apache Flink Simulation**: Session-based windowing with configurable window sizes (including sub-second)
- **Local AI Integration**: Quen 32B model via Ollama for strategic RM advice
- **Cognitive Analysis**: Real-time conversation analysis with intent, strategy, urgency, and emotion detection
- **Multi-Session Support**: Parallel processing of multiple conversation sessions
- **Rich Visual Output**: Color-coded terminal output with conversation windows and analysis
- **Configurable Streaming**: Adjustable speed factors and chunk types (character/word/sentence)

## 📋 Requirements

- Python 3.8+
- Ollama (for local Quen model)
- Internet connection (for initial Ollama setup)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd streamllm
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Ollama**:
   - Visit [https://ollama.ai/](https://ollama.ai/) and follow installation instructions
   - Pull the Quen model:
     ```bash
     ollama pull qwen2.5:32b
     ```

## 🎯 Usage

### Basic Usage

```bash
# Run with default settings (30-second windows, 2x speed)
python main.py

# Use custom input file
python main.py --input-file my_conversations.jsonl

# Adjust window size and speed
python main.py --window-size 60 --speed-factor 1.0
```

### Advanced Usage

```bash
# True streaming mode with word-level chunks
python main.py --streaming-mode true-streaming --chunk-type word --window-size 2.0

# Character-level streaming for maximum granularity
python main.py --streaming-mode true-streaming --chunk-type character --window-size 0.5

# Enhanced mode with rich output
python main.py --streaming-mode enhanced --debug-style rich --window-size 20
```

### Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--input-file` | Input JSONL file with conversation messages | `messages.jsonl` |
| `--window-size` | Window size in seconds (supports sub-second values) | `30.0` |
| `--speed-factor` | Speed factor for message emission | `2.0` |
| `--streaming-mode` | Streaming mode: `enhanced` or `true-streaming` | `enhanced` |
| `--chunk-type` | Chunk type for true streaming: `character`, `word`, `sentence` | `word` |
| `--debug-style` | Output style: `rich`, `colorama`, `plain` | `rich` |
| `--log-level` | Logging level | `INFO` |

## 📊 Input Format

The system expects a JSONL file with conversation messages in the following format:

```json
{"session_id": "abc123", "timestamp": "2024-01-15T14:30:00Z", "sender": "customer", "message": "Hi, I'm interested in refinancing my loan."}
{"session_id": "abc123", "timestamp": "2024-01-15T14:30:10Z", "sender": "rm", "message": "Hello! I'd be happy to help you with that."}
{"session_id": "def456", "timestamp": "2024-01-15T14:30:05Z", "sender": "customer", "message": "I need help with my investment portfolio."}
```

## 🧠 AI Analysis

The system provides real-time cognitive analysis including:

- **Customer Intent**: What the customer is trying to achieve
- **RM Strategy**: Recommended strategy for the relationship manager
- **Urgency Level**: Low/medium/high urgency assessment
- **Emotion**: Customer's emotional state
- **Next Action**: Specific next action for the RM

## 🏗️ Architecture

### Components

1. **Stream Processors**:
   - `EnhancedStreamProcessor`: Batched processing with session windows
   - `TrueStreamingProcessor`: Real-time character/word-level streaming

2. **Quen Client**: Local LLM integration via Ollama API

3. **Data Models**: Structured conversation events and analysis results

4. **Visual Output**: Rich terminal interface with color-coded sections

### Streaming Modes

#### Enhanced Mode
- Batches messages within time windows
- Processes complete conversation segments
- Suitable for analysis of conversation chunks

#### True Streaming Mode
- Processes individual characters/words in real-time
- Maintains cumulative session context
- Simulates actual streaming scenarios
- Provides strategic advice based on partial content

## 🔧 Configuration

### Window Sizes
- **Large windows (30s+)**: Complete conversation analysis
- **Medium windows (5-30s)**: Conversation segment analysis
- **Small windows (0.5-5s)**: Real-time streaming simulation
- **Sub-second windows (<1s)**: Character/word-level processing

### Speed Factors
- **1.0x**: Real-time speed
- **2.0x**: 2x faster than real-time
- **10.0x**: 10x faster for testing

## 📝 Examples

### Example 1: Real-time Streaming Analysis
```bash
python main.py --streaming-mode true-streaming --window-size 1.0 --chunk-type word --speed-factor 5.0
```

**Output**:
```
🟦 CUMULATIVE Streaming Window - Session abc123 ✅
┏━━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━┓
┃ Time         ┃ Speaker     ┃ Chunk       ┃ Type ┃ Complete ┃ Cumulative ┃
┡━━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━┩
│ 14:30:00.000 │ 👤 Customer │ Hi,         │ word │ ⏳       │            │
│ 14:30:00.010 │ 👤 Customer │ I'm         │ word │ ⏳       │            │
│ 14:30:00.020 │ 👤 Customer │ interested  │ word │ ⏳       │            │
└──────────────┴─────────────┴─────────────┴──────┴──────────┴────────────┘

🎯 Quen Strategic Advice ✅
Strategic advice to the RM: The RM should immediately acknowledge the customer's interest and gather more detailed information about their current loan situation and financial goals.

🧠 Cognitive Analysis
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Dimension       ┃ Value                                                                                                                                                                                  ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Customer Intent │ The customer is expressing an intent to potentially lower their monthly payments or improve terms of their existing loan through refinancing.                                          │
│ RM Strategy     │ The recommended strategy for the RM is to engage the customer by asking specific questions about their current loan, interest rates they're looking for, and what motivates them to    │
│                 │ consider refinancing now. This will help in providing tailored advice and solutions.                                                                                                   │
│ Urgency Level   │ medium                                                                                                                                                                                 │
│ Emotion         │ Neutral; however, there might be underlying stress or dissatisfaction with the current financial situation which could affect their emotions.                                          │
│ Next Action     │ The RM should gather detailed information about the customer's existing loan, including interest rates, monthly payments, and remaining term. This will allow for a more informed      │
│                 │ discussion on refinancing options.                                                                                                                                                     │
└─────────────────┴────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

**Copyright 2024 Emanuel Kuce Radis, IntelMe.AI**

## 🙏 Acknowledgments

- Apache Flink for streaming concepts inspiration
- Ollama for local LLM deployment
- Quen/Qwen model for AI analysis capabilities
- Rich library for beautiful terminal output

## 📞 Support

For support and questions:
- Create an issue in the repository
- Contact: Emanuel Kuce Radis (IntelMe.AI)

---

**Made with ❤️ by IntelMe.AI** 

## Local .env configuration (MVP)

For local runs, create a `.env` file at the project root (excluded from git) and set:

```
OPENAI_API_KEY=your-openai-key
OPENAI_EMBEDDING_MODEL=text-embedding-3-large
PINECONE_API_KEY=your-pinecone-key
# Optional Azure settings
AZURE_SERVICE_BUS_CONNECTION=...
AZURE_SERVICE_BUS_TOPIC=rm-events
AZURE_SERVICE_BUS_SUB=reasoner-workers
```

Start the API:

```
source .env
bash scripts/run_api.sh
```

Hit endpoints:
- POST `http://localhost:8000/ingest/event`
- POST `http://localhost:8000/ingest/flush/{session_id}`
- POST `http://localhost:8000/analyze/window`
- POST `http://localhost:8000/rm-copy/update` 