"""
产品列表接口测试
测试 /api/product/list 端点的功能
"""

import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pytest
from utils.data_loader import load_csv_test_data, parse_test_case
from core.assertions import assert_response_by_type

def _send_request(api_session, case):
    """发送请求的辅助函数"""
    method = case.get("method", "GET").upper()
    path = case.get("url", "")
    headers = case.get("headers", {})
    body = case.get("body")
    response_type = case.get("response_type", "json")
    
    if method == "GET":
        return api_session.get(path, params=body, headers=headers, response_type=response_type)
    elif method == "POST":
        return api_session.post(path, json_data=body, headers=headers, response_type=response_type)
    elif method == "PUT":
        return api_session.put(path, json_data=body, headers=headers, response_type=response_type)
    elif method == "DELETE":
        return api_session.delete(path, params=body, headers=headers, response_type=response_type)
    else:
        raise ValueError(f"不支持的 HTTP 方法: {method}")

def get_product_test_cases():
    """加载产品测试用例"""
    csv_file = os.path.join(os.path.dirname(__file__), "test_data", "product_data.csv")
    raw_cases = load_csv_test_data(csv_file)
    return [parse_test_case(raw_case) for raw_case in raw_cases]

@pytest.mark.parametrize("case", get_product_test_cases())
def test_product_list(case, api_session):
    """产品列表接口测试"""
    status, body = _send_request(api_session, case)
    
    # 基础断言
    assert_response_by_type(status, body, case["response_type"], case)
    
    # 针对产品列表的特殊断言
    if case["case_id"] == "1" and status == 200:
        # 正向用例：验证返回 3 个产品
        # 防御性检查：确保 body 是字典类型
        assert isinstance(body, dict), f"响应体不是字典类型，实际类型: {type(body).__name__}"
        assert "products" in body, "响应体缺少 products 字段"
        
        products = body["products"]
        assert isinstance(products, list), f"products 不是列表类型，实际类型: {type(products).__name__}"
        assert len(products) == 3, f"期望返回 3 个产品，实际返回 {len(products)} 个"
        
    elif case["case_id"] == "3" and status == 200:
        # 边界用例：验证产品字段结构
        # 防御性检查：确保 body 是字典类型
        assert isinstance(body, dict), f"响应体不是字典类型，实际类型: {type(body).__name__}"
        assert "products" in body, "响应体缺少 products 字段"
        
        products = body["products"]
        assert isinstance(products, list), f"products 不是列表类型，实际类型: {type(products).__name__}"
        assert len(products) > 0, "产品列表为空"
        
        for product in products:
            # 防御性检查：确保每个产品是字典类型
            assert isinstance(product, dict), f"产品不是字典类型，实际类型: {type(product).__name__}"
            
            # 验证每个产品都包含 id、name、price 字段
            assert "id" in product, "产品缺少 id 字段"
            assert "name" in product, "产品缺少 name 字段"
            assert "price" in product, "产品缺少 price 字段"
            
            # 验证字段类型
            assert isinstance(product["id"], int), f"产品 id 类型错误，期望 int，实际 {type(product['id']).__name__}"
            assert isinstance(product["name"], str), f"产品 name 类型错误，期望 str，实际 {type(product['name']).__name__}"
            assert isinstance(product["price"], (int, float)), f"产品 price 类型错误，期望 int/float，实际 {type(product['price']).__name__}"
            
            # 验证字段值有效性
            assert product["id"] > 0, "产品 id 必须大于 0"
            assert len(product["name"]) > 0, "产品 name 不能为空"
            assert product["price"] >= 0, "产品 price 不能为负数"