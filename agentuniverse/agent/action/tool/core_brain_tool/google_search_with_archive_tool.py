# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# @Time    : 2024/3/31 11:00
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: google_search_tool.py
from typing import Optional, List

from pydantic import Field
from langchain_community.utilities.google_serper import GoogleSerperAPIWrapper
from agentuniverse.agent.action.tool.tool import ToolInput
from agentuniverse.agent.action.tool.core_brain_tool.core_brain_tool import CoreBrainTool
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.base.context.context_archive_utils import update_context_archive


class GoogleSearchWithArchiveTool(CoreBrainTool):
    """The demo google search tool.

    Implement the execute method of demo google search tool, using the `GoogleSerperAPIWrapper` to implement a simple Google search.

    Note:
        You need to sign up for a free account at https://serper.dev and get the serpher api key (2500 free queries).
    """

    serper_api_key: Optional[str] = Field(default_factory=lambda: get_from_env("SERPER_API_KEY"))

    def update_archive_data(self, name, data, description):
        update_context_archive(name, data, description)

    def execute(self, tool_input: ToolInput):
        input = tool_input.get_data("query")
        # get top10 results from Google search.
        search = GoogleSerperAPIWrapper(serper_api_key=self.serper_api_key, k=10, gl="us", hl="en", type="search")
        return search.run(query=input)
