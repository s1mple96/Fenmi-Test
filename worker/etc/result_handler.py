# -*- coding: utf-8 -*-
"""
结果处理与回调模块
"""

def handle_result(result, ui=None):
    """
    处理ETC申办流程结果
    :param result: 结果数据
    :param ui: 可选，UI对象用于信号/弹窗等
    """
    if ui:
        if hasattr(ui, 'log_signal'):
            ui.log_signal.emit(str(result))
    # 其它处理可扩展... 