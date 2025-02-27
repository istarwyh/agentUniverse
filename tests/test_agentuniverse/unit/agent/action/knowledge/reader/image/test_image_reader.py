# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/2/12 12:01
# @Author  : wozhapen
# @Email   : wozhapen@gmail.com
# @FileName: test_image_reader.py

import os.path
import unittest
from agentuniverse.agent.action.knowledge.reader.image.image_reader import ImageReader


class TestImageReader(unittest.TestCase):

    def test_load_mix_language_success(self):
        """Test successful loading and parsing of image content."""
        reader = ImageReader(['en', 'ch_sim'], False)
        image_file_path = os.path.join(os.path.dirname(__file__), "test_en_and_zh.jpeg")
        documents = reader._load_data(file=image_file_path)
        if documents:
            print(documents[0].text)
        else:
            print("No content loaded or error occurred.")
        self.assertEqual(documents[0].text, "PEER 模式组件:\n该pattern通过计划\n(Plan)\n执行 (Execute)\n表达 (Express)\n评价 (Review) 四个不同职责的智能体,实现对复杂\n问题的多步拆解_\n分步执行。并基于评价反馈进行自主迭代。最终提升推理分析类任务表现。典型适用场景:  事件解读:\n行业分析")

    def test_load_en_language_success(self):
        """Test successful loading and parsing of image content."""
        reader = ImageReader()
        image_file_path = os.path.join(os.path.dirname(__file__), "test_image.jpeg")
        documents = reader._load_data(file=image_file_path)
        if documents:
            print(documents[0].text)
        else:
            print("No content loaded or error occurred.")
        self.assertEqual(documents[0].text, "Run your first example; and you can quickly experience the performance of the agents (or agent groups) built by\nagentUniverse through the tutorial:")

if __name__ == '__main__':
        unittest.main()