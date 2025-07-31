# -*- coding: utf-8 -*-
"""
参数校验与补全模块
"""
from .business_service import BusinessService


def validate_and_complete_params(params):
    """
    校验并补全ETC申办参数
    :param params: dict 用户输入参数
    :return: dict 校验和补全后的参数
    :raises: ValueError
    """
    # 使用业务逻辑服务进行验证
    BusinessService.validate_required_params(params)
    
    # 车牌颜色映射
    vc = params.get('vehicleColor', '0')
    if isinstance(vc, str) and vc in ["蓝色", "黄色", "绿色", "白色", "黑色"]:
        params['vehicleColor'] = BusinessService.get_vehicle_color_code(vc)
    else:
        try:
            params['vehicleColor'] = int(vc)
        except Exception:
            params['vehicleColor'] = 0
    
    # 其它参数补全可在此扩展...
    return params 