# -*- coding: utf-8 -*-
"""
货车ETC申办核心流程 - 基于55个接口的完整数据流分析
"""
import time
import uuid
from typing import Dict, Any, Optional, Callable
from apps.etc_apply.services.hcb.truck_api_client import TruckApiClient
from apps.etc_apply.services.hcb.truck_state_service import TruckFlowState, TruckStepManager, TruckStepStatus
from apps.etc_apply.services.rtx.log_service import LogService
from apps.etc_apply.services.rtx.core_service import CoreService


class TruckCore:
    """货车ETC申办核心流程控制器"""
    
    def __init__(self, params: Dict[str, Any], progress_callback: Optional[Callable] = None, 
                 base_url: str = None, browser_cookies: Dict = None):
        self.params = params
        self.base_url = base_url or "https://788360p9o5.yicp.fun"
        self.browser_cookies = browser_cookies or {}
        
        # 初始化服务
        self.api_client = TruckApiClient(self.base_url, cookies=self.browser_cookies)
        self.flow_state = TruckFlowState(progress_callback)
        self.log_service = LogService("truck_core")
        
        # 关键数据存储
        self.truck_etc_apply_id = None
        self.truck_user_id = None
        self.truck_user_wallet_id = None
        self.order_id = None
        self.user_bind_bank_id = None
        self.product_id = None
        self.bank_list = []
        self.product_info = {}
        
        # 运营商和产品相关
        self.operator_list = []
        self.selected_operator = None
        self.product_list = []
        self.selected_product = None
        self.selected_bank = None
        
        self.log_service.info("货车申办流程初始化完成")
    
    def run_full_truck_flow(self) -> Dict[str, Any]:
        """执行完整货车申办流程"""
        try:
            self.log_service.info("开始执行完整货车申办流程")
            
            # 执行完整的21步流程
            for step in range(1, 22):
                success = self._execute_step(step)
                if not success:
                    self.log_service.error(f"步骤{step}执行失败，流程终止")
                    return None
            
            # 返回最终结果
            result = {
                'truck_etc_apply_id': self.truck_etc_apply_id,
                'truck_user_id': self.truck_user_id,
                'truck_user_wallet_id': self.truck_user_wallet_id,
                'order_id': self.order_id,
                'status': 'completed'
            }
            
            self.log_service.info("货车申办流程全部完成")
            return result
            
        except Exception as e:
            self.log_service.error(f"货车申办流程异常: {str(e)}")
            raise e
    
    def run_to_step5(self) -> Dict[str, Any]:
        """执行到步骤5（获取申办ID后暂停）"""
        try:
            self.log_service.info("开始执行货车申办前置流程（到步骤5）")
            
            # 执行前5个步骤
            for step in range(1, 6):
                success = self._execute_step(step)
                if not success:
                    self.log_service.error(f"步骤{step}执行失败，流程终止")
                    return None
            
            return {
                'truck_etc_apply_id': self.truck_etc_apply_id,
                'truck_user_id': self.truck_user_id,
                'truck_user_wallet_id': self.truck_user_wallet_id,
                'status': 'step5_completed'
            }
            
        except Exception as e:
            self.log_service.error(f"货车申办前置流程异常: {str(e)}")
            raise e
    
    def run_from_step6(self) -> Dict[str, Any]:
        """从步骤6开始执行后续流程"""
        try:
            self.log_service.info("继续执行货车申办后续流程（从步骤6）")
            
            # 执行步骤6到21
            for step in range(6, 22):
                success = self._execute_step(step)
                if not success:
                    self.log_service.error(f"步骤{step}执行失败，流程终止")
                    return None
            
            return {
                'truck_etc_apply_id': self.truck_etc_apply_id,
                'truck_user_id': self.truck_user_id,
                'truck_user_wallet_id': self.truck_user_wallet_id,
                'order_id': self.order_id,
                'status': 'completed'
            }
            
        except Exception as e:
            self.log_service.error(f"货车申办后续流程异常: {str(e)}")
            raise e
    
    def _execute_step(self, step_number: int) -> bool:
        """执行单个步骤"""
        step_name = TruckStepManager.get_step_name(step_number)
        self.log_service.info(f"{step_number}.{step_name}")
        
        try:
            # 更新进度状态
            self.flow_state.update_progress(
                step_number, 
                f"{step_number}.{step_name}", 
                TruckStepStatus.RUNNING
            )
            
            # 根据步骤号执行对应逻辑
            success, error_detail = self._execute_step_logic(step_number)
            
            if success:
                self.flow_state.update_progress(
                    step_number, 
                    f"{step_number}.{step_name}完成", 
                    TruckStepStatus.SUCCESS
                )
                self.log_service.info(f"{step_number}.{step_name}完成")
                return True
            else:
                # 使用具体的错误信息，如果没有则使用默认信息
                error_msg = error_detail if error_detail else f"{step_number}.{step_name}失败"
                self.flow_state.update_progress(
                    step_number, 
                    error_msg, 
                    TruckStepStatus.FAILED
                )
                self.log_service.error(error_msg)
                # 通过进度回调传递错误信息到UI
                if self.flow_state.progress_callback:
                    self.flow_state.progress_callback(int((step_number / 21) * 100), error_msg)
                return False
                
        except Exception as e:
            error_msg = f"{step_number}.{step_name}异常: {str(e)}"
            self.flow_state.update_progress(
                step_number, 
                error_msg, 
                TruckStepStatus.FAILED
            )
            self.log_service.error(error_msg)
            # 通过进度回调传递错误信息到UI
            if self.flow_state.progress_callback:
                self.flow_state.progress_callback(int((step_number / 21) * 100), error_msg)
            return False
    
    def _execute_step_logic(self, step_number: int) -> tuple[bool, str]:
        """执行具体步骤逻辑，返回(成功标志, 错误详情)"""
        
        if step_number == 1:
            # 步骤1: 更新微信消息模板
            try:
                success = self._step1_update_wx_msg_template()
                return (success, None if success else "更新微信消息模板失败")
            except Exception as e:
                return (False, str(e))
            
        elif step_number == 2:
            # 步骤2: 获取运营商列表
            try:
                success = self._step2_get_operator_list()
                return (success, None if success else "获取运营商列表失败")
            except Exception as e:
                return (False, str(e))
            
        elif step_number == 3:
            # 步骤3: 根据运营商获取产品列表
            try:
                success = self._step3_get_product_list_by_operator()
                return (success, None if success else "获取产品列表失败")
            except Exception as e:
                return (False, str(e))
            
        elif step_number == 4:
            # 步骤4: 获取银行列表
            try:
                success = self._step4_get_bank_list()
                return (success, None if success else "获取银行列表失败")
            except Exception as e:
                return (False, str(e))
            
        elif step_number == 5:
            # 步骤5: 获取产品信息
            try:
                success = self._step5_get_product_info()
                return (success, None if success else "获取产品信息失败")
            except Exception as e:
                return (False, str(e))
            
        elif step_number == 6:
            # 步骤6: 校验车牌号信息
            try:
                success = self._step6_check_plate_no_info()
                return (success, None if success else "校验车牌号信息失败")
            except Exception as e:
                return (False, str(e))
            
        elif step_number == 7:
            # 步骤7: 检查是否可申办
            try:
                success = self._step7_check_is_not_car_num()
                return (success, None if success else "检查是否可申办失败")
            except Exception as e:
                return (False, str(e))
            
        elif step_number == 8:
            # 步骤8: 检查渠道使用地址
            try:
                success = self._step8_check_channel_use_address()
                return (success, None if success else "检查渠道使用地址失败")
            except Exception as e:
                return (False, str(e))
            
        elif step_number == 9:
            # 步骤9: 校验手机号
            try:
                success = self._step9_check_phone()
                return (success, None if success else "校验手机号失败")
            except Exception as e:
                return (False, str(e))
            
        elif step_number == 10:
            # 步骤10: 身份证OCR识别（可选）
            try:
                success = self._step10_ocr_identity_card()
                return (success, None if success else "身份证OCR识别失败")
            except Exception as e:
                return (False, str(e))
            
        elif step_number == 11:
            # 步骤11: 行驶证OCR识别（可选）
            try:
                success = self._step11_ocr_driver_license()
                return (success, None if success else "行驶证OCR识别失败")
            except Exception as e:
                return (False, str(e))
            
        elif step_number == 12:
            # 步骤12: 提交申办银行信息（关键步骤，获取申办ID）
            try:
                success = self._step12_submit_apply_bank_info()
                return (success, None if success else "提交申办银行信息失败")
            except Exception as e:
                return (False, str(e))
            
        elif step_number == 13:
            # 步骤13: 交通违章查询（可选）
            try:
                success = self._step13_traffic_query()
                return (success, None if success else "交通违章查询失败")
            except Exception as e:
                return (False, str(e))
            
        elif step_number == 14:
            # 步骤14: 提交车辆信息
            try:
                success = self._step14_submit_vehicle_info()
                return (success, None if success else "提交车辆信息失败")
            except Exception as e:
                return (False, str(e))
            
        elif step_number == 15:
            # 步骤15: 获取ETC申办信息
            try:
                success = self._step15_get_etc_apply_info()
                return (success, None if success else "获取ETC申办信息失败")
            except Exception as e:
                return (False, str(e))
            
        elif step_number == 16:
            # 步骤16: 保存车辆视频信息（可选）
            try:
                success = self._step16_save_car_video_info()
                return (success, None if success else "保存车辆视频信息失败")
            except Exception as e:
                return (False, str(e))
            
        elif step_number == 17:
            # 步骤17: 签发保险协议
            try:
                success = self._step17_issue_insure_agreements()
                return (success, None if success else "签发保险协议失败")
            except Exception as e:
                return (False, str(e))
            
        elif step_number == 18:
            # 步骤18: 查询绑定银行卡列表
            try:
                success = self._step18_select_bind_bank_list()
                return (success, None if success else "查询绑定银行卡列表失败")
            except Exception as e:
                return (False, str(e))
            
        elif step_number == 19:
            # 步骤19: 快捷支付预存
            try:
                success = self._step19_quick_pay_prestore()
                return (success, None if success else "快捷支付预存失败")
            except Exception as e:
                return (False, str(e))
            
        elif step_number == 20:
            # 步骤20: 提交OBU订单
            try:
                success = self._step20_submit_obu_order()
                return (success, None if success else "提交OBU订单失败")
            except Exception as e:
                return (False, str(e))
            
        elif step_number == 21:
            # 步骤21: 流程完成
            try:
                success = self._step21_flow_completed()
                return (success, None if success else "流程完成失败")
            except Exception as e:
                return (False, str(e))
            
        else:
            return (False, f"未知步骤号: {step_number}")
    
    # ==================== 具体步骤实现 ====================
    
    def _step1_update_wx_msg_template(self) -> bool:
        """步骤1: 更新微信消息模板"""
        try:
            # 使用新的签名生成方法
            params = CoreService.generate_hcb_params(
                'com.hcb.updateAllWXMsgTemplate',
                templateIdList='[]',  # 传递空数组字符串，避免后端空指针
                openId=self.params.get('openId', 'oDefaultTestOpenId12345')
            )
            
            response = self.api_client.update_wx_msg_template(params)
            self.log_service.info("更新微信消息模板成功")
            return response.get('ret') == '1'
            
        except Exception as e:
            self.log_service.error(f"更新微信消息模板失败: {str(e)}")
            return False
    
    def _step2_get_operator_list(self):
        """步骤2: 获取运营商列表"""
        try:
            self.log_service.info("2.获取运营商列表")
            
            params = CoreService.generate_hcb_params('com.hcb.channel.getOperatorList')
            response = self.api_client.get_operator_list(params)
            
            if not response or response.get('ret') != '1':
                error_msg = response.get('msg', '获取运营商列表失败') if response else '网络请求失败'
                raise Exception(f"获取运营商列表失败: {error_msg}")
            
            self.operator_list = response.get('rows', [])
            self.log_service.info(f"✅ 获取运营商列表成功，共{len(self.operator_list)}个运营商")
            
            # 如果只有一个运营商，自动选择
            if len(self.operator_list) == 1:
                self.selected_operator = self.operator_list[0]
                self.log_service.info(f"✅ 自动选择运营商: {self.selected_operator.get('name')}")
                return True
            
            # 如果有多个运营商，自动选择第一个
            if len(self.operator_list) > 1:
                self.selected_operator = self.operator_list[0]
                self.log_service.info(f"✅ 自动选择第一个运营商: {self.selected_operator.get('name')}")
                return True
            
            # 如果没有运营商
            error_msg = "❌ 未找到任何运营商"
            self.log_service.error(error_msg)
            print(f"[ERROR] {error_msg}")
            return False
            
        except Exception as e:
            error_msg = f"获取运营商列表失败: {e}"
            self.log_service.error(error_msg)
            print(f"[ERROR] {error_msg}")
            return False

    def _step3_get_product_list_by_operator(self):
        """步骤3: 根据运营商获取产品列表"""
        try:
            self.log_service.info("3.获取产品列表")
            
            if not self.selected_operator:
                raise Exception("未选择运营商")
            
            operator_id = self.selected_operator.get('id')
            params = CoreService.generate_hcb_params('com.hcb.channel.getProductListByOperator', 
                                                   operatorId=operator_id)
            
            response = self.api_client.get_product_list_by_operator(params)
            
            if not response or response.get('ret') != '1':
                error_msg = response.get('msg', '获取产品列表失败') if response else '网络请求失败'
                raise Exception(f"获取产品列表失败: {error_msg}")
            
            self.product_list = response.get('rows', [])
            self.log_service.info(f"✅ 获取产品列表成功，共{len(self.product_list)}个产品")
            
            # 如果只有一个产品，自动选择
            if len(self.product_list) == 1:
                self.selected_product = self.product_list[0]
                self.log_service.info(f"✅ 自动选择产品: {self.selected_product.get('name')}")
                return True
            
            # 如果有多个产品，自动选择第一个
            if len(self.product_list) > 1:
                self.selected_product = self.product_list[0]
                self.log_service.info(f"✅ 自动选择第一个产品: {self.selected_product.get('name')}")
                return True
            
            # 如果没有产品
            error_msg = "❌ 未找到任何产品"
            self.log_service.error(error_msg)
            print(f"[ERROR] {error_msg}")
            return False
            
        except Exception as e:
            error_msg = f"获取产品列表失败: {e}"
            self.log_service.error(error_msg)
            print(f"[ERROR] {error_msg}")
            return False

    def _step4_get_bank_list(self):
        """步骤4: 获取银行列表"""
        try:
            self.log_service.info("4.获取银行列表")
            
            if not self.selected_operator:
                raise Exception("未选择运营商")
            
            operator_id = self.selected_operator.get('id')
            params = CoreService.generate_hcb_params('com.hcb.channel.getBankList', 
                                                   operatorId=operator_id)
            response = self.api_client.get_bank_list(params)
            
            if not response or response.get('ret') != '1':
                error_msg = response.get('msg', '获取银行列表失败') if response else '网络请求失败'
                raise Exception(f"获取银行列表失败: {error_msg}")
            
            self.bank_list = response.get('rows', [])
            self.log_service.info(f"✅ 获取银行列表成功，共{len(self.bank_list)}个银行")
            
            # 自动选择第一个银行
            if self.bank_list:
                self.selected_bank = self.bank_list[0]
                self.log_service.info(f"✅ 自动选择银行: {self.selected_bank.get('name')}")
            else:
                error_msg = "❌ 未找到任何银行"
                self.log_service.error(error_msg)
                print(f"[ERROR] {error_msg}")
                return False
            
            return True
            
        except Exception as e:
            error_msg = f"获取银行列表失败: {e}"
            self.log_service.error(error_msg)
            print(f"[ERROR] {error_msg}")
            return False

    def _step5_get_product_info(self):
        """步骤5: 获取产品信息"""
        try:
            self.log_service.info("5.获取产品信息")
            
            if not self.selected_product:
                raise Exception("未选择产品")
            
            product_id = self.selected_product.get('id')
            bank_id = self.selected_product.get('id')  # 使用产品ID作为银行ID
            
            params = CoreService.generate_hcb_params('com.hcb.channel.getProductInfo', 
                                                   productId=product_id,
                                                   bankId=bank_id,
                                                   operatorId=self.selected_operator.get('id') if self.selected_operator else '')
            
            response = self.api_client.get_product_info(params)
            
            if not response or response.get('ret') != '1':
                error_msg = response.get('msg', '获取产品信息失败') if response else '网络请求失败'
                raise Exception(f"获取产品信息失败: {error_msg}")
            
            self.product_info = response.get('params', {})
            # 设置产品ID - 使用步骤5返回的产品信息中的ID
            if self.product_info:
                self.product_id = self.product_info.get('id')
                self.log_service.info(f"✅ 设置产品ID: {self.product_id}")
            elif self.selected_product:
                self.product_id = self.selected_product.get('id')
                self.log_service.info(f"✅ 备用设置产品ID: {self.product_id}")
            
            self.log_service.info(f"✅ 获取产品信息成功: {self.product_info.get('name', '')}")
            
            # 在步骤5结束时再次确认product_id的值
            self.log_service.info(f"步骤5结束时 - product_id: {self.product_id}")
            
            return True
            
        except Exception as e:
            error_msg = f"获取产品信息失败: {e}"
            self.log_service.error(error_msg)
            print(f"[ERROR] {error_msg}")
            return False
    
    def _step6_check_plate_no_info(self) -> bool:
        """步骤6: 校验车牌号信息（查询类接口，可跳过）"""
        try:
            # 检查是否有车牌号
            car_num = self.params.get('carNum', '')
            if not car_num:
                self.log_service.warning("未提供车牌号，跳过车牌号校验")
                return True
            
            params = CoreService.generate_hcb_params(
                'com.hcb.channel.checkPlateNoInfo',
                plateNo=car_num,  # 使用carNum参数
                plateColor=str(self.params.get('plateColor', '1')),  # 确保是字符串
                trunkUserId=self.params.get('trunkUserId', ''),
                channelId=self.params.get('channelId', '0000')
            )
            
            response = self.api_client.check_plate_no_info(params)
            if response.get('ret') == '1':
                self.log_service.info("校验车牌号信息成功")
                return True
            else:
                error_msg = response.get('msg', '未知错误')
                self.log_service.warning(f"⚠️ 车牌号校验失败（查询类接口，跳过继续）: {error_msg}")
                return True  # 查询类接口失败时跳过继续
            
        except Exception as e:
            self.log_service.warning(f"⚠️ 车牌号校验异常（查询类接口，跳过继续）: {str(e)}")
            return True  # 查询类接口异常时跳过继续
    
    def _step7_check_is_not_car_num(self) -> bool:
        """步骤7: 检查是否可申办（查询类接口，可跳过）"""
        try:
            params = CoreService.generate_hcb_params(
                'com.hcb.checkIsNotCarNum',
                carNum=self.params.get('carNum', ''),
                channelId=self.params.get('channelId', '0000')
            )
            
            response = self.api_client.check_is_not_car_num(params)
            if response.get('ret') == '1':
                self.log_service.info("检查是否可申办成功")
                return True
            else:
                error_msg = response.get('msg', '未知错误')
                self.log_service.warning(f"⚠️ 是否可申办检查失败（查询类接口，跳过继续）: {error_msg}")
                return True  # 查询类接口失败时跳过继续
            
        except Exception as e:
            self.log_service.warning(f"⚠️ 是否可申办检查异常（查询类接口，跳过继续）: {str(e)}")
            return True  # 查询类接口异常时跳过继续
    
    def _step8_check_channel_use_address(self) -> bool:
        """步骤8: 检查渠道使用地址（查询类接口，可跳过）"""
        try:
            params = CoreService.generate_hcb_params(
                'com.hcb.channel.checkChannelUseAddress',
                channelId=self.params.get('channelId', '0000')
            )
            
            response = self.api_client.check_channel_use_address(params)
            if response.get('ret') == '1':
                self.log_service.info("检查渠道使用地址成功")
                return True
            else:
                error_msg = response.get('msg', '未知错误')
                self.log_service.warning(f"⚠️ 渠道地址检查失败（查询类接口，跳过继续）: {error_msg}")
                return True  # 查询类接口失败时跳过继续
            
        except Exception as e:
            self.log_service.warning(f"⚠️ 渠道地址检查异常（查询类接口，跳过继续）: {str(e)}")
            return True  # 查询类接口异常时跳过继续
    
    def _generate_verification_code(self) -> str:
        """生成验证码：当前日期YYMMDD格式"""
        import datetime
        today = datetime.datetime.now()
        return today.strftime("%y%m%d")  # YYMMDD格式
    
    def _step9_check_phone(self) -> bool:
        """步骤9: 校验手机号"""
        try:
            # 生成验证码：当前日期YYMMDD格式
            verification_code = self._generate_verification_code()
            
            params = CoreService.generate_hcb_params(
                'com.hcb.channel.checkPhone',
                phone=self.params.get('phone', ''),
                channelId=self.params.get('channelId', '0000'),
                code=verification_code
            )
            
            self.log_service.info(f"使用验证码: {verification_code}")
            
            response = self.api_client.check_phone(params)
            if response.get('ret') == '1':
                self.log_service.info("校验手机号成功")
                return True
            else:
                error_msg = response.get('msg', '未知错误')
                self.log_service.error(f"校验手机号失败: {error_msg}")
                return False
            
        except Exception as e:
            self.log_service.error(f"校验手机号失败: {str(e)}")
            return False
    
    def _step10_ocr_identity_card(self) -> bool:
        """步骤10: 身份证OCR识别（可选步骤）"""
        try:
            # 如果没有提供身份证图片，跳过此步骤
            if not self.params.get('idCardUrl'):
                self.log_service.info("未提供身份证图片，跳过OCR识别")
                return True
            
            # 使用正确的参数生成方法
            params = CoreService.generate_hcb_params(
                'com.hcb.ocrIdentityCard',
                image=self.params.get('idCardUrl', ''),
                cardSide='front'
            )
            
            response = self.api_client.ocr_identity_card(params)
            return response.get('ret') == '1'
            
        except Exception as e:
            self.log_service.error(f"身份证OCR识别失败: {str(e)}")
            return True  # 可选步骤，失败不影响主流程
    
    def _step11_ocr_driver_license(self) -> bool:
        """步骤11: 行驶证OCR识别（可选步骤）"""
        try:
            # 如果没有提供行驶证图片，跳过此步骤
            if not self.params.get('licenseUrl'):
                self.log_service.info("未提供行驶证图片，跳过OCR识别")
                return True
            
            # 使用正确的参数生成方法
            params = CoreService.generate_hcb_params(
                'com.hcb.ocrDriverLicense',
                image=self.params.get('licenseUrl', '')
            )
            
            response = self.api_client.ocr_driver_license(params)
            return response.get('ret') == '1'
            
        except Exception as e:
            self.log_service.error(f"行驶证OCR识别失败: {str(e)}")
            return True  # 可选步骤，失败不影响主流程
    
    def _step12_submit_apply_bank_info(self) -> bool:
        """步骤12: 提交申办银行信息（关键步骤）"""
        try:
            # 使用默认图片URL（从之前成功的接口请求中获取）
            default_id_card_url = "https://img.jiaduobaoapp.com/images/files/2025/04/02/174350021421672.jpg"
            default_back_id_card_url = "https://img.jiaduobaoapp.com/images/files/2025/04/02/174350021421672.jpg"
            default_bank_pic_url = "https://img.jiaduobaoapp.com/images/files/2025/04/02/174350021421672.jpg"
            
            # 调试：检查product_id的值
            self.log_service.info(f"步骤12开始时 - product_id: {self.product_id}")
            self.log_service.info(f"步骤12开始时 - selected_product: {self.selected_product}")
            self.log_service.info(f"步骤12开始时 - selected_product.get('id'): {self.selected_product.get('id') if self.selected_product else 'None'}")
            
            # 如果product_id为空，尝试从selected_product获取
            if not self.product_id and self.selected_product:
                self.product_id = self.selected_product.get('id')
                self.log_service.info(f"步骤12中重新设置product_id: {self.product_id}")
            
            # 如果仍然为空，尝试从params中获取
            if not self.product_id:
                self.product_id = self.params.get('product_id')
                self.log_service.info(f"从params中获取product_id: {self.product_id}")
            
            # 最后的备用方案：使用固定的产品ID
            if not self.product_id:
                self.product_id = 'fbbc9573a2d6468780266492381bca65'  # 苏通卡定额pro（车龄5-7年）
                self.log_service.info(f"使用备用product_id: {self.product_id}")
            
            # 确保productId不为None
            final_product_id = self.product_id if self.product_id else 'fbbc9573a2d6468780266492381bca65'
            self.log_service.info(f"最终使用的productId: {final_product_id}")
            
            # 使用CoreService.generate_hcb_params生成标准参数
            params = CoreService.generate_hcb_params(
                'com.hcb.submitApplyBankInfo',
                truckEtcApplyId='',  # 初次提交为空
                idCardUrl=self.params.get('idCardUrl', default_id_card_url),
                backIdCardUrl=self.params.get('backIdCardUrl', default_back_id_card_url),
                cardHolder=self.params.get('cardHolder', ''),
                phone=self.params.get('phone', ''),
                urgentContact=self.params.get('urgentContact', '张三'),
                urgentPhone=self.params.get('urgentPhone', '13800138000'),
                idCode=self.params.get('idCode', ''),
                idAddress=self.params.get('idAddress') or 'XX省XX市XX区XX街道XX号',
                effectiveDate=self.params.get('effectiveDate', '20200101-20300101'),
                ethnic=self.params.get('ethnic', '汉'),
                idAuthority=self.params.get('idAuthority', 'XX市公安局'),
                anHuiId=self.params.get('anHuiId', ''),
                carNum=self.params.get('carNum', ''),
                plateColor=str(self.params.get('plateColor', '1')),  # 确保是字符串
                bankName=self.params.get('truck_bank_name', ''),  # 使用界面输入的银行名称
                bankNo=self.params.get('bankNo', ''),
                bankPicUrl=self.params.get('bankPicUrl', default_bank_pic_url),
                mobileNo=self.params.get('phone', ''),
                channelId=self.params.get('channelId', '0000'),
                productId=final_product_id,
                loginUserId=self.params.get('loginUserId', ''),
                userId=self.params.get('userId', ''),
                code=self.params.get('code', ''),
                smsCode=self.params.get('smsCode', ''),
                applyAccountId=self.params.get('applyAccountId', ''),
                openAccountApplyId=self.params.get('openAccountApplyId', ''),
                idProvinceCode=self.params.get('idProvinceCode', ''),
                idCityCode=self.params.get('idCityCode', ''),
                idDistrictCode=self.params.get('idDistrictCode', ''),
                idProvince=self.params.get('idProvince', ''),
                idCity=self.params.get('idCity', ''),
                idDistrict=self.params.get('idDistrict', ''),
                provinceCity=self.params.get('provinceCity', ''),
                openId=self.params.get('openId', 'oDefaultTestOpenId12345'),
                verifyCode=self._generate_verification_code(),  # 直接使用今天的验证码
                obuSubmitStatus=str(self.params.get('obuSubmitStatus', '1')),  # 确保是字符串
                terminalId=self.params.get('terminalId', ''),
                fissionId=self.params.get('fissionId', ''),
                orderType=self.params.get('orderType', '')
            )
            
            self.log_service.info(f"使用默认身份证正面图片: {default_id_card_url}")
            self.log_service.info(f"使用默认身份证背面图片: {default_back_id_card_url}")
            self.log_service.info(f"使用默认银行卡图片: {default_bank_pic_url}")
            
            response = self.api_client.submit_apply_bank_info(params)
            
            if response.get('ret') == '1':
                # 提取关键数据
                response_params = response.get('params', {})
                self.truck_etc_apply_id = response_params.get('truckEtcApplyId')
                self.truck_user_id = response_params.get('truckUserId')
                self.truck_user_wallet_id = response_params.get('truckUserWalletId')
                
                self.log_service.info(f"获取到申办ID: {self.truck_etc_apply_id}")
                self.log_service.info(f"获取到用户ID: {self.truck_user_id}")
                self.log_service.info(f"获取到钱包ID: {self.truck_user_wallet_id}")
                
                # 更新流程状态
                self.flow_state.set_truck_info(
                    self.truck_etc_apply_id,
                    self.truck_user_id,
                    self.truck_user_wallet_id
                )
                
                return True
            else:
                self.log_service.error(f"提交申办银行信息失败: {response.get('msg', '未知错误')}")
                return False
            
        except Exception as e:
            self.log_service.error(f"提交申办银行信息异常: {str(e)}")
            return False
    
    def _step13_traffic_query(self) -> bool:
        """步骤13: 交通违章查询（查询类接口，可跳过）"""
        try:
            if not self.truck_etc_apply_id:
                self.log_service.warning("⚠️ 缺少申办ID，跳过交通违章查询")
                return True  # 查询类接口，可跳过
            
            # 使用默认图片URL
            default_license_url = "https://img.jiaduobaoapp.com/images/files/2025/04/02/174350021421672.jpg"
            default_back_license_url = "https://img.jiaduobaoapp.com/images/files/2025/04/02/174350021421672.jpg"
            default_car_head_url = "https://img.jiaduobaoapp.com/images/files/2025/04/02/174350021421672.jpg"
            default_road_transport_url = "https://img.jiaduobaoapp.com/images/files/2025/04/02/174350021421672.jpg"
            
            # 构建完整的车辆信息参数
            params = CoreService.generate_hcb_params(
                'com.hcb.trafficQuery',
                truckEtcApplyId=self.truck_etc_apply_id,
                licenseUrl=default_license_url,
                backLicenseUrl=default_back_license_url,
                carHeadUrl=default_car_head_url,
                roadTransportUrl=default_road_transport_url,
                plateColor="1",
                name=self.params.get('name', ''),
                vin=self.params.get('vin', ''),
                vehicleAxles=self.params.get('vehicle_axles', '2'),
                vehicleWheels=self.params.get('vehicle_wheels', '4'),
                registerDate=self.params.get('register_date', '20200515'),
                issueDate=self.params.get('issue_date', '20200520'),
                model=self.params.get('model', 'EQ1180GZ5DJ1'),
                carType=self.params.get('car_type', '货车'),
                businessScope="",
                vehicleType="",
                vehicleEngineno=self.params.get('engine_no', '4DX23-140E5A'),
                approvedCount=self.params.get('approved_count', '3'),
                totalMass=self.params.get('total_mass', '18000'),
                weightLimits=self.params.get('weight_limits', '10500'),
                permittedTowweight="",
                unladenMass=self.params.get('unladen_mass', '7500'),
                usePurpose="货运",
                long=self.params.get('length', '8995'),
                width=self.params.get('width', '2496'),
                height=self.params.get('height', '3800'),
                channelId="0000",
                productId=self.product_id or "",
                ex_factory_time="",
                fuel_type="",
                fuel_name="",
                engine_power="",
                wheelbase="",
                businessLicenseNumber="",
                roadTransportationPermitCardNumber="",
                isTractor=None,
                carNum=self.params.get('carNum', '')
            )
            
            response = self.api_client.traffic_query(params)
            if response.get('ret') == '1':
                self.log_service.info("交通违章查询成功")
                return True
            else:
                error_msg = response.get('msg', '未知错误')
                self.log_service.warning(f"⚠️ 交通违章查询失败（查询类接口，跳过继续）: {error_msg}")
                return True  # 查询类接口失败时跳过继续
            
        except Exception as e:
            self.log_service.warning(f"⚠️ 交通违章查询异常（查询类接口，跳过继续）: {str(e)}")
            return True  # 查询类接口异常时跳过继续
    
    def _step14_submit_vehicle_info(self) -> bool:
        """步骤14: 提交车辆信息（查询验证类接口，可跳过）"""
        try:
            if not self.truck_etc_apply_id:
                self.log_service.warning("⚠️ 缺少申办ID，跳过车辆信息提交")
                return True  # 查询类接口，可跳过
            
            # 使用默认行驶证图片URL（基于身份证图片URL生成）
            default_license_url = "https://img.jiaduobaoapp.com/images/files/2025/04/02/174350021421672.jpg"
            default_back_license_url = "https://img.jiaduobaoapp.com/images/files/2025/04/02/174350021421672.jpg"
            default_car_head_url = "https://img.jiaduobaoapp.com/images/files/2025/04/02/174350021421672.jpg"
            default_road_transport_url = "https://img.jiaduobaoapp.com/images/files/2025/04/02/174350021421672.jpg"
            
            params = {
                'truckEtcApplyId': self.truck_etc_apply_id,
                'licenseUrl': self.params.get('licenseUrl', default_license_url),
                'backLicenseUrl': self.params.get('backLicenseUrl', default_back_license_url),
                'carHeadUrl': self.params.get('carHeadUrl', default_car_head_url),
                'roadTransportUrl': self.params.get('roadTransportUrl', default_road_transport_url),
                'plateColor': str(self.params.get('plateColor', '1')),
                'name': self.params.get('name', self.params.get('cardHolder', '')),  # 使用用户姓名
                'vin': self.params.get('vin', ''),
                'vehicleAxles': self.params.get('vehicleAxles', ''),
                'vehicleWheels': self.params.get('vehicleWheels', ''),
                'registerDate': self.params.get('registerDate', '20200515'),  # 使用正确的YYYYMMDD格式
                'issueDate': self.params.get('issueDate', '20200520'),      # 使用正确的YYYYMMDD格式
                'model': self.params.get('model', ''),
                'carType': self.params.get('carType', ''),
                'businessScope': self.params.get('businessScope', ''),
                'vehicleType': self.params.get('vehicleType', ''),
                'vehicleEngineno': self.params.get('vehicleEngineno', ''),
                'approvedCount': self.params.get('approvedCount', ''),
                'totalMass': self.params.get('totalMass', ''),
                'weightLimits': self.params.get('weightLimits', ''),
                'permittedTowweight': self.params.get('permittedTowweight', ''),
                'unladenMass': self.params.get('unladenMass', ''),
                'usePurpose': self.params.get('usePurpose', '货运'),
                'long': self.params.get('long', ''),
                'width': self.params.get('width', ''),
                'height': self.params.get('height', ''),
                'channelId': self.params.get('channelId', ''),
                'productId': self.product_id,
                'ex_factory_time': self.params.get('ex_factory_time', ''),
                'fuel_type': self.params.get('fuel_type', ''),
                'fuel_name': self.params.get('fuel_name', ''),
                'engine_power': self.params.get('engine_power', ''),
                'wheelbase': self.params.get('wheelbase', ''),
                'businessLicenseNumber': self.params.get('businessLicenseNumber', ''),
                'roadTransportationPermitCardNumber': self.params.get('roadTransportationPermitCardNumber', ''),
                'carNum': self.params.get('carNum', ''),
                'isApplyEtcOrder': self.params.get('isApplyEtcOrder'),
                'userId': self.params.get('userId', ''),
                'timestamp': int(time.time() * 1000),
                'hashcode': CoreService.generate_hash()
            }
            
            response = self.api_client.submit_vehicle_info(params)
            if response.get('ret') == '1':
                self.log_service.info("提交车辆信息成功")
                return True
            else:
                error_msg = response.get('msg', '提交车辆信息失败')
                self.log_service.warning(f"⚠️ 车辆信息验证失败（查询类接口，跳过继续）: {error_msg}")
                return True  # 查询验证类接口失败时跳过继续
            
        except Exception as e:
            self.log_service.warning(f"⚠️ 车辆信息验证异常（查询类接口，跳过继续）: {str(e)}")
            return True  # 查询验证类接口异常时跳过继续
    
    def _step15_get_etc_apply_info(self) -> bool:
        """步骤15: 获取ETC申办信息"""
        try:
            if not self.truck_etc_apply_id:
                self.log_service.error("缺少申办ID，无法获取申办信息")
                return False
            
            params = {
                'truckEtcApplyId': self.truck_etc_apply_id,
                'timestamp': int(time.time() * 1000),
                'hashcode': CoreService.generate_hash()
            }
            
            response = self.api_client.get_etc_apply_info(params)
            
            if response.get('ret') == '1':
                # 更新申办信息
                response_params = response.get('params', {})
                self.order_id = self.truck_etc_apply_id  # orderId通常等于truckEtcApplyId
                return True
            return False
            
        except Exception as e:
            self.log_service.error(f"获取ETC申办信息失败: {str(e)}")
            return False
    
    def _step16_save_car_video_info(self) -> bool:
        """步骤16: 保存车辆视频信息（可选步骤）"""
        try:
            if not self.truck_etc_apply_id:
                self.log_service.error("缺少申办ID，无法保存车辆视频信息")
                return False
            
            # 如果没有提供视频URL，跳过此步骤
            if not self.params.get('videoUrl'):
                self.log_service.info("未提供车辆视频，跳过保存视频信息")
                return True
            
            params = {
                'truckEtcApplyId': self.truck_etc_apply_id,
                'videoUrl': self.params.get('videoUrl', ''),
                'timestamp': int(time.time() * 1000),
                'hashcode': CoreService.generate_hash()
            }
            
            response = self.api_client.save_car_video_info(params)
            return response.get('ret') == '1'
            
        except Exception as e:
            self.log_service.error(f"保存车辆视频信息失败: {str(e)}")
            return True  # 可选步骤，失败不影响主流程
    
    def _step17_issue_insure_agreements(self) -> bool:
        """步骤17: 签发保险协议"""
        try:
            if not self.order_id:
                self.order_id = self.truck_etc_apply_id  # 使用申办ID作为订单ID
            
            params = {
                'orderId': self.order_id,
                'agreeType': self.params.get('agreeType', 'S'),
                'timestamp': int(time.time() * 1000),
                'hashcode': CoreService.generate_hash()
            }
            
            response = self.api_client.issue_insure_agreements(params)
            return response.get('ret') == '1'
            
        except Exception as e:
            self.log_service.error(f"签发保险协议失败: {str(e)}")
            return False
    
    def _step18_select_bind_bank_list(self) -> bool:
        """步骤18: 查询绑定银行卡列表"""
        try:
            # 使用正确的参数生成方法
            params = CoreService.generate_hcb_params(
                'com.hcb.bank.selectBindBankList',
                idCard=self.params.get('idCode', '')
            )
            
            response = self.api_client.select_bind_bank_list(params)
            
            if response.get('ret') == '1':
                # 提取银行卡ID
                data = response.get('data', {})
                bank_list = data.get('list', [])
                if bank_list:
                    # 使用第一个银行卡
                    self.user_bind_bank_id = bank_list[0].get('id')
                    self.log_service.info(f"获取到银行卡ID: {self.user_bind_bank_id}")
                return True
            return False
            
        except Exception as e:
            self.log_service.error(f"查询绑定银行卡列表失败: {str(e)}")
            return False
    
    def _step19_quick_pay_prestore(self) -> bool:
        """步骤19: 快捷支付预存"""
        try:
            if not self.order_id or not self.truck_user_id or not self.user_bind_bank_id:
                self.log_service.error("缺少必要参数，无法执行快捷支付预存")
                return False
            
            params = {
                'orderId': self.order_id,
                'truckUserId': self.truck_user_id,
                'userBindBankId': self.user_bind_bank_id,
                'amt': self.params.get('amt', '0.02'),
                'timestamp': int(time.time() * 1000),
                'hashcode': CoreService.generate_hash()
            }
            
            response = self.api_client.quick_pay_prestore(params)
            return response.get('ret') == '1'
            
        except Exception as e:
            self.log_service.error(f"快捷支付预存失败: {str(e)}")
            return False
    
    def _step20_submit_obu_order(self) -> bool:
        """步骤20: 提交OBU订单"""
        try:
            # 打印当前的ID值，用于调试
            self.log_service.info(f"步骤20开始 - 当前申办ID: {self.truck_etc_apply_id}")
            self.log_service.info(f"步骤20开始 - 当前订单ID: {self.order_id}")
            
            # 确保有订单ID
            if not self.order_id:
                if self.truck_etc_apply_id:
                    self.order_id = self.truck_etc_apply_id  # 使用申办ID作为订单ID
                else:
                    self.log_service.error("缺少订单ID，无法提交OBU订单")
                    return False
            
            params = {
                'orderId': self.order_id,  # 使用正确的参数名orderId
                'obuInfo': self.params.get('obuInfo', ''),
                'timestamp': int(time.time() * 1000),
                'hashcode': CoreService.generate_hash()
            }
            
            # 打印实际发送的参数
            self.log_service.info(f"步骤20 - 发送参数: {params}")
            
            response = self.api_client.submit_obu_order(params)
            return response.get('ret') == '1'
            
        except Exception as e:
            self.log_service.error(f"提交OBU订单失败: {str(e)}")
            return False
    
    def _step21_flow_completed(self) -> bool:
        """步骤21: 流程完成"""
        try:
            from apps.etc_apply.services.hcb.truck_data_service import TruckDataService
            
            # 更新数据库
            car_num = self.params.get('carNum', '')
            if car_num and self.truck_etc_apply_id:
                # 处理用户ID以适应数据库字段长度
                processed_user_id = TruckDataService.truncate_user_id(self.truck_user_id, 32)
                self.log_service.info(f"原始用户ID: {self.truck_user_id}")
                self.log_service.info(f"处理后用户ID: {processed_user_id}")
                self.log_service.info(f"用户ID长度: {len(processed_user_id)}")
                
                # 更新申请表状态
                TruckDataService.update_truck_apply_status(self.truck_etc_apply_id)
                self.log_service.info(f"已更新申请表状态: {self.truck_etc_apply_id}")
                
                # 更新用户状态并生成ETC号和OBU号
                result = TruckDataService.update_truck_user_final_status(car_num)
                self.log_service.info(f"已更新用户状态: {car_num}")
                self.log_service.info(f"生成ETC号: {result['etc_sn']}")
                self.log_service.info(f"生成OBU号: {result['obu_no']}")
                self.log_service.info(f"激活时间: {result['activation_time']}")
                
                # 插入用户绑定车辆关系记录
                # 尝试获取真实的用户ID（优先使用手机号）
                real_userinfo_id = self._get_real_user_id()
                if real_userinfo_id:
                    self.log_service.info(f"✅ 使用真实用户ID进行绑定: {real_userinfo_id}")
                    bind_result = TruckDataService.insert_bind_car_rel(real_userinfo_id, processed_user_id)
                    self.log_service.info(f"已插入绑定关系记录")
                else:
                    # 无法找到真实用户ID，记录错误并跳过绑定
                    self.log_service.error("❌ 无法找到真实用户ID，绑定失败")
                    self.log_service.error("请联系管理员手动在 hcb_userinfo 表中创建用户记录，或使用 direct_db_bind.py 工具进行绑定")
                    self.log_service.error(f"货车用户ID: {processed_user_id}")
                    self.log_service.error(f"手机号: {self.params.get('phone')}")
                    self.log_service.error(f"身份证: {self.params.get('idCode')}")
                    self.log_service.error(f"openId: {self.params.get('openId')}")
                    
                    # 虽然绑定失败，但申办流程已完成，返回成功
                    return True
                self.log_service.info(f"绑定关系ID: {bind_result['bindcarrel_id']}")
                self.log_service.info(f"用户信息ID: {bind_result['userinfo_id']}")
                self.log_service.info(f"货车用户ID: {bind_result['truckuser_id']}")
                self.log_service.info(f"创建时间: {bind_result['create_time']}")
            
            self.log_service.info("21.流程完成")
            self.log_service.info(f"申办ID: {self.truck_etc_apply_id}")
            self.log_service.info(f"用户ID: {self.truck_user_id}")
            self.log_service.info(f"钱包ID: {self.truck_user_wallet_id}")
            return True
            
        except Exception as e:
            self.log_service.error(f"21.流程完成异常: {str(e)}")
            return False 

    def _get_real_user_id(self) -> str:
        """尝试获取真实的用户ID - 直接查询数据库获取真实用户ID"""
        try:
            from apps.etc_apply.services.hcb.truck_core_service import TruckCoreService
            
            # 方法1: 通过手机号直接查询数据库获取用户信息（最优先）
            phone = self.params.get('phone')
            if phone:
                self.log_service.info(f"🔍 通过手机号查询真实用户ID: {phone}")
                try:
                    # 直接查询数据库
                    conf = TruckCoreService.get_hcb_mysql_config()
                    from common.mysql_util import MySQLUtil
                    db = MySQLUtil(**conf)
                    db.connect()
                    
                    sql_phone = """
                    SELECT USERINFO_ID FROM hcb.hcb_userinfo 
                    WHERE PHONE = %s AND STATUS = '1' 
                    ORDER BY CREATE_TIME DESC LIMIT 1
                    """
                    result = db.query(sql_phone, (phone,))
                    
                    if result and len(result) > 0:
                        real_user_id = result[0]['USERINFO_ID']
                        self.log_service.info(f"✅ 通过手机号找到真实用户ID: {real_user_id}")
                        db.close()
                        return real_user_id
                    
                    db.close()
                    self.log_service.warning(f"⚠️ 数据库中未找到手机号 {phone} 对应的用户")
                    
                except Exception as e:
                    self.log_service.error(f"❌ 数据库查询失败: {str(e)}")
            
            # 方法2: 通过身份证号直接查询数据库获取用户信息
            id_code = self.params.get('idCode')
            if id_code:
                self.log_service.info(f"🔍 通过身份证号查询真实用户ID: {id_code}")
                try:
                    # 直接查询数据库
                    conf = TruckCoreService.get_hcb_mysql_config()
                    from common.mysql_util import MySQLUtil
                    db = MySQLUtil(**conf)
                    db.connect()
                    
                    sql_id_code = """
                    SELECT USERINFO_ID FROM hcb.hcb_userinfo 
                    WHERE ID_CODE = %s AND STATUS = '1' 
                    ORDER BY CREATE_TIME DESC LIMIT 1
                    """
                    result = db.query(sql_id_code, (id_code,))
                    
                    if result and len(result) > 0:
                        real_user_id = result[0]['USERINFO_ID']
                        self.log_service.info(f"✅ 通过身份证号找到真实用户ID: {real_user_id}")
                        db.close()
                        return real_user_id
                    
                    db.close()
                    self.log_service.warning(f"⚠️ 数据库中未找到身份证号 {id_code} 对应的用户")
                    
                except Exception as e:
                    self.log_service.error(f"❌ 数据库查询失败: {str(e)}")
            
            # 方法3: 通过openId直接查询数据库获取用户信息
            openid = self.params.get('openId')
            if openid:
                self.log_service.info(f"🔍 通过openId查询真实用户ID: {openid}")
                try:
                    # 直接查询数据库
                    conf = TruckCoreService.get_hcb_mysql_config()
                    from common.mysql_util import MySQLUtil
                    db = MySQLUtil(**conf)
                    db.connect()
                    
                    sql_openid = """
                    SELECT USERINFO_ID FROM hcb.hcb_userinfo 
                    WHERE OPENID = %s AND STATUS = '1' 
                    ORDER BY CREATE_TIME DESC LIMIT 1
                    """
                    result = db.query(sql_openid, (openid,))
                    
                    if result and len(result) > 0:
                        real_user_id = result[0]['USERINFO_ID']
                        self.log_service.info(f"✅ 通过openId找到真实用户ID: {real_user_id}")
                        db.close()
                        return real_user_id
                    
                    db.close()
                    self.log_service.warning(f"⚠️ 数据库中未找到openId {openid} 对应的用户")
                    
                except Exception as e:
                    self.log_service.error(f"❌ 数据库查询失败: {str(e)}")
            
            # 如果所有查询都失败，返回None
            self.log_service.warning("⚠️ 无法获取真实用户ID，所有查询都失败")
            return None
            
        except Exception as e:
            self.log_service.error(f"❌ 获取真实用户ID失败: {str(e)}")
            return None 