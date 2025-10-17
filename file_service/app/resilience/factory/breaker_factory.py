import logging
import pybreaker
from app.config.settings import get_settings
from app.resilience.core.circuit_breaker_listener import CircuitBreakerListener

logger = logging.getLogger("docstream")
settings = get_settings()

def make_parser_breaker() -> pybreaker.CircuitBreaker:
    conf = settings.breaker_config.get("parser_service", {})
    fail_max = conf.get("fail_max", 3)
    reset_timeout = conf.get("reset_timeout", 30)
    listener = CircuitBreakerListener("parser_service")

    logger.info(f"Initialized parser breaker (fail_max={fail_max}, reset_timeout={reset_timeout}s)")
    return pybreaker.CircuitBreaker(
        fail_max=fail_max,
        reset_timeout=reset_timeout,
        name="parser_service",
        listeners=[listener],
    )

parser_breaker = make_parser_breaker()
