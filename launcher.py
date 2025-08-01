#!/usr/bin/env python3
"""
Quick Launcher for ElevenLabs Conversational AI Service
"""

import sys
import subprocess
import argparse
import os

def print_banner():
    """Print launcher banner."""
    print("=" * 80)
    print("🚀 ElevenLabs Conversational AI - Quick Launcher")
    print("=" * 80)

def print_modes():
    """Print available launch modes."""
    print("\n📋 Available Launch Modes:")
    print("  1. console    - Interactive console application")
    print("  2. fast       - Fast mode (3s windows, word chunks)")
    print("  3. standard   - Standard mode (5s windows, word chunks)")
    print("  4. detailed   - Detailed mode (10s windows, sentence chunks)")
    print("  5. test       - Test connections only")
    print("  6. simulate   - Run with simulated data (no microphone)")
    print("\n💡 Usage: python launcher.py <mode> [options]")

def run_command(cmd, description):
    """Run a command with description."""
    print(f"\n🚀 {description}")
    print(f"📝 Command: {' '.join(cmd)}")
    print("-" * 60)
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Command failed with exit code {e.returncode}")
    except FileNotFoundError:
        print(f"\n❌ Command not found: {cmd[0]}")

def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(
        description="Quick Launcher for ElevenLabs Conversational AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python launcher.py console
  python launcher.py fast
  python launcher.py standard --debug-style colorama
  python launcher.py test
        """
    )
    
    parser.add_argument(
        "mode",
        choices=["console", "fast", "standard", "detailed", "test", "simulate"],
        help="Launch mode"
    )
    
    parser.add_argument(
        "--agent-id",
        default="agent_01jydy1bkeefwsmp63xbp1kn0n",
        help="ElevenLabs agent ID"
    )
    
    parser.add_argument(
        "--debug-style",
        choices=["rich", "colorama", "plain"],
        default="rich",
        help="Debug output style"
    )
    
    parser.add_argument(
        "--window-size",
        type=float,
        help="Override window size (seconds)"
    )
    
    args = parser.parse_args()
    
    print_banner()
    
    # Mode configurations
    modes = {
        "console": {
            "cmd": ["python", "console_app.py"],
            "desc": "Starting Interactive Console Application"
        },
        "fast": {
            "cmd": ["python", "main_elevenlabs_microphone.py", 
                   "--agent-id", args.agent_id,
                   "--window-size", "3",
                   "--debug-style", args.debug_style,
                   "--chunk-type", "word"],
            "desc": "Starting Fast Mode (3s windows, word chunks)"
        },
        "standard": {
            "cmd": ["python", "main_elevenlabs_microphone.py",
                   "--agent-id", args.agent_id,
                   "--window-size", "5",
                   "--debug-style", args.debug_style,
                   "--chunk-type", "word"],
            "desc": "Starting Standard Mode (5s windows, word chunks)"
        },
        "detailed": {
            "cmd": ["python", "main_elevenlabs_microphone.py",
                   "--agent-id", args.agent_id,
                   "--window-size", "10",
                   "--debug-style", args.debug_style,
                   "--chunk-type", "sentence"],
            "desc": "Starting Detailed Mode (10s windows, sentence chunks)"
        },
        "test": {
            "cmd": ["python", "-c", """
import asyncio
from console_app import ConsoleApp

async def test():
    app = ConsoleApp()
    await app.test_connections()

asyncio.run(test())
            """],
            "desc": "Testing All Connections"
        },
        "simulate": {
            "cmd": ["python", "main.py",
                   "--streaming-mode", "true_streaming",
                   "--window-size", "5",
                   "--debug-style", args.debug_style,
                   "--chunk-type", "word"],
            "desc": "Starting Simulation Mode (no microphone)"
        }
    }
    
    # Override window size if specified
    if args.window_size and args.mode in ["fast", "standard", "detailed"]:
        mode_config = modes[args.mode]
        # Find and replace window-size argument
        for i, arg in enumerate(mode_config["cmd"]):
            if arg == "--window-size":
                mode_config["cmd"][i + 1] = str(args.window_size)
                break
    
    # Run the selected mode
    if args.mode in modes:
        mode_config = modes[args.mode]
        run_command(mode_config["cmd"], mode_config["desc"])
    else:
        print(f"❌ Unknown mode: {args.mode}")
        print_modes()
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        print_banner()
        print_modes()
        sys.exit(0)
    
    main() 