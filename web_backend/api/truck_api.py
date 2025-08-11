# -*- coding: utf-8 -*-
"""
货车申办API接口
"""
from flask import Blueprint, request, jsonify
import json
from web_backend.services.web_truck_service import WebTruckService
from common.log_util import get_logger

truck_bp = Blueprint('truck', __name__)
logger = get_logger("truck_api")

@truck_bp.route('/apply', methods=['POST'])
def apply_truck():
    """货车申办接口"""
    try:
        data = request.get_json()
        logger.info(f"收到货车申办请求: {json.dumps(data, ensure_ascii=False)}")
        
        # 参数验证 - 检查前端字段名
        required_fields = ['name', 'idCode', 'phone', 'plateProvince', 'plateLetter', 'plateNumber', 'vin']
        
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'缺少必填字段: {", ".join(missing_fields)}'
            }), 400
        
        # 转换字段名为服务层期望的格式
        service = WebTruckService()
        vehicle_color_code = service.get_vehicle_color_code(data.get('vehicleColor', '黄色'))
        
        service_data = {
            'name': data.get('name'),
            'id_code': data.get('idCode'),
            'phone': data.get('phone'),
            'bank_no': data.get('bankNo'),
            'bank_name': data.get('bankName'),
            'plate_province': data.get('plateProvince'),
            'plate_letter': data.get('plateLetter'),
            'plate_number': data.get('plateNumber'),
            'vin': data.get('vin'),
            'vehicle_color': vehicle_color_code,  # 转换为颜色代码
            'load_weight': data.get('loadWeight'),
            'length': data.get('length'),
            'width': data.get('width'),
            'height': data.get('height'),
            'vehicle_type': data.get('vehicleType'),
            'axle_count': data.get('axleCount'),
            'tire_count': data.get('tireCount'),
            'verify_code': data.get('verifyCode', '')
        }
        
        # 调用服务层处理申办
        result = service.start_truck_apply_flow(service_data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"货车申办失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '申办失败',
            'error': str(e)
        }), 500

@truck_bp.route('/status', methods=['GET'])
def get_service_status():
    """获取货车服务状态"""
    try:
        service = WebTruckService()
        result = service.check_service_status()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取货车服务状态失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取服务状态失败',
            'error': str(e)
        }), 500

@truck_bp.route('/validate', methods=['POST'])
def validate_truck_params():
    """验证货车申办参数"""
    try:
        data = request.get_json()
        logger.info(f"验证货车申办参数: {json.dumps(data, ensure_ascii=False)}")
        
        service = WebTruckService()
        validated_params = service.validate_truck_params(data)
        
        return jsonify({
            'success': True,
            'message': '货车参数验证通过',
            'data': validated_params
        })
        
    except Exception as e:
        logger.error(f"货车参数验证失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'货车参数验证失败: {str(e)}',
            'error': str(e)
        }), 400

@truck_bp.route('/get_default_data', methods=['GET'])
def get_default_data():
    """获取货车默认数据"""
    try:
        service = WebTruckService()
        result = service.get_default_data()
        
        return jsonify({
            'success': True,
            'data': result
        })
        
    except Exception as e:
        logger.error(f"获取货车默认数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '获取货车默认数据失败',
            'error': str(e)
        }), 500

@truck_bp.route('/operators', methods=['GET'])
def get_operators():
    """获取货车运营商列表"""
    try:
        logger.info("获取货车运营商列表")
        
        service = WebTruckService()
        result = service.get_operators()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取货车运营商列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取货车运营商列表失败: {str(e)}',
            'error': str(e)
        }), 500

@truck_bp.route('/products', methods=['GET'])
def get_products():
    """获取货车产品列表"""
    try:
        operator_code = request.args.get('operator_code', '')
        logger.info(f"获取货车产品列表，运营商: {operator_code}")
        
        if not operator_code:
            return jsonify({
                'success': False,
                'message': '缺少运营商参数'
            }), 400
        
        service = WebTruckService()
        result = service.get_products_by_operator(operator_code)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"获取货车产品列表失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取货车产品列表失败: {str(e)}',
            'error': str(e)
        }), 500

@truck_bp.route('/save_data', methods=['POST'])
def save_data():
    """保存货车数据"""
    try:
        data = request.get_json()
        logger.info(f"收到货车数据保存请求: {json.dumps(data, ensure_ascii=False)}")
        
        # 转换字段名为服务层期望的格式
        service = WebTruckService()
        vehicle_color_code = service.get_vehicle_color_code(data.get('vehicleColor', '黄色'))
        
        service_data = {
            'name': data.get('name'),
            'id_code': data.get('idCode'),
            'phone': data.get('phone'),
            'bank_no': data.get('bankNo'),
            'bank_name': data.get('bankName'),
            'plate_province': data.get('plateProvince'),
            'plate_letter': data.get('plateLetter'),
            'plate_number': data.get('plateNumber'),
            'vin': data.get('vin'),
            'vehicle_color': vehicle_color_code,  # 转换为颜色代码
            'load_weight': data.get('loadWeight'),
            'length': data.get('length'),
            'width': data.get('width'),
            'height': data.get('height'),
            'vehicle_type': data.get('vehicleType'),
            'axle_count': data.get('axleCount'),
            'tire_count': data.get('tireCount'),
            'verify_code': data.get('verifyCode', '')
        }
        
        result = service.save_truck_data(service_data)
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"保存货车数据失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': '保存数据失败',
            'error': str(e)
        }), 500

@truck_bp.route('/api_url', methods=['GET'])
def get_api_url():
    """获取API基础URL"""
    try:
        service = WebTruckService()
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