"""
AIA Enterprise Platform - Circuit Breaker Manager
===============================================

Production-grade circuit breaker implementation for service resilience,
fault tolerance, and graceful degradation of system components.
"""

import time
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable, List
from enum import Enum
from dataclasses import dataclass, field
from contextlib import asynccontextmanager
import functools

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Circuit is open, failing fast
    HALF_OPEN = "HALF_OPEN"  # Testing if service has recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior"""
    failure_threshold: int = 5
    recovery_timeout: int = 60  # seconds
    success_threshold: int = 3  # successful calls needed to close circuit
    timeout: int = 30  # seconds
    expected_exception: type = Exception
    fallback_function: Optional[Callable] = None


@dataclass
class CircuitBreakerMetrics:
    """Metrics for circuit breaker monitoring"""
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    timeouts: int = 0
    circuit_open_count: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None
    average_response_time: float = 0.0
    failure_rate: float = 0.0


class CircuitBreaker:
    """
    Production-grade circuit breaker with comprehensive monitoring and fallback support
    """

    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[float] = None
        self.next_attempt_time: float = 0
        self.metrics = CircuitBreakerMetrics()
        self._lock = asyncio.Lock()

        logger.info(f"🔧 Circuit breaker '{name}' initialized with config: {config}")

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection
        """
        async with self._lock:
            # Check if circuit should remain open
            if self.state == CircuitState.OPEN:
                if time.time() < self.next_attempt_time:
                    self.metrics.total_requests += 1
                    self.metrics.failed_requests += 1
                    logger.warning(f"Circuit breaker '{self.name}' is OPEN - failing fast")

                    if self.config.fallback_function:
                        logger.info(f"Executing fallback function for '{self.name}'")
                        return await self._execute_fallback(*args, **kwargs)

                    raise CircuitBreakerOpenError(
                        f"Circuit breaker '{self.name}' is OPEN. Service unavailable."
                    )
                else:
                    # Transition to half-open to test the service
                    self.state = CircuitState.HALF_OPEN
                    logger.info(f"Circuit breaker '{self.name}' transitioning to HALF_OPEN")

        # Execute the function
        start_time = time.time()
        try:
            # Set timeout for the call
            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=self.config.timeout
                )
            else:
                result = func(*args, **kwargs)

            # Record success
            end_time = time.time()
            response_time = end_time - start_time
            await self._record_success(response_time)

            return result

        except asyncio.TimeoutError:
            await self._record_failure(is_timeout=True)
            logger.error(f"Timeout in circuit breaker '{self.name}' after {self.config.timeout}s")

            if self.config.fallback_function:
                return await self._execute_fallback(*args, **kwargs)

            raise CircuitBreakerTimeoutError(
                f"Circuit breaker '{self.name}' timed out after {self.config.timeout}s"
            )

        except Exception as e:
            if isinstance(e, self.config.expected_exception):
                await self._record_failure()
                logger.error(f"Expected exception in circuit breaker '{self.name}': {e}")
            else:
                # Unexpected exception - don't count against circuit breaker
                logger.error(f"Unexpected exception in circuit breaker '{self.name}': {e}")

            if self.config.fallback_function:
                return await self._execute_fallback(*args, **kwargs)

            raise

    async def _record_success(self, response_time: float):
        """Record successful operation"""
        async with self._lock:
            self.metrics.total_requests += 1
            self.metrics.successful_requests += 1
            self.metrics.last_success_time = time.time()

            # Update average response time
            total_successful = self.metrics.successful_requests
            current_avg = self.metrics.average_response_time
            self.metrics.average_response_time = (
                (current_avg * (total_successful - 1) + response_time) / total_successful
            )

            if self.state == CircuitState.HALF_OPEN:
                self.success_count += 1
                if self.success_count >= self.config.success_threshold:
                    self._close_circuit()
            elif self.state == CircuitState.CLOSED:
                # Reset failure count on success
                self.failure_count = max(0, self.failure_count - 1)

            self._update_failure_rate()

    async def _record_failure(self, is_timeout: bool = False):
        """Record failed operation"""
        async with self._lock:
            self.metrics.total_requests += 1
            self.metrics.failed_requests += 1
            self.last_failure_time = time.time()
            self.metrics.last_failure_time = self.last_failure_time

            if is_timeout:
                self.metrics.timeouts += 1

            if self.state == CircuitState.HALF_OPEN:
                # Any failure in half-open state immediately opens circuit
                self._open_circuit()
            else:
                self.failure_count += 1
                if self.failure_count >= self.config.failure_threshold:
                    self._open_circuit()

            self._update_failure_rate()

    def _open_circuit(self):
        """Open the circuit breaker"""
        self.state = CircuitState.OPEN
        self.next_attempt_time = time.time() + self.config.recovery_timeout
        self.success_count = 0
        self.metrics.circuit_open_count += 1

        logger.warning(
            f"🚨 Circuit breaker '{self.name}' OPENED due to {self.failure_count} failures. "
            f"Next attempt allowed at {datetime.fromtimestamp(self.next_attempt_time)}"
        )

    def _close_circuit(self):
        """Close the circuit breaker"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0

        logger.info(f"✅ Circuit breaker '{self.name}' CLOSED - service recovered")

    def _update_failure_rate(self):
        """Update failure rate metric"""
        if self.metrics.total_requests > 0:
            self.metrics.failure_rate = (
                self.metrics.failed_requests / self.metrics.total_requests
            )

    async def _execute_fallback(self, *args, **kwargs) -> Any:
        """Execute fallback function if available"""
        try:
            if asyncio.iscoroutinefunction(self.config.fallback_function):
                return await self.config.fallback_function(*args, **kwargs)
            else:
                return self.config.fallback_function(*args, **kwargs)
        except Exception as e:
            logger.error(f"Fallback function failed for '{self.name}': {e}")
            raise CircuitBreakerFallbackError(
                f"Both main service and fallback failed for '{self.name}'"
            )

    def get_status(self) -> Dict[str, Any]:
        """Get current status and metrics"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "last_failure_time": self.last_failure_time,
            "next_attempt_time": self.next_attempt_time if self.state == CircuitState.OPEN else None,
            "metrics": {
                "total_requests": self.metrics.total_requests,
                "successful_requests": self.metrics.successful_requests,
                "failed_requests": self.metrics.failed_requests,
                "timeouts": self.metrics.timeouts,
                "circuit_open_count": self.metrics.circuit_open_count,
                "average_response_time": self.metrics.average_response_time,
                "failure_rate": self.metrics.failure_rate,
                "last_success_time": self.metrics.last_success_time,
                "last_failure_time": self.metrics.last_failure_time
            },
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "recovery_timeout": self.config.recovery_timeout,
                "success_threshold": self.config.success_threshold,
                "timeout": self.config.timeout
            }
        }

    def reset(self):
        """Reset circuit breaker to initial state"""
        with self._lock:
            self.state = CircuitState.CLOSED
            self.failure_count = 0
            self.success_count = 0
            self.last_failure_time = None
            self.next_attempt_time = 0
            self.metrics = CircuitBreakerMetrics()

        logger.info(f"🔄 Circuit breaker '{self.name}' reset")


class CircuitBreakerManager:
    """
    Manager for multiple circuit breakers with centralized configuration and monitoring
    """

    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
        self.default_config = CircuitBreakerConfig()

    def initialize_breakers(self, service_names: List[str],
                          custom_configs: Optional[Dict[str, CircuitBreakerConfig]] = None) -> Dict[str, CircuitBreaker]:
        """Initialize circuit breakers for given services"""
        custom_configs = custom_configs or {}

        for service_name in service_names:
            config = custom_configs.get(service_name, self.default_config)
            self.breakers[service_name] = CircuitBreaker(service_name, config)

        logger.info(f"🔧 Initialized {len(self.breakers)} circuit breakers")
        return self.breakers

    def get_breaker(self, service_name: str) -> CircuitBreaker:
        """Get circuit breaker for service"""
        if service_name not in self.breakers:
            raise ValueError(f"Circuit breaker '{service_name}' not found")
        return self.breakers[service_name]

    def get_all_status(self) -> Dict[str, Any]:
        """Get status of all circuit breakers"""
        return {
            name: breaker.get_status()
            for name, breaker in self.breakers.items()
        }

    def reset_all(self):
        """Reset all circuit breakers"""
        for breaker in self.breakers.values():
            breaker.reset()
        logger.info("🔄 All circuit breakers reset")

    def get_health_summary(self) -> Dict[str, Any]:
        """Get overall health summary"""
        total_breakers = len(self.breakers)
        open_breakers = sum(1 for b in self.breakers.values() if b.state == CircuitState.OPEN)
        half_open_breakers = sum(1 for b in self.breakers.values() if b.state == CircuitState.HALF_OPEN)
        closed_breakers = total_breakers - open_breakers - half_open_breakers

        overall_health = "healthy"
        if open_breakers > 0:
            overall_health = "degraded" if open_breakers < total_breakers else "unhealthy"

        return {
            "overall_health": overall_health,
            "total_breakers": total_breakers,
            "states": {
                "closed": closed_breakers,
                "open": open_breakers,
                "half_open": half_open_breakers
            },
            "open_services": [
                name for name, breaker in self.breakers.items()
                if breaker.state == CircuitState.OPEN
            ]
        }


# Decorator for easy circuit breaker integration
def circuit_breaker(service_name: str, config: Optional[CircuitBreakerConfig] = None):
    """Decorator to apply circuit breaker to functions"""
    def decorator(func):
        breaker_config = config or CircuitBreakerConfig()
        breaker = CircuitBreaker(f"{service_name}_{func.__name__}", breaker_config)

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            return await breaker.call(func, *args, **kwargs)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            return asyncio.run(breaker.call(func, *args, **kwargs))

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


# Context manager for circuit breaker operations
@asynccontextmanager
async def circuit_breaker_context(breaker: CircuitBreaker, *args, **kwargs):
    """Context manager for circuit breaker operations"""
    try:
        yield breaker
    except Exception as e:
        logger.error(f"Circuit breaker context error: {e}")
        raise


# Custom exceptions
class CircuitBreakerError(Exception):
    """Base exception for circuit breaker errors"""
    pass


class CircuitBreakerOpenError(CircuitBreakerError):
    """Exception raised when circuit breaker is open"""
    pass


class CircuitBreakerTimeoutError(CircuitBreakerError):
    """Exception raised when circuit breaker times out"""
    pass


class CircuitBreakerFallbackError(CircuitBreakerError):
    """Exception raised when fallback function fails"""
    pass


# Global circuit breaker manager instance
circuit_breaker_manager = CircuitBreakerManager()