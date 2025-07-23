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

from stream_processor_enhanced import EnhancedStreamProcessor
from stream_processor_true_streaming import TrueStreamingProcessor
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
        type=float,
        default=30.0,
        help='Window size in seconds for conversation aggregation (default: 30.0, supports sub-second values like 0.3)'
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
    
    parser.add_argument(
        '--debug-style',
        default='rich',
        choices=['rich', 'colorama', 'plain'],
        help='Debug output style (default: rich)'
    )
    
    parser.add_argument(
        '--streaming-mode',
        default='enhanced',
        choices=['enhanced', 'true-streaming'],
        help='Streaming mode: enhanced (batched) or true-streaming (character/word level) (default: enhanced)'
    )
    
    parser.add_argument(
        '--chunk-type',
        default='word',
        choices=['character', 'word', 'sentence'],
        help='Chunk type for true streaming mode (default: word)'
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
    print(f"🎨 Debug Style: {args.debug_style}")
    print(f"🔄 Streaming Mode: {args.streaming_mode}")
    if args.streaming_mode == 'true-streaming':
        print(f"📝 Chunk Type: {args.chunk_type}")
    print("=" * 80)
    
    # Check prerequisites
    if not check_prerequisites(args.input_file):
        logger.error("Prerequisites check failed. Exiting.")
        sys.exit(1)
    
    try:
        if args.streaming_mode == 'true-streaming':
            # Initialize true streaming processor
            processor = TrueStreamingProcessor(debug_style=args.debug_style)
            logger.info("Starting true streaming pipeline...")
            processor.execute(
                input_file=args.input_file,
                window_size_seconds=args.window_size,
                speed_factor=args.speed_factor,
                chunk_type=args.chunk_type
            )
        else:
            # Initialize Quen client
            quen_client = QuenClient()
            
            # Initialize enhanced stream processor
            processor = EnhancedStreamProcessor(quen_client, debug_style=args.debug_style)
            
            # Execute the streaming pipeline
            logger.info("Starting enhanced streaming pipeline...")
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