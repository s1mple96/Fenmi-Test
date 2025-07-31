# -*- coding: utf-8 -*-
# -------------------------------------------------------------
# 数据库批量造数插入线程（QThread）
# 支持进度条、取消、规则驱动造数，详细中文注释
# -------------------------------------------------------------
from PyQt5.QtCore import QThread, pyqtSignal
from common.mysql_util import MySQLUtil
from common.data_factory import DataFactory
import random
from datetime import datetime, timedelta

# 用户自定义日期格式转strftime格式
# 如 YYYYMMDD -> %Y%m%d
#    YYYY-MM-DD -> %Y-%m-%d
def user_date_format_to_strftime(fmt):
    fmt = fmt.replace('YYYY', '%Y').replace('MM', '%m').replace('DD', '%d')
    return fmt

class DataGenInsertWorker(QThread):
    """
    数据库批量造数插入线程，支持进度条、取消、规则驱动造数
    """
    progress = pyqtSignal(int)    # 进度百分比信号
    finished = pyqtSignal(str)    # 完成信号
    error = pyqtSignal(str)       # 错误信号
    batch_size = 100              # 每批插入条数

    def __init__(self, config, dbname, table, fields, types, rules, count, extras=None):
        super().__init__()
        self.config = config      # 数据库连接配置
        self.dbname = dbname      # 数据库名
        self.table = table        # 表名
        self.fields = fields      # 字段名列表
        self.types = types        # 字段类型列表
        self.rules = rules        # 造数规则列表
        self.count = count        # 总插入条数
        self._is_running = True   # 线程运行标志
        self.extras = extras or [None] * len(fields)  # 规则额外参数

    def run(self):
        """
        线程主函数，批量生成并插入数据，支持进度条和取消
        """
        try:
            config = self.config.copy()
            config['database'] = self.dbname
            db = MySQLUtil(**config)
            db.connect()
            total = self.count
            inserted = 0
            while inserted < total and self._is_running:
                batch = []
                for _ in range(min(self.batch_size, total - inserted)):
                    row = []
                    for i, field in enumerate(self.fields):
                        rule = self.rules[i]
                        ftype = self.types[i]
                        extra = self.extras[i] if self.extras else None
                        val = self.gen_value(rule, field, ftype, extra)
                        row.append(val)
                    batch.append(tuple(row))
                placeholders = ','.join(['%s'] * len(self.fields))
                sql = f"INSERT INTO `{self.table}` ({','.join(self.fields)}) VALUES ({placeholders})"
                db.cursor.executemany(sql, batch)
                db.conn.commit()
                inserted += len(batch)
                self.progress.emit(int(inserted * 100 / total))
            db.close()
            if self._is_running:
                self.finished.emit(f'成功插入{inserted}条数据')
            else:
                self.finished.emit(f'已取消，实际插入{inserted}条数据')
        except Exception as e:
            self.error.emit(str(e))

    def gen_value(self, rule, field, ftype, extra=None):
        """
        按规则生成单字段数据
        """
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
            return DataFactory.random_device_id()
        elif rule == '随机订单号':
            return DataFactory.random_order_id()
        elif rule == '随机银行卡号':
            return DataFactory.random_bank_card()
        elif rule == '随机银行地址':
            return DataFactory.random_bank_address()
        elif rule == '固定值':
            return extra if extra is not None else 'test'
        elif rule == '枚举值':
            if extra:
                enums = [v.strip() for v in extra.split(',') if v.strip()]
                return random.choice(enums) if enums else '0'
            return '0'
        elif rule == '随机日期':
            fmt = extra if extra else 'YYYY-MM-DD'
            strftime_fmt = user_date_format_to_strftime(fmt)
            dt = datetime.now() - timedelta(days=random.randint(0, 3650))
            try:
                return dt.strftime(strftime_fmt)
            except Exception:
                return dt.strftime('%Y%m%d')
        elif rule == '自增主键（自动生成）':
            return None
        else:
            # 自动识别类型
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
                    return DataFactory.random_device_id()
                if 'order' in fname:
                    return DataFactory.random_order_id()
                if 'card' in fname:
                    return DataFactory.random_bank_card()
                if 'bank' in fname:
                    return DataFactory.random_bank_address()
                return 'teststr'
            return 'test'

    def stop(self):
        """
        停止线程，安全取消插入
        """
        self._is_running = False
