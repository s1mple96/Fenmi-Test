# -*- coding: utf-8 -*-
"""
参数服务 - 统一处理参数构建和转换
"""
from typing import Dict, Any
from .config_service import ConfigService
from .business_service import BusinessService


def build_apply_params_from_ui(ui) -> Dict[str, Any]:
    """从UI收集数据并构建ETC申办参数"""
    # 收集基础表单数据
    form_data = {k: w.text().strip() for k, w in ui.inputs.items()}
    
    # 添加车牌信息
    if hasattr(ui, 'plate_province_edit'):
        form_data['plate_province'] = ui.plate_province_edit.text().strip()
    if hasattr(ui, 'plate_letter_edit'):
        form_data['plate_letter'] = ui.plate_letter_edit.text().strip()
    if hasattr(ui, 'plate_number_edit'):
        form_data['plate_number'] = ui.plate_number_edit.text().strip()
    if hasattr(ui, 'vin_edit'):
        form_data['vin'] = ui.vin_edit.text().strip()
    
    # 添加产品信息
    if hasattr(ui, 'selected_product') and ui.selected_product:
        form_data['selected_product'] = ui.selected_product
        # 记录产品选择日志
        product_name = ui.selected_product.get('product_name', '')
        operator_code = ui.selected_product.get('operator_code', '')
        if hasattr(ui, 'log_text'):
            ui.log_text.append(f"申办使用产品: {product_name} (ID: {ui.selected_product.get('product_id')}, 运营商: {operator_code})")
    else:
        # 记录默认产品日志
        if hasattr(ui, 'log_text'):
            ui.log_text.append(f"未选择产品，使用默认产品ID: 1503564182627360770")
    
    # 添加车牌颜色
    if hasattr(ui, 'plate_color_combo'):
        form_data['vehicle_color'] = ui.plate_color_combo.currentText()
    
    # 构建完整参数
    return build_apply_params(form_data)


def build_apply_params(form_data: Dict[str, Any]) -> Dict[str, Any]:
    """构建ETC申办参数"""
    params = {}
    
    # 基础用户信息映射
    params.update({
        'cardHolder': form_data.get('name', ''),
        'idCode': form_data.get('id_code', ''),
        'bindBankPhone': form_data.get('phone', ''),
        'bindBankNo': form_data.get('bank_no', ''),
    })
    
    # 车辆信息
    params.update({
        'carNum': _build_car_num(form_data),
        'vehicleColor': form_data.get('vehicle_color', '蓝色'),
        'vin': form_data.get('vin', ''),
    })
    
    # 产品信息
    if 'selected_product' in form_data and form_data['selected_product']:
        product = form_data['selected_product']
        params['productId'] = product.get('product_id')
        params['operatorCode'] = product.get('operator_code', 'TXB')
    else:
        params['productId'] = 1503564182627360770
        params['operatorCode'] = 'TXB'
    
    # 填充业务默认参数
    params.update(_get_business_defaults())
    
    # 验证参数
    BusinessService.validate_required_params(params)
    
    return params


def _build_car_num(form_data: Dict[str, Any]) -> str:
    """构建车牌号"""
    province = form_data.get('plate_province', '')
    letter = form_data.get('plate_letter', '')
    number = form_data.get('plate_number', '')
    return BusinessService.build_car_num(province, letter, number)


def _get_business_defaults() -> Dict[str, Any]:
    """获取业务默认参数"""
    return {
        'truckchannelId': '0000',
        'channelId': '0000',
        'orderType': '0',
        'tempCarNumFlag': '0',
        'bidOrderType': '1',
        'province': '广东省',
        'city': '深圳市',
        'handleLocation': '广东省,深圳市,龙岗区',
        'protocolId': '1480429588403593218',
        'signingImage': 'https://img.jiaduobaoapp.com/images/files/2025/07/07/175185352707236.png',
        'protocolType': 0,
        'idCardUrl': 'https://img.jiaduobaoapp.com/images/files/2025/07/07/175185335686382.jpg',
        'backIdCardUrl': 'https://img.jiaduobaoapp.com/images/files/2025/07/07/1751853438620143.jpg',
        'idcardValidity': '2016.10.25-2026.10.25',
        'idAddress': '广东省龙川县龙母镇张乐村委会下乐汉村97号',
        'urgentContact': '测试员',
        'urgentPhone': '13316690083',
        'bindBankUrl': '',
        'bindBankName': '中国工商银行',
        'bankCode': 'ICBC',
        'bankCardType': '01',
        'bankChannelCode': 'QUICK_COMBINED_PAY',
        'code': '',
        'bankCardInfoId': '1440968899762982912',
        'isAgree': 1,
        'licenseUrl': 'https://img.jiaduobaoapp.com/images/files/2025/07/07/175185367647574.png',
        'backLicenseUrl': 'https://img.jiaduobaoapp.com/images/files/2025/07/07/175185368337190.jpg',
        'carHeadUrl': 'https://img.jiaduobaoapp.com/images/files/2025/07/07/175185369119853.png',
        'vehicleType': '小型轿车',
        'model': '长安牌SC1031GDD53',
        'engineNum': '18505834',
        'useCharacter': '非营运',
        'owner': '',
        'registerDate': '20181029',
        'issueDate': '20181029',
        'approvedPassengerCapacity': 5,
        'length': 4660,
        'wide': 1775,
        'high': 1500,
        'grossMass': 2030,
        'unladenMass': 1454,
        'approvedLoad': '',
        'licenseVerifyFlag': 0,
        'updateCkg': '1',
        'addr': '湖南省湘潭县易俗河镇湘江路居委会',
    }

