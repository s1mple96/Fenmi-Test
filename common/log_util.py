# -*- coding: utf-8 -*-
# -------------------------------------------------------------
# 日志工具类，自动写入 log 目录，支持多模块日志
# -------------------------------------------------------------
import logging
import os
import sys
from datetime import datetime

def get_log_dir():
    """获取日志目录路径"""
    if hasattr(sys, 'frozen') and sys.frozen:
        # 打包后的exe环境 - 日志文件放在exe同目录的log文件夹
        exe_dir = os.path.dirname(sys.executable)
        log_dir = os.path.join(exe_dir, 'log')
    else:
        # 开发环境 - 日志文件放在项目根目录的log文件夹
        log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'log')
    
    # 确保日志目录存在
    if not os.path.exists(log_dir):
        try:
            os.makedirs(log_dir)
        except Exception as e:
            print(f"创建日志目录失败: {e}")
            # 如果无法创建日志目录，使用临时目录
            import tempfile
            log_dir = tempfile.gettempdir()
    
    return log_dir

class LogUtil:
    # 日志目录和文件自动创建
    LOG_DIR = get_log_dir()
    LOG_FILE = os.path.join(LOG_DIR, f"run_{datetime.now().strftime('%Y%m%d')}.log")

    @staticmethod
    def get_log_dir():
        """获取日志目录路径"""
        return get_log_dir()

    @staticmethod
    def get_logger(name: str = 'default'):
        """
        获取 logger 实例，自动写入日志文件
        :param name: 日志名称
        :return: logger对象
        """
        logger = logging.getLogger(name)
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
            file_handler = logging.FileHandler(LogUtil.LOG_FILE, encoding='utf-8')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        return logger

# 模块级别的 get_logger 函数，供外部直接导入使用
def get_logger(name: str = 'default'):
    """
    模块级别的 get_logger 函数，内部调用 LogUtil.get_logger
    :param name: 日志名称
    :return: logger对象
    """
    return LogUtil.get_logger(name)
