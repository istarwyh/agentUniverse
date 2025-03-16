import os
import unittest
from agentuniverse.agent.action.tool.tool_manager import ToolManager
from agentuniverse.base.agentuniverse import AgentUniverse
from agentuniverse.base.util.env_util import get_from_env

# 获取脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))
# 设置工作目录为脚本所在目录
os.chdir(script_dir)

AgentUniverse().start(config_path='../../config/config.toml')

class TavilyToolTest(unittest.TestCase):
    """
    Tavily工具的测试用例
    """
    # 从环境变量获取API密钥，如果没有则使用占位符
    #api_key = get_from_env("TAVILY_API_KEY") or "your_tavily_api_key_here"
    api_key = "tvly-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    # 测试查询
    test_query = "The latest developments of DeepSeek"
    test_context = "https://en.wikipedia.org/wiki/Lionel_Messi"

    def test_tavily_tool(self):
        """测试Tavily工具的标准搜索模式"""
        # 跳过测试如果没有有效的API密钥
        if self.api_key == "your_tavily_api_key_here":
            self.skipTest("未提供Tavily API密钥，跳过测试")
            
        tavily_tool = ToolManager().get_instance_obj("tavily_tool")
        
        print("\n-------------测试Tavily工具(标准模式)---------------")
        result = tavily_tool.run(query=self.test_query, api_key=self.api_key, search_mode="standard", format="markdown")
        #print(result)

        if len(result["results"]) > 0:
            print(f"标题: {result['results'][0]['title']}")
            print(f"URL: {result['results'][0]['url']}")
            content = result["results"][0]["content"]
            print(f"内容: {content[:200]}..." if len(content) > 200 else content)
        else:
            print("无搜索结果")

        if len(result["formatted_results"]) > 0:
            print(f"格式化结果: \n{result['formatted_results']}")
        
        print("\n-------------测试Tavily工具(上下文模式)---------------")
        result = tavily_tool.run(query=self.test_context, api_key=self.api_key, search_mode="context", format="markdown")
        print(result)
        

if __name__ == '__main__':
    unittest.main()
