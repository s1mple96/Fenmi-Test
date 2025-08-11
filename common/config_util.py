# -*- coding: utf-8 -*-
"""
配置工具模块 - 支持桌面版和Web版配置
"""
import os
import json
from pathlib import Path

def get_project_root():
    """获取项目根目录"""
    current_file = Path(__file__).resolve()
    # 从common/config_util.py向上两级到项目根目录
    return current_file.parent.parent

def get_config(config_type='desktop'):
    """
    获取配置信息
    
    Args:
        config_type: 配置类型，'desktop' 或 'web'
    
    Returns:
        dict: 配置字典
    """
    project_root = get_project_root()
    
    if config_type == 'web':
        # Web版配置文件
        config_path = project_root / 'config' / 'web_config.json'
    else:
        # 桌面版配置文件
        config_path = project_root / 'apps' / 'etc_apply' / 'config' / 'etc_config.json'
        # 如果桌面版配置不存在，尝试使用通用配置
        if not config_path.exists():
            config_path = project_root / 'config' / 'app_config.json'
    
    try:
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            print(f"警告: 配置文件不存在 - {config_path}")
            return {}
    except Exception as e:
        print(f"读取配置文件失败: {e}")
        return {}

def get_web_config():
    """获取Web配置（快捷方法）"""
    return get_config('web')

def get_desktop_config():
    """获取桌面版配置（快捷方法）"""
    return get_config('desktop')

# 保持向后兼容性的默认函数
def get_config_default():
    """默认获取桌面版配置，保持向后兼容"""
    return get_desktop_config() 