# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/4/8 11:44
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: gemini_official_llm_channel.py
from typing import Optional

from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_channel.llm_channel import LLMChannel

GEMINI_MAX_CONTEXT_LENGTH = {
    "gemini-2.0-flash": 1048576
}


class GeminiOfficialLLMChannel(LLMChannel):
    channel_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("GOOGLE_OFFICIAL_CHANNEL_API_KEY"))
    channel_organization: Optional[str] = Field(
        default_factory=lambda: get_from_env("GOOGLE_OFFICIAL_CHANNEL_ORGANIZATION"))
    channel_api_base: Optional[str] = Field(default_factory=lambda: get_from_env("GOOGLE_OFFICIAL_CHANNEL_API_BASE"))
    channel_proxy: Optional[str] = Field(default_factory=lambda: get_from_env("GOOGLE_OFFICIAL_CHANNEL_PROXY"))

    def max_context_length(self) -> int:
        if super().max_context_length():
            return super().max_context_length()
        return GEMINI_MAX_CONTEXT_LENGTH.get(self.channel_model_name, 8000)
