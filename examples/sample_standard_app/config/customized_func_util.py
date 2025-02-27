# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/2/27 16:35
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: customized_func_util.py
import os


class CustomizedFuncUtil(object):
    """
   This class is a utility class that allows users to define custom functions.
   During the startup of the agentUniverse, all functions in this class will be registered,
   and the `customized_init_config` method will be executed by default.

   Users can configure function calls in YAML files using the syntax `@FUNC(function_name(args))`.
   The agentUniverse will automatically parse the `@FUNC` annotation and execute the corresponding function,
   replacing the annotation with the function's return value.

   Example:
       - In YAML configuration: `@FUNC(load_api_key('qwen'))`
       - The framework will call the `load_api_key` method with the argument `'qwen'`,
         and replace the annotation with the returned API key.
   """

    def customized_init_config(self):
        """
        This method is automatically executed during the initialization of the agentUniverse.
        It serves as a hook for users to define custom initialization logic for the application.

        For example, this method can be used to:
            - Load additional configuration files.
            - Initialize external services or APIs.
            - Set up default values or environment variables required by the application.
        """
        pass

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
        return 'demo_deepseek_llm'
