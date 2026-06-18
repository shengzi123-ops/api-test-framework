# API Test Framework

![Tests](https://github.com/shengzi123-ops/api-test-framework/actions/workflows/test.yml/badge.svg)

## 1. 项目简介

基于 pytest + requests + Flask + MySQL 的接口自动化测试框架，支持数据驱动、Session管理、超时重试、失败响应保存、并发执行，集成数据库验证能力。

## 2. 目录结构树

```
api_test_framework/
├── core/                          # 核心模块
│   ├── __init__.py
│   ├── api_client.py              # API 请求封装
│   └── assertions.py              # 断言函数
├── utils/                         # 工具模块
│   ├── __init__.py
│   ├── data_loader.py             # CSV 数据加载
│   ├── db_utils.py                # 数据库工具
│   └── logger.py                  # 日志工具
├── server/                        # Mock 服务器
│   ├── mock_server.py
│   └── start_server.bat
├── scripts/                       # 工具脚本
│   ├── run_tests.bat              # 一键启动脚本（双击运行）
│   ├── run_tests.py               # 测试主程序
│   └── init_db.sql                # 数据库初始化脚本
├── tests/                         # 测试用例
│   ├── test_data/                 #csv测试用例
│   │   ├── login_data.csv
│   │   ├── product_data.csv
│   │   └── test_boundary_data.csv
│   ├── conftest.py                # Pytest 配置，提供全局 Fixture
│   ├── test_boundary.py           # 边界值测试
│   ├── test_db_integration.py     # 数据库集成测试
│   ├── test_login.py              # 登录接口测试
│   ├── test_product.py            # 产品列表测试
│   ├── test_public_api.py         # 公共API测试
│   ├── test_timeout_retry.py      # 超时重试测试
│   ├── test_user_flow.py          # 用户流程测试
│   └── test_user_info.py          # 用户信息测试
├── failed_responses/              # 失败响应保存
├── logs/                          # 日志文件
├── reports/                       # 测试报告
├── .env                           # 环境配置
├── pytest.ini                     # Pytest 配置
├── requirements.txt              # 依赖清单
└── README.md                      # 项目说明
```

## 3. 数据流

框架采用数据驱动模式，以 CSV 测试数据为入口，经过数据解析、参数化注入、鉴权处理、接口请求、自动断言全流程闭环，测试流程标准化、自动化。
完整数据流如下：

```
CSV 数据文件
    │
    ▼
data_loader.parse_test_case()      ← 字段解析、类型转换
    │
    ▼
@pytest.mark.parametrize           ← 参数化注入
    │
    ├─→ 鉴权分组 (requires_auth 字段)
    │       │
    │       ▼
    │   conftest.inject_auth_header ← 自动注入 Token
    │
    ▼
api_session.get/post/put/delete    ← 发送请求 (自动日志)
    │
    ▼
Mock 服务器 / 公开 API              ← 接收请求并返回响应
    │
    ▼
assert_response_by_type            ← 自动分发断言
    │
    ├─→ assert_json_response       ← JSON 响应断言
    ├─→ assert_text_response       ← 文本响应断言
    └─→ assert_content_response    ← 二进制响应断言
    │
    ▼
测试报告生成 / 失败响应保存
```

## 4. 快速开始

### 4.1 环境要求

- Python 3.8+
- MySQL 5.7+ 或 MySQL 8.0+

### 4.2 安装依赖

```bash
pip install -r requirements.txt
```

依赖包说明：
- `flask` - Mock 服务器框架
- `requests` - HTTP 请求库
- `pytest` - 测试框架
- `pytest-html` - HTML 测试报告
- `pytest-xdist` - 并发执行
- `pymysql` - MySQL 数据库驱动
- `python-dotenv` - 环境变量加载

### 4.3 配置环境变量

在 `.env` 文件中设置数据库连接参数：

```env
# 数据库配置
DB_HOST=127.0.0.1
DB_PORT=3307
DB_USER=root
DB_PASSWORD=your_password_here
DB_DATABASE=test_db
DB_CHARSET=utf8mb4
```

在脚本中加载环境变量：

```python
from dotenv import load_dotenv
load_dotenv()
```

### 4.4 启动 Mock 服务

```bash
python server/mock_server.py
```

或者使用批处理文件（Windows）：

```bash
server\start_server.bat
```

### 4.5 一键启动（推荐）

**方式1：双击运行（Windows）**
```bash
# 直接双击以下文件
scripts\run_tests.bat
```

**方式2：命令行运行**
```bash
python scripts/run_tests.py
```

一键启动脚本会自动完成：
1. ✅ 环境自检（检查 Python、MySQL）
2. ✅ 自动启动 Mock 服务器
3. ✅ 运行所有测试
4. ✅ 生成 HTML 报告
5. ✅ 自动打开浏览器查看报告
6. ✅ 测试结束后自动关闭 Mock 服务器

> **说明**：一键启动脚本默认跳过 `test_timeout_retry.py`（超时重试测试），因为该测试执行时间较长（3-5秒），不适合高频快速验证。此跳过**仅影响本地一键启动**，不影响：
> - GitHub Actions CI/CD 流水线（仍执行全量测试）
> - 手动运行全量测试（`pytest tests/ -v`）

### 4.6 手动运行测试

**运行全量测试**：
```bash
pytest tests/ -v --html=reports/report.html --self-contained-html
```

**运行特定测试文件**：
```bash
pytest tests/test_login.py -v
```

**运行特定测试用例**：
```bash
pytest tests/test_login.py::test_login -v
```

**运行带标记的测试**：
```bash

pytest tests/ -v -m smoke # 只跑冒烟测试

pytest tests/ -v -m auth_required # 只跑需要鉴权的⽤例
```

## 5. 核心设计亮点

### 5.1 请求封装层支持无状态和会话两种模式

- **无状态模式**：直接调用 `api_get()`、`api_post()` 等独立函数
- **会话模式**：使用 `ApiSession` 类维护会话，自动管理 Cookie 和 Headers

```python
# 无状态模式
status, body = api_post("/api/login", json_data={"username": "admin", "password": "123"})

# 会话模式
api = ApiSession("http://127.0.0.1:5000")
api.set_default_headers({"Authorization": "Bearer abc123"})
status, body = api.post("/api/user/update", json_data={"id": 1, "name": "新名称"})
```

### 5.2 超时重试机制

`api_get_with_retry()` 函数支持：
- **可配置重试次数**：默认 3 次
- **状态码重试**：自动重试 500/502/503/504 错误
- **退避算法**：支持线性递增退避，最小等待时间
- **详细日志**：记录每次重试的原因和等待时间

```python
status, body = api_get_with_retry(
    url="http://127.0.0.1:5000/api/unstable",
    max_retries=5,
    backoff=2,
    retry_on_status=[500, 502, 503, 504, 429],
    min_wait=1
)
```

### 5.3 统一断言引擎

`assert_response_by_type()` 支持多种响应类型断言：
- **JSON 响应**：验证状态码、字段值、字段类型、数据结构
- **文本响应**：验证状态码、包含/不包含关键字
- **二进制响应**：验证状态码、响应长度

**失败时自动保存**：测试失败后自动保存响应内容到 `failed_responses/` 目录，便于问题排查。

```python
# JSON 断言示例
assert_response_by_type(200, body, "json", {
    "expected_status": 200,
    "expected_items": ["token", "status"],
    "expected_values": {"status": "登录成功"}
})

# 文本断言示例
assert_response_by_type(200, "Hello World", "text", {
    "expected_status": 200,
    "expected_contains": ["Hello", "World"]
})
```

### 5.4 数据驱动与代码分离

使用 CSV 文件管理测试数据，测试代码与测试数据解耦：

```python
# test_data/login_data.csv
case_name,username,password,expected_status,expected_error
正向登录,admin,123456,200,
密码错误,admin,wrong,401,用户名或密码错误
用户不存在,notexist,123456,401,用户名或密码错误
```

```python
# 测试代码
cases = load_csv_test_data("tests/test_data/login_data.csv")
for case in cases:
    parsed = parse_test_case(case)
    status, body = api.post("/api/login", json_data=parsed["body"])
    assert_response_by_type(status, body, parsed["response_type"], parsed)
```

### 5.5 鉴权标记机制

使用 pytest 标记自动管理鉴权头，无需在每个测试中手动设置：

```python
# 标记需要鉴权的测试
@pytest.mark.auth_required
def test_user_info(api_session):
    status, body = api_session.get("/api/user/info")
    assert status == 200
```

**自动处理**：conftest.py 中的 `inject_auth_header` fixture 自动为带标记的测试注入 Authorization 头，测试结束后自动清理。

### 5.6 测试隔离与数据重置

- **Mock 数据重置**：每个测试前自动调用 `/api/user/reset` 重置 Mock 服务器状态
- **数据库隔离**：测试数据在测试结束后清理，不污染数据库
- **会话清理**：每个测试后自动重置 Headers，关闭连接

```python
# conftest.py
@pytest.fixture(scope="function", autouse=True)
def reset_server_data(api_session):
    """每个测试前自动重置 Mock 数据"""
    api_session.post("/api/user/reset")
    yield
```

### 5.7 并发执行与风险分析

支持 pytest-xdist 并发执行，提升测试效率：

```bash
# 并发运行所有测试（4个进程）
pytest tests/ -n 4 -v

# 只运行不需要数据库的测试
pytest tests/ -m "not db_integration" -n 4 -v
```

**风险分析**：
- 并发测试可能冲突的用例需要加锁或串行执行
- 数据库集成测试建议单独运行，避免并发写入冲突

### 5.8 Mock 服务器统一校验

Mock 服务器提供完整的请求验证能力：

- **必填字段验证**：自动检查请求体中的必填字段
- **字段类型验证**：验证参数类型是否正确
- **边界值校验**：支持长度限制、特殊字符等边界测试
- **错误模拟**：提供 500 错误、畸形 JSON、空响应等错误场景

### 5.9 数据库集成验证

集成真实数据库，支持端到端测试：

- **配置管理**：通过 .env 文件管理数据库连接参数
- **事务保护**：使用 try-except-rollback 确保数据一致性
- **测试数据清理**：测试结束后自动删除测试数据，不污染数据库

```python
# 测试注册接口与数据库的集成
def test_register_db_integration(api_session, db_connection):
    conn, cursor = db_connection
    
    # 调用注册接口
    status, body = api_session.post("/api/register", json_data={
        "username": "test_user",
        "password": "123456",
        "email": "test@example.com"
    })
    
    # 从数据库查询验证
    db_user = query_user_by_username(cursor, "test_user")
    assert db_user["username"] == "test_user"
    
    # 清理测试数据
    delete_user_by_username(cursor, conn, "test_user")
```

## 6. 测试数据说明

### 6.1 测试数据文件

| 文件 | 用途 |
|------|------|
| `test_data/login_data.csv` | 登录接口测试数据 |
| `test_data/product_data.csv` | 产品列表接口测试数据 |
| `test_data/test_boundary_data.csv` | 边界值测试数据 |

### 6.2 数据字段说明

CSV 文件支持以下字段：

| 字段 | 说明 |
|------|------|
| `case_name` | 用例名称 |
| `method` | HTTP 方法（GET/POST/PUT/DELETE） |
| `url` | 请求路径 |
| `body` | 请求体（JSON 格式） |
| `headers` | 请求头 |
| `response_type` | 响应类型（json/text/content） |
| `expected_status` | 期望状态码 |
| `expected_error` | 期望错误信息 |
| `requires_auth` | 是否需要鉴权（true/false） |

## 7. 输出说明

### 7.1 测试报告

生成的 HTML 报告保存在 `reports/` 目录：
- `report.html` - 普通报告
- `final_report.html` - 完整报告（包含 CSS）

### 7.2 日志文件

运行日志保存在 `logs/` 目录，格式：`test_YYYYMMDD.log`

### 7.3 失败响应

测试失败时，响应内容自动保存到 `failed_responses/` 目录，文件命名格式：`{case_name}_{timestamp}.{json|txt|bin}`

## 8. CI/CD 流水线

### 8.1 自动触发条件

项目已配置 GitHub Actions 流水线，支持以下触发方式：

| 触发方式 | 条件 | 说明 |
|----------|------|------|
| **push** | 推送到 `main` 分支 | 代码变更时自动运行 |
| **schedule** | 每天北京时间 06:00 | 定时自动运行测试 |
| **workflow_dispatch** | 手动点击按钮 | 随时手动触发运行 |

### 8.2 定时任务配置

流水线会**每天北京时间凌晨 06:00**自动运行测试：

```yaml
# .github/workflows/test.yml
on:
  push:
    branches: [main]
  schedule:
    - cron: '0 22 * * *'  # UTC 22:00 = 北京时间 06:00
```

**时区说明**：
- 北京时间 06:00 = UTC 时间 22:00（前一天）

### 8.3 查看流水线状态

1. 打开 GitHub 仓库：https://github.com/shengzi123-ops/api-test-framework
2. 点击 **Actions** 标签
3. 查看流水线运行状态和历史记录

### 8.4 手动触发流水线

除了自动触发，也可以手动触发流水线：

1. 打开 GitHub 仓库：https://github.com/shengzi123-ops/api-test-framework
2. 点击 **Actions** 标签
3. 在左侧选择 **API Tests** workflow
4. 点击 **Run workflow** 按钮
5. 选择目标分支（默认 `main`）
6. 点击 **Run workflow** 开始执行

### 8.5 流水线输出

- **测试报告**：自动生成 HTML 报告，可从 Artifacts 下载
- **运行日志**：完整的测试输出日志
- **状态徽章**：显示最近一次运行的状态

## 9. 常见问题

### 9.1 Mock 服务器无法启动

检查端口是否被占用：
```bash
netstat -ano | findstr 5000
```

### 9.2 数据库连接失败

确认 .env 文件中的数据库配置正确，且 MySQL 服务已启动。

### 9.3 测试数据残留

如果测试数据未清理，可以手动执行：
```python
from utils.db_utils import connect_db, delete_user_by_username

conn = connect_db()
cursor = conn.cursor()
delete_user_by_username(cursor, conn, "test_user")
conn.close()
```

## 10. 许可证

本项目仅供学习交流使用。
