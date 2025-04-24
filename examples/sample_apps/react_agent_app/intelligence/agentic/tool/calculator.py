# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/4/24 16:37
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: calculator.py
import asyncio
import random

from mcp.server.fastmcp import FastMCP, Context

# 创建MCP服务器
mcp = FastMCP("LocalDemo")


# 实现计算器工具
@mcp.tool()
def calculator(operation: str, x: float, y: float) -> str:
    """执行基本数学运算

    Args:
        operation: 操作类型 (add, subtract, multiply, divide)
        x: 第一个数字
        y: 第二个数字
    """
    if operation == "add":
        return f"{x} + {y} = {x + y}"
    elif operation == "subtract":
        return f"{x} - {y} = {x - y}"
    elif operation == "multiply":
        return f"{x} * {y} = {x * y}"
    elif operation == "divide":
        if y == 0:
            return "错误: 除数不能为零"
        return f"{x} / {y} = {x / y}"
    else:
        return f"不支持的操作: {operation}"


@mcp.tool()
def no_use_tool(input: str) -> str:
    """
        无效的工具
    """
    pass


if __name__ == "__main__":
    mcp.run(transport="stdio")
