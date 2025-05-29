# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/1/6 17:21
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: au_trace_context.py

from opentelemetry.sdk.trace.id_generator import RandomIdGenerator
from opentelemetry.trace import format_trace_id, format_span_id

id_generator = RandomIdGenerator()


class AuTraceContext:
    def __init__(self):
        self._session_id = None
        self._trace_id = '' or self._generate_trace_id()
        self._span_id = '' or self._generate_span_id()

    @classmethod
    def new_context(cls):
        return cls()

    @staticmethod
    def _generate_trace_id() -> str:
        trace_id_int = id_generator.generate_trace_id()
        # Format it as a hex string (standard OTel format)
        return format_trace_id(trace_id_int)

    @staticmethod
    def _generate_span_id() -> str:
        span_id_int = id_generator.generate_span_id()
        # Format it as a hex string (standard OTel format)
        return format_span_id(span_id_int)

    @property
    def session_id(self) -> str:
        return self._session_id

    @property
    def trace_id(self) -> str:
        return self._trace_id

    @property
    def span_id(self) -> str:
        return self._span_id

    def set_session_id(self, session_id: str):
        self._session_id = session_id

    def set_trace_id(self, trace_id: str):
        self._trace_id = trace_id

    def set_span_id(self, span_id: str):
        self._span_id = span_id

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "trace_id": self.trace_id,
            "span_id": self.span_id
        }

    def __str__(self):
        return f"Context(session_id={self.session_id}, trace_id={self.trace_id}, span_id={self.span_id})"

    def __repr__(self):
        return self.__str__()
