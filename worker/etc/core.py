# -*- coding: utf-8 -*-
"""
申办江苏客车ETC流程自动化worker（流程主控，仅供logic.py等上层调用）

【完整流程说明】
1. 校验车牌
2. 校验是否可申办
3. 获取渠道地址
4. 获取可选服务
5. 提交车牌
6. 协议签署
7. 提交身份和银行卡信息
8. 签约校验
9. 保存车辆信息
10. 可选服务更新
11. 代扣支付
12. 数据库状态修改
13. 一键入库流程
14. ETC卡用户OBU信息入库
15. 流程完成

【日志名称规范】
- 开始："{步骤号}. {步骤名称}"
- 完成："{步骤号}. {步骤名称}完成"
- 失败："{步骤号}. {步骤名称}失败: {错误信息}"
- 异常："{步骤号}. {步骤名称}异常: {异常详情}"

【分层说明】
本文件只做流程主控和调度，不做底层接口请求、参数拼装、数据库校验。
所有接口请求由api.py负责，参数拼装由param_builder.py负责，数据库校验由db_checker.py负责。
"""
from datetime import datetime
from worker.etc.param_builder import generate_default_params, build_stock_in_params
from worker.etc.api import ApiClient


class Core:
    """
    【分层说明】
    只做流程主控和调度，不做底层接口请求、参数拼装、数据库校验。
    params参数必须由上层保证已校验和补全。
    """

    def __init__(self, params=None, progress_callback=None, base_url=None, browser_cookies=None):
        self.progress_callback = progress_callback
        self.params = params or generate_default_params()
        self.order_id = None
        self.sign_order_id = None
        self.verify_code_no = None
        self.base_url = base_url
        self.browser_cookies = browser_cookies
        # 新增：自动初始化api
        if self.base_url:
            self.api = ApiClient(self.base_url, cookies=self.browser_cookies)
        else:
            self.api = None

    def _update_progress(self, percent, msg):
        if self.progress_callback:
            self.progress_callback(percent, msg)

    def assert_save_success(self, resp_text, step_name=""):
        if "success" in resp_text:
            return
        raise Exception(f"{step_name}保存失败，响应内容：{resp_text[:200]}")

    def assert_api_success(self, resp, api_name="接口"):  # 只断言code==200
        import json
        if isinstance(resp, str):
            try:
                resp = json.loads(resp)
            except Exception:
                raise Exception(f"{api_name} 响应不是有效的JSON: {resp}")
        if resp.get("code") != 200:
            msg = resp.get("msg") or resp.get("message") or str(resp)
            raise Exception(f"{api_name} 失败，原因: {msg}，返回内容: {resp}")

    # 分步方法
    def step1_check_car_num(self):
        try:
            result = self.api.check_car_num(self.params)
            self.assert_api_success(result, "校验车牌接口")
            self._update_progress(5, "1. 校验车牌完成")
            return result
        except Exception as e:
            error_msg = f"1. 校验车牌失败: {str(e)}"
            self._update_progress(5, error_msg)
            raise Exception(error_msg)

    def step2_check_is_not_car_num(self):
        try:
            result = self.api.check_is_not_car_num(self.params)
            self.assert_api_success(result, "校验是否可申办接口")
            self._update_progress(10, "2. 校验是否可申办完成")
            return result
        except Exception as e:
            error_msg = f"2. 校验是否可申办失败: {str(e)}"
            self._update_progress(10, error_msg)
            raise Exception(error_msg)

    def step3_get_channel_use_address(self):
        try:
            result = self.api.get_channel_use_address(self.params)
            self.assert_api_success(result, "获取渠道地址接口")
            self._update_progress(15, "3. 获取渠道地址完成")
            return result
        except Exception as e:
            error_msg = f"3. 获取渠道地址失败: {str(e)}"
            self._update_progress(15, error_msg)
            raise Exception(error_msg)

    def step4_get_optional_service_list(self):
        try:
            result = self.api.get_optional_service_list(self.params)
            self.assert_api_success(result, "获取可选服务接口")
            self._update_progress(20, "4. 获取可选服务完成")
            return result
        except Exception as e:
            error_msg = f"4. 获取可选服务失败: {str(e)}"
            self._update_progress(20, error_msg)
            raise Exception(error_msg)

    def step5_submit_car_num(self):
        try:
            res = self.api.submit_car_num(self.params)
            self.assert_api_success(res, "提交车牌接口")
            self.order_id = res["data"]["orderId"]
            self._update_progress(30, "5. 提交车牌完成")
            return res
        except Exception as e:
            error_msg = f"5. 提交车牌失败: {str(e)}"
            self._update_progress(30, error_msg)
            raise Exception(error_msg)

    def step6_protocol_add(self):
        try:
            result = self.api.protocol_add(self.order_id, self.params)
            self.assert_api_success(result, "协议签署接口")
            self._update_progress(40, "6. 协议签署完成")
            return result
        except Exception as e:
            error_msg = f"6. 协议签署失败: {str(e)}"
            self._update_progress(40, error_msg)
            raise Exception(error_msg)

    def step7_submit_identity_with_bank_sign(self):
        try:
            res = self.api.submit_identity_with_bank_sign(self.order_id, self.params)
            self.assert_api_success(res, "提交身份和银行卡信息接口")
            self.sign_order_id = res["data"]["signOrderId"]
            self.verify_code_no = res["data"]["verifyCodeNo"]
            # 保存etccardUserId，供后续步骤使用
            if res["data"].get("etccardUserId"):
                self.params["etccardUserId"] = res["data"]["etccardUserId"]
            self._update_progress(50, "7. 提交身份和银行卡信息完成")
            return res
        except Exception as e:
            error_msg = f"7. 提交身份和银行卡信息失败: {str(e)}"
            self._update_progress(50, error_msg)
            raise Exception(error_msg)

    def run_step7_get_code(self, order_id, sign_order_id):
        """
        发送短信验证码，返回 sign_order_id 和 verify_code_no
        """
        self.order_id = order_id
        self.sign_order_id = sign_order_id
        res = self.step7_submit_identity_with_bank_sign()
        return {
            "sign_order_id": self.sign_order_id,
            "verify_code_no": self.verify_code_no,
            "raw": res
        }

    def step8_sign_check(self, verify_code=None):
        try:
            code = verify_code if verify_code is not None else self.params.get("code", "")
            result = self.api.sign_check(self.params, code, self.verify_code_no, self.sign_order_id)
            self.assert_api_success(result, "签约校验接口")
            self._update_progress(60, "8. 签约校验完成")
            return result
        except Exception as e:
            error_msg = f"8. 签约校验失败: {str(e)}"
            self._update_progress(60, error_msg)
            raise Exception(error_msg)

    def step9_save_vehicle_info(self, order_id=None):
        try:
            oid = order_id or self.order_id
            res = self.api.save_vehicle_info(self.params, oid)
            self.assert_api_success(res, "保存车辆信息接口")
            if res and res.get("data") and res["data"].get("etccardUserId"):
                self.params["etccardUserId"] = res["data"]["etccardUserId"]
            self._update_progress(70, "9. 保存车辆信息完成")
            return res
        except Exception as e:
            error_msg = f"9. 保存车辆信息失败: {str(e)}"
            self._update_progress(70, error_msg)
            raise Exception(error_msg)

    def step10_optional_service_update(self, order_id=None):
        try:
            oid = order_id or self.order_id
            result = self.api.optional_service_update(oid)
            self.assert_api_success(result, "可选服务更新接口")
            self._update_progress(80, "10. 可选服务更新完成")
            return result
        except Exception as e:
            error_msg = f"10. 可选服务更新失败: {str(e)}"
            self._update_progress(80, error_msg)
            raise Exception(error_msg)

    def step11_withhold_pay(self, order_id=None, verify_code=None):
        try:
            oid = order_id or self.order_id
            # 代扣支付使用日期格式的验证码（YYMMDD格式，如250723）
            if verify_code is not None:
                code = verify_code
            else:
                # 生成当前日期的YYMMDD格式验证码
                code = datetime.now().strftime("%y%m%d")
            result = self.api.withhold_pay(self.params, oid, code)
            self.assert_api_success(result, "代扣支付接口")
            self._update_progress(85, "11. 代扣支付完成")
            return result
        except Exception as e:
            error_msg = f"11. 代扣支付失败: {str(e)}"
            self._update_progress(85, error_msg)
            raise Exception(error_msg)

    def step12_update_db_status(self):
        from worker.etc.db_update import update_order_status, update_card_user_status
        # 1. 申办订单状态修改
        self._update_progress(99, "12. 申办订单状态修改完成")
        update_order_status(self.order_id)
        # 2. ETC用户状态修改
        car_num = self.params.get("car_num")
        self._update_progress(100, "12. ETC用户状态修改完成")
        update_card_user_status(car_num)

    def step13_run_stock_in_flow(self):
        try:
            from worker.etc.db_update import run_stock_in_flow, get_mysql_config
            from utils.data_factory import DataFactory
            import uuid
            # 只保留完成日志
            config = get_mysql_config()
            dbname = 'hcb'  # 改为hcb数据库
            table = 'hcb_newstock'  # 改为库存表
            # 只取界面传递的完整车牌号
            car_num = self.params.get('carNum') or self.params.get('car_num')
            if not car_num:
                raise ValueError("未获取到界面拼接后的完整车牌号，请检查参数传递！")
            self.params['car_num'] = car_num
            
            # 生成OBU号和ETC号
            obu_no = DataFactory.random_obn_number()
            etc_sn = DataFactory.random_etc_number()
            activation_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # 保存生成的obu_no和etc_sn到params中，供step14使用
            self.params['obu_no'] = obu_no
            self.params['etc_sn'] = etc_sn
            self.params['activation_time'] = activation_time
            
            # 插入OBU设备记录
            obu_fields = [
                'NEWSTOCK_ID', 'CARD_OPERATORS', 'STATUS', 'CAR_NUM', 'STOCK_STATUS', 
                'SOURCE', 'REMARK', 'CREATE_TIME', 'DEVICE_CATEGORY', 'INTERNAL_DEVICE_NO', 
                'EXTERNAL_DEVICE_NO', 'TYPE'
            ]
            obu_types = [
                'varchar(32)', 'varchar(10)', 'varchar(10)', 'varchar(20)', 'varchar(10)',
                'varchar(10)', 'varchar(255)', 'datetime', 'varchar(10)', 'varchar(32)',
                'varchar(32)', 'varchar(10)'
            ]
            obu_rules = [
                '固定值', '固定值', '固定值', '固定值', '固定值',
                '固定值', '固定值', '固定值', '固定值', '固定值',
                '固定值', '固定值'
            ]
            obu_extras = [
                uuid.uuid4().hex, '1', '1', car_num, '0',
                '1', '激活设备不存在库存内', activation_time, '0', obu_no,
                obu_no, '0'
            ]
            
            # 插入ETC设备记录
            etc_fields = [
                'NEWSTOCK_ID', 'CARD_OPERATORS', 'STATUS', 'CAR_NUM', 'STOCK_STATUS', 
                'SOURCE', 'REMARK', 'CREATE_TIME', 'DEVICE_CATEGORY', 'INTERNAL_DEVICE_NO', 
                'EXTERNAL_DEVICE_NO', 'TYPE'
            ]
            etc_types = [
                'varchar(32)', 'varchar(10)', 'varchar(10)', 'varchar(20)', 'varchar(10)',
                'varchar(10)', 'varchar(255)', 'datetime', 'varchar(10)', 'varchar(32)',
                'varchar(32)', 'varchar(10)'
            ]
            etc_rules = [
                '固定值', '固定值', '固定值', '固定值', '固定值',
                '固定值', '固定值', '固定值', '固定值', '固定值',
                '固定值', '固定值'
            ]
            etc_extras = [
                uuid.uuid4().hex, '1', '1', car_num, '0',
                '1', '激活设备不存在库存内', activation_time, '0', etc_sn,
                etc_sn, '1'
            ]
            
            # 直接插入，不再回调进度
            run_stock_in_flow(config, dbname, table, obu_fields, obu_types, obu_rules, 1, obu_extras, None)
            run_stock_in_flow(config, dbname, table, etc_fields, etc_types, etc_rules, 1, etc_extras, None)
            
            self._update_progress(95, "13. 一键入库流程完成")
        except Exception as e:
            error_msg = f"13. 一键入库流程失败: {str(e)}"
            self._update_progress(95, error_msg)
            raise Exception(error_msg)

    def step14_update_obu_info(self):
        try:
            from worker.etc.db_update import update_card_user_obu_info
            car_num = self.params.get("car_num")
            # 使用step13中已经生成的obu_no和etc_sn，而不是重新生成
            obu_no = self.params.get("obu_no")
            etc_sn = self.params.get("etc_sn")
            activation_time = self.params.get("activation_time")
            if not all([car_num, obu_no, etc_sn, activation_time]):
                raise ValueError("step14缺少必要参数，请检查step13是否正确执行")
            update_card_user_obu_info(car_num, obu_no, etc_sn, activation_time)
            self._update_progress(98, "14. 卡用户OBU信息入库完成")
        except Exception as e:
            error_msg = f"14. 卡用户OBU信息入库失败: {str(e)}"
            self._update_progress(98, error_msg)
            raise Exception(error_msg)

    def run_step8_to_end(self, code, order_id, sign_order_id, verify_code_no):
        try:
            self.order_id = order_id
            self.sign_order_id = sign_order_id
            self.verify_code_no = verify_code_no
            # step7已经在之前执行过了，这里直接使用已有的参数
            # 不需要重复调用step7_submit_identity_with_bank_sign()
            try:
                res8 = self.step8_sign_check(code)
            except Exception as e:
                error_msg = f"8. 签约校验失败: {str(e)}"
                print(f"[ERROR] {error_msg}")
                self._update_progress(60, error_msg)
                raise Exception(error_msg)
            try:
                res9 = self.step9_save_vehicle_info()
            except Exception as e:
                error_msg = f"9. 保存车辆信息失败: {str(e)}"
                print(f"[ERROR] {error_msg}")
                self._update_progress(70, error_msg)
                # 不抛出异常，继续执行后续流程
                res9 = None
            try:
                res10 = self.step10_optional_service_update()
            except Exception as e:
                error_msg = f"10. 可选服务更新失败: {str(e)}"
                print(f"[ERROR] {error_msg}")
                self._update_progress(80, error_msg)
                raise Exception(error_msg)
            try:
                # 代扣支付使用日期格式验证码，不传递签约校验的验证码
                res11 = self.step11_withhold_pay()
            except Exception as e:
                error_msg = f"11. 代扣支付失败: {str(e)}"
                print(f"[ERROR] {error_msg}")
                self._update_progress(85, error_msg)
                raise Exception(error_msg)
            try:
                self.step12_update_db_status()
            except Exception as e:
                error_msg = f"12. 数据库状态修改失败: {str(e)}"
                print(f"[ERROR] {error_msg}")
                self._update_progress(90, error_msg)
                raise Exception(error_msg)
            try:
                self.step13_run_stock_in_flow()
            except Exception as e:
                error_msg = f"13. 一键入库流程失败: {str(e)}"
                print(f"[ERROR] {error_msg}")
                self._update_progress(95, error_msg)
                raise Exception(error_msg)
            try:
                self.step14_update_obu_info()
            except Exception as e:
                error_msg = f"14. 卡用户OBU信息入库失败: {str(e)}"
                print(f"[ERROR] {error_msg}")
                self._update_progress(98, error_msg)
                raise Exception(error_msg)
            self._update_progress(100, "15. 流程完成")
            print("[DEBUG] 全流程完成")
            return {
                "sign_check": res8,
                "save_vehicle_info": res9,
                "optional_service_update": res10,
                "withhold_pay": res11
            }
        except Exception as e:
            import traceback
            error_msg = f"ETC申办流程异常: {str(e)}"
            print(f"[ERROR] {error_msg}")
            print(traceback.format_exc())
            self._update_progress(100, error_msg)
            raise Exception(error_msg)
