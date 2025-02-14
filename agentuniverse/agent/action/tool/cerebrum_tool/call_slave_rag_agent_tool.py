# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/31 11:00
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: google_search_tool.py
from typing import Optional, List

from agentuniverse.agent.action.tool.tool import ToolInput
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.agent.action.tool.cerebrum_tool.cerebrum_tool import CerebrumTool
from agentuniverse.base.context.context_archive_utils import update_context_archive


class CallSlaveRagAgentTool(CerebrumTool):

    def update_archive_data(self, name, data, description):
        update_context_archive(name, data, description)

    def execute(self, tool_input: ToolInput):
        slave_agent = AgentManager().get_instance_obj(
            "slave_rag_agent")
        output_object = slave_agent.run(
            prompt_name=tool_input.get_data("prompt_name"),
            prompt_params=tool_input.get_data("prompt_params")
        )
        return output_object.get_data("output")
