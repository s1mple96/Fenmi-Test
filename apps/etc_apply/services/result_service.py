# -*- coding: utf-8 -*-
"""
结果处理与回调模块
"""
from common.mysql_util import MySQLUtil
from apps.etc_apply.services.config_service import ConfigService  # 新增导入


def get_mysql_config():
    """获取MySQL连接配置"""
    config = ConfigService.get_mysql_config()  # 使用配置服务
    config['database'] = 'rtx'  # 保持原有的数据库名
    return config


def close_mock_data():
    """关闭Mock数据配置"""
    try:
        mysql_conf = get_mysql_config()
        if not mysql_conf:
            print("未找到MySQL连接配置，无法关闭Mock数据")
            return False
        
        db = MySQLUtil(**mysql_conf)
        db.connect()
        sql = "UPDATE rtx.sys_config t SET t.config_value = '0' WHERE t.config_id = 55"
        db.execute(sql)
        db.close()
        print("Mock数据已关闭")
        return True
    except Exception as e:
        print(f"关闭Mock数据失败: {str(e)}")
        return False


def handle_result(result, ui=None):
    """
    处理ETC申办流程结果
    :param result: 结果数据
    :param ui: 可选，UI对象用于信号/弹窗等
    """
    # 流程完成后关闭Mock数据
    close_mock_data()
    
    if ui:
        if hasattr(ui, 'log_signal'):
            ui.log_signal.emit(str(result))
    # 其它处理可扩展... 