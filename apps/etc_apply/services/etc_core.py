# -*- coding: utf-8 -*-
"""
申办江苏客车ETC流程自动化worker（流程主控，仅供logic.py等上层调用）
"""
from datetime import datetime
from apps.etc_apply.services.api_client import ApiClient
from apps.etc_apply.services.error_service import ErrorService
from apps.etc_apply.services.state_service import FlowState, StepManager


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

    # 分步方法
    def step1_check_car_num(self):
        try:
            result = self.api.check_car_num(self.params)
            ErrorService.assert_api_success(result, "校验车牌接口")
            self._update_progress(1, StepManager.format_step_message(1))
            return result
        except Exception as e:
            error_msg = ErrorService.format_error_message(1, "校验车牌", e)
            self._update_progress(1, error_msg)
            raise Exception(error_msg)

    def step2_check_is_not_car_num(self):
        try:
            result = self.api.check_is_not_car_num(self.params)
            ErrorService.assert_api_success(result, "校验是否可申办接口")
            self._update_progress(2, StepManager.format_step_message(2))
            return result
        except Exception as e:
            error_msg = ErrorService.format_error_message(2, "校验是否可申办", e)
            self._update_progress(2, error_msg)
            raise Exception(error_msg)

    def step3_get_channel_use_address(self):
        try:
            result = self.api.get_channel_use_address(self.params)
            ErrorService.assert_api_success(result, "获取渠道地址接口")
            self._update_progress(3, StepManager.format_step_message(3))
            return result
        except Exception as e:
            error_msg = ErrorService.format_error_message(3, "获取渠道地址", e)
            self._update_progress(3, error_msg)
            raise Exception(error_msg)

    def step4_get_optional_service_list(self):
        try:
            result = self.api.get_optional_service_list(self.params)
            ErrorService.assert_api_success(result, "获取可选服务接口")
            self._update_progress(4, StepManager.format_step_message(4))
            return result
        except Exception as e:
            error_msg = ErrorService.format_error_message(4, "获取可选服务", e)
            self._update_progress(4, error_msg)
            raise Exception(error_msg)

    def step5_submit_car_num(self):
        try:
            res = self.api.submit_car_num(self.params)
            ErrorService.assert_api_success(res, "提交车牌接口")
            order_id = ErrorService.safe_get_nested(res, ["data", "orderId"])
            self.state.order_id = order_id
            self._update_progress(5, StepManager.format_step_message(5))
            return res
        except Exception as e:
            error_msg = ErrorService.format_error_message(5, "提交车牌", e)
            self._update_progress(5, error_msg)
            raise Exception(error_msg)

    def step6_protocol_add(self):
        try:
            result = self.api.protocol_add(self.state.order_id, self.params)
            ErrorService.assert_api_success(result, "协议签署接口")
            self._update_progress(6, StepManager.format_step_message(6))
            return result
        except Exception as e:
            error_msg = ErrorService.format_error_message(6, "协议签署", e)
            self._update_progress(6, error_msg)
            raise Exception(error_msg)

    def step7_submit_identity_with_bank_sign(self):
        try:
            res = self.api.submit_identity_with_bank_sign(self.state.order_id, self.params)
            ErrorService.assert_api_success(res, "提交身份和银行卡信息接口")
            sign_order_id = ErrorService.safe_get_nested(res, ["data", "signOrderId"])
            verify_code_no = ErrorService.safe_get_nested(res, ["data", "verifyCodeNo"])
            self.state.set_order_info(self.state.order_id, sign_order_id, verify_code_no)
            # 保存etccardUserId，供后续步骤使用
            etccard_user_id = ErrorService.safe_get_nested(res, ["data", "etccardUserId"])
            if etccard_user_id:
                self.params["etccardUserId"] = etccard_user_id
            self._update_progress(7, StepManager.format_step_message(7))
            return res
        except Exception as e:
            error_msg = ErrorService.format_error_message(7, "提交身份和银行卡信息", e)
            self._update_progress(7, error_msg)
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
            ErrorService.assert_api_success(result, "签约校验接口")
            self._update_progress(8, StepManager.format_step_message(8))
            return result
        except Exception as e:
            error_msg = ErrorService.format_error_message(8, "签约校验", e)
            self._update_progress(8, error_msg)
            raise Exception(error_msg)

    def step9_save_vehicle_info(self, order_id=None):
        try:
            oid = order_id or self.state.order_id
            res = self.api.save_vehicle_info(self.params, oid)
            ErrorService.assert_api_success(res, "保存车辆信息接口")
            etccard_user_id = ErrorService.safe_get_nested(res, ["data", "etccardUserId"])
            if etccard_user_id:
                self.params["etccardUserId"] = etccard_user_id
            self._update_progress(9, StepManager.format_step_message(9))
            return res
        except Exception as e:
            error_msg = ErrorService.format_error_message(9, "保存车辆信息", e)
            self._update_progress(9, error_msg)
            raise Exception(error_msg)

    def step10_optional_service_update(self, order_id=None):
        try:
            oid = order_id or self.state.order_id
            result = self.api.optional_service_update(oid)
            ErrorService.assert_api_success(result, "可选服务更新接口")
            self._update_progress(10, StepManager.format_step_message(10))
            return result
        except Exception as e:
            error_msg = ErrorService.format_error_message(10, "可选服务更新", e)
            self._update_progress(10, error_msg)
            raise Exception(error_msg)

    def step11_withhold_pay(self, order_id=None, verify_code=None):
        try:
            oid = order_id or self.state.order_id
            # 代扣支付使用日期格式的验证码（YYMMDD格式，如250723）
            if verify_code is not None:
                code = verify_code
            else:
                # 生成当前日期的YYMMDD格式验证码
                code = datetime.now().strftime("%y%m%d")
            result = self.api.withhold_pay(self.params, oid, code)
            ErrorService.assert_api_success(result, "代扣支付接口")
            self._update_progress(11, StepManager.format_step_message(11))
            return result
        except Exception as e:
            error_msg = ErrorService.format_error_message(11, "代扣支付", e)
            self._update_progress(11, error_msg)
            raise Exception(error_msg)

    def step12_update_db_status(self):
        try:
            from apps.etc_apply.services.db_service import OrderDbService, CardUserDbService
            # 1. 申办订单状态修改
            OrderDbService.update_order_status(self.state.order_id)
            # 2. ETC用户状态修改
            car_num = self.params.get("car_num") or self.params.get("carNum")
            if not car_num:
                # 尝试从车牌组成部分构建车牌号
                plate_province = self.params.get("plate_province", "")
                plate_letter = self.params.get("plate_letter", "")
                plate_number = self.params.get("plate_number", "")
                if plate_province and plate_letter and plate_number:
                    from apps.etc_apply.services.business_service import BusinessService
                    car_num = BusinessService.build_car_num(plate_province, plate_letter, plate_number)
                    # 更新params中的车牌号
                    self.params["carNum"] = car_num
                    self.params["car_num"] = car_num
            
            if not car_num:
                raise ValueError("step12缺少车牌号参数，请检查车牌信息是否完整")
            
            CardUserDbService.update_card_user_status(car_num)
            self._update_progress(12, StepManager.format_step_message(12))
        except Exception as e:
            # 直接抛出原始异常，让上层处理
            raise e

    def step13_run_stock_in_flow(self):
        try:
            from apps.etc_apply.services.db_service import run_stock_in_flow, insert_device_stock, get_mysql_config
            from common.data_factory import DataFactory
            from datetime import datetime
            
            # 获取车牌号 - 支持多种参数名
            car_num = self.params.get("car_num") or self.params.get("carNum")
            if not car_num:
                # 尝试从车牌组成部分构建车牌号
                plate_province = self.params.get("plate_province", "")
                plate_letter = self.params.get("plate_letter", "")
                plate_number = self.params.get("plate_number", "")
                if plate_province and plate_letter and plate_number:
                    from apps.etc_apply.services.business_service import BusinessService
                    car_num = BusinessService.build_car_num(plate_province, plate_letter, plate_number)
                    # 更新params中的车牌号
                    self.params["carNum"] = car_num
                    self.params["car_num"] = car_num
            
            if not car_num:
                raise ValueError("step13缺少车牌号参数，请检查车牌信息是否完整")
            
            # 生成设备号
            obu_no = DataFactory.random_obn_number()
            etc_sn = DataFactory.random_etc_number()
            activation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 保存生成的设备号到params中，供step14使用
            self.params['obu_no'] = obu_no
            self.params['etc_sn'] = etc_sn
            self.params['activation_time'] = activation_time
            
            # 先插入设备库存数据
            device_result = insert_device_stock(car_num)
            
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
            config = get_mysql_config('hcb')
            run_stock_in_flow(config, dbname, table, obu_fields, obu_types, obu_rules, 1, obu_extras, None)
            
            self._update_progress(13, StepManager.format_step_message(13))
        except Exception as e:
            # 直接抛出原始异常，让上层处理
            raise e

    def step14_update_obu_info(self):
        try:
            from apps.etc_apply.services.db_service import CardUserDbService
            car_num = self.params.get("car_num") or self.params.get("carNum")
            if not car_num:
                # 尝试从车牌组成部分构建车牌号
                plate_province = self.params.get("plate_province", "")
                plate_letter = self.params.get("plate_letter", "")
                plate_number = self.params.get("plate_number", "")
                if plate_province and plate_letter and plate_number:
                    from apps.etc_apply.services.business_service import BusinessService
                    car_num = BusinessService.build_car_num(plate_province, plate_letter, plate_number)
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
            CardUserDbService.update_card_user_obu_info(car_num, obu_no, etc_sn, activation_time)
            self._update_progress(14, StepManager.format_step_message(14))
        except Exception as e:
            # 直接抛出原始异常，让上层处理
            raise e

    def step15_update_final_status(self):
        try:
            from apps.etc_apply.services.db_service import update_final_card_user_status
            car_num = self.params.get("car_num") or self.params.get("carNum")
            if not car_num:
                # 尝试从车牌组成部分构建车牌号
                plate_province = self.params.get("plate_province", "")
                plate_letter = self.params.get("plate_letter", "")
                plate_number = self.params.get("plate_number", "")
                if plate_province and plate_letter and plate_number:
                    from apps.etc_apply.services.business_service import BusinessService
                    car_num = BusinessService.build_car_num(plate_province, plate_letter, plate_number)
                    # 更新params中的车牌号
                    self.params["carNum"] = car_num
                    self.params["car_num"] = car_num
            if not car_num:
                raise ValueError("step15缺少车牌号参数，请检查车牌信息是否完整")
            
            self._update_progress(15, "15. 最终状态更新完成")
            update_final_card_user_status(car_num)
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
