"""
Data models for the streaming conversation system

Copyright 2024 Emanuel Kuce Radis, IntelMe.AI

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any
import json


@dataclass
class MessageEvent:
    """Represents a single message event in the conversation stream."""
    session_id: str
    timestamp: datetime
    sender: str
    message: str
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        return {
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat(),
            'sender': self.sender,
            'message': self.message
        }


@dataclass
class CognitiveAnalysis:
    """Represents cognitive analysis of the conversation."""
    customer_intent: str
    rm_strategy: str
    urgency_level: str
    emotion: str
    next_action: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'customer_intent': self.customer_intent,
            'rm_strategy': self.rm_strategy,
            'urgency_level': self.urgency_level,
            'emotion': self.emotion,
            'next_action': self.next_action
        }


@dataclass
class QuenResponse:
    """Represents a response from the Quen model with cognitive analysis."""
    session_id: str
    response: str
    analysis: Optional[CognitiveAnalysis]
    timestamp: datetime
    
    def __str__(self):
        return f"[{self.timestamp.strftime('%H:%M:%S')}] Session {self.session_id}: {self.response}"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'session_id': self.session_id,
            'response': self.response,
            'analysis': self.analysis.to_dict() if self.analysis else None,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class ConversationWindow:
    """Represents an aggregated conversation window for Quen processing."""
    session_id: str
    window_start: datetime
    window_end: datetime
    messages: List[dict]
    
    def to_quen_prompt(self) -> str:
        """Convert to a prompt format suitable for Quen model with cognitive analysis."""
        conversation_text = "\n".join([
            f"{msg['sender'].title()}: {msg['message']}"
            for msg in self.messages
        ])
        
        return f"""You are Quen, an AI assistant providing strategic advice to Relationship Managers (RMs) based on real-time conversation analysis.

The following is a conversation between a Relationship Manager and a Customer:

{conversation_text}

Your role is to analyze this conversation and provide strategic guidance to the RM. You are NOT participating in the conversation directly - you are advising the RM on how to proceed.

Based on your analysis, provide:
1. Strategic advice to the RM on how to respond or proceed
2. Cognitive analysis of the conversation dynamics

Please provide your response in this exact JSON format:
{{
  "response": "Strategic advice to the RM: [Your specific guidance on how the RM should respond or proceed]",
  "analysis": {{
    "customer_intent": "What the customer is trying to achieve",
    "rm_strategy": "Recommended strategy for the RM",
    "urgency_level": "low/medium/high",
    "emotion": "Customer's emotional state",
    "next_action": "What the RM should do next"
  }}
}}

Remember: You are advising the RM, not participating in the conversation directly."""


@dataclass
class SpeakerStream:
    """Represents a stream of messages from a specific speaker."""
    session_id: str
    speaker: str  # "customer" or "rm"
    messages: List[MessageEvent]
    
    def add_message(self, message: MessageEvent):
        """Add a message to this speaker's stream."""
        self.messages.append(message)
    
    def get_messages_in_window(self, start_time: datetime, end_time: datetime) -> List[MessageEvent]:
        """Get messages within the specified time window."""
        return [
            msg for msg in self.messages
            if start_time <= msg.timestamp <= end_time
        ]
    
    def clear_messages_before(self, timestamp: datetime):
        """Clear messages before the specified timestamp."""
        self.messages = [msg for msg in self.messages if msg.timestamp >= timestamp] 