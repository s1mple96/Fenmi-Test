# -*- coding: utf-8 -*-
"""
参数校验与补全模块
"""

def validate_and_complete_params(params):
    """
    校验并补全ETC申办参数
    :param params: dict 用户输入参数
    :return: dict 校验和补全后的参数
    :raises: ValueError
    """
    required = ['carNum', 'cardHolder', 'idCode', 'bindBankNo', 'bindBankPhone']
    for key in required:
        if not params.get(key):
            raise ValueError(f"{key}为必填项")
    # 车牌颜色映射
    color_map = {"蓝色": 0, "黄色": 1, "绿色": 2, "白色": 3, "黑色": 4}
    vc = params.get('vehicleColor', '0')
    if isinstance(vc, str) and vc in color_map:
        params['vehicleColor'] = color_map[vc]
    else:
        try:
            params['vehicleColor'] = int(vc)
        except Exception:
            params['vehicleColor'] = 0
    # 其它参数补全可在此扩展...
    return params 