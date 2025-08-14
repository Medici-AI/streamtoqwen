#!/usr/bin/env python3
"""
Main entry point for ElevenLabs WebSocket streaming integration
"""

import asyncio
import argparse
import logging
import sys
from datetime import datetime

from quen_client import QuenClient
from elevenlabs_client import ElevenLabsStreamProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_banner():
    """Print application banner."""
    print("=" * 80)
    print("🎤 ElevenLabs Real-time Conversational AI Streamer")
    print("=" * 80)
    print("🔗 Integrates with ElevenLabs conversational AI for live analysis")
    print("🧠 Uses Quen LLM for strategic advice and cognitive analysis")
    print("⏱️  Real-time windowing with cumulative context")
    print("=" * 80)

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="ElevenLabs WebSocket Streaming with Quen Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main_elevenlabs.py --api-key YOUR_KEY --window-size 20 --debug-style rich
  python main_elevenlabs.py --api-key YOUR_KEY --window-size 15 --debug-style colorama
        """
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
        "--chunk-type",
        choices=["character", "word", "sentence"],
        default="word",
        help="Chunk type for streaming (default: word)"
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    print(f"📁 API Key: {'*' * 20}{args.api_key[-4:]}")
    print(f"⏱️  Window Size: {args.window_size} seconds")
    print(f"🎨 Debug Style: {args.debug_style}")
    print(f"🔤 Chunk Type: {args.chunk_type}")
    print("=" * 80)
    
    # Initialize Quen client
    logger.info("🔧 Initializing Quen client...")
    quen_client = QuenClient()
    
    # Test Quen connection
    try:
        test_response = quen_client.get_response(
            session_id="test",
            conversation_context="This is a test message to verify Quen is working.",
            is_incomplete=False
        )
        logger.info("✅ Quen model is available via Ollama")
    except Exception as e:
        logger.error(f"❌ Failed to connect to Quen: {e}")
        sys.exit(1)
    
    # Initialize ElevenLabs stream processor
    logger.info("🔧 Initializing ElevenLabs stream processor...")
    processor = ElevenLabsStreamProcessor(quen_client, debug_style=args.debug_style)
    
    # Start processing
    logger.info("🚀 Starting ElevenLabs stream processor...")
    logger.info("📝 Instructions:")
    logger.info("   1. The system will connect to ElevenLabs")
    logger.info("   2. Start a conversation in ElevenLabs")
    logger.info("   3. Speak naturally - the system will analyze in real-time")
    logger.info("   4. Watch the console for window analysis and Quen advice")
    logger.info("   5. Press Ctrl+C to stop")
    
    try:
        # Run the async processor
        asyncio.run(processor.execute(
            api_key=args.api_key,
            window_size_seconds=args.window_size,
            chunk_type=args.chunk_type
        ))
    except KeyboardInterrupt:
        logger.info("👋 ElevenLabs stream processor stopped")
    except Exception as e:
        logger.error(f"❌ Error in ElevenLabs stream processor: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 