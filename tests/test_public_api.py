"""
公共 API 测试用例
测试不同响应类型的处理
"""

import sys
import os
import requests

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from api_test_framework.core.api_client import api_get


# 检查外部服务是否可用
def check_external_service():
    """检查外部服务及其关键端点是否可用"""
    base_url = "http://httpbin.org"
    endpoints = [
        base_url,                    # 首页
        f"{base_url}/robots.txt",    # robots.txt
        f"{base_url}/html",          # HTML 页面
        f"{base_url}/image/jpeg"     # 图片端点
    ]
    
    for url in endpoints:
        try:
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                return False
        except:
            return False
    
    return True


@pytest.mark.skipif(
    not check_external_service(),
    reason="httpbin.org 或其端点（/robots.txt、/html、/image/jpeg）不可用，跳过外部 API 测试"
)
class TestPublicApi:
    """公共 API 测试类"""
    
    def test_text_response_robots(self):
        """测试普通文本响应 - robots.txt"""
        status, text = api_get("http://httpbin.org/robots.txt", response_type='text')
        
        # 断言状态码
        assert status == 200, f"期望状态码 200，实际 {status}"
        
        # 断言响应体不为空
        assert text is not None, "响应体为空"
        assert isinstance(text, str), "响应体不是字符串类型"
        
        # 断言包含预期内容
        assert "User-agent" in text, "响应体不包含 User-agent"
        assert "Disallow" in text, "响应体不包含 Disallow"
    
    def test_text_response_html(self):
        """测试 HTML 响应"""
        status, html = api_get("http://httpbin.org/html", response_type='text')
        
        # 断言状态码
        assert status == 200, f"期望状态码 200，实际 {status}"
        
        # 断言响应体不为空且是字符串
        assert html is not None, "响应体为空"
        assert isinstance(html, str), "响应体不是字符串类型"
        
        # 断言 HTML 内容长度合理
        assert len(html) > 100, "HTML 内容过短"
        assert "<html" in html.lower(), "响应体不是 HTML"
    
    def test_content_response_image(self):
        """测试二进制图片响应"""
        status, img = api_get("http://httpbin.org/image/jpeg", response_type='content')
        
        # 断言状态码
        assert status == 200, f"期望状态码 200，实际 {status}"
        
        # 断言响应体不为空且是字节类型
        assert img is not None, "响应体为空"
        assert isinstance(img, bytes), "响应体不是二进制类型"
        
        # 断言图片大小合理（JPEG 图片通常大于 1KB）
        assert len(img) > 1024, "图片数据过小"
