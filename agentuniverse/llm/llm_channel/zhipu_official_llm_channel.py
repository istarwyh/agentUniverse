# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/4/8 11:36
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: zhipu_official_llm_channel.py
from typing import Optional

from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_channel.llm_channel import LLMChannel

ZHIPU_MAX_CONTEXT_LENGTH = {
    "GLM-4-Plus": 128000,
    "GLM-4-0520": 128000,
    "GLM-4-AirX": 8000,
    "GLM-4-Air": 128000,
    "GLM-4-Long": 1000000,
    "GLM-4-Flash": 128000,
    "GLM-4": 128000,
}


class ZhiPuOfficialLLMChannel(LLMChannel):
    channel_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("ZHIPU_OFFICIAL_CHANNEL_API_KEY"))
    channel_organization: Optional[str] = Field(
        default_factory=lambda: get_from_env("ZHIPU_OFFICIAL_CHANNEL_ORGANIZATION"))
    channel_api_base: Optional[str] = Field(default_factory=lambda: get_from_env(
        "ZHIPU_OFFICIAL_CHANNEL_API_BASE") or "https://open.bigmodel.cn/api/paas/v4/")
    channel_proxy: Optional[str] = Field(default_factory=lambda: get_from_env("ZHIPU_OFFICIAL_CHANNEL_PROXY"))

    def max_context_length(self) -> int:
        """Max context length.

          The total length of input tokens and generated tokens is limited by the openai model's context length.
          """
        return ZHIPU_MAX_CONTEXT_LENGTH.get(self.channel_model_name, 128000)
