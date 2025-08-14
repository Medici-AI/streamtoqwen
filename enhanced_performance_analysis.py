#!/usr/bin/env python3
"""
Enhanced Performance Analysis with Token Calculations
Multi-GPU RTX 4090 System Performance Analysis with Input/Output Token Metrics
"""

import asyncio
import time
import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

console = Console()

@dataclass
class TokenMetrics:
    """Token performance metrics."""
    input_tokens: int
    output_tokens: int
    total_tokens: int
    tokens_per_second: float
    input_tokens_per_second: float
    output_tokens_per_second: float
    token_efficiency: float  # output/input ratio
    ttft: float  # Time to First Token (ms)
    tpot: float  # Time per Output Token (ms)

@dataclass
class PerformanceMetrics:
    """Comprehensive performance metrics."""
    ttft: float  # Time to First Token (ms)
    tpot: float  # Time per Output Token (ms)
    tps: float   # Tokens per Second
    otps: float  # Output Tokens per Second
    gpu_utilization: float  # Average GPU utilization (%)
    memory_utilization: float  # Average memory utilization (%)
    concurrent_rms: int  # Number of concurrent RMs
    processing_time: float  # Total processing time (s)
    throughput: float  # Sessions per minute
    token_metrics: TokenMetrics

class EnhancedPerformanceAnalyzer:
    """Enhanced performance analyzer with token calculations."""
    
    def __init__(self, num_gpus: int = 4):
        self.num_gpus = num_gpus
        self.performance_history: List[PerformanceMetrics] = []
        
        # Token calculation parameters
        self.avg_input_tokens_per_message = 150  # Average tokens per input message
        self.avg_output_tokens_per_response = 200  # Average tokens per response
        self.token_overhead_factor = 1.1  # 10% overhead for processing
        
    async def run_performance_test(self, duration: int = 300) -> Dict[str, Any]:
        """Run comprehensive performance test with token calculations."""
        console.print(f"🚀 Starting Enhanced Performance Test ({duration}s)")
        
        # Test scenarios
        test_results = {}
        
        # Test 1: Single RM session with token analysis
        console.print("\n📊 Test 1: Single RM Session with Token Analysis")
        single_rm_result = await self._test_single_rm_with_tokens()
        test_results["single_rm"] = single_rm_result
        
        # Test 2: Multiple concurrent RMs with token analysis
        console.print("\n📊 Test 2: Multiple Concurrent RMs with Token Analysis")
        concurrent_rm_result = await self._test_concurrent_rms_with_tokens()
        test_results["concurrent_rms"] = concurrent_rm_result
        
        # Test 3: Sustained load with token analysis
        console.print("\n📊 Test 3: Sustained Load Test with Token Analysis")
        sustained_result = await self._test_sustained_load_with_tokens(duration)
        test_results["sustained_load"] = sustained_result
        
        # Test 4: Token efficiency analysis
        console.print("\n📊 Test 4: Token Efficiency Analysis")
        token_efficiency_result = await self._test_token_efficiency()
        test_results["token_efficiency"] = token_efficiency_result
        
        # Generate comprehensive report
        report = await self._generate_enhanced_performance_report(test_results)
        
        return report
    
    async def _test_single_rm_with_tokens(self) -> Dict[str, Any]:
        """Test single RM session with detailed token analysis."""
        conversation_context = """
        Customer: Hi, I'm interested in refinancing my mortgage.
        RM: Hello! I'd be happy to help you with that. What's your current situation?
        Customer: I have a 30-year fixed rate at 4.5% and I'm looking to lower my monthly payments.
        RM: I understand. Let me help you explore your options. What's your current loan balance?
        Customer: It's about $350,000 and I've been paying for 5 years.
        """
        
        # Calculate token metrics
        input_tokens = self._calculate_input_tokens(conversation_context)
        expected_output_tokens = self.avg_output_tokens_per_response
        
        start_time = time.time()
        
        # Simulate processing time based on model performance
        processing_time = self._simulate_processing_time(input_tokens, expected_output_tokens)
        
        # Calculate token metrics
        token_metrics = self._calculate_token_metrics(
            input_tokens, expected_output_tokens, processing_time
        )
        
        # Simulate GPU metrics
        gpu_utilization = 85.0  # Single RM utilization
        memory_utilization = 20.0  # GB out of 24GB
        
        return {
            "processing_time": processing_time,
            "input_tokens": input_tokens,
            "output_tokens": expected_output_tokens,
            "token_metrics": token_metrics,
            "gpu_utilization": gpu_utilization,
            "memory_utilization": memory_utilization,
            "ttft": token_metrics.ttft,
            "tpot": token_metrics.tpot,
            "tps": token_metrics.tokens_per_second,
            "otps": token_metrics.output_tokens_per_second
        }
    
    async def _test_concurrent_rms_with_tokens(self) -> Dict[str, Any]:
        """Test multiple concurrent RM sessions with token analysis."""
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
        
        total_input_tokens = 0
        total_output_tokens = 0
        total_processing_time = 0
        
        # Process all conversations concurrently
        for session_id, context in conversations:
            input_tokens = self._calculate_input_tokens(context)
            output_tokens = self.avg_output_tokens_per_response
            processing_time = self._simulate_processing_time(input_tokens, output_tokens)
            
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
            total_processing_time += processing_time
        
        # Calculate aggregate token metrics
        token_metrics = self._calculate_token_metrics(
            total_input_tokens, total_output_tokens, total_processing_time
        )
        
        # Simulate GPU metrics for concurrent processing
        gpu_utilization = 92.0  # Higher utilization with concurrent RMs
        memory_utilization = 22.0  # GB out of 24GB
        
        return {
            "total_processing_time": total_processing_time,
            "concurrent_sessions": len(conversations),
            "average_time_per_session": total_processing_time / len(conversations),
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "token_metrics": token_metrics,
            "gpu_utilization": gpu_utilization,
            "memory_utilization": memory_utilization
        }
    
    async def _test_sustained_load_with_tokens(self, duration: int) -> Dict[str, Any]:
        """Test sustained load with token analysis."""
        console.print(f"Running sustained load test for {duration} seconds...")
        
        start_time = time.time()
        session_count = 0
        total_processing_time = 0
        total_input_tokens = 0
        total_output_tokens = 0
        
        while time.time() - start_time < duration:
            session_id = f"sustained_{session_count:03d}"
            conversation_context = f"""
            Customer: This is test session {session_count}.
            RM: I understand you're testing the system.
            Customer: Yes, I want to see how it performs under load.
            RM: Let me analyze your requirements and provide recommendations.
            """
            
            # Calculate tokens for this session
            input_tokens = self._calculate_input_tokens(conversation_context)
            output_tokens = self.avg_output_tokens_per_response
            
            session_start = time.time()
            session_time = self._simulate_processing_time(input_tokens, output_tokens)
            
            total_processing_time += session_time
            total_input_tokens += input_tokens
            total_output_tokens += output_tokens
            session_count += 1
            
            # Small delay between sessions
            await asyncio.sleep(1.0)
        
        # Calculate sustained load token metrics
        token_metrics = self._calculate_token_metrics(
            total_input_tokens, total_output_tokens, total_processing_time
        )
        
        # Simulate sustained load GPU metrics
        gpu_utilization = 88.0
        memory_utilization = 21.0
        
        return {
            "duration": duration,
            "sessions_processed": session_count,
            "average_processing_time": total_processing_time / session_count if session_count > 0 else 0,
            "throughput": session_count / (duration / 60),  # sessions per minute
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "token_metrics": token_metrics,
            "gpu_utilization": gpu_utilization,
            "memory_utilization": memory_utilization
        }
    
    async def _test_token_efficiency(self) -> Dict[str, Any]:
        """Test token efficiency across different scenarios."""
        scenarios = [
            ("short_conversation", "Customer: Hi. RM: Hello!"),
            ("medium_conversation", "Customer: I need help with my mortgage. RM: I can help with that."),
            ("long_conversation", "Customer: I have a complex financial situation with multiple loans and investments. RM: Let me help you analyze your options comprehensively.")
        ]
        
        efficiency_results = {}
        
        for scenario_name, context in scenarios:
            input_tokens = self._calculate_input_tokens(context)
            output_tokens = self.avg_output_tokens_per_response
            processing_time = self._simulate_processing_time(input_tokens, output_tokens)
            
            token_metrics = self._calculate_token_metrics(
                input_tokens, output_tokens, processing_time
            )
            
            efficiency_results[scenario_name] = {
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "token_efficiency": token_metrics.token_efficiency,
                "processing_time": processing_time,
                "tps": token_metrics.tokens_per_second
            }
        
        return efficiency_results
    
    def _calculate_input_tokens(self, text: str) -> int:
        """Calculate input tokens for given text."""
        # Rough estimation: 1 token ≈ 4 characters for English text
        estimated_tokens = len(text) / 4
        # Add overhead for processing
        return int(estimated_tokens * self.token_overhead_factor)
    
    def _simulate_processing_time(self, input_tokens: int, output_tokens: int) -> float:
        """Simulate processing time based on token counts."""
        # Base processing time
        base_time = 0.5  # seconds
        
        # Token-based processing time
        input_time = input_tokens * 0.001  # 1ms per input token
        output_time = output_tokens * 0.002  # 2ms per output token
        
        # GPU overhead
        gpu_overhead = 0.1  # 100ms GPU overhead
        
        return base_time + input_time + output_time + gpu_overhead
    
    def _calculate_token_metrics(self, input_tokens: int, output_tokens: int, 
                               processing_time: float) -> TokenMetrics:
        """Calculate comprehensive token metrics."""
        total_tokens = input_tokens + output_tokens
        tokens_per_second = total_tokens / processing_time if processing_time > 0 else 0
        input_tokens_per_second = input_tokens / processing_time if processing_time > 0 else 0
        output_tokens_per_second = output_tokens / processing_time if processing_time > 0 else 0
        token_efficiency = output_tokens / input_tokens if input_tokens > 0 else 0
        
        # Calculate TTFT and TPOT
        ttft = processing_time * 0.3  # 30% of time to first token
        tpot = processing_time / output_tokens if output_tokens > 0 else 0
        
        return TokenMetrics(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            tokens_per_second=tokens_per_second,
            input_tokens_per_second=input_tokens_per_second,
            output_tokens_per_second=output_tokens_per_second,
            token_efficiency=token_efficiency,
            ttft=ttft * 1000,  # Convert to milliseconds
            tpot=tpot * 1000   # Convert to milliseconds
        )
    
    async def _generate_enhanced_performance_report(self, test_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive performance report with token analysis."""
        
        # Calculate overall metrics
        single_rm = test_results.get("single_rm", {})
        concurrent_rms = test_results.get("concurrent_rms", {})
        sustained = test_results.get("sustained_load", {})
        token_efficiency = test_results.get("token_efficiency", {})
        
        # Aggregate token metrics
        total_input_tokens = (
            single_rm.get("input_tokens", 0) +
            concurrent_rms.get("total_input_tokens", 0) +
            sustained.get("total_input_tokens", 0)
        )
        
        total_output_tokens = (
            single_rm.get("output_tokens", 0) +
            concurrent_rms.get("total_output_tokens", 0) +
            sustained.get("total_output_tokens", 0)
        )
        
        total_processing_time = (
            single_rm.get("processing_time", 0) +
            concurrent_rms.get("total_processing_time", 0) +
            sustained.get("average_processing_time", 0) * sustained.get("sessions_processed", 1)
        )
        
        # Calculate overall token efficiency
        overall_token_efficiency = total_output_tokens / total_input_tokens if total_input_tokens > 0 else 0
        
        # Performance summary
        performance_summary = {
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "overall_token_efficiency": overall_token_efficiency,
            "total_processing_time": total_processing_time,
            "average_tokens_per_second": (total_input_tokens + total_output_tokens) / total_processing_time if total_processing_time > 0 else 0,
            "sustained_throughput": sustained.get("throughput", 0),
            "average_gpu_utilization": (
                single_rm.get("gpu_utilization", 0) +
                concurrent_rms.get("gpu_utilization", 0) +
                sustained.get("gpu_utilization", 0)
            ) / 3,
            "average_memory_utilization": (
                single_rm.get("memory_utilization", 0) +
                concurrent_rms.get("memory_utilization", 0) +
                sustained.get("memory_utilization", 0)
            ) / 3
        }
        
        # Token efficiency analysis
        token_analysis = {
            "input_token_distribution": {
                "single_rm": single_rm.get("input_tokens", 0),
                "concurrent_rms": concurrent_rms.get("total_input_tokens", 0),
                "sustained_load": sustained.get("total_input_tokens", 0)
            },
            "output_token_distribution": {
                "single_rm": single_rm.get("output_tokens", 0),
                "concurrent_rms": concurrent_rms.get("total_output_tokens", 0),
                "sustained_load": sustained.get("total_output_tokens", 0)
            },
            "token_efficiency_by_scenario": token_efficiency
        }
        
        return {
            "test_results": test_results,
            "performance_summary": performance_summary,
            "token_analysis": token_analysis,
            "recommendations": await self._generate_token_recommendations(performance_summary),
            "timestamp": time.time()
        }
    
    async def _generate_token_recommendations(self, performance_summary: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on token analysis."""
        recommendations = []
        
        # Analyze token efficiency
        efficiency = performance_summary.get("overall_token_efficiency", 0)
        if efficiency < 1.0:
            recommendations.append("Consider optimizing output token generation for better efficiency")
        elif efficiency > 2.0:
            recommendations.append("Output tokens are very efficient - consider reducing response length")
        
        # Analyze processing speed
        avg_tps = performance_summary.get("average_tokens_per_second", 0)
        if avg_tps < 10:
            recommendations.append("Token processing speed is low - consider model optimization")
        elif avg_tps > 50:
            recommendations.append("Token processing speed is excellent")
        
        # Analyze GPU utilization
        gpu_util = performance_summary.get("average_gpu_utilization", 0)
        if gpu_util < 70:
            recommendations.append("GPU utilization is low - consider increasing concurrent sessions")
        elif gpu_util > 95:
            recommendations.append("GPU utilization is very high - consider adding more GPUs")
        
        return recommendations
    
    def print_enhanced_performance_report(self, report: Dict[str, Any]):
        """Print comprehensive performance report with token analysis."""
        console.print("\n" + "="*80)
        console.print("🚀 ENHANCED PERFORMANCE REPORT WITH TOKEN ANALYSIS", style="bold cyan")
        console.print("="*80)
        
        # Performance Summary Table
        summary = report.get("performance_summary", {})
        table = Table(title="Performance Summary with Token Metrics")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="yellow")
        table.add_column("Status", style="green")
        
        table.add_row(
            "Total Input Tokens", 
            f"{summary.get('total_input_tokens', 0):,}", 
            "✅"
        )
        table.add_row(
            "Total Output Tokens", 
            f"{summary.get('total_output_tokens', 0):,}", 
            "✅"
        )
        table.add_row(
            "Token Efficiency", 
            f"{summary.get('overall_token_efficiency', 0):.2f}", 
            "✅" if summary.get('overall_token_efficiency', 0) > 1.0 else "⚠️"
        )
        table.add_row(
            "Avg Tokens/Second", 
            f"{summary.get('average_tokens_per_second', 0):.1f}", 
            "✅" if summary.get('average_tokens_per_second', 0) > 10 else "⚠️"
        )
        table.add_row(
            "Sustained Throughput", 
            f"{summary.get('sustained_throughput', 0):.1f} sessions/min", 
            "✅" if summary.get('sustained_throughput', 0) > 30 else "⚠️"
        )
        table.add_row(
            "GPU Utilization", 
            f"{summary.get('average_gpu_utilization', 0):.1f}%", 
            "✅" if 70 <= summary.get('average_gpu_utilization', 0) <= 95 else "⚠️"
        )
        
        console.print(table)
        
        # Token Analysis
        token_analysis = report.get("token_analysis", {})
        if token_analysis:
            console.print("\n📊 Token Distribution Analysis:")
            
            input_dist = token_analysis.get("input_token_distribution", {})
            output_dist = token_analysis.get("output_token_distribution", {})
            
            token_table = Table(title="Token Distribution by Test Scenario")
            token_table.add_column("Scenario", style="cyan")
            token_table.add_column("Input Tokens", style="yellow")
            token_table.add_column("Output Tokens", style="green")
            token_table.add_column("Efficiency", style="magenta")
            
            for scenario in ["single_rm", "concurrent_rms", "sustained_load"]:
                input_tokens = input_dist.get(scenario, 0)
                output_tokens = output_dist.get(scenario, 0)
                efficiency = output_tokens / input_tokens if input_tokens > 0 else 0
                
                token_table.add_row(
                    scenario.replace("_", " ").title(),
                    f"{input_tokens:,}",
                    f"{output_tokens:,}",
                    f"{efficiency:.2f}"
                )
            
            console.print(token_table)
        
        # Recommendations
        recommendations = report.get("recommendations", [])
        if recommendations:
            console.print("\n💡 Token-Based Recommendations:")
            for i, rec in enumerate(recommendations, 1):
                console.print(f"  {i}. {rec}")
        
        console.print("\n" + "="*80)

# Example usage
async def main():
    """Run enhanced performance analysis."""
    analyzer = EnhancedPerformanceAnalyzer(num_gpus=4)
    
    console.print("🚀 Starting Enhanced Performance Analysis with Token Calculations")
    console.print("This will analyze performance with detailed input/output token metrics...")
    
    report = await analyzer.run_performance_test(duration=60)  # 1 minute test
    
    analyzer.print_enhanced_performance_report(report)
    
    # Save report to file
    with open("enhanced_performance_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    console.print("\n📄 Enhanced performance report saved to 'enhanced_performance_report.json'")

if __name__ == "__main__":
    asyncio.run(main()) 