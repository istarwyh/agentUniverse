import asyncio
import functools
from concurrent.futures.thread import ThreadPoolExecutor
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.base.util.manager.billing_center_manager import BillingCenterManager, BillingCenter, \
    BillingCenterInfo
from agentuniverse.llm.llm_output import LLMOutput

thread_pool = ThreadPoolExecutor(max_workers=5)

def trace_billing(func):
    @functools.wraps(func)
    async def wrapper_async(*args, **kwargs):
        billing_type = BillingCenterManager().billing_center_type
        if not BillingCenterManager().use_billing_center:
            result = func(*args, **kwargs)
            return result
        billing_center_info = BillingCenterInfo()
        if billing_type == "proxy":
            extra_headers = BillingCenter.llm_headers(args[0], billing_center_info)
            api_base = BillingCenterManager().billing_center_url
            kwargs['extra_headers'] = extra_headers
            kwargs['api_base'] = api_base
            return func(*args, **kwargs)
        llm = args[0]
        BillingCenter.update_billing_center_params(llm, billing_center_info, kwargs)
        result = func(*args, **kwargs)
        if isinstance(result, LLMOutput):
            billing_center_info.usage = BillingCenter.get_billing_tokens(kwargs, result)
            billing_center_info.output = result.model_dump()
            LOGGER.info(f"Billing info {billing_center_info.usage}")
            thread_pool.submit(billing_center_info.push_billing_center_info)
        else:
            async def generator():
                async for item in BillingCenter.async_billing_tokens_from_stream(llm, result, billing_center_info):
                    yield item
                LOGGER.info(f"Billing info {billing_center_info.usage}")
                thread_pool.submit(billing_center_info.push_billing_center_info)

            return generator()
        return result

    @functools.wraps(func)
    def wrapper_sync(*args, **kwargs):
        billing_type = BillingCenterManager().billing_center_type
        if not BillingCenterManager().use_billing_center:
            result = func(*args, **kwargs)
            return result
        billing_center_info = BillingCenterInfo()
        if billing_type == "proxy":
            extra_headers = BillingCenter.llm_headers(args[0], billing_center_info)
            api_base = BillingCenterManager().billing_center_url
            kwargs['extra_headers'] = extra_headers
            kwargs['api_base'] = api_base
            return func(*args, **kwargs)
        result = func(*args, **kwargs)
        llm = args[0]
        BillingCenter.update_billing_center_params(llm, billing_center_info, kwargs)
        if isinstance(result, LLMOutput):
            billing_center_info.usage = BillingCenter.get_billing_tokens(llm, kwargs, result)
            billing_center_info.output = result.model_dump()
            LOGGER.info(f"Billing info {billing_center_info.usage}")
            thread_pool.submit(billing_center_info.push_billing_center_info)
            return result
        else:
            def generator():
                for item in BillingCenter.billing_tokens_from_stream(llm, result, billing_center_info):
                    yield item
                LOGGER.info(f"Billing info {billing_center_info.usage}")
                thread_pool.submit(billing_center_info.push_billing_center_info)

            return generator()

    if asyncio.iscoroutinefunction(func):
        # async function
        return wrapper_async
    else:
        # sync function
        return wrapper_sync
