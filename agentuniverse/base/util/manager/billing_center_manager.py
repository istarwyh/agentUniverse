# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/5/9 09:32
# @Author  : weizjajj
# @Email   : weizhongjie.wzj@antgroup.com
# @FileName: billing_center_manager.py
import json
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Iterator, AsyncIterator, Optional

import httpx

from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.context.framework_context_manager import FrameworkContextManager
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.base.util.monitor.monitor import Monitor
from agentuniverse.base.util.tracing.au_trace_manager import AuTraceManager
from agentuniverse.llm.llm_channel.llm_channel import LLMChannel
from agentuniverse.llm.openai_style_llm import OpenAIStyleLLM

from agentuniverse.llm.llm_output import LLMOutput
from pydantic import BaseModel

from agentuniverse.base.annotation.singleton import singleton

client = httpx.Client(timeout=60)


class BillingCenterInfo(BaseModel):
    app_id: Optional[str] = None
    agent_id: Optional[str] = None
    session_id: Optional[str] = None
    trace_id: Optional[str] = None
    scene_code: Optional[str] = None
    base_url: Optional[str] = ""
    model: Optional[str] = None
    usage: Optional[dict] = None
    input: Optional[dict] = None
    output: Optional[dict] = None

    def __init__(self, **kwargs):
        params = kwargs
        app_id = ApplicationConfigManager().app_configer.base_info_appname
        params['app_id'] = app_id
        agent_id = kwargs.get("agent_id", None)
        if not agent_id:
            agent_id = self._get_caller_agent()
        params['agent_id'] = agent_id
        if not kwargs.get("trace_id"):
            trace_id = AuTraceManager().get_trace_id()
            params['trace_id'] = trace_id
        if not kwargs.get("session_id"):
            session_id = AuTraceManager().get_session_id()
            params['session_id'] = session_id
        if not kwargs.get("scene_code"):
            scene_code = FrameworkContextManager().get_context("scene_code")
            params["scene_code"] = scene_code
        super().__init__(**params)

    @staticmethod
    def _get_caller_agent():
        source_list = Monitor.get_invocation_chain()
        if len(source_list) > 0:
            # 逆序遍历
            for item in reversed(source_list):
                if item.get("type") == "agent":
                    return item.get("source", None)
        return "unknown"

    def push_billing_center_info(self):
        params = self.model_dump()
        LOGGER.info(json.dumps(params, ensure_ascii=False, indent=4))
        endpoint = BillingCenterManager().billing_center_url + "/billing/token/usage"
        response = client.post(
            endpoint, json=params, headers={
                "content-type": "application/json"
            }
        )
        if response.status_code != 200:
            LOGGER.error(f"Push billing center info error {params}")
        else:
            LOGGER.info(
                f"Push billing center success {json.dumps(params, ensure_ascii=False, indent=4)}")


@singleton
class BillingCenterManager:
    def __init__(self, configer=None):
        billing_center_info = configer.value.get("BILLING_CENTER")
        self.use_billing_center = billing_center_info.get("use_billing_center")
        self.billing_center_url = billing_center_info.get("billing_center_url")
        self.billing_center_type = billing_center_info.get("billing_type")


class BillingCenter(BaseModel):

    @classmethod
    def llm_headers(cls, llm, billing_center_info: BillingCenterInfo):
        extra_headers = None
        if hasattr(llm, "ext_headers"):
            extra_headers = llm.ext_headers
        elif hasattr(llm, "headers"):
            extra_headers = llm.headers
        if not extra_headers:
            extra_headers = {
                "content-type": "application/json"
            }
        extra_headers = extra_headers.copy()
        keys = ['agent_id', 'app_id', 'scene_code', 'session_id', 'trace_id']
        billing_center_info_dict = billing_center_info.model_dump()
        for key in keys:
            extra_headers[key] = billing_center_info_dict.get(key, "") if billing_center_info_dict.get(key) else ""
        if isinstance(llm, OpenAIStyleLLM):
            extra_headers["base_url"] = llm.api_base
            if llm.proxy:
                extra_headers["proxy"] = llm.proxy
            return extra_headers
        elif isinstance(llm, LLMChannel):
            extra_headers["base_url"] = llm.channel_api_base
            if llm.channel_proxy:
                extra_headers["proxy"] = llm.channel_proxy
        else:
            extra_headers["base_url"] = llm.model_name
        return extra_headers

    @classmethod
    def get_base_url(cls, base_url: str):
        billing_type = BillingCenterManager().billing_center_type
        if BillingCenterManager().use_billing_center and billing_type == "proxy":
            return BillingCenterManager().billing_center_url
        return base_url

    @classmethod
    def billing_tokens_from_stream(cls, llm, generator: Iterator[LLMOutput],
                                   billing_center_params: BillingCenterInfo):
        content = ""
        usage = None
        for llm_output in generator:
            content += llm_output.text
            if "usage" in llm_output.raw and llm_output.raw.get("usage"):
                usage = llm_output.raw.get("usage")
            yield llm_output
        llm_output = LLMOutput(
            text=content,
            raw={}
        )
        billing_center_params.output = llm_output.model_dump()
        if usage:
            billing_center_params.usage = usage
            return

        billing_center_params.usage = cls.get_billing_tokens(llm, billing_center_params.input,
                                                             llm_output)

    @classmethod
    async def async_billing_tokens_from_stream(cls, llm, generator: AsyncIterator[LLMOutput],
                                               billing_center_params: BillingCenterInfo):
        content = ""
        usage = None
        async for llm_output in generator:
            content += llm_output.text
            if "usage" in llm_output.raw and llm_output.raw.get("usage"):
                usage = llm_output.raw.get("usage")
            yield llm_output
        llm_output = LLMOutput(
            text=content,
            raw={}
        )
        billing_center_params.output = llm_output.model_dump()
        if usage:
            billing_center_params.usage = usage
            return
        billing_center_params.usage = cls.get_billing_tokens(llm, billing_center_params.input,
                                                             llm_output)

    @classmethod
    def update_billing_center_params(cls, llm, params: BillingCenterInfo, input: dict) -> BillingCenterInfo:
        if "model" in input:
            params.model = input.get("model")
        else:
            params.model = llm.model_name

        if isinstance(llm, LLMChannel):
            params.base_url = llm.channel_api_base
        elif isinstance(llm, OpenAIStyleLLM):
            params.base_url = llm.api_base
        elif getattr(llm, "service_id"):
            params.base_url = llm.service_id
        elif getattr(llm, "serviceId"):
            params.base_url = llm.serviceId
        elif getattr(llm, "endpoint"):
            params.base_url = llm.endpoint
        else:
            params = llm.model_name
        return params

    @classmethod
    def _get_billing_tokens(cls, llm, input: dict, output: LLMOutput) -> dict:
        text = ""
        if "messages" in input:
            messages = input.get("messages")
            for message in messages:
                content = message.get("content")
                if isinstance(content, str):
                    text += content
                elif isinstance(content, list):
                    for item in content:
                        if item.get("type") == "text":
                            text += item.get("content")
        elif "prompt" in input:
            text = str(input.get("prompt"))
        prompt_tokens = llm.get_num_tokens(text)
        output = output.text
        completion_tokens = llm.get_num_tokens(output)
        total_tokens = prompt_tokens + completion_tokens
        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }

    @classmethod
    def get_billing_tokens(cls, llm, input: dict, output: LLMOutput):
        output_json = output.raw
        if "usage" in output_json and output_json['usage'].get("prompt_tokens", 0) > 0:
            return output_json['usage']
        return cls._get_billing_tokens(llm, input, output)
