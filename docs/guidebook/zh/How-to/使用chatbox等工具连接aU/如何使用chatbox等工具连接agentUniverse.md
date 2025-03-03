# 使用chatbox连接agentUniverse

chatbox、cherrystudio等工具支持连接各类遵循OpenAI格式输出的模型，并以会话的形式展示出来。为了方便大家的调试，我们提供了遵循OpenAI协议的template。

## 1. 准备工作

首先 下载并安装CherryStudio: [https://cherry-ai.com/download] 
或者下载并安装Chatbox: [https://chatboxai.app/zh#download]

其次 准备一个agentUniverse项目，并可以运行sample standard app当中的demo_agent

## 2. 在aU项目中创建一个符合OpenAI 格式的Agent

* 创建智能体py文件
  在项目中intelligence/agentic/agent/agent_template目录下创建一个openai_protocol_agent.py文件，内容如下：

```python

from agentuniverse.agent.input_object import InputObject

from agentuniverse.agent.template.openai_protocol_template import OpenAIProtocolTemplate


class DemoOpenAIProtocolAgent(OpenAIProtocolTemplate):

    def input_keys(self) -> list[str]:
        return ['input']

    def output_keys(self) -> list[str]:
        return ['output']

    def parse_input(self, input_object: InputObject, agent_input: dict) -> dict:
        agent_input['input'] = input_object.get_data('input')
        return agent_input

    def parse_result(self, agent_result: dict) -> dict:
        return {**agent_result, 'output': agent_result['output']}
```

* 在intelligence/agentic/agent/agent_instance目录下创建智能体openai_protocol_agent.yaml文件,

```yaml
info:
  #  Please fill in the basic info of your agent. The following is a sample.
  name: 'openai_protocol_agent'
  description: 'demo agent'
profile:
  # Please fill in the profile of your agent. The following is a sample.
  prompt_version: demo_agent.cn
  # Please select the llm.
  llm_model:
    # you can change this config to a customized LLM
    # e.g. demo_llm, which defined in /intelligence/agentic/llm/demo_llm.yaml
    name: 'qwen_25_72b_llm'
action:
  # Please select the tools and knowledge base.
  tool:
    # here we use a mock_search_tool to mock a search result
    # you can change to customized search tool
    # e.g. demo_search_tool, to do a real internet search
    # for using demo_search_tool, you need to get either /Google/Bing/search.io search API key
    # and config it into /config/custom_key.toml
    - 'mock_search_tool'
  knowledge:
  # advantage feature，please refer to doc
memory:
  name: 'demo_memory'
metadata:
  type: AGENT
  class: DemoOpenAIProtocolAgent

```

* 在intelligence/service/agent_service目录下，创建openai_agent_service.yaml文件

```yaml
name: 'openai_service'
description: 'demo service of demo agent'
agent: 'openai_protocol_agent'
metadata:
  type: 'SERVICE'
```

## 3. 配置 chatbox 或者 cherrystudio

* 启动chatbox，并打开一个会话窗口。打开后的主界面如图：  
  <img src="../../../_picture/chatbox_main_page.png" width="600" />
* 点击主页中设置按钮，进入设置页面进行配置。  
  <img src= "../../../_picture/chatbox_setting_page.png" width="600" />
  * 配置注意：
    * 配置API域名：http://127.0.0.1:8888
    * 配置API路径：/chat/completions
    * 配置模型：openai_service,即你所创建的agent service
    * API密钥：随意配置
    * 名称：可以任意配置
* 点击保存

## 4. 测试
* 在chatbox中输入任意内容，点击发送按钮，即可看到agent的输出。如图:  
<img src="../../../_picture/chatbox_test_result.png" width="600" />




