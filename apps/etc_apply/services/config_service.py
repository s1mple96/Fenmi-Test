# -*- coding: utf-8 -*-
"""
配置服务 - 统一管理配置文件读取
"""
import json
import os


class ConfigService:
    """配置服务 - 只提供基础的配置读取功能"""
    
    @staticmethod
    def get_config_path(filename: str) -> str:
        """获取配置文件路径"""
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        return os.path.join(base_dir, 'config', filename)
    
    @staticmethod
    def get_api_base_url() -> str:
        """获取API基础URL"""
        config_path = ConfigService.get_config_path('app_config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config.get('api', {}).get('base_url', 'http://788360p9o5.yicp.fun')
        except Exception as e:
            print(f"读取配置文件失败: {e}")
            return 'http://788360p9o5.yicp.fun'  # 默认值
    
    @staticmethod
    def get_etc_service_url() -> str:
        """获取ETC服务URL"""
        config_path = ConfigService.get_config_path('app_config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config.get('etc_service', {}).get('base_url', 'http://ectbao.imdo.co')
        except Exception as e:
            print(f"读取ETC服务配置失败: {e}")
            return 'http://ectbao.imdo.co'  # 默认值
    
    @staticmethod
    def get_browser_cookies() -> dict:
        """获取浏览器cookies"""
        config_path = ConfigService.get_config_path('app_config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config.get('browser_cookies', {})
        except Exception as e:
            print(f"读取浏览器cookies配置失败: {e}")
            return {}
    
    @staticmethod
    def get_mysql_config() -> dict:
        """获取MySQL连接配置"""
        config_path = ConfigService.get_config_path('app_config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            db_config = config.get('database', {}).get('hcb', {})
            return {
                'host': db_config.get('host', 'localhost'),
                'port': db_config.get('port', 3306),
                'user': db_config.get('username', 'root'),
                'password': db_config.get('password', 'password'),
                'database': db_config.get('database', 'hcb'),
            }
        except Exception as e:
            print(f"读取MySQL配置失败: {e}")
            raise Exception("未找到MySQL连接配置！") 