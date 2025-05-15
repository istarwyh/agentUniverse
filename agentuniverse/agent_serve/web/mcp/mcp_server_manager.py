# !/usr/bin/env python3
# -*- coding:utf-8 -*-
import functools
import inspect
from typing import Literal

from mcp.server.fastmcp import FastMCP

from agentuniverse.agent.action.tool.tool import Tool
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.agent.action.toolkit.toolkit_manager import ToolkitManager
from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.component.component_enum import ComponentEnum
from agentuniverse.base.config.component_configer.component_configer import \
    ComponentConfiger

# @Time    : 2025/5/8 17:37
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: mcp_server_manager.py


DEFAULT_SERVER_NAME = 'default_mcp_server'


def is_method_overridden(
        override_method: callable,
        origin_method: callable) -> bool:
    if not callable(override_method):
        return False

    is_overridden = False
    if origin_method is None:
        is_overridden = True
    elif override_method is not origin_method:
        is_overridden = True

    return is_overridden


def create_exposed_tool_method_wrapper(tool_name):
    method_name = 'async_execute'
    original_method = getattr(ToolManager().get_instance_obj(tool_name).__class__, method_name)

    # If async_execute method hasn't been overridden, use execute method
    if not is_method_overridden(
        original_method,
        getattr(Tool, method_name)
    ):
        method_name = 'execute'
        original_method = getattr(ToolManager().get_instance_obj(tool_name).__class__, method_name)

    original_signature = inspect.signature(original_method)
    original_parameters = list(original_signature.parameters.values())

    exposed_parameters = original_parameters[1:]

    exposed_signature = inspect.Signature(
        parameters=exposed_parameters,
        return_annotation=original_signature.return_annotation
    )

    if inspect.iscoroutinefunction(original_method):
        @functools.wraps(original_method)
        async def wrapper(*args, **kwargs):
            instance = ToolManager().get_instance_obj(tool_name)
            return await getattr(instance, method_name)(*args, **kwargs)
    else:
        @functools.wraps(original_method)
        def wrapper(*args, **kwargs):
            instance = ToolManager().get_instance_obj(tool_name)
            return getattr(instance, method_name)(*args, **kwargs)
    wrapper.__signature__ = exposed_signature

    return wrapper


@singleton
class MCPServerManager:
    server_tool_map: dict = {
        DEFAULT_SERVER_NAME: {
            'tool': [],
            'toolkit': []
        }
    }

    def register_mcp_tool(self, configer_instance: ComponentConfiger, configer_type: str):
        if isinstance(configer_instance.as_mcp_tool, dict):
            mcp_tool_config = configer_instance.as_mcp_tool
            server_name = mcp_tool_config.get('server_name', DEFAULT_SERVER_NAME)
            if server_name not in self.server_tool_map:
                self.server_tool_map[server_name] = {
                    'tool': [],
                    'toolkit': []
                }
        else:
            server_name = DEFAULT_SERVER_NAME

        if configer_type == ComponentEnum.TOOL.value:
            self.server_tool_map[server_name]['tool'].append(configer_instance.name)
        else:
            self.server_tool_map[server_name]['toolkit'].append(configer_instance.name)

    def start_server(self,
                     host: str = '0.0.0.0',
                     port: int = 8890,
                     transport: Literal["sse", "streamable_http"] = "sse"):
        # TODO: support streamable http server in next version.
        import uvicorn
        from mcp.server.fastmcp import FastMCP
        from starlette.applications import Starlette
        from starlette.routing import Mount
        routes_list = []

        for server_name, tool_dict in self.server_tool_map.items():
            mcp_server = FastMCP(server_name)

            for _tool in tool_dict['tool']:
                tool_instance = ToolManager().get_instance_obj(_tool)
                mcp_server.add_tool(
                    fn=create_exposed_tool_method_wrapper(_tool),
                    name=tool_instance.name,
                    description=tool_instance.description
                )

            for _toolkit in tool_dict['toolkit']:
                toolkit_instance = ToolkitManager().get_instance_obj(_toolkit)
                for _tool in toolkit_instance.tool_names:
                    tool_instance = ToolManager().get_instance_obj(_tool)
                    mcp_server.add_tool(
                        fn=create_exposed_tool_method_wrapper(_tool),
                        name=tool_instance.name,
                        description=tool_instance.description
                    )
            routes_list.append(Mount(f"/{server_name}", app=mcp_server.sse_app(f"/{server_name}")),)
        app = Starlette(routes=routes_list)
        uvicorn.run(app, host=host, port=port)
