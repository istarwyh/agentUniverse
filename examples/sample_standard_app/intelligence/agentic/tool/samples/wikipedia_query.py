# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: wikipedia_query.py


from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

from sample_standard_app.intelligence.agentic.tool.samples.langchain_tool import LangChainTool


class WikipediaTool(LangChainTool):
    def init_langchain_tool(self, component_configer):
        wrapper = WikipediaAPIWrapper()
        return WikipediaQueryRun(api_wrapper=wrapper)
