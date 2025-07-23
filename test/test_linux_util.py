import json
import os
import pytest
from utils.linux_util import LinuxUtil

# 读取 Linux 连接信息
def get_linux_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'connections.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        configs = json.load(f)
    for item in configs:
        if item['type'] == 'linux':
            return item
    raise Exception('未找到Linux连接信息')

class TestLinuxUtil:
    def test_exec_command(self):
        linux_info = get_linux_config()
        host = linux_info['address']
        username = linux_info['username']
        password = linux_info['password']
        util = LinuxUtil(host, username, password)
        try:
            # 进入/test目录并执行ls命令
            result = util.exec_command('cd /test && ls')
            print('目录内容:', result)
            assert isinstance(result, str)
        finally:
            util.close()
