import logging
import os
from datetime import datetime


def configure_logging():
    """配置日志（可由主程序调用，简化版）"""
    # 避免重复配置
    root_logger = logging.getLogger()
    if root_logger.handlers:
        return  # 已配置过
    
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # 增加文件日志处理器
    log_filename = os.path.join(os.path.dirname(__file__), 'api_client.log')
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    root_logger.addHandler(file_handler)


def setup_logging(
    level=logging.INFO,
    log_format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    log_dir=None,
    log_filename=None,
    console_output=True,
    file_output=True,
    clear_existing_handlers=True
):
    """
    灵活配置日志系统
    
    Args:
        level: 日志级别，默认为 logging.INFO
        log_format: 日志格式字符串
        log_dir: 日志文件目录，默认为 None（使用当前目录）
        log_filename: 日志文件名，默认为 None（自动生成带日期的文件名）
        console_output: 是否输出到控制台，默认为 True
        file_output: 是否输出到文件，默认为 True
        clear_existing_handlers: 是否清除已存在的处理器，默认为 True
    
    Returns:
        logging.Logger: 配置好的根日志器
    """
    # 获取根日志器
    root_logger = logging.getLogger()
    
    # 设置日志级别
    root_logger.setLevel(level)
    
    # 清除已存在的处理器（避免重复输出）
    if clear_existing_handlers and root_logger.handlers:
        root_logger.handlers.clear()
    
    # 创建日志格式器
    formatter = logging.Formatter(log_format)
    
    # 控制台输出
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    # 文件输出
    if file_output:
        # 确定日志目录
        if log_dir is None:
            log_dir = os.path.dirname(__file__)
        
        # 确保目录存在
        os.makedirs(log_dir, exist_ok=True)
        
        # 确定日志文件名
        if log_filename is None:
            timestamp = datetime.now().strftime("%Y%m%d")
            log_filename = f"test_{timestamp}.log"
        
        log_path = os.path.join(log_dir, log_filename)
        file_handler = logging.FileHandler(log_path, encoding='utf-8')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    return root_logger


