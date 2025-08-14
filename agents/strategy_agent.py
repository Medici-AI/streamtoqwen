"""
Strategy Agent - Provides strategic recommendations and business logic
"""

import json
import re
from typing import Dict, Any
from .base_agent import BaseAgent

class StrategyAgent(BaseAgent):
    """Agent specialized in providing strategic recommendations and business logic."""
    
    def __init__(self):
        super().__init__(
            name="Strategy Agent",
            color="🟡",
            storage_path="data/strategy_agent",
            llm_type="gpt4o"
        )
    
    def get_analysis_prompt(self, conversation_context: str) -> str:
        """Get strategy analysis prompt."""
        return f"""
You are an expert Strategy Agent specializing in business strategy and RM recommendations. Your role is to provide strategic advice based on conversation analysis.

CONVERSATION CONTEXT:
{conversation_context}

Provide strategic recommendations in this JSON format:
{{
    "strategic_approach": "Recommended strategic approach for the RM",
    "business_opportunities": ["List of business opportunities identified"],
    "risk_factors": ["Potential risks or concerns to address"],
    "competitive_advantages": ["How to position against competitors"],
    "value_proposition": "The value proposition to emphasize",
    "next_strategic_steps": ["Specific strategic actions to take"],
    "strategy_confidence": "high/medium/low",
    "strategy_analysis": "Detailed strategic analysis and reasoning"
}}

Focus on:
- What strategic approach should the RM take?
- What business opportunities are present?
- What risks need to be managed?
- How to create competitive advantages?
- What value proposition to emphasize?
- What specific strategic actions to take?

Provide actionable strategic insights that help the RM make informed business decisions.
"""
    
    def parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse strategy analysis response."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)
                
                # Ensure all required fields exist
                required_fields = [
                    "strategic_approach", "business_opportunities", "risk_factors",
                    "competitive_advantages", "value_proposition", "next_strategic_steps",
                    "strategy_confidence", "strategy_analysis"
                ]
                
                for field in required_fields:
                    if field not in parsed:
                        if field in ["business_opportunities", "risk_factors", "competitive_advantages", "next_strategic_steps"]:
                            parsed[field] = []
                        else:
                            parsed[field] = "Not specified"
                
                return parsed
            else:
                # Fallback parsing
                return {
                    "strategic_approach": "Unable to parse",
                    "business_opportunities": [],
                    "risk_factors": [],
                    "competitive_advantages": [],
                    "value_proposition": "Unable to parse",
                    "next_strategic_steps": [],
                    "strategy_confidence": "low",
                    "strategy_analysis": response[:200] + "..." if len(response) > 200 else response
                }
                
        except Exception as e:
            return {
                "strategic_approach": "Error parsing response",
                "business_opportunities": [],
                "risk_factors": [],
                "competitive_advantages": [],
                "value_proposition": "Error parsing response",
                "next_strategic_steps": [],
                "strategy_confidence": "low",
                "strategy_analysis": f"Error: {str(e)}"
            } 