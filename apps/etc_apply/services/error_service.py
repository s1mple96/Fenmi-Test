# -*- coding: utf-8 -*-
"""
错误处理服务 - 统一管理异常处理和错误响应
"""
import json
import traceback
from typing import Dict, Any, Optional


class ErrorService:
    """错误处理服务"""
    
    @staticmethod
    def assert_api_success(resp: Any, api_name: str = "接口") -> None:
        """
        断言API响应成功
        :param resp: API响应
        :param api_name: API名称
        :raises: Exception 当响应不成功时
        """
        if isinstance(resp, str):
            try:
                resp = json.loads(resp)
            except Exception:
                raise Exception(f"{api_name} 响应不是有效的JSON: {resp}")
        
        if resp.get("code") != 200:
            msg = resp.get("msg") or resp.get("message") or str(resp)
            raise Exception(f"{api_name} 失败，原因: {msg}，返回内容: {resp}")
    
    @staticmethod
    def assert_save_success(resp_text: str, step_name: str = "") -> None:
        """
        断言保存操作成功
        :param resp_text: 响应文本
        :param step_name: 步骤名称
        :raises: Exception 当保存失败时
        """
        if "success" not in resp_text:
            raise Exception(f"{step_name}保存失败，响应内容：{resp_text[:200]}")
    
    @staticmethod
    def format_error_message(step_number: int, step_name: str, error: Exception) -> str:
        """
        格式化错误消息
        :param step_number: 步骤编号
        :param step_name: 步骤名称
        :param error: 异常对象
        :return: 格式化的错误消息
        """
        return f"{step_number}. {step_name}失败: {str(error)}"
    
    @staticmethod
    def format_exception_message(step_number: int, step_name: str, error: Exception) -> str:
        """
        格式化异常消息
        :param step_number: 步骤编号
        :param step_name: 步骤名称
        :param error: 异常对象
        :return: 格式化的异常消息
        """
        return f"{step_number}. {step_name}异常: {str(error)}"
    
    @staticmethod
    def handle_api_exception(api_name: str, url: str, data: Dict[str, Any], error: Exception) -> Exception:
        """
        处理API异常
        :param api_name: API名称
        :param url: 请求URL
        :param data: 请求数据
        :param error: 原始异常
        :return: 格式化的异常
        """
        # 只显示关键错误信息，避免UI被撑大
        error_msg = str(error)
        if "接口响应格式错误" in error_msg:
            # 提取具体的错误原因
            if ":" in error_msg:
                return Exception(f"接口响应格式错误: {error_msg.split(':', 1)[1].strip()}")
            else:
                return Exception(f"接口响应格式错误: {error_msg}")
        else:
            # 其他错误只显示错误信息，不显示URL和参数
            return Exception(f"接口调用失败: {error_msg}")
    
    @staticmethod
    def validate_required_params(params: Dict[str, Any], required_keys: list) -> None:
        """
        验证必需参数
        :param params: 参数字典
        :param required_keys: 必需参数列表
        :raises: ValueError 当缺少必需参数时
        """
        missing_keys = [key for key in required_keys if not params.get(key)]
        if missing_keys:
            raise ValueError(f"缺少必需参数: {', '.join(missing_keys)}")
    
    @staticmethod
    def safe_get_nested(data: Dict[str, Any], keys: list, default: Any = None) -> Any:
        """
        安全获取嵌套字典的值
        :param data: 数据字典
        :param keys: 键路径列表
        :param default: 默认值
        :return: 获取的值或默认值
        """
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current
    
    @staticmethod
    def format_api_error(api_name: str, response: Dict[str, Any], url: str = "") -> str:
        """
        格式化API错误信息
        :param api_name: API名称
        :param response: API响应
        :param url: 请求URL
        :return: 格式化的错误信息
        """
        code = response.get("code", "未知")
        msg = response.get("msg", response.get("message", "未知错误"))
        data = response.get("data")
        
        error_parts = [f"{api_name} 调用失败"]
        if url:
            error_parts.append(f"URL: {url}")
        error_parts.append(f"错误码: {code}")
        error_parts.append(f"错误信息: {msg}")
        
        if data:
            error_parts.append(f"响应数据: {data}")
        
        return " | ".join(error_parts)
    
    @staticmethod
    def format_database_error(operation: str, error: Exception) -> str:
        """
        格式化数据库错误信息
        :param operation: 数据库操作
        :param error: 数据库异常
        :return: 格式化的错误信息
        """
        error_msg = str(error)
        if "Can't connect to MySQL server" in error_msg:
            return f"数据库连接失败: {operation} - MySQL服务器连接异常，请检查数据库服务是否启动"
        elif "Access denied" in error_msg:
            return f"数据库权限错误: {operation} - 用户名或密码错误"
        elif "Unknown database" in error_msg:
            return f"数据库不存在: {operation} - 指定的数据库不存在"
        elif "Table doesn't exist" in error_msg:
            return f"表不存在: {operation} - 指定的数据表不存在"
        else:
            return f"数据库操作失败: {operation} - {error_msg}"
    
    @staticmethod
    def format_network_error(operation: str, error: Exception) -> str:
        """
        格式化网络错误信息
        :param operation: 操作名称
        :param error: 网络异常
        :return: 格式化的错误信息
        """
        error_msg = str(error)
        if "Connection refused" in error_msg:
            return f"网络连接失败: {operation} - 服务器拒绝连接，请检查网络和服务状态"
        elif "timeout" in error_msg.lower():
            return f"网络超时: {operation} - 请求超时，请检查网络连接"
        elif "SSL" in error_msg:
            return f"SSL证书错误: {operation} - 证书验证失败"
        else:
            return f"网络错误: {operation} - {error_msg}"
    
    @staticmethod
    def format_validation_error(field: str, value: Any, expected: str) -> str:
        """
        格式化验证错误信息
        :param field: 字段名
        :param value: 字段值
        :param expected: 期望格式
        :return: 格式化的错误信息
        """
        return f"参数验证失败: {field} = '{value}' 不符合 {expected} 格式要求"
    
    @staticmethod
    def format_business_error(step: str, reason: str, details: str = "") -> str:
        """
        格式化业务错误信息
        :param step: 业务步骤
        :param reason: 错误原因
        :param details: 详细信息
        :return: 格式化的错误信息
        """
        error_msg = f"业务处理失败: {step} - {reason}"
        if details:
            error_msg += f" | 详情: {details}"
        return error_msg 