"""
数据库工具函数模块
提供可复用的数据库操作函数
支持从 .env 文件和环境变量读取配置
"""

import os
import pymysql

def load_env_file(env_path=".env"):
    """
    从 .env 文件加载环境变量
    :param env_path: .env 文件路径
    """
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()

def get_db_config():
    """
    获取数据库配置（优先环境变量，其次默认值）
    :return: 数据库配置字典
    """
    # 先尝试加载 .env 文件
    load_env_file()
    
    return {
        "host": os.environ.get("DB_HOST", "127.0.0.1"),
        "port": int(os.environ.get("DB_PORT", 3307)),
        "user": os.environ.get("DB_USER", "root"),
        "password": os.environ.get("DB_PASSWORD", ""),
        "database": os.environ.get("DB_DATABASE", "test_db"),
        "charset": os.environ.get("DB_CHARSET", "utf8mb4")
    }

def connect_db(host=None, port=None, user=None, password=None, database=None, charset=None):
    """
    创建数据库连接
    参数优先级：函数参数 > 环境变量 > 默认值
    """
    # 获取配置
    config = get_db_config()
    
    # 使用传入的参数或配置中的值
    return pymysql.connect(
        host=host or config["host"],
        port=port or config["port"],
        user=user or config["user"],
        password=password or config["password"],
        database=database or config["database"],
        charset=charset or config["charset"]
    )

def insert_user(cursor, conn, username, password, email):
    """
    参数化插入用户
    :param cursor: 数据库游标
    :param conn: 数据库连接
    :param username: 用户名
    :param password: 密码
    :param email: 邮箱
    :return: (成功标志, 用户ID/错误信息)
    """
    try:
        cursor.execute(
            "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
            (username, password, email)
        )
        conn.commit()
        return True, cursor.lastrowid
    except pymysql.MySQLError as e:
        conn.rollback()
        return False, str(e)

def query_user_by_username(cursor, username):
    """
    根据用户名查询用户
    :param cursor: 数据库游标
    :param username: 用户名
    :return: 用户字典或 None
    """
    cursor.execute("SELECT id, username, email, role, created_at FROM users WHERE username = %s", (username,))
    row = cursor.fetchone()
    if row:
        columns = [desc[0] for desc in cursor.description]
        user = dict(zip(columns, row))
        if "created_at" in user and user["created_at"]:
            user["created_at"] = user["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        return user
    return None

def delete_user_by_username(cursor, conn, username):
    """
    根据用户名删除用户
    :param cursor: 数据库游标
    :param conn: 数据库连接
    :param username: 用户名
    :return: (成功标志, 影响行数/错误信息)
    """
    try:
        cursor.execute("DELETE FROM users WHERE username = %s", (username,))
        conn.commit()
        return True, cursor.rowcount
    except pymysql.MySQLError as e:
        conn.rollback()
        return False, str(e)

def get_user_stats(cursor):
    """
    获取用户统计信息
    :param cursor: 数据库游标
    :return: (总用户数, 角色分组统计字典)
    """
    cursor.execute("SELECT COUNT(*) FROM users")
    total_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role")
    role_stats = {}
    for role, count in cursor.fetchall():
        role_name = role if role else "未设置角色"
        role_stats[role_name] = count
    
    return total_count, role_stats

def query_all_users(cursor):
    """
    查询所有用户
    :param cursor: 数据库游标
    :return: 用户字典列表
    """
    cursor.execute("SELECT id, username, email, role, created_at FROM users")
    rows = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    
    users = []
    for row in rows:
        user = dict(zip(columns, row))
        if "created_at" in user and user["created_at"]:
            user["created_at"] = user["created_at"].strftime("%Y-%m-%d %H:%M:%S")
        users.append(user)
    
    return users
