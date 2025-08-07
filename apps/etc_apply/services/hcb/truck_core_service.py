# -*- coding: utf-8 -*-
"""
货车核心服务 - 提供配置和工具函数
"""
import json
from typing import Dict, Any
from apps.etc_apply.services.rtx.core_service import CoreService


class TruckCoreService:
    """货车核心服务"""
    
    @staticmethod
    def get_hcb_mysql_config() -> Dict[str, Any]:
        """获取货车数据库配置"""
        try:
            # 使用CoreService的HCB数据库配置方法
            return CoreService.get_hcb_mysql_config()
        except Exception as e:
            raise Exception(f"获取货车MySQL配置失败: {str(e)}")
    
    @staticmethod
    def format_database_error(operation: str, error: Exception) -> str:
        """格式化数据库错误信息"""
        return f"数据库操作失败 - {operation}: {str(error)}"
    
    @staticmethod
    def get_business_config() -> Dict[str, Any]:
        """获取业务配置"""
        return CoreService.get_business_config() 