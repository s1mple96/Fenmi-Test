# -*- coding: utf-8 -*-
# -------------------------------------------------------------
# Redis 操作工具类，封装常用字符串、哈希等操作
# -------------------------------------------------------------
import redis
from typing import Optional, Any

class RedisUtil:
    """
    Redis 操作工具类，支持常用的字符串、哈希等操作。
    """
    def __init__(self, host: str, port: int, password: Optional[str] = None, db: int = 0):
        """
        初始化 RedisUtil 实例
        :param host: Redis 服务器地址
        :param port: Redis 端口
        :param password: Redis 密码，可选
        :param db: 数据库编号，默认0
        """
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.client: Optional[redis.Redis] = None

    def connect(self):
        """
        建立 Redis 连接
        """
        self.client = redis.Redis(host=self.host, port=self.port, password=self.password, db=self.db, decode_responses=True)

    def set(self, key: str, value: Any, ex: Optional[int] = None):
        """
        设置字符串键值
        :param key: 键
        :param value: 值
        :param ex: 过期时间（秒）
        """
        if not self.client:
            self.connect()
        self.client.set(key, value, ex=ex)

    def get(self, key: str) -> Any:
        """
        获取字符串键值
        :param key: 键
        :return: 值
        """
        if not self.client:
            self.connect()
        return self.client.get(key)

    def delete(self, key: str):
        """
        删除键
        :param key: 键
        """
        if not self.client:
            self.connect()
        self.client.delete(key)

    def hset(self, name: str, key: str, value: Any):
        """
        设置哈希表字段
        :param name: 哈希表名
        :param key: 字段名
        :param value: 字段值
        """
        if not self.client:
            self.connect()
        self.client.hset(name, key, value)

    def hget(self, name: str, key: str) -> Any:
        """
        获取哈希表字段值
        :param name: 哈希表名
        :param key: 字段名
        :return: 字段值
        """
        if not self.client:
            self.connect()
        return self.client.hget(name, key)

    def close(self):
        """
        关闭 Redis 连接
        """
        if self.client:
            self.client.close()
            self.client = None
