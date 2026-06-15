"""
断言模块
提供 API 响应断言功能
"""

import json
import os
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def assert_status_code(actual_status, expected_status, case_name):
    """
    断言状态码
    
    Args:
        actual_status: 实际状态码
        expected_status: 期望状态码
        case_name: 用例名称
    
    Raises:
        AssertionError: 状态码不匹配时
    """
    logger.info(f"[{case_name}] 开始检查状态码...")
    assert actual_status == expected_status, \
        f"[{case_name}] 状态码不匹配：期望={expected_status}，实际={actual_status}"
    logger.info(f"[{case_name}] ✓ 状态码断言通过 (status={actual_status})")


def assert_json_response(body, expected_fields=None, expected_values=None, 
                        expected_error=None, case_name=""):
    """
    断言 JSON 响应
    
    Args:
        body: 响应体（字典）
        expected_fields: 期望存在的字段列表
        expected_values: 期望的键值对字典
        expected_error: 期望的错误信息（部分匹配）
        case_name: 用例名称
    
    Raises:
        AssertionError: 断言失败时
    """
    if expected_fields:
        logger.info(f"[{case_name}] 开始检查字段存在: {expected_fields}...")
        for field in expected_fields:
            assert field in body, \
                f"[{case_name}] 缺少期望字段: {field}"
        logger.info(f"[{case_name}] ✓ 字段存在断言通过 ({len(expected_fields)}个字段)")
    
    if expected_values:
        logger.info(f"[{case_name}] 开始检查字段值...")
        for key, expected_value in expected_values.items():
            assert key in body, f"[{case_name}] 缺少字段: {key}"
            assert body[key] == expected_value, \
                f"[{case_name}] 字段 {key} 值不匹配：期望={expected_value}，实际={body[key]}"
        logger.info(f"[{case_name}] ✓ 字段值断言通过")
    
    if expected_error:
        logger.info(f"[{case_name}] 开始检查错误信息...")
        error_message = body.get("error", "")
        assert expected_error in error_message, \
            f"[{case_name}] 错误信息不匹配：期望包含'{expected_error}'，实际='{error_message}'"
        logger.info(f"[{case_name}] ✓ 错误信息断言通过")


def assert_text_response(body, expected_items=None, unexpected_items=None,
                        min_length=None, max_length=None, case_name=""):
    """
    断言文本响应
    
    Args:
        body: 响应体（字符串）
        expected_items: 期望包含的字符串列表
        unexpected_items: 不应包含的字符串列表
        min_length: 最小长度
        max_length: 最大长度
        case_name: 用例名称
    
    Raises:
        AssertionError: 断言失败时
    """
    if expected_items:
        logger.info(f"[{case_name}] 开始检查期望文本内容: {expected_items}...")
        for item in expected_items:
            assert item in body, \
                f"[{case_name}] 响应中不包含期望内容: '{item}'"
        logger.info(f"[{case_name}] ✓ 期望文本内容断言通过")
    
    if unexpected_items:
        logger.info(f"[{case_name}] 开始检查不应包含的内容: {unexpected_items}...")
        for item in unexpected_items:
            assert item not in body, \
                f"[{case_name}] 响应中不应包含内容: '{item}'"
        logger.info(f"[{case_name}] ✓ 不应包含内容断言通过")
    
    if min_length is not None:
        logger.info(f"[{case_name}] 开始检查最小长度: {min_length}...")
        assert len(body) >= min_length, \
            f"[{case_name}] 响应长度不足：期望>= {min_length}，实际={len(body)}"
        logger.info(f"[{case_name}] ✓ 最小长度断言通过")
    
    if max_length is not None:
        logger.info(f"[{case_name}] 开始检查最大长度: {max_length}...")
        assert len(body) <= max_length, \
            f"[{case_name}] 响应长度超限：期望<= {max_length}，实际={len(body)}"
        logger.info(f"[{case_name}] ✓ 最大长度断言通过")


def save_response_on_failure(status, body, case_name, response_type):
    """
    保存失败响应到文件
    
    Args:
        status: 状态码
        body: 响应体
        case_name: 用例名称
        response_type: 响应类型（json/text/content）
    """
    output_dir = "failed_responses"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 清理文件名中的非法字符
    safe_case_name = case_name.replace('/', '_').replace('\\', '_').replace(':', '_')
    
    if response_type == "json":
        filename = f"{safe_case_name}_{timestamp}.json"
        filepath = os.path.join(output_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({"status": status, "body": body}, f, indent=2, ensure_ascii=False)
            logger.info(f"失败响应已保存到: {filepath}")
        except Exception as e:
            logger.error(f"保存失败响应失败: {e}")
    elif response_type == "text":
        filename = f"{safe_case_name}_{timestamp}.txt"
        filepath = os.path.join(output_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Status: {status}\n")
                f.write("---\n")
                f.write(str(body))
            logger.info(f"失败响应已保存到: {filepath}")
        except Exception as e:
            logger.error(f"保存失败响应失败: {e}")
    elif response_type == "content":
        filename = f"{safe_case_name}_{timestamp}.bin"
        filepath = os.path.join(output_dir, filename)
        try:
            with open(filepath, 'wb') as f:
                f.write(body)
            logger.info(f"失败响应已保存到: {filepath}")
        except Exception as e:
            logger.error(f"保存失败响应失败: {e}")
    else:
        logger.warning(f"未知的 response_type: {response_type}")


def assert_response_by_type(status, body, response_type, parsed_case):
    """
    根据响应类型进行断言
    
    Args:
        status: 状态码
        body: 响应体
        response_type: 响应类型（json/text/content）
        parsed_case: 解析后的测试用例字典
    
    Raises:
        AssertionError: 断言失败时
    """
    case_name = parsed_case.get("case_name", "")
    expected_status = parsed_case.get("expected_status", 200)
    
    try:
        # 状态码断言
        assert_status_code(status, expected_status, case_name)
        
        # 根据响应类型进行不同的断言
        if response_type == "json":
            assert_json_response(
                body,
                expected_fields=parsed_case.get("expected_items"),
                expected_values=parsed_case.get("expected_values"),
                expected_error=parsed_case.get("expected_error"),
                case_name=case_name
            )
        elif response_type == "text":
            assert_text_response(
                body,
                expected_items=parsed_case.get("expected_items"),
                unexpected_items=parsed_case.get("unexpected_items"),
                min_length=parsed_case.get("min_length"),
                max_length=parsed_case.get("max_length"),
                case_name=case_name
            )
        elif response_type == "content":
            # 二进制内容，只检查长度约束
            if parsed_case.get("min_length") is not None:
                assert len(body) >= parsed_case["min_length"], \
                    f"[{case_name}] 响应长度不足"
            if parsed_case.get("max_length") is not None:
                assert len(body) <= parsed_case["max_length"], \
                    f"[{case_name}] 响应长度超限"
            logger.info(f"[{case_name}] ✓ 二进制内容断言通过")
        else:
            logger.warning(f"[{case_name}] 未知的 response_type: {response_type}")
            
    except AssertionError as e:
        save_response_on_failure(status, body, case_name, response_type)
        raise
    except Exception as e:
        save_response_on_failure(status, body, case_name, response_type)
        logger.error(f"[{case_name}] 发生非断言异常: {type(e).__name__}: {str(e)}")
        raise


def assert_response(status, body, case_or_expected_status=200, expected_fields=None, 
                   expected_values=None, expected_error=None, case_name=""):
    """
    统一断言函数（支持两种调用方式）
    
    方式1（推荐）：传入字典
    assert_response(status, body, {
        "name": "用例名称",
        "expected_status": 200,
        "expected_fields": ["field1", "field2"],
        "expected_values": {"key": "value"},
        "expected_error": "错误信息"
    })
    
    方式2（兼容旧版）：传入单独参数
    assert_response(status, body, 200, ["field1"], {"key": "value"}, "错误信息", "用例名称")
    
    Args:
        status: 实际状态码
        body: 响应体
        case_or_expected_status: 用例字典或期望状态码
        expected_fields: 期望存在的字段列表
        expected_values: 期望的键值对字典
        expected_error: 期望的错误信息
        case_name: 用例名称
    
    Raises:
        AssertionError: 断言失败时
    """
    # 判断是传入的是字典还是状态码
    if isinstance(case_or_expected_status, dict):
        case = case_or_expected_status
        expected_status = case.get("expected_status", 200)
        case_name = case.get("name", case.get("case_name", ""))
        expected_fields = case.get("expected_fields", case.get("expected_items"))
        expected_values = case.get("expected_values")
        expected_error = case.get("expected_error")
    else:
        expected_status = case_or_expected_status
    
    assert_status_code(status, expected_status, case_name)
    
    if isinstance(body, dict):
        assert_json_response(body, expected_fields, expected_values, expected_error, case_name)
    else:
        logger.info(f"[{case_name}] 响应体不是JSON格式，跳过字段检查")
