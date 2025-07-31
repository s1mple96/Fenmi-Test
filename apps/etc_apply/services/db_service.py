from common.mysql_util import MySQLUtil
import random
from datetime import datetime
import uuid
from apps.etc_apply.services.config_service import ConfigService
from apps.etc_apply.services.error_service import ErrorService


def get_mysql_config(database='rtx'):
    """
    获取MySQL连接配置
    :param database: 数据库名称，支持 'rtx' 或 'hcb'
    :return: 数据库配置
    """
    config = ConfigService.get_mysql_config()
    config['database'] = database
    return config


class OrderDbService:
    """订单数据库服务"""
    
    @staticmethod
    def update_order_status(order_id):
        """更新订单状态"""
        try:
            conf = get_mysql_config('rtx')
            db = MySQLUtil(**conf)
            db.connect()
            sql = "UPDATE rtx_etcapply_order t SET t.order_status = '7' WHERE t.order_id = %s"
            db.execute(sql, (order_id,))
            db.close()
        except Exception as e:
            error_msg = ErrorService.format_database_error("更新订单状态", e)
            raise Exception(error_msg)


class CardUserDbService:
    """卡用户数据库服务"""
    
    @staticmethod
    def update_card_user_status(car_num):
        """更新卡用户状态"""
        try:
            conf = get_mysql_config('rtx')
            db = MySQLUtil(**conf)
            db.connect()
            sql = """
            UPDATE rtx_etc_card_user t 
            SET t.status = '3', t.update_time = NOW() 
            WHERE t.car_num = %s
            """
            db.execute(sql, (car_num,))
            db.close()
        except Exception as e:
            error_msg = ErrorService.format_database_error("更新卡用户状态", e)
            raise Exception(error_msg)
    
    @staticmethod
    def update_card_user_obu_info(car_num, obu_no, etc_sn, activation_time):
        """更新卡用户OBU信息"""
        try:
            conf = get_mysql_config('rtx')
            db = MySQLUtil(**conf)
            db.connect()
            sql = """
            UPDATE rtx_etc_card_user t 
            SET t.obu_no = %s, t.etc_sn = %s, t.activation_time = %s, t.update_time = NOW() 
            WHERE t.car_num = %s
            """
            db.execute(sql, (obu_no, etc_sn, activation_time, car_num))
            db.close()
        except Exception as e:
            error_msg = ErrorService.format_database_error("更新卡用户OBU信息", e)
            raise Exception(error_msg)


def update_final_card_user_status(car_num):
    try:
        conf = get_mysql_config('rtx')  # 使用rtx数据库
        db = MySQLUtil(**conf)
        db.connect()
        # 更新最终状态
        sql = """
        UPDATE rtx_etc_card_user t 
        SET t.active_status = 2007, t.status = '1', t.update_time = NOW() 
        WHERE t.car_num = %s
        """
        db.execute(sql, (car_num,))
        db.close()
    except Exception as e:
        error_msg = ErrorService.format_database_error("更新最终卡用户状态", e)
        raise Exception(error_msg)


def insert_device_stock(car_num: str) -> dict:
    """
    插入设备库存数据
    :param car_num: 车牌号，格式如 "苏Z9T4P0"
    :return: 包含设备号信息的字典
    """
    # 车牌简称到省份全名映射
    PLATE_PREFIX_TO_PROVINCE = {
        "苏": "江苏", "湘": "湖南", "桂": "广西", "黑": "黑龙江",
        "蒙": "内蒙古", "皖": "安徽", "川": "四川",
    }
    
    # 省份与设备号前缀映射（纯数字）
    PROVINCE_CODE_MAP = {
        "江苏": "3201", "湖南": "4301", "广西": "4501", "黑龙江": "2301",
        "内蒙古": "1501", "安徽": "3401", "四川": "5101",
    }
    
    def generate_device_no(province, device_type):
        code = PROVINCE_CODE_MAP.get(province, "9999")
        length = 16 if device_type == "0" else 20
        remain = length - len(code)
        suffix = ''.join(random.choices("0123456789", k=remain))
        return code + suffix
    
    # 解析车牌号获取省份
    province_abbr = car_num[0] if car_num else "苏"
    province_name = PLATE_PREFIX_TO_PROVINCE.get(province_abbr, "江苏")
    
    # 生成设备号
    obn_no = generate_device_no(province_name, "0")
    etc_no = generate_device_no(province_name, "1")
    
    # 准备数据
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    base_data = {
        "CARD_OPERATORS": "1",
        "STATUS": "1",
        "CAR_NUM": car_num,
        "STOCK_STATUS": "0",
        "SOURCE": "1",
        "REMARK": "激活设备不存在库存内",
        "CREATE_TIME": now,
        "DEVICE_CATEGORY": "0"
    }
    
    obn_data = base_data.copy()
    obn_data.update({
        "NEWSTOCK_ID": uuid.uuid4().hex,
        "INTERNAL_DEVICE_NO": obn_no,
        "EXTERNAL_DEVICE_NO": obn_no,
        "TYPE": "0"
    })
    
    etc_data = base_data.copy()
    etc_data.update({
        "NEWSTOCK_ID": uuid.uuid4().hex,
        "INTERNAL_DEVICE_NO": etc_no,
        "EXTERNAL_DEVICE_NO": etc_no,
        "TYPE": "1"
    })
    
    # 插入数据库
    mysql_conf = get_mysql_config('hcb')  # 使用hcb数据库
    db = MySQLUtil(**mysql_conf)
    db.connect()
    
    def insert_row(row):
        keys = ','.join(f'`{k}`' for k in row.keys())
        vals = ','.join(['%s'] * len(row))
        sql = f"INSERT INTO hcb_newstock ({keys}) VALUES ({vals})"
        db.execute(sql, tuple(row.values()))
    
    insert_row(obn_data)
    insert_row(etc_data)
    db.close()
    
    return {
        'car_num': car_num,
        'obn_no': obn_no,
        'etc_no': etc_no
    }


def run_stock_in_flow(config, dbname, table, fields, types, rules, count, extras=None, progress_callback=None):
    """
    一键入库流程
    """
    import uuid
    import random
    from datetime import datetime
    
    config = config.copy()
    config['database'] = dbname
    db = MySQLUtil(**config)
    db.connect()
    
    def gen_value(rule, field, ftype, extra=None):
        if rule == 'uuid':
            return uuid.uuid4().hex
        elif rule == 'random_device':
            # 生成随机设备号
            return ''.join(random.choices('0123456789', k=16))
        elif rule == 'now':
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        elif rule == 'fixed' and extra:
            return extra
        elif rule == '1':
            return '1'
        elif rule == '0':
            return '0'
        elif rule == 'str' and extra:
            return str(extra)
        else:
            return ''
    
    for i in range(count):
        data = {}
        for j, field in enumerate(fields):
            rule = rules[j] if j < len(rules) else 'fixed'
            extra = None
            if isinstance(extras, dict):
                extra = extras.get(field)
            elif isinstance(extras, list) and j < len(extras):
                extra = extras[j]
            data[field] = gen_value(rule, field, types[j], extra)
        
        # 插入数据
        keys = ','.join(f'`{k}`' for k in data.keys())
        vals = ','.join(['%s'] * len(data))
        sql = f"INSERT INTO {table} ({keys}) VALUES ({vals})"
        db.execute(sql, tuple(data.values()))
        
        if progress_callback:
            progress_callback(int((i + 1) / count * 100), f"插入第{i+1}条数据")
    
    db.close() 