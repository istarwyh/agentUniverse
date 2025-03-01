# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/2/28 19:49
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: agent_llm_configer.py
from typing import Optional

from agentuniverse.base.annotation.singleton import singleton
from ..configer import Configer


@singleton
class AgentLLMConfiger(Configer):
    default_llm: Optional[str] = None
    agent_llm_config: Optional[dict] = {}

    def __init__(self, config_path: str = None):
        super().__init__(config_path)
        if config_path:
            try:
                self.load()
            except FileNotFoundError as e:
                print(f"Custom key file {config_path} read error, "
                      f"skip load custom key.")
        if self.value:
            self.default_llm = self.value.get('DEFAULT', {}).get('default_llm', None)
            self.agent_llm_config = self.value.get('AGENT_LLM_CONFIG', {})
