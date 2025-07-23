#!/usr/bin/env python3
"""
RM Conversation Streamer with Flink & Quen Integration

This application simulates streaming conversations between relationship managers
and customers through Apache Flink, applies session-based windowing, and generates
AI responses using a local Quen model via Ollama.

Usage:
    python main.py [--input-file messages.jsonl] [--window-size 30] [--speed-factor 2.0]
"""

import argparse
import logging
import sys
from pathlib import Path

from stream_processor_simple import SimpleStreamProcessor
from quen_client import QuenClient


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('streamllm.log')
        ]
    )


def check_prerequisites(input_file: str) -> bool:
    """Check if all prerequisites are met."""
    logger = logging.getLogger(__name__)
    
    # Check if input file exists
    if not Path(input_file).exists():
        logger.error(f"Input file not found: {input_file}")
        return False
    
    # Check if Ollama is running and Quen model is available
    quen_client = QuenClient()
    if not quen_client.is_available():
        logger.warning("Quen model not available via Ollama. Will use mock responses.")
        logger.info("To use real Quen model:")
        logger.info("1. Install Ollama: https://ollama.ai/")
        logger.info("2. Pull Quen model: ollama pull quen:32b")
        logger.info("3. Start Ollama service")
    else:
        logger.info("✅ Quen model is available via Ollama")
    
    return True


def main():
    """Main entry point for the streaming application."""
    parser = argparse.ArgumentParser(
        description="RM Conversation Streamer with Flink & Quen Integration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                                    # Use default settings
  python main.py --input-file data.jsonl           # Use custom input file
  python main.py --window-size 60 --speed-factor 1.0  # 60s windows, real-time speed
        """
    )
    
    parser.add_argument(
        '--input-file',
        default='messages.jsonl',
        help='Input JSONL file with conversation messages (default: messages.jsonl)'
    )
    
    parser.add_argument(
        '--window-size',
        type=int,
        default=30,
        help='Window size in seconds for conversation aggregation (default: 30)'
    )
    
    parser.add_argument(
        '--speed-factor',
        type=float,
        default=2.0,
        help='Speed factor for message emission (default: 2.0 = 2x speed)'
    )
    
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level (default: INFO)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)
    
    # Print startup banner
    print("=" * 80)
    print("🚀 RM Conversation Streamer with Flink & Quen Integration")
    print("=" * 80)
    print(f"📁 Input File: {args.input_file}")
    print(f"⏱️  Window Size: {args.window_size} seconds")
    print(f"⚡ Speed Factor: {args.speed_factor}x")
    print(f"🔧 Log Level: {args.log_level}")
    print("=" * 80)
    
    # Check prerequisites
    if not check_prerequisites(args.input_file):
        logger.error("Prerequisites check failed. Exiting.")
        sys.exit(1)
    
    try:
        # Initialize Quen client
        quen_client = QuenClient()
        
        # Initialize simplified stream processor
        processor = SimpleStreamProcessor(quen_client)
        
        # Execute the streaming pipeline
        logger.info("Starting streaming pipeline...")
        processor.execute(args.input_file, args.window_size, args.speed_factor)
        
    except KeyboardInterrupt:
        logger.info("Streaming interrupted by user")
        print("\n🛑 Streaming stopped by user")
    except Exception as e:
        logger.error(f"Error in streaming pipeline: {e}")
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 