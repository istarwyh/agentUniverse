# LLM Instrumentor

该 Instrumentor 为 agentUniverse 框架提供自动化的 OpenTelemetry 追踪和指标收集功能，能够自动为使用 `@trace_llm` 装饰器的 LLM 调用创建 spans 和 metrics。

## Span 属性

当 LLM 被调用时，会自动创建一个 span 并设置以下属性：

### 基础属性

| 属性名 | 类型 | 描述 | 示例值                         |
|--------|------|------|-----------------------------|
| `au.span.kind` | string | Span 类型标识 | `"llm"`                     |
| `au.llm.name` | string | LLM 的名称 | `"gpt-4o"`                  |
| `au.llm.channel_name` | string | LLM 通道名称 | `"openai_official_channel"` |
| `au.llm.duration` | float | LLM 执行总时长（秒） | `1.234`                     |
| `au.llm.status` | string | LLM 执行状态 | `"success"` 或 `"error"`     |

### 输入输出属性

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `au.llm.input` | string | LLM 输入参数的 JSON 序列化 |
| `au.llm.llm_params` | string | LLM 参数配置的 JSON 序列化 |
| `au.trace.caller_info` | string | 调用者信息的 JSON 序列化 |
| `au.llm.first_token.duration` | float | 首个 token 响应时间（秒） |

### Token 使用属性

| 属性名 | 类型 | 描述           |
|--------|------|--------------|
| `au.llm.usage.prompt_tokens` | int | 提示词 token 数量 |
| `au.llm.usage.completion_tokens` | int | 生成 token 数量  |
| `au.llm.usage.total_tokens` | int | 总 token 数量   |

### 错误属性（仅在出错时设置）

| 属性名 | 类型 | 描述 |
|--------|------|------|
| `au.llm.error.type` | string | 错误类型（异常类名） |
| `au.llm.error.message` | string | 错误消息 |

## Metrics 指标

请注意 agentUniverse 中 Metric 统计方式为 `DELTA`。

### Counter 计数器

| 指标名 | 类型 | 单位 | 描述 | 标签 |
|--------|------|------|------|------|
| `llm_calls_total` | Counter | `1` | LLM 调用总次数 | `llm_name`, `channel_name`, `caller` |
| `llm_errors_total` | Counter | `1` | LLM 错误总次数 | `llm_name`, `channel_name`, `caller`, `error_type` |

### Histogram 直方图

| 指标名 | 类型 | 单位 | 描述 | 标签 |
|--------|------|------|------|------|
| `llm_call_duration` | Histogram | `s` | LLM 调用持续时间分布 | `llm_name`, `channel_name`, `caller` |
| `llm_first_token_duration` | Histogram | `s` | 首个 token 响应时间分布 | `llm_name`, `channel_name`, `caller`, `streaming` |
| `llm_total_tokens` | Histogram | `1` | LLM 调用总 token 数量分布 | `llm_name`, `channel_name`, `caller` |
| `llm_prompt_tokens` | Histogram | `1` | LLM 调用提示词 token 数量分布 | `llm_name`, `channel_name`, `caller` |
| `llm_completion_tokens` | Histogram | `1` | LLM 调用完成 token 数量分布 | `llm_name`, `channel_name`, `caller` |

### Metric 标签说明

| 标签名 | 描述 | 可能值 |
|--------|------|--------|
| `llm_name` | LLM 的名称 | 任意字符串 |
| `channel_name` | LLM 通道名称 | 任意字符串 |
| `caller` | 调用来源 | `"user"`, `"agent"`, 等 |
| `streaming` | 是否为流式调用 | `true`, `false` |
| `error_type` | 错误类型（仅错误指标） | 异常类名，如 `"ValueError"` |

## 常量定义

```python
#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/6/10 15:01
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: consts.py

INSTRUMENTOR_NAME = "opentelemetry-instrumentation-agentuniverse-llm"
INSTRUMENTOR_VERSION = "0.1.0"

# Metric names
class MetricNames:
    """Metric name constants."""
    LLM_CALLS_TOTAL = "llm_calls_total"
    LLM_ERRORS_TOTAL = "llm_errors_total"
    LLM_CALL_DURATION = "llm_call_duration"
    LLM_FIRST_TOKEN_DURATION = "llm_first_token_duration"
    LLM_TOTAL_TOKENS = "llm_total_tokens"
    LLM_PROMPT_TOKENS = "llm_prompt_tokens"
    LLM_COMPLETION_TOKENS = "llm_completion_tokens"

# Span attribute names
class SpanAttributes:
    """Span attribute name constants."""
    # Basic span attributes
    SPAN_KIND = "au.span.kind"
    AU_LLM_NAME = "au.llm.name"
    AU_LLM_CHANNEL_NAME = "au.llm.channel_name"
    AU_LLM_INPUT = "au.llm.input"
    AU_LLM_LLM_PARAMS = "au.llm.llm_params"
    AU_TRACE_CALLER_INFO = "au.trace.caller_info"

    # Status and timing attributes
    AU_LLM_DURATION = "au.llm.duration"
    AU_LLM_STATUS = "au.llm.status"
    AU_LLM_FIRST_TOKEN_DURATION = "au.llm.first_token.duration"

    # Token usage attributes
    AU_LLM_USAGE_PROMPT_TOKENS = "au.llm.usage.prompt_tokens"
    AU_LLM_USAGE_COMPLETION_TOKENS = "au.llm.usage.completion_tokens"
    AU_LLM_USAGE_TOTAL_TOKENS = "au.llm.usage.total_tokens"

    # Error attributes
    AU_LLM_ERROR_TYPE = "au.llm.error.type"
    AU_LLM_ERROR_MESSAGE = "au.llm.error.message"

# Metric label names
class MetricLabels:
    """Metric label name constants."""
    ERROR_TYPE = "error_type"
    STREAMING = "streaming"
    LLM_NAME = "llm_name"
    CHANNEL_NAME = "channel_name"
    CALLER = "caller"
```
