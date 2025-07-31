# -*- coding: utf-8 -*-
"""
核心服务 - 整合配置、验证、错误处理等基础功能
"""
import json
import os
import re
import traceback
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime


class CoreService:
    """核心服务 - 整合基础功能"""
    
    # ==================== 配置管理 ====================
    
    _config_cache = None
    _etc_config_cache = None
    
    @staticmethod
    def _load_config() -> Dict[str, Any]:
        """加载主配置文件"""
        if CoreService._config_cache is None:
            config_path = CoreService.get_config_path('app_config.json')
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    CoreService._config_cache = json.load(f)
            except Exception as e:
                print(f"读取配置文件失败: {e}")
                CoreService._config_cache = {}
        return CoreService._config_cache
    
    @staticmethod
    def _load_etc_config() -> Dict[str, Any]:
        """加载ETC配置文件"""
        if CoreService._etc_config_cache is None:
            config_path = CoreService.get_config_path('etc_config.json')
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    CoreService._etc_config_cache = json.load(f)
            except Exception as e:
                print(f"读取ETC配置文件失败: {e}")
                CoreService._etc_config_cache = {}
        return CoreService._etc_config_cache
    
    @staticmethod
    def get_config_path(filename: str) -> str:
        """获取配置文件路径"""
        # 优先从 apps/etc_apply/config 目录加载
        etc_config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        etc_config_path = os.path.join(etc_config_dir, filename)
        
        if os.path.exists(etc_config_path):
            return etc_config_path
        
        # 如果不存在，则从项目根目录的 config 目录加载（向后兼容）
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        return os.path.join(base_dir, 'config', filename)
    
    @staticmethod
    def get_api_base_url() -> str:
        """获取API基础URL"""
        config = CoreService._load_etc_config()
        return config.get('api', {}).get('base_url', 'http://788360p9o5.yicp.fun')
    
    @staticmethod
    def get_browser_cookies() -> dict:
        """获取浏览器cookies"""
        config = CoreService._load_etc_config()
        return config.get('browser_cookies', {})
    
    @staticmethod
    def get_mysql_config(database: str = 'hcb') -> Dict[str, Any]:
        """获取MySQL连接配置"""
        config = CoreService._load_etc_config()
        db_config = config.get('database', {}).get(database, {})
        mysql_config = {
            'host': db_config.get('host', 'localhost'),
            'port': db_config.get('port', 3306),
            'user': db_config.get('username', 'root'),
            'password': db_config.get('password', 'password'),
            'database': database,
        }
        return mysql_config
    
    @staticmethod
    def get_rtx_mysql_config() -> Dict[str, Any]:
        """获取RTX数据库配置"""
        return CoreService.get_mysql_config('rtx')
    
    @staticmethod
    def get_hcb_mysql_config() -> Dict[str, Any]:
        """获取HCB数据库配置"""
        return CoreService.get_mysql_config('hcb')
    
    @staticmethod
    def get_business_config() -> Dict[str, Any]:
        """获取业务配置"""
        config = CoreService._load_etc_config()
        return config.get('business', {})
    
    @staticmethod
    def get_ui_config() -> Dict[str, Any]:
        """获取UI配置"""
        config = CoreService._load_etc_config()
        return config.get('ui', {})
    
    @staticmethod
    def get_validation_config() -> Dict[str, Any]:
        """获取验证配置"""
        config = CoreService._load_etc_config()
        return config.get('validation', {})
    
    @staticmethod
    def get_device_config() -> Dict[str, Any]:
        """获取设备配置"""
        config = CoreService._load_etc_config()
        return config.get('device', {})
    
    @staticmethod
    def get_vehicle_colors() -> Dict[str, int]:
        """获取车辆颜色映射"""
        config = CoreService._load_etc_config()
        return config.get('vehicle_colors', {})
    
    @staticmethod
    def get_default_params() -> Dict[str, Any]:
        """获取默认参数"""
        config = CoreService._load_etc_config()
        default_params = config.get('default_params', {})
        return default_params
    
    @staticmethod
    def get_steps_config() -> Dict[str, Any]:
        """获取步骤配置"""
        config = CoreService._load_etc_config()
        return config.get('steps', {})
    
    # ==================== 参数验证 ====================
    
    @staticmethod
    def validate_car_num(car_num: str) -> bool:
        """验证车牌号格式"""
        if not car_num or len(car_num) < 6:
            return False
        
        validation_config = CoreService.get_validation_config()
        pattern = validation_config.get('car_number_pattern', r'^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵青藏川宁琼粤港澳台][A-Z][A-Z0-9]{5}$')
        return bool(re.match(pattern, car_num))
    
    @staticmethod
    def validate_id_code(id_code: str) -> bool:
        """验证身份证号格式"""
        if not id_code or len(id_code) != 18:
            return False
        
        validation_config = CoreService.get_validation_config()
        pattern = validation_config.get('id_code_pattern', r'^\d{17}[\dXx]$')
        return bool(re.match(pattern, id_code))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """验证手机号格式"""
        if not phone or len(phone) != 11 or not phone.isdigit() or not phone.startswith('1'):
            return False
        
        validation_config = CoreService.get_validation_config()
        pattern = validation_config.get('phone_pattern', r'^1[3-9]\d{9}$')
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_bank_card(bank_card: str) -> bool:
        """验证银行卡号格式"""
        if not bank_card or not bank_card.isdigit() or len(bank_card) < 13 or len(bank_card) > 19:
            return False
        
        validation_config = CoreService.get_validation_config()
        pattern = validation_config.get('bank_card_pattern', r'^\d{13,19}$')
        return bool(re.match(pattern, bank_card))
    
    @staticmethod
    def validate_vin(vin: str) -> bool:
        """验证VIN码格式"""
        if not vin:
            return True  # VIN码可选
        
        validation_config = CoreService.get_validation_config()
        pattern = validation_config.get('vin_pattern', r'^[A-Z0-9]{17}$')
        return bool(re.match(pattern, vin))
    
    @staticmethod
    def validate_required_params(params: Dict[str, Any], required_fields: List[str]) -> None:
        """验证必需的业务参数"""
        missing_fields = [field for field in required_fields if not params.get(field)]
        if missing_fields:
            raise ValueError(f"缺少必需参数: {', '.join(missing_fields)}")
        
        # 验证各字段格式
        car_num = params.get('carNum', '')
        if car_num and not CoreService.validate_car_num(car_num):
            raise ValueError(f"车牌号格式错误: {car_num}")
        
        id_code = params.get('idCode', '')
        if id_code and not CoreService.validate_id_code(id_code):
            raise ValueError(f"身份证号格式错误: {id_code}")
        
        phone = params.get('bindBankPhone', '')
        if phone and not CoreService.validate_phone(phone):
            raise ValueError(f"手机号格式错误: {phone}")
        
        bank_card = params.get('bindBankNo', '')
        if bank_card and not CoreService.validate_bank_card(bank_card):
            raise ValueError(f"银行卡号格式错误: {bank_card}")
    
    @staticmethod
    def build_car_num(province: str, letter: str, number: str) -> str:
        """构建完整车牌号"""
        return f"{province}{letter}{number}"
    
    @staticmethod
    def get_vehicle_color_code(color_name: str) -> int:
        """获取车辆颜色代码"""
        vehicle_colors = CoreService.get_vehicle_colors()
        return vehicle_colors.get(color_name, 0)
    
    # ==================== 错误处理 ====================
    
    @staticmethod
    def assert_api_success(resp: Any, api_name: str = "接口") -> None:
        """断言API响应成功"""
        if isinstance(resp, str):
            try:
                resp = json.loads(resp)
            except Exception:
                raise Exception(f"{api_name} 响应不是有效的JSON: {resp}")
        
        if resp.get("code") != 200:
            msg = resp.get("msg") or resp.get("message") or str(resp)
            raise Exception(f"{api_name} 失败，原因: {msg}")
    
    @staticmethod
    def format_error_message(step_number: int, step_name: str, error: Exception) -> str:
        """格式化错误消息"""
        return f"{step_number}. {step_name}失败: {str(error)}"
    
    @staticmethod
    def safe_get_nested(data: Dict[str, Any], keys: list, default: Any = None) -> Any:
        """安全获取嵌套字典的值"""
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current
    
    @staticmethod
    def format_database_error(operation: str, error: Exception) -> str:
        """格式化数据库错误信息"""
        error_msg = str(error)
        if "Can't connect to MySQL server" in error_msg:
            return f"数据库连接失败: {operation} - MySQL服务器连接异常"
        elif "Access denied" in error_msg:
            return f"数据库权限错误: {operation} - 用户名或密码错误"
        elif "Unknown database" in error_msg:
            return f"数据库不存在: {operation} - 指定的数据库不存在"
        else:
            return f"数据库操作失败: {operation} - {error_msg}"
    
    @staticmethod
    def format_network_error(operation: str, error: Exception) -> str:
        """格式化网络错误信息"""
        error_msg = str(error)
        if "Connection refused" in error_msg:
            return f"网络连接失败: {operation} - 服务器拒绝连接"
        elif "timeout" in error_msg.lower():
            return f"网络超时: {operation} - 请求超时"
        else:
            return f"网络错误: {operation} - {error_msg}"
    
    @staticmethod
    def handle_exception_with_context(context: str, error: Exception) -> Exception:
        """处理异常并添加上下文信息"""
        error_msg = str(error)
        if "MySQL" in error_msg or "database" in error_msg.lower():
            return Exception(CoreService.format_database_error(context, error))
        elif "Connection" in error_msg or "timeout" in error_msg.lower():
            return Exception(CoreService.format_network_error(context, error))
        else:
            return Exception(f"{context}失败: {error_msg}")
    
    # ==================== 业务工具 ====================
    
    @staticmethod
    def generate_verify_code() -> str:
        """生成验证码（日期格式：YYMMDD）"""
        return datetime.now().strftime("%y%m%d")
    
    @staticmethod
    def should_continue_on_error(step_number: int) -> bool:
        """判断某步骤失败时是否应该继续执行后续步骤"""
        steps_config = CoreService.get_steps_config()
        continue_on_error_steps = steps_config.get('continue_on_error_steps', [9])
        return step_number in continue_on_error_steps
    
    @staticmethod
    def is_critical_step(step_number: int) -> bool:
        """判断是否为关键步骤"""
        steps_config = CoreService.get_steps_config()
        critical_steps = steps_config.get('critical_steps', [1, 2, 5, 6, 7, 8, 10, 11, 12, 13, 14])
        return step_number in critical_steps
    
    @staticmethod
    def get_step_retry_count(step_number: int) -> int:
        """获取步骤重试次数"""
        steps_config = CoreService.get_steps_config()
        retry_config = steps_config.get('retry_config', {})
        return retry_config.get(str(step_number), 1)
    
    @staticmethod
    def format_order_info(order_id: str, sign_order_id: str, verify_code_no: str) -> Dict[str, str]:
        """格式化订单信息"""
        return {
            'order_id': order_id,
            'sign_order_id': sign_order_id,
            'verify_code_no': verify_code_no
        }
    
    @staticmethod
    def clear_cache():
        """清除配置缓存"""
        CoreService._config_cache = None
        CoreService._etc_config_cache = None 