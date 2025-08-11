# -*- coding: utf-8 -*-
"""
通用API接口
"""
from flask import Blueprint, request, jsonify
from web_backend.services.web_common_service import WebCommonService
from common.log_util import get_logger

common_bp = Blueprint('common', __name__)
logger = get_logger("common_api")

@common_bp.route('/provinces', methods=['GET'])
def get_provinces():
    """获取省份列表"""
    try:
        service = WebCommonService()
        result = service.get_provinces()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"获取省份列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取省份列表失败',
            'error': str(e)
        }), 500

@common_bp.route('/plate_letters/<province>', methods=['GET'])
def get_plate_letters(province):
    """获取车牌字母列表"""
    try:
        service = WebCommonService()
        result = service.get_plate_letters(province)
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"获取车牌字母列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取车牌字母列表失败',
            'error': str(e)
        }), 500

@common_bp.route('/validate', methods=['POST'])
def validate_data():
    """数据验证接口"""
    try:
        data = request.get_json()
        field_type = data.get('type')
        value = data.get('value')
        
        service = WebCommonService()
        result = service.validate_field(field_type, value)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"数据验证失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '验证失败',
            'error': str(e)
        }), 500

@common_bp.route('/upload', methods=['POST'])
def upload_file():
    """文件上传接口"""
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '没有上传文件'
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '文件名为空'
            }), 400
        
        service = WebCommonService()
        result = service.handle_file_upload(file)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '文件上传失败',
            'error': str(e)
        }), 500 