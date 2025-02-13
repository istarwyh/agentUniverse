# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/10/30 20:02
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: discussion_group_template.py
import json
from cerebrum_agent_app.intelligence.agentic.prompt.demo_prompt_knowledge import DEMO_PROMPT_KNOWLEDGE
from agentuniverse.agent.template.cerebrum_agent_template import CerebrumAgentTemplate


class TourPlanAgentTemplate(CerebrumAgentTemplate):
    def get_prompt_knowledge(self):
        return json.dumps(DEMO_PROMPT_KNOWLEDGE, ensure_ascii=False)
