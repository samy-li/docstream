import logging
from opentelemetry import trace

logger = logging.getLogger(__name__)
tracer = trace.get_tracer(__name__)


class CircuitBreakerListener:
    """
    Observes breaker events and logs them.
    """

    def __init__(self, service_name: str):
        self.service_name = service_name

    def state_change(self, cb, old_state, new_state):
        """Called when circuit breaker state changes."""
        state = str(new_state).lower()
        with tracer.start_as_current_span(
                f"circuit_state_change:{self.service_name}") as span:
            span.set_attribute("service", self.service_name)
            span.set_attribute("old_state", str(old_state))
            span.set_attribute("new_state", str(new_state))
        logger.warning(
            f"[{self.service_name}] CircuitBreaker {old_state} → {new_state}",
            extra={"service": self.service_name, "state": state},
        )

    def failure(self, cb, exc):
        """Called when a request fails."""
        exc_type = type(exc).__name__
        with tracer.start_as_current_span(
                f"circuit_failure:{self.service_name}") as span:
            span.set_attribute("service", self.service_name)
            span.set_attribute("exception_type", exc_type)
            span.record_exception(exc)
        logger.error(
            f"[{self.service_name}] Failure detected: {exc}",
            extra={"service": self.service_name, "state": cb.current_state,
                   "error": str(exc), "exception_type": exc_type},
        )

    def success(self, cb):
        """Called when a request succeeds."""
        current_state = str(cb.current_state).lower()

        # Only log on successful recovery (transitioning to closed)
        if current_state == "closed":
            with tracer.start_as_current_span(
                    f"circuit_success:{self.service_name}") as span:
                span.set_attribute("service", self.service_name)
            logger.info(
                f"[{self.service_name}] Circuit recovered",
                extra={"service": self.service_name, "state": current_state},
            )