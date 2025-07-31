import os

def resource_path(relative_path):
    """获取资源文件的绝对路径，始终以项目根目录为基准"""
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path) 