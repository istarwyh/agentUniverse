# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/3/28 10:51
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: dashscope_llm_channel.py
from typing import Optional

from pydantic import Field

from agentuniverse.base.config.component_configer.component_configer import ComponentConfiger
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_channel.llm_channel import LLMChannel


class DashscopeLLMChannel(LLMChannel):
    channel_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("DASHSCOPE_CHANNEL_API_KEY"))
    channel_organization: Optional[str] = Field(default_factory=lambda: get_from_env("DASHSCOPE_CHANNEL_ORGANIZATION"))
    channel_api_base: Optional[str] = Field(default_factory=lambda: get_from_env("DASHSCOPE_CHANNEL_API_BASE"))
    channel_proxy: Optional[str] = Field(default_factory=lambda: get_from_env("DASHSCOPE_CHANNEL_PROXY"))

    def _initialize_by_component_configer(self, component_configer: ComponentConfiger) -> 'DashscopeLLMChannel':
        super()._initialize_by_component_configer(component_configer)
        return self
