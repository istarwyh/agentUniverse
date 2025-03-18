# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/1/3 14:13
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: trace_manager.py

from agentuniverse.base.context.framework_context_manager import \
    FrameworkContextManager
from agentuniverse.base.util.tracing.au_trace_context import AuTraceContext
from agentuniverse.base.annotation.singleton import singleton


@singleton
class AuTraceManager:
    def __init__(self, context_class=None):
        self.context_class = context_class or AuTraceContext

    def set_context_class(self, context_class):
        self.context_class = context_class

    def reset_context(self):
        FrameworkContextManager().del_context("__au_trace_context__")
        FrameworkContextManager().del_context("LOG_CONTEXT")

    @property
    def trace_context(self) -> AuTraceContext:
        context = FrameworkContextManager().get_context("__au_trace_context__")
        if not context:
            context = self.context_class.new_context()
            FrameworkContextManager().set_context("__au_trace_context__",
                                                  context)
        return context

    def set_log_context(self):
        self.trace_context.set_log_context()

    def set_session_id(self, session_id):
        self.trace_context.set_session_id(session_id)

    def get_session_id(self):
        return self.trace_context.trace_id

    def set_trace_id(self, trace_id):
        self.trace_context.set_trace_id(trace_id)

    def get_trace_id(self):
        return self.trace_context.trace_id

    def set_span_id(self, span_id):
        self.trace_context.set_span_id(span_id)

    def get_span_id(self):
        return self.trace_context.span_id
