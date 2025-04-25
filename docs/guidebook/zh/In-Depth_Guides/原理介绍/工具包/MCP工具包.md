# 如何定义一个MCP工具包

MCPToolkit是工具包中的一个特殊分类，它能够通过配置链接MCPServer，获取工具信息，并通过这些信息自动创建对应的MCPTool。

根据MCPServer的种类可分为两类，一是通过标准输入输出流连接的MCPServer，另一种是通过SSE连接的MCPServer。

通过标准输入输出流连接的MCPToolkit定义示例如下：
```yaml
name: 'weather_toolkit'
description: |
  这是一个天气相关的工具包
transport: 'stdio'
command: 'python'
args:
  - 'stdio_server.py'
env:
  TIMEOUT: 100

metadata:
  type: 'TOOLKIT'
  module: 'agentuniverse.agent.action.toolkit.mcp_toolkit'
  class: 'MCPToolkit'
```

通过SSE连接的MCPToolkit定义示例如下：
```yaml
name: 'search_toolkit'
description: |
  这是一个搜索相关的工具包
transport: 'sse'
url: 'http://localhost:8000/sse'

metadata:
  type: 'TOOLKIT'
  module: 'agentuniverse.agent.action.toolkit.mcp_toolkit'
  class: 'MCPToolkit'
```

- 关于`transport`、`url`、`command`、`args`、`env`参数的填写方式请参考[MCP工具](../工具/MCP工具.md)