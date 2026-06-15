"""
数据库集成测试
测试场景：调用注册接口后，验证数据是否正确写入数据库
"""

import pytest
import os
import sys
import logging

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from utils.db_utils import (
    connect_db,
    query_user_by_username,
    delete_user_by_username,
    insert_user
)


@pytest.fixture(scope="function")
def db_connection():
    """
    数据库连接 Fixture
    测试结束后自动关闭连接
    """
    conn = None
    cursor = None
    try:
        conn = connect_db()
        cursor = conn.cursor()
        yield conn, cursor
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def test_register_db_integration(api_session, db_connection):
    """
    测试注册接口与数据库的集成
    
    流程：
    1. 清理可能存在的测试数据
    2. 调用注册接口 /api/register
    3. 从接口返回中获取用户信息
    4. 连接数据库查询刚注册的用户
    5. 对比接口返回和数据库中的数据是否一致
    6. 清理测试数据（删除刚注册的用户）
    """
    logger = logging.getLogger(__name__)
    
    conn, cursor = db_connection
    
    # 1. 准备测试数据
    test_username = "test_integration_user"
    test_password = "test_password_123"
    test_email = "test_integration@example.com"
    
    # 清理可能存在的测试用户
    delete_user_by_username(cursor, conn, test_username)
    
    # 2. 调用注册接口
    register_data = {
        "username": test_username,
        "password": test_password,
        "email": test_email
    }
    
    status, body = api_session.post("/api/register", json_data=register_data)
    
    # 验证注册成功
    assert status == 201, f"注册失败，状态码: {status}, 响应: {body}"
    assert body.get("status") == "注册成功", f"注册状态错误: {body}"
    
    api_user = body.get("user")
    assert api_user is not None, "接口未返回用户信息"
    
    # 3. 从数据库查询刚注册的用户
    db_user = query_user_by_username(cursor, test_username)
    
    # 验证数据库中存在该用户
    assert db_user is not None, f"数据库中未找到用户: {test_username}"
    
    # 4. 对比接口返回和数据库中的数据
    logger.info("=== 数据对比 ===")
    logger.info(f"接口返回用户: {api_user}")
    logger.info(f"数据库查询用户: {db_user}")
    
    # 对比关键字段（注意：数据库查询不返回 password，因为安全原因）
    assert api_user["username"] == db_user["username"], \
        f"用户名不一致: 接口={api_user['username']}, 数据库={db_user['username']}"
    
    assert api_user["email"] == db_user["email"], \
        f"邮箱不一致: 接口={api_user['email']}, 数据库={db_user['email']}"
    
    assert api_user["role"] == db_user["role"], \
        f"角色不一致: 接口={api_user['role']}, 数据库={db_user['role']}"
    
    # 时间格式可能有细微差异（秒级精度），只对比日期部分
    api_created_date = api_user["created_at"].split(" ")[0]
    db_created_date = db_user["created_at"].split(" ")[0] if db_user["created_at"] else ""
    assert api_created_date == db_created_date, \
        f"创建日期不一致: 接口={api_user['created_at']}, 数据库={db_user['created_at']}"
    
    logger.info("✅ 所有字段对比通过")
    
    # 5. 清理测试数据
    success, result = delete_user_by_username(cursor, conn, test_username)
    assert success, f"清理测试数据失败: {result}"
    logger.info(f"✅ 测试数据已清理，删除 {result} 条记录")


def test_register_duplicate_username(api_session, db_connection):
    """
    测试重复注册同一用户名
    
    流程：
    1. 先在数据库中插入一个用户
    2. 调用注册接口注册相同用户名
    3. 验证返回 409 错误
    """
    logger = logging.getLogger(__name__)
    
    conn, cursor = db_connection
    
    # 1. 先在数据库中插入用户
    test_username = "test_duplicate_user"
    test_password = "password123"
    test_email = "duplicate@example.com"
    
    success, user_id = insert_user(cursor, conn, test_username, test_password, test_email)
    assert success, f"插入测试用户失败: {user_id}"
    logger.info(f"已在数据库插入用户，ID: {user_id}")
    
    # 2. 调用注册接口注册相同用户名
    register_data = {
        "username": test_username,
        "password": "different_password",
        "email": "different@example.com"
    }
    
    status, body = api_session.post("/api/register", json_data=register_data)
    
    # 3. 验证返回 409 错误
    assert status == 409, f"预期 409 状态码，实际: {status}"
    assert body.get("error") == "用户名已存在", f"错误信息不正确: {body}"
    
    logger.info("✅ 重复用户名检测通过")
    
    # 4. 清理测试数据
    success, result = delete_user_by_username(cursor, conn, test_username)
    assert success, f"清理测试数据失败: {result}"
    logger.info(f"✅ 测试数据已清理")
