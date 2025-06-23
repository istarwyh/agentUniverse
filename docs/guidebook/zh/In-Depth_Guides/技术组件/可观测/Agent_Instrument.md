# Agent Instrument


该 Instrumentor 为 agentUniverse 框架提供自动化的 OpenTelemetry 追踪和指标收集功能，能够自动为使用 `@trace_agent` 装饰器的 Agent 调用创建 spans 和 metrics。


## Span 属性

当 Agent 被调用时，会自动创建一个 span 并设置以下属性：

### 基础属性

| 属性名 | 类型 | 描述 | 示例值                     |
|--------|------|------|-------------------------|
| `au.span.kind` | string | Span 类型标识 | `"agent"`               |
| `au.agent.name` | string | Agent 的名称 | `"ChatAgent"`           |
| `au.agent.pair_id` | string | Agent 调用的配对 ID | `"agent-1234-5678"`     |
| `au.agent.duration` | float | Agent 执行总时长（秒） | `1.234`                 |
| `au.agent.status` | string | Agent 执行状态 | `"success"` 或 `"error"` |

### 输入输出属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `au.agent.input` | string | Agent 输入参数的 JSON 序列化 |
| `au.agent.output` | string | Agent 输出结果的 JSON 序列化 |
| `au.trace.caller_info` | string | 调用者信息的 JSON 序列化 |
| `au.agent.first_token.duration` | float | 首个 token 响应时间（秒） |

### Token 使用属性

| 属性名                                | 类型 | 描述           |
|------------------------------------|------|--------------|
| `au.agent.usage.prompt_tokens`     | int | 提示词 token 数量 |
| `au.agent.usage.completion_tokens` | int | 生成 token 数量  |
| `au.agent.usage.total_tokens`      | int | 总 token 数量   |

### 错误属性（仅在出错时设置）

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `au.agent.error.type` | string | 错误类型（异常类名） |
| `au.agent.error.message` | string | 错误消息 |

## Metrics 指标

请注意agentUniverse中Metric统计方式为`DELTA`。

### Counter 计数器

| 指标名 | 类型 | 单位 | 描述 | 标签 |
|--------|------|------|------|------|
| `agent_calls_total` | Counter | `1` | Agent 调用总次数 | `agent_name`, `caller`, `streaming` |
| `agent_errors_total` | Counter | `1` | Agent 错误总次数 | `agent_name`, `caller`, `error_type`, `streaming` |

### Histogram 直方图

| 指标名                          | 类型 | 单位 | 描述                     | 标签 |
|------------------------------|------|------|------------------------|------|
| `agent_call_duration`        | Histogram | `s` | Agent 调用持续时间分布         | `agent_name`, `caller`, `streaming` |
| `agent_first_token_duration` | Histogram | `s` | 首个 token 响应时间分布        | `agent_name`, `caller`, `streaming` |
| `agent_total_tokens`         | Histogram | `1` | Agent 调用总 token 数量分布   | `agent_name`, `caller`, `streaming` |
| `agent_prompt_tokens`        | Histogram | `1` | Agent 调用提示词 token 数量分布 | `agent_name`, `caller`, `streaming` |
| `agent_completion_tokens`    | Histogram | `1` | Agent 调用完成 token 数量分布  | `agent_name`, `caller`, `streaming` |

### Metric 标签说明

| 标签名 | 描述 | 可能值 |
|--------|------|--------|
| `agent_name` | Agent 的名称 | 任意字符串 |
| `caller` | 调用来源 | `"user"`, `"agent"`, 等 |
| `streaming` | 是否为流式调用 | `true`, `false` |
| `error_type` | 错误类型（仅错误指标） | 异常类名，如 `"ValueError"` |

