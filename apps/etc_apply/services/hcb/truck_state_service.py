# -*- coding: utf-8 -*-
"""
货车ETC申办状态管理服务
"""
from typing import Dict, Any, Optional, Callable
from enum import Enum
from apps.etc_apply.services.rtx.core_service import CoreService


class TruckStepStatus(Enum):
    """货车流程步骤状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class TruckFlowState:
    """货车流程状态管理"""
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        self.progress_callback = progress_callback
        self.current_step = 0
        self.total_steps = 21  # 货车流程总步数（修复：原来是11，应该是21）
        self.step_status = {}
        self.truck_etc_apply_id = None
        self.truck_user_id = None
        self.truck_user_wallet_id = None
        self.params = {}
        
    def update_progress(self, step_number: int, message: str, status: TruckStepStatus = TruckStepStatus.SUCCESS):
        """更新进度"""
        self.current_step = step_number
        self.step_status[step_number] = status
        
        if self.progress_callback:
            percent = int((step_number / self.total_steps) * 100)
            self.progress_callback(percent, message)
    
    def set_truck_info(self, truck_etc_apply_id: str, truck_user_id: str = None, truck_user_wallet_id: str = None):
        """设置货车申办信息"""
        self.truck_etc_apply_id = truck_etc_apply_id
        if truck_user_id:
            self.truck_user_id = truck_user_id
        if truck_user_wallet_id:
            self.truck_user_wallet_id = truck_user_wallet_id
    
    def get_truck_info(self) -> Dict[str, str]:
        """获取货车申办信息"""
        return {
            'truck_etc_apply_id': self.truck_etc_apply_id,
            'truck_user_id': self.truck_user_id,
            'truck_user_wallet_id': self.truck_user_wallet_id
        }
    
    def set_params(self, params: Dict[str, Any]):
        """设置参数"""
        self.params = params
    
    def get_params(self) -> Dict[str, Any]:
        """获取参数"""
        return self.params
    
    def is_step_completed(self, step_number: int) -> bool:
        """检查步骤是否完成"""
        return self.step_status.get(step_number) == TruckStepStatus.SUCCESS
    
    def get_completed_steps(self) -> list:
        """获取已完成的步骤"""
        return [step for step, status in self.step_status.items() if status == TruckStepStatus.SUCCESS]
    
    def reset(self):
        """重置状态"""
        self.current_step = 0
        self.step_status = {}
        self.truck_etc_apply_id = None
        self.truck_user_id = None
        self.truck_user_wallet_id = None
        self.params = {}


class TruckStepManager:
    """货车流程步骤管理器"""
    
    STEP_DEFINITIONS = {
        1: {"name": "更新微信消息模板", "weight": 5},
        2: {"name": "获取运营商列表", "weight": 5},
        3: {"name": "获取产品列表", "weight": 5},
        4: {"name": "获取银行列表", "weight": 5},
        5: {"name": "获取产品信息", "weight": 5},
        6: {"name": "获取顶级渠道", "weight": 5},
        7: {"name": "获取货车产品绿通卡标识", "weight": 5},
        8: {"name": "获取验证码", "weight": 5},
        9: {"name": "校验手机号", "weight": 5},
        10: {"name": "提交申请信息", "weight": 5},
        11: {"name": "提交申请银行信息", "weight": 5},
        12: {"name": "交通违章查询", "weight": 5},
        13: {"name": "提交车辆信息", "weight": 5},
        14: {"name": "提交申请渠道信息", "weight": 5},
        15: {"name": "提交申请产品信息", "weight": 5},
        16: {"name": "提交申请运营商信息", "weight": 5},
        17: {"name": "提交申请银行绑定信息", "weight": 5},
        18: {"name": "提交申请银行验证信息", "weight": 5},
        19: {"name": "提交申请银行验证结果", "weight": 5},
        20: {"name": "提交OBU订单", "weight": 5},
        21: {"name": "流程完成", "weight": 5}
    }
    
    @classmethod
    def get_step_name(cls, step_number: int) -> str:
        """获取步骤名称"""
        step_def = cls.STEP_DEFINITIONS.get(step_number, {})
        return step_def.get("name", f"步骤{step_number}")
    
    @classmethod
    def get_step_weight(cls, step_number: int) -> int:
        """获取步骤权重"""
        step_def = cls.STEP_DEFINITIONS.get(step_number, {})
        return step_def.get("weight", 1)
    
    @classmethod
    def format_step_message(cls, step_number: int, step_name: str, action: str = "") -> str:
        """格式化步骤消息"""
        return f"{step_number}.{step_name}{action}"
    
    @classmethod
    def calculate_progress(cls, current_step: int) -> float:
        """计算进度百分比"""
        total_weight = sum(cls.get_step_weight(i) for i in range(1, 22))  # 21个步骤
        current_weight = sum(cls.get_step_weight(i) for i in range(1, current_step + 1))
        return (current_weight / total_weight) * 100 if total_weight > 0 else 0
    
    @staticmethod
    def get_critical_steps() -> list:
        """获取关键步骤"""
        return [5, 6, 8, 10]  # 提交申办信息、提交车辆信息、签发协议、支付
    
    @staticmethod
    def is_critical_step(step_number: int) -> bool:
        """判断是否为关键步骤"""
        return step_number in TruckStepManager.get_critical_steps()
    
    @staticmethod
    def get_step_retry_count(step_number: int) -> int:
        """获取步骤重试次数"""
        # 从配置文件读取重试配置
        steps_config = CoreService.get_steps_config()
        retry_config = steps_config.get('retry_config', {})
        return retry_config.get(str(step_number), 1) 