# -*- coding: utf-8 -*-
# -------------------------------------------------------------
# Linux 操作工具类，封装 SSH、命令、上传、下载等常用功能
# -------------------------------------------------------------
import paramiko
from typing import Optional

class LinuxUtil:
    """
    Linux 操作工具类，支持 SSH 远程连接、命令执行、文件上传下载等功能。
    """
    def __init__(self, host: str, username: str, password: str, port: int = 22):
        """
        初始化 LinuxUtil 实例
        :param host: 服务器地址
        :param username: 登录用户名
        :param password: 登录密码
        :param port: SSH 端口，默认22
        """
        self.host = host
        self.username = username
        self.password = password
        self.port = port
        self.client: Optional[paramiko.SSHClient] = None

    def connect(self):
        """
        建立 SSH 连接
        """
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.client.connect(self.host, port=self.port, username=self.username, password=self.password)

    def exec_command(self, command: str) -> str:
        """
        执行远程命令
        :param command: 要执行的命令字符串
        :return: 命令输出结果
        :raises Exception: 命令执行出错时抛出
        """
        if not self.client:
            self.connect()
        stdin, stdout, stderr = self.client.exec_command(command)
        result = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        if error:
            raise Exception(f'执行命令出错: {error}')
        return result

    def upload_file(self, local_path: str, remote_path: str):
        """
        上传本地文件到远程服务器
        :param local_path: 本地文件路径
        :param remote_path: 远程文件路径
        """
        if not self.client:
            self.connect()
        sftp = self.client.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()

    def download_file(self, remote_path: str, local_path: str):
        """
        从远程服务器下载文件到本地
        :param remote_path: 远程文件路径
        :param local_path: 本地文件路径
        """
        if not self.client:
            self.connect()
        sftp = self.client.open_sftp()
        sftp.get(remote_path, local_path)
        sftp.close()

    def close(self):
        """
        关闭 SSH 连接
        """
        if self.client:
            self.client.close()
            self.client = None
