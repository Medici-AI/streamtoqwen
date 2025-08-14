"""
Decision Agent - Makes real-time decisions and action planning
"""

import json
import re
from typing import Dict, Any
from .base_agent import BaseAgent

class DecisionAgent(BaseAgent):
    """Agent specialized in real-time decision making and action planning."""
    
    def __init__(self):
        super().__init__(
            name="Decision Agent",
            color="🔴",
            storage_path="data/decision_agent",
            llm_type="quen"
        )
    
    def get_analysis_prompt(self, conversation_context: str) -> str:
        """Get decision analysis prompt."""
        return f"""
You are an expert Decision Agent specializing in real-time decision making and action planning. Your role is to make immediate decisions based on conversation analysis.

CONVERSATION CONTEXT:
{conversation_context}

Make real-time decisions and provide action planning in this JSON format:
{{
    "immediate_action": "The immediate action the RM should take",
    "action_priority": "high/medium/low",
    "action_urgency": "immediate/soon/later",
    "decision_confidence": "high/medium/low",
    "alternative_actions": ["Alternative actions to consider"],
    "decision_rationale": "Why this decision was made",
    "expected_outcomes": ["Expected outcomes of this action"],
    "decision_analysis": "Detailed analysis of the decision and action plan"
}}

Focus on:
- What immediate action should the RM take?
- How urgent is this action?
- How confident are we in this decision?
- What alternatives should be considered?
- Why is this the best decision?
- What outcomes do we expect?
- How should the RM proceed?

Provide actionable decisions that help the RM take immediate, effective action.
"""
    
    def parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse decision analysis response."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)
                
                # Ensure all required fields exist
                required_fields = [
                    "immediate_action", "action_priority", "action_urgency",
                    "decision_confidence", "alternative_actions", "decision_rationale",
                    "expected_outcomes", "decision_analysis"
                ]
                
                for field in required_fields:
                    if field not in parsed:
                        if field in ["alternative_actions", "expected_outcomes"]:
                            parsed[field] = []
                        else:
                            parsed[field] = "Not specified"
                
                return parsed
            else:
                # Fallback parsing
                return {
                    "immediate_action": "Unable to parse",
                    "action_priority": "medium",
                    "action_urgency": "soon",
                    "decision_confidence": "low",
                    "alternative_actions": [],
                    "decision_rationale": "Unable to parse",
                    "expected_outcomes": [],
                    "decision_analysis": response[:200] + "..." if len(response) > 200 else response
                }
                
        except Exception as e:
            return {
                "immediate_action": "Error parsing response",
                "action_priority": "medium",
                "action_urgency": "soon",
                "decision_confidence": "low",
                "alternative_actions": [],
                "decision_rationale": "Error parsing response",
                "expected_outcomes": [],
                "decision_analysis": f"Error: {str(e)}"
            } 