from dataclasses import dataclass, asdict
from datetime import datetime
from typing import List, Optional
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
class ConversationWindow:
    """Represents an aggregated conversation window for Quen processing."""
    session_id: str
    window_start: datetime
    window_end: datetime
    messages: List[dict]
    
    def to_quen_prompt(self) -> str:
        """Convert to a prompt format suitable for Quen model."""
        conversation_text = "\n".join([
            f"{msg['sender'].title()}: {msg['message']}"
            for msg in self.messages
        ])
        
        return f"""The following is a conversation between a Relationship Manager and a Customer:

{conversation_text}

Based on the above window of conversation, what should the RM say next? Please provide a natural, helpful response that continues the conversation appropriately."""


@dataclass
class QuenResponse:
    """Represents a response from the Quen model."""
    session_id: str
    response: str
    timestamp: datetime
    
    def __str__(self):
        return f"[{self.timestamp.strftime('%H:%M:%S')}] Session {self.session_id}: {self.response}" 