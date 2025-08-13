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
    def enable_mock_data() -> bool:
        """启用Mock数据配置"""
        try:
            mysql_conf = CoreService.get_rtx_mysql_config()
            if not mysql_conf:
                print("未找到MySQL连接配置，无法启用Mock数据")
                return False
            
            business_config = CoreService.get_business_config()
            mock_config_id = business_config.get('mock_config_id', 55)
            
            db = MySQLUtil(**mysql_conf)
            db.connect()
            sql = f"UPDATE rtx.sys_config t SET t.config_value = '1' WHERE t.config_id = {mock_config_id}"
            db.execute(sql)
            db.close()
            print("客车Mock数据已启用")
            return True
        except Exception as e:
            error_msg = CoreService.format_database_error("启用Mock数据", e)
            print(f"启用Mock数据失败: {error_msg}")
            return False
    
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
            print("客车Mock数据已关闭")
            return True
        except Exception as e:
            error_msg = CoreService.format_database_error("关闭Mock数据", e)
            print(f"关闭Mock数据失败: {error_msg}")
            return False
    
    @staticmethod
    def insert_device_stock(car_num: str, operator_id: str = None, operator_name: str = None, operator_code: str = None) -> Dict[str, str]:
        """插入设备库存数据"""
        device_config = CoreService.get_device_config()
        province_mapping = device_config.get('province_mapping', {})
        province_codes = device_config.get('province_codes', {})
        obu_length = device_config.get('obu_length', 16)
        etc_length = device_config.get('etc_length', 20)
        
        def generate_device_no_by_prefix(prefix, device_type):
            """根据前缀生成设备号"""
            length = obu_length if device_type == "0" else etc_length
            remain = length - len(prefix)
            suffix = ''.join(random.choices("0123456789", k=remain))
            return prefix + suffix
        
        def generate_device_no_by_province(province, device_type):
            """根据省份生成设备号（兜底方案）"""
            code = province_codes.get(province, "3201")
            length = obu_length if device_type == "0" else etc_length
            remain = length - len(code)
            suffix = ''.join(random.choices("0123456789", k=remain))
            return code + suffix
        
        # 🔥 新逻辑：优先根据运营商编码生成设备号前缀
        if operator_code:
            # 使用运营商编码获取前缀
            device_prefix = CoreService.get_operator_prefix_by_code(operator_code)
            obu_no = generate_device_no_by_prefix(device_prefix, "0")
            etc_no = generate_device_no_by_prefix(device_prefix, "1")
            print(f"[INFO] 根据运营商编码 {operator_code} 生成设备号，前缀: {device_prefix}")
        else:
            # 兜底方案：解析车牌号获取省份
            province_abbr = car_num[0] if car_num else "苏"
            province_name = province_mapping.get(province_abbr, "江苏")
            obu_no = generate_device_no_by_province(province_name, "0")
            etc_no = generate_device_no_by_province(province_name, "1")
            print(f"[INFO] 根据车牌省份 {province_name} 生成设备号（兜底方案）")
        
        # 获取设备运营商代码 - 优先级：编码精确匹配 > ID映射 > 默认值
        if operator_code:
            # 最高优先级：使用运营商编码进行精确匹配
            operator_codes = CoreService.get_device_operator_codes_by_operator_code(operator_code)
            print(f"[INFO] 使用运营商编码进行精确匹配: {operator_code}")
        elif operator_id:
            # 中等优先级：兼容原有的ID方式
            operator_codes = CoreService.get_device_operator_codes_by_product(operator_id)
            print(f"[INFO] 使用运营商ID进行匹配: {operator_id}")
        else:
            # 最低优先级：使用默认值
            operator_codes = {'obu_code': '1', 'etc_code': '10'}
            print(f"[INFO] 使用默认运营商代码")
        
        # 准备数据
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        base_data = {
            "STATUS": "1",
            "CAR_NUM": car_num,
            "STOCK_STATUS": "0",
            "SOURCE": "1",
            "REMARK": "激活设备不存在库存内",
            "CREATE_TIME": now,
            "DEVICE_CATEGORY": "0"
        }
        
        # ETC设备数据 (TYPE=0) - 使用ETC运营商代码
        etc_data = base_data.copy()
        etc_data.update({
            "NEWSTOCK_ID": uuid.uuid4().hex,
            "INTERNAL_DEVICE_NO": etc_no,
            "EXTERNAL_DEVICE_NO": etc_no,
            "TYPE": "0",  # 🔥 修正：数据库定义 0=ETC
            "CARD_OPERATORS": operator_codes['etc_code']  # 🔥 ETC使用对应运营商代码
        })
        
        # OBU设备数据 (TYPE=1) - 使用OBU运营商代码
        obu_data = base_data.copy()
        obu_data.update({
            "NEWSTOCK_ID": uuid.uuid4().hex,
            "INTERNAL_DEVICE_NO": obu_no,
            "EXTERNAL_DEVICE_NO": obu_no,
            "TYPE": "1",  # 🔥 修正：数据库定义 1=OBU
            "CARD_OPERATORS": operator_codes['obu_code']  # 🔥 OBU使用对应运营商代码
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
        
        insert_row(etc_data)
        insert_row(obu_data)
        db.close()
        
        operator_info = operator_code or operator_name or operator_id or "默认"
        print(f"✅ 客车设备入库成功:")
        print(f"   - 车牌号: {car_num}")
        print(f"   - 运营商: {operator_info}")
        print(f"   - ETC号: {etc_no} (TYPE=0, 运营商代码: {operator_codes['etc_code']})")
        print(f"   - OBU号: {obu_no} (TYPE=1, 运营商代码: {operator_codes['obu_code']})")
        
        return {
            'car_num': car_num,
            'obu_no': obu_no,
            'etc_no': etc_no,
            'obu_operator_code': operator_codes['obu_code'],
            'etc_operator_code': operator_codes['etc_code'],
            'operator_info': operator_info
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
        """从UI构建申办参数"""
        try:
            # 收集表单数据
            form_data = {}
            
            # 根据当前车辆类型收集表单数据
            current_vehicle_type = getattr(ui, 'current_vehicle_type', 'passenger')
            
            if current_vehicle_type == 'passenger':
                # 客车使用通用字段名
                passenger_fields = {
                    'name': 'name',
                    'id_code': 'id_code',
                    'phone': 'phone',
                    'bank_no': 'bank_no',
                    'bank_name': 'bank_name'
                }
                
                # 收集客车表单数据
                for ui_field, param_field in passenger_fields.items():
                    if ui_field in ui.inputs:
                        widget = ui.inputs[ui_field]
                        if hasattr(widget, 'text'):
                            value = widget.text().strip()
                            if value:  # 只添加非空值
                                form_data[param_field] = value
                
                # 添加客车选择的产品信息
                if hasattr(ui, 'selected_product') and ui.selected_product:
                    form_data['selected_product'] = ui.selected_product
                    # 如果产品包含运营商信息，也添加到参数中
                    operator_name = ui.selected_product.get('operator_name') or ui.selected_product.get('OPERATOR_NAME')
                    operator_code = ui.selected_product.get('operator_code') or ui.selected_product.get('OPERATOR_CODE')
                    
                    if operator_name:
                        form_data['operatorName'] = operator_name
                        print(f"[INFO] 客车参数中添加运营商名称: {operator_name}")
                    
                    if operator_code:
                        form_data['operatorCode'] = operator_code
                        print(f"[INFO] 客车参数中添加运营商编码: {operator_code}")
            else:
                # 货车使用货车专用字段名
                truck_fields = {
                    'truck_name': 'name',
                    'truck_id_code': 'id_code',
                    'truck_phone': 'phone',
                    'truck_bank_no': 'bank_no',
                    'truck_bank_name': 'bank_name'
                }
                
                # 收集货车表单数据
                for ui_field, param_field in truck_fields.items():
                    if ui_field in ui.inputs:
                        widget = ui.inputs[ui_field]
                        if hasattr(widget, 'text'):
                            value = widget.text().strip()
                            if value:  # 只添加非空值
                                form_data[param_field] = value
            
            # 根据当前车辆类型收集车牌信息
            current_vehicle_type = getattr(ui, 'current_vehicle_type', 'passenger')
            
            if current_vehicle_type == 'passenger':
                # 客车车牌字段名
                province_widget = getattr(ui, 'plate_province_edit', None)
                letter_widget = getattr(ui, 'plate_letter_edit', None)
                number_widget = getattr(ui, 'plate_number_edit', None)
                color_widget = getattr(ui, 'plate_color_combo', None)
            else:
                # 货车车牌字段名
                province_widget = getattr(ui, 'truck_plate_province_edit', None)
                letter_widget = getattr(ui, 'truck_plate_letter_edit', None)
                number_widget = getattr(ui, 'truck_plate_number_edit', None)
                color_widget = getattr(ui, 'truck_plate_color_combo', None)
            
            # 收集车牌信息
            if province_widget and letter_widget and number_widget:
                province = province_widget.text().strip()
                letter = letter_widget.text().strip()
                number = number_widget.text().strip()
                if province and letter and number:
                    form_data['car_num'] = province + letter + number
                    form_data['plate_province'] = province
                    form_data['plate_letter'] = letter
                    form_data['plate_number'] = number
            
            # 收集车牌颜色
            if color_widget:
                if hasattr(color_widget, 'currentText'):
                    form_data['vehicle_color'] = color_widget.currentText()
                else:
                    form_data['vehicle_color'] = color_widget.text().strip()
            
            # 添加VIN码
            if current_vehicle_type == 'passenger':
                vin_widget = getattr(ui, 'vin_edit', None)
            else:
                vin_widget = getattr(ui, 'truck_vin_edit', None)
            
            if vin_widget and hasattr(vin_widget, 'text'):
                vin = vin_widget.text().strip()
                if vin:
                    form_data['vin'] = vin
            
            # 货车专用字段收集
            if current_vehicle_type == 'truck':
                truck_specific_fields = [
                    'model', 'car_type', 'register_date', 'issue_date', 'engine_no',
                    'vehicle_axles', 'vehicle_wheels', 'total_mass', 'unladen_mass',
                    'approved_count', 'weight_limits', 'length', 'width', 'height',
                    'urgent_contact', 'urgent_phone', 'effective_date', 'id_authority', 'id_address'
                ]
                
                for field_name in truck_specific_fields:
                    if field_name in ui.inputs:
                        widget = ui.inputs[field_name]
                        if hasattr(widget, 'text'):
                            value = widget.text().strip()
                            if value:
                                form_data[field_name] = value
                        elif hasattr(widget, 'currentText'):
                            value = widget.currentText().strip()
                            if value:
                                form_data[field_name] = value
            
            # 添加车辆类型标识
            form_data['vehicle_type'] = current_vehicle_type
            
            # 构建申办参数
            return DataService.build_apply_params(form_data)
            
        except Exception as e:
            raise Exception(f"从UI构建申办参数失败: {str(e)}")
    
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
            'bindBankName': form_data.get('bank_name', ''),  # 添加银行名称
        })
        
        # 车辆信息
        params.update({
            'carNum': DataService._build_car_num(form_data),
            'vehicleColor': form_data.get('vehicle_color', '蓝色'),
            'vin': form_data.get('vin', ''),
        })
        
        # 货车专用参数
        vehicle_type = form_data.get('vehicle_type', '')
        if vehicle_type == 'truck' or vehicle_type == '货车':
            params.update({
                'vehicleAxles': form_data.get('vehicle_axles', '2'),
                'vehicleWheels': form_data.get('vehicle_wheels', '4'),
                'totalMass': form_data.get('total_mass', '18000'),
                'unladenMass': form_data.get('unladen_mass', '7500'),
                'model': form_data.get('model', 'EQ1180GZ5DJ1'),
                'carType': form_data.get('car_type', '货车'),
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
        vehicle_type = form_data.get('vehicle_type', '')
        if vehicle_type == 'truck' or vehicle_type == '货车':
            # 货车需要更多必需参数
            CoreService.validate_required_params(params, [
                'carNum', 'cardHolder', 'idCode', 'bindBankPhone', 'bindBankNo', 
                'vin', 'vehicleAxles', 'vehicleWheels', 'totalMass', 'unladenMass', 
                'model', 'carType'
            ])
        else:
            # 客车基础参数验证
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