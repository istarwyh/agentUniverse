# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/2/17 11:09
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: multimodal_agent.py
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent import Agent
from agentuniverse.agent.agent_manager import AgentManager

AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)


def chat():
    instance: Agent = AgentManager().get_instance_obj('multimodal_agent')
    output_object = instance.run(input="图中描绘的是什么景象?", image_urls=[
        'https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20241022/emyrja/dog_and_girl.jpeg'])
    res_info = f"\n图中描绘的景象是:\n"
    res_info += output_object.get_data('output')
    print(res_info)
    output_object = instance.run(input="做一首诗描述这个场景")
    res_info = f"\n做一首诗描述这个场景:\n"
    res_info += output_object.get_data('output')
    print(res_info)


if __name__ == '__main__':
    chat()
