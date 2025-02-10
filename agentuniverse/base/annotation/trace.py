# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/5 15:33
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: trace.py
import asyncio
import functools
import inspect
import time

from functools import wraps

from agentuniverse.base.util.monitor.monitor import Monitor
from agentuniverse.llm.llm_output import LLMOutput


def trace_llm(func):
    """Annotation: @trace_llm

    Decorator to trace the LLM invocation, add llm input and output to the monitor.
    """

    @wraps(func)
    async def wrapper_async(*args, **kwargs):
        # get llm input from arguments
        llm_input = _get_input(func, *args, **kwargs)

        source = func.__qualname__

        # check whether the tracing switch is enabled
        self = llm_input.pop('self', None)

        if self and hasattr(self, 'name'):
            name = self.name
            if name is not None:
                source = name

        if self and hasattr(self, 'tracing'):
            if self.tracing is False:
                return await func(*args, **kwargs)

        # add invocation chain to the monitor module.
        Monitor.add_invocation_chain({'source': source, 'type': 'llm'})

        start_time = time.time()
        Monitor().trace_llm_input(source=source, llm_input=llm_input)

        # invoke function
        result = await func(*args, **kwargs)
        # not streaming
        if isinstance(result, LLMOutput):
            # add llm invocation info to monitor
            Monitor().trace_llm_invocation(source=func.__qualname__, llm_input=llm_input, llm_output=result.text,
                                           cost_time=time.time() - start_time)

            # add llm token usage to monitor
            Monitor().trace_llm_token_usage(self, llm_input, result.text)
            Monitor.pop_invocation_chain()
            return result
        else:
            # streaming
            async def gen_iterator():
                llm_output = []
                async for chunk in result:
                    llm_output.append(chunk.text)
                    yield chunk
                # add llm invocation info to monitor
                output_str = "".join(llm_output)
                Monitor().trace_llm_invocation(source=func.__qualname__, llm_input=llm_input,
                                               llm_output=output_str, cost_time=time.time() - start_time)
                # add llm token usage to monitor
                Monitor().trace_llm_token_usage(self, llm_input, output_str)
                Monitor.pop_invocation_chain()

            return gen_iterator()

    @functools.wraps(func)
    def wrapper_sync(*args, **kwargs):
        # get llm input from arguments
        llm_input = _get_input(func, *args, **kwargs)

        source = func.__qualname__

        # check whether the tracing switch is enabled
        self = llm_input.pop('self', None)

        if self and hasattr(self, 'name'):
            name = self.name
            if name is not None:
                source = name

        if self and hasattr(self, 'tracing'):
            if self.tracing is False:
                return func(*args, **kwargs)

        # add invocation chain to the monitor module.
        Monitor.add_invocation_chain({'source': source, 'type': 'llm'})

        start_time = time.time()
        Monitor().trace_llm_input(source=source, llm_input=llm_input)

        # invoke function
        result = func(*args, **kwargs)
        # not streaming
        if isinstance(result, LLMOutput):
            # add llm invocation info to monitor
            Monitor().trace_llm_invocation(source=source, llm_input=llm_input, llm_output=result.text,
                                           cost_time=time.time() - start_time)

            # add llm token usage to monitor
            Monitor().trace_llm_token_usage(self, llm_input, result.text)
            Monitor.pop_invocation_chain()
            return result
        else:
            # streaming
            def gen_iterator():
                llm_output = []
                for chunk in result:
                    llm_output.append(chunk.text)
                    yield chunk
                # add llm invocation info to monitor
                output_str = "".join(llm_output)
                Monitor().trace_llm_invocation(source=func.__qualname__, llm_input=llm_input,
                                               llm_output=output_str, cost_time=time.time() - start_time)

                # add llm token usage to monitor
                Monitor().trace_llm_token_usage(self, llm_input, output_str)
                Monitor.pop_invocation_chain()

            return gen_iterator()

    if asyncio.iscoroutinefunction(func):
        # async function
        return wrapper_async
    else:
        # sync function
        return wrapper_sync


def trace_agent(func):
    """Annotation: @trace_agent

    Decorator to trace the agent invocation, add agent input and output to the monitor.
    """

    @functools.wraps(func)
    async def wrapper_async(*args, **kwargs):
        # get agent input from arguments
        agent_input = _get_input(func, *args, **kwargs)
        # check whether the tracing switch is enabled
        source = func.__qualname__
        self = agent_input.pop('self', None)

        tracing = None
        if isinstance(self, object):
            agent_model = getattr(self, 'agent_model', None)
            if isinstance(agent_model, object):
                info = getattr(agent_model, 'info', None)
                profile = getattr(agent_model, 'profile', None)
                if isinstance(info, dict):
                    source = info.get('name', None)
                if isinstance(profile, dict):
                    tracing = profile.get('tracing', None)

        if tracing is False:
            return await func(*args, **kwargs)

        # add invocation chain to the monitor module.
        Monitor.init_invocation_chain()
        Monitor.add_invocation_chain({'source': source, 'type': 'agent'})

        start_time = time.time()
        Monitor().trace_agent_input(source=source, agent_input=agent_input)

        # invoke function
        result = await func(*args, **kwargs)
        # add agent invocation info to monitor
        Monitor().trace_agent_invocation(source=source, agent_input=agent_input, agent_output=result,
                                         cost_time=time.time() - start_time)
        Monitor.pop_invocation_chain()
        return result

    @functools.wraps(func)
    def wrapper_sync(*args, **kwargs):
        # get agent input from arguments
        agent_input = _get_input(func, *args, **kwargs)
        # check whether the tracing switch is enabled
        source = func.__qualname__
        self = agent_input.pop('self', None)

        tracing = None
        if isinstance(self, object):
            agent_model = getattr(self, 'agent_model', None)
            if isinstance(agent_model, object):
                info = getattr(agent_model, 'info', None)
                profile = getattr(agent_model, 'profile', None)
                if isinstance(info, dict):
                    source = info.get('name', None)
                if isinstance(profile, dict):
                    tracing = profile.get('tracing', None)

        if tracing is False:
            return func(*args, **kwargs)

        # add invocation chain to the monitor module.
        Monitor.init_invocation_chain()
        Monitor.add_invocation_chain({'source': source, 'type': 'agent'})

        start_time = time.time()
        Monitor().trace_agent_input(source=source, agent_input=agent_input)

        # invoke function
        result = func(*args, **kwargs)
        # add agent invocation info to monitor
        Monitor().trace_agent_invocation(source=source, agent_input=agent_input, agent_output=result,
                                         cost_time=time.time() - start_time)
        Monitor.pop_invocation_chain()
        return result

    if asyncio.iscoroutinefunction(func):
        # async function
        return wrapper_async
    else:
        # sync function
        return wrapper_sync


def trace_tool(func):
    """Annotation: @trace_tool

    Decorator to trace the tool invocation.
    """

    @functools.wraps(func)
    def wrapper_sync(*args, **kwargs):
        # get tool input from arguments
        tool_input = _get_input(func, *args, **kwargs)
        start_time = time.time()

        source = func.__qualname__
        self = tool_input.pop('self', None)

        if self and hasattr(self, 'tracing'):
            if self.tracing is False:
                return func(*args, **kwargs)

        if isinstance(self, object):
            name = getattr(self, 'name', None)
            if name is not None:
                source = name

        Monitor().trace_tool_input(source, tool_input)

        # add invocation chain to the monitor module.
        Monitor.add_invocation_chain({'source': source, 'type': 'tool'})

        # invoke function
        result = func(*args, **kwargs)

        # add tool invocation info to monitor
        Monitor().trace_tool_invocation(source=source, tool_input=tool_input, tool_output=result,
                                        cost_time=time.time() - start_time)

        Monitor.pop_invocation_chain()

        return result

    # sync function
    return wrapper_sync


def trace_knowledge(func):
    """Annotation: @trace_knowledge

    Decorator to trace the knowledge invocation.
    """

    @functools.wraps(func)
    def wrapper_sync(*args, **kwargs):
        # get knowledge input from arguments
        knowledge_input = _get_input(func, *args, **kwargs)

        source = func.__qualname__
        self = knowledge_input.pop('self', None)

        if self and hasattr(self, 'tracing'):
            if self.tracing is False:
                return func(*args, **kwargs)

        if isinstance(self, object):
            name = getattr(self, 'name', None)
            if name is not None:
                source = name

        # add invocation chain to the monitor module.
        Monitor.add_invocation_chain({'source': source, 'type': 'knowledge'})

        # invoke function
        result = func(*args, **kwargs)

        Monitor.pop_invocation_chain()

        return result

    # sync function
    return wrapper_sync


def _get_input(func, *args, **kwargs) -> dict:
    """Get the agent input from arguments."""
    sig = inspect.signature(func)
    bound_args = sig.bind(*args, **kwargs)
    bound_args.apply_defaults()
    return {k: v for k, v in bound_args.arguments.items()}
