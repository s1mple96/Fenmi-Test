# -*- coding: utf-8 -*-
"""
业务逻辑服务 - 统一管理ETC申办的业务规则和逻辑
"""
from typing import Dict, Any, Optional
from datetime import datetime


class BusinessService:
    """业务逻辑服务"""
    
    @staticmethod
    def validate_car_num(car_num: str) -> bool:
        """
        验证车牌号格式
        :param car_num: 车牌号
        :return: 是否有效
        """
        if not car_num:
            return False
        
        # 基本格式验证：省份简称 + 字母 + 数字
        if len(car_num) < 6:
            return False
        
        # 检查省份简称
        province_abbr = car_num[0]
        valid_provinces = ['京', '津', '冀', '晋', '蒙', '辽', '吉', '黑', '沪', '苏', '浙', '皖', '闽', '赣', '鲁', '豫', '鄂', '湘', '粤', '桂', '琼', '渝', '川', '贵', '云', '藏', '陕', '甘', '青', '宁', '新']
        if province_abbr not in valid_provinces:
            return False
        
        return True
    
    @staticmethod
    def validate_id_code(id_code: str) -> bool:
        """
        验证身份证号格式
        :param id_code: 身份证号
        :return: 是否有效
        """
        if not id_code:
            return False
        
        # 基本格式验证：18位数字或17位数字+X
        if len(id_code) != 18:
            return False
        
        # 检查前17位是否为数字
        if not id_code[:17].isdigit():
            return False
        
        # 检查最后一位是否为数字或X
        if not (id_code[-1].isdigit() or id_code[-1].upper() == 'X'):
            return False
        
        return True
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        验证手机号格式
        :param phone: 手机号
        :return: 是否有效
        """
        if not phone:
            return False
        
        # 基本格式验证：11位数字，以1开头
        if len(phone) != 11 or not phone.isdigit() or not phone.startswith('1'):
            return False
        
        return True
    
    @staticmethod
    def validate_bank_card(bank_card: str) -> bool:
        """
        验证银行卡号格式
        :param bank_card: 银行卡号
        :return: 是否有效
        """
        if not bank_card:
            return False
        
        # 基本格式验证：13-19位数字
        if not bank_card.isdigit() or len(bank_card) < 13 or len(bank_card) > 19:
            return False
        
        return True
    
    @staticmethod
    def generate_verify_code() -> str:
        """
        生成验证码（日期格式：YYMMDD）
        :return: 验证码
        """
        return datetime.now().strftime("%y%m%d")
    
    @staticmethod
    def build_car_num(province: str, letter: str, number: str) -> str:
        """
        构建完整车牌号
        :param province: 省份简称
        :param letter: 字母
        :param number: 数字
        :return: 完整车牌号
        """
        return f"{province}{letter}{number}"
    
    @staticmethod
    def extract_car_num_parts(car_num: str) -> Dict[str, str]:
        """
        解析车牌号各部分
        :param car_num: 完整车牌号
        :return: 车牌号各部分
        """
        if not car_num or len(car_num) < 6:
            return {}
        
        return {
            'province': car_num[0],
            'letter': car_num[1] if len(car_num) > 1 else '',
            'number': car_num[2:] if len(car_num) > 2 else ''
        }
    
    @staticmethod
    def get_vehicle_color_code(color_name: str) -> int:
        """
        获取车辆颜色代码
        :param color_name: 颜色名称
        :return: 颜色代码
        """
        color_map = {
            "蓝色": 0,
            "黄色": 1,
            "绿色": 2,
            "白色": 3,
            "黑色": 4
        }
        return color_map.get(color_name, 0)
    
    @staticmethod
    def validate_product_info(product: Dict[str, Any]) -> bool:
        """
        验证产品信息
        :param product: 产品信息
        :return: 是否有效
        """
        required_fields = ['product_id', 'product_name', 'operator_code']
        return all(field in product for field in required_fields)
    
    @staticmethod
    def format_order_info(order_id: str, sign_order_id: str, verify_code_no: str) -> Dict[str, str]:
        """
        格式化订单信息
        :param order_id: 订单ID
        :param sign_order_id: 签约订单ID
        :param verify_code_no: 验证码编号
        :return: 格式化的订单信息
        """
        return {
            'order_id': order_id,
            'sign_order_id': sign_order_id,
            'verify_code_no': verify_code_no
        }
    
    @staticmethod
    def should_continue_on_error(step_number: int) -> bool:
        """
        判断某步骤失败时是否应该继续执行后续步骤
        :param step_number: 步骤编号
        :return: 是否继续
        """
        # 某些步骤失败时允许继续执行后续步骤
        continue_on_error_steps = [9]  # 保存车辆信息失败时继续
        return step_number in continue_on_error_steps
    
    @staticmethod
    def is_critical_step(step_number: int) -> bool:
        """
        判断是否为关键步骤
        :param step_number: 步骤编号
        :return: 是否为关键步骤
        """
        # 定义关键步骤，这些步骤失败会导致整个流程失败
        critical_steps = [1, 2, 5, 6, 7, 8, 10, 11, 12, 13, 14]
        return step_number in critical_steps
    
    @staticmethod
    def get_step_retry_count(step_number: int) -> int:
        """
        获取步骤重试次数
        :param step_number: 步骤编号
        :return: 重试次数
        """
        # 定义不同步骤的重试次数
        retry_config = {
            1: 1,  # 校验车牌
            2: 1,  # 校验是否可申办
            5: 2,  # 提交车牌
            7: 2,  # 提交身份和银行卡信息
            8: 3,  # 签约校验
            11: 2,  # 代扣支付
        }
        return retry_config.get(step_number, 1)
    
    @staticmethod
    def validate_required_params(params: Dict[str, Any]) -> None:
        """
        验证必需的业务参数
        :param params: 参数字典
        :raises: ValueError 当缺少必需参数时
        """
        from apps.etc_apply.services.error_service import ErrorService
        
        required_fields = ['carNum', 'cardHolder', 'idCode', 'bindBankPhone', 'bindBankNo']
        missing_fields = [field for field in required_fields if not params.get(field)]
        
        if missing_fields:
            raise ValueError(f"缺少必需参数: {', '.join(missing_fields)}")
        
        # 验证车牌号格式
        car_num = params.get('carNum', '')
        if not BusinessService.validate_car_num(car_num):
            raise ValueError(ErrorService.format_validation_error('carNum', car_num, '省份简称+字母+数字'))
        
        # 验证身份证号格式
        id_code = params.get('idCode', '')
        if not BusinessService.validate_id_code(id_code):
            raise ValueError(ErrorService.format_validation_error('idCode', id_code, '18位身份证号'))
        
        # 验证手机号格式
        phone = params.get('bindBankPhone', '')
        if not BusinessService.validate_phone(phone):
            raise ValueError(ErrorService.format_validation_error('bindBankPhone', phone, '11位手机号'))
        
        # 验证银行卡号格式
        bank_card = params.get('bindBankNo', '')
        if not BusinessService.validate_bank_card(bank_card):
            raise ValueError(ErrorService.format_validation_error('bindBankNo', bank_card, '13-19位银行卡号')) 