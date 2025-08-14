#!/usr/bin/env python3
"""
Multi-GPU Overlay Middleware for RTX 4090 System
Handles GPU orchestration, memory management, and cross-GPU communication
"""

import asyncio
import logging
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import torch
import torch.distributed as dist
from torch.cuda import memory
import psutil
import GPUtil

logger = logging.getLogger(__name__)

class GPUState(Enum):
    IDLE = "idle"
    BUSY = "busy"
    OVERLOADED = "overloaded"
    ERROR = "error"

@dataclass
class GPUMetrics:
    """GPU performance and resource metrics."""
    gpu_id: int
    memory_used: float  # GB
    memory_total: float  # GB
    memory_percent: float  # %
    temperature: float  # Celsius
    power_draw: float  # Watts
    utilization: float  # %
    state: GPUState
    timestamp: float

class MultiGPUMiddleware:
    """Overlay middleware for multi-GPU RTX 4090 orchestration."""
    
    def __init__(self, num_gpus: int = 4, memory_threshold: float = 0.85):
        self.num_gpus = num_gpus
        self.memory_threshold = memory_threshold
        self.gpu_states: Dict[int, GPUState] = {}
        self.memory_pools: Dict[int, List[torch.Tensor]] = {}
        self.task_queue: Dict[int, List[Dict]] = {}
        self.performance_metrics: List[GPUMetrics] = []
        
        # Initialize GPU states
        for gpu_id in range(num_gpus):
            self.gpu_states[gpu_id] = GPUState.IDLE
            self.memory_pools[gpu_id] = []
            self.task_queue[gpu_id] = []
        
        # Start monitoring
        self.monitoring_task = None
        self.is_running = False
    
    async def start(self):
        """Start the middleware monitoring and orchestration."""
        logger.info(f"Starting Multi-GPU Middleware with {self.num_gpus} GPUs")
        self.is_running = True
        self.monitoring_task = asyncio.create_task(self._monitor_gpus())
        
        # Initialize CUDA devices
        for gpu_id in range(self.num_gpus):
            if torch.cuda.is_available():
                torch.cuda.set_device(gpu_id)
                torch.cuda.empty_cache()
                logger.info(f"Initialized GPU {gpu_id}")
    
    async def stop(self):
        """Stop the middleware."""
        logger.info("Stopping Multi-GPU Middleware")
        self.is_running = False
        if self.monitoring_task:
            self.monitoring_task.cancel()
            try:
                await self.monitoring_task
            except asyncio.CancelledError:
                pass
    
    async def _monitor_gpus(self):
        """Monitor GPU performance and resource usage."""
        while self.is_running:
            try:
                for gpu_id in range(self.num_gpus):
                    metrics = await self._get_gpu_metrics(gpu_id)
                    self.performance_metrics.append(metrics)
                    
                    # Update GPU state based on metrics
                    await self._update_gpu_state(gpu_id, metrics)
                    
                    # Clean up old metrics (keep last 1000)
                    if len(self.performance_metrics) > 1000:
                        self.performance_metrics = self.performance_metrics[-1000:]
                
                await asyncio.sleep(1.0)  # Monitor every second
                
            except Exception as e:
                logger.error(f"Error in GPU monitoring: {e}")
                await asyncio.sleep(5.0)
    
    async def _get_gpu_metrics(self, gpu_id: int) -> GPUMetrics:
        """Get current GPU metrics."""
        try:
            # Get GPU info using GPUtil
            gpus = GPUtil.getGPUs()
            if gpu_id < len(gpus):
                gpu = gpus[gpu_id]
                memory_used = gpu.memoryUsed
                memory_total = gpu.memoryTotal
                memory_percent = (memory_used / memory_total) * 100
                temperature = gpu.temperature
                power_draw = gpu.power if hasattr(gpu, 'power') else 0
                utilization = gpu.load * 100 if gpu.load else 0
                
                # Determine state
                if memory_percent > 95:
                    state = GPUState.OVERLOADED
                elif memory_percent > 70:
                    state = GPUState.BUSY
                else:
                    state = GPUState.IDLE
                
                return GPUMetrics(
                    gpu_id=gpu_id,
                    memory_used=memory_used,
                    memory_total=memory_total,
                    memory_percent=memory_percent,
                    temperature=temperature,
                    power_draw=power_draw,
                    utilization=utilization,
                    state=state,
                    timestamp=time.time()
                )
            else:
                return GPUMetrics(
                    gpu_id=gpu_id,
                    memory_used=0,
                    memory_total=24,  # RTX 4090 has 24GB
                    memory_percent=0,
                    temperature=0,
                    power_draw=0,
                    utilization=0,
                    state=GPUState.ERROR,
                    timestamp=time.time()
                )
                
        except Exception as e:
            logger.error(f"Error getting metrics for GPU {gpu_id}: {e}")
            return GPUMetrics(
                gpu_id=gpu_id,
                memory_used=0,
                memory_total=24,
                memory_percent=0,
                temperature=0,
                power_draw=0,
                utilization=0,
                state=GPUState.ERROR,
                timestamp=time.time()
            )
    
    async def _update_gpu_state(self, gpu_id: int, metrics: GPUMetrics):
        """Update GPU state based on metrics."""
        self.gpu_states[gpu_id] = metrics.state
        
        # Log warnings for overloaded GPUs
        if metrics.state == GPUState.OVERLOADED:
            logger.warning(f"GPU {gpu_id} is overloaded: {metrics.memory_percent:.1f}% memory used")
        
        # Log high temperature warnings
        if metrics.temperature > 80:
            logger.warning(f"GPU {gpu_id} temperature is high: {metrics.temperature:.1f}°C")
    
    async def allocate_gpu(self, memory_required: float, priority: int = 1) -> Optional[int]:
        """Allocate GPU based on available memory and load balancing."""
        available_gpus = []
        
        for gpu_id in range(self.num_gpus):
            if gpu_id in self.gpu_states:
                state = self.gpu_states[gpu_id]
                if state != GPUState.OVERLOADED and state != GPUState.ERROR:
                    # Get current metrics
                    metrics = await self._get_gpu_metrics(gpu_id)
                    available_memory = metrics.memory_total - metrics.memory_used
                    
                    if available_memory >= memory_required:
                        available_gpus.append((gpu_id, available_memory, metrics.utilization))
        
        if not available_gpus:
            logger.warning(f"No GPU available for {memory_required}GB memory requirement")
            return None
        
        # Sort by utilization (prefer less utilized GPUs)
        available_gpus.sort(key=lambda x: x[2])
        
        # Return the least utilized GPU
        selected_gpu = available_gpus[0][0]
        logger.info(f"Allocated GPU {selected_gpu} for {memory_required}GB requirement")
        return selected_gpu
    
    async def transfer_tensor(self, tensor: torch.Tensor, source_gpu: int, target_gpu: int) -> torch.Tensor:
        """Transfer tensor between GPUs with optimization."""
        try:
            start_time = time.time()
            
            # Use CUDA streams for asynchronous transfer
            with torch.cuda.stream(torch.cuda.Stream()):
                # Pin memory for faster transfer
                if not tensor.is_pinned():
                    tensor = tensor.pin_memory()
                
                # Transfer to target GPU
                tensor_on_target = tensor.to(f'cuda:{target_gpu}', non_blocking=True)
                
                # Wait for transfer to complete
                torch.cuda.current_stream().synchronize()
            
            transfer_time = time.time() - start_time
            tensor_size_gb = tensor.numel() * tensor.element_size() / (1024**3)
            transfer_speed = tensor_size_gb / transfer_time
            
            logger.info(f"Transferred {tensor_size_gb:.2f}GB tensor from GPU {source_gpu} to GPU {target_gpu} "
                       f"in {transfer_time:.3f}s ({transfer_speed:.2f}GB/s)")
            
            return tensor_on_target
            
        except Exception as e:
            logger.error(f"Error transferring tensor from GPU {source_gpu} to GPU {target_gpu}: {e}")
            raise
    
    async def broadcast_tensor(self, tensor: torch.Tensor, source_gpu: int) -> Dict[int, torch.Tensor]:
        """Broadcast tensor to all GPUs."""
        results = {}
        
        for target_gpu in range(self.num_gpus):
            if target_gpu != source_gpu:
                results[target_gpu] = await self.transfer_tensor(tensor, source_gpu, target_gpu)
            else:
                results[target_gpu] = tensor
        
        return results
    
    async def gather_tensors(self, tensors: Dict[int, torch.Tensor], target_gpu: int) -> torch.Tensor:
        """Gather tensors from all GPUs to target GPU."""
        gathered_tensors = []
        
        for source_gpu, tensor in tensors.items():
            if source_gpu != target_gpu:
                transferred_tensor = await self.transfer_tensor(tensor, source_gpu, target_gpu)
                gathered_tensors.append(transferred_tensor)
            else:
                gathered_tensors.append(tensor)
        
        # Concatenate all tensors
        return torch.cat(gathered_tensors, dim=0)
    
    async def get_memory_pool(self, gpu_id: int) -> List[torch.Tensor]:
        """Get memory pool for specific GPU."""
        return self.memory_pools.get(gpu_id, [])
    
    async def add_to_memory_pool(self, gpu_id: int, tensor: torch.Tensor):
        """Add tensor to GPU memory pool."""
        if gpu_id not in self.memory_pools:
            self.memory_pools[gpu_id] = []
        
        self.memory_pools[gpu_id].append(tensor)
        logger.debug(f"Added tensor to GPU {gpu_id} memory pool")
    
    async def clear_memory_pool(self, gpu_id: int):
        """Clear memory pool for specific GPU."""
        if gpu_id in self.memory_pools:
            self.memory_pools[gpu_id].clear()
            torch.cuda.empty_cache()
            logger.info(f"Cleared memory pool for GPU {gpu_id}")
    
    async def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary for all GPUs."""
        if not self.performance_metrics:
            return {}
        
        # Get latest metrics for each GPU
        latest_metrics = {}
        for gpu_id in range(self.num_gpus):
            gpu_metrics = [m for m in self.performance_metrics if m.gpu_id == gpu_id]
            if gpu_metrics:
                latest_metrics[gpu_id] = gpu_metrics[-1]
        
        # Calculate averages
        total_memory_used = sum(m.memory_used for m in latest_metrics.values())
        total_memory_total = sum(m.memory_total for m in latest_metrics.values())
        avg_temperature = sum(m.temperature for m in latest_metrics.values()) / len(latest_metrics)
        avg_utilization = sum(m.utilization for m in latest_metrics.values()) / len(latest_metrics)
        
        return {
            "total_memory_used_gb": total_memory_used,
            "total_memory_total_gb": total_memory_total,
            "memory_utilization_percent": (total_memory_used / total_memory_total) * 100,
            "average_temperature_celsius": avg_temperature,
            "average_utilization_percent": avg_utilization,
            "gpu_states": {gpu_id: state.value for gpu_id, state in self.gpu_states.items()},
            "timestamp": time.time()
        }
    
    async def health_check(self) -> Dict[int, bool]:
        """Perform health check on all GPUs."""
        health_status = {}
        
        for gpu_id in range(self.num_gpus):
            try:
                metrics = await self._get_gpu_metrics(gpu_id)
                is_healthy = (
                    metrics.state != GPUState.ERROR and
                    metrics.temperature < 85 and
                    metrics.memory_percent < 95
                )
                health_status[gpu_id] = is_healthy
                
                if not is_healthy:
                    logger.warning(f"GPU {gpu_id} health check failed: "
                                 f"state={metrics.state}, temp={metrics.temperature}°C, "
                                 f"memory={metrics.memory_percent:.1f}%")
                
            except Exception as e:
                logger.error(f"Error in health check for GPU {gpu_id}: {e}")
                health_status[gpu_id] = False
        
        return health_status

# Example usage
async def main():
    """Example usage of the Multi-GPU Middleware."""
    middleware = MultiGPUMiddleware(num_gpus=4)
    
    try:
        await middleware.start()
        
        # Example: Allocate GPU for model inference
        gpu_id = await middleware.allocate_gpu(memory_required=8.0)
        if gpu_id is not None:
            print(f"Allocated GPU {gpu_id} for model inference")
        
        # Example: Get performance summary
        summary = await middleware.get_performance_summary()
        print(f"Performance summary: {summary}")
        
        # Example: Health check
        health = await middleware.health_check()
        print(f"GPU health status: {health}")
        
        await asyncio.sleep(10)  # Run for 10 seconds
        
    finally:
        await middleware.stop()

if __name__ == "__main__":
    asyncio.run(main()) 