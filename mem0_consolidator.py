"""
Mem0 Consolidator - Intelligent memory extraction and consolidation
"""

import json
import os
from datetime import datetime
from typing import Dict, Any, List
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

class Mem0Consolidator:
    """Intelligent memory extraction and consolidation from all agents."""
    
    def __init__(self):
        self.console = Console()
        self.consolidation_path = "data/mem0_consolidation"
        os.makedirs(self.consolidation_path, exist_ok=True)
    
    def extract_agent_memories(self, agent_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract relevant memories from all agent results."""
        memories = {
            "intent_memories": [],
            "strategy_memories": [],
            "sentiment_memories": [],
            "learning_memories": [],
            "decision_memories": [],
            "cross_agent_insights": []
        }
        
        for result in agent_results:
            agent_name = result.get("agent", "unknown")
            
            if "Intent Agent" in agent_name:
                memories["intent_memories"].append({
                    "primary_intent": result.get("primary_intent"),
                    "motivations": result.get("motivations"),
                    "intent_confidence": result.get("intent_confidence"),
                    "timestamp": result.get("timestamp")
                })
            
            elif "Strategy Agent" in agent_name:
                memories["strategy_memories"].append({
                    "strategic_approach": result.get("strategic_approach"),
                    "business_opportunities": result.get("business_opportunities", []),
                    "value_proposition": result.get("value_proposition"),
                    "strategy_confidence": result.get("strategy_confidence"),
                    "timestamp": result.get("timestamp")
                })
            
            elif "Sentiment Agent" in agent_name:
                memories["sentiment_memories"].append({
                    "primary_emotion": result.get("primary_emotion"),
                    "sentiment_score": result.get("sentiment_score"),
                    "emotional_intensity": result.get("emotional_intensity"),
                    "trust_level": result.get("trust_level"),
                    "timestamp": result.get("timestamp")
                })
            
            elif "Learning Agent" in agent_name:
                memories["learning_memories"].append({
                    "identified_patterns": result.get("identified_patterns", []),
                    "knowledge_insights": result.get("knowledge_insights", []),
                    "pattern_confidence": result.get("pattern_confidence"),
                    "timestamp": result.get("timestamp")
                })
            
            elif "Decision Agent" in agent_name:
                memories["decision_memories"].append({
                    "immediate_action": result.get("immediate_action"),
                    "action_priority": result.get("action_priority"),
                    "decision_confidence": result.get("decision_confidence"),
                    "timestamp": result.get("timestamp")
                })
        
        return memories
    
    def consolidate_insights(self, agent_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Consolidate insights from all agents."""
        memories = self.extract_agent_memories(agent_results)
        
        # Extract key insights
        intent_insights = self._extract_intent_insights(memories["intent_memories"])
        strategy_insights = self._extract_strategy_insights(memories["strategy_memories"])
        sentiment_insights = self._extract_sentiment_insights(memories["sentiment_memories"])
        learning_insights = self._extract_learning_insights(memories["learning_memories"])
        decision_insights = self._extract_decision_insights(memories["decision_memories"])
        
        # Cross-agent analysis
        cross_agent_insights = self._analyze_cross_agent_patterns(
            intent_insights, strategy_insights, sentiment_insights, 
            learning_insights, decision_insights
        )
        
        consolidation = {
            "consolidated_insights": {
                "intent": intent_insights,
                "strategy": strategy_insights,
                "sentiment": sentiment_insights,
                "learning": learning_insights,
                "decision": decision_insights,
                "cross_agent": cross_agent_insights
            },
            "overall_assessment": self._create_overall_assessment(
                intent_insights, strategy_insights, sentiment_insights,
                learning_insights, decision_insights, cross_agent_insights
            ),
            "strategic_recommendations": self._generate_strategic_recommendations(
                intent_insights, strategy_insights, sentiment_insights,
                learning_insights, decision_insights, cross_agent_insights
            ),
            "timestamp": datetime.now().isoformat()
        }
        
        # Save consolidation
        self._save_consolidation(consolidation)
        
        return consolidation
    
    def _extract_intent_insights(self, intent_memories: List[Dict]) -> Dict[str, Any]:
        """Extract key insights from intent memories."""
        if not intent_memories:
            return {"confidence": "low", "insights": []}
        
        latest = intent_memories[-1]
        return {
            "primary_intent": latest.get("primary_intent"),
            "motivations": latest.get("motivations"),
            "confidence": latest.get("intent_confidence", "low"),
            "insights": [memory.get("primary_intent") for memory in intent_memories if memory.get("primary_intent")]
        }
    
    def _extract_strategy_insights(self, strategy_memories: List[Dict]) -> Dict[str, Any]:
        """Extract key insights from strategy memories."""
        if not strategy_memories:
            return {"confidence": "low", "insights": []}
        
        latest = strategy_memories[-1]
        return {
            "strategic_approach": latest.get("strategic_approach"),
            "opportunities": latest.get("business_opportunities", []),
            "value_proposition": latest.get("value_proposition"),
            "confidence": latest.get("strategy_confidence", "low"),
            "insights": [memory.get("strategic_approach") for memory in strategy_memories if memory.get("strategic_approach")]
        }
    
    def _extract_sentiment_insights(self, sentiment_memories: List[Dict]) -> Dict[str, Any]:
        """Extract key insights from sentiment memories."""
        if not sentiment_memories:
            return {"confidence": "low", "insights": []}
        
        latest = sentiment_memories[-1]
        return {
            "primary_emotion": latest.get("primary_emotion"),
            "sentiment_score": latest.get("sentiment_score"),
            "emotional_intensity": latest.get("emotional_intensity"),
            "trust_level": latest.get("trust_level"),
            "confidence": "medium",  # Sentiment analysis confidence
            "insights": [memory.get("primary_emotion") for memory in sentiment_memories if memory.get("primary_emotion")]
        }
    
    def _extract_learning_insights(self, learning_memories: List[Dict]) -> Dict[str, Any]:
        """Extract key insights from learning memories."""
        if not learning_memories:
            return {"confidence": "low", "insights": []}
        
        latest = learning_memories[-1]
        return {
            "patterns": latest.get("identified_patterns", []),
            "knowledge": latest.get("knowledge_insights", []),
            "confidence": latest.get("pattern_confidence", "low"),
            "insights": latest.get("identified_patterns", [])
        }
    
    def _extract_decision_insights(self, decision_memories: List[Dict]) -> Dict[str, Any]:
        """Extract key insights from decision memories."""
        if not decision_memories:
            return {"confidence": "low", "insights": []}
        
        latest = decision_memories[-1]
        return {
            "immediate_action": latest.get("immediate_action"),
            "priority": latest.get("action_priority"),
            "confidence": latest.get("decision_confidence", "low"),
            "insights": [memory.get("immediate_action") for memory in decision_memories if memory.get("immediate_action")]
        }
    
    def _analyze_cross_agent_patterns(self, intent: Dict, strategy: Dict, 
                                    sentiment: Dict, learning: Dict, decision: Dict) -> Dict[str, Any]:
        """Analyze patterns across all agents."""
        patterns = {
            "high_confidence_alignment": [],
            "conflicting_insights": [],
            "synergistic_opportunities": [],
            "risk_indicators": []
        }
        
        # Check for high confidence alignments
        if intent.get("confidence") == "high" and strategy.get("confidence") == "high":
            patterns["high_confidence_alignment"].append("Intent and Strategy aligned")
        
        if sentiment.get("sentiment_score") == "positive" and intent.get("confidence") == "high":
            patterns["synergistic_opportunities"].append("Positive sentiment with clear intent")
        
        # Check for conflicts
        if sentiment.get("sentiment_score") == "negative" and intent.get("confidence") == "high":
            patterns["conflicting_insights"].append("Clear intent but negative sentiment")
        
        # Check for risks
        if decision.get("priority") == "high" and sentiment.get("trust_level") == "low":
            patterns["risk_indicators"].append("High priority action with low trust")
        
        return patterns
    
    def _create_overall_assessment(self, intent: Dict, strategy: Dict, 
                                 sentiment: Dict, learning: Dict, decision: Dict, 
                                 cross_agent: Dict) -> Dict[str, Any]:
        """Create overall assessment from all insights."""
        return {
            "overall_confidence": self._calculate_overall_confidence(intent, strategy, sentiment, learning, decision),
            "key_insights": [
                intent.get("primary_intent"),
                strategy.get("strategic_approach"),
                sentiment.get("primary_emotion"),
                decision.get("immediate_action")
            ],
            "risk_level": self._assess_risk_level(sentiment, decision, cross_agent),
            "opportunity_level": self._assess_opportunity_level(intent, strategy, sentiment),
            "recommended_focus": self._determine_recommended_focus(intent, strategy, sentiment, decision)
        }
    
    def _calculate_overall_confidence(self, intent: Dict, strategy: Dict, 
                                    sentiment: Dict, learning: Dict, decision: Dict) -> str:
        """Calculate overall confidence level."""
        confidences = [
            intent.get("confidence", "low"),
            strategy.get("confidence", "low"),
            learning.get("confidence", "low"),
            decision.get("confidence", "low")
        ]
        
        high_count = confidences.count("high")
        medium_count = confidences.count("medium")
        
        if high_count >= 3:
            return "high"
        elif high_count + medium_count >= 3:
            return "medium"
        else:
            return "low"
    
    def _assess_risk_level(self, sentiment: Dict, decision: Dict, cross_agent: Dict) -> str:
        """Assess overall risk level."""
        risk_indicators = len(cross_agent.get("risk_indicators", []))
        
        if risk_indicators >= 2:
            return "high"
        elif risk_indicators >= 1:
            return "medium"
        else:
            return "low"
    
    def _assess_opportunity_level(self, intent: Dict, strategy: Dict, sentiment: Dict) -> str:
        """Assess opportunity level."""
        positive_indicators = 0
        
        if intent.get("confidence") == "high":
            positive_indicators += 1
        if strategy.get("confidence") == "high":
            positive_indicators += 1
        if sentiment.get("sentiment_score") == "positive":
            positive_indicators += 1
        
        if positive_indicators >= 2:
            return "high"
        elif positive_indicators >= 1:
            return "medium"
        else:
            return "low"
    
    def _determine_recommended_focus(self, intent: Dict, strategy: Dict, 
                                   sentiment: Dict, decision: Dict) -> str:
        """Determine recommended focus area."""
        if decision.get("priority") == "high":
            return "immediate_action"
        elif intent.get("confidence") == "low":
            return "clarify_intent"
        elif sentiment.get("sentiment_score") == "negative":
            return "address_sentiment"
        elif strategy.get("confidence") == "low":
            return "develop_strategy"
        else:
            return "proceed_optimally"
    
    def _generate_strategic_recommendations(self, intent: Dict, strategy: Dict,
                                          sentiment: Dict, learning: Dict, 
                                          decision: Dict, cross_agent: Dict) -> List[str]:
        """Generate strategic recommendations."""
        recommendations = []
        
        # Immediate action recommendations
        if decision.get("immediate_action"):
            recommendations.append(f"Take immediate action: {decision.get('immediate_action')}")
        
        # Intent-based recommendations
        if intent.get("confidence") == "low":
            recommendations.append("Clarify customer intent through targeted questions")
        
        # Sentiment-based recommendations
        if sentiment.get("sentiment_score") == "negative":
            recommendations.append("Address customer concerns and build trust")
        
        # Strategy-based recommendations
        if strategy.get("strategic_approach"):
            recommendations.append(f"Follow strategic approach: {strategy.get('strategic_approach')}")
        
        # Learning-based recommendations
        if learning.get("patterns"):
            recommendations.append("Apply learned patterns to improve interaction")
        
        return recommendations
    
    def _save_consolidation(self, consolidation: Dict[str, Any]):
        """Save consolidation to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"consolidation_{timestamp}.json"
        filepath = os.path.join(self.consolidation_path, filename)
        
        try:
            with open(filepath, 'w') as f:
                json.dump(consolidation, f, indent=2)
        except Exception as e:
            print(f"Error saving consolidation: {e}")
    
    def display_consolidation(self, consolidation: Dict[str, Any]):
        """Display consolidation results with rich formatting."""
        # Create main panel
        text = f"""
🎯 Overall Assessment:
   Confidence: {consolidation['overall_assessment']['overall_confidence']}
   Risk Level: {consolidation['overall_assessment']['risk_level']}
   Opportunity Level: {consolidation['overall_assessment']['opportunity_level']}
   Recommended Focus: {consolidation['overall_assessment']['recommended_focus']}

📋 Strategic Recommendations:
"""
        
        for rec in consolidation['strategic_recommendations']:
            text += f"   • {rec}\n"
        
        text += f"\n🔄 Cross-Agent Patterns:"
        cross_agent = consolidation['consolidated_insights']['cross_agent']
        for pattern_type, patterns in cross_agent.items():
            if patterns:
                text += f"\n   {pattern_type}: {', '.join(patterns)}"
        
        panel = Panel(
            text,
            title="🧠 Mem0 Consolidation Results",
            border_style="cyan",
            padding=(1, 2)
        )
        
        self.console.print(panel) 