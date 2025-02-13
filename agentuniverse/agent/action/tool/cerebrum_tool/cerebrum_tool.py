# !/usr/bin/env python3
# -*- coding:utf-8 -*-
from abc import ABC

# @Time    : 2024/12/16 17:40
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: cerebrum_tool.py

from abc import abstractmethod
from langchain_core.utils.json import parse_and_check_json_markdown
from agentuniverse.base.annotation.trace import trace_tool
from agentuniverse.agent.action.tool.tool import Tool, ToolInput


class CerebrumTool(Tool, ABC):

    @abstractmethod
    def update_archive_data(self, name, data, description):
        raise NotImplementedError


    def input_check(self, kwargs: dict) -> None:
        """Check whether the input parameters of the tool contain input keys of the tool"""
        if self.input_keys:
            for key in self.input_keys:
                if key not in kwargs.keys():
                    raise Exception(f'{self.get_instance_code()} - The input must include key: {key}.')

    @trace_tool
    def run(self, **kwargs):
        """The callable method that runs the tool."""
        json_input = kwargs.get("input")
        json_input = parse_and_check_json_markdown(
            json_input,
            [*self.input_keys, "save_params"]
        )

        tool_input = ToolInput(**json_input)
        execute_result = self.execute(tool_input)

        # save result to archive data
        self.update_archive_data(
            name=json_input["save_params"]["name"],
            data=execute_result,
            description=json_input["save_params"]["description"]
        )

        if json_input["save_params"].get("full_return"):
            return execute_result
        else:
            return "The task is complete, you may proceed to the next step."

    @trace_tool
    def langchain_run(self, *args, callbacks=None, **kwargs):
        """The callable method that runs the tool."""
        json_input = args[0]
        json_input = parse_and_check_json_markdown(
            json_input,
            [*self.input_keys, "save_params"]
        )
        json_input["callbacks"] = callbacks
        tool_input = ToolInput(json_input)
        execute_result = self.execute(tool_input)

        # save result to archive data
        self.update_archive_data(
            name=json_input["save_params"]["name"],
            data=execute_result,
            description=json_input["save_params"]["description"]
        )

        if json_input["save_params"].get("full_return"):
            return execute_result
        else:
            return "The task is complete, you may proceed to the next step."
