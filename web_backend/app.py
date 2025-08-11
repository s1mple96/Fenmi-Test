# -*- coding: utf-8 -*-
"""
ETC申办系统 - Flask Web后端
"""
import sys
import os
import time
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.insert(0, project_root)

from common.config_util import get_config
from common.log_util import get_logger
from web_backend.api import create_api_blueprint
from web_backend.services.web_etc_service import WebETCService
from web_backend.services.web_truck_service import WebTruckService

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'etc-apply-system-secret-key'

# 启用CORS支持
CORS(app, supports_credentials=True)

# 配置日志
logger = get_logger("web_backend")

# 注册API蓝图
api_bp = create_api_blueprint()
app.register_blueprint(api_bp, url_prefix='/api')

@app.route('/')
def index():
    """首页"""
    return jsonify({
        'message': 'ETC申办系统 Web API',
        'version': '1.0.0',
        'status': 'running'
    })

@app.route('/api/health')
def health_check():
    """健康检查接口"""
    return jsonify({
        'status': 'healthy',
        'timestamp': int(time.time())
    })

@app.errorhandler(Exception)
def handle_exception(e):
    """全局异常处理"""
    logger.error(f"API异常: {str(e)}")
    return jsonify({
        'success': False,
        'message': '服务器内部错误',
        'error': str(e)
    }), 500

if __name__ == '__main__':
    
    # 读取配置
    config = get_config('web')
    host = config.get('web_server', {}).get('host', '127.0.0.1')
    port = config.get('web_server', {}).get('port', 5000)
    debug = config.get('web_server', {}).get('debug', True)
    
    logger.info(f"启动ETC申办系统Web服务器 - {host}:{port}")
    app.run(host=host, port=port, debug=debug) 