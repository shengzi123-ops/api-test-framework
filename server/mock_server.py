from flask import Flask, request, jsonify, make_response
import time
import json
import copy
import os

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 支持中文显示

# 数据库连接函数
def load_env_file():
    """从 .env 文件加载环境变量（从项目根目录加载）"""
    # 获取项目根目录（server/ -> api_test_framework/）
    server_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(server_dir)
    env_file = os.path.join(project_root, '.env')
    
    if os.path.exists(env_file):
        with open(env_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    # 只在环境变量不存在时设置（shell环境变量优先）
                    if key.strip() not in os.environ:
                        os.environ[key.strip()] = value.strip()

def get_db_connection():
    """获取数据库连接"""
    load_env_file()
    import pymysql
    return pymysql.connect(
        host=os.environ.get("DB_HOST", "127.0.0.1"),
        port=int(os.environ.get("DB_PORT", 3307)),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_DATABASE", "test_db"),
        charset=os.environ.get("DB_CHARSET", "utf8mb4")
    )

# 用户数据存储（模拟数据库）
users = {
    1: {"name": "张三", "role": "管理员"}
}

# 默认用户数据（用于重置）
DEFAULT_USERS = {
    1: {"name": "张三", "role": "管理员"}
}

# 产品数据存储（模拟数据库）
products = [
    {"id": 1, "name": "笔记本电脑", "price": 5999.99},
    {"id": 2, "name": "无线鼠标", "price": 199.00},
    {"id": 3, "name": "机械键盘", "price": 499.00}
]

# 用于登录验证的用户（用户名: 密码）
VALID_CREDENTIALS = {
    "admin": "123456"
}

def json_response(data, status=200):
    """统一返回 JSON 响应，确保中文正确显示"""
    response = make_response(json.dumps(data, ensure_ascii=False, indent=2))
    response.status_code = status
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response

# ============================================
# 请求验证工具函数
# ============================================

def validate_json_request(required_fields=None, field_types=None):
    """
    验证 JSON 请求
    
    Args:
        required_fields: 必填字段列表
        field_types: 字段类型映射字典，如 {"id": int, "name": str}
    
    Returns:
        (data, error_response) 元组
        - data: 解析后的 JSON 数据（如果验证通过）
        - error_response: 错误响应（如果验证失败），None 表示验证通过
    """
    # 1. 检查 Content-Type 是否为 JSON
    content_type = request.headers.get('Content-Type', '')
    if 'application/json' not in content_type and request.method == 'POST':
        return None, json_response({"error": "Content-Type 必须为 application/json"}, 400)
    
    # 2. 尝试解析 JSON
    try:
        data = request.get_json(force=False)
    except Exception as e:
        return None, json_response({"error": f"JSON 格式错误: {str(e)}"}, 400)
    
    # 3. 检查请求体是否为空
    if data is None:
        return None, json_response({"error": "请求体不能为空"}, 400)
    
    # 4. 检查数据类型是否为字典
    if not isinstance(data, dict):
        return None, json_response({"error": "请求体必须是 JSON 对象"}, 400)
    
    # 5. 检查空对象（没有任何字段）
    if not data:
        return None, json_response({"error": "请求体不能为空"}, 400)
    
    # 6. 验证必填字段
    missing_fields = []
    if required_fields:
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
            elif data[field] is None:
                missing_fields.append(field)
        
        if missing_fields:
            return None, json_response(
                {"error": f"缺失必填字段: {', '.join(missing_fields)}"}, 
                400
            )
    
    # 7. 验证字段类型
    if field_types:
        for field, expected_type in field_types.items():
            if field in data and data[field] is not None:
                if not isinstance(data[field], expected_type):
                    return None, json_response(
                        {"error": f"字段 {field} 类型错误，期望 {expected_type.__name__}"}, 
                        400
                    )
    
    return data, None

# ============================================
# Mock 接口定义
# ============================================

@app.route('/api/hello', methods=['GET'])
def hello():
    """测试接口"""
    return json_response({"message": "Mock服务器启动成功！"})

@app.route('/api/echo', methods=['GET'])
def echo():
    """返回查询参数"""
    return json_response({"args": dict(request.args)})

@app.route('/api/login', methods=['POST'])
def login():
    """登录接口 - 带完整校验（支持边界值测试）"""
    # 验证请求
    data, error = validate_json_request(
        required_fields=['username', 'password'],
        field_types={'username': str, 'password': str}
    )
    if error:
        return error
    
    original_username = data.get('username', '')
    original_password = data.get('password', '')
    username = original_username.strip()
    password = original_password.strip()
    
    # 检查空字符串（虽然 validate_json_request 已检查，但需要检查空白）
    if not username:
        return json_response({"error": "用户名不能为空"}, 400)
    if not password:
        return json_response({"error": "密码不能为空"}, 400)
    
    # 检查用户名是否包含空格（前后有空格也算非法字符）
    if ' ' in original_username:
        return json_response({"error": "用户名包含非法字符"}, 400)
    
    # 检查密码是否包含空格（前后有空格也算非法字符）
    if ' ' in original_password:
        return json_response({"error": "密码包含非法字符"}, 400)
    
    # 检查特殊字符（包含 @#$%^&*()+ 及 Unicode 表情符号）
    special_chars = '@#$%^&*()+😊'
    
    username_has_special = any(char in original_username for char in special_chars)
    password_has_special = any(char in original_password for char in special_chars)
    
    if username_has_special:
        return json_response({"error": "用户名包含非法字符"}, 400)
    
    if password_has_special:
        return json_response({"error": "密码包含非法字符"}, 400)
    
    # 边界值测试：长度限制 1-32 个字符
    if len(username) < 1 or len(username) > 32:
        return json_response({"error": "用户名或密码错误"}, 401)
    
    if len(password) < 1 or len(password) > 32:
        return json_response({"error": "用户名或密码错误"}, 401)
    
    # 检查是否为边界值测试模式（跳过密码验证，只验证格式）
    test_mode = request.headers.get('X-Test-Mode', '')
    
    # 验证用户名密码是否正确（非边界测试模式下）
    if test_mode != 'boundary' and VALID_CREDENTIALS.get(username) != password:
        return json_response({"error": "用户名或密码错误"}, 401)
    
    # 所有校验通过，返回登录成功
    return json_response({"token": "abc123", "status": "登录成功"})

@app.route('/api/user/info', methods=['GET'])
def user_info():
    """获取用户信息"""
    token = request.headers.get('Authorization')
    valid_tokens = ['Bearer abc123', 'Bearer valid_token_123456']
    if token not in valid_tokens:
        return json_response({"error": "未授权"}, 401)
    
    if 1 in users:
        return json_response({"id": 1, "name": users[1]["name"], "role": users[1]["role"]})
    return json_response({"error": "用户不存在"}, 404)

@app.route('/api/user/update', methods=['POST'])
def update_user():
    """修改用户信息 - 带完整校验"""
    token = request.headers.get('Authorization')
    if token != 'Bearer abc123':
        return json_response({"error": "未授权"}, 401)
    
    # 验证请求
    data, error = validate_json_request(
        required_fields=['id'],
        field_types={'id': (int, str), 'name': str, 'role': str}
    )
    if error:
        return error
    
    raw_id = data.get('id')
    try:
        user_id = int(raw_id)
    except (ValueError, TypeError):
        return json_response({"error": "无效的用户ID，必须为数字"}, 400)
    
    if user_id <= 0:
        return json_response({"error": "用户ID必须大于0"}, 400)
    
    if user_id in users:
        users[user_id]['name'] = data.get('name', users[user_id]['name'])
        users[user_id]['role'] = data.get('role', users[user_id]['role'])
        return json_response({"status": "success", "user": users[user_id]})
    return json_response({"error": "用户不存在"}, 404)

@app.route('/api/user/delete', methods=['GET', 'DELETE'])
def delete_user():
    """删除用户"""
    token = request.headers.get('Authorization')
    if token != 'Bearer abc123':
        return json_response({"error": "未授权"}, 401)
    
    if request.method == 'GET':
        raw_id = request.args.get('id')
    else:
        # DELETE 请求需要验证 JSON
        data, error = validate_json_request(
            required_fields=['id'],
            field_types={'id': (int, str)}
        )
        if error:
            return error
        raw_id = data.get('id')
    
    if raw_id is None:
        return json_response({"error": "缺失必填字段: id"}, 400)
    
    try:
        user_id = int(raw_id)
    except (ValueError, TypeError):
        return json_response({"error": "无效的用户ID，必须为数字"}, 400)
    
    if user_id <= 0:
        return json_response({"error": "用户ID必须大于0"}, 400)
    
    if user_id in users:
        del users[user_id]
        return json_response({"status": "deleted"})
    return json_response({"error": "用户不存在"}, 404)

@app.route('/api/user/reset', methods=['POST'])
def reset_users():
    """重置用户数据"""
    global users
    users = copy.deepcopy(DEFAULT_USERS)
    return json_response({"status": "reset success", "users": users})

@app.route('/api/delay/<int:seconds>', methods=['GET'])
def delay(seconds):
    """模拟延迟接口"""
    time.sleep(seconds)
    return json_response({"message": f"延迟{seconds}秒后返回"})

@app.route('/api/status/<int:code>', methods=['GET'])
def return_status(code):
    """返回指定状态码"""
    return json_response({"status": code}, code)

@app.route('/robots.txt', methods=['GET'])
def robots_txt():
    """robots.txt 接口"""
    robots = """User-agent: *
Disallow: /admin/
Disallow: /api/
Allow: /
"""
    return robots, 200, {'Content-Type': 'text/plain'}

@app.route('/api/error/500', methods=['GET'])
def error_500():
    """返回500状态码"""
    return json_response({"error": "服务器内部错误"}, 500)

@app.route('/api/error/malformed', methods=['GET'])
def error_malformed():
    """返回HTTP 200但响应体是畸形字符串（不是合法JSON）"""
    return "{this is not valid json", 200, {'Content-Type': 'application/json'}

@app.route('/api/error/empty', methods=['GET'])
def error_empty():
    """返回HTTP 200但响应体为空"""
    return "", 200, {'Content-Type': 'text/plain'}

@app.route('/html', methods=['GET'])
def html_page():
    """HTML 页面接口"""
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <meta charset="UTF-8">
</head>
<body>
    <h1>Welcome to the Test Page</h1>
    <p>This is a test HTML page for API testing.</p>
</body>
</html>"""
    return html, 200, {'Content-Type': 'text/html'}

@app.route('/api/product/list', methods=['GET', 'POST'])
def product_list():
    """获取产品列表（不需要鉴权）"""
    if request.method == 'POST':
        return json_response({"error": "Method Not Allowed"}, 405)
    return json_response({"products": products})

@app.route('/api/register', methods=['POST'])
def register():
    """用户注册接口
    
    请求体:
        username: 用户名 (必填, VARCHAR(50))
        password: 密码 (必填, VARCHAR(50))
        email: 邮箱 (可选, VARCHAR(100))
        role: 角色 (可选, 默认 'user', VARCHAR(20))
    
    返回:
        id: 用户ID (自增)
        username: 用户名
        password: 密码
        email: 邮箱
        role: 角色
        created_at: 创建时间
    """
    # 验证请求
    data, error = validate_json_request(
        required_fields=['username', 'password'],
        field_types={'username': str, 'password': str, 'email': str, 'role': str}
    )
    if error:
        return error
    
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    email = data.get('email', '').strip() if data.get('email') else None
    role = data.get('role', 'user').strip() if data.get('role') else 'user'
    
    # 检查用户名是否为空
    if not username:
        return json_response({"error": "用户名不能为空"}, 400)
    
    # 检查密码是否为空
    if not password:
        return json_response({"error": "密码不能为空"}, 400)
    
    # 检查用户名长度 (VARCHAR(50))
    if len(username) > 50:
        return json_response({"error": "用户名长度不能超过50个字符"}, 400)
    
    # 检查密码长度 (VARCHAR(50))
    if len(password) > 50:
        return json_response({"error": "密码长度不能超过50个字符"}, 400)
    
    # 检查邮箱长度 (VARCHAR(100))
    if email and len(email) > 100:
        return json_response({"error": "邮箱长度不能超过100个字符"}, 400)
    
    # 检查角色长度 (VARCHAR(20))
    if len(role) > 20:
        return json_response({"error": "角色长度不能超过20个字符"}, 400)
    
    # 连接数据库并检查用户名是否已存在
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 检查用户名是否已存在
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        if cursor.fetchone():
            return json_response({"error": "用户名已存在"}, 409)
        
        # 插入新用户
        import datetime
        created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(
            "INSERT INTO users (username, password, email, role, created_at) VALUES (%s, %s, %s, %s, %s)",
            (username, password, email, role, created_at)
        )
        conn.commit()
        
        user_id = cursor.lastrowid
        
        # 查询刚插入的用户信息
        cursor.execute("SELECT id, username, email, role, created_at FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        new_user = dict(zip(columns, row))
        
        # 将 datetime 对象转换为字符串
        if 'created_at' in new_user and new_user['created_at']:
            if hasattr(new_user['created_at'], 'strftime'):
                new_user['created_at'] = new_user['created_at'].strftime("%Y-%m-%d %H:%M:%S")
        
        return json_response({"status": "注册成功", "user": new_user}, 201)
        
    except Exception as e:
        if conn:
            conn.rollback()
        return json_response({"error": f"注册失败: {str(e)}"}, 500)
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

if __name__ == '__main__':
    app.run(debug=True)
