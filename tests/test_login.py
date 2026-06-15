import sys
import os
import json
import logging
import pytest
import csv

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from api_test_framework.core.api_client import ApiSession
from api_test_framework.core.assertions import assert_response

# 加载 CSV 数据
def load_csv(file_path):
    with open(file_path, encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

login_data = load_csv("tests/test_data/login_data.csv")


@pytest.mark.parametrize("case", login_data)
def test_login(case, api_session):
    """登录接口测试（数据驱动）"""
    # 解析 body 字段中的 JSON 数据
    body_data = json.loads(case["body"]) if case["body"] else {}
    status, body = api_session.post("/api/login", json_data=body_data)
    
    assert status == int(case["expected_status"])
    if case.get("expected_fields"):
        for field in case["expected_fields"].split("|"):
            assert field in body
    if case.get("expected_error"):
        assert case["expected_error"] in body.get("error", "")
