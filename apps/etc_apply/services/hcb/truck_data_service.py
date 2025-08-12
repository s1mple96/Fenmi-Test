# -*- coding: utf-8 -*-
"""
货车数据服务 - 整合数据库操作和参数处理
"""
import random
import uuid
from datetime import datetime
from typing import Dict, Any
from common.mysql_util import MySQLUtil
from apps.etc_apply.services.hcb.truck_core_service import TruckCoreService


class TruckDataService:
    """货车数据服务 - 整合数据库操作和参数处理"""
    
    # ==================== 数据库操作 ====================
    
    @staticmethod
    def update_truck_apply_status(truck_etc_apply_id: str) -> None:
        """更新货车申请表状态"""
        try:
            conf = TruckCoreService.get_hcb_mysql_config()
            db = MySQLUtil(**conf)
            db.connect()
            sql = "UPDATE hcb.hcb_trucketcapply t SET t.ETCSTATUS = '11' WHERE t.TRUCKETCAPPLY_ID = %s"
            db.execute(sql, (truck_etc_apply_id,))
            db.close()
        except Exception as e:
            error_msg = TruckCoreService.format_database_error("更新货车申请表状态", e)
            raise Exception(error_msg)
    
    @staticmethod
    def update_truck_user_status(car_num: str) -> None:
        """更新货车用户状态"""
        try:
            conf = TruckCoreService.get_hcb_mysql_config()
            db = MySQLUtil(**conf)
            db.connect()
            sql = """
            UPDATE hcb.hcb_truckuser t 
            SET t.STATUS = '1', t.ETCSTATUS = '1', t.ACTIVATION_TIME = NOW() 
            WHERE t.CAR_NUM = %s
            """
            db.execute(sql, (car_num,))
            db.close()
        except Exception as e:
            error_msg = TruckCoreService.format_database_error("更新货车用户状态", e)
            raise Exception(error_msg)
    
    @staticmethod
    def update_truck_user_obu_info(car_num: str, obu_no: str, etc_sn: str) -> None:
        """更新货车用户OBU信息"""
        try:
            conf = TruckCoreService.get_hcb_mysql_config()
            db = MySQLUtil(**conf)
            db.connect()
            sql = """
            UPDATE hcb.hcb_truckuser t 
            SET t.ETC_SN = %s, t.OBU_NO = %s, t.ACTIVATION_TIME = NOW() 
            WHERE t.CAR_NUM = %s
            """
            db.execute(sql, (etc_sn, obu_no, car_num))
            db.close()
        except Exception as e:
            error_msg = TruckCoreService.format_database_error("更新货车用户OBU信息", e)
            raise Exception(error_msg)
    
    @staticmethod
    def generate_etc_sn(car_num: str = None) -> str:
        """生成ETC号（参考客车rtx方式）"""
        try:
            # 从车牌号获取省份
            province_abbr = car_num[0] if car_num and len(car_num) > 0 else "苏"
            
            # 省份简称到代码的映射（与DataFactory保持一致）
            province_prefix = {
                '京': '1100', '津': '1200', '沪': '3100', '渝': '5000',
                '冀': '1300', '豫': '4100', '云': '5300', '辽': '2100', '黑': '2300',
                '湘': '4300', '皖': '3400', '鲁': '3700', '新': '6500', '苏': '3200',
                '浙': '3300', '赣': '3600', '鄂': '4200', '桂': '4500', '甘': '6200',
                '晋': '1400', '蒙': '1500', '陕': '6100', '吉': '2200', '闽': '3500',
                '贵': '5200', '青': '6300', '藏': '5400', '川': '5100', '宁': '6400', 
                '琼': '4600', '粤': '4400'
            }
            
            # 获取省份代码
            prefix = province_prefix.get(province_abbr, '3200')  # 默认苏州
            
            # ETC号总长度20位，省份代码4位，剩余16位随机数字
            etc_length = 20
            remain = etc_length - len(prefix)
            suffix = ''.join([str(random.randint(0, 9)) for _ in range(remain)])
            
            return prefix + suffix
            
        except Exception as e:
            # 异常时使用默认苏州代码
            prefix = '3200'
            suffix = ''.join([str(random.randint(0, 9)) for _ in range(16)])
            return prefix + suffix
    
    @staticmethod
    def generate_obu_no(car_num: str = None) -> str:
        """生成OBU号（参考客车rtx方式）"""
        try:
            # 从车牌号获取省份
            province_abbr = car_num[0] if car_num and len(car_num) > 0 else "苏"
            
            # 省份简称到代码的映射（与DataFactory保持一致）
            province_prefix = {
                '京': '1100', '津': '1200', '沪': '3100', '渝': '5000',
                '冀': '1300', '豫': '4100', '云': '5300', '辽': '2100', '黑': '2300',
                '湘': '4300', '皖': '3400', '鲁': '3700', '新': '6500', '苏': '3200',
                '浙': '3300', '赣': '3600', '鄂': '4200', '桂': '4500', '甘': '6200',
                '晋': '1400', '蒙': '1500', '陕': '6100', '吉': '2200', '闽': '3500',
                '贵': '5200', '青': '6300', '藏': '5400', '川': '5100', '宁': '6400', 
                '琼': '4600', '粤': '4400'
            }
            
            # 获取省份代码
            prefix = province_prefix.get(province_abbr, '3200')  # 默认苏州
            
            # OBU号总长度16位，省份代码4位，剩余12位随机数字
            obu_length = 16
            remain = obu_length - len(prefix)
            suffix = ''.join([str(random.randint(0, 9)) for _ in range(remain)])
            
            return prefix + suffix
            
        except Exception as e:
            # 异常时使用默认苏州代码
            prefix = '3200'
            suffix = ''.join([str(random.randint(0, 9)) for _ in range(12)])
            return prefix + suffix
    
    @staticmethod
    def update_truck_user_final_status(car_num: str) -> None:
        """更新货车用户最终状态（包含ETC号和OBU号）"""
        try:
            # 生成ETC号和OBU号
            etc_sn = TruckDataService.generate_etc_sn(car_num)
            obu_no = TruckDataService.generate_obu_no(car_num)
            
            # 更新数据库
            TruckDataService.update_truck_user_obu_info(car_num, obu_no, etc_sn)
            TruckDataService.update_truck_user_status(car_num)
            
            return {
                'etc_sn': etc_sn,
                'obu_no': obu_no,
                'activation_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        except Exception as e:
            error_msg = TruckCoreService.format_database_error("更新货车用户最终状态", e)
            raise Exception(error_msg)
    
    @staticmethod
    def close_mock_data() -> bool:
        """关闭Mock数据配置（货车版本）- 使用客车系统的rtx.sys_config表"""
        try:
            # 使用客车系统的rtx数据库配置
            from apps.etc_apply.services.rtx.core_service import CoreService
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
            print("货车Mock数据已关闭（使用rtx.sys_config表）")
            return True
        except Exception as e:
            print(f"关闭货车Mock数据失败: {str(e)}")
            return False
    
    @staticmethod
    def enable_mock_data() -> bool:
        """启用Mock数据配置（货车版本）- 使用客车系统的rtx.sys_config表"""
        try:
            # 使用客车系统的rtx数据库配置
            from apps.etc_apply.services.rtx.core_service import CoreService
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
            print("货车Mock数据已启用（使用rtx.sys_config表）")
            return True
        except Exception as e:
            print(f"启用货车Mock数据失败: {str(e)}")
            return False
    
    @staticmethod
    def insert_bind_car_rel(userinfo_id: str, truckuser_id: str) -> None:
        """插入用户绑定车辆关系记录"""
        try:
            import uuid
            from datetime import datetime
            
            conf = TruckCoreService.get_hcb_mysql_config()
            db = MySQLUtil(**conf)
            db.connect()
            
            # 生成绑定关系ID
            bindcarrel_id = str(uuid.uuid4()).replace('-', '')
            # 当前时间
            create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            sql = """
            INSERT INTO hcb.hcb_bindcarrel 
            (BINDCARREL_ID, USERINFO_ID, TRUCKUSER_ID, CREATE_TIME, FLAG) 
            VALUES (%s, %s, %s, %s, '1')
            """
            db.execute(sql, (bindcarrel_id, userinfo_id, truckuser_id, create_time))
            db.close()
            
            return {
                'bindcarrel_id': bindcarrel_id,
                'userinfo_id': userinfo_id,
                'truckuser_id': truckuser_id,
                'create_time': create_time
            }
        except Exception as e:
            error_msg = TruckCoreService.format_database_error("插入用户绑定车辆关系", e)
            raise Exception(error_msg)
    
    @staticmethod
    def truncate_user_id(user_id: str, max_length: int = 32) -> str:
        """处理用户ID以适应数据库字段长度"""
        if not user_id:
            return ""
        
        # 清理ID，移除空格和特殊字符
        cleaned_id = user_id.strip()
        
        # 如果ID长度超过限制，截断
        if len(cleaned_id) > max_length:
            # 使用前max_length位
            return cleaned_id[:max_length]
        
        return cleaned_id
    
    @staticmethod
    def manual_bind_user_vehicle(phone: str, openid: str, id_code: str, truck_user_id: str, truck_etc_apply_id: str, car_num: str) -> dict:
        """手动绑定用户车辆 - 优先使用手机号查询"""
        try:
            import uuid
            from datetime import datetime
            from apps.etc_apply.services.hcb.truck_core_service import TruckCoreService
            from common.mysql_util import MySQLUtil
            
            conf = TruckCoreService.get_hcb_mysql_config()
            db = MySQLUtil(**conf)
            db.connect()
            
            # 1. 优先通过手机号查找用户
            user_id = None
            if phone:
                # 查询用户信息表
                sql_phone = """
                SELECT USER_ID FROM hcb.hcb_userinfo 
                WHERE PHONE = %s AND FLAG = '1' 
                ORDER BY CREATE_TIME DESC LIMIT 1
                """
                result = db.query_one(sql_phone, (phone,))
                if result:
                    user_id = result[0]
                    print(f"✅ 通过手机号找到用户ID: {user_id}")
            
            # 2. 如果通过手机号找不到，尝试通过身份证查找
            if not user_id and id_code:
                sql_idcard = """
                SELECT USER_ID FROM hcb.hcb_userinfo 
                WHERE ID_CODE = %s AND FLAG = '1'
                ORDER BY CREATE_TIME DESC LIMIT 1
                """
                result = db.query_one(sql_idcard, (id_code,))
                if result:
                    user_id = result[0]
                    print(f"✅ 通过身份证找到用户ID: {user_id}")
            
            # 3. 通过openId查询用户信息（第三优先级）
            if not user_id and openid and openid != 'oDefaultTestOpenId12345':
                try:
                    sql_openid = """
                    SELECT USER_ID FROM hcb.hcb_userinfo 
                    WHERE OPEN_ID = %s AND FLAG = '1' 
                    ORDER BY CREATE_TIME DESC LIMIT 1
                    """
                    result = db.query_one(sql_openid, (openid,))
                    if result:
                        user_id = result[0]
                        print(f"✅ 通过openId找到用户ID: {user_id}")
                except Exception as e:
                    print(f"⚠️ 通过openId查询用户失败: {e}")
            
            # 4. 如果都找不到，使用标识作为用户ID
            if not user_id:
                if phone:
                    user_id = f"phone_{phone}"[:32]
                    print(f"⚠️ 使用手机号作为用户标识: {user_id}")
                elif openid:
                    user_id = f"wx_{openid}"[:32]
                    print(f"⚠️ 使用openId作为用户标识: {user_id}")
                else:
                    user_id = f"id_{id_code}"[:32]
                    print(f"⚠️ 使用身份证作为用户标识: {user_id}")
            
            # 5. 检查是否已经绑定
            check_sql = """
            SELECT BINDCARREL_ID FROM hcb.hcb_bindcarrel 
            WHERE USERINFO_ID = %s AND TRUCKUSER_ID = %s AND FLAG = '1'
            """
            existing = db.query_one(check_sql, (user_id, truck_user_id))
            if existing:
                db.close()
                return {
                    'success': False,
                    'message': '用户车辆已经绑定',
                    'bindcarrel_id': existing[0],
                    'userinfo_id': user_id,
                    'truckuser_id': truck_user_id
                }
            
            # 6. 执行绑定
            bindcarrel_id = str(uuid.uuid4()).replace('-', '')
            create_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            sql_bind = """
            INSERT INTO hcb.hcb_bindcarrel 
            (BINDCARREL_ID, USERINFO_ID, TRUCKUSER_ID, CREATE_TIME, FLAG) 
            VALUES (%s, %s, %s, %s, '1')
            """
            db.execute(sql_bind, (bindcarrel_id, user_id, truck_user_id, create_time))
            db.close()
            
            return {
                'success': True,
                'message': '车辆绑定成功',
                'bindcarrel_id': bindcarrel_id,
                'userinfo_id': user_id,
                'truckuser_id': truck_user_id,
                'truck_etc_apply_id': truck_etc_apply_id,
                'car_num': car_num,
                'create_time': create_time
            }
            
        except Exception as e:
            error_msg = TruckCoreService.format_database_error("手动绑定用户车辆", e)
            return {
                'success': False,
                'message': error_msg,
                'error': str(e)
            }
    
    @staticmethod
    def insert_truck_user_extends(truck_user_id: str, truck_etc_apply_id: str, params: Dict[str, Any]) -> str:
        """插入货车用户扩展信息到HCB_TRUCKUSEREXTENDS表（设备和运营商相关信息）"""
        try:
            import uuid
            from datetime import datetime
            
            conf = TruckCoreService.get_hcb_mysql_config()
            db = MySQLUtil(**conf)
            db.connect()
            
            # 生成扩展信息ID
            truckuser_extends_id = str(uuid.uuid4()).replace('-', '')
            
            # 根据实际表结构插入数据
            sql = """
            INSERT INTO hcb.hcb_truckuserextends 
            (TRUCKUSEREXTENDS_ID, TRUCKUSER_ID, twice_active_count, freeze_active_count, 
             total_active_count, DEVICE_USABLE, DEVICE_CATEGORY, NEGATIVE_BLACK, 
             OPERATOR_STA, STA_SAME, BILL_TIME_EXCE, DEVICE_KEY, normal_status) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # 设置默认值，符合货车ETC的业务逻辑
            db.execute(sql, (
                truckuser_extends_id,      # TRUCKUSEREXTENDS_ID
                truck_user_id,             # TRUCKUSER_ID
                5,                         # twice_active_count: 剩余二次激活次数，默认5次
                0,                         # freeze_active_count: 冻结二次激活次数，默认0
                0,                         # total_active_count: 累计使用激活次数，默认0
                '1',                       # DEVICE_USABLE: 设备适用类型，1-货车专用
                '0',                       # DEVICE_CATEGORY: 设备类别，0-普通设备
                '0',                       # NEGATIVE_BLACK: 一键余额负数下黑标识，默认0
                '正常',                    # OPERATOR_STA: 运营商状态，默认正常
                '1',                       # STA_SAME: 状态是否相同，默认1相同
                '0',                       # BILL_TIME_EXCE: 账单时间异常，默认0正常
                0,                         # DEVICE_KEY: 设备密钥，默认0(3DES)
                '1'                        # normal_status: 正常状态，默认1
            ))
            
            db.close()
            
            return truckuser_extends_id
            
        except Exception as e:
            error_msg = TruckCoreService.format_database_error("插入货车用户扩展信息", e)
            raise Exception(error_msg)
    
    @staticmethod
    def insert_truck_device_stock(car_num: str, etc_sn: str, obu_no: str, operator_id: str = None, operator_name: str = None) -> Dict[str, str]:
        """插入货车设备库存数据到hcb_newstock表"""
        try:
            import uuid
            from datetime import datetime
            from apps.etc_apply.services.rtx.core_service import CoreService
            
            conf = TruckCoreService.get_hcb_mysql_config()
            db = MySQLUtil(**conf)
            db.connect()
            
            # 根据运营商名称或ID获取设备运营商代码
            if operator_name:
                # 优先使用运营商名称进行模糊匹配
                operator_codes = CoreService.get_device_operator_codes_by_operator_name(operator_name)
                print(f"[INFO] 货车使用运营商名称进行匹配: {operator_name}")
            elif operator_id:
                # 兼容原有的ID方式
                operator_codes = CoreService.get_device_operator_codes_by_product(operator_id)
                print(f"[INFO] 货车使用运营商ID进行匹配: {operator_id}")
            else:
                # 使用默认值
                operator_codes = {'obu_code': '1', 'etc_code': '10'}
                print(f"[INFO] 货车使用默认运营商代码")
            
            # 准备基础数据
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            base_data = {
                "STATUS": "1",                # 状态
                "CAR_NUM": car_num,           # 车牌号
                "STOCK_STATUS": "0",          # 库存状态
                "SOURCE": "1",                # 来源
                "REMARK": "激活设备不存在库存内", # 备注
                "CREATE_TIME": now,           # 创建时间
                "DEVICE_CATEGORY": "0"        # 设备类别
            }
            
            # OBU设备数据 (TYPE=0) - 使用OBU运营商代码
            obu_data = base_data.copy()
            obu_data.update({
                "NEWSTOCK_ID": uuid.uuid4().hex,
                "INTERNAL_DEVICE_NO": obu_no,
                "EXTERNAL_DEVICE_NO": obu_no,
                "TYPE": "0",  # 0表示OBU
                "CARD_OPERATORS": operator_codes['obu_code']  # 🔥 OBU使用对应运营商代码
            })
            
            # ETC设备数据 (TYPE=1) - 使用ETC运营商代码
            etc_data = base_data.copy()
            etc_data.update({
                "NEWSTOCK_ID": uuid.uuid4().hex,
                "INTERNAL_DEVICE_NO": etc_sn,
                "EXTERNAL_DEVICE_NO": etc_sn,
                "TYPE": "1",  # 1表示ETC
                "CARD_OPERATORS": operator_codes['etc_code']  # 🔥 ETC使用对应运营商代码
            })
            
            # 插入数据库
            def insert_row(row):
                keys = ','.join(f'`{k}`' for k in row.keys())
                vals = ','.join(['%s'] * len(row))
                sql = f"INSERT INTO hcb.hcb_newstock ({keys}) VALUES ({vals})"
                db.execute(sql, tuple(row.values()))
            
            insert_row(obu_data)
            insert_row(etc_data)
            db.close()
            
            operator_info = operator_name or operator_id or "默认"
            print(f"✅ 货车设备入库成功:")
            print(f"   - 车牌号: {car_num}")
            print(f"   - 运营商: {operator_info}")
            print(f"   - OBU号: {obu_no} (运营商代码: {operator_codes['obu_code']})")
            print(f"   - ETC号: {etc_sn} (运营商代码: {operator_codes['etc_code']})")
            
            return {
                'car_num': car_num,
                'obu_no': obu_no,
                'etc_sn': etc_sn,
                'obu_stock_id': obu_data['NEWSTOCK_ID'],
                'etc_stock_id': etc_data['NEWSTOCK_ID'],
                'obu_operator_code': operator_codes['obu_code'],
                'etc_operator_code': operator_codes['etc_code'],
                'operator_info': operator_info
            }
            
        except Exception as e:
            error_msg = TruckCoreService.format_database_error("插入货车设备库存", e)
            raise Exception(error_msg)
    
    # ==================== 参数处理 ====================
    
    @staticmethod
    def validate_and_complete_truck_params(params: Dict[str, Any]) -> Dict[str, Any]:
        """验证并完善货车参数"""
        # 验证货车专用参数
        TruckDataService._validate_truck_params(params)
        
        # 车牌颜色映射（货车通常是黄色）
        vc = params.get('plateColor', '1')
        if isinstance(vc, str) and vc in ["蓝色", "黄色", "绿色", "白色", "黑色"]:
            from apps.etc_apply.services.rtx.core_service import CoreService
            params['plateColor'] = CoreService.get_vehicle_color_code(vc)
        else:
            try:
                params['plateColor'] = int(vc)
            except Exception:
                params['plateColor'] = 1  # 默认黄色（货车）
        
        # 补全货车默认参数
        truck_defaults = TruckDataService._get_truck_defaults()
        for key, value in truck_defaults.items():
            if key not in params or not params[key]:
                params[key] = value
        
        return params
    
    @staticmethod
    def _validate_truck_params(params):
        """验证货车专用参数"""
        from apps.etc_apply.services.rtx.core_service import CoreService
        
        required_fields = [
            'cardHolder',     # 持卡人
            'idCode',         # 身份证号
            'phone',          # 手机号
            'carNum',         # 车牌号
            'bankName',       # 银行名称
            'bankNo',         # 银行卡号
            'vin',            # VIN码
            'vehicleAxles',   # 车轴数
            'vehicleWheels',  # 车轮数
            'totalMass',      # 总质量
            'unladenMass',    # 整备质量
            'model',          # 车辆型号
            'carType'         # 车辆类型
        ]
        
        missing_fields = [field for field in required_fields if not params.get(field)]
        if missing_fields:
            raise ValueError(f"缺少必需的货车参数: {', '.join(missing_fields)}")
        
        # 验证各字段格式
        if not CoreService.validate_car_num(params.get('carNum', '')):
            raise ValueError(f"车牌号格式错误: {params.get('carNum')}")
        
        if not CoreService.validate_id_code(params.get('idCode', '')):
            raise ValueError(f"身份证号格式错误: {params.get('idCode')}")
        
        if not CoreService.validate_phone(params.get('phone', '')):
            raise ValueError(f"手机号格式错误: {params.get('phone')}")
        
        if not CoreService.validate_bank_card(params.get('bankNo', '')):
            raise ValueError(f"银行卡号格式错误: {params.get('bankNo')}")
        
        if not CoreService.validate_vin(params.get('vin', '')):
            raise ValueError(f"VIN码格式错误: {params.get('vin')}")
    
    @staticmethod
    def _get_truck_defaults():
        """获取货车默认参数"""
        return {
            'plateColor': '1',  # 黄色（货车）
            'channelId': '0000',
            'operatorId': '717830e1c3a948709ec0a92b44400c60',
            'isCompany': '0',
            'obuSubmitStatus': '1',
            'ethnic': '汉',
            'usePurpose': '货运',
            'agreeType': 'S',
            'payType': '0'
        }
    
    @staticmethod
    def _build_truck_params(form_data, ui=None):
        """构建货车申办参数"""
        from apps.etc_apply.services.rtx.core_service import CoreService
        
        params = {}
        
        # 货车专用字段映射
        params.update({
            'cardHolder': form_data.get('truck_name', ''),  # 货车专用字段
            'idCode': form_data.get('truck_id_code', ''),   # 货车专用字段
            'phone': form_data.get('truck_phone', ''),      # 货车专用字段
            'mobileNo': form_data.get('truck_phone', ''),   # 货车专用字段
            'bankNo': form_data.get('truck_bank_no', ''),   # 货车专用字段
            'bankName': form_data.get('truck_bank_name', ''), # 货车专用字段
            # 同时设置truck_bank_name字段，确保在步骤12中能正确获取
            'truck_bank_name': form_data.get('truck_bank_name', ''),
        })
        
        # 获取货车默认值
        truck_defaults = TruckDataService.get_truck_default_values()
        
        # 车辆信息
        params.update({
            'carNum': TruckDataService._build_car_num(form_data),
            'plateColor': form_data.get('plate_color', '1'),
            'vin': form_data.get('vin', ''),
            'vehicleAxles': form_data.get('vehicle_axles', '2'),  # 默认2轴
            'vehicleWheels': form_data.get('vehicle_wheels', '6'),  # 默认6轮
            'totalMass': form_data.get('total_mass', truck_defaults.get('total_mass', '18000')),
            'unladenMass': form_data.get('unladen_mass', truck_defaults.get('unladen_mass', '7500')),
            'model': form_data.get('model', truck_defaults.get('model', 'EQ1180GZ5DJ1')),
            'carType': form_data.get('car_type', '货车'),
            'registerDate': form_data.get('register_date', truck_defaults.get('register_date', '20200515')),
            'issueDate': form_data.get('issue_date', truck_defaults.get('issue_date', '20200520')),
            'vehicleEngineno': form_data.get('engine_no', truck_defaults.get('engine_no', '4DX23-140E5A')),
            'approvedCount': form_data.get('approved_count', '3'),  # 默认3人
            'weightLimits': form_data.get('weight_limits', truck_defaults.get('weight_limits', '10500')),
            'usePurpose': form_data.get('use_purpose', '货运'),
            'long': form_data.get('length', truck_defaults.get('length', '8995')),
            'width': form_data.get('width', truck_defaults.get('width', '2496')),
            'height': form_data.get('height', truck_defaults.get('height', '3800')),
        })
        
        # 产品信息
        business_config = CoreService.get_business_config()
        if hasattr(ui, 'selected_truck_product') and ui.selected_truck_product:
            # 使用UI中选择的货车产品
            selected_product = ui.selected_truck_product
            params['productId'] = selected_product.get('ETCBANK_ID', '')
            params['bankCode'] = selected_product.get('BANK_CODE', '')
            params['bankName'] = selected_product.get('NAME', '')
            # 使用选择的运营商ID
            operator_id = selected_product.get('OPERATOR_ID', '717830e1c3a948709ec0a92b44400c60')
            params['operatorId'] = operator_id
            print(f"使用选择的货车产品: {selected_product.get('NAME')} (ID: {selected_product.get('ETCBANK_ID')}, 运营商: {operator_id})")
        elif 'selected_product' in form_data and form_data['selected_product']:
            product = form_data['selected_product']
            # 处理货车产品数据结构 - 优先使用ETCBANK_ID，兼容product_id
            product_id = product.get('ETCBANK_ID') or product.get('product_id')
            params['productId'] = product_id
            params['bankCode'] = product.get('BANK_CODE', '')
            params['bankName'] = product.get('NAME', '')
            # 使用选择的运营商ID
            operator_id = product.get('OPERATOR_ID', '717830e1c3a948709ec0a92b44400c60')
            params['operatorId'] = operator_id
            print(f"使用表单中的货车产品: {product.get('NAME')} (ID: {product_id}, 运营商: {operator_id})")
        else:
            params['productId'] = business_config.get('default_product_id', '0bcc3075edef4151a9a2bff052607a24')
            params['operatorId'] = '717830e1c3a948709ec0a92b44400c60'  # 默认苏通卡运营商
        
        # 填充默认参数
        params.update({
            'channelId': '0000',
            'isCompany': '0',
            'obuSubmitStatus': '1',
            'ethnic': '汉',
            'urgentContact': form_data.get('urgent_contact', '张三'),
            'urgentPhone': form_data.get('urgent_phone', '13800138000'),
            'effectiveDate': form_data.get('effective_date', '20200101-20300101'),
            'idAuthority': form_data.get('id_authority', 'XX市公安局'),
            'idAddress': form_data.get('id_address', ''),
            'openId': form_data.get('open_id', 'oDefaultTestOpenId12345'),
            'verifyCode': form_data.get('verify_code', ''),  # 让TruckCore动态生成验证码
        })
        
        return params
    
    @staticmethod
    def _build_car_num(form_data):
        """构建车牌号"""
        from apps.etc_apply.services.rtx.core_service import CoreService
        province = form_data.get('plate_province', '')
        letter = form_data.get('plate_letter', '')
        number = form_data.get('plate_number', '')
        return CoreService.build_car_num(province, letter, number)
    
    @staticmethod
    def get_truck_default_values():
        """获取货车表单的默认值"""
        return {
            'model': 'EQ1180GZ5DJ1',
            'register_date': '20200515',  # 修改为YYYYMMDD格式
            'issue_date': '20200520',     # 修改为YYYYMMDD格式
            'engine_no': '4DX23-140E5A',
            'total_mass': '18000',
            'unladen_mass': '7500',
            'weight_limits': '10500',
            'length': '8995',
            'width': '2496',
            'height': '3800',
            'id_address': '广东省深圳市龙岗区双子塔F座'
        } 