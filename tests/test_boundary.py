"""
边界值测试脚本
使用 pytest parametrize 参数化执行测试用例
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from api_test_framework.utils.data_loader import load_csv_test_data, parse_test_case
from api_test_framework.core.assertions import assert_response_by_type


def get_auth_required_cases():
    """
    获取需要鉴权的测试用例（根据 CSV 中的 requires_auth 字段）
    """
    csv_file = os.path.join(os.path.dirname(__file__), "test_data", "test_boundary_data.csv")
    raw_cases = load_csv_test_data(csv_file)
    cases = [parse_test_case(raw_case) for raw_case in raw_cases]
    
    # 根据 CSV 中的 requires_auth 字段过滤
    return [case for case in cases if case["requires_auth"]]


def get_no_auth_cases():
    """
    获取不需要鉴权的测试用例（根据 CSV 中的 requires_auth 字段）
    """
    csv_file = os.path.join(os.path.dirname(__file__), "test_data", "test_boundary_data.csv")
    raw_cases = load_csv_test_data(csv_file)
    cases = [parse_test_case(raw_case) for raw_case in raw_cases]
    
    # 根据 CSV 中的 requires_auth 字段过滤
    return [case for case in cases if not case["requires_auth"]]


def get_text_test_cases():
    """
    获取文本响应边界值测试用例
    """
    return [
        {
            "case_id": "T1",
            "case_name": "文本响应-空响应体",
            "url": "/api/error/empty",
            "method": "GET",
            "headers": None,
            "body": None,
            "response_type": "text",
            "expected_status": 200,
            "expected_items": [],
            "expected_values": None,
            "expected_error": "",
            "unexpected_items": [],
            "min_length": None,
            "max_length": 0,
        },
        {
            "case_id": "T2",
            "case_name": "文本响应-畸形JSON字符串",
            "url": "/api/error/malformed",
            "method": "GET",
            "headers": None,
            "body": None,
            "response_type": "text",
            "expected_status": 200,
            "expected_items": ["this is not valid json"],
            "expected_values": None,
            "expected_error": "",
            "unexpected_items": [],
            "min_length": 20,
            "max_length": 50,
        },
        {
            "case_id": "T3",
            "case_name": "文本响应-robots.txt内容检查",
            "url": "/robots.txt",
            "method": "GET",
            "headers": None,
            "body": None,
            "response_type": "text",
            "expected_status": 200,
            "expected_items": ["User-agent", "Disallow"],
            "expected_values": None,
            "expected_error": "",
            "unexpected_items": [],
            "min_length": 30,
            "max_length": 100,
        },
    ]


def _send_request(api_session, case):
    """
    通用请求发送函数
    """
    if case["method"] == "GET":
        return api_session.get(
            case["url"],
            params=None,
            headers=case["headers"],
            response_type=case["response_type"]
        )
    elif case["method"] == "POST":
        # 边界值测试模式：登录接口添加 X-Test-Mode 头跳过密码验证
        request_headers = case["headers"].copy() if isinstance(case["headers"], dict) else {}
        if case["url"] == "/api/login":
            request_headers["X-Test-Mode"] = "boundary"
        
        return api_session.post(
            case["url"],
            json_data=case["body"],
            headers=request_headers,
            response_type=case["response_type"]
        )
    else:
        pytest.fail(f"不支持的请求方法: {case['method']}")


@pytest.mark.auth_required
@pytest.mark.parametrize("case", get_auth_required_cases())
def test_boundary_cases_with_auth(case, api_session):
    """
    需要鉴权的边界值测试用例
    使用 @pytest.mark.auth_required 标记，conftest.py 会自动注入 Authorization 头
    """
    status, body = _send_request(api_session, case)
    assert_response_by_type(status, body, case["response_type"], case)


@pytest.mark.parametrize("case", get_no_auth_cases())
def test_boundary_cases_no_auth(case, api_session):
    """
    不需要鉴权的边界值测试用例
    """
    status, body = _send_request(api_session, case)
    assert_response_by_type(status, body, case["response_type"], case)


@pytest.mark.parametrize("case", get_text_test_cases())
def test_text_boundary_cases(case, api_session):
    """
    文本响应边界值测试用例
    """
    status, body = _send_request(api_session, case)
    assert_response_by_type(status, body, case["response_type"], case)