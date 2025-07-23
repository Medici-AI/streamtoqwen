import requests
import json
import logging
from datetime import datetime
from typing import Optional
from models import ConversationWindow, QuenResponse, CognitiveAnalysis

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
    
    def generate_response(self, conversation_window: ConversationWindow, is_incomplete: bool = False) -> QuenResponse:
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
                    "max_tokens": 500
                }
            }
            
            logger.info(f"Sending prompt to Quen for session {conversation_window.session_id}")
            response = requests.post(self.api_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                quen_response_text = result.get('response', '').strip()
                logger.info(f"Received response from Quen: {quen_response_text[:100]}...")
                
                # Try to parse structured response
                parsed_response = self._parse_structured_response(quen_response_text)
                
                return QuenResponse(
                    session_id=conversation_window.session_id,
                    response=parsed_response['response'],
                    analysis=parsed_response['analysis'],
                    timestamp=datetime.now()
                )
            else:
                logger.error(f"Quen API error: {response.status_code} - {response.text}")
                return self._get_mock_response(conversation_window)
                
        except Exception as e:
            logger.error(f"Error communicating with Quen: {e}")
            return self._get_mock_response(conversation_window)
    
    def _parse_structured_response(self, response_text: str) -> dict:
        """Parse the structured response from Quen, handling both JSON and fallback formats."""
        try:
            # Try to extract JSON from the response
            # Look for JSON blocks in the response
            import re
            
            # Find JSON-like content
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                parsed = json.loads(json_str)
                
                # Validate the structure
                if 'response' in parsed and 'analysis' in parsed:
                    analysis_data = parsed['analysis']
                    analysis = CognitiveAnalysis(
                        customer_intent=analysis_data.get('customer_intent', 'unknown'),
                        rm_strategy=analysis_data.get('rm_strategy', 'unknown'),
                        urgency_level=analysis_data.get('urgency_level', 'medium'),
                        emotion=analysis_data.get('emotion', 'neutral'),
                        next_action=analysis_data.get('next_action', 'continue conversation')
                    )
                    
                    return {
                        'response': parsed['response'],
                        'analysis': analysis
                    }
            
            # Fallback: treat the entire response as text
            logger.warning("Could not parse structured response, using fallback")
            return {
                'response': response_text,
                'analysis': self._get_mock_analysis()
            }
            
        except Exception as e:
            logger.error(f"Error parsing structured response: {e}")
            return {
                'response': response_text,
                'analysis': self._get_mock_analysis()
            }
    
    def _get_mock_analysis(self) -> CognitiveAnalysis:
        """Generate a mock cognitive analysis."""
        return CognitiveAnalysis(
            customer_intent="general inquiry",
            rm_strategy="assist and guide",
            urgency_level="medium",
            emotion="positive",
            next_action="continue conversation"
        )
    
    def get_response(self, session_id: str, conversation_context: str, is_incomplete: bool = False) -> QuenResponse:
        """Get response for streaming context."""
        # Create a conversation window for compatibility
        conversation_window = ConversationWindow(
            session_id=session_id,
            window_start=datetime.now(),
            window_end=datetime.now(),
            messages=[{"sender": "system", "message": conversation_context}]
        )
        
        # Add incomplete context note to the prompt
        if is_incomplete:
            conversation_window.messages[0]["message"] += "\n\n[NOTE: This conversation context is incomplete and being streamed in real-time. Please provide strategic advice to the RM based on the partial information available.]"
        
        return self.generate_response(conversation_window, is_incomplete)
    
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
            analysis=self._get_mock_analysis(),
            timestamp=datetime.now()
        ) 