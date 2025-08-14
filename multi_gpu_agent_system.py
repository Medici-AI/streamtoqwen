#!/usr/bin/env python3
"""
Multi-GPU Agent System for RTX 4090
Distributes agents across GPUs and handles concurrent execution
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import torch
import json
import os

from multi_gpu_middleware import MultiGPUMiddleware
from agents.base_agent import BaseAgent
from agents.intent_agent import IntentAgent
from agents.sentiment_agent import SentimentAgent
from agents.strategy_agent import StrategyAgent
from agents.learning_agent import LearningAgent
from agents.decision_agent import DecisionAgent

logger = logging.getLogger(__name__)

class AgentType(Enum):
    INTENT = "intent"
    SENTIMENT = "sentiment"
    STRATEGY = "strategy"
    LEARNING = "learning"
    DECISION = "decision"

@dataclass
class AgentAllocation:
    """Agent allocation configuration."""
    agent_type: AgentType
    gpu_id: int
    memory_required: float  # GB
    priority: int
    is_active: bool = True

class MultiGPUAgentSystem:
    """Multi-GPU agent system for concurrent RM processing."""
    
    def __init__(self, num_gpus: int = 4, max_rms: int = 4):
        self.num_gpus = num_gpus
        self.max_rms = max_rms
        self.middleware = MultiGPUMiddleware(num_gpus=num_gpus)
        
        # Agent allocations per GPU
        self.agent_allocations: Dict[int, List[AgentAllocation]] = {}
        self.active_agents: Dict[str, BaseAgent] = {}
        self.rm_sessions: Dict[str, Dict[str, Any]] = {}
        
        # Performance tracking
        self.performance_metrics: List[Dict[str, Any]] = []
        self.is_running = False
        
        # Initialize agent allocations
        self._initialize_agent_allocations()
    
    def _initialize_agent_allocations(self):
        """Initialize agent allocations across GPUs."""
        # GPU 0: Intent Agent + RM Session 1
        self.agent_allocations[0] = [
            AgentAllocation(AgentType.INTENT, 0, 2.0, 1),
        ]
        
        # GPU 1: Sentiment Agent + RM Session 2
        self.agent_allocations[1] = [
            AgentAllocation(AgentType.SENTIMENT, 1, 2.0, 1),
        ]
        
        # GPU 2: Strategy Agent + RM Session 3
        self.agent_allocations[2] = [
            AgentAllocation(AgentType.STRATEGY, 2, 2.0, 1),
        ]
        
        # GPU 3: Learning Agent + RM Session 4
        self.agent_allocations[3] = [
            AgentAllocation(AgentType.LEARNING, 3, 2.0, 1),
        ]
        
        # Decision Agent can run on any GPU based on availability
        self.agent_allocations[0].append(AgentAllocation(AgentType.DECISION, 0, 1.5, 2))
    
    async def start(self):
        """Start the multi-GPU agent system."""
        logger.info(f"Starting Multi-GPU Agent System with {self.num_gpus} GPUs")
        self.is_running = True
        
        # Start middleware
        await self.middleware.start()
        
        # Initialize agents
        await self._initialize_agents()
        
        # Start monitoring
        asyncio.create_task(self._monitor_performance())
    
    async def stop(self):
        """Stop the multi-GPU agent system."""
        logger.info("Stopping Multi-GPU Agent System")
        self.is_running = False
        
        # Stop all agents
        for agent_id, agent in self.active_agents.items():
            try:
                await agent.cleanup()
            except Exception as e:
                logger.error(f"Error stopping agent {agent_id}: {e}")
        
        # Stop middleware
        await self.middleware.stop()
    
    async def _initialize_agents(self):
        """Initialize agents on their allocated GPUs."""
        for gpu_id, allocations in self.agent_allocations.items():
            for allocation in allocations:
                if allocation.is_active:
                    await self._create_agent(allocation)
    
    async def _create_agent(self, allocation: AgentAllocation):
        """Create and initialize an agent on the specified GPU."""
        try:
            # Set CUDA device for agent creation
            torch.cuda.set_device(allocation.gpu_id)
            
            # Create agent based on type
            agent = None
            if allocation.agent_type == AgentType.INTENT:
                agent = IntentAgent(
                    name="intent_agent",
                    color="🔵",
                    storage_path="data/intent_agent",
                    llm_type="quen"
                )
            elif allocation.agent_type == AgentType.SENTIMENT:
                agent = SentimentAgent(
                    name="sentiment_agent",
                    color="🟢",
                    storage_path="data/sentiment_agent",
                    llm_type="quen"
                )
            elif allocation.agent_type == AgentType.STRATEGY:
                agent = StrategyAgent(
                    name="strategy_agent",
                    color="🟡",
                    storage_path="data/strategy_agent",
                    llm_type="gpt4o"
                )
            elif allocation.agent_type == AgentType.LEARNING:
                agent = LearningAgent(
                    name="learning_agent",
                    color="🟣",
                    storage_path="data/learning_agent",
                    llm_type="gpt4o"
                )
            elif allocation.agent_type == AgentType.DECISION:
                agent = DecisionAgent(
                    name="decision_agent",
                    color="🔴",
                    storage_path="data/decision_agent",
                    llm_type="quen"
                )
            
            if agent:
                agent_id = f"{allocation.agent_type.value}_{allocation.gpu_id}"
                self.active_agents[agent_id] = agent
                logger.info(f"Created {allocation.agent_type.value} agent on GPU {allocation.gpu_id}")
            
        except Exception as e:
            logger.error(f"Error creating {allocation.agent_type.value} agent on GPU {allocation.gpu_id}: {e}")
    
    async def process_rm_session(self, session_id: str, conversation_context: str) -> Dict[str, Any]:
        """Process RM session with concurrent agent analysis."""
        try:
            start_time = time.time()
            
            # Check if we can handle another RM session
            if len(self.rm_sessions) >= self.max_rms:
                logger.warning(f"Maximum RM sessions ({self.max_rms}) reached")
                return {"error": "Maximum sessions reached"}
            
            # Add session to tracking
            self.rm_sessions[session_id] = {
                "start_time": start_time,
                "context": conversation_context,
                "status": "processing"
            }
            
            # Run concurrent agent analysis
            agent_tasks = []
            for agent_id, agent in self.active_agents.items():
                task = asyncio.create_task(
                    self._run_agent_analysis(agent_id, agent, session_id, conversation_context)
                )
                agent_tasks.append(task)
            
            # Wait for all agents to complete
            agent_results = await asyncio.gather(*agent_tasks, return_exceptions=True)
            
            # Process results
            analysis_results = {}
            for i, (agent_id, agent) in enumerate(self.active_agents.items()):
                if isinstance(agent_results[i], Exception):
                    logger.error(f"Agent {agent_id} failed: {agent_results[i]}")
                    analysis_results[agent_id] = {"error": str(agent_results[i])}
                else:
                    analysis_results[agent_id] = agent_results[i]
            
            # Update session status
            self.rm_sessions[session_id]["status"] = "completed"
            self.rm_sessions[session_id]["analysis_results"] = analysis_results
            self.rm_sessions[session_id]["processing_time"] = time.time() - start_time
            
            # Log performance metrics
            await self._log_performance_metrics(session_id, start_time, analysis_results)
            
            return {
                "session_id": session_id,
                "analysis_results": analysis_results,
                "processing_time": time.time() - start_time,
                "gpu_utilization": await self._get_gpu_utilization()
            }
            
        except Exception as e:
            logger.error(f"Error processing RM session {session_id}: {e}")
            return {"error": str(e)}
    
    async def _run_agent_analysis(self, agent_id: str, agent: BaseAgent, 
                                 session_id: str, conversation_context: str) -> Dict[str, Any]:
        """Run agent analysis on the allocated GPU."""
        try:
            # Get GPU allocation for this agent
            gpu_id = self._get_agent_gpu_id(agent_id)
            
            # Set CUDA device
            torch.cuda.set_device(gpu_id)
            
            # Run agent analysis
            result = await agent.analyze(conversation_context, session_id)
            
            # Add GPU information to result
            result["gpu_id"] = gpu_id
            result["agent_id"] = agent_id
            
            return result
            
        except Exception as e:
            logger.error(f"Error in agent analysis for {agent_id}: {e}")
            return {"error": str(e)}
    
    def _get_agent_gpu_id(self, agent_id: str) -> int:
        """Get the GPU ID for a specific agent."""
        for gpu_id, allocations in self.agent_allocations.items():
            for allocation in allocations:
                if f"{allocation.agent_type.value}_{allocation.gpu_id}" == agent_id:
                    return allocation.gpu_id
        return 0  # Default to GPU 0
    
    async def _get_gpu_utilization(self) -> Dict[int, float]:
        """Get GPU utilization for all GPUs."""
        try:
            summary = await self.middleware.get_performance_summary()
            return summary.get("gpu_states", {})
        except Exception as e:
            logger.error(f"Error getting GPU utilization: {e}")
            return {}
    
    async def _log_performance_metrics(self, session_id: str, start_time: float, 
                                     analysis_results: Dict[str, Any]):
        """Log performance metrics for the session."""
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Get GPU performance summary
        gpu_summary = await self.middleware.get_performance_summary()
        
        metrics = {
            "session_id": session_id,
            "processing_time": processing_time,
            "num_agents": len(analysis_results),
            "gpu_summary": gpu_summary,
            "timestamp": end_time
        }
        
        self.performance_metrics.append(metrics)
        
        # Keep only last 1000 metrics
        if len(self.performance_metrics) > 1000:
            self.performance_metrics = self.performance_metrics[-1000:]
    
    async def _monitor_performance(self):
        """Monitor system performance."""
        while self.is_running:
            try:
                # Get current performance summary
                summary = await self.middleware.get_performance_summary()
                
                # Log performance every 30 seconds
                if len(self.performance_metrics) % 30 == 0:
                    logger.info(f"Performance Summary: {summary}")
                
                await asyncio.sleep(1.0)
                
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(5.0)
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get current system status."""
        try:
            # Get middleware status
            middleware_summary = await self.middleware.get_performance_summary()
            health_status = await self.middleware.health_check()
            
            # Get active sessions
            active_sessions = {
                session_id: {
                    "status": session_data["status"],
                    "processing_time": session_data.get("processing_time", 0),
                    "start_time": session_data["start_time"]
                }
                for session_id, session_data in self.rm_sessions.items()
            }
            
            # Get agent status
            agent_status = {}
            for agent_id, agent in self.active_agents.items():
                gpu_id = self._get_agent_gpu_id(agent_id)
                agent_status[agent_id] = {
                    "gpu_id": gpu_id,
                    "status": "active",
                    "type": agent_id.split("_")[0]
                }
            
            return {
                "system_status": "running" if self.is_running else "stopped",
                "active_sessions": len(self.rm_sessions),
                "max_sessions": self.max_rms,
                "active_agents": len(self.active_agents),
                "gpu_summary": middleware_summary,
                "health_status": health_status,
                "sessions": active_sessions,
                "agents": agent_status,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}
    
    async def cleanup_session(self, session_id: str):
        """Clean up resources for a specific session."""
        if session_id in self.rm_sessions:
            del self.rm_sessions[session_id]
            logger.info(f"Cleaned up session {session_id}")
    
    async def get_performance_report(self) -> Dict[str, Any]:
        """Get detailed performance report."""
        if not self.performance_metrics:
            return {"error": "No performance metrics available"}
        
        # Calculate averages
        total_sessions = len(self.performance_metrics)
        avg_processing_time = sum(m["processing_time"] for m in self.performance_metrics) / total_sessions
        avg_agents_per_session = sum(m["num_agents"] for m in self.performance_metrics) / total_sessions
        
        # Get latest GPU summary
        latest_gpu_summary = self.performance_metrics[-1]["gpu_summary"] if self.performance_metrics else {}
        
        return {
            "total_sessions_processed": total_sessions,
            "average_processing_time": avg_processing_time,
            "average_agents_per_session": avg_agents_per_session,
            "latest_gpu_summary": latest_gpu_summary,
            "performance_metrics": self.performance_metrics[-10:],  # Last 10 metrics
            "timestamp": time.time()
        }

# Example usage
async def main():
    """Example usage of the Multi-GPU Agent System."""
    agent_system = MultiGPUAgentSystem(num_gpus=4, max_rms=4)
    
    try:
        await agent_system.start()
        
        # Example: Process RM session
        conversation_context = """
        Customer: Hi, I'm interested in refinancing my mortgage.
        RM: Hello! I'd be happy to help you with that. What's your current situation?
        Customer: I have a 30-year fixed rate at 4.5% and I'm looking to lower my monthly payments.
        """
        
        result = await agent_system.process_rm_session("session_001", conversation_context)
        print(f"Session processing result: {result}")
        
        # Get system status
        status = await agent_system.get_system_status()
        print(f"System status: {status}")
        
        # Get performance report
        report = await agent_system.get_performance_report()
        print(f"Performance report: {report}")
        
        await asyncio.sleep(5)  # Run for 5 seconds
        
    finally:
        await agent_system.stop()

if __name__ == "__main__":
    asyncio.run(main()) 