#!/usr/bin/env python3
"""
ElevenLabs Audio Monitor Setup Script
Handles installation and configuration for real-time audio monitoring
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_system_requirements():
    """Check if system meets requirements for audio monitoring."""
    print("🔍 Checking system requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    
    # Check OS
    system = platform.system()
    if system not in ["Darwin", "Linux", "Windows"]:
        print(f"❌ Unsupported OS: {system}")
        return False
    
    print(f"✅ OS: {system}")
    print(f"✅ Python: {sys.version}")
    return True

def install_audio_dependencies():
    """Install audio processing dependencies."""
    print("🔧 Installing audio dependencies...")
    
    system = platform.system()
    
    if system == "Darwin":  # macOS
        try:
            # Install portaudio via brew
            subprocess.run(["brew", "install", "portaudio"], check=True)
            print("✅ PortAudio installed via Homebrew")
        except subprocess.CalledProcessError:
            print("⚠️  PortAudio installation failed. Please install manually:")
            print("   brew install portaudio")
            return False
        except FileNotFoundError:
            print("⚠️  Homebrew not found. Please install PortAudio manually:")
            print("   brew install portaudio")
            return False
    
    elif system == "Linux":
        try:
            # Install portaudio via apt
            subprocess.run(["sudo", "apt-get", "update"], check=True)
            subprocess.run(["sudo", "apt-get", "install", "-y", "portaudio19-dev"], check=True)
            print("✅ PortAudio installed via apt")
        except subprocess.CalledProcessError:
            print("⚠️  PortAudio installation failed. Please install manually:")
            print("   sudo apt-get install portaudio19-dev")
            return False
    
    elif system == "Windows":
        print("ℹ️  Windows: PortAudio should be included with PyAudio")
    
    return True

def install_python_dependencies():
    """Install Python dependencies."""
    print("📦 Installing Python dependencies...")
    
    try:
        # Install requirements
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "audio_monitor_requirements.txt"], check=True)
        print("✅ Python dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install Python dependencies: {e}")
        return False

def test_audio_system():
    """Test audio system functionality."""
    print("🎵 Testing audio system...")
    
    try:
        import pyaudio
        import wave
        
        # Test PyAudio
        p = pyaudio.PyAudio()
        info = p.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        
        print(f"✅ PyAudio initialized successfully")
        print(f"✅ Found {numdevices} audio devices")
        
        # List audio devices
        for i in range(0, numdevices):
            device_info = p.get_device_info_by_host_api_device_index(0, i)
            print(f"   Device {i}: {device_info['name']}")
        
        p.terminate()
        return True
        
    except ImportError as e:
        print(f"❌ Audio dependencies not installed: {e}")
        return False
    except Exception as e:
        print(f"❌ Audio system test failed: {e}")
        return False

def create_config_file():
    """Create configuration file for ElevenLabs API."""
    config_content = """# ElevenLabs Audio Monitor Configuration

# ElevenLabs API Configuration
ELEVENLABS_API_KEY = "your_api_key_here"

# Voice Configuration
VOICE_ID_RM = "21m00Tcm4TlvDq8ikWAM"  # Rachel - Professional
VOICE_ID_CUSTOMER = "AZnzlk1XvdvUeBnXmlld"  # Domi - Friendly

# Audio Configuration
AUDIO_FORMAT = "pcm_16000"
SAMPLE_RATE = 44100
CHANNELS = 1
CHUNK_SIZE = 1024

# Multi-GPU Configuration
NUM_GPUS = 4
MAX_CONCURRENT_RMS = 3
MODEL_NAME = "qwen3:32b"

# Monitoring Configuration
INFLUENCE_THRESHOLDS = {
    "high": 0.8,
    "medium": 0.6,
    "low": 0.4
}

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FILE = "audio_monitor.log"
"""
    
    config_path = Path("audio_monitor_config.py")
    if not config_path.exists():
        with open(config_path, "w") as f:
            f.write(config_content)
        print("✅ Configuration file created: audio_monitor_config.py")
        print("⚠️  Please update your ElevenLabs API key in the config file")
    else:
        print("ℹ️  Configuration file already exists")

def print_usage_instructions():
    """Print usage instructions."""
    print("\n" + "="*60)
    print("🎵 ELEVENLABS AUDIO MONITOR SETUP COMPLETE")
    print("="*60)
    
    print("\n📋 Next Steps:")
    print("1. Update your ElevenLabs API key in 'audio_monitor_config.py'")
    print("2. Ensure your multi-GPU system is running")
    print("3. Start the audio monitor:")
    print("   python elevenlabs_audio_monitor.py")
    
    print("\n🎮 Usage:")
    print("- The system will connect to ElevenLabs WebSocket")
    print("- You'll hear real-time audio output with influence feedback")
    print("- Visual indicators show system influence levels:")
    print("  🟢 HIGH INFLUENCE: Strong system influence")
    print("  🟡 MEDIUM INFLUENCE: Moderate system influence")
    print("  🔴 LOW INFLUENCE: Minimal system influence")
    
    print("\n📊 Monitoring Features:")
    print("- Real-time audio playback")
    print("- Influence level calculation")
    print("- Processing time metrics")
    print("- Agent response tracking")
    print("- Audio event statistics")
    
    print("\n🔧 Troubleshooting:")
    print("- If audio doesn't work, check your system's audio devices")
    print("- Ensure ElevenLabs API key is valid")
    print("- Check GPU availability for multi-GPU system")
    print("- Monitor system resources during operation")
    
    print("\n" + "="*60)

def main():
    """Main setup function."""
    print("🎵 ElevenLabs Audio Monitor Setup")
    print("="*40)
    
    # Check system requirements
    if not check_system_requirements():
        print("❌ System requirements not met")
        return False
    
    # Install audio dependencies
    if not install_audio_dependencies():
        print("❌ Audio dependencies installation failed")
        return False
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("❌ Python dependencies installation failed")
        return False
    
    # Test audio system
    if not test_audio_system():
        print("❌ Audio system test failed")
        return False
    
    # Create configuration file
    create_config_file()
    
    # Print usage instructions
    print_usage_instructions()
    
    print("✅ Setup completed successfully!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 