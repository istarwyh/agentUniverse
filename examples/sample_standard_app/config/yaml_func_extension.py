# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/2/28 17:32
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: yaml_func_extension.py
import os

from agentuniverse.base.config.configer import Configer


class YamlFuncExtension:
    """
   This class is a yaml function extension class that allows users to define custom functions in YAML configuration.
   During the startup of the agentUniverse, all functions in this class will be registered.

   Users can configure function calls in YAML files using the syntax `@FUNC(function_name(args))`.
   The agentUniverse will automatically parse the `@FUNC` annotation and execute the corresponding function,
   replacing the annotation with the function's return value.

   Example:
       - In YAML configuration: `@FUNC(load_api_key('qwen'))`
       - The framework will call the `load_api_key` method with the argument `'qwen'`,
         and replace the annotation with the returned API key.
   """

    def load_api_key(self, model_name: str):
        """
       Load the API key for the specified model from environment variables.

       Args:
           model_name (str): The name of the model for which the API key is required.

       Returns:
           str: The API key for the specified model if found; otherwise, an empty string.
       """
        if model_name == "qwen":
            return os.getenv("DASHSCOPE_API_KEY")
        elif model_name == "deepseek":
            return os.getenv("DEEPSEEK_API_KEY")
        else:
            return ""

    def get_llm_by_agent_id(self, agent_id: str):
        """
        Retrieve the LLM ID associated with the given agent ID.

        Args:
            agent_id (str): The ID of the agent for which the LLM is required.

        Returns:
            str: The ID of the LLM component instance associated with the agent ID.
        """
        if agent_id == "demo_agent":
            return 'demo_llm'
        return 'demo_llm'
