#!/usr/bin/env python3
"""
Console Application for ElevenLabs Real-time Conversational AI Service
"""

import asyncio
import argparse
import logging
import sys
import time
import threading
from datetime import datetime
from typing import Optional, Dict, Any
import json

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm
from rich.align import Align

from quen_client import QuenClient
from microphone_client import MicrophoneClient
from models import MessageEvent, StreamingChunk

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ServiceStatus:
    """Track service status and metrics."""
    
    def __init__(self):
        self.is_running = False
        self.is_connected = False
        self.is_recording = False
        self.start_time = None
        self.session_count = 0
        self.message_count = 0
        self.window_count = 0
        self.last_activity = None
        self.error_count = 0
        self.quen_response_time = 0.0
        self.audio_chunks_sent = 0
        
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.now()
    
    def get_uptime(self) -> str:
        """Get formatted uptime."""
        if not self.start_time:
            return "00:00:00"
        
        delta = datetime.now() - self.start_time
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        seconds = delta.seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

class ConsoleApp:
    """Main console application for managing the ElevenLabs service."""
    
    def __init__(self):
        self.console = Console()
        self.status = ServiceStatus()
        self.quen_client = None
        self.microphone_client = None
        self.processor = None
        self.config = {}
        
    def print_banner(self):
        """Print application banner."""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🎤 ElevenLabs Conversational AI Console                   ║
║                                                                              ║
║  Real-time microphone input → ElevenLabs → Quen Analysis → Strategic Advice  ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        self.console.print(banner, style="cyan")
    
    def print_help(self):
        """Print help information."""
        help_text = """
📋 Available Commands:
  start     - Start the ElevenLabs service
  stop      - Stop the service
  status    - Show current service status
  config    - Show/update configuration
  test      - Test connections (Quen, microphone)
  logs      - Show recent logs
  help      - Show this help
  quit      - Exit the application

🔧 Configuration Options:
  --agent-id      - ElevenLabs agent ID
  --window-size   - Analysis window size (seconds)
  --debug-style   - Output style (rich/colorama/plain)
  --chunk-type    - Audio chunk type (character/word/sentence)
        """
        self.console.print(help_text, style="green")
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return {
            "agent_id": self.config.get("agent_id", "agent_01jydy1bkeefwsmp63xbp1kn0n"),
            "window_size": self.config.get("window_size", 5.0),
            "debug_style": self.config.get("debug_style", "rich"),
            "chunk_type": self.config.get("chunk_type", "word"),
            "quen_timeout": self.config.get("quen_timeout", 60.0),
            "connection_timeout": self.config.get("connection_timeout", 10.0)
        }
    
    def set_config(self, key: str, value: Any):
        """Set configuration value."""
        self.config[key] = value
        self.console.print(f"✅ Configuration updated: {key} = {value}", style="green")
    
    def show_config(self):
        """Show current configuration."""
        config = self.get_config()
        
        table = Table(title="🔧 Current Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="yellow")
        
        for key, value in config.items():
            table.add_row(key, str(value))
        
        self.console.print(table)
    
    def show_status(self):
        """Show current service status."""
        status_table = Table(title="📊 Service Status")
        status_table.add_column("Metric", style="cyan")
        status_table.add_column("Value", style="yellow")
        
        # Service status
        status_table.add_row("Service Running", "🟢 Yes" if self.status.is_running else "🔴 No")
        status_table.add_row("ElevenLabs Connected", "🟢 Yes" if self.status.is_connected else "🔴 No")
        status_table.add_row("Microphone Active", "🟢 Yes" if self.status.is_recording else "🔴 No")
        
        # Metrics
        status_table.add_row("Uptime", self.status.get_uptime())
        status_table.add_row("Sessions", str(self.status.session_count))
        status_table.add_row("Messages", str(self.status.message_count))
        status_table.add_row("Windows Processed", str(self.status.window_count))
        status_table.add_row("Audio Chunks Sent", str(self.status.audio_chunks_sent))
        status_table.add_row("Errors", str(self.status.error_count))
        
        if self.status.last_activity:
            status_table.add_row("Last Activity", self.status.last_activity.strftime("%H:%M:%S"))
        
        if self.status.quen_response_time > 0:
            status_table.add_row("Avg Quen Response", f"{self.status.quen_response_time:.2f}s")
        
        self.console.print(status_table)
    
    async def test_connections(self):
        """Test all connections."""
        self.console.print("🔍 Testing connections...", style="yellow")
        
        # Test Quen
        try:
            self.console.print("🧠 Testing Quen connection...", style="blue")
            quen_client = QuenClient()
            
            start_time = time.time()
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    quen_client.get_response,
                    session_id="test",
                    conversation_context="This is a test message.",
                    is_incomplete=False
                ),
                timeout=30.0
            )
            response_time = time.time() - start_time
            
            self.console.print(f"✅ Quen: Connected (Response time: {response_time:.2f}s)", style="green")
            
        except Exception as e:
            self.console.print(f"❌ Quen: Failed - {e}", style="red")
            return False
        
        # Test microphone
        try:
            self.console.print("🎤 Testing microphone...", style="blue")
            import pyaudio
            
            p = pyaudio.PyAudio()
            device_count = p.get_device_count()
            input_devices = []
            
            for i in range(device_count):
                device_info = p.get_device_info_by_index(i)
                if device_info['maxInputChannels'] > 0:
                    input_devices.append(device_info['name'])
            
            p.terminate()
            
            if input_devices:
                self.console.print(f"✅ Microphone: {len(input_devices)} input device(s) found", style="green")
                for device in input_devices[:3]:  # Show first 3
                    self.console.print(f"   📻 {device}", style="blue")
            else:
                self.console.print("❌ Microphone: No input devices found", style="red")
                return False
                
        except Exception as e:
            self.console.print(f"❌ Microphone: Failed - {e}", style="red")
            return False
        
        # Test ElevenLabs connection
        try:
            self.console.print("🔗 Testing ElevenLabs connection...", style="blue")
            config = self.get_config()
            
            # Quick connection test
            import websockets
            ws_url = f"wss://api.elevenlabs.io/v1/convai/conversation?agent_id={config['agent_id']}"
            
            async with websockets.connect(ws_url, ping_interval=20, ping_timeout=10) as websocket:
                self.console.print("✅ ElevenLabs: WebSocket connection successful", style="green")
                
        except Exception as e:
            self.console.print(f"❌ ElevenLabs: Failed - {e}", style="red")
            return False
        
        self.console.print("🎉 All connections tested successfully!", style="green")
        return True
    
    async def start_service(self):
        """Start the ElevenLabs service."""
        if self.status.is_running:
            self.console.print("⚠️  Service is already running", style="yellow")
            return
        
        self.console.print("🚀 Starting ElevenLabs service...", style="green")
        
        # Initialize components
        try:
            # Initialize Quen client
            self.quen_client = QuenClient()
            
            # Initialize processor
            from main_elevenlabs_microphone import ElevenLabsMicrophoneProcessor
            self.processor = ElevenLabsMicrophoneProcessor(
                self.quen_client, 
                debug_style=self.config.get("debug_style", "rich")
            )
            
            # Start service
            self.status.is_running = True
            self.status.start_time = datetime.now()
            self.status.update_activity()
            
            # Start in background
            config = self.get_config()
            
            # Create task for service execution
            service_task = asyncio.create_task(
                self.processor.execute(
                    agent_id=config["agent_id"],
                    window_size_seconds=config["window_size"],
                    chunk_type=config["chunk_type"]
                )
            )
            
            # Monitor service
            await self._monitor_service(service_task)
            
        except Exception as e:
            self.console.print(f"❌ Failed to start service: {e}", style="red")
            self.status.is_running = False
            self.status.error_count += 1
    
    async def _monitor_service(self, service_task):
        """Monitor the running service."""
        try:
            # Create live status display
            with Live(self._create_status_display(), refresh_per_second=2) as live:
                while self.status.is_running:
                    try:
                        # Update status
                        self._update_status_from_processor()
                        
                        # Update display
                        live.update(self._create_status_display())
                        
                        # Check if service task is done
                        if service_task.done():
                            if service_task.exception():
                                self.console.print(f"❌ Service error: {service_task.exception()}", style="red")
                            break
                        
                        await asyncio.sleep(0.5)
                        
                    except KeyboardInterrupt:
                        self.console.print("\n🛑 Stopping service...", style="yellow")
                        break
                    except Exception as e:
                        self.console.print(f"❌ Monitor error: {e}", style="red")
                        self.status.error_count += 1
                        
        except Exception as e:
            self.console.print(f"❌ Monitor failed: {e}", style="red")
        finally:
            self.status.is_running = False
    
    def _update_status_from_processor(self):
        """Update status from processor if available."""
        if self.processor:
            # Update connection status
            if hasattr(self.processor, 'microphone_client') and self.processor.microphone_client:
                self.status.is_connected = self.processor.microphone_client.websocket is not None
                self.status.is_recording = self.processor.microphone_client.is_recording
            
            # Update activity
            self.status.update_activity()
    
    def _create_status_display(self):
        """Create live status display."""
        layout = Layout()
        
        # Header
        header = Panel(
            f"🎤 ElevenLabs Service - {'🟢 Running' if self.status.is_running else '🔴 Stopped'}",
            style="cyan"
        )
        layout.add(header)
        
        # Status grid
        status_grid = Layout()
        status_grid.split_row(
            Layout(name="left"),
            Layout(name="right")
        )
        
        # Left panel - Service metrics
        left_table = Table(title="📊 Service Metrics")
        left_table.add_column("Metric", style="cyan")
        left_table.add_column("Value", style="yellow")
        
        left_table.add_row("Uptime", self.status.get_uptime())
        left_table.add_row("Status", "🟢 Active" if self.status.is_running else "🔴 Inactive")
        left_table.add_row("ElevenLabs", "🟢 Connected" if self.status.is_connected else "🔴 Disconnected")
        left_table.add_row("Microphone", "🟢 Recording" if self.status.is_recording else "🔴 Stopped")
        left_table.add_row("Messages", str(self.status.message_count))
        left_table.add_row("Windows", str(self.status.window_count))
        left_table.add_row("Errors", str(self.status.error_count))
        
        # Right panel - Configuration
        config = self.get_config()
        right_table = Table(title="⚙️ Configuration")
        right_table.add_column("Setting", style="cyan")
        right_table.add_column("Value", style="yellow")
        
        right_table.add_row("Agent ID", config["agent_id"][:20] + "..." if len(config["agent_id"]) > 20 else config["agent_id"])
        right_table.add_row("Window Size", f"{config['window_size']}s")
        right_table.add_row("Debug Style", config["debug_style"])
        right_table.add_row("Chunk Type", config["chunk_type"])
        
        status_grid["left"].update(Panel(left_table))
        status_grid["right"].update(Panel(right_table))
        
        layout.add(status_grid)
        
        # Instructions
        instructions = Panel(
            "💡 Press Ctrl+C to stop the service",
            style="green"
        )
        layout.add(instructions)
        
        return layout
    
    def stop_service(self):
        """Stop the ElevenLabs service."""
        if not self.status.is_running:
            self.console.print("⚠️  Service is not running", style="yellow")
            return
        
        self.console.print("🛑 Stopping service...", style="yellow")
        self.status.is_running = False
        
        if self.processor and hasattr(self.processor, 'microphone_client'):
            asyncio.create_task(self.processor.microphone_client.disconnect())
        
        self.console.print("✅ Service stopped", style="green")
    
    async def run_interactive(self):
        """Run the interactive console."""
        self.print_banner()
        self.print_help()
        
        while True:
            try:
                command = Prompt.ask("\n🎤 Enter command", choices=[
                    "start", "stop", "status", "config", "test", "logs", "help", "quit"
                ])
                
                if command == "quit":
                    if self.status.is_running:
                        if Confirm.ask("⚠️  Service is running. Stop it?"):
                            self.stop_service()
                    self.console.print("👋 Goodbye!", style="green")
                    break
                    
                elif command == "start":
                    await self.start_service()
                    
                elif command == "stop":
                    self.stop_service()
                    
                elif command == "status":
                    self.show_status()
                    
                elif command == "config":
                    self.show_config()
                    
                elif command == "test":
                    await self.test_connections()
                    
                elif command == "logs":
                    self.console.print("📋 Recent logs:", style="blue")
                    # In a real implementation, you'd show actual logs
                    self.console.print("   (Log display not implemented yet)")
                    
                elif command == "help":
                    self.print_help()
                    
            except KeyboardInterrupt:
                self.console.print("\n👋 Goodbye!", style="green")
                break
            except Exception as e:
                self.console.print(f"❌ Error: {e}", style="red")

async def main():
    """Main entry point."""
    app = ConsoleApp()
    await app.run_interactive()

if __name__ == "__main__":
    asyncio.run(main()) 