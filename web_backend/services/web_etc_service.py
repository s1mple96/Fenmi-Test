# -*- coding: utf-8 -*-
"""
Web版ETC申办服务 - 无UI依赖的后端服务
"""
import json
import time
from typing import Dict, Any, Optional, Callable

# 只导入核心服务，避免UI依赖
from common.log_util import get_logger
from common.config_util import get_web_config


class WebETCService:
    """Web版ETC申办服务"""
    
    def __init__(self):
        self.logger = get_logger("web_etc_service")
    
    def validate_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """验证和完善参数"""
        try:
            # 基本参数验证
            required_fields = ['name', 'id_code', 'phone', 'plate_province', 'plate_letter', 'plate_number', 'vin']
            for field in required_fields:
                if not params.get(field):
                    raise ValueError(f"缺少必要字段: {field}")
            
            self.logger.info("参数验证通过")
            return params
        except Exception as e:
            self.logger.error(f"参数验证失败: {e}")
            raise ValueError(f"参数验证失败: {e}")
    
    def start_etc_apply_flow(self, params: Dict[str, Any], progress_callback: Optional[Callable] = None) -> Dict[str, Any]:
        """
        启动ETC申办流程 - Web版本
        :param params: 参数字典
        :param progress_callback: 进度回调函数
        :return: 申办结果
        """
        try:
            # 验证参数
            validated_params = self.validate_params(params)
            
            # 默认进度回调
            if progress_callback is None:
                progress_callback = self._default_progress_callback
            
            # 获取配置
            config = get_web_config()
            browser_cookies = config.get('browser_cookies', {})
            service_url = config.get('api', {}).get('base_url', '')
            
            progress_callback(10, "开始ETC申办流程")
            
            # 导入真正的申办流程
            import sys
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            sys.path.insert(0, project_root)
            
            from apps.etc_apply.services.rtx.etc_core import Core
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
                'vehicle_color': validated_params.get('vehicle_color', '蓝色'),
                'vehicle_type': 'passenger',  # 客车类型
                'selected_product': {
                    'product_id': validated_params.get('product_id', ''),
                    'operator_code': validated_params.get('operator_code', 'TXB')
                }
            }
            
            core_params = DataService.build_apply_params(form_data)
            core_params = DataService.validate_and_complete_params(core_params)
            
            # 创建Core实例并执行申办流程
            worker = Core(
                params=core_params,
                progress_callback=progress_callback,
                base_url=service_url,
                browser_cookies=browser_cookies
            )
            
            # 自定义进度回调，实时更新前端
            def real_time_progress_callback(percent, message):
                progress_callback(percent, message)
                # 这里可以添加WebSocket或其他实时通信机制
                # 暂时使用日志记录
                self.logger.info(f"实时进度: {percent}% - {message}")
            
            # 设置worker的进度回调
            worker.state.progress_callback = real_time_progress_callback
            
            # 执行前6步
            real_time_progress_callback(20, "检查车牌号")
            worker.step1_check_car_num()
            
            real_time_progress_callback(30, "验证车牌信息")
            worker.step2_check_is_not_car_num()
            
            real_time_progress_callback(40, "获取渠道信息")
            worker.step3_get_channel_use_address()
            
            real_time_progress_callback(50, "提交车牌信息")
            worker.step5_submit_car_num()
            
            real_time_progress_callback(60, "添加协议")
            worker.step6_protocol_add()
            
            # 获取可选服务（在有了orderId之后）
            real_time_progress_callback(70, "获取可选服务")
            try:
                worker.step4_get_optional_service_list()
            except Exception as e:
                self.logger.warning(f"获取可选服务失败，继续执行: {e}")
                # 如果获取可选服务失败，继续执行后续步骤
            
            # 获取验证码
            real_time_progress_callback(80, "获取验证码")
            verify_result = worker.run_step7_get_code(
                worker.state.order_id, 
                worker.state.sign_order_id
            )
            
            real_time_progress_callback(90, "验证码获取成功")
            
            result = {
                'success': True,
                'message': 'ETC申办流程启动成功，请确认验证码',
                'data': {
                    'apply_id': f'ETC_{int(time.time())}',
                    'status': 'waiting_verify',
                    'order_id': worker.state.order_id,
                    'sign_order_id': verify_result['sign_order_id'],
                    'verify_code_no': verify_result['verify_code_no'],
                    'params': validated_params
                }
            }
            
            progress_callback(100, "申办流程完成，等待验证码确认")
            self.logger.info("ETC申办流程执行完成")
            return result
            
        except Exception as e:
            self.logger.error(f"ETC申办流程失败: {e}")
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
        """获取客车默认数据"""
        try:
            # 从配置获取默认数据
            config = get_web_config()
            
            ui_config = config.get('ui', {})
            vehicle_colors = config.get('vehicle_colors', {})
            
            return {
                'default_province': ui_config.get('default_province', '苏'),
                'default_letter': ui_config.get('default_letter', 'Z'),
                'default_plate_number': ui_config.get('default_plate_number', '9T4P0'),
                'default_vehicle_color': ui_config.get('default_vehicle_color', '蓝色'),
                'hot_provinces': ui_config.get('hot_provinces', ['苏', '桂', '黑', '蒙', '湘', '川']),
                'vehicleColors': vehicle_colors
            }
        except Exception as e:
            self.logger.error(f"获取客车默认数据失败: {e}")
            raise e
    
    def get_vehicle_color_code(self, color_name: str) -> int:
        """获取车辆颜色代码"""
        try:
            config = get_web_config()
            vehicle_colors = config.get('vehicle_colors', {})
            return vehicle_colors.get(color_name, 0)
        except Exception as e:
            self.logger.error(f"获取车辆颜色代码失败: {e}")
            return 0
    
    def confirm_verify_code(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """确认验证码并完成申办流程"""
        try:
            verify_code = data.get('verifyCode')
            order_id = data.get('orderId')
            sign_order_id = data.get('signOrderId')
            verify_code_no = data.get('verifyCodeNo')
            
            if not all([verify_code, order_id, sign_order_id, verify_code_no]):
                return {
                    'success': False,
                    'message': '缺少必要的验证码参数'
                }
            
            # 导入真正的申办流程
            import sys
            import os
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
            sys.path.insert(0, project_root)
            
            from apps.etc_apply.services.rtx.etc_core import Core
            from apps.etc_apply.services.rtx.data_service import DataService
            
            # 获取配置
            config = get_web_config()
            browser_cookies = config.get('browser_cookies', {})
            service_url = config.get('api', {}).get('base_url', '')
            
            # 创建Core实例
            worker = Core(
                params={},  # 这里不需要完整参数，只需要验证码相关参数
                progress_callback=self._default_progress_callback,
                base_url=service_url,
                browser_cookies=browser_cookies
            )
            
            # 设置状态
            worker.state.order_id = order_id
            worker.state.sign_order_id = sign_order_id
            worker.state.verify_code_no = verify_code_no
            
            # 执行验证码确认和后续流程
            self.logger.info("开始验证码确认流程")
            
            # 步骤8：验证码校验
            worker.step8_verify_code_check(verify_code)
            
            # 步骤9：签约校验
            worker.step9_sign_check()
            
            # 步骤10：提交签约
            worker.step10_submit_sign()
            
            # 步骤11：获取签约结果
            worker.step11_get_sign_result()
            
            # 步骤12：获取OBU信息
            worker.step12_get_obu_info()
            
            # 步骤13：获取ETC信息
            worker.step13_get_etc_info()
            
            # 步骤14：完成申办
            worker.step14_finish_apply()
            
            result = {
                'success': True,
                'message': 'ETC申办成功完成',
                'data': {
                    'order_id': order_id,
                    'sign_order_id': sign_order_id,
                    'status': 'completed',
                    'obu_info': getattr(worker.state, 'obu_info', {}),
                    'etc_info': getattr(worker.state, 'etc_info', {})
                }
            }
            
            self.logger.info("ETC申办流程完全完成")
            return result
            
        except Exception as e:
            self.logger.error(f"确认验证码失败: {e}")
            return {
                'success': False,
                'message': f'确认验证码失败: {str(e)}',
                'error': str(e)
            }
    
    def save_etc_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """保存客车数据"""
        try:
            # 这里应该调用实际的数据保存逻辑
            # 暂时返回模拟结果
            self.logger.info(f"保存客车数据: {json.dumps(data, ensure_ascii=False)}")
            
            return {
                'success': True,
                'message': '客车数据保存成功',
                'data': {
                    'save_id': f'ETC_SAVE_{int(time.time())}',
                    'timestamp': int(time.time())
                }
            }
        except Exception as e:
            self.logger.error(f"保存客车数据失败: {e}")
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
                'message': '服务状态正常',
                'data': {
                    'api_url': api_url,
                    'status': 'available'
                }
            }
        except Exception as e:
            self.logger.error(f"服务状态检查失败: {e}")
            return {
                'success': False,
                'message': f'服务状态检查失败: {str(e)}',
                'error': str(e)
            }
    
    def get_products_by_operator(self, operator_code: str = 'TXB', vehicle_type: str = '0') -> Dict[str, Any]:
        """根据运营商获取产品列表
        Args:
            operator_code: 运营商代码
            vehicle_type: 车辆类型 0=客车, 1=货车
        """
        try:
            from common.mysql_util import MySQLUtil
            
            # 获取数据库配置
            config = get_web_config()
            
            if operator_code.startswith('HCB_'):
                # 慧车宝产品查询
                operator_id = operator_code.replace('HCB_', '')
                mysql_config = config.get('database', {}).get('hcb', {})
                db = MySQLUtil(**mysql_config)
                db.connect()
                
                # 根据车辆类型过滤产品：0=客车, 1=货车
                user_type_filter = vehicle_type  # 直接使用传入的vehicle_type参数
                
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
                    and a.USER_TYPE = %s
                )
                """
                
                self.logger.info(f"查询HCB产品，运营商ID: {operator_id}, 车辆类型: {user_type_filter}")
                rows = db.query(sql, (operator_code, operator_id, user_type_filter))
                db.close()
                
                products = []
                for row in rows:
                    products.append({
                        'id': str(row['product_id']),
                        'name': row['product_name'],
                        'operator_code': row['operator_code'],
                        'status': row['status']
                    })
                
            else:
                # RTX/TXB产品查询
                mysql_config = config.get('database', {}).get('rtx', {})
                db = MySQLUtil(**mysql_config)
                db.connect()
                
                # 简化查询，不依赖user_type字段
                sql = """
                select product_id, product_name, operator_code, status 
                from rtx_product 
                where PRODUCT_ID in (
                    select PRODUCT_ID from rtx_channel_company_profit 
                    where channelcompany_id = 'd4949f0bc4c04a53987ac747287f3943'
                ) 
                and status = 1
                and operator_code = %s
                """
                
                rows = db.query(sql, (operator_code,))
                db.close()
                
                products = []
                for row in rows:
                    products.append({
                        'id': row['product_id'],
                        'name': row['product_name'],
                        'operator_code': row['operator_code'],
                        'status': row['status']
                    })
            
            self.logger.info(f"查询到 {len(products)} 个产品，运营商: {operator_code}")
            
            return {
                'success': True,
                'data': products
            }
            
        except Exception as e:
            self.logger.error(f"获取产品列表失败: {str(e)}")
            return {
                'success': False,
                'message': f'获取产品列表失败: {str(e)}',
                'data': []
            }
    
    def get_operators(self, vehicle_type: str = '0') -> Dict[str, Any]:
        """获取运营商列表
        Args:
            vehicle_type: 车辆类型 0=客车, 1=货车
        """
        try:
            from common.mysql_util import MySQLUtil
            
            # 获取数据库配置
            config = get_web_config()
            
            operators = []
            
            if vehicle_type == '0':
                # 客车：只查询RTX数据库
                try:
                    mysql_config = config.get('database', {}).get('rtx', {})
                    db = MySQLUtil(**mysql_config)
                    db.connect()
                    
                    sql = """
                    select distinct operator_code, operator_code as operator_name
                    from rtx_product 
                    where status = 1
                    and PRODUCT_ID in (
                        select PRODUCT_ID from rtx_channel_company_profit 
                        where channelcompany_id = 'd4949f0bc4c04a53987ac747287f3943'
                    )
                    order by operator_code
                    """
                    
                    rows = db.query(sql)
                    db.close()
                    
                    for row in rows:
                        operators.append({
                            'code': row['operator_code'],
                            'name': row['operator_name']
                        })
                    
                    self.logger.info(f"查询到 {len(operators)} 个客车运营商")
                    
                except Exception as e:
                    self.logger.warning(f"查询RTX运营商失败: {str(e)}")
            
            elif vehicle_type == '1':
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
            self.logger.error(f"获取运营商列表失败: {str(e)}")
            return {
                'success': False,
                'message': f'获取运营商列表失败: {str(e)}',
                'data': []
            } 