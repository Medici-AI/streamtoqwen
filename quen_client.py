import requests
import json
import logging
from datetime import datetime
from typing import Optional
from models import ConversationWindow, QuenResponse

logger = logging.getLogger(__name__)


class QuenClient:
    """Client for communicating with local Quen model via Ollama."""
    
    def __init__(self, base_url: str = "http://localhost:11434", model_name: str = "qwen2.5:32b"):
        self.base_url = base_url
        self.model_name = model_name
        self.api_url = f"{base_url}/api/generate"
        
    def is_available(self) -> bool:
        """Check if Quen model is available via Ollama."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                return any(model['name'] == self.model_name for model in models)
            return False
        except Exception as e:
            logger.warning(f"Could not connect to Ollama: {e}")
            return False
    
    def generate_response(self, conversation_window: ConversationWindow) -> QuenResponse:
        """Generate a response from Quen model for the given conversation window."""
        try:
            prompt = conversation_window.to_quen_prompt()
            
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 200
                }
            }
            
            logger.info(f"Sending prompt to Quen for session {conversation_window.session_id}")
            response = requests.post(self.api_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                quen_response = result.get('response', '').strip()
                logger.info(f"Received response from Quen: {quen_response[:100]}...")
                
                return QuenResponse(
                    session_id=conversation_window.session_id,
                    response=quen_response,
                    timestamp=datetime.now()
                )
            else:
                logger.error(f"Quen API error: {response.status_code} - {response.text}")
                return self._get_mock_response(conversation_window)
                
        except Exception as e:
            logger.error(f"Error communicating with Quen: {e}")
            return self._get_mock_response(conversation_window)
    
    def _get_mock_response(self, conversation_window: ConversationWindow) -> QuenResponse:
        """Generate a mock response when Quen is unavailable."""
        mock_responses = [
            "I understand your concern. Let me help you with that refinancing option.",
            "That's a great question. Based on your current situation, I'd recommend...",
            "I can see you're interested in our services. Let me provide you with some options.",
            "Thank you for sharing that information. Here's what I can offer you...",
            "I appreciate you bringing this up. Let me walk you through the process."
        ]
        
        import random
        mock_response = random.choice(mock_responses)
        
        logger.warning(f"Using mock response for session {conversation_window.session_id}")
        
        return QuenResponse(
            session_id=conversation_window.session_id,
            response=f"[MOCK] {mock_response}",
            timestamp=datetime.now()
        ) 