"""
超时测试用例

测试场景：
1. 调用延迟接口，设置极短超时时间，验证超时处理
2. 调用延迟接口，设置足够长超时时间，验证正常返回
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 加载 .env 环境变量文件（从项目根目录加载）
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
env_file = os.path.join(project_root, '.env')
load_dotenv(env_file, override=True)
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")

import pytest
from core.api_client import api_get


class TestTimeout:
    """超时测试用例类"""
    
    def test_timeout_with_short_timeout(self):
        """
        测试超时场景：调用延迟3秒的接口，设置超时0.001秒
        
        预期结果：
        - status 为 None
        - body["error"] 为 "timeout"
        """
        # 调用延迟3秒的接口，但设置超时时间仅0.001秒
        status, body = api_get(
            url=f"{BASE_URL}/api/delay/3",
            timeout=0.001
        )
        
        # 断言超时处理
        assert status is None, f"期望 status 为 None，实际得到 {status}"
        assert "error" in body, "期望 body 包含 error 字段"
        assert body["error"] == "timeout", f"期望 error 为 'timeout'，实际得到 '{body['error']}'"
    
    def test_success_with_long_timeout(self):
        """
        测试正常场景：调用延迟3秒的接口，设置超时5秒（大于延迟时间）
        
        预期结果：
        - status 为 200
        - body 包含预期的消息
        """
        # 调用延迟3秒的接口，设置超时时间5秒（足够完成请求）
        status, body = api_get(
            url=f"{BASE_URL}/api/delay/3",
            timeout=5
        )
        
        # 断言正常返回
        assert status == 200, f"期望 status 为 200，实际得到 {status}"
        assert "message" in body, "期望 body 包含 message 字段"
        assert "延迟3秒后返回" in body["message"], f"期望消息包含'延迟3秒后返回'，实际消息: {body['message']}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
