# !/usr/bin/env python3
# -*- coding:utf-8 -*-

import os
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager


AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)
file_path = "./test_doc.docx"
absolute_path = os.path.abspath(file_path)


def chat(question: str):
    instance: Agent = AgentManager().get_instance_obj('demo_react_agent_with_all_tools')
    instance.run(input=question)


if __name__ == '__main__':
    # 在运行该案例前，你可以通过根目录下的uv_install.sh的脚本来安装案例中用到的MCP工具和运行环境。
    # Before running this case, you can install the MCP tool and runtime
    # environment used in the case by executing the uv_install.sh script
    # located in the root directory.

    chat(f"帮我完成以下几个任务："
         f"1.给出一段python代码，可以判断数字是否为素数，给出之前必须验证代码是否可以运行，最少验证1次\n"
         f"2.请先帮我计算38x67，再帮我算一下114/514\n"
         f"3.帮我查一查2025年支付宝联动的游戏有哪些\n"
         f"4.查看{absolute_path}中的内容，并找到用户goldenhawk15的密码，然后也在同样的路径下创建一个新的docx文件把密码写进去")
