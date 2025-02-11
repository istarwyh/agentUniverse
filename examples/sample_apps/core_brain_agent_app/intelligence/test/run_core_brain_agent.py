# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/13 14:18
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: run_neo4jstore.py
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.agent.agent_manager import AgentManager

AgentUniverse().start(config_path='../../config/config.toml', core_mode=True)



if __name__=="__main__":
    tour_plan_agent = AgentManager().get_instance_obj('tour_plan_agent')

    result = tour_plan_agent.run(
        agent_introduction="你是一名专业的旅游规划人员",
        agent_target="你的目标是调用工具为用户规划完整的旅行计划",
        expert_knowledge='''
                        你的基础思路应该是调用工具达成目的。
                        因此你的规划行为应该包含以下几步，你要严格遵守流程完成，不允许擅自更改顺序：
                        ## 第一步：让子agent分析用户的旅行需求，制定一个完整的信息搜索计划，这一步你需要知道详细的结果，以便执行后续的流程。
                        ## 第二步：根据第一步的结果调用工具搜索相关的信息，这一步需要多次执行，直到你完成了信息搜索计划中的所有流程。但你无需知道工具详细的执行结果。
                        ## 第三步：让子agent根据第二步中搜集到的所有信息制定一份完整的旅行计划。
                    ''',
        user_query="我想去杭州旅行三天，想顺带去盗墓笔记相关的地方圣地巡礼"
    )
    print("test")