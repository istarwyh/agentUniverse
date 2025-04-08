# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/4/8 11:45
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: openai_official_llm_channel.py
from typing import Optional

from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_channel.llm_channel import LLMChannel

OPENAI_MAX_CONTEXT_LENGTH = {
    "gpt-3.5-turbo": 4096,
    "gpt-3.5-turbo-0301": 4096,
    "gpt-3.5-turbo-0613": 4096,
    "gpt-3.5-turbo-16k": 16384,
    "gpt-3.5-turbo-16k-0613": 16384,
    "gpt-35-turbo": 4096,
    "gpt-35-turbo-16k": 16384,
    "gpt-3.5-turbo-1106": 16384,
    "gpt-3.5-turbo-0125": 16384,
    "gpt-4-0314": 8192,
    "gpt-4": 8192,
    "gpt-4-32k": 32768,
    "gpt-4-32k-0613": 32768,
    "gpt-4-0613": 8192,
    "gpt-4-1106-preview": 128000,
    "gpt-4-turbo": 128000,
    "gpt-4o": 128000,
    "gpt-4o-2024-05-13": 128000,
}


class OpenAIOfficialLLMChannel(LLMChannel):
    channel_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("OPENAI_OFFICIAL_CHANNEL_API_KEY"))
    channel_organization: Optional[str] = Field(
        default_factory=lambda: get_from_env("OPENAI_OFFICIAL_CHANNEL_ORGANIZATION"))
    channel_api_base: Optional[str] = Field(
        default_factory=lambda: get_from_env("OPENAI_OFFICIAL_CHANNEL_API_BASE") or "https://api.openai.com/v1")
    channel_proxy: Optional[str] = Field(default_factory=lambda: get_from_env("OPENAI_OFFICIAL_CHANNEL_PROXY"))

    def max_context_length(self) -> int:
        if super().max_context_length():
            return super().max_context_length()
        return OPENAI_MAX_CONTEXT_LENGTH.get(self.channel_model_name, 128000)
