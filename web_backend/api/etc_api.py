# -*- coding: utf-8 -*-
"""
客车ETC申办API接口
"""
from flask import Blueprint, request, jsonify
import json
from web_backend.services.web_etc_service import WebETCService
from common.log_util import get_logger

etc_bp = Blueprint('etc', __name__)
logger = get_logger("etc_api")

@etc_bp.route('/apply', methods=['POST'])
def apply_etc():
    """客车ETC申办接口"""
    try:
        data = request.get_json()
        logger.info(f"收到客车ETC申办请求: {json.dumps(data, ensure_ascii=False)}")
        
        # 参数验证 - 检查前端字段名
        required_fields = ['name', 'idCode', 'phone', 'plateProvince', 'plateLetter', 'plateNumber', 'vin']
        
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'缺少必填字段: {", ".join(missing_fields)}'
            }), 400
        
        # 转换字段名为服务层期望的格式
        service = WebETCService()
        vehicle_color_code = service.get_vehicle_color_code(data.get('vehicleColor', '蓝色'))
        
        service_data = {
            'name': data.get('name'),
            'id_code': data.get('idCode'),
            'phone': data.get('phone'),
            'bank_no': data.get('bankNo'),
            'bank_name': data.get('bankName'),
            'operator_code': data.get('operatorCode', 'TXB'),
            'product_id': data.get('productId'),
            'plate_province': data.get('plateProvince'),
            'plate_letter': data.get('plateLetter'),
            'plate_number': data.get('plateNumber'),
            'vin': data.get('vin'),
            'vehicle_color': vehicle_color_code,  # 转换为颜色代码
            'verify_code': data.get('verifyCode', '')
        }
        
        # 调用服务层处理申办
        result = service.start_etc_apply_flow(service_data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"客车ETC申办失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '申办失败',
            'error': str(e)
        }), 500

@etc_bp.route('/status', methods=['GET'])
def get_service_status():
    """获取ETC服务状态"""
    try:
        service = WebETCService()
        result = service.check_service_status()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取服务状态失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取服务状态失败',
            'error': str(e)
        }), 500

@etc_bp.route('/validate', methods=['POST'])
def validate_params():
    """验证ETC申办参数"""
    try:
        data = request.get_json()
        logger.info(f"验证ETC申办参数: {json.dumps(data, ensure_ascii=False)}")
        
        service = WebETCService()
        validated_params = service.validate_params(data)
        
        return jsonify({
            'success': True,
            'message': '参数验证通过',
            'data': validated_params
        })
        
    except Exception as e:
        logger.error(f"参数验证失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'参数验证失败: {str(e)}',
            'error': str(e)
        }), 400

@etc_bp.route('/get_default_data', methods=['GET'])
def get_default_data():
    """获取客车默认数据"""
    try:
        service = WebETCService()
        result = service.get_default_data()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"获取客车默认数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取客车默认数据失败',
            'error': str(e)
        }), 500

@etc_bp.route('/save_data', methods=['POST'])
def save_data():
    """保存客车数据"""
    try:
        data = request.get_json()
        logger.info(f"收到客车数据保存请求: {json.dumps(data, ensure_ascii=False)}")
        
        # 转换字段名为服务层期望的格式
        service = WebETCService()
        vehicle_color_code = service.get_vehicle_color_code(data.get('vehicleColor', '蓝色'))
        
        service_data = {
            'name': data.get('name'),
            'id_code': data.get('idCode'),
            'phone': data.get('phone'),
            'bank_no': data.get('bankNo'),
            'bank_name': data.get('bankName'),
            'operator_code': data.get('operatorCode', 'TXB'),
            'product_id': data.get('productId'),
            'plate_province': data.get('plateProvince'),
            'plate_letter': data.get('plateLetter'),
            'plate_number': data.get('plateNumber'),
            'vin': data.get('vin'),
            'vehicle_color': vehicle_color_code,  # 转换为颜色代码
            'verify_code': data.get('verifyCode', '')
        }
        
        result = service.save_etc_data(service_data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"保存客车数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '保存数据失败',
            'error': str(e)
        }), 500

@etc_bp.route('/api_url', methods=['GET'])
def get_api_url():
    """获取API基础URL"""
    try:
        service = WebETCService()
        api_url = service.get_api_base_url()
        
        return jsonify({
            'success': True,
            'data': {
                'api_url': api_url
            }
        })
        
    except Exception as e:
        logger.error(f"获取API URL失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取API URL失败',
            'error': str(e)
        }), 500

@etc_bp.route('/products', methods=['GET'])
def get_products():
    """获取产品列表"""
    try:
        operator_code = request.args.get('operator_code', 'TXB')
        vehicle_type = request.args.get('vehicle_type', '0')  # 0=客车, 1=货车
        logger.info(f"获取产品列表，运营商: {operator_code}, 车辆类型: {vehicle_type}")
        
        service = WebETCService()
        result = service.get_products_by_operator(operator_code, vehicle_type)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取产品列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取产品列表失败: {str(e)}',
            'error': str(e)
        }), 500

@etc_bp.route('/operators', methods=['GET'])
def get_operators():
    """获取运营商列表"""
    try:
        vehicle_type = request.args.get('vehicle_type', '0')  # 0=客车, 1=货车
        logger.info(f"获取运营商列表，车辆类型: {vehicle_type}")
        
        service = WebETCService()
        result = service.get_operators(vehicle_type)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取运营商列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取运营商列表失败: {str(e)}',
            'error': str(e)
        }), 500

@etc_bp.route('/confirm_verify_code', methods=['POST'])
def confirm_verify_code():
    """确认验证码并完成申办"""
    try:
        data = request.get_json()
        logger.info(f"确认验证码: {json.dumps(data, ensure_ascii=False)}")
        
        service = WebETCService()
        result = service.confirm_verify_code(data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"确认验证码失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'确认验证码失败: {str(e)}',
            'error': str(e)
        }), 500

@etc_bp.route('/progress/<task_id>', methods=['GET'])
def get_progress(task_id):
    """获取申办进度"""
    try:
        # 这里可以从缓存或数据库获取进度
        # 暂时返回模拟进度
        return jsonify({
            'success': True,
            'data': {
                'progress': 50,
                'message': '正在处理申办...',
                'status': 'processing'
            }
        })
    except Exception as e:
        logger.error(f"获取进度失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取进度失败',
            'error': str(e)
        }), 500 