import os
import sys
import time
import subprocess
import webbrowser
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_run.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def check_mysql():
    """检查MySQL服务是否启动"""
    try:
        import pymysql
        conn = pymysql.connect(
            host='127.0.0.1',
            port=3307,
            user='root',
            password='S1047989171',
            database='test_db'
        )
        conn.close()
        logging.info("✅ MySQL连接成功")
        return True
    except Exception as e:
        logging.warning(f"⚠️ MySQL未启动或连接失败: {e}")
        return False

def start_mysql():
    """尝试启动MySQL服务"""
    logging.info("尝试启动MySQL服务...")
    try:
        subprocess.run(
            ['net', 'start', 'MySQL'],
            check=True,
            capture_output=True,
            text=True
        )
        time.sleep(3)
        if check_mysql():
            logging.info("✅ MySQL启动成功")
            return True
        else:
            logging.error("❌ MySQL启动后仍无法连接")
            return False
    except subprocess.CalledProcessError as e:
        logging.warning(f"⚠️ 使用net start失败: {e.stderr}")
        return False

def start_mock_server():
    """启动Mock服务器"""
    logging.info("启动Mock服务器...")
    process = subprocess.Popen(
        [sys.executable, 'server/mock_server.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    time.sleep(3)
    
    if process.poll() is not None:
        stderr = process.stderr.read().decode('utf-8', errors='ignore')
        logging.error(f"❌ Mock服务器启动失败: {stderr}")
        return None
    
    logging.info("✅ Mock服务器启动成功")
    return process

def ensure_report_dir():
    """确保报告目录存在"""
    os.makedirs('reports', exist_ok=True)

def run_tests():
    """运行pytest测试"""
    logging.info("开始执行测试...")
    ensure_report_dir()
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = f'reports/test_report_{timestamp}.html'
    
    result = subprocess.run(
        [
            sys.executable, '-m', 'pytest',
            'tests/', '-v',
            f'--html={report_path}',
            '--self-contained-html'
        ],
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace'
    )
    
    logging.info(f"测试完成，退出码: {result.returncode}")
    
    if result.stdout:
        for line in result.stdout.split('\n')[-15:]:
            logging.info(f"测试输出: {line}")
    
    if result.stderr:
        logging.error(f"错误输出: {result.stderr[:500]}")
    
    return report_path, result.returncode

def open_report(report_path):
    """在浏览器中打开报告"""
    if os.path.exists(report_path):
        abs_path = os.path.abspath(report_path)
        logging.info(f"📊 打开报告: {abs_path}")
        webbrowser.open(f'file://{abs_path}')
    else:
        logging.error("❌ 报告文件不存在")

def clean_up(mock_process):
    """清理工作：关闭Mock服务器"""
    logging.info("🧹 清理资源...")
    
    if mock_process:
        try:
            mock_process.terminate()
            try:
                mock_process.wait(timeout=3)
                logging.info("✅ Mock服务器已优雅关闭")
            except subprocess.TimeoutExpired:
                mock_process.kill()
                logging.info("⚠️ 强制关闭Mock服务器")
        except Exception as e:
            logging.warning(f"关闭Mock服务器时出错: {e}")

def main():
    """主函数"""
    mock_process = None
    
    try:
        logging.info("===== 🚀 开始环境自检 =====")
        
        # 1. 检查MySQL
        if not check_mysql():
            logging.info("尝试自动启动MySQL...")
            if not start_mysql():
                logging.warning("MySQL启动失败，请手动启动MySQL服务后重试")
        
        # 2. 启动Mock服务器
        mock_process = start_mock_server()
        if not mock_process:
            logging.error("Mock服务器启动失败，退出")
            return
        
        # 3. 运行测试
        report_path, exit_code = run_tests()
        
        # 4. 打开报告
        open_report(report_path)
        
        # 5. 结果总结
        if exit_code == 0:
            logging.info("🎉 所有测试通过！")
        else:
            logging.warning(f"⚠️ 测试未全部通过，退出码: {exit_code}")
            
    except Exception as e:
        logging.error(f"❌ 执行过程中发生错误: {e}", exc_info=True)
    finally:
        # 6. 清理工作
        clean_up(mock_process)
        logging.info("===== 🏁 测试流程结束 =====")

if __name__ == '__main__':
    main()