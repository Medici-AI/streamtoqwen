"""
Sentiment Agent - Analyzes emotional states and sentiment
"""

import json
import re
from typing import Dict, Any
from .base_agent import BaseAgent

class SentimentAgent(BaseAgent):
    """Agent specialized in analyzing emotional states and sentiment."""
    
    def __init__(self):
        super().__init__(
            name="Sentiment Agent",
            color="🟢",
            storage_path="data/sentiment_agent",
            llm_type="quen"
        )
    
    def get_analysis_prompt(self, conversation_context: str) -> str:
        """Get sentiment analysis prompt."""
        return f"""
You are an expert Sentiment Analysis Agent. Your role is to analyze emotional states and sentiment from conversations.

CONVERSATION CONTEXT:
{conversation_context}

Analyze the emotional state and sentiment in this JSON format:
{{
    "primary_emotion": "The dominant emotion (happy, frustrated, anxious, satisfied, etc.)",
    "emotional_intensity": "high/medium/low",
    "sentiment_score": "positive/neutral/negative",
    "emotional_triggers": ["What triggered these emotions"],
    "emotional_stability": "stable/volatile/improving/declining",
    "trust_level": "high/medium/low",
    "engagement_level": "high/medium/low",
    "emotional_insights": "Detailed analysis of emotional state and sentiment"
}}

Focus on:
- What is the customer's primary emotion?
- How intense is their emotional state?
- What is the overall sentiment?
- What triggered these emotions?
- How stable is their emotional state?
- What is their trust level?
- How engaged are they?
- What emotional insights can guide the RM?

Provide emotional intelligence insights that help the RM understand and respond to the customer's emotional state.
"""
    
    def parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse sentiment analysis response."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)
                
                # Ensure all required fields exist
                required_fields = [
                    "primary_emotion", "emotional_intensity", "sentiment_score",
                    "emotional_triggers", "emotional_stability", "trust_level",
                    "engagement_level", "emotional_insights"
                ]
                
                for field in required_fields:
                    if field not in parsed:
                        if field == "emotional_triggers":
                            parsed[field] = []
                        else:
                            parsed[field] = "Not specified"
                
                return parsed
            else:
                # Fallback parsing
                return {
                    "primary_emotion": "Unable to parse",
                    "emotional_intensity": "medium",
                    "sentiment_score": "neutral",
                    "emotional_triggers": [],
                    "emotional_stability": "stable",
                    "trust_level": "medium",
                    "engagement_level": "medium",
                    "emotional_insights": response[:200] + "..." if len(response) > 200 else response
                }
                
        except Exception as e:
            return {
                "primary_emotion": "Error parsing response",
                "emotional_intensity": "medium",
                "sentiment_score": "neutral",
                "emotional_triggers": [],
                "emotional_stability": "stable",
                "trust_level": "medium",
                "engagement_level": "medium",
                "emotional_insights": f"Error: {str(e)}"
            } 