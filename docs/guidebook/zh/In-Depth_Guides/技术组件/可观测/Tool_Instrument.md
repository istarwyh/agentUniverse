# Tool Instrumentor

该 Instrumentor 为 agentUniverse 框架提供自动化的 OpenTelemetry 追踪和指标收集功能，能够自动为使用 `@trace_tool` 装饰器的 Tool 调用创建 spans 和 metrics。

## Span 属性

当 Tool 被调用时，会自动创建一个 span 并设置以下属性：

### 基础属性

| 属性名 | 类型 | 描述 | 示例值 |
|--------|------|------|--------|
| `au.span.kind` | string | Span 类型标识 | `"tool"` |
| `au.tool.name` | string | Tool 的名称 | `"SearchTool"` |
| `au.tool.pair_id` | string | Tool 调用的配对 ID | `"tool-1234-5678"` |
| `au.tool.duration` | float | Tool 执行总时长（秒） | `0.856` |
| `au.tool.status` | string | Tool 执行状态 | `"success"` 或 `"error"` |

### 输入输出属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `au.tool.input` | string | Tool 输入参数的 JSON 序列化 |
| `au.tool.output` | string | Tool 输出结果的 JSON 序列化 |
| `au.trace.caller_info` | string | 调用者信息的 JSON 序列化 |

### Token 使用属性

| 属性名                               | 类型 | 描述           |
|-----------------------------------|------|--------------|
| `au.tool.usage.prompt_tokens`     | int | 提示词 token 数量 |
| `au.tool.usage.completion_tokens` | int | 生成 token 数量  |
| `au.tool.usage.total_tokens`      | int | 总 token 数量   |

### 错误属性（仅在出错时设置）

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `au.tool.error.type` | string | 错误类型（异常类名） |
| `au.tool.error.message` | string | 错误消息 |

## Metrics 指标

请注意 agentUniverse 中 Metric 统计方式为 `DELTA`。

### Counter 计数器

| 指标名 | 类型 | 单位 | 描述 | 标签 |
|--------|------|------|------|------|
| `tool_calls_total` | Counter | `1` | Tool 调用总次数 | `tool_name`, `caller` |
| `tool_errors_total` | Counter | `1` | Tool 错误总次数 | `tool_name`, `caller`, `error_type` |

### Histogram 直方图

| 指标名                      | 类型 | 单位 | 描述                     | 标签 |
|--------------------------|------|------|------------------------|------|
| `tool_call_duration`     | Histogram | `s` | Tool 调用持续时间分布          | `tool_name`, `caller` |
| `tool_total_tokens`      | Histogram | `1` | Tool 调用总 token 数量分布    | `tool_name`, `caller` |
| `tool_prompt_tokens`     | Histogram | `1` | Tool 调用提示词 token 数量分布 | `tool_name`, `caller` |
| `tool_completion_tokens` | Histogram | `1` | Tool 调用完成 token 数量分布  | `tool_name`, `caller` |

### Metric 标签说明

| 标签名 | 描述 | 可能值 |
|--------|------|--------|
| `tool_name` | Tool 的名称 | 任意字符串 |
| `caller` | 调用来源 | `"user"`, `"agent"`, 等 |
| `error_type` | 错误类型（仅错误指标） | 异常类名，如 `"ValueError"` |

