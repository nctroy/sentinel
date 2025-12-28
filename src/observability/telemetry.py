"""
OpenTelemetry instrumentation for Sentinel.
Provides distributed tracing for all agent operations.
"""

import os
import logging
from typing import Dict, Any, Optional
from functools import wraps

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

logger = logging.getLogger(__name__)

# Global tracer instance
_tracer: Optional[trace.Tracer] = None


def setup_telemetry(service_name: str = "sentinel") -> trace.Tracer:
    """
    Initialize OpenTelemetry with SigNoz backend.

    Args:
        service_name: Name of the service for telemetry

    Returns:
        Configured tracer instance
    """
    global _tracer

    if _tracer is not None:
        logger.warning("Telemetry already initialized, returning existing tracer")
        return _tracer

    try:
        # Configure resource with service name
        resource = Resource(attributes={
            SERVICE_NAME: service_name
        })

        # Create tracer provider
        provider = TracerProvider(resource=resource)

        # Get OTLP endpoint from environment or use default
        otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")

        # Create OTLP exporter for SigNoz
        otlp_exporter = OTLPSpanExporter(
            endpoint=otlp_endpoint,
            insecure=True  # Use insecure for local development
        )

        # Add span processor with batch export
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))

        # Set as global tracer provider
        trace.set_tracer_provider(provider)

        # Create and cache tracer
        _tracer = trace.get_tracer(__name__)

        logger.info(f"OpenTelemetry initialized: service={service_name}, endpoint={otlp_endpoint}")

        return _tracer

    except Exception as e:
        logger.error(f"Failed to initialize telemetry: {e}", exc_info=True)
        # Return no-op tracer if setup fails
        return trace.get_tracer(__name__)


def get_tracer() -> trace.Tracer:
    """
    Get the global tracer instance.
    Initializes telemetry if not already done.

    Returns:
        Configured tracer instance
    """
    global _tracer

    if _tracer is None:
        return setup_telemetry()

    return _tracer


def instrument_agent_method(method_name: str):
    """
    Decorator to instrument agent methods with OpenTelemetry spans.

    Args:
        method_name: Name to use for the span

    Usage:
        @instrument_agent_method("agent.diagnose")
        async def diagnose(self) -> Dict[str, Any]:
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            tracer = get_tracer()

            with tracer.start_as_current_span(method_name) as span:
                # Add agent context attributes
                span.set_attribute("agent.id", getattr(self, 'agent_id', 'unknown'))
                span.set_attribute("agent.type", getattr(self, 'agent_type', 'unknown'))
                span.set_attribute("agent.domain", getattr(self, 'domain', 'unknown'))

                try:
                    # Execute the wrapped method
                    result = await func(self, *args, **kwargs)

                    # Add result metadata to span
                    if isinstance(result, dict):
                        if 'confidence' in result:
                            span.set_attribute("result.confidence", result['confidence'])
                        if 'impact_score' in result:
                            span.set_attribute("result.impact_score", result['impact_score'])
                        if 'status' in result:
                            span.set_attribute("result.status", result['status'])

                    span.set_attribute("success", True)
                    return result

                except Exception as e:
                    # Record exception in span
                    span.record_exception(e)
                    span.set_attribute("success", False)
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    raise

        return wrapper
    return decorator


def instrument_claude_call(func):
    """
    Decorator specifically for Claude API calls to track token usage and latency.

    Usage:
        @instrument_claude_call
        async def call_claude(self, system_prompt: str, user_message: str) -> str:
            ...
    """
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        tracer = get_tracer()

        with tracer.start_as_current_span("claude.api.call") as span:
            # Add agent context
            span.set_attribute("agent.id", getattr(self, 'agent_id', 'unknown'))

            # Add prompt metadata
            system_prompt = kwargs.get('system_prompt', args[0] if len(args) > 0 else '')
            user_message = kwargs.get('user_message', args[1] if len(args) > 1 else '')

            span.set_attribute("prompt.system.length", len(system_prompt))
            span.set_attribute("prompt.user.length", len(user_message))

            try:
                result = await func(self, *args, **kwargs)
                span.set_attribute("success", True)
                return result

            except Exception as e:
                span.record_exception(e)
                span.set_attribute("success", False)
                span.set_attribute("error.type", type(e).__name__)
                raise

    return wrapper


def add_span_attributes(attributes: Dict[str, Any]) -> None:
    """
    Add custom attributes to the current span.

    Args:
        attributes: Dictionary of key-value pairs to add to span
    """
    current_span = trace.get_current_span()

    if current_span.is_recording():
        for key, value in attributes.items():
            current_span.set_attribute(key, value)


def record_metric(name: str, value: float, attributes: Optional[Dict[str, Any]] = None) -> None:
    """
    Record a custom metric in the current span.

    Args:
        name: Metric name
        value: Metric value
        attributes: Optional attributes to add to the metric
    """
    current_span = trace.get_current_span()

    if current_span.is_recording():
        current_span.set_attribute(f"metric.{name}", value)

        if attributes:
            for key, val in attributes.items():
                current_span.set_attribute(f"metric.{name}.{key}", val)
