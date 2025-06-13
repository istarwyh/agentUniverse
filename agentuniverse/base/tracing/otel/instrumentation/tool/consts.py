# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/6/10 15:01
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: consts.py


# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/6/9 14:55
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: tool_constants.py

"""
Constants for Tool instrumentor metrics and attributes.
"""

# Instrumentor metadata
INSTRUMENTOR_NAME = "opentelemetry-instrumentation-agentuniverse-tool"
INSTRUMENTOR_VERSION = "0.1.0"


# Metric names
class MetricNames:
    TOOL_CALLS_TOTAL = "tool_calls_total"
    TOOL_ERRORS_TOTAL = "tool_errors_total"
    TOOL_CALL_DURATION = "tool_call_duration"


# Span attribute names
class SpanAttributes:
    # Tool-specific attributes
    SPAN_KIND = "au.span.kind"
    TOOL_NAME = "au.tool.name"
    TOOL_INPUT = "au.tool.input"
    TOOL_OUTPUT = "au.tool.output"
    TOOL_DURATION = "au.tool.duration"
    TOOL_STATUS = "au.tool.status"
    TOOL_PAIR_ID = "au.tool.pair_id"

    # Error attributes
    TOOL_ERROR_TYPE = "au.tool.error.type"
    TOOL_ERROR_MESSAGE = "au.tool.error.message"

    # Trace attributes
    TRACE_CALLER_INFO = "au.trace.caller_info"


# Label names for metrics
class MetricLabels:
    TOOL_NAME = "tool_name"
    CALLER = "caller"
    ERROR_TYPE = "error_type"
