"""
Intent Agent - Analyzes customer intent and motivations
"""

import json
import re
from typing import Dict, Any
from .base_agent import BaseAgent

class IntentAgent(BaseAgent):
    """Agent specialized in analyzing customer intent and motivations."""
    
    def __init__(self):
        super().__init__(
            name="Intent Agent",
            color="🔵",
            storage_path="data/intent_agent",
            llm_type="quen"
        )
    
    def get_analysis_prompt(self, conversation_context: str) -> str:
        """Get intent analysis prompt."""
        return f"""
You are an expert Intent Analysis Agent. Your role is to analyze customer intent and motivations from conversations.

CONVERSATION CONTEXT:
{conversation_context}

Analyze the customer's intent and provide insights in this JSON format:
{{
    "primary_intent": "The main thing the customer wants to accomplish",
    "secondary_intents": ["List of other things they might want"],
    "motivations": "Why they want this (financial, convenience, urgency, etc.)",
    "intent_confidence": "high/medium/low",
    "intent_clarity": "clear/unclear/mixed",
    "next_expected_actions": ["What the customer likely wants to do next"],
    "intent_analysis": "Detailed analysis of the customer's intent and motivations"
}}

Focus on:
- What does the customer actually want?
- Why do they want it?
- How clear is their intent?
- What are their underlying motivations?
- What actions do they expect next?

Provide strategic insights that help the RM understand the customer's true intentions.
"""
    
    def parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse intent analysis response."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)
                
                # Ensure all required fields exist
                required_fields = [
                    "primary_intent", "secondary_intents", "motivations",
                    "intent_confidence", "intent_clarity", "next_expected_actions",
                    "intent_analysis"
                ]
                
                for field in required_fields:
                    if field not in parsed:
                        parsed[field] = "Not specified"
                
                return parsed
            else:
                # Fallback parsing
                return {
                    "primary_intent": "Unable to parse",
                    "secondary_intents": [],
                    "motivations": "Unable to parse",
                    "intent_confidence": "low",
                    "intent_clarity": "unclear",
                    "next_expected_actions": [],
                    "intent_analysis": response[:200] + "..." if len(response) > 200 else response
                }
                
        except Exception as e:
            return {
                "primary_intent": "Error parsing response",
                "secondary_intents": [],
                "motivations": "Error parsing response",
                "intent_confidence": "low",
                "intent_clarity": "unclear",
                "next_expected_actions": [],
                "intent_analysis": f"Error: {str(e)}"
            } 