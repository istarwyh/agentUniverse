# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/12/17 15:17
# @Author  : fanen.lhy
# @Email   : fanen.lhy@antgroup.com
# @FileName: demo_prompt_knowledge.py

DEMO_PROMPT_KNOWLEDGE = [
    {
        "name": "tour_plan_prompt.cn",
        "description": "总结收集到的旅游信息，生成一份完整旅游计划的提示词",
        "input_params": [
            {
                "name": "user_query",
                "format": "用户的旅行需求"
            },
            {
                "name": "search_result",
                "format": "已经搜集归档的目的地城市旅游信息, 要求是一个list，如[$#{酒店信息},$#{景点信息}]"
            }
        ]
    },{
        "name": "demo_planning_agent.cn",
        "description": "将原始问题拆分为多个子问题的提示词",
        "input_params": [
            {
                "name": "input",
                "format": "用户的原始问题"
            }
        ]
    },{
        "name": "user_query_intent_parse_prompt.cn",
        "description": "分析用户的旅行需求，生成需要搜集哪些信息的计划的提示词",
        "input_params": [
            {
                "name": "user_query",
                "format": "用户的旅行需求"
            }
        ]
    },{
        "name": "user_query_intent_parse_prompt.cn",
        "description": "金融专家，在各维度评估query（用户输入）和answer（模型输出）分数的提示词",
        "input_params": [
            {
                "name": "query",
                "format": "用户的原始输入问题"
            },{
                "name": "answer",
                "format": "模型的输出答案"
            }
        ]
    }
]