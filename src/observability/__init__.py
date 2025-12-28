"""
Observability module for Sentinel.
Provides OpenTelemetry instrumentation for distributed tracing.
"""

from src.observability.telemetry import (
    setup_telemetry,
    get_tracer,
    instrument_agent_method,
    instrument_claude_call,
    add_span_attributes,
    record_metric
)

__all__ = [
    "setup_telemetry",
    "get_tracer",
    "instrument_agent_method",
    "instrument_claude_call",
    "add_span_attributes",
    "record_metric"
]
