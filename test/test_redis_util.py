import json
import os
import pytest
from utils.redis_util import RedisUtil

# 读取 Redis 连接信息
def get_redis_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'connections.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        configs = json.load(f)
    for item in configs:
        if item['type'] == 'redis':
            host, port = item['address'].split(':')
            return {
                'host': host,
                'port': int(port),
                'password': item.get('password')
            }
    raise Exception('未找到Redis连接信息')

class TestRedisUtil:
    def test_set_get_delete(self):
        config = get_redis_config()
        r = RedisUtil(**config)
        try:
            r.set('pytest_key', 'pytest_value', ex=10)
            value = r.get('pytest_key')
            assert value == 'pytest_value'
            r.delete('pytest_key')
            assert r.get('pytest_key') is None
        finally:
            r.close()

    def test_hset_hget(self):
        config = get_redis_config()
        r = RedisUtil(**config)
        try:
            r.hset('pytest_hash', 'field1', 'value1')
            value = r.hget('pytest_hash', 'field1')
            assert value == 'value1'
            r.delete('pytest_hash')
        finally:
            r.close()
