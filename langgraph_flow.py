"""
LangGraph Flow for Multi-Agent Conversational AI System
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from agents import IntentAgent, StrategyAgent, SentimentAgent, LearningAgent, DecisionAgent
from mem0_consolidator import Mem0Consolidator

class MultiAgentFlow:
    """LangGraph-based flow for multi-agent conversation analysis."""
    
    def __init__(self):
        self.console = Console()
        
        # Initialize all agents
        self.intent_agent = IntentAgent()
        self.strategy_agent = StrategyAgent()
        self.sentiment_agent = SentimentAgent()
        self.learning_agent = LearningAgent()
        self.decision_agent = DecisionAgent()
        
        # Initialize Mem0 consolidator
        self.mem0_consolidator = Mem0Consolidator()
        
        # Flow state
        self.session_id = None
        self.conversation_context = None
    
    async def execute_flow(self, conversation_context: str, session_id: str) -> Dict[str, Any]:
        """Execute the complete multi-agent flow."""
        self.session_id = session_id
        self.conversation_context = conversation_context
        
        self.console.print(f"\n🚀 Starting Multi-Agent Analysis Flow", style="bold cyan")
        self.console.print(f"📝 Session: {session_id}", style="cyan")
        self.console.print(f"⏰ Timestamp: {datetime.now().strftime('%H:%M:%S')}", style="cyan")
        
        # Step 1: Parallel Agent Execution
        agent_results = await self._execute_parallel_agents()
        
        # Step 2: Mem0 Consolidation
        consolidation = self.mem0_consolidator.consolidate_insights(agent_results)
        
        # Step 3: Display Results
        self._display_flow_results(agent_results, consolidation)
        
        return {
            "agent_results": agent_results,
            "consolidation": consolidation,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _execute_parallel_agents(self) -> List[Dict[str, Any]]:
        """Execute all agents in parallel."""
        self.console.print(f"\n🔵🟡🟢🟣🔴 Executing Agents in Parallel...", style="bold")
        
        # Create tasks for all agents
        tasks = [
            asyncio.create_task(self.intent_agent.analyze(self.conversation_context, self.session_id)),
            asyncio.create_task(self.strategy_agent.analyze(self.conversation_context, self.session_id)),
            asyncio.create_task(self.sentiment_agent.analyze(self.conversation_context, self.session_id)),
            asyncio.create_task(self.learning_agent.analyze(self.conversation_context, self.session_id)),
            asyncio.create_task(self.decision_agent.analyze(self.conversation_context, self.session_id))
        ]
        
        # Wait for all agents to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        agent_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.console.print(f"❌ Agent {i+1} failed: {result}", style="red")
                agent_results.append({
                    "agent": f"Agent_{i+1}",
                    "error": str(result),
                    "timestamp": datetime.now().isoformat()
                })
            else:
                agent_results.append(result)
        
        return agent_results
    
    def _display_flow_results(self, agent_results: List[Dict[str, Any]], consolidation: Dict[str, Any]):
        """Display comprehensive flow results."""
        self.console.print(f"\n📊 Multi-Agent Analysis Complete", style="bold green")
        
        # Display agent summary
        self._display_agent_summary(agent_results)
        
        # Display consolidation results
        self.mem0_consolidator.display_consolidation(consolidation)
        
        # Display final recommendations
        self._display_final_recommendations(consolidation)
    
    def _display_agent_summary(self, agent_results: List[Dict[str, Any]]):
        """Display summary of all agent results."""
        table = Table(title="🤖 Agent Analysis Summary")
        table.add_column("Agent", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Key Insight", style="yellow")
        table.add_column("Confidence", style="magenta")
        
        for result in agent_results:
            agent_name = result.get("agent", "Unknown")
            status = "✅ Success" if "error" not in result else "❌ Error"
            
            # Extract key insight based on agent type
            key_insight = self._extract_key_insight(result)
            confidence = self._extract_confidence(result)
            
            table.add_row(agent_name, status, key_insight, confidence)
        
        self.console.print(table)
    
    def _extract_key_insight(self, result: Dict[str, Any]) -> str:
        """Extract key insight from agent result."""
        if "error" in result:
            return "Error occurred"
        
        agent_name = result.get("agent", "")
        
        if "Intent" in agent_name:
            return result.get("primary_intent", "No intent identified")
        elif "Strategy" in agent_name:
            return result.get("strategic_approach", "No strategy identified")
        elif "Sentiment" in agent_name:
            return result.get("primary_emotion", "No emotion identified")
        elif "Learning" in agent_name:
            patterns = result.get("identified_patterns", [])
            return patterns[0] if patterns else "No patterns identified"
        elif "Decision" in agent_name:
            return result.get("immediate_action", "No action identified")
        else:
            return "Unknown agent"
    
    def _extract_confidence(self, result: Dict[str, Any]) -> str:
        """Extract confidence from agent result."""
        if "error" in result:
            return "N/A"
        
        agent_name = result.get("agent", "")
        
        if "Intent" in agent_name:
            return result.get("intent_confidence", "low")
        elif "Strategy" in agent_name:
            return result.get("strategy_confidence", "low")
        elif "Sentiment" in agent_name:
            return "medium"  # Sentiment analysis confidence
        elif "Learning" in agent_name:
            return result.get("pattern_confidence", "low")
        elif "Decision" in agent_name:
            return result.get("decision_confidence", "low")
        else:
            return "unknown"
    
    def _display_final_recommendations(self, consolidation: Dict[str, Any]):
        """Display final strategic recommendations."""
        assessment = consolidation.get("overall_assessment", {})
        recommendations = consolidation.get("strategic_recommendations", [])
        
        text = f"""
🎯 Final Strategic Assessment:
   Overall Confidence: {assessment.get('overall_confidence', 'low')}
   Risk Level: {assessment.get('risk_level', 'low')}
   Opportunity Level: {assessment.get('opportunity_level', 'low')}
   Recommended Focus: {assessment.get('recommended_focus', 'proceed_optimally')}

📋 Key Recommendations:
"""
        
        for i, rec in enumerate(recommendations[:5], 1):  # Show top 5
            text += f"   {i}. {rec}\n"
        
        if len(recommendations) > 5:
            text += f"   ... and {len(recommendations) - 5} more recommendations\n"
        
        panel = Panel(
            text,
            title="🎯 Final Strategic Recommendations",
            border_style="green",
            padding=(1, 2)
        )
        
        self.console.print(panel)
    
    async def test_flow(self):
        """Test the flow with sample conversation."""
        test_conversation = """
customer: Hi, I'm interested in refinancing my home loan. The current rate is 6.5% and I want to see if I can get a better deal.
rm: I understand you're looking to refinance. Let me check our current rates for you. What's your current loan amount and remaining term?
customer: I have about $300,000 remaining and 15 years left on a 30-year mortgage.
rm: Perfect. Let me pull up our current refinancing options for you.
"""
        
        test_session = f"test_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.console.print(f"\n🧪 Testing Multi-Agent Flow", style="bold yellow")
        self.console.print(f"📝 Test conversation loaded", style="yellow")
        
        result = await self.execute_flow(test_conversation, test_session)
        
        return result

# Convenience function for easy usage
async def run_multi_agent_analysis(conversation_context: str, session_id: str) -> Dict[str, Any]:
    """Run multi-agent analysis with the given conversation context."""
    flow = MultiAgentFlow()
    return await flow.execute_flow(conversation_context, session_id)

if __name__ == "__main__":
    # Test the flow
    asyncio.run(MultiAgentFlow().test_flow()) 