"""
Base Agent Class for Multi-Agent System
"""

import json
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import asyncio

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

class BaseAgent(ABC):
    """Base class for all specialized agents."""
    
    def __init__(self, name: str, color: str, storage_path: str, llm_type: str = "quen"):
        self.name = name
        self.color = color
        self.storage_path = storage_path
        self.llm_type = llm_type  # "quen" or "gpt4o"
        
        # Initialize storage
        os.makedirs(storage_path, exist_ok=True)
        
        # Initialize console for colored output
        self.console = Console()
        
        # Initialize LLM client
        self.llm_client = self._initialize_llm()
        
        # Agent-specific data
        self.agent_data = {}
        self.load_agent_data()
    
    def _initialize_llm(self):
        """Initialize the appropriate LLM client."""
        if self.llm_type == "quen":
            from quen_client import QuenClient
            return QuenClient()
        elif self.llm_type == "gpt4o":
            from openai_client import OpenAIClient
            return OpenAIClient()
        else:
            raise ValueError(f"Unsupported LLM type: {self.llm_type}")
    
    def get_storage_file(self, filename: str) -> str:
        """Get full path for storage file."""
        return os.path.join(self.storage_path, filename)
    
    def load_agent_data(self):
        """Load agent-specific data from storage."""
        data_file = self.get_storage_file("agent_data.json")
        if os.path.exists(data_file):
            try:
                with open(data_file, 'r') as f:
                    self.agent_data = json.load(f)
            except Exception as e:
                logging.error(f"Failed to load agent data for {self.name}: {e}")
                self.agent_data = {}
        else:
            self.agent_data = {}
    
    def save_agent_data(self):
        """Save agent-specific data to storage."""
        data_file = self.get_storage_file("agent_data.json")
        try:
            with open(data_file, 'w') as f:
                json.dump(self.agent_data, f, indent=2)
        except Exception as e:
            logging.error(f"Failed to save agent data for {self.name}: {e}")
    
    def log_analysis(self, analysis_result: Dict[str, Any]):
        """Log agent analysis with colored output."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Create colored text
        text = Text()
        text.append(f"{self.color} {self.name} Analysis ({timestamp})\n", style="bold")
        
        # Add analysis details
        for key, value in analysis_result.items():
            if key != "raw_response":
                text.append(f"   {key}: {value}\n", style="white")
        
        # Create panel
        panel = Panel(
            text,
            title=f"{self.color} {self.name}",
            border_style=self._get_border_color(),
            padding=(1, 2)
        )
        
        self.console.print(panel)
        
        # Also log to file
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "analysis": analysis_result
        }
        
        log_file = self.get_storage_file("analysis_log.jsonl")
        try:
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            logging.error(f"Failed to log analysis for {self.name}: {e}")
    
    def _get_border_color(self) -> str:
        """Get border color based on agent color."""
        color_map = {
            "🔵": "blue",
            "🟡": "yellow", 
            "🟢": "green",
            "🟣": "magenta",
            "🔴": "red"
        }
        return color_map.get(self.color, "white")
    
    @abstractmethod
    def get_analysis_prompt(self, conversation_context: str) -> str:
        """Get agent-specific analysis prompt."""
        pass
    
    @abstractmethod
    def parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse agent-specific analysis response."""
        pass
    
    async def analyze(self, conversation_context: str, session_id: str) -> Dict[str, Any]:
        """Perform agent-specific analysis."""
        try:
            # Get agent-specific prompt
            prompt = self.get_analysis_prompt(conversation_context)
            
            # Get LLM response
            if self.llm_type == "quen":
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.llm_client.get_response,
                        session_id=f"{session_id}_{self.name.lower()}",
                        conversation_context=prompt,
                        is_incomplete=False
                    ),
                    timeout=30.0
                )
                raw_response = response.response
            else:
                # For GPT-4o
                response = await self.llm_client.generate_response(prompt)
                raw_response = response
            
            # Parse agent-specific response
            analysis_result = self.parse_analysis_response(raw_response)
            analysis_result["raw_response"] = raw_response
            analysis_result["agent"] = self.name
            analysis_result["timestamp"] = datetime.now().isoformat()
            
            # Log the analysis
            self.log_analysis(analysis_result)
            
            # Update agent data
            self._update_agent_data(analysis_result, session_id)
            
            return analysis_result
            
        except Exception as e:
            error_result = {
                "error": str(e),
                "agent": self.name,
                "timestamp": datetime.now().isoformat()
            }
            self.console.print(f"❌ {self.color} {self.name} Error: {e}", style="red")
            return error_result
    
    def _update_agent_data(self, analysis_result: Dict[str, Any], session_id: str):
        """Update agent-specific data with new analysis."""
        if "session_history" not in self.agent_data:
            self.agent_data["session_history"] = {}
        
        if session_id not in self.agent_data["session_history"]:
            self.agent_data["session_history"][session_id] = []
        
        self.agent_data["session_history"][session_id].append(analysis_result)
        
        # Keep only last 10 analyses per session
        if len(self.agent_data["session_history"][session_id]) > 10:
            self.agent_data["session_history"][session_id] = \
                self.agent_data["session_history"][session_id][-10:]
        
        self.save_agent_data() 