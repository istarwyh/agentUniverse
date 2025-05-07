import asyncio
import functools
import json
from concurrent.futures.thread import ThreadPoolExecutor
from typing import Optional, Any

import httpx

from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.llm.llm_output import LLMOutput
from pydantic import BaseModel

from agentuniverse.base.config.application_configer.application_config_manager import ApplicationConfigManager
from agentuniverse.base.util.monitor.monitor import Monitor
from agentuniverse.base.util.tracing.au_trace_manager import AuTraceManager

client = httpx.Client(timeout=60)
thread_pool = ThreadPoolExecutor(max_workers=5)


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
            scene_code = AuTraceManager().get_scene_code()
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
        endpoint = ApplicationConfigManager().app_configer.billing_center_url + "/billing/token/usage"
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


def trace_billing(func):
    @functools.wraps(func)
    async def wrapper_async(*args, **kwargs):
        billing_type = ApplicationConfigManager().app_configer.billing_center.get("billing_type")
        result = await func(*args, **kwargs)
        if not ApplicationConfigManager().app_configer.use_billing_center:
            return result
        if billing_type == "proxy":
            return result
        billing_center_params = kwargs.pop("billing_center_params", None)
        if not billing_center_params:
            billing_center_params = BillingCenterInfo()
        llm = args[0]
        llm.update_billing_center_params(billing_center_params, kwargs)
        if isinstance(result, LLMOutput):
            billing_center_params.usage = llm.get_billing_tokens(kwargs, result)
            billing_center_params.output = result.model_dump()
            LOGGER.info(f"Billing info {billing_center_params.usage}")
            thread_pool.submit(billing_center_params.push_billing_center_info)
        else:
            async def generator():
                async for item in llm.async_billing_tokens_from_stream(result, billing_center_params):
                    yield item
                LOGGER.info(f"Billing info {billing_center_params.usage}")
                thread_pool.submit(billing_center_params.push_billing_center_info)

            return generator()
        return result

    @functools.wraps(func)
    def wrapper_sync(*args, **kwargs):
        billing_type = ApplicationConfigManager().app_configer.billing_center.get("billing_type")
        result = func(*args, **kwargs)
        if not ApplicationConfigManager().app_configer.use_billing_center:
            return result
        if billing_type == "proxy":
            return result
        billing_center_params = kwargs.pop("billing_center_params", None)
        if not billing_center_params:
            billing_center_params = BillingCenterInfo()
        llm = args[0]
        llm.update_billing_center_params(billing_center_params, kwargs)
        if isinstance(result, LLMOutput):
            billing_center_params.usage = llm.get_billing_tokens(kwargs, result)
            billing_center_params.output = result.model_dump()
            LOGGER.info(f"Billing info {billing_center_params.usage}")
            thread_pool.submit(billing_center_params.push_billing_center_info)
            return result
        else:
            def generator():
                for item in llm.billing_tokens_from_stream(result, billing_center_params):
                    yield item
                LOGGER.info(f"Billing info {billing_center_params.usage}")
                thread_pool.submit(billing_center_params.push_billing_center_info)

            return generator()

    if asyncio.iscoroutinefunction(func):
        # async function
        return wrapper_async
    else:
        # sync function
        return wrapper_sync


class BillingCenter(BaseModel):

    @classmethod
    def get_base_url(cls, base_url: str):
        billing_type = ApplicationConfigManager().app_configer.billing_center.get("billing_type")
        if ApplicationConfigManager().app_configer.use_billing_center and billing_type == "proxy":
            return ApplicationConfigManager().app_configer.billing_center_url
        return base_url

    @classmethod
    def billing_center_openai_channel_headers(cls, llm, params_map: dict[str, Any]):
        billing_type = ApplicationConfigManager().app_configer.billing_center.get("billing_type")
        if not ApplicationConfigManager().app_configer.use_billing_center:
            return llm.channel_ext_headers, params_map
        if billing_type == "push":
            params_map.pop("billing_center_params")
            return llm.channel_ext_headers, params_map
        billing_center_params: BillingCenterInfo = params_map.pop("billing_center_params")
        extra_headers = billing_center_params.model_dump(
            include={'agent_id', 'app_id', 'scene_code', 'session_id', 'trace_id'}
        )
        extra_headers["OriginalUrl"] = llm.channel_api_base
        if llm.channel_proxy:
            extra_headers["proxy"] = llm.channel_proxy if llm.channel_proxy else ""
        return {**llm.channel_ext_headers, **extra_headers}, params_map

    @classmethod
    def billing_center_openai_headers(cls, llm, params_map: dict[str, Any]):
        billing_type = ApplicationConfigManager().app_configer.billing_center.get("billing_type")
        if not ApplicationConfigManager().app_configer.use_billing_center:
            return llm.ext_headers, params_map
        if billing_type == "push":
            params_map.pop("billing_center_params")
            return llm.ext_headers, params_map
        billing_center_params: BillingCenterInfo = params_map.pop("billing_center_params")
        extra_headers = billing_center_params.model_dump(
            include={'agent_id', 'app_id', 'scene_code', 'session_id', 'trace_id'}
        )
        extra_headers["OriginalUrl"] = llm.api_base
        if llm.proxy:
            extra_headers["proxy"] = llm.proxy
        return {**llm.ext_headers, **extra_headers}, params_map
