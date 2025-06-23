# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/2 16:06
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: llm_output.py
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field

from agentuniverse.agent.memory.message import Message

LLM_OUTPUT_TYPE = Literal[
    "text",
    "message",
    "function_call",
    "tool_call",
    "stream",
    "error"
]

FINISH_REASON_TYPE = Literal[
    "stop",
    "length",
    "tool_calls",
    "function_call",
    "content_filter",
    "error"
]


class FunctionCall(BaseModel):
    name: str
    arguments: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        allow_mutation = False
        frozen = True


class TokenUsage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens

    def to_dict(self) -> dict:
        return {
            'completion_tokens': self.completion_tokens,
            'prompt_tokens': self.prompt_tokens,
            'total_tokens': self.total_tokens
        }

    def __add__(self, other):
        if isinstance(other, TokenUsage):
            return TokenUsage(
                prompt_tokens=self.prompt_tokens + other.prompt_tokens,
                completion_tokens=self.completion_tokens + other.completion_tokens
            )
        else:
            return NotImplemented


class LLMOutput(BaseModel):
    """The basic class for llm output."""

    type: LLM_OUTPUT_TYPE = "text"

    """The text of the llm output."""
    text: Optional[str] = None

    """The raw data of the llm output."""
    raw: Optional[Any] = None

    message: Optional[Message] = None

    finish_reason: Optional[FINISH_REASON_TYPE] = None

    function_call: Optional[FunctionCall] = None

    usage: Optional[TokenUsage] = None

    def is_stream(self) -> bool:
        return self.type == "stream"

    def is_function_call(self) -> bool:
        return self.type in ("function_call", "tool_call")
