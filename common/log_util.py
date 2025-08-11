# -*- coding: utf-8 -*-
# -------------------------------------------------------------
# 日志工具类，自动写入 log 目录，支持多模块日志
# -------------------------------------------------------------
import logging
import os
from datetime import datetime

class LogUtil:
    # 日志目录和文件自动创建
    LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'log')
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    LOG_FILE = os.path.join(LOG_DIR, f"run_{datetime.now().strftime('%Y%m%d')}.log")

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
