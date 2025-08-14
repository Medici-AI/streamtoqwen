"""
OpenAI Client for GPT-4o Integration
"""

import os
import logging
from typing import Optional
import asyncio

logger = logging.getLogger(__name__)

class OpenAIClient:
    """Client for OpenAI GPT-4o integration."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("No OpenAI API key provided. Using mock responses.")
            self.use_mock = True
        else:
            self.use_mock = False
            try:
                import openai
                self.client = openai.AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                logger.error("OpenAI library not installed. Using mock responses.")
                self.use_mock = True
    
    async def generate_response(self, prompt: str) -> str:
        """Generate response using GPT-4o."""
        if self.use_mock:
            return self._generate_mock_response(prompt)
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are an expert AI assistant providing strategic analysis and insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._generate_mock_response(prompt)
    
    def _generate_mock_response(self, prompt: str) -> str:
        """Generate mock response for testing."""
        if "strategic" in prompt.lower():
            return """
{
    "strategic_approach": "Proactive rate comparison and pre-approval process",
    "business_opportunities": ["Rate optimization", "Customer retention", "Cross-selling"],
    "risk_factors": ["Rate fluctuations", "Customer indecision"],
    "competitive_advantages": ["Quick response time", "Personalized service"],
    "value_proposition": "Competitive rates with excellent customer service",
    "next_strategic_steps": ["Present current rates", "Start pre-approval process"],
    "strategy_confidence": "high",
    "strategy_analysis": "Customer shows clear intent for refinancing with specific rate awareness. Recommend immediate rate comparison and streamlined pre-approval process."
}
"""
        elif "learning" in prompt.lower():
            return """
{
    "identified_patterns": ["Rate-conscious customers prefer quick comparisons", "Specific loan details indicate serious intent"],
    "knowledge_insights": ["Customers with specific loan amounts are more likely to proceed"],
    "behavioral_trends": ["Customers provide detailed information when serious about refinancing"],
    "learning_opportunities": ["Track conversion rates for detailed vs vague inquiries"],
    "pattern_confidence": "high",
    "knowledge_relevance": "high",
    "long_term_implications": ["Focus on customers with specific loan details", "Streamline rate comparison process"],
    "learning_analysis": "Customer behavior shows clear patterns of serious intent when specific loan details are provided."
}
"""
        else:
            return """
{
    "analysis": "Mock analysis response",
    "confidence": "medium",
    "insights": ["Mock insight 1", "Mock insight 2"]
}
""" 