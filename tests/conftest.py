"""
Pytest 配置文件
提供全局 Fixture
"""

import sys
import os


import pytest
import logging

# 添加项目根目录到 Python 路径（向上两级到 api_test_framework）
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(project_root))  # 再向上一级，使得可以 import api_test_framework.xxx
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
# 加载 .env 环境变量文件（从项目根目录加载）
from dotenv import load_dotenv
env_file = os.path.join(project_root, '.env')
load_dotenv(env_file, override=True)

from core.api_client import ApiSession
from utils.logger import setup_logging

# 从环境变量读取配置
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")

# 配置日志系统（全局初始化，只执行一次）
setup_logging(
    level=logging.INFO,
    log_format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    log_dir='logs',
    console_output=True,
    file_output=True
)


@pytest.fixture(scope="function")
def api_session():
    """
    Fixture 1：API Session 管理
    
    创建 API 会话实例，测试结束后自动清理
    
    Yields:
        ApiSession: API 会话实例
    """
    api = ApiSession(BASE_URL)
    yield api
    api.reset_headers()  # 重置 headers 避免影响其他测试
    api.close()


@pytest.fixture(scope="function", autouse=True)
def reset_server_data(api_session):
    """
    Fixture 2：数据重置
    
    依赖：api_session fixture
    
    功能：
    在每个测试前重置 Mock 服务器数据
    
    Yields:
        None
    """
    logger = logging.getLogger(__name__)
    
    # 重置 Mock 服务器数据
    try:
        status, body = api_session.post("/api/user/reset")
        if status == 200:
            logger.info("[AUTO] Mock 服务器数据已重置")
        else:
            logger.warning(f"[AUTO] Mock 服务器数据重置失败: {body}")
    except Exception as e:
        logger.error(f"[AUTO] 重置 Mock 服务器时发生错误: {e}")
    
    yield
    
    # 测试结束后执行清理操作（使用 DEBUG 级别降低干扰）
    logger.debug("[AUTO] 测试完成")


@pytest.fixture(scope="function", autouse=True)
def inject_auth_header(request, api_session):
    """
    Fixture 3：自动为标记了 auth_required 的用例注入 Authorization 头
    
    依赖：api_session fixture
    
    功能：
    - 检查当前用例是否有 auth_required 标记
    - 如果有，自动设置 Authorization 头为 "Bearer abc123"
    - 测试结束后清理，避免影响下一个用例
    
    使用方式：
    @pytest.mark.auth_required
    def test_protected_api(api_session):
        # 此测试会自动携带 Authorization 头
        status, body = api_session.get("/api/protected")
    """
    # 检查当前用例是否有 auth_required 标记
    if request.node.get_closest_marker("auth_required"):
        api_session.set_default_headers({"Authorization": "Bearer abc123"})
    
    yield
    
    # 测试结束后清理，避免影响下一个用例
    if request.node.get_closest_marker("auth_required"):
        api_session.reset_headers()