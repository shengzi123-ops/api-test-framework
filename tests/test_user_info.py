"""
用户信息测试脚本
测试鉴权相关接口
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
from api_test_framework.core.api_client import ApiSession
from api_test_framework.core.assertions import assert_response
from api_test_framework.utils.logger import setup_logging
import logging

# 配置日志
setup_logging()
logger = logging.getLogger(__name__)


@pytest.fixture
def api_session():
    """创建 API 会话 fixture"""
    session = ApiSession(BASE_URL)
    yield session
    session.reset_headers()  # 测试结束后重置 headers
    session.close()


def test_user_info_with_valid_token(api_session):
    """测试有效 Token 获取用户信息"""
    logger.info("测试：有效 Token")
    api_session.set_default_headers({"Authorization": "Bearer abc123"})
    status, body = api_session.get("/api/user/info")
    
    case = {
        "name": "有效Token获取用户信息",
        "expected_status": 200,
        "expected_fields": ["id", "name", "role"],
        "expected_values": {"name": "张三", "role": "管理员"}
    }
    assert_response(status, body, case)


def test_user_info_with_invalid_token(api_session):
    """测试无效 Token"""
    logger.info("测试：无效 Token")
    api_session.set_default_headers({"Authorization": "Bearer wrong_token"})
    status, body = api_session.get("/api/user/info")
    
    case = {
        "name": "无效Token",
        "expected_status": 401,
        "expected_error": "未授权"
    }
    assert_response(status, body, case)


def test_user_info_without_auth(api_session):
    """测试缺少 Authorization 头"""
    logger.info("测试：缺少 Authorization 头")
    # 不设置 Authorization 头
    status, body = api_session.get("/api/user/info")
    
    case = {
        "name": "缺少Authorization头",
        "expected_status": 401,
        "expected_error": "未授权"
    }
    assert_response(status, body, case)
