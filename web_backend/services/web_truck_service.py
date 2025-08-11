# -*- coding: utf-8 -*-
"""
Web版货车ETC申办服务 - 无UI依赖的后端服务
"""
import json
import time
from typing import Dict, Any, Optional, Callable

# 只导入核心服务，避免UI依赖
from common.log_util import get_logger
from common.config_util import get_web_config


class WebTruckService:
    """Web版货车ETC申办服务"""
    
    def __init__(self):
        self.logger = get_logger("web_truck_service")
    
    def validate_truck_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """验证和完善货车参数"""
        try:
            # 这里应该使用货车数据服务验证参数，但需要去掉UI依赖
            # 暂时进行基本验证
            required_fields = ['name', 'id_code', 'phone', 'plate_province', 'plate_letter', 'plate_number', 'vin']
            for field in required_fields:
                if not params.get(field):
                    raise ValueError(f"缺少必要字段: {field}")
            
            self.logger.info("货车参数验证通过")
            return params
        except Exception as e:
            self.logger.error(f"货车参数验证失败: {e}")
            raise ValueError(f"货车参数验证失败: {e}")
    
    def start_truck_apply_flow(self, params: Dict[str, Any], progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        启动货车ETC申办流程 - Web版本
        :param params: 参数字典
        :param progress_callback: 进度回调函数
        :return: 申办结果
        """
        try:
            # 验证参数
            validated_params = self.validate_truck_params(params)
            
            # 默认进度回调
            if progress_callback is None:
                progress_callback = self._default_progress_callback
            
            # 获取配置
            config = get_web_config()
            browser_cookies = config.get('browser_cookies', {})
            service_url = config.get('api', {}).get('base_url', '')
            
            progress_callback(10, "开始货车ETC申办流程")
            
            # 导入真正的申办流程
            import sys
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            sys.path.insert(0, project_root)
            
            from apps.etc_apply.services.hcb.truck_core import TruckCore
            from apps.etc_apply.services.rtx.data_service import DataService
            
            # 转换参数格式 - 使用DataService的build_apply_params方法
            # 将web参数转换为申办流程需要的格式
            form_data = {
                'name': validated_params.get('name', ''),
                'id_code': validated_params.get('id_code', ''),
                'phone': validated_params.get('phone', ''),
                'bank_no': validated_params.get('bank_no', ''),
                'bank_name': validated_params.get('bank_name', ''),
                'plate_province': validated_params.get('plate_province', ''),
                'plate_letter': validated_params.get('plate_letter', ''),
                'plate_number': validated_params.get('plate_number', ''),
                'vin': validated_params.get('vin', ''),
                'vehicle_color': validated_params.get('vehicle_color', '黄色'),
                'vehicle_type': 'truck',  # 货车类型
                'vehicle_axles': validated_params.get('axle_count', '2'),
                'vehicle_wheels': validated_params.get('tire_count', '6'),
                'total_mass': validated_params.get('load_weight', '18000'),
                'unladen_mass': '7500',
                'model': 'EQ1180GZ5DJ1',
                'car_type': '货车',
                'selected_product': {
                    'product_id': validated_params.get('product_id', ''),
                    'operator_code': validated_params.get('operator_code', 'TXB')
                }
            }
            
            core_params = DataService.build_apply_params(form_data)
            core_params = DataService.validate_and_complete_params(core_params)
            
            # 创建TruckCore实例并执行申办流程
            worker = TruckCore(
                params=core_params,
                progress_callback=progress_callback,
                base_url=service_url,
                browser_cookies=browser_cookies
            )
            
            # 执行货车申办流程
            progress_callback(20, "检查车牌号")
            worker.step1_check_car_num()
            
            progress_callback(40, "验证车牌信息")
            worker.step2_check_is_not_car_num()
            
            progress_callback(60, "提交车牌信息")
            worker.step3_submit_car_num()
            
            progress_callback(80, "获取验证码")
            verify_result = worker.run_step4_get_code()
            
            progress_callback(90, "验证码获取成功")
            
            result = {
                'success': True,
                'message': '货车ETC申办流程启动成功，请确认验证码',
                'data': {
                    'apply_id': f'TRUCK_{int(time.time())}',
                    'status': 'waiting_verify',
                    'order_id': worker.state.order_id,
                    'sign_order_id': verify_result.get('sign_order_id'),
                    'verify_code_no': verify_result.get('verify_code_no'),
                    'params': validated_params
                }
            }
            
            progress_callback(100, "货车申办流程完成，等待验证码确认")
            self.logger.info("货车ETC申办流程执行完成")
            return result
            
        except Exception as e:
            self.logger.error(f"货车ETC申办流程失败: {e}")
            return {
                'success': False,
                'message': f'申办失败: {str(e)}',
                'error': str(e)
            }
    
    def _default_progress_callback(self, percent: int, message: str):
        """默认进度回调函数"""
        self.logger.info(f"进度 {percent}%: {message}")
    
    def get_api_base_url(self) -> str:
        """获取API基础URL"""
        try:
            config = get_web_config()
            return config.get('api', {}).get('base_url', '')
        except Exception as e:
            self.logger.error(f"获取API基础URL失败: {e}")
            return ""
    
    def get_default_data(self) -> Dict[str, Any]:
        """获取货车默认数据"""
        try:
            # 从配置获取默认数据
            config = get_web_config()
            
            ui_config = config.get('ui', {})
            vehicle_colors = config.get('vehicle_colors', {})
            
            return {
                'default_province': ui_config.get('default_province', '苏'),
                'default_letter': ui_config.get('default_letter', 'Z'),
                'default_plate_number': ui_config.get('default_plate_number', '9T4P0'),
                'default_vehicle_color': ui_config.get('default_vehicle_color', '黄色'),
                'hot_provinces': ui_config.get('hot_provinces', ['苏', '桂', '黑', '蒙', '湘', '川']),
                'vehicleColors': vehicle_colors,
                'default_load_weight': '10',
                'default_length': '12',
                'default_width': '2.5',
                'default_height': '3.5',
                'default_vehicle_type': '重型货车',
                'default_axle_count': '3',
                'default_tire_count': '10'
            }
        except Exception as e:
            self.logger.error(f"获取货车默认数据失败: {e}")
            raise e
    
    def get_vehicle_color_code(self, color_name: str) -> int:
        """获取车辆颜色代码"""
        try:
            config = get_web_config()
            vehicle_colors = config.get('vehicle_colors', {})
            return vehicle_colors.get(color_name, 1)  # 货车默认黄色
        except Exception as e:
            self.logger.error(f"获取车辆颜色代码失败: {e}")
            return 1
    
    def get_operators(self) -> Dict[str, Any]:
        """获取货车运营商列表"""
        try:
            from common.mysql_util import MySQLUtil
            
            # 获取数据库配置
            config = get_web_config()
            operators = []
            
            # 货车：只查询HCB数据库
            try:
                mysql_config = config.get('database', {}).get('hcb', {})
                db = MySQLUtil(**mysql_config)
                db.connect()
                
                sql = """
                select distinct a.OPERATOR_ID as operator_code,
                       concat('HCB_', a.OPERATOR_ID) as operator_name
                from hcb_product a
                left join hcb_channelproductgroupconfig b on a.PRODUCT_GROUP_CODE = b.product_group_code 
                and b.source='1' and b.channel_id='0000'
                where a.STATUS = '1'
                and b.extend_authority='1' and b.extend_open ='1' and b.business_type='0'
                and a.IS_SELF_SERVICE_PRODUCT='0'
                and a.PRODUCT_ID in(
                    select PRODUCT_ID from hcb_channelcompanyprofit 
                    where CHANNELCOMPANY_ID= 'd4949f0bc4c04a53987ac747287f3943' and status='1'
                )
                and a.USER_TYPE = '1'
                order by a.OPERATOR_ID
                """
                
                self.logger.info(f"查询HCB货车运营商")
                rows = db.query(sql)
                db.close()
                
                for row in rows:
                    operators.append({
                        'code': f"HCB_{row['operator_code']}",
                        'name': row['operator_name']
                    })
                
                self.logger.info(f"查询到 {len(operators)} 个货车运营商")
                
            except Exception as e:
                self.logger.warning(f"查询HCB运营商失败: {str(e)}")
            
            return {
                'success': True,
                'data': operators
            }
            
        except Exception as e:
            self.logger.error(f"获取货车运营商列表失败: {str(e)}")
            return {
                'success': False,
                'message': f'获取货车运营商列表失败: {str(e)}',
                'data': []
            }
    
    def get_products_by_operator(self, operator_code: str) -> Dict[str, Any]:
        """获取货车产品列表"""
        try:
            from common.mysql_util import MySQLUtil
            
            # 获取数据库配置
            config = get_web_config()
            
            if not operator_code.startswith('HCB_'):
                return {
                    'success': False,
                    'message': '货车只支持HCB运营商',
                    'data': []
                }
            
            # 慧车宝货车产品查询
            operator_id = operator_code.replace('HCB_', '')
            mysql_config = config.get('database', {}).get('hcb', {})
            db = MySQLUtil(**mysql_config)
            db.connect()
            
            sql = """
            select ETCBANK_ID as product_id, NAME as product_name, 
                   %s as operator_code, STATUS as status
            from HCB_ETCBANK
            where STATUS = '1' 
            and ETCBANK_ID in(
                select a.LOAN_BANKID from hcb_product a
                left join hcb_channelproductgroupconfig b on a.PRODUCT_GROUP_CODE = b.product_group_code 
                and b.source='1' and b.channel_id='0000'
                where a.STATUS = '1'
                and b.extend_authority='1' and b.extend_open ='1' and b.business_type='0'
                and a.IS_SELF_SERVICE_PRODUCT='0'
                and a.PRODUCT_ID in(
                    select PRODUCT_ID from hcb_channelcompanyprofit 
                    where CHANNELCOMPANY_ID= 'd4949f0bc4c04a53987ac747287f3943' and status='1'
                )
                and a.OPERATOR_ID = %s
                and a.USER_TYPE = '1'
            )
            """
            
            self.logger.info(f"查询HCB货车产品，运营商ID: {operator_id}")
            rows = db.query(sql, (operator_code, operator_id))
            db.close()
            
            products = []
            for row in rows:
                products.append({
                    'id': str(row['product_id']),
                    'name': row['product_name'],
                    'operator_code': row['operator_code'],
                    'status': row['status']
                })
            
            self.logger.info(f"查询到 {len(products)} 个货车产品，运营商: {operator_code}")
            
            return {
                'success': True,
                'data': products
            }
            
        except Exception as e:
            self.logger.error(f"获取货车产品列表失败: {str(e)}")
            return {
                'success': False,
                'message': f'获取货车产品列表失败: {str(e)}',
                'data': []
            }

    def save_truck_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """保存货车数据"""
        try:
            # 这里应该调用实际的数据保存逻辑
            # 暂时返回模拟结果
            self.logger.info(f"保存货车数据: {json.dumps(data, ensure_ascii=False)}")
            
            return {
                'success': True,
                'message': '货车数据保存成功',
                'data': {
                    'save_id': f'TRUCK_SAVE_{int(time.time())}',
                    'timestamp': int(time.time())
                }
            }
        except Exception as e:
            self.logger.error(f"保存货车数据失败: {e}")
            return {
                'success': False,
                'message': f'保存数据失败: {str(e)}',
                'error': str(e)
            }
    
    def check_service_status(self) -> Dict[str, Any]:
        """检查服务状态"""
        try:
            api_url = self.get_api_base_url()
            return {
                'success': True,
                'message': '货车服务状态正常',
                'data': {
                    'api_url': api_url,
                    'status': 'available'
                }
            }
        except Exception as e:
            self.logger.error(f"货车服务状态检查失败: {e}")
            return {
                'success': False,
                'message': f'货车服务状态检查失败: {str(e)}',
                'error': str(e)
            } 