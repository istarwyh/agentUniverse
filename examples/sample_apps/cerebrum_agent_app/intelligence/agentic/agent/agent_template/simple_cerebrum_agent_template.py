# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/30 20:02
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: discussion_group_template.py
import json
from agentuniverse.agent.template.cerebrum_agent_template import CerebrumAgentTemplate


class SimpleCerebrumAgentTemplate(CerebrumAgentTemplate):
    prompt_knowledge_dict: dict = {}

    def set_prompt_knowledge_dict(self, prompt_knowledge_dict: dict):
        self.prompt_knowledge_dict = prompt_knowledge_dict

    def get_prompt_knowledge(self):
        return json.dumps(self.prompt_knowledge_dict, ensure_ascii=False)
