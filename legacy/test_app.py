#!/usr/bin/env python3
"""
Test script for RM Conversation Streamer components.

This script tests individual components without running the full Flink pipeline.
"""

import json
import logging
from datetime import datetime
from models import MessageEvent, ConversationWindow, QuenResponse
from quen_client import QuenClient

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_message_parsing():
    """Test parsing of message events from JSON."""
    print("🧪 Testing Message Parsing...")
    
    sample_json = {
        "session_id": "test123",
        "timestamp": "2025-01-23T14:30:00Z",
        "sender": "customer",
        "message": "Hello, I need help with my account."
    }
    
    # Test JSON parsing
    event = MessageEvent(
        session_id=sample_json['session_id'],
        timestamp=datetime.fromisoformat(sample_json['timestamp'].replace('Z', '+00:00')),
        sender=sample_json['sender'],
        message=sample_json['message']
    )
    
    print(f"✅ Parsed event: {event.session_id} - {event.sender}: {event.message}")
    return event


def test_conversation_window():
    """Test conversation window creation and prompt generation."""
    print("\n🧪 Testing Conversation Window...")
    
    messages = [
        {"sender": "customer", "message": "Hi, I'm interested in refinancing my loan."},
        {"sender": "rm", "message": "Hello! I'd be happy to help you with refinancing. What's your current loan situation?"},
        {"sender": "customer", "message": "I have a 30-year fixed mortgage at 4.5% interest rate."}
    ]
    
    window = ConversationWindow(
        session_id="test123",
        window_start=datetime.now(),
        window_end=datetime.now(),
        messages=messages
    )
    
    print(f"✅ Created window for session: {window.session_id}")
    print(f"✅ Window contains {len(window.messages)} messages")
    
    # Test prompt generation
    prompt = window.to_quen_prompt()
    print(f"✅ Generated prompt ({len(prompt)} characters)")
    print(f"📝 Prompt preview: {prompt[:100]}...")
    
    return window


def test_quen_client():
    """Test Quen client functionality."""
    print("\n🧪 Testing Quen Client...")
    
    client = QuenClient()
    
    # Test availability check
    is_available = client.is_available()
    print(f"✅ Quen availability check: {'Available' if is_available else 'Not available (will use mock)'}")
    
    # Test response generation
    test_window = ConversationWindow(
        session_id="test123",
        window_start=datetime.now(),
        window_end=datetime.now(),
        messages=[
            {"sender": "customer", "message": "Hi, I need help with my investment portfolio."},
            {"sender": "rm", "message": "I'd be happy to help! What are your investment goals?"}
        ]
    )
    
    response = client.generate_response(test_window)
    print(f"✅ Generated response: {response.response[:100]}...")
    
    return response


def test_input_file():
    """Test reading the input file."""
    print("\n🧪 Testing Input File...")
    
    try:
        with open('messages.jsonl', 'r') as file:
            lines = file.readlines()
            print(f"✅ Input file contains {len(lines)} messages")
            
            # Parse first few messages
            for i, line in enumerate(lines[:3]):
                data = json.loads(line.strip())
                print(f"   Message {i+1}: {data['session_id']} - {data['sender']}: {data['message'][:50]}...")
                
    except FileNotFoundError:
        print("❌ Input file not found: messages.jsonl")
    except Exception as e:
        print(f"❌ Error reading input file: {e}")


def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 RM Conversation Streamer - Component Tests")
    print("=" * 60)
    
    try:
        # Run tests
        test_message_parsing()
        test_conversation_window()
        test_quen_client()
        test_input_file()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("🚀 Ready to run: python main.py")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 