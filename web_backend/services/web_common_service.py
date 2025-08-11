# -*- coding: utf-8 -*-
"""
通用Web服务
"""
import sys
import os
import re
import json
from werkzeug.utils import secure_filename

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from common.log_util import get_logger
from common.config_util import get_web_config

class WebCommonService:
    """通用Web服务"""
    
    def __init__(self):
        self.logger = get_logger("web_common_service")
        
    def get_provinces(self):
        """获取省份列表"""
        try:
            # 从Web配置获取省份映射
            config = get_web_config()
            device_config = config.get('device', {})
            ui_config = config.get('ui', {})
            
            # 省份映射
            province_mapping = device_config.get('province_mapping', {})
            
            # 热门省份
            hot_provinces = ui_config.get('hot_provinces', [])
            
            # 所有省份
            all_provinces = list(province_mapping.keys())
            
            return {
                'hot_provinces': hot_provinces,
                'all_provinces': all_provinces,
                'province_mapping': province_mapping
            }
            
        except Exception as e:
            self.logger.error(f"获取省份列表失败: {str(e)}")
            raise e
    
    def get_plate_letters(self, province):
        """获取车牌字母列表"""
        try:
            # 根据省份返回对应的字母列表
            # 这里可以根据实际业务需求自定义每个省份的字母列表
            default_letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
            
            # 全国所有省份、自治区、直辖市、特别行政区的字母配置
            province_letters = {
                # 直辖市
                '京': ['A', 'B', 'C', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'Y'],  # 北京
                '津': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R'],  # 天津
                '沪': ['A', 'B', 'C', 'D', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'R'],  # 上海
                '渝': ['A', 'B', 'C', 'F', 'G', 'H'],  # 重庆
                
                # 华北地区
                '冀': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'R', 'T'],  # 河北
                '晋': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M'],  # 山西
                '蒙': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M'],  # 内蒙古
                
                # 东北地区
                '辽': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P'],  # 辽宁
                '吉': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K'],  # 吉林
                '黑': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'R'],  # 黑龙江
                
                # 华东地区
                '苏': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N'],  # 江苏
                '浙': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L'],  # 浙江
                '皖': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S'],  # 安徽
                '闽': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K'],  # 福建
                '赣': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M'],  # 江西
                '鲁': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V'],  # 山东
                
                # 华中地区
                '豫': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'U'],  # 河南
                '鄂': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S'],  # 湖北
                '湘': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'U'],  # 湖南
                
                # 华南地区
                '粤': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'],  # 广东
                '桂': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'R'],  # 广西
                '琼': ['A', 'B', 'C', 'D', 'E'],  # 海南
                
                # 西南地区
                '川': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'],  # 四川
                '贵': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J'],  # 贵州
                '云': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S'],  # 云南
                '藏': ['A', 'B', 'C', 'D', 'E', 'F', 'G'],  # 西藏
                
                # 西北地区
                '陕': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'V'],  # 陕西
                '甘': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P'],  # 甘肃
                '青': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H'],  # 青海
                '宁': ['A', 'B', 'C', 'D', 'E'],  # 宁夏
                '新': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R'],  # 新疆
                
                # 特别行政区
                '港': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'],  # 香港
                '澳': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'],  # 澳门
                
                # 台湾地区（预留）
                '台': ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J', 'K', 'L', 'M', 'N', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z'],  # 台湾
                
                # 特殊车牌（使馆、领馆等）
                '使': ['1', '2', '3', '4', '5', '6', '7', '8', '9'],  # 使馆车牌
                '领': ['1', '2', '3', '4', '5', '6', '7', '8', '9']   # 领馆车牌
            }
            
            letters = province_letters.get(province, default_letters)
            
            return letters
            
        except Exception as e:
            self.logger.error(f"获取车牌字母列表失败: {str(e)}")
            raise e
    
    def validate_field(self, field_type, value):
        """验证字段值"""
        try:
            config = get_web_config()
            validation_config = config.get('validation', {})
            
            if field_type == 'id_code':
                pattern = validation_config.get('id_code_pattern')
                is_valid = bool(re.match(pattern, value)) if pattern else True
                message = '身份证号格式正确' if is_valid else '身份证号格式不正确'
                
            elif field_type == 'phone':
                pattern = validation_config.get('phone_pattern')
                is_valid = bool(re.match(pattern, value)) if pattern else True
                message = '手机号格式正确' if is_valid else '手机号格式不正确'
                
            elif field_type == 'bank_card':
                pattern = validation_config.get('bank_card_pattern')
                is_valid = bool(re.match(pattern, value)) if pattern else True
                message = '银行卡号格式正确' if is_valid else '银行卡号格式不正确'
                
            elif field_type == 'vin':
                pattern = validation_config.get('vin_pattern')
                is_valid = bool(re.match(pattern, value)) if pattern else True
                message = '车架号格式正确' if is_valid else '车架号格式不正确'
                
            elif field_type == 'car_number':
                pattern = validation_config.get('car_number_pattern')
                is_valid = bool(re.match(pattern, value)) if pattern else True
                message = '车牌号格式正确' if is_valid else '车牌号格式不正确'
                
            else:
                is_valid = True
                message = '未知验证类型'
            
            return {
                'success': True,
                'valid': is_valid,
                'message': message
            }
            
        except Exception as e:
            self.logger.error(f"验证字段失败: {str(e)}")
            return {
                'success': False,
                'valid': False,
                'message': f'验证失败: {str(e)}'
            }
    
    def handle_file_upload(self, file):
        """处理文件上传"""
        try:
            # 检查文件扩展名
            ui_config = CoreService.get_ui_config()
            allowed_extensions = ui_config.get('allowed_file_extensions', ['.txt', '.csv', '.json'])
            
            filename = secure_filename(file.filename)
            file_ext = os.path.splitext(filename)[1].lower()
            
            if file_ext not in allowed_extensions:
                return {
                    'success': False,
                    'message': f'不支持的文件格式，仅支持: {", ".join(allowed_extensions)}'
                }
            
            # 创建上传目录
            upload_dir = os.path.join(project_root, 'temp', 'uploads')
            os.makedirs(upload_dir, exist_ok=True)
            
            # 生成唯一文件名
            import time
            timestamp = int(time.time())
            new_filename = f"{timestamp}_{filename}"
            file_path = os.path.join(upload_dir, new_filename)
            
            # 保存文件
            file.save(file_path)
            
            # 处理文件内容
            file_data = self._process_uploaded_file(file_path, file_ext)
            
            return {
                'success': True,
                'message': '文件上传成功',
                'data': {
                    'filename': new_filename,
                    'file_path': file_path,
                    'file_data': file_data
                }
            }
            
        except Exception as e:
            self.logger.error(f"文件上传失败: {str(e)}")
            return {
                'success': False,
                'message': f'文件上传失败: {str(e)}'
            }
    
    def _process_uploaded_file(self, file_path, file_ext):
        """处理上传的文件内容"""
        try:
            if file_ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
                    
            elif file_ext == '.csv':
                import csv
                data = []
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        data.append(row)
                return data
                
            elif file_ext == '.txt':
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    return [line.strip() for line in lines if line.strip()]
                    
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"处理文件内容失败: {str(e)}")
            return None 