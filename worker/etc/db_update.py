from PyQt5.QtCore import QThread
from utils.mysql_util import MySQLUtil
import random
from datetime import datetime, timedelta
import json, os

# 获取MySQL连接配置
def get_mysql_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'connections.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        configs = json.load(f)
    for c in configs:
        if c.get('type') == 'mysql':
            host, port = c['address'].split(':')
            return {
                'host': host,
                'port': int(port),
                'user': c['username'],
                'password': c['password'],
                'database': 'rtx',
            }
    raise Exception('未找到MySQL连接配置')

def update_order_status(order_id):
    conf = get_mysql_config()
    db = MySQLUtil(**conf)
    db.connect()
    sql = "UPDATE rtx.rtx_etcapply_order t SET t.order_status = '7' WHERE t.order_id = %s"
    db.execute(sql, (order_id,))
    db.close()

def update_card_user_status(car_num):
    conf = get_mysql_config()
    db = MySQLUtil(**conf)
    db.connect()
    # 先查id
    sql_sel = "SELECT id FROM rtx.rtx_etc_card_user WHERE car_num = %s ORDER BY id DESC LIMIT 1"
    rows = db.query(sql_sel, (car_num,))
    if rows:
        card_user_id = rows[0]['id']
        sql_upd = "UPDATE rtx.rtx_etc_card_user t SET t.status = '1' WHERE t.id = %s"
        db.execute(sql_upd, (card_user_id,))
    db.close()

def update_card_user_obu_info(car_num, obu_no, etc_sn, activation_time):
    conf = get_mysql_config()
    db = MySQLUtil(**conf)
    db.connect()
    print(f"[DEBUG] update_card_user_obu_info: car_num={car_num}, obu_no={obu_no}, etc_sn={etc_sn}, activation_time={activation_time}")
    sql = "UPDATE rtx.rtx_etc_card_user t SET t.obu_no = %s, t.etc_sn = %s, t.activation_time = %s, t.active_status = 3024, t.status = '1' WHERE t.car_num = %s"
    db.execute(sql, (obu_no, etc_sn, activation_time, car_num))
    print(f"[DEBUG] update_card_user_obu_info: 更新行数={db.cursor.rowcount}")
    db.close()

def run_stock_in_flow(config, dbname, table, fields, types, rules, count, extras=None, progress_callback=None):
    """
    一键入库主流程，支持规则驱动批量插入，支持进度回调
    """
    from utils.data_factory import DataFactory  # 只在这里import一次
    extras = extras or [None] * len(fields)
    config = config.copy()
    config['database'] = dbname
    db = MySQLUtil(**config)
    db.connect()
    total = count
    inserted = 0
    batch_size = 100
    def gen_value(rule, field, ftype, extra=None):
        if rule == '雪花ID':
            return DataFactory.random_snowflake_id()
        if rule == '随机姓名':
            return DataFactory.random_name()
        elif rule == '随机手机号':
            return DataFactory.random_phone()
        elif rule == '随机身份证':
            return DataFactory.random_id_number()
        elif rule == '随机车牌':
            return DataFactory.random_plate_number()['plate_number']
        elif rule == '随机ETC号':
            return DataFactory.random_etc_number()
        elif rule == '随机OBN号':
            return DataFactory.random_obn_number()
        elif rule == '随机设备号':
            return DataFactory.random_device_id() if hasattr(DataFactory, 'random_device_id') else 'D' + ''.join(random.choices('0123456789', k=15))
        elif rule == '随机订单号':
            return DataFactory.random_order_id() if hasattr(DataFactory, 'random_order_id') else 'O' + ''.join(random.choices('0123456789', k=15))
        elif rule == '随机银行卡号':
            return DataFactory.random_bank_card()
        elif rule == '随机银行地址':
            return DataFactory.random_bank_address() if hasattr(DataFactory, 'random_bank_address') else fake.address()
        elif rule == '固定值':
            return extra if extra is not None else 'test'
        elif rule == '枚举值':
            if extra:
                enums = [v.strip() for v in extra.split(',') if v.strip()]
                return random.choice(enums) if enums else '0'
            return '0'
        elif rule == '随机日期':
            fmt = extra if extra else 'YYYY-MM-DD'
            strftime_fmt = fmt.replace('YYYY', '%Y').replace('MM', '%m').replace('DD', '%d')
            dt = datetime.now() - timedelta(days=random.randint(0, 3650))
            try:
                return dt.strftime(strftime_fmt)
            except Exception:
                return dt.strftime('%Y-%m-%d')
        elif rule == '自增主键（自动生成）':
            return None
        else:
            ftype_low = ftype.lower()
            fname = field.lower()
            if 'int' in ftype_low:
                if 'bigint' in ftype_low:
                    return random.randint(1000000000, 9999999999)
                return random.randint(1, 100000)
            if 'decimal' in ftype_low or 'float' in ftype_low or 'double' in ftype_low:
                return round(random.uniform(1, 10000), 2)
            if 'date' in ftype_low and 'time' not in ftype_low:
                return (datetime.now() - timedelta(days=random.randint(0, 3650))).strftime('%Y-%m-%d')
            if 'datetime' in ftype_low or 'timestamp' in ftype_low:
                return (datetime.now() - timedelta(days=random.randint(0, 3650))).strftime('%Y-%m-%d %H:%M:%S')
            if 'char' in ftype_low or 'text' in ftype_low:
                if 'name' in fname:
                    return DataFactory.random_name()
                if 'phone' in fname:
                    return DataFactory.random_phone()
                if 'id' in fname and 'card' not in fname:
                    return DataFactory.random_id_number()
                if 'plate' in fname:
                    return DataFactory.random_plate_number()['plate_number']
                if 'etc' in fname:
                    return DataFactory.random_etc_number()
                if 'obn' in fname:
                    return DataFactory.random_obn_number()
                if 'device' in fname:
                    return DataFactory.random_device_id() if hasattr(DataFactory, 'random_device_id') else 'D' + ''.join(random.choices('0123456789', k=15))
                if 'order' in fname:
                    return DataFactory.random_order_id() if hasattr(DataFactory, 'random_order_id') else 'O' + ''.join(random.choices('0123456789', k=15))
                if 'card' in fname:
                    return DataFactory.random_bank_card()
                if 'bank' in fname:
                    return DataFactory.random_bank_address() if hasattr(DataFactory, 'random_bank_address') else fake.address()
                return 'teststr'
            return 'test'
    while inserted < total:
        batch = []
        for _ in range(min(batch_size, total - inserted)):
            row = []
            for i, field in enumerate(fields):
                rule = rules[i]
                ftype = types[i]
                extra = extras[i] if extras else None
                val = gen_value(rule, field, ftype, extra)
                row.append(val)
            batch.append(tuple(row))
        placeholders = ','.join(['%s'] * len(fields))
        sql = f"INSERT INTO `{table}` ({','.join(fields)}) VALUES ({placeholders})"
        print(f"[DEBUG] run_stock_in_flow 插入 fields: {fields}")
        print(f"[DEBUG] run_stock_in_flow 插入 values: {batch}")
        db.cursor.executemany(sql, batch)
        db.conn.commit()
        inserted += len(batch)
        if progress_callback:
            progress_callback(int(inserted * 100 / total))
    db.close() 