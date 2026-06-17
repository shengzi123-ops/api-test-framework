import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 加载 .env 环境变量文件（从项目根目录加载）
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from dotenv import load_dotenv
env_file = os.path.join(project_root, '.env')
load_dotenv(env_file, override=True)
BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")

from core.api_client import ApiSession
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_user_flow():
    """完整的用户操作流程测试"""
    api = ApiSession(BASE_URL)
    
    try:
        logger.info("=" * 60)
        logger.info("🚀 开始测试：完整用户操作流程")
        logger.info("=" * 60)
        
        # 0. 重置用户数据（确保测试环境干净）
        logger.info("📋 步骤0：重置用户数据")
        status, body = api.post("/api/user/reset")
        assert status == 200, f"重置失败：状态码={status}"
        logger.info(f"✅ 重置成功：{body}")
        
        # 1. 登录
        logger.info("📋 步骤1：登录")
        status, body = api.post("/api/login", json_data={"username": "admin", "password": "123456"})
        assert status == 200, f"登录失败：状态码={status}, 响应={body}"
        token = body["token"]
        logger.info(f"✅ 登录成功，token: {token}")
        api.set_default_headers({"Authorization": f"Bearer {token}"})
        
        # 2. 查询用户信息
        logger.info("📋 步骤2：查询用户信息")
        status, body = api.get("/api/user/info")
        assert status == 200, f"查询失败：状态码={status}"
        assert body["name"] == "张三", f"用户名错误：期望=张三，实际={body.get('name')}"
        logger.info(f"✅ 查询成功：{body}")
        
        # 3. 修改用户信息
        logger.info("📋 步骤3：修改用户信息")
        status, body = api.post("/api/user/update", json_data={"id": 1, "name": "李四", "role": "超级管理员"})
        assert status == 200, f"修改失败：状态码={status}"
        assert body["user"]["name"] == "李四", f"修改后用户名错误：期望=李四，实际={body.get('user', {}).get('name')}"
        logger.info(f"✅ 修改成功：{body}")
        
        # 4. 查询验证修改
        logger.info("📋 步骤4：验证修改")
        status, body = api.get("/api/user/info")
        assert status == 200, f"查询失败：状态码={status}"
        assert body["name"] == "李四", f"验证失败：期望=李四，实际={body.get('name')}"
        logger.info(f"✅ 验证通过：{body}")
        
        # 5. 删除用户
        logger.info("📋 步骤5：删除用户")
        status, body = api.get("/api/user/delete?id=1")
        assert status == 200, f"删除失败：状态码={status}"
        logger.info(f"✅ 删除成功：{body}")
        
        # 6. 验证删除
        logger.info("📋 步骤6：验证删除")
        status, body = api.get("/api/user/info")
        assert status == 404, f"验证失败：期望=404，实际={status}"
        logger.info(f"✅ 验证删除成功：{body}")
        
        logger.info("=" * 60)
        logger.info("🎉 完整流程测试通过")
        logger.info("=" * 60)
        
    except AssertionError as e:
        logger.error(f"❌ 测试失败：{e}")
        raise
    except Exception as e:
        logger.error(f"❌ 测试异常：{e}")
        raise
    finally:
        # 清理资源
        api.reset_headers()
        api.close()
        logger.info("🔒 资源已清理")

if __name__ == "__main__":
    test_user_flow()
