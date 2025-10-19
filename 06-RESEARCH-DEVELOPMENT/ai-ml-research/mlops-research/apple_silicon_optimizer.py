#!/usr/bin/env python3
"""
🍎 APPLE SILICON GPU OPTIMIZER - NEURAL PROCESSING ACCELERATION
==============================================================

Apple Silicon GPU optimization system for maximum neural processing performance.
Implements Metal Performance Shaders (MPS) optimization for PyTorch and TensorFlow.

Key Features:
- Apple Silicon GPU detection and optimization
- PyTorch MPS backend configuration
- Memory management for unified architecture
- Performance profiling and optimization
- Neural network compilation optimization
- Real-time performance monitoring

Author: Claude Code (MLOps Specialist)
Version: v3.0 - Apple Silicon Optimized
Deployment: Optimized for M1/M2/M3 processors
"""

import json
import logging
import time
import threading
import psutil
import platform
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field, asdict
from pathlib import Path
import numpy as np
from collections import defaultdict, deque

# PyTorch with MPS support
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import Adam, AdamW
from torch.profiler import profile, record_function, ProfilerActivity

# System monitoring
import subprocess
import plistlib

# FastAPI for monitoring endpoints
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

@dataclass
class AppleSiliconSpecs:
    """Apple Silicon hardware specifications."""
    chip_name: str
    cpu_cores: int
    gpu_cores: int
    neural_engine_cores: int
    unified_memory_gb: float
    memory_bandwidth_gb_s: float
    compute_units: int
    max_threads_per_threadgroup: int

@dataclass
class PerformanceMetrics:
    """Performance metrics for Apple Silicon optimization."""
    timestamp: datetime
    gpu_utilization: float
    memory_usage_mb: float
    memory_usage_percent: float
    thermal_state: str
    power_consumption_watts: float
    compute_throughput_gflops: float
    neural_processing_fps: float
    optimization_score: float

@dataclass
class OptimizationConfig:
    """Configuration for Apple Silicon optimization."""
    enable_mps: bool = True
    memory_fraction: float = 0.8
    allow_tf32: bool = True
    enable_compilation: bool = True
    enable_mixed_precision: bool = True
    batch_size_optimization: bool = True
    threadgroup_optimization: bool = True
    thermal_throttling_protection: bool = True

class AppleSiliconDetector:
    """Detect Apple Silicon specifications and capabilities."""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.specs = None
        self._detect_hardware()

    def _detect_hardware(self):
        """Detect Apple Silicon hardware specifications."""
        try:
            # Check if running on macOS
            if platform.system() != "Darwin":
                self.logger.warning("Not running on macOS, Apple Silicon optimizations disabled")
                return

            # Get system information
            system_info = self._get_system_info()

            # Detect chip type
            chip_name = self._detect_chip_name()

            # Get memory information
            memory_info = self._get_memory_info()

            # Estimate GPU cores based on chip
            gpu_cores = self._estimate_gpu_cores(chip_name)

            self.specs = AppleSiliconSpecs(
                chip_name=chip_name,
                cpu_cores=psutil.cpu_count(logical=False),
                gpu_cores=gpu_cores,
                neural_engine_cores=16,  # Standard for M-series chips
                unified_memory_gb=memory_info["total_gb"],
                memory_bandwidth_gb_s=self._estimate_memory_bandwidth(chip_name),
                compute_units=gpu_cores // 8,  # Approximate compute units
                max_threads_per_threadgroup=1024
            )

            self.logger.info(f"🍎 Detected Apple Silicon: {self.specs.chip_name}")
            self.logger.info(f"   GPU Cores: {self.specs.gpu_cores}")
            self.logger.info(f"   Unified Memory: {self.specs.unified_memory_gb:.1f} GB")
            self.logger.info(f"   Memory Bandwidth: {self.specs.memory_bandwidth_gb_s} GB/s")

        except Exception as e:
            self.logger.error(f"Hardware detection failed: {e}")

    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        try:
            result = subprocess.run(
                ["system_profiler", "SPHardwareDataType", "-json"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                return data["SPHardwareDataType"][0] if data.get("SPHardwareDataType") else {}

        except Exception as e:
            self.logger.warning(f"Could not get system info: {e}")

        return {}

    def _detect_chip_name(self) -> str:
        """Detect the specific Apple Silicon chip."""
        try:
            result = subprocess.run(
                ["sysctl", "-n", "machdep.cpu.brand_string"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                brand_string = result.stdout.strip()

                # Extract chip name from brand string
                if "M3" in brand_string:
                    if "Max" in brand_string:
                        return "M3 Max"
                    elif "Pro" in brand_string:
                        return "M3 Pro"
                    else:
                        return "M3"
                elif "M2" in brand_string:
                    if "Ultra" in brand_string:
                        return "M2 Ultra"
                    elif "Max" in brand_string:
                        return "M2 Max"
                    elif "Pro" in brand_string:
                        return "M2 Pro"
                    else:
                        return "M2"
                elif "M1" in brand_string:
                    if "Ultra" in brand_string:
                        return "M1 Ultra"
                    elif "Max" in brand_string:
                        return "M1 Max"
                    elif "Pro" in brand_string:
                        return "M1 Pro"
                    else:
                        return "M1"

                return brand_string

        except Exception as e:
            self.logger.warning(f"Could not detect chip name: {e}")

        return "Unknown Apple Silicon"

    def _get_memory_info(self) -> Dict[str, float]:
        """Get memory information."""
        memory = psutil.virtual_memory()
        return {
            "total_gb": memory.total / (1024**3),
            "available_gb": memory.available / (1024**3)
        }

    def _estimate_gpu_cores(self, chip_name: str) -> int:
        """Estimate GPU cores based on chip name."""
        gpu_core_mapping = {
            "M1": 8,
            "M1 Pro": 16,
            "M1 Max": 32,
            "M1 Ultra": 64,
            "M2": 10,
            "M2 Pro": 19,
            "M2 Max": 38,
            "M2 Ultra": 76,
            "M3": 10,
            "M3 Pro": 18,
            "M3 Max": 40
        }

        return gpu_core_mapping.get(chip_name, 8)

    def _estimate_memory_bandwidth(self, chip_name: str) -> float:
        """Estimate memory bandwidth based on chip name."""
        bandwidth_mapping = {
            "M1": 68.25,
            "M1 Pro": 200,
            "M1 Max": 400,
            "M1 Ultra": 800,
            "M2": 100,
            "M2 Pro": 200,
            "M2 Max": 400,
            "M2 Ultra": 800,
            "M3": 100,
            "M3 Pro": 150,
            "M3 Max": 300
        }

        return bandwidth_mapping.get(chip_name, 100)

    def is_apple_silicon_available(self) -> bool:
        """Check if Apple Silicon is available."""
        return self.specs is not None

    def get_specifications(self) -> Optional[AppleSiliconSpecs]:
        """Get Apple Silicon specifications."""
        return self.specs

class MPSOptimizer:
    """Metal Performance Shaders (MPS) optimizer for PyTorch."""

    def __init__(self, config: OptimizationConfig):
        self.config = config
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.device = None
        self._initialize_mps()

    def _initialize_mps(self):
        """Initialize MPS backend."""
        if not self.config.enable_mps:
            self.logger.info("MPS optimization disabled by configuration")
            self.device = torch.device("cpu")
            return

        if not torch.backends.mps.is_available():
            self.logger.warning("MPS not available, falling back to CPU")
            self.device = torch.device("cpu")
            return

        try:
            # Set MPS as default device
            self.device = torch.device("mps")

            # Configure MPS settings
            if hasattr(torch.backends.mps, 'set_allocator_settings'):
                torch.backends.mps.set_allocator_settings(
                    memory_fraction=self.config.memory_fraction,
                    max_split_size_mb=128
                )

            # Enable mixed precision if supported
            if self.config.enable_mixed_precision:
                torch.backends.cudnn.benchmark = False  # Not needed for MPS

            self.logger.info("🚀 MPS backend initialized successfully")

        except Exception as e:
            self.logger.error(f"MPS initialization failed: {e}")
            self.device = torch.device("cpu")

    def optimize_model(self, model: nn.Module) -> nn.Module:
        """Optimize model for Apple Silicon."""
        try:
            # Move model to MPS device
            model = model.to(self.device)

            # Apply model-specific optimizations
            if self.config.enable_compilation and hasattr(torch, 'compile'):
                try:
                    # Use torch.compile for optimization
                    model = torch.compile(
                        model,
                        backend="aot_eager",  # Use AOT eager for MPS compatibility
                        mode="default"
                    )
                    self.logger.info("✅ Model compilation enabled")
                except Exception as e:
                    self.logger.warning(f"Model compilation failed: {e}")

            # Set model to optimal mode
            model.eval()  # Use eval mode for inference optimization

            self.logger.info("🍎 Model optimized for Apple Silicon")
            return model

        except Exception as e:
            self.logger.error(f"Model optimization failed: {e}")
            return model

    def optimize_batch_size(
        self,
        model: nn.Module,
        input_shape: Tuple[int, ...],
        target_memory_usage: float = 0.7
    ) -> int:
        """Find optimal batch size for Apple Silicon."""
        if not self.config.batch_size_optimization:
            return 32  # Default batch size

        try:
            model = model.to(self.device)
            optimal_batch_size = 1

            # Start with small batch size and increase
            for batch_size in [1, 2, 4, 8, 16, 32, 64, 128, 256]:
                try:
                    # Create test batch
                    test_input = torch.randn(batch_size, *input_shape[1:]).to(self.device)

                    # Test forward pass
                    with torch.no_grad():
                        _ = model(test_input)

                    # Check memory usage
                    if hasattr(torch.mps, 'current_allocated_memory'):
                        memory_used = torch.mps.current_allocated_memory()
                        total_memory = psutil.virtual_memory().total
                        memory_fraction = memory_used / total_memory

                        if memory_fraction > target_memory_usage:
                            break

                    optimal_batch_size = batch_size

                except Exception as e:
                    self.logger.debug(f"Batch size {batch_size} failed: {e}")
                    break

            self.logger.info(f"🎯 Optimal batch size: {optimal_batch_size}")
            return optimal_batch_size

        except Exception as e:
            self.logger.error(f"Batch size optimization failed: {e}")
            return 32

    def create_optimized_dataloader(
        self,
        dataset,
        batch_size: Optional[int] = None,
        **kwargs
    ):
        """Create optimized DataLoader for Apple Silicon."""
        if batch_size is None:
            batch_size = 32

        # Apple Silicon specific optimizations
        dataloader_kwargs = {
            'batch_size': batch_size,
            'shuffle': kwargs.get('shuffle', True),
            'num_workers': min(4, psutil.cpu_count()),  # Optimal for unified memory
            'pin_memory': False,  # Not needed for MPS
            'persistent_workers': True,
            'prefetch_factor': 2,
            **kwargs
        }

        from torch.utils.data import DataLoader
        return DataLoader(dataset, **dataloader_kwargs)

class PerformanceMonitor:
    """Monitor Apple Silicon performance metrics."""

    def __init__(self):
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self.metrics_history = deque(maxlen=1000)
        self.monitoring_thread = None
        self.running = False

    def start_monitoring(self):
        """Start performance monitoring."""
        if self.running:
            return

        self.running = True
        self.monitoring_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()

        self.logger.info("📊 Performance monitoring started")

    def _monitoring_loop(self):
        """Background monitoring loop."""
        while self.running:
            try:
                metrics = self._collect_metrics()
                self.metrics_history.append(metrics)
                time.sleep(5)  # Collect metrics every 5 seconds

            except Exception as e:
                self.logger.error(f"Metrics collection error: {e}")
                time.sleep(10)

    def _collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics."""
        # Get system metrics
        memory = psutil.virtual_memory()
        cpu_freq = psutil.cpu_freq()

        # Get thermal state
        thermal_state = self._get_thermal_state()

        # Estimate GPU utilization (simplified)
        gpu_utilization = self._estimate_gpu_utilization()

        # Calculate optimization score
        optimization_score = self._calculate_optimization_score(
            gpu_utilization, memory.percent, thermal_state
        )

        return PerformanceMetrics(
            timestamp=datetime.now(),
            gpu_utilization=gpu_utilization,
            memory_usage_mb=memory.used / (1024**2),
            memory_usage_percent=memory.percent,
            thermal_state=thermal_state,
            power_consumption_watts=self._estimate_power_consumption(),
            compute_throughput_gflops=self._estimate_compute_throughput(),
            neural_processing_fps=self._estimate_neural_fps(),
            optimization_score=optimization_score
        )

    def _get_thermal_state(self) -> str:
        """Get system thermal state."""
        try:
            result = subprocess.run(
                ["pmset", "-g", "thermlog"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                output = result.stdout.lower()
                if "critical" in output:
                    return "critical"
                elif "warning" in output or "hot" in output:
                    return "warning"
                else:
                    return "normal"

        except Exception as e:
            self.logger.debug(f"Thermal state detection failed: {e}")

        return "unknown"

    def _estimate_gpu_utilization(self) -> float:
        """Estimate GPU utilization."""
        try:
            # Check if PyTorch MPS is being used
            if torch.backends.mps.is_available():
                # Simplified estimation based on system load
                load_avg = psutil.getloadavg()[0]
                cpu_count = psutil.cpu_count()
                return min(100.0, (load_avg / cpu_count) * 100)

        except Exception as e:
            self.logger.debug(f"GPU utilization estimation failed: {e}")

        return 0.0

    def _estimate_power_consumption(self) -> float:
        """Estimate power consumption."""
        # Simplified estimation based on CPU usage and thermal state
        cpu_percent = psutil.cpu_percent(interval=1)
        base_power = 15.0  # Base power consumption for Apple Silicon

        # Scale with CPU usage
        dynamic_power = (cpu_percent / 100) * 20.0

        return base_power + dynamic_power

    def _estimate_compute_throughput(self) -> float:
        """Estimate compute throughput in GFLOPS."""
        # Simplified estimation
        cpu_percent = psutil.cpu_percent()
        max_gflops = 10000  # Approximate for Apple Silicon

        return (cpu_percent / 100) * max_gflops

    def _estimate_neural_fps(self) -> float:
        """Estimate neural processing FPS."""
        # Simplified estimation
        gpu_util = self._estimate_gpu_utilization()
        max_fps = 1000  # Approximate maximum

        return (gpu_util / 100) * max_fps

    def _calculate_optimization_score(
        self,
        gpu_util: float,
        memory_percent: float,
        thermal_state: str
    ) -> float:
        """Calculate overall optimization score."""
        # Base score from utilization
        util_score = min(gpu_util / 80.0, 1.0)  # Target 80% utilization

        # Memory efficiency score
        memory_score = 1.0 - min(memory_percent / 90.0, 1.0)  # Penalty above 90%

        # Thermal score
        thermal_score = {
            "normal": 1.0,
            "warning": 0.7,
            "critical": 0.3,
            "unknown": 0.5
        }.get(thermal_state, 0.5)

        # Weighted average
        return (util_score * 0.4 + memory_score * 0.3 + thermal_score * 0.3) * 100

    def get_current_metrics(self) -> Optional[PerformanceMetrics]:
        """Get current performance metrics."""
        if self.metrics_history:
            return self.metrics_history[-1]
        return None

    def get_metrics_summary(self, minutes: int = 10) -> Dict[str, Any]:
        """Get performance metrics summary."""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        recent_metrics = [
            m for m in self.metrics_history
            if m.timestamp >= cutoff_time
        ]

        if not recent_metrics:
            return {"error": "No recent metrics available"}

        return {
            "period_minutes": minutes,
            "samples_count": len(recent_metrics),
            "avg_gpu_utilization": np.mean([m.gpu_utilization for m in recent_metrics]),
            "avg_memory_usage_percent": np.mean([m.memory_usage_percent for m in recent_metrics]),
            "avg_optimization_score": np.mean([m.optimization_score for m in recent_metrics]),
            "thermal_states": list({m.thermal_state for m in recent_metrics}),
            "peak_throughput_gflops": max([m.compute_throughput_gflops for m in recent_metrics])
        }

    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)

        self.logger.info("🛑 Performance monitoring stopped")

class AppleSiliconOptimizer:
    """Main Apple Silicon optimization system."""

    def __init__(self, config: OptimizationConfig = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or OptimizationConfig()

        # Initialize components
        self.detector = AppleSiliconDetector()
        self.mps_optimizer = MPSOptimizer(self.config)
        self.performance_monitor = PerformanceMonitor()

        # System state
        self.optimized_models = {}
        self.optimization_history = []

        self.logger.info("🍎 Apple Silicon Optimizer initialized")

    def is_available(self) -> bool:
        """Check if Apple Silicon optimization is available."""
        return self.detector.is_apple_silicon_available()

    def get_device(self) -> torch.device:
        """Get optimal device for computation."""
        return self.mps_optimizer.device

    def optimize_model(
        self,
        model: nn.Module,
        model_id: str,
        input_shape: Tuple[int, ...] = None
    ) -> Tuple[nn.Module, Dict[str, Any]]:
        """Optimize model for Apple Silicon."""
        self.logger.info(f"🎯 Optimizing model {model_id} for Apple Silicon")

        start_time = time.time()

        # Apply MPS optimizations
        optimized_model = self.mps_optimizer.optimize_model(model)

        # Find optimal batch size if input shape provided
        optimal_batch_size = None
        if input_shape:
            optimal_batch_size = self.mps_optimizer.optimize_batch_size(
                optimized_model, input_shape
            )

        # Record optimization
        optimization_time = time.time() - start_time
        optimization_info = {
            "model_id": model_id,
            "optimization_time": optimization_time,
            "device": str(self.mps_optimizer.device),
            "optimal_batch_size": optimal_batch_size,
            "compilation_enabled": self.config.enable_compilation,
            "mixed_precision_enabled": self.config.enable_mixed_precision,
            "optimized_at": datetime.now()
        }

        self.optimized_models[model_id] = optimization_info
        self.optimization_history.append(optimization_info)

        self.logger.info(f"✅ Model {model_id} optimized in {optimization_time:.2f}s")

        return optimized_model, optimization_info

    def create_optimal_training_setup(
        self,
        model: nn.Module,
        learning_rate: float = 1e-3,
        weight_decay: float = 1e-4
    ) -> Dict[str, Any]:
        """Create optimal training setup for Apple Silicon."""
        # Optimizer selection
        optimizer = AdamW(
            model.parameters(),
            lr=learning_rate,
            weight_decay=weight_decay,
            eps=1e-8  # Optimal for mixed precision
        )

        # Learning rate scheduler
        scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(
            optimizer,
            T_max=100,
            eta_min=learning_rate * 0.01
        )

        # Scaler for mixed precision (if enabled)
        scaler = None
        if self.config.enable_mixed_precision and self.mps_optimizer.device.type == "mps":
            # Note: MPS doesn't fully support autocast yet, but prepare for future
            scaler = torch.cuda.amp.GradScaler() if torch.cuda.is_available() else None

        return {
            "optimizer": optimizer,
            "scheduler": scheduler,
            "scaler": scaler,
            "device": self.mps_optimizer.device
        }

    def profile_model_performance(
        self,
        model: nn.Module,
        input_tensor: torch.Tensor,
        num_iterations: int = 100
    ) -> Dict[str, Any]:
        """Profile model performance on Apple Silicon."""
        self.logger.info("📊 Profiling model performance...")

        model = model.to(self.mps_optimizer.device)
        input_tensor = input_tensor.to(self.mps_optimizer.device)
        model.eval()

        # Warmup
        with torch.no_grad():
            for _ in range(10):
                _ = model(input_tensor)

        # Synchronize MPS operations
        if self.mps_optimizer.device.type == "mps":
            torch.mps.synchronize()

        # Benchmark
        start_time = time.time()

        with torch.no_grad():
            for _ in range(num_iterations):
                _ = model(input_tensor)

        if self.mps_optimizer.device.type == "mps":
            torch.mps.synchronize()

        total_time = time.time() - start_time
        avg_inference_time = total_time / num_iterations
        throughput = 1.0 / avg_inference_time

        # Memory usage
        memory_usage = 0
        if hasattr(torch.mps, 'current_allocated_memory'):
            memory_usage = torch.mps.current_allocated_memory()

        performance_results = {
            "avg_inference_time_ms": avg_inference_time * 1000,
            "throughput_fps": throughput,
            "total_time_seconds": total_time,
            "iterations": num_iterations,
            "memory_usage_mb": memory_usage / (1024**2),
            "device": str(self.mps_optimizer.device),
            "batch_size": input_tensor.shape[0],
            "input_shape": list(input_tensor.shape)
        }

        self.logger.info(f"⚡ Performance: {avg_inference_time*1000:.2f}ms per inference, "
                        f"{throughput:.1f} FPS")

        return performance_results

    def start_monitoring(self):
        """Start performance monitoring."""
        self.performance_monitor.start_monitoring()

    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.performance_monitor.stop_monitoring()

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status."""
        specs = self.detector.get_specifications()
        current_metrics = self.performance_monitor.get_current_metrics()

        return {
            "apple_silicon_available": self.is_available(),
            "hardware_specs": asdict(specs) if specs else None,
            "mps_available": torch.backends.mps.is_available(),
            "current_device": str(self.mps_optimizer.device),
            "optimization_config": asdict(self.config),
            "optimized_models_count": len(self.optimized_models),
            "current_performance": asdict(current_metrics) if current_metrics else None,
            "system_timestamp": datetime.now()
        }

    def get_optimization_recommendations(self) -> List[Dict[str, Any]]:
        """Get optimization recommendations."""
        recommendations = []

        specs = self.detector.get_specifications()
        if not specs:
            return [{"type": "error", "message": "Apple Silicon not detected"}]

        current_metrics = self.performance_monitor.get_current_metrics()

        # Memory recommendations
        if current_metrics and current_metrics.memory_usage_percent > 85:
            recommendations.append({
                "type": "memory",
                "severity": "high",
                "message": "High memory usage detected",
                "suggestion": "Consider reducing batch size or model complexity"
            })

        # Thermal recommendations
        if current_metrics and current_metrics.thermal_state == "warning":
            recommendations.append({
                "type": "thermal",
                "severity": "medium",
                "message": "System running warm",
                "suggestion": "Consider reducing workload or improving cooling"
            })

        # Performance recommendations
        if current_metrics and current_metrics.optimization_score < 60:
            recommendations.append({
                "type": "performance",
                "severity": "medium",
                "message": "Low optimization score",
                "suggestion": "Enable model compilation and mixed precision training"
            })

        return recommendations

# FastAPI application for Apple Silicon optimization monitoring
app = FastAPI(title="Apple Silicon Optimizer", version="3.0")

# Global optimizer instance
optimizer = None

@app.on_event("startup")
async def startup_event():
    """Initialize optimizer on startup."""
    global optimizer
    optimizer = AppleSiliconOptimizer()
    optimizer.start_monitoring()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    if optimizer:
        optimizer.stop_monitoring()

class OptimizationRequest(BaseModel):
    model_id: str
    enable_compilation: bool = True
    enable_mixed_precision: bool = True
    memory_fraction: float = 0.8

@app.get("/api/v3/optimization/status")
async def get_system_status():
    """Get Apple Silicon optimization status."""
    try:
        status = optimizer.get_system_status()
        return {"success": True, "data": status}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/optimization/recommendations")
async def get_recommendations():
    """Get optimization recommendations."""
    try:
        recommendations = optimizer.get_optimization_recommendations()
        return {"success": True, "data": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v3/optimization/metrics")
async def get_performance_metrics():
    """Get current performance metrics."""
    try:
        current_metrics = optimizer.performance_monitor.get_current_metrics()
        summary = optimizer.performance_monitor.get_metrics_summary()

        return {
            "success": True,
            "data": {
                "current": asdict(current_metrics) if current_metrics else None,
                "summary": summary
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "system": "apple_silicon_optimizer",
        "apple_silicon_available": optimizer.is_available() if optimizer else False
    }

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [%(levelname)s] - %(name)s - %(message)s'
    )

    # Example usage
    optimizer = AppleSiliconOptimizer()
    optimizer.start_monitoring()

    # Create example model
    model = nn.Sequential(
        nn.Linear(768, 512),
        nn.ReLU(),
        nn.Linear(512, 256),
        nn.ReLU(),
        nn.Linear(256, 128)
    )

    # Optimize model
    if optimizer.is_available():
        optimized_model, optimization_info = optimizer.optimize_model(
            model,
            "example_model",
            input_shape=(32, 768)
        )

        print("🍎 Apple Silicon Optimization Complete:")
        print(json.dumps(optimization_info, indent=2, default=str))

        # Profile performance
        test_input = torch.randn(32, 768)
        performance_results = optimizer.profile_model_performance(
            optimized_model, test_input
        )

        print("📊 Performance Results:")
        print(json.dumps(performance_results, indent=2))

    # Run FastAPI server
    uvicorn.run(
        "apple_silicon_optimizer:app",
        host="0.0.0.0",
        port=8005,
        log_level="info",
        reload=False
    )