#!/usr/bin/env python3
"""
Multi-GPU RTX 4090 Performance Analysis
Provides detailed performance metrics and comparisons
"""

import asyncio
import time
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from multi_gpu_middleware import MultiGPUMiddleware
from multi_gpu_agent_system import MultiGPUAgentSystem

console = Console()

@dataclass
class PerformanceMetrics:
    """Performance metrics for multi-GPU system."""
    ttft: float  # Time to First Token (ms)
    tpot: float  # Time per Output Token (ms)
    tps: float   # Tokens per Second
    otps: float  # Output Tokens per Second
    gpu_utilization: float  # Average GPU utilization (%)
    memory_utilization: float  # Average memory utilization (%)
    concurrent_rms: int  # Number of concurrent RMs
    processing_time: float  # Total processing time (s)
    throughput: float  # Sessions per minute

class MultiGPUPerformanceAnalyzer:
    """Performance analyzer for multi-GPU RTX 4090 system."""
    
    def __init__(self, num_gpus: int = 4):
        self.num_gpus = num_gpus
        self.middleware = MultiGPUMiddleware(num_gpus=num_gpus)
        self.agent_system = MultiGPUAgentSystem(num_gpus=num_gpus, max_rms=4)
        self.performance_history: List[PerformanceMetrics] = []
    
    async def run_performance_test(self, test_duration: int = 300) -> Dict[str, Any]:
        """Run comprehensive performance test."""
        console.print(f"🚀 Starting Multi-GPU Performance Test ({test_duration}s)")
        
        try:
            # Start systems
            await self.middleware.start()
            await self.agent_system.start()
            
            # Test scenarios
            test_results = {}
            
            # Test 1: Single RM session
            console.print("\n📊 Test 1: Single RM Session")
            single_rm_result = await self._test_single_rm()
            test_results["single_rm"] = single_rm_result
            
            # Test 2: Multiple concurrent RMs
            console.print("\n📊 Test 2: Multiple Concurrent RMs")
            concurrent_rm_result = await self._test_concurrent_rms()
            test_results["concurrent_rms"] = concurrent_rm_result
            
            # Test 3: Sustained load
            console.print("\n📊 Test 3: Sustained Load Test")
            sustained_result = await self._test_sustained_load(test_duration)
            test_results["sustained_load"] = sustained_result
            
            # Test 4: GPU stress test
            console.print("\n📊 Test 4: GPU Stress Test")
            stress_result = await self._test_gpu_stress()
            test_results["gpu_stress"] = stress_result
            
            # Generate comprehensive report
            report = await self._generate_performance_report(test_results)
            
            return report
            
        finally:
            await self.agent_system.stop()
            await self.middleware.stop()
    
    async def _test_single_rm(self) -> Dict[str, Any]:
        """Test single RM session performance."""
        conversation_context = """
        Customer: Hi, I'm interested in refinancing my mortgage.
        RM: Hello! I'd be happy to help you with that. What's your current situation?
        Customer: I have a 30-year fixed rate at 4.5% and I'm looking to lower my monthly payments.
        RM: I understand. Let me help you explore your options. What's your current loan balance?
        Customer: It's about $350,000 and I've been paying for 5 years.
        """
        
        start_time = time.time()
        result = await self.agent_system.process_rm_session("test_single_001", conversation_context)
        processing_time = time.time() - start_time
        
        # Get GPU metrics
        gpu_summary = await self.middleware.get_performance_summary()
        
        return {
            "processing_time": processing_time,
            "gpu_utilization": gpu_summary.get("average_utilization_percent", 0),
            "memory_utilization": gpu_summary.get("memory_utilization_percent", 0),
            "result": result
        }
    
    async def _test_concurrent_rms(self) -> Dict[str, Any]:
        """Test multiple concurrent RM sessions."""
        conversations = [
            ("test_concurrent_001", """
            Customer: I need help with investment planning.
            RM: Of course! What are your financial goals?
            Customer: I want to save for retirement and my children's education.
            """),
            ("test_concurrent_002", """
            Customer: I'm looking for a business loan.
            RM: I can help with that. What type of business do you have?
            Customer: I run a small restaurant and need to expand.
            """),
            ("test_concurrent_003", """
            Customer: Can you help me with insurance options?
            RM: Absolutely! What type of coverage are you looking for?
            Customer: I need life insurance and health coverage.
            """),
            ("test_concurrent_004", """
            Customer: I want to open a savings account.
            RM: Great choice! What's your savings goal?
            Customer: I want to save $10,000 for emergencies.
            """)
        ]
        
        start_time = time.time()
        
        # Process all conversations concurrently
        tasks = []
        for session_id, context in conversations:
            task = self.agent_system.process_rm_session(session_id, context)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # Get GPU metrics
        gpu_summary = await self.middleware.get_performance_summary()
        
        return {
            "total_time": total_time,
            "concurrent_sessions": len(conversations),
            "average_time_per_session": total_time / len(conversations),
            "gpu_utilization": gpu_summary.get("average_utilization_percent", 0),
            "memory_utilization": gpu_summary.get("memory_utilization_percent", 0),
            "results": results
        }
    
    async def _test_sustained_load(self, duration: int) -> Dict[str, Any]:
        """Test sustained load over specified duration."""
        console.print(f"Running sustained load test for {duration} seconds...")
        
        start_time = time.time()
        session_count = 0
        total_processing_time = 0
        
        while time.time() - start_time < duration:
            session_id = f"sustained_{session_count:03d}"
            conversation_context = f"""
            Customer: This is test session {session_count}.
            RM: I understand you're testing the system.
            Customer: Yes, I want to see how it performs under load.
            RM: Let me analyze your requirements and provide recommendations.
            """
            
            session_start = time.time()
            result = await self.agent_system.process_rm_session(session_id, conversation_context)
            session_time = time.time() - session_start
            
            total_processing_time += session_time
            session_count += 1
            
            # Clean up session
            await self.agent_system.cleanup_session(session_id)
            
            # Small delay between sessions
            await asyncio.sleep(1.0)
        
        # Get final GPU metrics
        gpu_summary = await self.middleware.get_performance_summary()
        
        return {
            "duration": duration,
            "sessions_processed": session_count,
            "average_processing_time": total_processing_time / session_count if session_count > 0 else 0,
            "throughput": session_count / (duration / 60),  # sessions per minute
            "gpu_utilization": gpu_summary.get("average_utilization_percent", 0),
            "memory_utilization": gpu_summary.get("memory_utilization_percent", 0)
        }
    
    async def _test_gpu_stress(self) -> Dict[str, Any]:
        """Test GPU stress with maximum concurrent load."""
        console.print("Running GPU stress test...")
        
        # Create maximum concurrent sessions
        max_sessions = 4
        conversations = []
        
        for i in range(max_sessions):
            session_id = f"stress_{i:02d}"
            conversation_context = f"""
            Customer: This is stress test session {i}.
            RM: I'm here to help with your financial needs.
            Customer: I need comprehensive financial planning.
            RM: Let me analyze your situation and provide detailed recommendations.
            Customer: I want to optimize my investment portfolio.
            RM: I'll help you create a personalized investment strategy.
            """
            conversations.append((session_id, conversation_context))
        
        start_time = time.time()
        
        # Process all sessions concurrently
        tasks = []
        for session_id, context in conversations:
            task = self.agent_system.process_rm_session(session_id, context)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = time.time() - start_time
        
        # Get GPU metrics during stress
        gpu_summary = await self.middleware.get_performance_summary()
        health_status = await self.middleware.health_check()
        
        return {
            "max_concurrent_sessions": max_sessions,
            "total_processing_time": total_time,
            "average_time_per_session": total_time / max_sessions,
            "gpu_utilization": gpu_summary.get("average_utilization_percent", 0),
            "memory_utilization": gpu_summary.get("memory_utilization_percent", 0),
            "gpu_health": health_status,
            "results": results
        }
    
    async def _generate_performance_report(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        
        # Calculate overall metrics
        single_rm = test_results.get("single_rm", {})
        concurrent_rms = test_results.get("concurrent_rms", {})
        sustained = test_results.get("sustained_load", {})
        stress = test_results.get("gpu_stress", {})
        
        # Performance summary
        performance_summary = {
            "single_rm_processing_time": single_rm.get("processing_time", 0),
            "concurrent_rm_processing_time": concurrent_rms.get("total_time", 0),
            "sustained_throughput": sustained.get("throughput", 0),
            "stress_test_utilization": stress.get("gpu_utilization", 0),
            "average_gpu_utilization": (
                single_rm.get("gpu_utilization", 0) +
                concurrent_rms.get("gpu_utilization", 0) +
                sustained.get("gpu_utilization", 0) +
                stress.get("gpu_utilization", 0)
            ) / 4,
            "average_memory_utilization": (
                single_rm.get("memory_utilization", 0) +
                concurrent_rms.get("memory_utilization", 0) +
                sustained.get("memory_utilization", 0) +
                stress.get("memory_utilization", 0)
            ) / 4
        }
        
        # Performance comparison with A100
        a100_comparison = {
            "ttft_ratio": performance_summary["single_rm_processing_time"] / 0.5,  # A100: 500ms
            "throughput_ratio": performance_summary["sustained_throughput"] / 60,  # A100: 60 sessions/min
            "utilization_ratio": performance_summary["average_gpu_utilization"] / 85,  # A100: 85%
            "cost_efficiency": 8.6 / 300,  # RTX 4090 cost vs A100 cost
        }
        
        return {
            "test_results": test_results,
            "performance_summary": performance_summary,
            "a100_comparison": a100_comparison,
            "recommendations": await self._generate_recommendations(performance_summary),
            "timestamp": time.time()
        }
    
    async def _generate_recommendations(self, performance_summary: Dict[str, Any]) -> List[str]:
        """Generate performance recommendations."""
        recommendations = []
        
        # Analyze processing time
        if performance_summary["single_rm_processing_time"] > 2.0:
            recommendations.append("Consider optimizing model quantization for faster inference")
        
        # Analyze throughput
        if performance_summary["sustained_throughput"] < 30:
            recommendations.append("Increase batch processing or reduce model complexity")
        
        # Analyze GPU utilization
        if performance_summary["average_gpu_utilization"] < 70:
            recommendations.append("GPU utilization is low - consider increasing concurrent sessions")
        elif performance_summary["average_gpu_utilization"] > 95:
            recommendations.append("GPU utilization is very high - consider adding more GPUs")
        
        # Analyze memory utilization
        if performance_summary["average_memory_utilization"] > 90:
            recommendations.append("Memory utilization is high - consider memory optimization techniques")
        
        return recommendations
    
    def print_performance_report(self, report: Dict[str, Any]):
        """Print formatted performance report."""
        console.print("\n" + "="*80)
        console.print("🎮 MULTI-GPU RTX 4090 PERFORMANCE REPORT", style="bold cyan")
        console.print("="*80)
        
        # Performance Summary Table
        summary = report.get("performance_summary", {})
        table = Table(title="Performance Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")
        table.add_column("Target", style="green")
        table.add_column("Status", style="magenta")
        
        table.add_row(
            "Single RM Processing Time",
            f"{summary.get('single_rm_processing_time', 0):.2f}s",
            "<2.0s",
            "✅" if summary.get('single_rm_processing_time', 0) < 2.0 else "⚠️"
        )
        
        table.add_row(
            "Sustained Throughput",
            f"{summary.get('sustained_throughput', 0):.1f} sessions/min",
            ">30 sessions/min",
            "✅" if summary.get('sustained_throughput', 0) > 30 else "⚠️"
        )
        
        table.add_row(
            "Average GPU Utilization",
            f"{summary.get('average_gpu_utilization', 0):.1f}%",
            "70-95%",
            "✅" if 70 <= summary.get('average_gpu_utilization', 0) <= 95 else "⚠️"
        )
        
        table.add_row(
            "Average Memory Utilization",
            f"{summary.get('average_memory_utilization', 0):.1f}%",
            "<90%",
            "✅" if summary.get('average_memory_utilization', 0) < 90 else "⚠️"
        )
        
        console.print(table)
        
        # A100 Comparison
        comparison = report.get("a100_comparison", {})
        console.print("\n📊 A100 Comparison:")
        console.print(f"  • Performance Ratio: {comparison.get('ttft_ratio', 0):.2f}x (vs A100)")
        console.print(f"  • Throughput Ratio: {comparison.get('throughput_ratio', 0):.2f}x (vs A100)")
        console.print(f"  • Cost Efficiency: {comparison.get('cost_efficiency', 0):.2f}x (vs A100)")
        
        # Recommendations
        recommendations = report.get("recommendations", [])
        if recommendations:
            console.print("\n💡 Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                console.print(f"  {i}. {rec}")
        
        console.print("\n" + "="*80)

# Example usage
async def main():
    """Run performance analysis."""
    analyzer = MultiGPUPerformanceAnalyzer(num_gpus=4)
    
    console.print("🎮 Starting Multi-GPU RTX 4090 Performance Analysis")
    console.print("This will test the system with various load scenarios...")
    
    report = await analyzer.run_performance_test(duration=60)  # 1 minute test
    
    analyzer.print_performance_report(report)
    
    # Save report to file
    with open("multi_gpu_performance_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    console.print("\n📄 Performance report saved to 'multi_gpu_performance_report.json'")

if __name__ == "__main__":
    asyncio.run(main()) 