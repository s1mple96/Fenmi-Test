# -*- coding: utf-8 -*-
"""
申办江苏客车ETC流程自动化worker（流程主控，仅供logic.py等上层调用）
"""
from datetime import datetime
from apps.etc_apply.services.rtx.api_client import ApiClient
from apps.etc_apply.services.rtx.core_service import CoreService
from apps.etc_apply.services.rtx.state_service import FlowState, StepManager
from apps.etc_apply.services.rtx.data_service import DataService


class Core:
    """
    【分层说明】
    只做流程主控和调度，不做底层接口请求、参数拼装、数据库校验。
    params参数必须由上层保证已校验和补全。
    """

    def __init__(self, params=None, progress_callback=None, base_url=None, browser_cookies=None):
        self.state = FlowState(progress_callback)
        self.params = params or {}
        self.state.set_params(self.params)
        self.base_url = base_url
        self.browser_cookies = browser_cookies
        # 新增：自动初始化api
        if self.base_url:
            self.api = ApiClient(self.base_url, cookies=self.browser_cookies)
        else:
            self.api = None

    def _update_progress(self, step_number: int, message: str):
        """更新进度"""
        # 如果是错误消息，只显示失败原因，不显示步骤详情
        if "失败" in message or "异常" in message or "错误" in message:
            # 提取失败原因，限制长度避免UI被撑大
            if ":" in message:
                error_reason = message.split(":", 1)[1].strip()
                # 限制错误消息长度，避免UI被撑大
                if len(error_reason) > 100:
                    error_reason = error_reason[:100] + "..."
                print(f"[ERROR] {error_reason}")
            else:
                # 限制错误消息长度
                if len(message) > 100:
                    message = message[:100] + "..."
                print(f"[ERROR] {message}")
        else:
            # 成功消息正常显示
            print(f"[INFO] {message}")
        self.state.update_progress(step_number, message)
    
    def _handle_api_error(self, step_number: int, step_name: str, error: Exception):
        """处理API错误，提供详细的错误信息"""
        error_msg = CoreService.format_error_message(step_number, step_name, error)
        
        # 检查是否有详细错误信息
        if hasattr(error, 'error_detail'):
            error_detail = error.error_detail
            
            # 通过进度回调传递错误信息到UI
            if self.state.progress_callback:
                # 如果进度回调支持错误处理，传递详细信息
                ui = None
                
                # 尝试多种方式获取UI对象
                if hasattr(self.state.progress_callback, '__self__'):
                    ui = self.state.progress_callback.__self__
                elif hasattr(self.state.progress_callback, 'ui'):
                    ui = self.state.progress_callback.ui
                
                if ui and hasattr(ui, 'show_api_error'):
                    # 使用CoreService的通用方法格式化错误信息
                    error_message = error_detail.get('error_message', str(error))
                    full_error_message = CoreService.format_api_error_with_details(error_message, error_detail)
                    
                    ui.show_api_error(
                        f"步骤{step_number}: {step_name}", 
                        full_error_message,
                        error_detail.get('error_code')
                    )
        
        self._update_progress(step_number, error_msg)
        return error_msg

    # 分步方法
    def step1_check_car_num(self):
        try:
            result = self.api.check_car_num(self.params)
            CoreService.assert_api_success(result, "校验车牌接口")
            self._update_progress(1, StepManager.format_step_message(1))
            return result
        except Exception as e:
            error_msg = self._handle_api_error(1, "校验车牌", e)
            raise Exception(error_msg)

    def step2_check_is_not_car_num(self):
        try:
            result = self.api.check_is_not_car_num(self.params)
            CoreService.assert_api_success(result, "校验是否可申办接口")
            self._update_progress(2, StepManager.format_step_message(2))
            return result
        except Exception as e:
            error_msg = self._handle_api_error(2, "校验是否可申办", e)
            raise Exception(error_msg)

    def step3_get_channel_use_address(self):
        try:
            result = self.api.get_channel_use_address(self.params)
            CoreService.assert_api_success(result, "获取渠道地址接口")
            self._update_progress(3, StepManager.format_step_message(3))
            return result
        except Exception as e:
            error_msg = self._handle_api_error(3, "获取渠道地址", e)
            raise Exception(error_msg)

    def step4_get_optional_service_list(self):
        try:
            result = self.api.get_optional_service_list(self.params)
            CoreService.assert_api_success(result, "获取可选服务接口")
            self._update_progress(4, StepManager.format_step_message(4))
            return result
        except Exception as e:
            error_msg = self._handle_api_error(4, "获取可选服务", e)
            raise Exception(error_msg)

    def step5_submit_car_num(self):
        try:
            res = self.api.submit_car_num(self.params)
            CoreService.assert_api_success(res, "提交车牌接口")
            order_id = CoreService.safe_get_nested(res, ["data", "orderId"])
            self.state.order_id = order_id
            self._update_progress(5, StepManager.format_step_message(5))
            return res
        except Exception as e:
            error_msg = self._handle_api_error(5, "提交车牌", e)
            raise Exception(error_msg)

    def step6_protocol_add(self):
        try:
            result = self.api.protocol_add(self.state.order_id, self.params)
            CoreService.assert_api_success(result, "协议签署接口")
            self._update_progress(6, StepManager.format_step_message(6))
            return result
        except Exception as e:
            error_msg = self._handle_api_error(6, "协议签署", e)
            raise Exception(error_msg)

    def step7_submit_identity_with_bank_sign(self):
        try:
            res = self.api.submit_identity_with_bank_sign(self.state.order_id, self.params)
            CoreService.assert_api_success(res, "提交身份和银行卡信息接口")
            sign_order_id = CoreService.safe_get_nested(res, ["data", "signOrderId"])
            verify_code_no = CoreService.safe_get_nested(res, ["data", "verifyCodeNo"])
            self.state.set_order_info(self.state.order_id, sign_order_id, verify_code_no)
            # 保存etccardUserId，供后续步骤使用
            etccard_user_id = CoreService.safe_get_nested(res, ["data", "etccardUserId"])
            if etccard_user_id:
                self.params["etccardUserId"] = etccard_user_id
            self._update_progress(7, StepManager.format_step_message(7))
            return res
        except Exception as e:
            error_msg = self._handle_api_error(7, "提交身份和银行卡信息", e)
            raise Exception(error_msg)

    def run_step7_get_code(self, order_id, sign_order_id):
        """
        发送短信验证码，返回 sign_order_id 和 verify_code_no
        """
        self.state.order_id = order_id
        self.state.sign_order_id = sign_order_id
        res = self.step7_submit_identity_with_bank_sign()
        return {
            "sign_order_id": self.state.sign_order_id,
            "verify_code_no": self.state.verify_code_no,
            "raw": res
        }

    def step8_sign_check(self, verify_code=None):
        try:
            code = verify_code if verify_code is not None else self.params.get("code", "")
            result = self.api.sign_check(self.params, code, self.state.verify_code_no, self.state.sign_order_id)
            CoreService.assert_api_success(result, "签约校验接口")
            self._update_progress(8, StepManager.format_step_message(8))
            return result
        except Exception as e:
            error_msg = self._handle_api_error(8, "签约校验", e)
            raise Exception(error_msg)

    def step9_save_vehicle_info(self, order_id=None):
        try:
            oid = order_id or self.state.order_id
            res = self.api.save_vehicle_info(self.params, oid)
            CoreService.assert_api_success(res, "保存车辆信息接口")
            etccard_user_id = CoreService.safe_get_nested(res, ["data", "etccardUserId"])
            if etccard_user_id:
                self.params["etccardUserId"] = etccard_user_id
            self._update_progress(9, StepManager.format_step_message(9))
            return res
        except Exception as e:
            error_msg = self._handle_api_error(9, "保存车辆信息", e)
            raise Exception(error_msg)

    def step10_optional_service_update(self, order_id=None):
        try:
            oid = order_id or self.state.order_id
            result = self.api.optional_service_update(oid)
            CoreService.assert_api_success(result, "可选服务更新接口")
            self._update_progress(10, StepManager.format_step_message(10))
            return result
        except Exception as e:
            error_msg = self._handle_api_error(10, "可选服务更新", e)
            raise Exception(error_msg)

    def step11_withhold_pay(self, order_id=None, verify_code=None):
        try:
            oid = order_id or self.state.order_id
            # 代扣支付使用日期格式的验证码（YYMMDD格式，如250723）
            if verify_code is not None:
                code = verify_code
            else:
                # 生成当前日期的YYMMDD格式验证码
                code = CoreService.generate_verify_code()
            result = self.api.withhold_pay(self.params, oid, code)
            CoreService.assert_api_success(result, "代扣支付接口")
            self._update_progress(11, StepManager.format_step_message(11))
            return result
        except Exception as e:
            error_msg = self._handle_api_error(11, "代扣支付", e)
            raise Exception(error_msg)

    def step12_update_db_status(self):
        try:
            # 1. 申办订单状态修改
            DataService.update_order_status(self.state.order_id)
            # 2. ETC用户状态修改
            car_num = self.params.get("car_num") or self.params.get("carNum")
            if not car_num:
                # 尝试从车牌组成部分构建车牌号
                plate_province = self.params.get("plate_province", "")
                plate_letter = self.params.get("plate_letter", "")
                plate_number = self.params.get("plate_number", "")
                if plate_province and plate_letter and plate_number:
                    car_num = CoreService.build_car_num(plate_province, plate_letter, plate_number)
                    # 更新params中的车牌号
                    self.params["carNum"] = car_num
                    self.params["car_num"] = car_num
            
            if not car_num:
                raise ValueError("step12缺少车牌号参数，请检查车牌信息是否完整")
            
            DataService.update_card_user_status(car_num)
            self._update_progress(12, StepManager.format_step_message(12))
        except Exception as e:
            # 直接抛出原始异常，让上层处理
            raise e

    def step13_run_stock_in_flow(self):
        try:
            from common.data_factory import DataFactory
            
            # 获取车牌号 - 支持多种参数名
            car_num = self.params.get("car_num") or self.params.get("carNum")
            if not car_num:
                # 尝试从车牌组成部分构建车牌号
                plate_province = self.params.get("plate_province", "")
                plate_letter = self.params.get("plate_letter", "")
                plate_number = self.params.get("plate_number", "")
                if plate_province and plate_letter and plate_number:
                    car_num = CoreService.build_car_num(plate_province, plate_letter, plate_number)
                    # 更新params中的车牌号
                    self.params["carNum"] = car_num
                    self.params["car_num"] = car_num
            
            if not car_num:
                raise ValueError("step13缺少车牌号参数，请检查车牌信息是否完整")
            
            # 注释掉原来的设备号生成，现在在insert_device_stock中生成
            """
            # 生成设备号
            obu_no = DataFactory.random_obn_number()
            etc_sn = DataFactory.random_etc_number()
            activation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 保存生成的设备号到params中，供step14使用
            self.params['obu_no'] = obu_no
            self.params['etc_sn'] = etc_sn
            self.params['activation_time'] = activation_time
            """
            
            # 先插入设备库存数据
            operator_id = self.params.get('operatorId')  # 获取运营商ID
            # 尝试获取运营商名称（客车申办场景下运营商名称通常在产品信息中）
            operator_name = self.params.get('operatorName') or self.params.get('operator_name')
            # 尝试获取运营商编码（客车的精确匹配优先选择）
            operator_code = self.params.get('operatorCode') or self.params.get('operator_code')
            
            # 如果没有运营商编码，尝试从选择的产品中获取
            if not operator_code:
                selected_product = self.params.get('selected_product')
                if selected_product:
                    operator_code = selected_product.get('operator_code')
                    print(f"[INFO] 从选择的产品获取运营商编码: {operator_code}")
            
            # 如果没有运营商名称，尝试从选择的产品中获取
            if not operator_name:
                # 尝试从选择的产品信息中获取运营商名称
                selected_product = self.params.get('selected_product')
                if selected_product:
                    operator_name = CoreService.get_operator_name_from_product(selected_product)
                    print(f"[INFO] 从选择的产品获取运营商名称: {operator_name}")
            
            # 如果还是没有运营商名称，尝试从运营商ID映射获取
            if not operator_name and operator_id:
                operator_name = CoreService._get_operator_name_by_id(operator_id)
                print(f"[INFO] 从运营商ID映射获取运营商名称: {operator_name}")
            
            device_result = DataService.insert_device_stock(car_num, operator_id, operator_name, operator_code)
            
            # 从device_result中获取生成的设备号，保存到params中供step14使用
            if device_result:
                obu_no = device_result.get('obn_no')  # insert_device_stock返回的是obn_no
                etc_sn = device_result.get('etc_no')   # insert_device_stock返回的是etc_no
                activation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # 保存到params中，供step14使用
                self.params['obu_no'] = obu_no
                self.params['etc_sn'] = etc_sn
                self.params['activation_time'] = activation_time
                
                print(f"[INFO] 设备号已保存: OBU={obu_no}, ETC={etc_sn}")
            
            # 注释掉原有的重复入库流程，避免覆盖我们的精确匹配结果
            # 原有的run_stock_in_flow会使用固定的CARD_OPERATORS规则，会覆盖我们的精确匹配
            """
            # 设置入库参数  
            dbname = "hcb"
            table = "hcb_newstock"
            obu_fields = ["NEWSTOCK_ID", "CARD_OPERATORS", "STATUS", "CAR_NUM", "STOCK_STATUS", "SOURCE", "REMARK", "CREATE_TIME", "DEVICE_CATEGORY", "INTERNAL_DEVICE_NO", "EXTERNAL_DEVICE_NO", "TYPE"]
            obu_types = ["str", "str", "str", "str", "str", "str", "str", "str", "str", "str", "str", "str"]
            obu_rules = ["uuid", "1", "1", "str", "0", "1", "激活设备不存在库存内", "now", "0", "str", "str", "0"]
            obu_extras = {
                "CAR_NUM": car_num,
                "INTERNAL_DEVICE_NO": obu_no,
                "EXTERNAL_DEVICE_NO": obu_no
            }
            
            # 执行入库流程
            config = CoreService.get_hcb_mysql_config()
            DataService.run_stock_in_flow(config, dbname, table, obu_fields, obu_types, obu_rules, 1, obu_extras, None)
            """
            
            print(f"[INFO] step13设备入库完成，使用精确匹配的运营商代码")
            
            self._update_progress(13, StepManager.format_step_message(13))
        except Exception as e:
            # 直接抛出原始异常，让上层处理
            raise e

    def step14_update_obu_info(self):
        try:
            car_num = self.params.get("car_num") or self.params.get("carNum")
            if not car_num:
                # 尝试从车牌组成部分构建车牌号
                plate_province = self.params.get("plate_province", "")
                plate_letter = self.params.get("plate_letter", "")
                plate_number = self.params.get("plate_number", "")
                if plate_province and plate_letter and plate_number:
                    car_num = CoreService.build_car_num(plate_province, plate_letter, plate_number)
                    # 更新params中的车牌号
                    self.params["carNum"] = car_num
                    self.params["car_num"] = car_num
            
            if not car_num:
                raise ValueError("step14缺少车牌号参数，请检查车牌信息是否完整")
            
            # 使用step13中已经生成的obu_no和etc_sn，而不是重新生成
            obu_no = self.params.get("obu_no")
            etc_sn = self.params.get("etc_sn")
            activation_time = self.params.get("activation_time")
            if not all([car_num, obu_no, etc_sn, activation_time]):
                raise ValueError("step14缺少必要参数，请检查step13是否正确执行")
            DataService.update_card_user_obu_info(car_num, obu_no, etc_sn, activation_time)
            self._update_progress(14, StepManager.format_step_message(14))
        except Exception as e:
            # 直接抛出原始异常，让上层处理
            raise e

    def step15_update_final_status(self):
        try:
            car_num = self.params.get("car_num") or self.params.get("carNum")
            if not car_num:
                # 尝试从车牌组成部分构建车牌号
                plate_province = self.params.get("plate_province", "")
                plate_letter = self.params.get("plate_letter", "")
                plate_number = self.params.get("plate_number", "")
                if plate_province and plate_letter and plate_number:
                    car_num = CoreService.build_car_num(plate_province, plate_letter, plate_number)
                    # 更新params中的车牌号
                    self.params["carNum"] = car_num
                    self.params["car_num"] = car_num
            if not car_num:
                raise ValueError("step15缺少车牌号参数，请检查车牌信息是否完整")
            
            self._update_progress(15, "15. 最终状态更新完成")
            DataService.update_final_card_user_status(car_num)
        except Exception as e:
            # 直接抛出原始异常，让上层处理
            raise e

    def run_step8_to_end(self, code, order_id, sign_order_id, verify_code_no):
        try:
            self.state.set_order_info(order_id, sign_order_id, verify_code_no)
            # step7已经在之前执行过了，这里直接使用已有的参数
            # 不需要重复调用step7_submit_identity_with_bank_sign()
            
            # 执行step8: 签约校验
            res8 = self.step8_sign_check(code)
            
            # 执行step9: 保存车辆信息
            res9 = self.step9_save_vehicle_info()
            
            # 执行step10: 可选服务更新
            res10 = self.step10_optional_service_update()
            
            # 执行step11: 代扣支付
            res11 = self.step11_withhold_pay()
            
            # 执行step12: 数据库状态修改
            self.step12_update_db_status()
            
            # 执行step13: 一键入库流程
            self.step13_run_stock_in_flow()
            
            # 执行step14: ETC卡用户OBU信息入库
            self.step14_update_obu_info()
            
            # 执行step15: 最终状态更新
            self.step15_update_final_status()
            
            # 流程完成
            self._update_progress(16, StepManager.format_step_message(16))
            print("[DEBUG] 全流程完成")
            return {
                "sign_check": res8,
                "save_vehicle_info": res9,
                "optional_service_update": res10,
                "withhold_pay": res11
            }
            
        except Exception as e:
            import traceback
            # 只显示失败原因，不显示详细步骤
            if ":" in str(e):
                error_reason = str(e).split(":", 1)[1].strip()
                print(f"[ERROR] {error_reason}")
            else:
                print(f"[ERROR] {str(e)}")
            # 不更新进度到16，保持当前失败步骤的进度
            raise Exception(str(e))
