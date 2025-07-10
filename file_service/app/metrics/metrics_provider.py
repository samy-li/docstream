import logging
from typing import Dict, Optional

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import \
    OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource

logger = logging.getLogger(__name__)


class MetricsProvider:
    """
    A single-purpose wrapper around OpenTelemetry metrics setup.
    It configures a MeterProvider with OTLP gRPC export to the Collector,
    and exposes a simple method to create named counters.
    """

    def __init__(
            self,
            service_name: str,
            collector_endpoint: str = "otel-collector:4317",
            export_interval_ms: int = 10_000,
    ) -> None:
        """
        Initializes the MetricsProvider with service-specific metadata.

        Args:
            service_name (str): Logical name of the current service.
            collector_endpoint (str): OTLP Collector gRPC endpoint.
            export_interval_ms (int): Metric export interval in milliseconds.
        """
        self._service_name = service_name
        self._collector_endpoint = collector_endpoint
        self._export_interval_ms = export_interval_ms

        self._meter_provider: Optional[MeterProvider] = None
        self._meter = None

    def init(self) -> None:
        """
        Initializes and registers the MeterProvider.
        Should be called once during service startup.
        """
        if self._meter_provider:
            logger.debug("MetricsProvider already initialized.")
            return

        logger.info(
            f"[MetricsProvider] Initializing export to {self._collector_endpoint}")

        reader = PeriodicExportingMetricReader(
            OTLPMetricExporter(endpoint=self._collector_endpoint,
                               insecure=True),
            export_interval_millis=self._export_interval_ms,
        )
        self._meter_provider = MeterProvider(
            metric_readers=[reader],
            resource=Resource.create({"service.name": self._service_name}),
        )
        metrics.set_meter_provider(self._meter_provider)
        self._meter = metrics.get_meter(self._service_name)

        logger.info(
            f"[MetricsProvider] MeterProvider initialized for {self._service_name}")

    def create_counter(
            self,
            name: str,
            description: str,
            unit: str = "1",
            initial_labels: Optional[Dict[str, str]] = None,
    ) -> metrics.Counter:
        """
        Creates and returns a named OpenTelemetry Counter.

        Optionally emits a zero-count sample with initial labels
        to ensure the counter appears in Prometheus/OTLP pipelines.

        Args:
            name (str): Metric name.
            description (str): Metric description.
            unit (str): Measurement unit (default is "1").
            initial_labels (Dict[str, str], optional): Pre-applied label set.

        Returns:
            metrics.Counter: The initialized OpenTelemetry Counter.
        """
        if not self._meter:
            raise RuntimeError(
                "MetricsProvider.init() must be called before using metrics.")

        counter = self._meter.create_counter(name, description=description,
                                             unit=unit)

        if initial_labels is not None:
            counter.add(0, initial_labels)

        logger.debug(f"[MetricsProvider] Counter '{name}' created.")

        return counter
