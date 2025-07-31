# -*- coding: utf-8 -*-
"""
状态管理服务 - 统一管理ETC申办流程的状态和进度
"""
from typing import Dict, Any, Optional, Callable
from enum import Enum


class StepStatus(Enum):
    """步骤状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class FlowState:
    """流程状态管理"""
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        self.progress_callback = progress_callback
        self.current_step = 0
        self.total_steps = 15
        self.step_status = {}
        self.order_id = None
        self.sign_order_id = None
        self.verify_code_no = None
        self.params = {}
        
    def update_progress(self, step_number: int, message: str, status: StepStatus = StepStatus.SUCCESS):
        """
        更新进度
        :param step_number: 步骤编号
        :param message: 消息
        :param status: 状态
        """
        self.current_step = step_number
        self.step_status[step_number] = status
        
        if self.progress_callback:
            percent = int((step_number / self.total_steps) * 100)
            self.progress_callback(percent, message)
    
    def set_order_info(self, order_id: str, sign_order_id: str, verify_code_no: str):
        """
        设置订单信息
        :param order_id: 订单ID
        :param sign_order_id: 签约订单ID
        :param verify_code_no: 验证码编号
        """
        self.order_id = order_id
        self.sign_order_id = sign_order_id
        self.verify_code_no = verify_code_no
    
    def get_order_info(self) -> Dict[str, str]:
        """
        获取订单信息
        :return: 订单信息字典
        """
        return {
            'order_id': self.order_id,
            'sign_order_id': self.sign_order_id,
            'verify_code_no': self.verify_code_no
        }
    
    def set_params(self, params: Dict[str, Any]):
        """
        设置参数
        :param params: 参数字典
        """
        self.params = params
    
    def get_params(self) -> Dict[str, Any]:
        """
        获取参数
        :return: 参数字典
        """
        return self.params
    
    def is_step_completed(self, step_number: int) -> bool:
        """
        检查步骤是否完成
        :param step_number: 步骤编号
        :return: 是否完成
        """
        return self.step_status.get(step_number) == StepStatus.SUCCESS
    
    def get_completed_steps(self) -> list:
        """
        获取已完成的步骤
        :return: 已完成的步骤列表
        """
        return [step for step, status in self.step_status.items() if status == StepStatus.SUCCESS]
    
    def reset(self):
        """重置状态"""
        self.current_step = 0
        self.step_status = {}
        self.order_id = None
        self.sign_order_id = None
        self.verify_code_no = None
        self.params = {}


class StepManager:
    """步骤管理器"""
    
    STEP_DEFINITIONS = {
        1: {"name": "校验车牌", "weight": 5},
        2: {"name": "校验是否可申办", "weight": 5},
        3: {"name": "获取渠道地址", "weight": 5},
        4: {"name": "获取可选服务", "weight": 5},
        5: {"name": "提交车牌", "weight": 10},
        6: {"name": "协议签署", "weight": 10},
        7: {"name": "提交身份和银行卡信息", "weight": 10},
        8: {"name": "签约校验", "weight": 10},
        9: {"name": "保存车辆信息", "weight": 10},
        10: {"name": "可选服务更新", "weight": 5},
        11: {"name": "代扣支付", "weight": 5},
        12: {"name": "数据库状态修改", "weight": 5},
        13: {"name": "一键入库流程", "weight": 10},
        14: {"name": "ETC卡用户OBU信息入库", "weight": 5},
        15: {"name": "最终状态更新", "weight": 5},
        16: {"name": "流程完成", "weight": 5}
    }
    
    @staticmethod
    def get_step_name(step_number: int) -> str:
        """
        获取步骤名称
        :param step_number: 步骤编号
        :return: 步骤名称
        """
        return StepManager.STEP_DEFINITIONS.get(step_number, {}).get("name", f"步骤{step_number}")
    
    @staticmethod
    def get_step_weight(step_number: int) -> int:
        """
        获取步骤权重
        :param step_number: 步骤编号
        :return: 步骤权重
        """
        return StepManager.STEP_DEFINITIONS.get(step_number, {}).get("weight", 5)
    
    @staticmethod
    def calculate_progress(completed_steps: list) -> int:
        """
        计算进度百分比
        :param completed_steps: 已完成的步骤列表
        :return: 进度百分比
        """
        if not completed_steps:
            return 0
        
        total_weight = sum(StepManager.get_step_weight(step) for step in range(1, 17))
        completed_weight = sum(StepManager.get_step_weight(step) for step in completed_steps)
        
        return int((completed_weight / total_weight) * 100)
    
    @staticmethod
    def format_step_message(step_number: int, action: str = "完成") -> str:
        """
        格式化步骤消息
        :param step_number: 步骤编号
        :param action: 动作
        :return: 格式化的消息
        """
        step_name = StepManager.get_step_name(step_number)
        return f"{step_number}. {step_name}{action}" 