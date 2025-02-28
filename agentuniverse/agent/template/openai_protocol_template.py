# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2025/2/26 09:47
# @Author  : weizjajj 
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: openai_agent_template.py
import datetime
import json
from queue import Queue
from typing import Any, List, Dict

from langchain_core.runnables import RunnableSerializable

from agentuniverse.agent.input_object import InputObject
from agentuniverse.agent.memory.memory import Memory
from agentuniverse.agent.memory.message import Message

from agentuniverse.agent.template.agent_template import AgentTemplate
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager
from agentuniverse.base.util.memory_util import get_memory_string


class OpenAIProtocolTemplate(AgentTemplate):
    def input_keys(self) -> list[str]:
        return [
            'messages', 'model', 'stream'
        ]

    def convert_message(self, messages: List[Dict]):
        for message in messages:
            if message.get('role') == 'user':
                message['type'] = 'human'
            elif message.get('role') == 'assistant':
                message['type'] = 'ai'
        return [Message.from_dict(message) for message in messages]

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        for key in self.input_keys():
            if input_object.get_data(key):
                agent_input[key] = input_object.get_data(key)
        messages = agent_input.get('messages')
        convert_messages = self.convert_message(messages)
        input = messages[-1].get('content')
        agent_input['input'] = input
        if len(convert_messages) > 1:
            agent_input['chat_history'] = convert_messages[0:len(convert_messages) - 1]
        return agent_input

    def process_memory(self, agent_input: dict, **kwargs) -> Memory | None:
        if 'chat_history' in agent_input:
            agent_input['chat_history'] = get_memory_string(agent_input.get('chat_history'),
                                                            agent_input.get('agent_id'))
            return None
        return super().process_memory(agent_input, **kwargs)

    def output_keys(self) -> list[str]:
        return ["choices"]

    def parse_result(self, agent_result: dict) -> dict:
        return {
            "object": "chat.completion",
            "id": FrameworkContextManager().get_context('trace_id'),
            "created": int(datetime.datetime.now().timestamp()),
            "model": self.agent_model.info.get('name'),
            "choices": [
                {
                    "message": {
                        "role": "assistant",
                        "content": agent_result.get('output')
                    },
                    "index": 0,
                }
            ],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            },
            "output": agent_result.get('output')
        }

    def add_openai_output_stream(self, output_stream: Queue, agent_output: str):
        if output_stream is None:
            return
        output = {
            "object": "chat.completion.chunk",
            "id": FrameworkContextManager().get_context('trace_id'),
            "created": int(datetime.datetime.now().timestamp()),
            "model": self.agent_model.info.get('name'),
            "choices": [
                {
                    "delta": {
                        "role": "assistant",
                        "content": agent_output
                    },
                    "index": 0,
                }
            ]
        }
        output_stream.put(json.dumps(output))

    def invoke_chain(self, chain: RunnableSerializable[Any, str], agent_input: dict, input_object: InputObject,
                     **kwargs):
        if not input_object.get_data('output_stream'):
            res = chain.invoke(input=agent_input, config=self.get_run_config())
            return res
        result = []
        for token in chain.stream(input=agent_input, config=self.get_run_config()):
            self.add_openai_output_stream(input_object.get_data('output_stream', None), token)
            result.append(token)
        return self.generate_result(result)
