# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/4/8 14:16
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: claude_official_llm_channel.py
from typing import Optional

from pydantic import Field

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.llm.llm_channel.llm_channel import LLMChannel

CLAUDE_MAX_CONTEXT_LENGTH = {
    "claude-3-opus-20240229": 200000,
    "claude-3-sonnet-20240229": 200000,
    "claude-3-haiku-20240307": 200000,
    "claude-2.1": 200000,
    "claude-2.0": 100000,
    "claude-instant-1.2": 100000
}


class ClaudeOfficialLLMChannel(LLMChannel):
    channel_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("ANTHROPIC_OFFICIAL_CHANNEL_API_KEY"))
    channel_organization: Optional[str] = Field(
        default_factory=lambda: get_from_env("ANTHROPIC_OFFICIAL_CHANNEL_ORGANIZATION"))
    channel_api_base: Optional[str] = Field(
        default_factory=lambda: get_from_env("ANTHROPIC_OFFICIAL_CHANNEL_API_BASE") or "https://api.anthropic.com/v1/")
    channel_proxy: Optional[str] = Field(default_factory=lambda: get_from_env("ANTHROPIC_OFFICIAL_CHANNEL_PROXY"))

    def max_context_length(self) -> int:
        if super().max_context_length():
            return super().max_context_length()
        return CLAUDE_MAX_CONTEXT_LENGTH.get(self.channel_model_name, 8000)
