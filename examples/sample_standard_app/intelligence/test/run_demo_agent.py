# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/4/1 14:32
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: test_rag_agent.py

from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager
from agentuniverse.base.agentuniverse import AgentUniverse

AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)


def chat(question: str):
    """ Peer agents example.

    The peer agents in agentUniverse become a chatbot and can ask questions to get the answer.
    """
    instance: Agent = AgentManager().get_instance_obj('demo_agent')
    output_object = instance.run(input=question)
    res_info = f"\nDemo agent execution result is :\n"
    res_info += output_object.get_data('output')
    print(res_info)


if __name__ == '__main__':
    chat("分析下巴菲特减持比亚迪的原因")

# class DemoAgentTest(unittest.TestCase):
#     """
#     Test cases for the rag agent
#     """
#
#     def setUp(self) -> None:
#         pass
#
#     def test_demo_agent(self):
#         chat("分析下巴菲特减持比亚迪的原因")
#
#
# if __name__ == '__main__':
#     unittest.main()
