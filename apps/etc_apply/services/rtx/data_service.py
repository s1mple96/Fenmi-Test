# -*- coding: utf-8 -*-
"""
数据服务 - 整合数据库操作和参数处理
"""
import random
import uuid
from datetime import datetime
from typing import Dict, Any
from common.mysql_util import MySQLUtil
from apps.etc_apply.services.rtx.core_service import CoreService


class DataService:
    """数据服务 - 整合数据库操作和参数处理"""
    
    # ==================== 数据库操作 ====================
    
    @staticmethod
    def update_order_status(order_id: str) -> None:
        """更新订单状态"""
        try:
            conf = CoreService.get_rtx_mysql_config()
            db = MySQLUtil(**conf)
            db.connect()
            sql = "UPDATE rtx_etcapply_order t SET t.order_status = '7' WHERE t.order_id = %s"
            db.execute(sql, (order_id,))
            db.close()
        except Exception as e:
            error_msg = CoreService.format_database_error("更新订单状态", e)
            raise Exception(error_msg)
    
    @staticmethod
    def update_card_user_status(car_num: str) -> None:
        """更新卡用户状态"""
        try:
            conf = CoreService.get_rtx_mysql_config()
            db = MySQLUtil(**conf)
            db.connect()
            sql = """
            UPDATE rtx_etc_card_user t 
            SET t.status = '3', t.update_time = NOW() 
            WHERE t.car_num = %s
            """
            db.execute(sql, (car_num,))
            db.close()
        except Exception as e:
            error_msg = CoreService.format_database_error("更新卡用户状态", e)
            raise Exception(error_msg)
    
    @staticmethod
    def update_card_user_obu_info(car_num: str, obu_no: str, etc_sn: str, activation_time: str) -> None:
        """更新卡用户OBU信息"""
        try:
            conf = CoreService.get_rtx_mysql_config()
            db = MySQLUtil(**conf)
            db.connect()
            sql = """
            UPDATE rtx_etc_card_user t 
            SET t.obu_no = %s, t.etc_sn = %s, t.activation_time = %s, t.update_time = NOW() 
            WHERE t.car_num = %s
            """
            db.execute(sql, (obu_no, etc_sn, activation_time, car_num))
            db.close()
        except Exception as e:
            error_msg = CoreService.format_database_error("更新卡用户OBU信息", e)
            raise Exception(error_msg)
    
    @staticmethod
    def update_final_card_user_status(car_num: str) -> None:
        """更新最终卡用户状态"""
        try:
            conf = CoreService.get_rtx_mysql_config()
            db = MySQLUtil(**conf)
            db.connect()
            sql = """
            UPDATE rtx_etc_card_user t 
            SET t.active_status = 2007, t.status = '1', t.update_time = NOW() 
            WHERE t.car_num = %s
            """
            db.execute(sql, (car_num,))
            db.close()
        except Exception as e:
            error_msg = CoreService.format_database_error("更新最终卡用户状态", e)
            raise Exception(error_msg)
    
    @staticmethod
    def close_mock_data() -> bool:
        """关闭Mock数据配置"""
        try:
            mysql_conf = CoreService.get_rtx_mysql_config()
            if not mysql_conf:
                print("未找到MySQL连接配置，无法关闭Mock数据")
                return False
            
            business_config = CoreService.get_business_config()
            mock_config_id = business_config.get('mock_config_id', 55)
            
            db = MySQLUtil(**mysql_conf)
            db.connect()
            sql = f"UPDATE rtx.sys_config t SET t.config_value = '0' WHERE t.config_id = {mock_config_id}"
            db.execute(sql)
            db.close()
            print("Mock数据已关闭")
            return True
        except Exception as e:
            error_msg = CoreService.format_database_error("关闭Mock数据", e)
            print(f"关闭Mock数据失败: {error_msg}")
            return False
    
    @staticmethod
    def insert_device_stock(car_num: str) -> Dict[str, str]:
        """插入设备库存数据"""
        device_config = CoreService.get_device_config()
        province_mapping = device_config.get('province_mapping', {})
        province_codes = device_config.get('province_codes', {})
        obu_length = device_config.get('obu_length', 16)
        etc_length = device_config.get('etc_length', 20)
        
        def generate_device_no(province, device_type):
            code = province_codes.get(province, "9999")
            length = obu_length if device_type == "0" else etc_length
            remain = length - len(code)
            suffix = ''.join(random.choices("0123456789", k=remain))
            return code + suffix
        
        # 解析车牌号获取省份
        province_abbr = car_num[0] if car_num else "苏"
        province_name = province_mapping.get(province_abbr, "江苏")
        
        # 生成设备号
        obn_no = generate_device_no(province_name, "0")
        etc_no = generate_device_no(province_name, "1")
        
        # 准备数据
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        base_data = {
            "CARD_OPERATORS": "1",
            "STATUS": "1",
            "CAR_NUM": car_num,
            "STOCK_STATUS": "0",
            "SOURCE": "1",
            "REMARK": "激活设备不存在库存内",
            "CREATE_TIME": now,
            "DEVICE_CATEGORY": "0"
        }
        
        obn_data = base_data.copy()
        obn_data.update({
            "NEWSTOCK_ID": uuid.uuid4().hex,
            "INTERNAL_DEVICE_NO": obn_no,
            "EXTERNAL_DEVICE_NO": obn_no,
            "TYPE": "0"
        })
        
        etc_data = base_data.copy()
        etc_data.update({
            "NEWSTOCK_ID": uuid.uuid4().hex,
            "INTERNAL_DEVICE_NO": etc_no,
            "EXTERNAL_DEVICE_NO": etc_no,
            "TYPE": "1"
        })
        
        # 插入数据库
        mysql_conf = CoreService.get_hcb_mysql_config()
        db = MySQLUtil(**mysql_conf)
        db.connect()
        
        def insert_row(row):
            keys = ','.join(f'`{k}`' for k in row.keys())
            vals = ','.join(['%s'] * len(row))
            sql = f"INSERT INTO hcb_newstock ({keys}) VALUES ({vals})"
            db.execute(sql, tuple(row.values()))
        
        insert_row(obn_data)
        insert_row(etc_data)
        db.close()
        
        return {
            'car_num': car_num,
            'obn_no': obn_no,
            'etc_no': etc_no
        }
    
    @staticmethod
    def run_stock_in_flow(config, dbname, table, fields, types, rules, count, extras=None, progress_callback=None):
        """一键入库流程"""
        config = config.copy()
        config['database'] = dbname
        db = MySQLUtil(**config)
        db.connect()
        
        def gen_value(rule, field, ftype, extra=None):
            if rule == 'uuid':
                return uuid.uuid4().hex
            elif rule == 'random_device':
                return ''.join(random.choices('0123456789', k=16))
            elif rule == 'now':
                return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            elif rule == 'fixed' and extra:
                return extra
            elif rule == '1':
                return '1'
            elif rule == '0':
                return '0'
            elif rule == 'str' and extra:
                return str(extra)
            else:
                return ''
        
        for i in range(count):
            data = {}
            for j, field in enumerate(fields):
                rule = rules[j] if j < len(rules) else 'fixed'
                extra = None
                if isinstance(extras, dict):
                    extra = extras.get(field)
                elif isinstance(extras, list) and j < len(extras):
                    extra = extras[j]
                data[field] = gen_value(rule, field, types[j], extra)
            
            # 插入数据
            keys = ','.join(f'`{k}`' for k in data.keys())
            vals = ','.join(['%s'] * len(data))
            sql = f"INSERT INTO {table} ({keys}) VALUES ({vals})"
            db.execute(sql, tuple(data.values()))
            
            if progress_callback:
                progress_callback(int((i + 1) / count * 100), f"插入第{i+1}条数据")
        
        db.close()
    
    # ==================== 参数处理 ====================
    
    @staticmethod
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
            business_config = CoreService.get_business_config()
            default_product_id = business_config.get('default_product_id', '1503564182627360770')
            if hasattr(ui, 'log_text'):
                ui.log_text.append(f"未选择产品，使用默认产品ID: {default_product_id}")
        
        # 添加车牌颜色
        if hasattr(ui, 'plate_color_combo'):
            form_data['vehicle_color'] = ui.plate_color_combo.currentText()
        
        # 构建完整参数
        return DataService.build_apply_params(form_data)
    
    @staticmethod
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
            'carNum': DataService._build_car_num(form_data),
            'vehicleColor': form_data.get('vehicle_color', '蓝色'),
            'vin': form_data.get('vin', ''),
        })
        
        # 产品信息
        business_config = CoreService.get_business_config()
        if 'selected_product' in form_data and form_data['selected_product']:
            product = form_data['selected_product']
            params['productId'] = product.get('product_id')
            params['operatorCode'] = product.get('operator_code', 'TXB')
        else:
            params['productId'] = business_config.get('default_product_id', '1503564182627360770')
            params['operatorCode'] = business_config.get('default_operator_code', 'TXB')
        
        # 填充业务默认参数
        default_params = CoreService.get_default_params()
        params.update(default_params)
        
        # 验证参数
        CoreService.validate_required_params(params, ['carNum', 'cardHolder', 'idCode', 'bindBankPhone', 'bindBankNo'])
        
        return params
    
    @staticmethod
    def _build_car_num(form_data: Dict[str, Any]) -> str:
        """构建车牌号"""
        province = form_data.get('plate_province', '')
        letter = form_data.get('plate_letter', '')
        number = form_data.get('plate_number', '')
        return CoreService.build_car_num(province, letter, number)
    
    @staticmethod
    def validate_and_complete_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """校验并补全ETC申办参数"""
        # 使用核心服务进行验证
        CoreService.validate_required_params(params, ['carNum', 'cardHolder', 'idCode', 'bindBankPhone', 'bindBankNo'])
        
        # 车牌颜色映射
        vc = params.get('vehicleColor', '0')
        if isinstance(vc, str) and vc in ["蓝色", "黄色", "绿色", "白色", "黑色"]:
            params['vehicleColor'] = CoreService.get_vehicle_color_code(vc)
        else:
            try:
                params['vehicleColor'] = int(vc)
            except Exception:
                params['vehicleColor'] = 0
        
        return params 