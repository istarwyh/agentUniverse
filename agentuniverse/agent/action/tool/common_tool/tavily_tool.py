# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/3/15 20:34
# @Author  : wangyapei
# @FileName: tavily_tool.py
# @Need install: pip install tavily-python

import json
from typing import Any, Dict, Literal, Optional, List

from pydantic import Field

from agentuniverse.agent.action.tool.tool import Tool, ToolInput
from agentuniverse.agent.action.tool.enum import ToolTypeEnum
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.base.util.logging.logging_util import LOGGER

try:
    from tavily import TavilyClient
except ImportError:
    raise ImportError("`tavily-python` not installed. Please install using `pip install tavily-python`")



class TavilyTool(Tool):
    """Tavily搜索工具，用于通过Tavily API进行网络搜索。
    
    该工具可以执行网络搜索并返回搜索结果，支持两种搜索模式：
    1. 标准搜索：返回结构化的搜索结果
    2. 上下文搜索：返回适合作为LLM上下文的搜索结果
    
    Args:
        api_key (Optional[str]): Tavily API密钥，如果不提供则从环境变量获取
        search_depth (Literal["basic", "advanced"]): 搜索深度，可选"basic"或"advanced"
        max_tokens (int): 返回结果的最大token数
        include_answer (bool): 是否包含AI生成的摘要答案
        format (Literal["json", "markdown"]): 返回结果的格式
    """
    description: str = "使用Tavily API进行网络搜索，获取实时在线信息"

    # 基本配置参数
    api_key: Optional[str] = Field(default_factory=lambda: get_from_env("TAVILY_API_KEY"), description="Tavily API密钥")
    search_depth: Literal["basic", "advanced"] = Field(default="basic", description="搜索深度")
    max_tokens: int = Field(default=6000, description="返回结果的最大token数")
    include_answer: bool = Field(default=False, description="是否包含AI生成的摘要答案")
    format: Literal["json", "markdown"] = Field(default="markdown", description="返回结果的格式")
    search_mode: Literal["standard", "context"] = Field(default="standard", description="搜索模式：standard或context")
    
    # 通用可选参数
    topic: Optional[Literal["general", "news"]] = Field(default=None, description="搜索主题：general或news")
    days: Optional[int] = Field(default=None, description="当topic为news时，指定搜索的天数")
    time_range: Optional[Literal["day", "week", "month", "year"]] = Field(default=None, description="搜索时间范围")
    max_results: int = Field(default=5, description="返回的最大结果数")
    include_domains: Optional[List[str]] = Field(default=None, description="包含的域名列表")
    exclude_domains: Optional[List[str]] = Field(default=None, description="排除的域名列表")
    
    # 仅标准搜索模式可用的参数
    include_raw_content: bool = Field(default=False, description="是否包含原始内容")
    include_images: bool = Field(default=False, description="是否包含图片")
    include_image_descriptions: bool = Field(default=False, description="是否包含图片描述")

    def execute(self, tool_input: ToolInput):
        """执行Tavily搜索工具。
        
        Args:
            tool_input (ToolInput): 包含查询和可选配置参数的输入对象
        
        Returns:
            Dict: 包含搜索结果的字典
        """
        query = tool_input.get_data("query")
        if not query:
            return {"error": "未提供搜索查询"}
            
        # 更新可选配置（如果提供）
        possible_params = [
            "api_key", "search_depth", "max_tokens", "include_answer", "format", "search_mode",
            "topic", "days", "time_range", "max_results", "include_domains", "exclude_domains",
            "include_raw_content", "include_images", "include_image_descriptions"
        ]
        
        for param in possible_params:
            if tool_input.get_data(param) is not None:
                setattr(self, param, tool_input.get_data(param))
        
        # 检查API密钥
        if not self.api_key:
            return {"error": "未提供Tavily API密钥，请设置TAVILY_API_KEY环境变量或在调用时提供api_key参数"}

        try:
            # 初始化Tavily客户端
            client = TavilyClient(api_key=self.api_key)
            
            # 根据搜索模式执行不同的搜索
            if self.search_mode == "context":
                # 上下文搜索模式 - 支持的参数
                context_params = {
                    "query": query,
                    "search_depth": self.search_depth,
                    "max_tokens": self.max_tokens
                }
                
                # 添加其他可选参数（如果有设置）
                for param_name, param_attr in {
                    "topic": self.topic,
                    "days": self.days,
                    "time_range": self.time_range,
                    "max_results": self.max_results,
                    "include_domains": self.include_domains,
                    "exclude_domains": self.exclude_domains
                }.items():
                    if param_attr is not None:
                        context_params[param_name] = param_attr
                
                # 执行上下文搜索
                result = client.get_search_context(**context_params)
                return {"search_results": result, "mode": "context", "query": query}
            else:
                # 标准搜索模式
                # 标准搜索模式 - 支持的参数
                search_params = {
                    "query": query,
                    "search_depth": self.search_depth
                }
                
                # 添加其他可选参数（如果有设置）
                for param_name, param_attr in {
                    "topic": self.topic,
                    "days": self.days,
                    "time_range": self.time_range,
                    "max_results": self.max_results,
                    "include_domains": self.include_domains,
                    "exclude_domains": self.exclude_domains,
                    "include_answer": self.include_answer,
                    "include_raw_content": self.include_raw_content,
                    "include_images": self.include_images,
                    "include_image_descriptions": self.include_image_descriptions
                }.items():
                    if param_attr is not None:
                        search_params[param_name] = param_attr
                
                # 执行标准搜索
                response = client.search(**search_params)
                
                # 处理响应
                result = self._process_standard_search_response(query, response)
                return result
                
        except Exception as e:
            LOGGER.error(f"Tavily搜索出错: {e}")
            return {"error": f"搜索过程中出错: {str(e)}"}

    def _process_standard_search_response(self, query: str, response: Dict[str, Any]) -> Dict[str, Any]:
        """处理标准搜索模式的响应。
        
        Args:
            query (str): 搜索查询
            response (Dict[str, Any]): Tavily API的原始响应
            
        Returns:
            Dict[str, Any]: 处理后的响应
        """
        # 创建干净的响应对象
        clean_response: Dict[str, Any] = {"query": query, "mode": "standard"}
        if "answer" in response:
            clean_response["answer"] = response["answer"]

        # 处理结果，确保不超过max_tokens
        clean_results = []
        current_token_count = len(json.dumps(clean_response))
        for result in response.get("results", []):
            _result = {
                "title": result["title"],
                "url": result["url"],
                "content": result["content"],
                "score": result["score"],
            }
            current_token_count += len(json.dumps(_result))
            if current_token_count > self.max_tokens:
                break
            clean_results.append(_result)
        clean_response["results"] = clean_results

        # 根据格式返回结果
        if self.format == "json":
            clean_response["formatted_results"] = json.dumps(clean_response) if clean_response else "未找到结果。"
        elif self.format == "markdown":
            _markdown = ""
            _markdown += f"# {query}\n\n"
            if "answer" in clean_response:
                _markdown += "### 摘要\n"
                _markdown += f"{clean_response.get('answer')}\n\n"
            for result in clean_response["results"]:
                _markdown += f"### [{result['title']}]({result['url']})\n"
                _markdown += f"{result['content']}\n\n"
            clean_response["formatted_results"] = _markdown

        return clean_response
