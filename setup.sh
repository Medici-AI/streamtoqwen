#!/bin/bash

# RM Conversation Streamer Setup Script

echo "🚀 Setting up RM Conversation Streamer with Flink & Quen Integration"
echo "=================================================================="

# Check Python version
echo "📋 Checking Python version..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" = "$required_version" ]; then
    echo "✅ Python $python_version is compatible"
else
    echo "❌ Python $python_version is too old. Please install Python 3.8+"
    exit 1
fi

# Create virtual environment
echo "🔧 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if Ollama is installed
echo "🤖 Checking Ollama installation..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama is installed"
    
    # Check if Quen model is available
    if ollama list | grep -q "quen:32b"; then
        echo "✅ Quen 32B model is available"
    else
        echo "⚠️  Quen 32B model not found. To install:"
        echo "   ollama pull quen:32b"
    fi
else
    echo "⚠️  Ollama not found. To install:"
    echo "   curl -fsSL https://ollama.ai/install.sh | sh"
    echo "   ollama pull quen:32b"
    echo "   ollama serve"
fi

# Test the application
echo "🧪 Running component tests..."
python test_app.py

echo ""
echo "🎉 Setup complete!"
echo ""
echo "To run the application:"
echo "   source venv/bin/activate"
echo "   python main.py"
echo ""
echo "For help:"
echo "   python main.py --help"
echo ""
echo "To test components:"
echo "   python test_app.py" 