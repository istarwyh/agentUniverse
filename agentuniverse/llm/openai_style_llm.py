# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/5/21 13:52
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: openai_style_llm.py

from typing import Any, Optional, AsyncIterator, Iterator, Union

import httpx
import openai
import tiktoken
from langchain_core.language_models.base import BaseLanguageModel
from openai import OpenAI, AsyncOpenAI

from agentuniverse.base.config.component_configer.configers.llm_configer import LLMConfiger
from agentuniverse.base.util.billing_center import BillingCenter, BillingCenterInfo
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.base.util.system_util import process_yaml_func
from agentuniverse.llm.llm import LLM, LLMOutput
from agentuniverse.llm.openai_style_langchain_instance import LangchainOpenAIStyleInstance


class OpenAIStyleLLM(LLM):
    """This is a wrapper around the OpenAI API that implements a chat interface for the LLM.

    It uses the `chat` endpoint of the OpenAI API.
    It also supports using the `completion` endpoint instead of the `chat` endpoint.
    It supports both sync and async modes.

    Attributes:
        api_key (Optional[str]): The API key to use for authentication.
        organization (Optional[str]): The organization ID to use for authentication.
        api_base (Optional[str]): The base URL to use for the API requests.
        proxy (Optional[str]): The proxy to use for the API requests.
        client_args (Optional[dict]): Additional arguments to pass to the client.
    """

    api_key: Optional[str] = None
    organization: Optional[str] = None
    api_base: Optional[str] = None
    proxy: Optional[str] = None
    client_args: Optional[dict] = None
    ext_params: Optional[dict] = {}
    ext_headers: Optional[dict] = {}

    def _new_client(self):
        """Initialize the openai client."""
        if self.client is not None:
            return self.client
        return OpenAI(
            api_key=self.api_key,
            organization=self.organization,
            base_url=BillingCenter.get_base_url(self.api_base),
            timeout=self.request_timeout,
            max_retries=self.max_retries,
            http_client=httpx.Client(proxy=self.proxy) if self.proxy else None,

            **(self.client_args or {}),
        )

    def _new_async_client(self):
        """Initialize the openai async client."""
        if self.async_client is not None:
            return self.async_client
        return AsyncOpenAI(
            api_key=self.api_key,
            organization=self.organization,
            base_url=BillingCenter.get_base_url(self.api_base),
            timeout=self.request_timeout,
            max_retries=self.max_retries,
            http_client=httpx.AsyncClient(proxy=self.proxy) if self.proxy else None,
            **(self.client_args or {}),
        )

    def _call(self, messages: list, **kwargs: Any) -> Union[LLMOutput, Iterator[LLMOutput]]:
        """Run the OpenAI LLM.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        streaming = kwargs.pop("streaming") if "streaming" in kwargs else self.streaming
        if 'stream' in kwargs:
            streaming = kwargs.pop('stream')
        self.client = self._new_client()
        client = self.client
        extra_headers, kwargs = BillingCenter.billing_center_openai_headers(self, kwargs)
        chat_completion = client.chat.completions.create(
            messages=messages,
            model=kwargs.pop('model', self.model_name),
            temperature=kwargs.pop('temperature', self.temperature),
            stream=kwargs.pop('stream', streaming),
            max_tokens=kwargs.pop('max_tokens', self.max_tokens),
            extra_headers=extra_headers,
            extra_body=self.ext_params,
            **kwargs,
        )
        if not streaming:
            text = chat_completion.choices[0].message.content
            return LLMOutput(text=text, raw=chat_completion.model_dump())
        return self.generate_stream_result(chat_completion)

    async def _acall(self, messages: list, **kwargs: Any) -> Union[LLMOutput, AsyncIterator[LLMOutput]]:
        """Asynchronously run the OpenAI LLM.

        Args:
            messages (list): The messages to send to the LLM.
            **kwargs: Arbitrary keyword arguments.
        """
        streaming = kwargs.pop("streaming") if "streaming" in kwargs else self.streaming
        if 'stream' in kwargs:
            streaming = kwargs.pop('stream')
        self.async_client = self._new_async_client()
        async_client = self.async_client
        extra_headers, kwargs = BillingCenter.billing_center_openai_headers(self, kwargs)
        chat_completion = await async_client.chat.completions.create(
            messages=messages,
            model=kwargs.pop('model', self.model_name),
            temperature=kwargs.pop('temperature', self.temperature),
            stream=kwargs.pop('stream', streaming),
            max_tokens=kwargs.pop('max_tokens', self.max_tokens),
            extra_headers=extra_headers,
            extra_body=self.ext_params,
            **kwargs,
        )
        if not streaming:
            text = chat_completion.choices[0].message.content
            return LLMOutput(text=text, raw=chat_completion.model_dump())
        return self.agenerate_stream_result(chat_completion)

    def as_langchain(self) -> BaseLanguageModel:
        """Convert the AgentUniverse(AU) openai llm class to the langchain openai llm class."""
        self.init_channel()
        if self._channel_instance:
            return self._channel_instance.as_langchain()
        return LangchainOpenAIStyleInstance(self)

    def set_by_agent_model(self, **kwargs) -> None:
        """ Assign values of parameters to the OpenAILLM model in the agent configuration."""
        copied_obj = super().set_by_agent_model(**kwargs)
        if 'api_key' in kwargs and kwargs['api_key']:
            copied_obj.api_key = kwargs['api_key']
        if 'api_base' in kwargs and kwargs['api_base']:
            copied_obj.api_base = kwargs['api_base']
        if 'proxy' in kwargs and kwargs['proxy']:
            copied_obj.proxy = kwargs['proxy']
        if 'client_args' in kwargs and kwargs['client_args']:
            copied_obj.client_args = kwargs['client_args']
        return copied_obj

    @staticmethod
    def parse_result(chunk):
        """Generate the result of the stream."""
        chat_completion = chunk
        if not isinstance(chunk, dict):
            chunk = chunk.dict()
        if len(chunk["choices"]) == 0:
            return LLMOutput(text="", raw=chat_completion.model_dump())
        choice = chunk["choices"][0]
        message = choice.get("delta")
        text = message.get("content")
        if text is None:
            text = ""
        return LLMOutput(text=text, raw=chat_completion.model_dump())

    def generate_stream_result(self, stream: openai.Stream):
        """Generate the result of the stream."""
        for chunk in stream:
            llm_output = self.parse_result(chunk)
            if llm_output:
                yield llm_output

    async def agenerate_stream_result(self, stream: AsyncIterator) -> AsyncIterator[LLMOutput]:
        """Generate the result of the stream."""
        async for chunk in stream:
            llm_output = self.parse_result(chunk)
            if llm_output:
                yield llm_output

    def initialize_by_component_configer(self, component_configer: LLMConfiger) -> 'LLM':
        if 'api_base' in component_configer.configer.value:
            api_base = component_configer.configer.value.get('api_base')
            self.api_base = process_yaml_func(api_base, component_configer.yaml_func_instance)
        elif 'api_base_env' in component_configer.configer.value:
            self.api_base = get_from_env(component_configer.configer.value.get('api_base_env'))
        if 'api_key' in component_configer.configer.value:
            api_key = component_configer.configer.value.get('api_key')
            self.api_key = process_yaml_func(api_key, component_configer.yaml_func_instance)
        elif 'api_key_env' in component_configer.configer.value:
            self.api_key = get_from_env(component_configer.configer.value.get('api_key_env'))
        if 'organization' in component_configer.configer.value:
            organization = component_configer.configer.value.get('organization')
            self.organization = process_yaml_func(organization, component_configer.yaml_func_instance)
        if 'proxy' in component_configer.configer.value:
            proxy = component_configer.configer.value.get('proxy')
            self.proxy = process_yaml_func(proxy, component_configer.yaml_func_instance)
        if component_configer.configer.value.get("extra_headers"):
            self.ext_headers = component_configer.configer.value.get("extra_headers")
        if component_configer.configer.value.get("extra_params"):
            self.ext_params = component_configer.configer.value.get("extra_params")

        return super().initialize_by_component_configer(component_configer)

    def get_num_tokens(self, text: str) -> int:
        """Get the number of tokens present in the text.

        Useful for checking if an input will fit in an openai model's context window.

        Args:
            text: The string input to tokenize.

        Returns:
            The integer number of tokens in the text.
        """
        try:
            encoding = tiktoken.encoding_for_model(self.model_name)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        return len(encoding.encode(text))

    def max_context_length(self) -> int:
        """Return the maximum length of the context."""
        if super().max_context_length():
            return super().max_context_length()

    def get_billing_tokens(self, input: dict, output: LLMOutput):
        output_json = output.raw
        if "usage" in output_json and output_json['usage'].get("prompt_tokens", 0) > 0:
            return output_json['usage']
        messages = input.get("messages")
        text = ""
        for message in messages:
            content = message.get("content")
            if isinstance(content, str):
                text += content
            elif isinstance(content, list):
                for item in content:
                    if item.get("type") == "text":
                        content += item.get("content")
        prompt_tokens = self.get_num_tokens_from_model(text, model=input.get("model"))
        output = output.text
        completion_tokens = self.get_num_tokens_from_model(output, model=input.get("model"))
        total_tokens = prompt_tokens + completion_tokens
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }

    def billing_tokens_from_stream(self, generator: Iterator[LLMOutput],
                                   billing_center_params: BillingCenterInfo):
        content = ""
        usage = None
        for llm_output in generator:
            content += llm_output.text
            if "usage" in llm_output.raw and llm_output.raw.get("usage"):
                usage = llm_output.raw.get("usage")
            yield llm_output
        if usage:
            billing_center_params.usage = usage
            return
        llm_output = LLMOutput(
            text=content,
            raw={}
        )
        billing_center_params.output = llm_output.model_dump()
        billing_center_params.usage = self.get_billing_tokens(billing_center_params.input,
                                                              llm_output)

    async def async_billing_tokens_from_stream(self, generator: AsyncIterator[LLMOutput],
                                               billing_center_params: BillingCenterInfo):
        content = ""
        usage = None
        async for llm_output in generator:
            content += llm_output.text
            if "usage" in llm_output.raw and llm_output.raw.get("usage"):
                usage = llm_output.raw.get("usage")
            yield llm_output
        if usage:
            billing_center_params.usage = usage
            return
        llm_output = LLMOutput(
            text=content,
            raw={}
        )
        billing_center_params.output = llm_output.model_dump()
        billing_center_params.usage = self.get_billing_tokens(billing_center_params.input,
                                                              llm_output)

    def update_billing_center_params(self, params: BillingCenterInfo, input: dict):
        params.base_url = self.api_base
        return super().update_billing_center_params(params, input)
