# -*- coding: utf-8 -*-
"""
API蓝图模块
"""
from flask import Blueprint
from .etc_api import etc_bp
from .truck_api import truck_bp
from .common_api import common_bp

def create_api_blueprint():
    """创建API蓝图"""
    api_bp = Blueprint('api', __name__)
    
    # 注册子蓝图
    api_bp.register_blueprint(etc_bp, url_prefix='/etc')
    api_bp.register_blueprint(truck_bp, url_prefix='/truck') 
    api_bp.register_blueprint(common_bp, url_prefix='/common')
    
    return api_bp 