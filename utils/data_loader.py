"""
CSV 数据加载和解析模块
提供从 CSV 文件加载测试数据并解析各种字段的功能
"""

import csv
import json
import logging

logger = logging.getLogger(__name__)


def load_csv_test_data(file_path):
    """
    从 CSV 文件加载测试数据

    Args:
        file_path: CSV 文件路径

    Returns:
        包含所有测试用例的列表，每个用例是一个字典
    """
    test_data = []
    try:
        with open(file_path, mode='r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                test_data.append(row)
        logger.info(f"成功加载 {len(test_data)} 条测试用例")
        return test_data
    except FileNotFoundError:
        logger.error(f"文件不存在: {file_path}")
        raise
    except Exception as e:
        logger.error(f"加载 CSV 失败: {str(e)}")
        raise


def parse_json_field(value):
    """
    解析 JSON 字段，处理空字符串情况

    Args:
        value: 待解析的字符串值

    Returns:
        解析后的 JSON 对象，如果为空或解析失败则返回 None
    """
    if not value or value.strip() == '':
        return None
    try:
        return json.loads(value)
    except json.JSONDecodeError:
        logger.warning(f"JSON 解析失败: {value}")
        return None


def parse_keywords(value):
    """
    解析关键词字段，支持逗号和竖线分隔，并过滤空字符串

    Args:
        value: 待解析的字符串值，支持 "a,b,c" 或 "a|b|c" 格式

    Returns:
        关键词列表
    """
    if not value or value.strip() == '':
        return []
    # 先尝试按竖线分割（CSV中使用|分隔）
    if '|' in value:
        return [k.strip() for k in value.split('|') if k.strip()]
    # 否则按逗号分割
    return [k.strip() for k in value.split(',') if k.strip()]


def parse_test_case(case):
    """
    解析单个测试用例的所有字段

    Args:
        case: CSV 读取的原始用例字典

    Returns:
        解析后的完整测试用例字典
    """
    # 解析 expected_items：优先使用 expected_fields，fallback 到 expected_keywords
    fields = parse_keywords(case.get("expected_fields", ""))
    keywords = parse_keywords(case.get("expected_keywords", ""))
    expected_items = fields if fields else keywords

    parsed_case = {
        "case_id": case.get("case_id", ""),
        "case_name": case.get("case_name", ""),
        "url": case.get("url", ""),
        "method": case.get("method", "GET").upper(),
        "headers": parse_json_field(case.get("headers", "")),
        "body": parse_json_field(case.get("body", "")),
        "response_type": case.get("response_type", "json"),
        "expected_status": int(case.get("expected_status", 200)) if case.get("expected_status") else 200,
        # 统一字段名：expected_items 用于需要检查的字符串列表
        "expected_items": expected_items,
        "expected_values": parse_json_field(case.get("expected_values", "")),
        "expected_error": case.get("expected_error", ""),
        # 统一字段名：unexpected_items 用于不应包含的字符串列表
        "unexpected_items": parse_keywords(case.get("unexpected_keywords", "")),
        "min_length": int(case.get("min_length")) if case.get("min_length") else None,
        "max_length": int(case.get("max_length")) if case.get("max_length") else None,
        # 是否需要鉴权
        "requires_auth": case.get("requires_auth", "").strip().lower() == "true"
    }
    return parsed_case