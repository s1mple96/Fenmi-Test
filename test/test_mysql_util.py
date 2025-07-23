import json
import os
import pytest
from utils.mysql_util import MySQLUtil

# 读取 MySQL 连接信息
def get_mysql_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'connections.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        configs = json.load(f)
    for item in configs:
        if item['type'] == 'mysql':
            host, port = item['address'].split(':')
            return {
                'host': host,
                'port': int(port),
                'user': item['username'],
                'password': item['password'],
                'database': 'test'  # 这里假设数据库名为test，如有不同请修改
            }
    raise Exception('未找到MySQL连接信息')

class TestMySQLUtil:
    def test_query(self):
        config = get_mysql_config()
        db = MySQLUtil(**config)
        try:
            # 查询当前数据库所有表
            result = db.query('SHOW TABLES')
            print('所有表:', result)
            assert isinstance(result, list)
        finally:
            db.close()

    def test_execute(self):
        config = get_mysql_config()
        db = MySQLUtil(**config)
        try:
            # 创建临时表并插入数据
            db.execute('CREATE TABLE IF NOT EXISTS test_tmp(id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(20))')
            affected = db.execute('INSERT INTO test_tmp(name) VALUES(%s)', ('pytest',))
            print('插入行数:', affected)
            assert affected == 1
            # 查询插入的数据
            result = db.query('SELECT * FROM test_tmp WHERE name=%s', ('pytest',))
            print('查询结果:', result)
            assert result[0]['name'] == 'pytest'
        finally:
            db.execute('DROP TABLE IF EXISTS test_tmp')
            db.close()
