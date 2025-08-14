"""
Learning Agent - Extracts patterns and builds long-term knowledge
"""

import json
import re
from typing import Dict, Any
from .base_agent import BaseAgent

class LearningAgent(BaseAgent):
    """Agent specialized in pattern recognition and long-term knowledge building."""
    
    def __init__(self):
        super().__init__(
            name="Learning Agent",
            color="🟣",
            storage_path="data/learning_agent",
            llm_type="gpt4o"
        )
    
    def get_analysis_prompt(self, conversation_context: str) -> str:
        """Get learning analysis prompt."""
        return f"""
You are an expert Learning Agent specializing in pattern recognition and long-term knowledge building. Your role is to extract insights and patterns from conversations.

CONVERSATION CONTEXT:
{conversation_context}

Analyze patterns and extract knowledge in this JSON format:
{{
    "identified_patterns": ["Patterns observed in this conversation"],
    "knowledge_insights": ["New knowledge gained from this interaction"],
    "behavioral_trends": ["Customer behavior trends identified"],
    "learning_opportunities": ["What can be learned from this interaction"],
    "pattern_confidence": "high/medium/low",
    "knowledge_relevance": "high/medium/low",
    "long_term_implications": ["Long-term implications of these patterns"],
    "learning_analysis": "Detailed analysis of patterns and knowledge extraction"
}}

Focus on:
- What patterns are emerging in this conversation?
- What new knowledge can be extracted?
- What behavioral trends are observable?
- What learning opportunities exist?
- How confident are we in these patterns?
- How relevant is this knowledge?
- What are the long-term implications?
- How can this learning be applied?

Provide insights that help build long-term knowledge and improve future interactions.
"""
    
    def parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse learning analysis response."""
        try:
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                parsed = json.loads(json_str)
                
                # Ensure all required fields exist
                required_fields = [
                    "identified_patterns", "knowledge_insights", "behavioral_trends",
                    "learning_opportunities", "pattern_confidence", "knowledge_relevance",
                    "long_term_implications", "learning_analysis"
                ]
                
                for field in required_fields:
                    if field not in parsed:
                        if field in ["identified_patterns", "knowledge_insights", "behavioral_trends", 
                                   "learning_opportunities", "long_term_implications"]:
                            parsed[field] = []
                        else:
                            parsed[field] = "Not specified"
                
                return parsed
            else:
                # Fallback parsing
                return {
                    "identified_patterns": [],
                    "knowledge_insights": [],
                    "behavioral_trends": [],
                    "learning_opportunities": [],
                    "pattern_confidence": "low",
                    "knowledge_relevance": "low",
                    "long_term_implications": [],
                    "learning_analysis": response[:200] + "..." if len(response) > 200 else response
                }
                
        except Exception as e:
            return {
                "identified_patterns": [],
                "knowledge_insights": [],
                "behavioral_trends": [],
                "learning_opportunities": [],
                "pattern_confidence": "low",
                "knowledge_relevance": "low",
                "long_term_implications": [],
                "learning_analysis": f"Error: {str(e)}"
            } 