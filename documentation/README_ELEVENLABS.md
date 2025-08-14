# 🎤 ElevenLabs Real-time Conversational AI Streamer

This module integrates with **ElevenLabs conversational AI** to provide real-time streaming analysis using our existing windowing logic and Quen LLM integration.

## 🚀 **Features**

- **Real-time Audio Streaming**: Direct integration with ElevenLabs conversational AI
- **Live Analysis**: Real-time windowing and cognitive analysis as conversations happen
- **Voice Diversity**: Different voice profiles for RM and Customer
- **Cumulative Context**: Maintains full conversation history for better analysis
- **Strategic Advice**: Quen LLM provides real-time strategic guidance to RMs
- **Rich Debug Output**: Color-coded console output with conversation windows

## 📋 **Prerequisites**

### 1. **ElevenLabs Account**
- Sign up at [ElevenLabs](https://elevenlabs.io)
- Get your API key from the dashboard
- Set up voice profiles for RM and Customer

### 2. **Ollama with Quen Model**
```bash
# Install Quen model
ollama pull qwen2.5:32b

# Start Ollama server
ollama serve
```

### 3. **Python Environment**
```bash
# Install dependencies
pip install -r requirements.txt
```

## 🔧 **Setup**

### 1. **Get ElevenLabs API Key**
1. Go to [ElevenLabs Dashboard](https://elevenlabs.io/app)
2. Navigate to Profile Settings
3. Copy your API key

### 2. **Configure Voice IDs**
You can use default voice IDs or create custom ones:

**Default Voices:**
- RM: `21m00Tcm4TlvDq8ikWAM` (Rachel - Professional)
- Customer: `AZnzlk1XvdvUeBnXmlld` (Domi - Friendly)

**Custom Voices:**
1. Go to ElevenLabs Voice Library
2. Create or select voice profiles
3. Copy the voice IDs

### 3. **Test Connection**
```bash
# Test with your API key
python main_elevenlabs.py --api-key YOUR_API_KEY --window-size 20
```

## 🎯 **Usage**

### **Basic Usage**
```bash
python main_elevenlabs.py --api-key YOUR_API_KEY
```

### **Advanced Configuration**
```bash
python main_elevenlabs.py \
    --api-key YOUR_API_KEY \
    --window-size 30.0 \
    --debug-style rich \
    --voice-rm 21m00Tcm4TlvDq8ikWAM \
    --voice-customer AZnzlk1XvdvUeBnXmlld
```

### **Parameters**

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--api-key` | ElevenLabs API key | Required |
| `--window-size` | Analysis window in seconds | 30.0 |
| `--debug-style` | Output style (rich/colorama/plain) | rich |
| `--voice-rm` | Voice ID for Relationship Manager | 21m00Tcm4TlvDq8ikWAM |
| `--voice-customer` | Voice ID for Customer | AZnzlk1XvdvUeBnXmlld |

## 🔄 **How It Works**

### **1. Connection Flow**
```
ElevenLabs WebSocket → Our Processor → Quen Analysis → Console Output
```

### **2. Real-time Processing**
1. **Connect** to ElevenLabs WebSocket stream
2. **Receive** real-time conversation messages
3. **Buffer** messages by session ID
4. **Window** messages based on time intervals
5. **Analyze** with Quen LLM for strategic advice
6. **Display** results in real-time

### **3. Message Flow**
```
ElevenLabs Message → MessageEvent → Session Buffer → Window Processing → Quen Analysis → Strategic Advice
```

## 📊 **Output Examples**

### **Conversation Window**
```
🎤 ElevenLabs Conversation Window - Session: conv_123
📅 Window End: 14:30:45
   Customer: Hi, I'm interested in refinancing my mortgage
   RM: Great! I can help you with that. What's your current rate?
   Customer: It's about 4.5% and I'd like to get a better rate
```

### **Quen Strategic Advice**
```
🤖 Quen Strategic Advice:
   The customer is clearly interested in refinancing and has done some research. 
   Focus on gathering their current loan details and explaining the refinancing process.
```

### **Cognitive Analysis**
```
🧠 Cognitive Analysis:
   Customer Intent: Refinancing inquiry with rate improvement goal
   RM Strategy: Educate and gather information
   Urgency Level: medium
   Emotion: positive
   Next Action: Request current loan details
```

## 🎤 **ElevenLabs Integration Details**

### **WebSocket Connection**
- **URL**: `wss://api.elevenlabs.io/v1/stream`
- **Authentication**: Bearer token with API key
- **Protocol**: Real-time bidirectional communication

### **Message Types**
- `conversation_start`: Initialize new conversation
- `message`: Real-time conversation message
- `message_end`: End of current message
- `conversation_end`: End conversation session

### **Voice Configuration**
```python
voice_ids = {
    "rm": "21m00Tcm4TlvDq8ikWAM",      # Professional RM voice
    "customer": "AZnzlk1XvdvUeBnXmlld"  # Friendly customer voice
}
```

## 🔍 **Debugging**

### **Log Files**
- `elevenlabs_stream.log`: Detailed application logs
- Console output: Real-time conversation analysis

### **Common Issues**

**1. Connection Failed**
```bash
# Check API key
python main_elevenlabs.py --api-key YOUR_API_KEY --debug-style plain
```

**2. Quen Model Not Available**
```bash
# Ensure Ollama is running
ollama serve

# Check model availability
ollama list
```

**3. WebSocket Errors**
```bash
# Check network connectivity
curl -I https://api.elevenlabs.io
```

## 🧪 **Testing**

### **Test with Mock Data**
```bash
# Use existing mock processor for testing
python main.py --input-file messages.jsonl --window-size 20
```

### **Test ElevenLabs Connection**
```python
# Test script
from elevenlabs_client import ElevenLabsWebSocketClient

async def test_connection():
    client = ElevenLabsWebSocketClient("YOUR_API_KEY")
    connected = await client.connect()
    print(f"Connected: {connected}")
    await client.disconnect()

# Run test
asyncio.run(test_connection())
```

## 🔒 **Security**

### **API Key Management**
- Store API keys securely (environment variables)
- Never commit API keys to version control
- Use API key rotation for production

### **Environment Variables**
```bash
export ELEVENLABS_API_KEY="your_api_key_here"
python main_elevenlabs.py --api-key $ELEVENLABS_API_KEY
```

## 📈 **Performance**

### **Optimization Tips**
- **Window Size**: Adjust based on conversation pace (20-60 seconds)
- **Voice Quality**: Use high-quality voice models for better recognition
- **Network**: Ensure stable internet connection for WebSocket

### **Monitoring**
- Watch `elevenlabs_stream.log` for performance metrics
- Monitor WebSocket connection stability
- Track Quen response times

## 🚀 **Production Deployment**

### **1. Environment Setup**
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export ELEVENLABS_API_KEY="your_production_key"
export OLLAMA_HOST="http://localhost:11434"
```

### **2. Service Configuration**
```bash
# Run as service
nohup python main_elevenlabs.py --api-key $ELEVENLABS_API_KEY &
```

### **3. Monitoring**
```bash
# Monitor logs
tail -f elevenlabs_stream.log

# Check process
ps aux | grep main_elevenlabs
```

## 🤝 **Contributing**

### **Development Setup**
1. Fork the repository
2. Create feature branch
3. Test with ElevenLabs API
4. Submit pull request

### **Testing Guidelines**
- Test with real ElevenLabs conversations
- Verify windowing logic accuracy
- Check Quen response quality
- Validate error handling

## 📄 **License**

Apache License 2.0 - See [LICENSE](LICENSE) for details.

**Copyright 2024 Emanuel Kuce Radis, IntelMe.AI**

## 🙏 **Acknowledgments**

- **ElevenLabs**: For providing the conversational AI platform
- **Ollama**: For local LLM inference
- **Quen/Qwen**: For strategic analysis capabilities

---

**🎯 Ready to start real-time conversational analysis? Get your ElevenLabs API key and run the streamer!** 