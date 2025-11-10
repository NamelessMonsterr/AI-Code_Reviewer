from datetime import datetime, timedelta
from typing import Callable, Any
import logging
from enum import Enum
import functools

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """Circuit breaker pattern for external service calls"""

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout_seconds: int = 60,
        half_open_attempts: int = 3,
        name: str = "circuit_breaker",
    ):
        self.failure_threshold = failure_threshold
        self.timeout_seconds = timeout_seconds
        self.half_open_attempts = half_open_attempts
        self.name = name

        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self.half_open_success_count = 0

    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""

        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker {self.name} entering HALF_OPEN state")
            else:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker {self.name} is OPEN. "
                    f"Will retry after {self._time_until_retry()} seconds"
                )

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result

        except Exception as e:
            self._on_failure()
            raise

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset"""
        if self.last_failure_time is None:
            return True

        time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
        return time_since_failure >= self.timeout_seconds

    def _time_until_retry(self) -> int:
        """Calculate seconds until retry"""
        if self.last_failure_time is None:
            return 0

        time_since_failure = (datetime.now() - self.last_failure_time).total_seconds()
        return max(0, int(self.timeout_seconds - time_since_failure))

    def _on_success(self):
        """Handle successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_success_count += 1

            if self.half_open_success_count >= self.half_open_attempts:
                self._reset()
                logger.info(f"Circuit breaker {self.name} CLOSED after successful recovery")

        elif self.state == CircuitState.CLOSED:
            self.failure_count = 0

    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()

        if self.state == CircuitState.HALF_OPEN:
            self._trip()
            logger.warning(f"Circuit breaker {self.name} OPENED - recovery failed")

        elif self.failure_count >= self.failure_threshold:
            self._trip()
            logger.warning(
                f"Circuit breaker {self.name} OPENED after {self.failure_count} failures"
            )

    def _trip(self):
        """Open the circuit"""
        self.state = CircuitState.OPEN
        self.half_open_success_count = 0

    def _reset(self):
        """Close the circuit"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.half_open_success_count = 0
        self.last_failure_time = None

    def get_status(self) -> dict:
        """Get current circuit breaker status"""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self.failure_count,
            "last_failure": self.last_failure_time.isoformat() if self.last_failure_time else None,
            "time_until_retry": self._time_until_retry() if self.state == CircuitState.OPEN else 0,
        }


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""

    pass


def circuit_breaker(failure_threshold: int = 5, timeout_seconds: int = 60, name: str = None):
    """Decorator for circuit breaker pattern"""

    def decorator(func):
        cb_name = name or func.__name__
        cb = CircuitBreaker(failure_threshold, timeout_seconds, name=cb_name)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return cb.call(func, *args, **kwargs)

        wrapper.circuit_breaker = cb
        return wrapper

    return decorator
