#!/usr/bin/env python3
"""
ElevenLabs REST-based Conversational AI Streamer

This script integrates with ElevenLabs using REST API to provide real-time
streaming analysis using our existing windowing logic and Quen LLM integration.
"""

import asyncio
import argparse
import logging
import os
import sys
from datetime import datetime

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from elevenlabs_rest_client import ElevenLabsRestProcessor
from quen_client import QuenClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('elevenlabs_rest_stream.log')
    ]
)

logger = logging.getLogger(__name__)

def print_banner():
    """Print startup banner."""
    print("=" * 80)
    print("🎤 ElevenLabs REST-based Conversational AI Streamer")
    print("=" * 80)
    print("🔗 Integrates with ElevenLabs API for live analysis")
    print("🧠 Uses Quen LLM for strategic advice and cognitive analysis")
    print("⏱️  Real-time windowing with cumulative context")
    print("🎭 Simulated conversation for testing")
    print("=" * 80)

async def main():
    """Main entry point for ElevenLabs REST streaming."""
    parser = argparse.ArgumentParser(
        description="ElevenLabs REST-based Conversational AI Streamer"
    )
    
    parser.add_argument(
        "--api-key",
        required=True,
        help="ElevenLabs API key"
    )
    
    parser.add_argument(
        "--window-size",
        type=float,
        default=20.0,
        help="Window size in seconds (default: 20.0)"
    )
    
    parser.add_argument(
        "--debug-style",
        choices=["rich", "colorama", "plain"],
        default="rich",
        help="Debug output style (default: rich)"
    )
    
    parser.add_argument(
        "--voice-rm",
        default="21m00Tcm4TlvDq8ikWAM",  # Default RM voice ID
        help="Voice ID for Relationship Manager"
    )
    
    parser.add_argument(
        "--voice-customer",
        default="AZnzlk1XvdvUeBnXmlld",  # Default Customer voice ID
        help="Voice ID for Customer"
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Display configuration
    print(f"📁 API Key: {'*' * 20}{args.api_key[-4:]}")
    print(f"⏱️  Window Size: {args.window_size} seconds")
    print(f"🎨 Debug Style: {args.debug_style}")
    print(f"🎤 RM Voice ID: {args.voice_rm}")
    print(f"🎤 Customer Voice ID: {args.voice_customer}")
    print("=" * 80)
    
    try:
        # Initialize Quen client
        logger.info("🔧 Initializing Quen client...")
        quen_client = QuenClient()
        
        # Test Quen connection
        try:
            # Quick test to see if Quen is available
            test_response = quen_client.get_response(
                session_id="test",
                conversation_context="Test message",
                is_incomplete=False
            )
            logger.info("✅ Quen model is available via Ollama")
        except Exception as e:
            logger.warning(f"⚠️  Quen model not available: {e}")
            logger.info("🔄 Continuing with mock responses...")
        
        # Initialize ElevenLabs REST processor
        logger.info("🔧 Initializing ElevenLabs REST processor...")
        processor = ElevenLabsRestProcessor(
            api_key=args.api_key,
            quen_client=quen_client,
            debug_style=args.debug_style
        )
        
        # Configure voice IDs
        voice_ids = {
            "rm": args.voice_rm,
            "customer": args.voice_customer
        }
        
        logger.info("🚀 Starting ElevenLabs REST processor...")
        logger.info("📝 Instructions:")
        logger.info("   1. The system will test ElevenLabs API connection")
        logger.info("   2. Start a simulated conversation for testing")
        logger.info("   3. Watch the console for window analysis and Quen advice")
        logger.info("   4. The conversation will simulate real-time streaming")
        logger.info("   5. Press Ctrl+C to stop")
        
        # Start the processor
        await processor.start(window_size_seconds=args.window_size)
        
    except KeyboardInterrupt:
        logger.info("🛑 Received interrupt signal")
    except Exception as e:
        logger.error(f"❌ Error in ElevenLabs REST processor: {e}")
        return 1
    finally:
        # Cleanup
        if 'processor' in locals():
            await processor.stop()
        logger.info("👋 ElevenLabs REST processor stopped")
    
    return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1) 