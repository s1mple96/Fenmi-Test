# -*- coding: utf-8 -*-
# -------------------------------------------------------------
# MySQL 数据库操作工具类，封装连接、查询、增删改等常用功能
# -------------------------------------------------------------
import pymysql
from typing import Optional, List, Dict, Any

class MySQLUtil:
    def __init__(self, host: str, port: int, user: str, password: str, database: str, charset: str = 'utf8mb4'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.charset = charset
        self.conn: Optional[pymysql.connections.Connection] = None
        self.cursor: Optional[pymysql.cursors.Cursor] = None

    def connect(self):
        self.conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset=self.charset
        )
        self.cursor = self.conn.cursor(pymysql.cursors.DictCursor)

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def query(self, sql: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
        if not self.conn:
            self.connect()
        self.cursor.execute(sql, params)
        return self.cursor.fetchall()

    def execute(self, sql: str, params: Optional[tuple] = None) -> int:
        if not self.conn:
            self.connect()
        result = self.cursor.execute(sql, params)
        self.conn.commit()
        return result

    @staticmethod
    def get_databases(config: dict) -> List[str]:
        db = MySQLUtil(**config)
        db.connect()
        dbs = db.query('SHOW DATABASES')
        db.close()
        return [list(row.values())[0] for row in dbs]

    @staticmethod
    def get_tables(config: dict, database: str) -> List[str]:
        config = config.copy()
        config['database'] = database
        db = MySQLUtil(**config)
        db.connect()
        tables = db.query('SHOW TABLES')
        db.close()
        return [list(row.values())[0] for row in tables]

    @staticmethod
    def get_table_ddl(config: dict, database: str, table: str) -> str:
        config = config.copy()
        config['database'] = database
        db = MySQLUtil(**config)
        db.connect()
        ddl = db.query(f'SHOW CREATE TABLE `{table}`')
        db.close()
        if ddl:
            return ddl[0]['Create Table']
        return ''

    @staticmethod
    def get_product_list_from_db(config_path: str, channelcompany_id: str = 'd4949f0bc4c04a53987ac747287f3943'):
        """
        读取config/connections.json，连接MySQL，查询产品列表
        :param config_path: 配置文件路径
        :param channelcompany_id: 渠道公司ID
        :return: 产品列表
        """
        import json
        import os
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"配置文件不存在: {config_path}")
        with open(config_path, 'r', encoding='utf-8') as f:
            configs = json.load(f)
        mysql_conf = None
        for c in configs:
            if c.get('type') == 'mysql':
                host, port = c['address'].split(':')
                mysql_conf = {
                    'host': host,
                    'port': int(port),
                    'user': c['username'],
                    'password': c['password'],
                    'database': 'rtx',
                }
                break
        if not mysql_conf:
            raise Exception("未找到MySQL连接配置！")
        db = MySQLUtil(**mysql_conf)
        db.connect()
        sql = ("select product_id,product_name,operator_code,status "
               "from rtx_product "
               "where PRODUCT_ID in "
               "(select PRODUCT_ID from rtx_channel_company_profit "
               f"where channelcompany_id = '{channelcompany_id}')")
        rows = db.query(sql)
        db.close()
        return rows
