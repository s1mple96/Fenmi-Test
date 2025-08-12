# -*- coding: utf-8 -*-
"""
核心服务 - 整合配置、验证、错误处理等基础功能
"""
import json
import os
import re
import traceback
from typing import Dict, Any, List, Tuple, Optional
from datetime import datetime


class CoreService:
    """核心服务 - 整合基础功能"""
    
    # ==================== 配置管理 ====================
    
    _etc_config_cache = None
    
    @staticmethod
    def _load_etc_config() -> Dict[str, Any]:
        """加载ETC配置文件"""
        if CoreService._etc_config_cache is None:
            config_path = CoreService.get_config_path('etc_config.json')
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    CoreService._etc_config_cache = json.load(f)
            except Exception as e:
                print(f"读取ETC配置文件失败: {e}")
                CoreService._etc_config_cache = {}
        return CoreService._etc_config_cache
    
    @staticmethod
    def get_config_path(filename: str) -> str:
        """获取配置文件路径"""
        # 获取当前文件所在目录 (apps/etc_apply/services/rtx)
        current_dir = os.path.dirname(__file__)
        
        # 向上两级到 apps/etc_apply
        etc_apply_dir = os.path.dirname(os.path.dirname(current_dir))
        
        # 构建config目录路径
        etc_config_dir = os.path.join(etc_apply_dir, 'config')
        etc_config_path = os.path.join(etc_config_dir, filename)
        
        if os.path.exists(etc_config_path):
            return etc_config_path
        
        # 如果不存在，则从项目根目录的 config 目录加载（向后兼容）
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        fallback_path = os.path.join(base_dir, 'config', filename)
        
        return fallback_path
    
    @staticmethod
    def get_api_base_url() -> str:
        """获取API基础URL"""
        config = CoreService._load_etc_config()
        return config.get('api', {}).get('base_url', 'http://788360p9o5.yicp.fun')
    
    @staticmethod
    def get_browser_cookies() -> dict:
        """获取浏览器cookies"""
        config = CoreService._load_etc_config()
        return config.get('browser_cookies', {})
    
    @staticmethod
    def get_mysql_config(database: str = 'hcb') -> Dict[str, Any]:
        """获取MySQL连接配置"""
        config = CoreService._load_etc_config()
        db_config = config.get('database', {}).get(database, {})
        mysql_config = {
            'host': db_config.get('host', 'localhost'),
            'port': db_config.get('port', 3306),
            'user': db_config.get('username', 'root'),
            'password': db_config.get('password', 'password'),
            'database': database,
        }
        return mysql_config
    
    @staticmethod
    def get_rtx_mysql_config() -> Dict[str, Any]:
        """获取RTX数据库配置"""
        return CoreService.get_mysql_config('rtx')
    
    @staticmethod
    def get_hcb_mysql_config() -> Dict[str, Any]:
        """获取HCB数据库配置"""
        return CoreService.get_mysql_config('hcb')
    
    @staticmethod
    def get_business_config() -> Dict[str, Any]:
        """获取业务配置"""
        config = CoreService._load_etc_config()
        return config.get('business', {})
    
    @staticmethod
    def get_ui_config() -> Dict[str, Any]:
        """获取UI配置"""
        config = CoreService._load_etc_config()
        return config.get('ui', {})
    
    @staticmethod
    def get_validation_config() -> Dict[str, Any]:
        """获取验证配置"""
        config = CoreService._load_etc_config()
        return config.get('validation', {})
    
    @staticmethod
    def get_device_config() -> Dict[str, Any]:
        """获取设备配置"""
        config = CoreService._load_etc_config()
        return config.get('device', {})
    
    @staticmethod
    def get_vehicle_colors() -> Dict[str, int]:
        """获取车辆颜色映射"""
        config = CoreService._load_etc_config()
        return config.get('vehicle_colors', {})
    
    @staticmethod
    def get_default_params() -> Dict[str, Any]:
        """获取默认参数"""
        config = CoreService._load_etc_config()
        default_params = config.get('default_params', {})
        return default_params
    
    @staticmethod
    def get_steps_config() -> Dict[str, Any]:
        """获取步骤配置"""
        config = CoreService._load_etc_config()
        return config.get('steps', {})
    
    # ==================== 参数验证 ====================
    
    @staticmethod
    def validate_car_num(car_num: str) -> bool:
        """验证车牌号格式"""
        if not car_num or len(car_num) < 6:
            return False
        
        validation_config = CoreService.get_validation_config()
        pattern = validation_config.get('car_number_pattern', r'^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵青藏川宁琼粤港澳台][A-Z][A-Z0-9]{5}$')
        return bool(re.match(pattern, car_num))
    
    @staticmethod
    def validate_id_code(id_code: str) -> bool:
        """验证身份证号格式"""
        if not id_code or len(id_code) != 18:
            return False
        
        validation_config = CoreService.get_validation_config()
        pattern = validation_config.get('id_code_pattern', r'^\d{17}[\dXx]$')
        return bool(re.match(pattern, id_code))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """验证手机号格式"""
        if not phone or len(phone) != 11 or not phone.isdigit() or not phone.startswith('1'):
            return False
        
        validation_config = CoreService.get_validation_config()
        pattern = validation_config.get('phone_pattern', r'^1[3-9]\d{9}$')
        return bool(re.match(pattern, phone))
    
    @staticmethod
    def validate_bank_card(bank_card: str) -> bool:
        """验证银行卡号格式"""
        if not bank_card or not bank_card.isdigit() or len(bank_card) < 13 or len(bank_card) > 19:
            return False
        
        validation_config = CoreService.get_validation_config()
        pattern = validation_config.get('bank_card_pattern', r'^\d{13,19}$')
        return bool(re.match(pattern, bank_card))
    
    @staticmethod
    def validate_vin(vin: str) -> bool:
        """验证VIN码格式"""
        if not vin:
            return True  # VIN码可选
        
        validation_config = CoreService.get_validation_config()
        pattern = validation_config.get('vin_pattern', r'^[A-Z0-9]{17}$')
        return bool(re.match(pattern, vin))
    
    @staticmethod
    def validate_required_params(params: Dict[str, Any], required_fields: List[str]) -> None:
        """验证必需的业务参数"""
        missing_fields = [field for field in required_fields if not params.get(field)]
        if missing_fields:
            raise ValueError(f"缺少必需参数: {', '.join(missing_fields)}")
        
        # 验证各字段格式
        car_num = params.get('carNum', '')
        if car_num and not CoreService.validate_car_num(car_num):
            raise ValueError(f"车牌号格式错误: {car_num}")
        
        id_code = params.get('idCode', '')
        if id_code and not CoreService.validate_id_code(id_code):
            raise ValueError(f"身份证号格式错误: {id_code}")
        
        phone = params.get('bindBankPhone', '')
        if phone and not CoreService.validate_phone(phone):
            raise ValueError(f"手机号格式错误: {phone}")
        
        bank_card = params.get('bindBankNo', '')
        if bank_card and not CoreService.validate_bank_card(bank_card):
            raise ValueError(f"银行卡号格式错误: {bank_card}")
    
    @staticmethod
    def build_car_num(province: str, letter: str, number: str) -> str:
        """构建完整车牌号"""
        return f"{province}{letter}{number}"
    
    @staticmethod
    def get_vehicle_color_code(color_name: str) -> int:
        """获取车辆颜色代码"""
        vehicle_colors = CoreService.get_vehicle_colors()
        return vehicle_colors.get(color_name, 0)
    
    # ==================== 设备运营商管理 ====================
    
    @staticmethod
    def get_device_operator_code_by_name(operator_name: str, device_type: str = "0") -> str:
        """
        根据运营商名称获取设备运营商代码（模糊匹配）
        :param operator_name: 运营商名称（如：江苏苏通卡、广东粤通卡等）
        :param device_type: 设备类型 "0"=OBU, "1"=ETC
        :return: 设备运营商代码
        """
        try:
            from common.mysql_util import MySQLUtil
            import re
            
            # 获取数据库配置
            mysql_conf = CoreService.get_hcb_mysql_config()
            db = MySQLUtil(**mysql_conf)
            db.connect()
            
            # 根据设备类型选择不同的字典父ID
            # 🔥 重要修正：根据数据库DDL，TYPE字段：0=ETC, 1=OBU
            if device_type == "1":  # TYPE=1 是 OBU
                parent_id = "8fc26605b4df45119c87db730dc8f81f"
                device_name = "OBU"
            else:  # TYPE=0 是 ETC (device_type == "0")
                parent_id = "d55a901aafa24cc8b73e6f140278dc10"
                device_name = "ETC"
            
            # 查询该设备类型下的所有运营商代码
            sql = """
            SELECT NAME, NAME_EN 
            FROM hcb.sys_dictionaries t 
            WHERE PARENT_ID = %s
            """
            rows = db.query(sql, (parent_id,))
            db.close()
            
            if not rows:
                CoreService._log_warning(f"未找到{device_name}运营商代码，使用默认值")
                # 🔥 重要修正：根据数据库DDL，TYPE字段：0=ETC, 1=OBU
                return "1" if device_type == "1" else "10"  # OBU默认1, ETC默认10
            
            # 提取运营商名称中的关键词进行匹配
            match_keywords = CoreService._extract_operator_keywords(operator_name)
            CoreService._log_info(f"从运营商名称 '{operator_name}' 提取关键词: {match_keywords}")
            
            # 尝试模糊匹配
            matched_operators = []
            for row in rows:
                device_operator_name = row.get('NAME', '')
                # 检查是否包含关键词
                for keyword in match_keywords:
                    if keyword in device_operator_name:
                        matched_operators.append(row)
                        CoreService._log_info(f"匹配到{device_name}运营商: {device_operator_name} (关键词: {keyword})")
                        break
            
            if matched_operators:
                # 如果有匹配的运营商，随机选择一个
                import random
                selected_operator = random.choice(matched_operators)
                operator_code = selected_operator.get('NAME_EN', '1')
                operator_name_matched = selected_operator.get('NAME', '未知运营商')
                CoreService._log_info(f"为{device_name}选择匹配的运营商: {operator_name_matched} (代码: {operator_code})")
                return operator_code
            else:
                # 如果没有匹配的，随机选择一个
                import random
                selected_operator = random.choice(rows)
                operator_code = selected_operator.get('NAME_EN', '1')
                operator_name_random = selected_operator.get('NAME', '未知运营商')
                CoreService._log_warning(f"未找到匹配的{device_name}运营商，随机选择: {operator_name_random} (代码: {operator_code})")
                return operator_code
            
        except Exception as e:
            CoreService._log_error(f"获取设备运营商代码失败: {str(e)}")
            # 返回默认值
            # 🔥 重要修正：根据数据库DDL，TYPE字段：0=ETC, 1=OBU
            return "1" if device_type == "1" else "10"  # OBU默认1, ETC默认10
    
    @staticmethod
    def _extract_operator_keywords(operator_name: str) -> list:
        """
        从运营商名称中提取关键词用于匹配
        :param operator_name: 运营商名称
        :return: 关键词列表
        """
        if not operator_name:
            return []
        
        # 省份简称到全称的映射
        province_mapping = {
            '苏': ['江苏', '苏'],
            '粤': ['广东', '粤'],
            '京': ['北京', '京'],
            '沪': ['上海', '沪'],
            '津': ['天津', '津'],
            '渝': ['重庆', '渝'],
            '冀': ['河北', '冀'],
            '豫': ['河南', '豫'],
            '云': ['云南', '云'],
            '辽': ['辽宁', '辽'],
            '黑': ['黑龙江', '黑'],
            '湘': ['湖南', '湘'],
            '皖': ['安徽', '皖'],
            '鲁': ['山东', '鲁'],
            '新': ['新疆', '新'],
            '浙': ['浙江', '浙'],
            '赣': ['江西', '赣'],
            '鄂': ['湖北', '鄂'],
            '桂': ['广西', '桂'],
            '甘': ['甘肃', '甘'],
            '晋': ['山西', '晋'],
            '蒙': ['内蒙古', '蒙'],
            '陕': ['陕西', '陕'],
            '吉': ['吉林', '吉'],
            '闽': ['福建', '闽'],
            '贵': ['贵州', '贵'],
            '青': ['青海', '青'],
            '藏': ['西藏', '藏'],
            '川': ['四川', '川'],
            '宁': ['宁夏', '宁'],
            '琼': ['海南', '琼']
        }
        
        keywords = []
        
        # 直接包含的关键词
        keywords.append(operator_name)
        
        # 检查是否包含省份信息
        for abbr, full_names in province_mapping.items():
            for full_name in full_names:
                if full_name in operator_name or abbr in operator_name:
                    keywords.extend(full_names)
                    break
        
        # 移除重复项
        keywords = list(set(keywords))
        
        return keywords
    
    @staticmethod
    def get_device_operator_codes_by_operator_name(operator_name: str) -> Dict[str, str]:
        """
        根据产品运营商名称获取对应的OBU和ETC运营商代码
        :param operator_name: 产品运营商名称
        :return: {'obu_code': 'xx', 'etc_code': 'xx'}
        """
        try:
            obu_code = CoreService.get_device_operator_code_by_name(operator_name, "0")
            etc_code = CoreService.get_device_operator_code_by_name(operator_name, "1")
            
            return {
                'obu_code': obu_code,
                'etc_code': etc_code
            }
        except Exception as e:
            CoreService._log_error(f"获取设备运营商代码失败: {str(e)}")
            return {
                'obu_code': "1",
                'etc_code': "10"
            }
    
    @staticmethod
    def get_device_operator_code(operator_id: str, device_type: str = "0") -> str:
        """
        根据运营商ID获取设备运营商代码（向后兼容方法）
        :param operator_id: 运营商ID 
        :param device_type: 设备类型 "0"=OBU, "1"=ETC
        :return: 设备运营商代码
        """
        # 这里需要通过运营商ID获取运营商名称，然后调用新的方法
        try:
            operator_name = CoreService._get_operator_name_by_id(operator_id)
            if operator_name:
                return CoreService.get_device_operator_code_by_name(operator_name, device_type)
            else:
                # 如果无法获取运营商名称，使用随机方式
                return CoreService.get_device_operator_code_by_name("", device_type)
        except Exception as e:
            CoreService._log_error(f"通过ID获取设备运营商代码失败: {str(e)}")
            # 🔥 重要修正：根据数据库DDL，TYPE字段：0=ETC, 1=OBU
            return "1" if device_type == "1" else "10"  # OBU默认1, ETC默认10
    
    @staticmethod
    def _get_operator_name_by_id(operator_id: str) -> str:
        """
        根据运营商ID获取运营商名称
        :param operator_id: 运营商ID
        :return: 运营商名称
        """
        try:
            # 运营商ID映射（主要用于货车）
            operator_id_mapping = {
                '717830e1c3a948709ec0a92b44400c60': '江苏苏通卡',
                # 可以添加更多运营商ID映射
            }
            
            return operator_id_mapping.get(operator_id, '')
        except Exception as e:
            CoreService._log_error(f"获取运营商名称失败: {str(e)}")
            return ""
    
    @staticmethod
    def _get_operator_name_by_code(operator_code: str) -> str:
        """
        根据运营商代码获取运营商名称（主要用于客车）
        :param operator_code: 运营商代码（如：TXB、LTK等）
        :return: 运营商名称
        """
        try:
            # 客车运营商代码映射
            operator_code_mapping = {
                'TXB': '江苏苏通卡',
                'LTK': '黑龙江龙通卡', 
                'MTK': '内蒙古蒙通卡',
                'XTK': '湖南湘通卡',
                'YTK': '广东粤通卡',
                'BTK': '北京速通科技',
                'STK': '上海ETC',
                'ZTK': '浙江ETC',
                'CTK': '四川ETC',
                'HTK': '河北ETC',
                'ATK': '安徽ETC',
                'FTK': '福建ETC',
                'GTK': '广西ETC',
                'GZTK': '贵州ETC',
                'HNTK': '河南ETC',
                'HBTK': '湖北ETC',
                'JTK': '江西ETC',
                'JLTK': '吉林ETC',
                'LNTK': '辽宁ETC',
                'NTK': '宁夏ETC',
                'QTK': '青海ETC',
                'SXTK': '山西ETC',
                'SDTK': '山东ETC',
                'SCTK': '陕西ETC',
                'TTK': '天津ETC',
                'XJTK': '新疆ETC',
                'XZTK': '西藏ETC',
                'YNTK': '云南ETC',
                'CQTK': '重庆ETC',
                'HNTK': '海南ETC'
            }
            
            return operator_code_mapping.get(operator_code, '')
        except Exception as e:
            CoreService._log_error(f"通过代码获取运营商名称失败: {str(e)}")
            return ""
    
    @staticmethod
    def get_operator_name_from_product(product_data: Dict[str, Any]) -> str:
        """
        从产品数据中获取运营商名称
        :param product_data: 产品数据
        :return: 运营商名称
        """
        try:
            # 优先从OPERATOR_NAME获取（货车产品）
            if 'OPERATOR_NAME' in product_data:
                return product_data['OPERATOR_NAME']
            
            # 从operator_code获取（客车产品）
            if 'operator_code' in product_data:
                return CoreService._get_operator_name_by_code(product_data['operator_code'])
            
            # 从OPERATOR_ID获取（备用）
            if 'OPERATOR_ID' in product_data:
                return CoreService._get_operator_name_by_id(product_data['OPERATOR_ID'])
            
            return ''
        except Exception as e:
            CoreService._log_error(f"从产品数据获取运营商名称失败: {str(e)}")
            return ""
    
    @staticmethod
    def get_device_operator_codes_by_product(operator_id: str) -> Dict[str, str]:
        """
        根据产品运营商ID获取对应的OBU和ETC运营商代码（向后兼容方法）
        :param operator_id: 产品运营商ID
        :return: {'obu_code': 'xx', 'etc_code': 'xx'}
        """
        try:
            operator_name = CoreService._get_operator_name_by_id(operator_id)
            if operator_name:
                return CoreService.get_device_operator_codes_by_operator_name(operator_name)
            else:
                # 如果无法获取运营商名称，使用随机方式
                obu_code = CoreService.get_device_operator_code_by_name("", "0")
                etc_code = CoreService.get_device_operator_code_by_name("", "1")
                return {
                    'obu_code': obu_code,
                    'etc_code': etc_code
                }
        except Exception as e:
            CoreService._log_error(f"获取设备运营商代码失败: {str(e)}")
            return {
                'obu_code': "1",
                'etc_code': "10"
            }
    
    @staticmethod
    def get_device_operator_code_by_operator_code(operator_code: str, device_type: str = "0") -> str:
        """
        根据运营商编码精确获取设备运营商代码 - 使用BZ字段精确匹配
        :param operator_code: 运营商编码（如：XTK、MTK、LTK等）
        :param device_type: 设备类型 "0"=OBU, "1"=ETC
        :return: 设备运营商代码
        """
        try:
            from common.mysql_util import MySQLUtil
            
            # 获取数据库配置
            conf = CoreService.get_hcb_mysql_config()
            db = MySQLUtil(**conf)
            db.connect()
            
            # 根据设备类型选择不同的字典父ID
            # 🔥 重要修正：根据数据库DDL，TYPE字段：0=ETC, 1=OBU
            if device_type == "1":  # TYPE=1 是 OBU
                parent_id = "8fc26605b4df45119c87db730dc8f81f"
            else:  # TYPE=0 是 ETC (device_type == "0")
                parent_id = "d55a901aafa24cc8b73e6f140278dc10"
            
            # 💡 使用BZ字段进行精确匹配（新的精确方法）
            query = """
                SELECT NAME, NAME_EN, BZ 
                FROM hcb.sys_dictionaries 
                WHERE PARENT_ID = %s AND BZ = %s
                LIMIT 1
            """
            result = db.query(query, (parent_id, operator_code))
            db.close()
            
            if result and len(result) > 0:
                operator_info = result[0]
                name_en = operator_info.get('NAME_EN', '1')
                name = operator_info.get('NAME', '未知')
                
                CoreService._log_info(f"✅ BZ字段精确匹配成功: {operator_code} → {name} (代码: {name_en})")
                return name_en
            else:
                CoreService._log_warning(f"⚠️ BZ字段精确匹配失败，尝试省份模糊匹配: {operator_code}")
                
                # 如果BZ字段匹配失败，回退到原有的省份匹配方法
                code_to_province = {
                    "XTK": "湖南", "MTK": "内蒙古", "LTK": "黑龙江", "CTK": "四川",
                    "TXB": "江苏", "YTK": "广东", "ETK": "浙江", "ZTK": "山东",
                    "HTK": "河南", "BTK": "北京", "STK": "上海", "TTK": "天津"
                }
                
                province = code_to_province.get(operator_code)
                if not province:
                    CoreService._log_warning(f"未知运营商编码: {operator_code}")
                    return "1"
                
                # 构建目标设备运营商名称
                # 🔥 重要修正：根据数据库DDL，TYPE字段：0=ETC, 1=OBU
                device_suffix = "OBU" if device_type == "1" else "ETC"
                target_name = f"{province}{device_suffix}"
                CoreService._log_info(f"运营商编码 {operator_code} → 省份 {province} → 目标设备运营商 {target_name}")
                
                # 查询数据库中的设备运营商
                query_fallback = """
                    SELECT NAME, NAME_EN, BZ 
                    FROM hcb.sys_dictionaries 
                    WHERE PARENT_ID = %s AND NAME LIKE %s
                    LIMIT 1
                """
                db = MySQLUtil(**conf)
                db.connect()
                result_fallback = db.query(query_fallback, (parent_id, f"%{province}%"))
                db.close()
                
                if result_fallback and len(result_fallback) > 0:
                    operator_info = result_fallback[0]
                    name_en = operator_info.get('NAME_EN', '1')
                    name = operator_info.get('NAME', '未知')
                    
                    CoreService._log_info(f"✅ 省份模糊匹配成功: {operator_code} → {name} (代码: {name_en})")
                    return name_en
                else:
                    CoreService._log_error(f"❌ 省份模糊匹配也失败: {operator_code}")
                    return "1"
                
        except Exception as e:
            CoreService._log_error(f"通过运营商编码获取设备运营商代码失败: {str(e)}")
            return "1"
    
    @staticmethod
    def get_device_operator_codes_by_operator_code(operator_code: str) -> Dict[str, str]:
        """
        根据运营商编码获取OBU和ETC运营商代码
        :param operator_code: 运营商编码（如：XTK、MTK等）
        :return: {'obu_code': 'xx', 'etc_code': 'xx'}
        """
        try:
            obu_code = CoreService.get_device_operator_code_by_operator_code(operator_code, "0")
            etc_code = CoreService.get_device_operator_code_by_operator_code(operator_code, "1")
            
            return {
                'obu_code': obu_code,
                'etc_code': etc_code
            }
        except Exception as e:
            CoreService._log_error(f"通过运营商编码获取设备运营商代码失败: {str(e)}")
            return {'obu_code': '1', 'etc_code': '10'}

    # ==================== 设备运营商名称反向查询 ====================
    
    @staticmethod
    def get_operator_name_by_card_operators(card_operators: str, device_type: str = "0") -> str:
        """
        根据CARD_OPERATORS字段值反向查询运营商名称 - 增强显示BZ字段信息
        :param card_operators: CARD_OPERATORS字段值（如："6", "8"）
        :param device_type: 设备类型 "0"=OBU, "1"=ETC
        :return: 运营商名称（如："内蒙古OBU [MTK]", "内蒙古ETC [MTK]"）
        """
        try:
            from common.mysql_util import MySQLUtil
            
            # 获取数据库配置
            conf = CoreService.get_hcb_mysql_config()
            db = MySQLUtil(**conf)
            db.connect()
            
            # 根据设备类型选择不同的字典父ID
            # 🔥 重要修正：根据数据库DDL，TYPE字段：0=ETC, 1=OBU
            if device_type == "1":  # TYPE=1 是 OBU
                parent_id = "8fc26605b4df45119c87db730dc8f81f"
            else:  # TYPE=0 是 ETC (device_type == "0")
                parent_id = "d55a901aafa24cc8b73e6f140278dc10"
            
            # 查询对应的运营商名称和BZ字段
            query = """
                SELECT NAME, NAME_EN, BZ 
                FROM hcb.sys_dictionaries 
                WHERE PARENT_ID = %s AND NAME_EN = %s
                LIMIT 1
            """
            result = db.query(query, (parent_id, card_operators))
            db.close()
            
            if result and len(result) > 0:
                operator_info = result[0]
                name = operator_info.get('NAME', f'未知运营商')
                bz = operator_info.get('BZ', '')
                
                # 如果有BZ字段，在运营商名称后加上编码显示
                if bz:
                    return f"{name} [{bz}]"
                else:
                    return name
            else:
                return f'未知运营商(代码:{card_operators})'
            
        except Exception as e:
            CoreService._log_error(f"根据CARD_OPERATORS查询运营商名称失败: {str(e)}")
            return f'查询失败(代码:{card_operators})'
    
    @staticmethod
    def get_device_info_with_operator_names(devices: list) -> list:
        """
        为设备列表添加运营商名称信息
        :param devices: 设备信息列表（包含CARD_OPERATORS和TYPE字段）
        :return: 添加了运营商名称的设备列表
        """
        try:
            result_devices = []
            
            for device in devices:
                device_copy = device.copy()
                card_operators = device.get('CARD_OPERATORS', '')
                device_type = device.get('TYPE', '0')
                
                # 获取运营商名称
                operator_name = CoreService.get_operator_name_by_card_operators(card_operators, device_type)
                device_copy['设备运营商'] = operator_name
                
                # 添加设备类型显示名称
                # 🔥 重要修正：根据数据库DDL，TYPE字段：0=ETC, 1=OBU
                device_copy['设备类型'] = 'OBU' if device_type == '1' else 'ETC'
                
                result_devices.append(device_copy)
            
            return result_devices
            
        except Exception as e:
            CoreService._log_error(f"添加运营商名称信息失败: {str(e)}")
            return devices

    # ==================== 设备查询服务 ====================
    
    @staticmethod
    def query_devices_by_car_num(car_num: str) -> list:
        """
        根据车牌号查询设备信息
        :param car_num: 车牌号
        :return: 设备信息列表（包含运营商名称）
        """
        try:
            from common.mysql_util import MySQLUtil
            
            # 获取数据库配置
            conf = CoreService.get_hcb_mysql_config()
            db = MySQLUtil(**conf)
            db.connect()
            
            # 查询设备信息
            query = """
                SELECT NEWSTOCK_ID, INTERNAL_DEVICE_NO, EXTERNAL_DEVICE_NO, 
                       TYPE, CARD_OPERATORS, STATUS, CREATE_TIME, CAR_NUM,
                       STOCK_STATUS, SOURCE, REMARK
                FROM hcb.hcb_newstock 
                WHERE CAR_NUM = %s
                ORDER BY CREATE_TIME DESC
            """
            devices = db.query(query, (car_num,))
            db.close()
            
            # 添加运营商名称信息
            if devices:
                devices_with_names = CoreService.get_device_info_with_operator_names(devices)
                print(f"[INFO] 查询到车牌 {car_num} 的设备信息 {len(devices_with_names)} 条")
                return devices_with_names
            else:
                print(f"[INFO] 未找到车牌 {car_num} 的设备信息")
                return []
            
        except Exception as e:
            CoreService._log_error(f"查询设备信息失败: {str(e)}")
            return []
    
    @staticmethod
    def _log_info(message: str):
        """记录信息日志"""
        print(f"[INFO] {message}")
    
    @staticmethod
    def _log_warning(message: str):
        """记录警告日志"""
        print(f"[WARNING] {message}")
    
    @staticmethod
    def _log_error(message: str):
        """记录错误日志"""
        print(f"[ERROR] {message}")

    # ==================== 错误处理 ====================
    
    @staticmethod
    def assert_api_success(resp: Any, api_name: str = "接口") -> None:
        """断言API响应成功"""
        if isinstance(resp, str):
            try:
                resp = json.loads(resp)
            except Exception:
                raise Exception(f"{api_name} 响应不是有效的JSON: {resp}")
        
        if resp.get("code") != 200:
            msg = resp.get("msg") or resp.get("message") or str(resp)
            raise Exception(f"{api_name} 失败，原因: {msg}")
    
    @staticmethod
    def format_error_message(step_number: int, step_name: str, error: Exception) -> str:
        """格式化错误消息"""
        return f"{step_number}. {step_name}失败: {str(error)}"
    
    @staticmethod
    def safe_get_nested(data: Dict[str, Any], keys: list, default: Any = None) -> Any:
        """安全获取嵌套字典的值"""
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return default
        return current
    
    @staticmethod
    def format_database_error(operation: str, error: Exception) -> str:
        """格式化数据库错误信息"""
        error_msg = str(error)
        if "Can't connect to MySQL server" in error_msg:
            return f"数据库连接失败: {operation} - MySQL服务器连接异常"
        elif "Access denied" in error_msg:
            return f"数据库权限错误: {operation} - 用户名或密码错误"
        elif "Unknown database" in error_msg:
            return f"数据库不存在: {operation} - 指定的数据库不存在"
        else:
            return f"数据库操作失败: {operation} - {error_msg}"
    
    @staticmethod
    def format_network_error(operation: str, error: Exception) -> str:
        """格式化网络错误信息"""
        error_msg = str(error)
        if "Connection refused" in error_msg:
            return f"网络连接失败: {operation} - 无法连接到服务器"
        elif "timeout" in error_msg.lower():
            return f"网络超时: {operation} - 请求超时，请检查网络连接"
        elif "Name or service not known" in error_msg:
            return f"域名解析失败: {operation} - 无法解析服务器地址"
        else:
            return f"网络错误: {operation} - {error_msg}"
    
    @staticmethod
    def create_api_error_detail(api_path: str, url: str, error_code: str, error_message: str, 
                               request_data: Any = None, response_data: Any = None) -> Dict[str, Any]:
        """创建统一的API错误详情结构"""
        return {
            "api_path": api_path,
            "url": url, 
            "error_code": error_code,
            "error_message": error_message,
            "request_data": request_data,
            "response_data": response_data
        }
    
    @staticmethod
    def format_api_error_with_details(error_message: str, error_detail: Dict[str, Any]) -> str:
        """格式化包含详细调试信息的API错误消息"""
        # 添加调试信息
        debug_info = "\n\n" + "="*40 + "\n"
        debug_info += "📋 API调用详情\n"
        debug_info += "="*40 + "\n"
        debug_info += f"🔹 API路径: {error_detail.get('api_path', '未知')}\n"
        debug_info += f"🔹 请求URL: {error_detail.get('url', '未知')}\n"
        debug_info += f"🔹 错误码: {error_detail.get('error_code', '未知')}\n"
        
        # 添加请求参数
        request_data = error_detail.get('request_data')
        if request_data:
            debug_info += f"🔹 请求参数:\n"
            import json
            try:
                formatted_request = json.dumps(request_data, ensure_ascii=False, indent=2)
                debug_info += f"{formatted_request}\n"
            except:
                debug_info += f"{request_data}\n"
        
        # 添加响应结果
        response_data = error_detail.get('response_data')
        if response_data:
            debug_info += f"🔹 响应结果:\n"
            try:
                formatted_response = json.dumps(response_data, ensure_ascii=False, indent=2)
                debug_info += f"{formatted_response}\n"
            except:
                debug_info += f"{response_data}\n"
        
        # 组合完整的错误信息
        return error_message + debug_info
    
    @staticmethod
    def handle_exception_with_context(context: str, error: Exception) -> Exception:
        """处理异常并添加上下文信息"""
        error_msg = str(error)
        if "MySQL" in error_msg or "database" in error_msg.lower():
            return Exception(CoreService.format_database_error(context, error))
        elif "Connection" in error_msg or "timeout" in error_msg.lower():
            return Exception(CoreService.format_network_error(context, error))
        else:
            return Exception(f"{context}失败: {error_msg}")
    
    # ==================== 业务工具 ====================
    
    @staticmethod
    def generate_verify_code() -> str:
        """生成验证码（日期格式：YYMMDD）"""
        return datetime.now().strftime("%y%m%d")
    
    @staticmethod
    def generate_hash(timestamp=None) -> str:
        """生成hash码（用于HCB API请求的hashcode参数）"""
        import hashlib
        import time
        
        # 如果没有提供时间戳，生成当前时间戳（毫秒）
        if timestamp is None:
            timestamp = int(time.time() * 1000)
        
        # HCB签名算法: md5('chefuAPPchefuapp@2018' + timestamp)
        sign_string = f'chefuAPPchefuapp@2018{timestamp}'
        
        # 生成MD5 hash
        hash_obj = hashlib.md5(sign_string.encode('utf-8'))
        return hash_obj.hexdigest()
    
    @staticmethod
    def generate_hcb_params(relativeurl, **extra_params):
        """生成HCB API标准参数（包含正确的签名）"""
        import time
        
        timestamp = int(time.time() * 1000)
        hashcode = CoreService.generate_hash(timestamp)
        
        params = {
            'relativeurl': relativeurl,
            'caller': 'chefuAPP',
            'timestamp': timestamp,
            'hashcode': hashcode
        }
        
        # 添加额外参数
        params.update(extra_params)
        return params
    
    @staticmethod
    def should_continue_on_error(step_number: int) -> bool:
        """判断某步骤失败时是否应该继续执行后续步骤"""
        steps_config = CoreService.get_steps_config()
        continue_on_error_steps = steps_config.get('continue_on_error_steps', [9])
        return step_number in continue_on_error_steps
    
    @staticmethod
    def is_critical_step(step_number: int) -> bool:
        """判断是否为关键步骤"""
        steps_config = CoreService.get_steps_config()
        critical_steps = steps_config.get('critical_steps', [1, 2, 5, 6, 7, 8, 10, 11, 12, 13, 14])
        return step_number in critical_steps
    
    @staticmethod
    def get_step_retry_count(step_number: int) -> int:
        """获取步骤重试次数"""
        steps_config = CoreService.get_steps_config()
        retry_config = steps_config.get('retry_config', {})
        return retry_config.get(str(step_number), 1)
    
    @staticmethod
    def format_order_info(order_id: str, sign_order_id: str, verify_code_no: str) -> Dict[str, str]:
        """格式化订单信息"""
        return {
            'order_id': order_id,
            'sign_order_id': sign_order_id,
            'verify_code_no': verify_code_no
        }
    
    @staticmethod
    def clear_cache():
        """清除配置缓存"""
        CoreService._etc_config_cache = None 