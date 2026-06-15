"""
API 测试框架核心模块
提供 API 客户端和断言功能
"""

from .api_client import (
    api_get,
    api_post,
    api_put,
    api_delete,
    ApiSession,
    configure_logging
)

from .assertions import (
    assert_status_code,
    assert_json_response,
    assert_text_response,
    assert_response_by_type,
    save_response_on_failure
)

__all__ = [
    # API 客户端
    'api_get',
    'api_post',
    'api_put',
    'api_delete',
    'ApiSession',
    'configure_logging',
    # 断言函数
    'assert_status_code',
    'assert_json_response',
    'assert_text_response',
    'assert_response_by_type',
    'save_response_on_failure'
]
