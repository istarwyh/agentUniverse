# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/4/8 11:38
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: kimi_official_llm_channel.py
from typing import Optional

from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_channel.llm_channel import LLMChannel

KIMI_MAX_CONTEXT_LENGTH = {
    "moonshot-v1-8k": 8000,
    "moonshot-v1-32k": 32000,
    "moonshot-v1-128k": 128000
}


class KimiOfficialLLMChannel(LLMChannel):
    channel_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("KIMI_OFFICIAL_CHANNEL_API_KEY"))
    channel_organization: Optional[str] = Field(
        default_factory=lambda: get_from_env("KIMI_OFFICIAL_CHANNEL_ORGANIZATION"))
    channel_api_base: Optional[str] = Field(default_factory=lambda: get_from_env(
        "KIMI_OFFICIAL_CHANNEL_API_BASE") or "https://api.moonshot.cn/v1")
    channel_proxy: Optional[str] = Field(default_factory=lambda: get_from_env("KIMI_OFFICIAL_CHANNEL_PROXY"))

    def max_context_length(self) -> int:
        if super().max_context_length():
            return super().max_context_length()
        return KIMI_MAX_CONTEXT_LENGTH.get(self.channel_model_name, 8000)
