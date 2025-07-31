# -*- coding: utf-8 -*-
"""
日志服务 - 统一管理日志记录和格式化
"""
import logging
import sys
from typing import Optional, Dict, Any
from datetime import datetime


class LogService:
    """日志服务"""
    
    def __init__(self, name: str = "etc_apply", log_file: Optional[str] = None):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # 避免重复添加handler
        if not self.logger.handlers:
            self._setup_handlers(log_file)
    
    def _setup_handlers(self, log_file: Optional[str] = None):
        """设置日志处理器"""
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        
        # 控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # 文件处理器（如果指定了日志文件）
        if log_file:
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
    
    def info(self, message: str):
        """记录信息日志"""
        self.logger.info(message)
    
    def error(self, message: str):
        """记录错误日志"""
        self.logger.error(message)
    
    def warning(self, message: str):
        """记录警告日志"""
        self.logger.warning(message)
    
    def debug(self, message: str):
        """记录调试日志"""
        self.logger.debug(message)
    
    def log_api_request(self, path: str, data: Dict[str, Any]):
        """记录API请求日志"""
        self.info(f"【接口请求】{path}\n参数: {data}")
    
    def log_api_response(self, path: str, response: Any):
        """记录API响应日志"""
        self.info(f"【接口响应】{path}\n内容: {response}")
    
    def log_api_error(self, path: str, data: Dict[str, Any], error: Exception):
        """记录API错误日志"""
        self.error(f"【接口异常】{path}\n参数: {data}\n错误: {error}")
    
    def log_step_start(self, step_number: int, step_name: str):
        """记录步骤开始日志"""
        self.info(f"{step_number}. {step_name}")
    
    def log_step_success(self, step_number: int, step_name: str):
        """记录步骤成功日志"""
        self.info(f"{step_number}. {step_name}完成")
    
    def log_step_failure(self, step_number: int, step_name: str, error: Exception):
        """记录步骤失败日志"""
        self.error(f"{step_number}. {step_name}失败: {str(error)}")
    
    def log_step_exception(self, step_number: int, step_name: str, error: Exception):
        """记录步骤异常日志"""
        self.error(f"{step_number}. {step_name}异常: {str(error)}")
    
    def log_flow_start(self, params: Dict[str, Any]):
        """记录流程开始日志"""
        self.info("=== ETC申办流程开始 ===")
        self.info(f"车牌号: {params.get('carNum', 'N/A')}")
        self.info(f"持卡人: {params.get('cardHolder', 'N/A')}")
        self.info(f"产品ID: {params.get('productId', 'N/A')}")
    
    def log_flow_complete(self, result: Dict[str, Any]):
        """记录流程完成日志"""
        self.info("=== ETC申办流程完成 ===")
        self.info(f"结果: {result}")
    
    def log_flow_error(self, error: Exception):
        """记录流程错误日志"""
        self.error("=== ETC申办流程异常 ===")
        self.error(f"错误: {str(error)}")
    
    def log_parameter_validation(self, params: Dict[str, Any]):
        """记录参数验证日志"""
        self.info("=== 参数验证 ===")
        for key, value in params.items():
            if key in ['carNum', 'cardHolder', 'idCode', 'bindBankPhone', 'bindBankNo']:
                # 敏感信息脱敏
                if key == 'idCode' and value:
                    masked_value = value[:6] + '*' * (len(value) - 10) + value[-4:] if len(value) > 10 else value
                elif key == 'bindBankNo' and value:
                    masked_value = value[:4] + '*' * (len(value) - 8) + value[-4:] if len(value) > 8 else value
                elif key == 'bindBankPhone' and value:
                    masked_value = value[:3] + '*' * (len(value) - 7) + value[-4:] if len(value) > 7 else value
                else:
                    masked_value = value
                self.info(f"{key}: {masked_value}")
    
    def log_product_selection(self, product: Dict[str, Any]):
        """记录产品选择日志"""
        self.info("=== 产品选择 ===")
        self.info(f"产品名称: {product.get('product_name', 'N/A')}")
        self.info(f"产品ID: {product.get('product_id', 'N/A')}")
        self.info(f"运营商: {product.get('operator_code', 'N/A')}")
    
    def log_order_info(self, order_id: str, sign_order_id: str, verify_code_no: str):
        """记录订单信息日志"""
        self.info("=== 订单信息 ===")
        self.info(f"订单ID: {order_id}")
        self.info(f"签约订单ID: {sign_order_id}")
        self.info(f"验证码编号: {verify_code_no}")


class UILogService:
    """UI日志服务 - 专门处理UI相关的日志显示"""
    
    @staticmethod
    def format_log_message(message: str, level: str = "INFO") -> str:
        """
        格式化日志消息
        :param message: 消息内容
        :param level: 日志级别
        :return: 格式化的消息
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        return f"[{timestamp}] {level}: {message}"
    
    @staticmethod
    def format_progress_message(step_number: int, step_name: str, status: str = "完成") -> str:
        """
        格式化进度消息
        :param step_number: 步骤编号
        :param step_name: 步骤名称
        :param status: 状态
        :return: 格式化的进度消息
        """
        return f"{step_number}. {step_name}{status}"
    
    @staticmethod
    def format_error_message(step_number: int, step_name: str, error: str) -> str:
        """
        格式化错误消息
        :param step_number: 步骤编号
        :param step_name: 步骤名称
        :param error: 错误信息
        :return: 格式化的错误消息
        """
        return f"{step_number}. {step_name}失败: {error}"
    
    @staticmethod
    def mask_sensitive_info(text: str) -> str:
        """
        脱敏敏感信息
        :param text: 原始文本
        :return: 脱敏后的文本
        """
        # 身份证号脱敏
        import re
        id_pattern = r'(\d{6})\d{8}(\d{4})'
        text = re.sub(id_pattern, r'\1********\2', text)
        
        # 银行卡号脱敏
        bank_pattern = r'(\d{4})\d{8,12}(\d{4})'
        text = re.sub(bank_pattern, r'\1********\2', text)
        
        # 手机号脱敏
        phone_pattern = r'(\d{3})\d{4}(\d{4})'
        text = re.sub(phone_pattern, r'\1****\2', text)
        
        return text 