# -*- coding: utf-8 -*-
# -------------------------------------------------------------
# MongoDB 数据库操作工具类，封装连接、增删改查等常用功能
# -------------------------------------------------------------
from pymongo import MongoClient
from typing import Optional, List, Dict, Any

class MongoDBUtil:
    """
    MongoDB 数据库操作工具类，支持连接、增删改查等常用操作。
    """
    def __init__(self, host: str, port: int, database: str, username: Optional[str] = None, password: Optional[str] = None):
        """
        初始化 MongoDBUtil 实例
        :param host: 数据库地址
        :param port: 端口号
        :param database: 数据库名
        :param username: 用户名，可选
        :param password: 密码，可选
        """
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password
        self.client: Optional[MongoClient] = None
        self.db = None

    def connect(self):
        """
        建立数据库连接
        """
        if self.username and self.password:
            self.client = MongoClient(self.host, self.port, username=self.username, password=self.password)
        else:
            self.client = MongoClient(self.host, self.port)
        self.db = self.client[self.database]

    def close(self):
        """
        关闭数据库连接
        """
        if self.client:
            self.client.close()

    def insert_one(self, collection: str, data: Dict[str, Any]) -> Any:
        """
        插入一条数据
        :param collection: 集合名
        :param data: 插入的数据
        :return: 插入结果
        """
        if not self.client:
            self.connect()
        return self.db[collection].insert_one(data)

    def find(self, collection: str, query: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        查询数据
        :param collection: 集合名
        :param query: 查询条件
        :return: 查询结果列表
        """
        if not self.client:
            self.connect()
        return list(self.db[collection].find(query or {}))

    def update_one(self, collection: str, query: Dict[str, Any], update: Dict[str, Any]) -> Any:
        """
        更新一条数据
        :param collection: 集合名
        :param query: 查询条件
        :param update: 更新内容
        :return: 更新结果
        """
        if not self.client:
            self.connect()
        return self.db[collection].update_one(query, {'$set': update})

    def delete_one(self, collection: str, query: Dict[str, Any]) -> Any:
        """
        删除一条数据
        :param collection: 集合名
        :param query: 查询条件
        :return: 删除结果
        """
        if not self.client:
            self.connect()
        return self.db[collection].delete_one(query)
