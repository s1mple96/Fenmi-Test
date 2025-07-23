import json
import os
import pytest
from utils.mongodb_util import MongoDBUtil

# 读取 MongoDB 连接信息
def get_mongodb_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'connections.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        configs = json.load(f)
    for item in configs:
        if item['type'] == 'mongodb':
            host, port = item['address'].split(':')
            return {
                'host': host,
                'port': int(port),
                'database': 'test',  # 假设数据库名为test，如有不同请修改
                'username': item.get('username'),
                'password': item.get('password')
            }
    raise Exception('未找到MongoDB连接信息')

class TestMongoDBUtil:
    def test_insert_find_update_delete(self):
        config = get_mongodb_config()
        db = MongoDBUtil(**config)
        try:
            # 插入数据
            insert_result = db.insert_one('test_collection', {'name': 'pytest', 'value': 123})
            assert insert_result.inserted_id is not None
            # 查询数据
            find_result = db.find('test_collection', {'name': 'pytest'})
            assert len(find_result) > 0
            # 更新数据
            update_result = db.update_one('test_collection', {'name': 'pytest'}, {'value': 456})
            assert update_result.modified_count == 1
            # 删除数据
            delete_result = db.delete_one('test_collection', {'name': 'pytest'})
            assert delete_result.deleted_count == 1
        finally:
            db.close()
