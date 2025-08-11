# -*- coding: utf-8 -*-
"""
货车ETC申办API客户端 - 基于HCB接口
"""
import requests
from apps.etc_apply.services.rtx.log_service import LogService
from apps.etc_apply.services.rtx.core_service import CoreService


class TruckApiClient:
    """货车ETC申办API客户端"""
    
    def __init__(self, base_url=None, log_file=None, cookies=None):
        # 如果没有提供base_url，使用默认值
        if base_url is None:
            # 使用CoreService统一读取配置文件
            base_url = CoreService.get_api_base_url()
            # 强制使用HTTP
            if base_url.startswith('https://'):
                base_url = base_url.replace('https://', 'http://')
        
        self.base_url = base_url
        self.session = requests.Session()
        # 设置网络超时
        self.session.timeout = 30
        self.log_service = LogService("truck_api_client", log_file)
        self.cookies = cookies or {}
        self.last_error_detail = None  # 保存最后一次的错误详情
        if self.cookies:
            self.session.cookies.update(self.cookies)
    
    def post(self, path, data, headers=None, cookies=None):
        """统一的POST请求方法，发送JSON格式数据"""
        # 确保URL正确拼接
        if self.base_url.endswith('/'):
            if path.startswith('/'):
                url = self.base_url + path[1:]  # 移除path开头的/
            else:
                url = self.base_url + path
        else:
            if path.startswith('/'):
                url = self.base_url + path
            else:
                url = self.base_url + '/' + path
            
        default_headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 18_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.60(0x18003c32) NetType/4G Language/zh_CN",
            "Accept": "*/*",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip,compress,br,deflate",
        }
        if headers:
            default_headers.update(headers)
        if not self.session.cookies and self.cookies:
            self.session.cookies.update(self.cookies)
        
        self.log_service.log_api_request(path, data)
        
        try:
            # HCB接口发送JSON格式数据，但Content-Type为application/x-www-form-urlencoded
            import json
            # 确保所有字符串值都是有效的
            cleaned_data = {}
            for key, value in data.items():
                if isinstance(value, str):
                    # 清理字符串，移除可能的特殊字符
                    original_value = value
                    cleaned_value = value.strip()
                    
                    # 检查字符串中是否有问题字符
                    problem_chars = ['"', '\n', '\r', '\t', '\\']
                    has_problem = any(char in cleaned_value for char in problem_chars)
                    if has_problem:
                        self.log_service.warning(f"🚨 字段 '{key}' 包含特殊字符: '{original_value}'")
                        # 转义特殊字符
                        cleaned_value = cleaned_value.replace('\\', '\\\\').replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
                        self.log_service.info(f"🔧 字段 '{key}' 清理后: '{cleaned_value}'")
                    
                    if cleaned_value:
                        cleaned_data[key] = cleaned_value
                    else:
                        self.log_service.warning(f"⚠️ 字段 '{key}' 清理后为空，原值: '{original_value}'")
                else:
                    cleaned_data[key] = value
            
            # 记录日志用的json字符串
            json_data = json.dumps(cleaned_data, ensure_ascii=False, separators=(',', ':'))

            # 调试：打印JSON数据长度和内容
            self.log_service.info(f"发送JSON数据长度: {len(json_data)}")
            self.log_service.info(f"发送JSON数据: {json_data}")
            
            # 验证JSON格式是否正确
            try:
                json.loads(json_data)  # 验证JSON格式
                self.log_service.info("✅ JSON格式验证通过")
            except json.JSONDecodeError as json_err:
                self.log_service.error(f"❌ JSON格式错误: {json_err}")
                self.log_service.error(f"❌ 原始数据: {data}")
                self.log_service.error(f"❌ 清理后数据: {cleaned_data}")
                raise Exception(f"JSON格式错误: {json_err}")

            # 仍按表单方式发送纯JSON字符串，保持与后端兼容
            self.log_service.info(f"🌐 发送POST请求到: {url}")
            self.log_service.info(f"📤 请求头: {default_headers}")
            self.log_service.info(f"📝 请求体类型: {type(json_data)} 长度: {len(json_data)}")
            
            # 明确设置Content-Length避免数据截断 - 关键：直接使用字节数据发送
            json_bytes = json_data.encode('utf-8')
            default_headers['Content-Length'] = str(len(json_bytes))
            self.log_service.info(f"🔢 实际字节长度: {len(json_bytes)}, Content-Length: {default_headers['Content-Length']}")
            
            # 关键修复：直接发送字节数据而不是字符串，确保长度一致
            self.log_service.info(f"📦 发送字节数据前10字节: {json_bytes[:10]}")
            self.log_service.info(f"📦 发送字节数据后10字节: {json_bytes[-10:]}")
            
            resp = self.session.post(url, data=json_bytes, headers=default_headers, cookies=cookies)
            resp.raise_for_status()
            self.log_service.log_api_response(path, resp.text)
            
            try:
                response_data = resp.json()
                # HCB接口成功标志是ret="1"
                if response_data.get("ret") != "1":
                    error_msg = response_data.get("msg") or f"业务错误: {response_data.get('ret')}"
                    error_code = response_data.get("ret")
                    
                    # 记录详细错误信息
                    self.log_service.error(f"{path} 调用失败 | URL: {url} | 错误码: {error_code} | 错误信息: {error_msg}")
                    
                    # 创建结构化异常信息
                    error_detail = CoreService.create_api_error_detail(
                        api_path=path,
                        url=url,
                        error_code=error_code,
                        error_message=error_msg,
                        request_data=cleaned_data,
                        response_data=response_data
                    )
                    
                    # 保存错误详情，供后续错误处理使用
                    self.last_error_detail = error_detail
                    
                    # 立即抛出异常
                    exception = Exception(f"业务错误: {error_msg}")
                    exception.error_detail = error_detail
                    raise exception
                return response_data
            except Exception as e:
                if hasattr(e, 'error_detail'):
                    # 如果是我们创建的业务异常，直接重新抛出
                    raise e
                else:
                    # JSON解析异常或其他异常
                    self.log_service.error(f"{path} 响应解析失败: {str(e)}")
                    raise Exception(f"响应解析失败: {str(e)}")
                    
        except requests.exceptions.RequestException as e:
            self.log_service.error(f"{path} 网络请求失败: {str(e)}")
            raise Exception(f"网络请求失败: {str(e)}")
        except Exception as e:
            # 如果异常已经有error_detail，直接重新抛出
            if hasattr(e, 'error_detail'):
                raise e
            else:
                self.log_service.error(f"{path} 请求异常: {str(e)}")
                raise Exception(f"请求异常: {str(e)}")
    
    # ==================== 货车流程专用接口 ====================
    
    def update_wx_msg_template(self, params):
        """更新微信消息模板"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "templateIdList": params.get("templateIdList", ""),
            "openId": params.get("openId", ""),
            "relativeurl": "com.hcb.updateAllWXMsgTemplate",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def get_bank_list(self, params):
        """获取银行列表 - 实际上是获取产品列表"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "channelId": params.get("channelId", "0000"),
            "operatorId": params.get("operatorId", ""),
            "isCompany": params.get("isCompany", "0"),
            "relativeurl": "com.hcb.channel.getBankList",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def get_product_info(self, params):
        """获取产品信息"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "channelId": params.get("channelId", "0000"),
            "operatorId": params.get("operatorId", ""),
            "bankId": params.get("bankId", ""),
            "relativeurl": "com.hcb.channel.getProductInfo",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def get_bank_list_simple(self, params):
        """获取简单银行列表"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "relativeurl": "com.hcb.getBankList",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def submit_apply_bank_info(self, params):
        """提交申办银行信息"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "truckEtcApplyId": params.get("truckEtcApplyId", ""),
            "idCardUrl": params.get("idCardUrl", ""),
            "backIdCardUrl": params.get("backIdCardUrl", ""),
            "cardHolder": params.get("cardHolder", ""),
            "phone": params.get("phone", ""),
            "urgentContact": params.get("urgentContact", ""),
            "urgentPhone": params.get("urgentPhone", ""),
            "idCode": params.get("idCode", ""),
            "idAddress": params.get("idAddress", ""),
            "effectiveDate": params.get("effectiveDate", ""),
            "ethnic": params.get("ethnic", "汉"),
            "idAuthority": params.get("idAuthority", ""),
            "anHuiId": params.get("anHuiId", ""),
            "carNum": params.get("carNum", ""),
            "plateColor": params.get("plateColor", "1"),
            "bankName": params.get("bankName", ""),
            "bankNo": params.get("bankNo", ""),
            "bankPicUrl": params.get("bankPicUrl", ""),
            "mobileNo": params.get("mobileNo", ""),
            "channelId": params.get("channelId", "0000"),
            "productId": params.get("productId", ""),
            "loginUserId": params.get("loginUserId", ""),
            "userId": params.get("userId", ""),
            "code": params.get("code", ""),
            "smsCode": params.get("smsCode", ""),
            "applyAccountId": params.get("applyAccountId", ""),
            "openAccountApplyId": params.get("openAccountApplyId", ""),
            "idProvinceCode": params.get("idProvinceCode", ""),
            "idCityCode": params.get("idCityCode", ""),
            "idDistrictCode": params.get("idDistrictCode", ""),
            "idProvince": params.get("idProvince", ""),
            "idCity": params.get("idCity", ""),
            "idDistrict": params.get("idDistrict", ""),
            "provinceCity": params.get("provinceCity", ""),
            "openId": params.get("openId", ""),
            "verifyCode": params.get("verifyCode", ""),
            "obuSubmitStatus": params.get("obuSubmitStatus", "1"),
            "terminalId": params.get("terminalId", ""),
            "fissionId": params.get("fissionId", ""),
            "orderType": params.get("orderType", ""),
            "relativeurl": "com.hcb.submitApplyBankInfo",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def submit_vehicle_info(self, params):
        """提交车辆信息"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "truckEtcApplyId": params.get("truckEtcApplyId", ""),
            "licenseUrl": params.get("licenseUrl", ""),
            "backLicenseUrl": params.get("backLicenseUrl", ""),
            "carHeadUrl": params.get("carHeadUrl", ""),
            "roadTransportUrl": params.get("roadTransportUrl", ""),
            "plateColor": params.get("plateColor", "1"),
            "name": params.get("name", ""),
            "vin": params.get("vin", ""),
            "vehicleAxles": params.get("vehicleAxles", ""),
            "vehicleWheels": params.get("vehicleWheels", ""),
            "registerDate": params.get("registerDate", ""),
            "issueDate": params.get("issueDate", ""),
            "model": params.get("model", ""),
            "carType": params.get("carType", ""),
            "businessScope": params.get("businessScope", ""),
            "vehicleType": params.get("vehicleType", ""),
            "vehicleEngineno": params.get("vehicleEngineno", ""),
            "approvedCount": params.get("approvedCount", ""),
            "totalMass": params.get("totalMass", ""),
            "weightLimits": params.get("weightLimits", ""),
            "permittedTowweight": params.get("permittedTowweight", ""),
            "unladenMass": params.get("unladenMass", ""),
            "usePurpose": params.get("usePurpose", "货运"),
            "long": params.get("long", ""),
            "width": params.get("width", ""),
            "height": params.get("height", ""),
            "channelId": params.get("channelId", ""),
            "productId": params.get("productId", ""),
            "ex_factory_time": params.get("ex_factory_time", ""),
            "fuel_type": params.get("fuel_type", ""),
            "fuel_name": params.get("fuel_name", ""),
            "engine_power": params.get("engine_power", ""),
            "wheelbase": params.get("wheelbase", ""),
            "businessLicenseNumber": params.get("businessLicenseNumber", ""),
            "roadTransportationPermitCardNumber": params.get("roadTransportationPermitCardNumber", ""),
            "isTractor": params.get("isTractor"),
            "carNum": params.get("carNum", ""),
            "relativeurl": "com.hcb.submitVehicleInfo",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def get_etc_apply_info(self, params):
        """获取ETC申办信息"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "truckEtcApplyId": params.get("truckEtcApplyId", ""),
            "relativeurl": "com.hcb.geEtcApplyinfo",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def issue_insure_agreements(self, params):
        """签发保险协议"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "orderId": params.get("orderId", ""),
            "agreeType": params.get("agreeType", "S"),
            "relativeurl": "com.hcb.issueInsureAgreements",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def select_bind_bank_list(self, params):
        """查询绑定银行卡列表"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "idCard": params.get("idCard", ""),
            "relativeurl": "com.hcb.bank.selectBindBankList",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def truck_pay(self, params):
        """货车支付"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "truckEtcApplyId": params.get("truckEtcApplyId", ""),
            "payType": params.get("payType", "0"),
            "bankCardId": params.get("bankCardId", ""),
            "payMoney": params.get("payMoney", ""),
            "relativeurl": "com.hcb.truckPay",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def quick_pay_prestore(self, params):
        """快捷支付预存"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "orderId": params.get("orderId", ""),
            "truckUserId": params.get("truckUserId", ""),
            "userBindBankId": params.get("userBindBankId", ""),
            "amt": params.get("amt", "0.02"),
            "relativeurl": "com.hcb.quickPayPrestore",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def report_log(self, params):
        """上报日志"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "pageId": params.get("pageId", ""),
            "eventName": params.get("eventName", "OUT"),
            "appType": params.get("appType", "HCB"),
            "openId": params.get("openId", ""),
            "channelId": params.get("channelId", ""),
            "userId": params.get("userId", ""),
            "relativeurl": "com.hcb.reportLog",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    # ==================== 新发现的重要接口 ====================
    
    def get_top_channel(self, params):
        """获取顶级渠道"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "truckChannelId": params.get("truckChannelId", "0000"),  # 修正参数名
            "relativeurl": "com.hcb.channel.getTopChannel",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def get_product_ldkq_flag(self, params):
        """获取货车产品绿通卡标识"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "productId": params.get("productId", ""),
            "relativeurl": "com.hcb.truck.product.getProductLdkqFlag",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def check_plate_no_info(self, params):
        """校验车牌号信息"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "plateNo": params.get("plateNo", ""),
            "plateColor": str(params.get("plateColor", "1")),  # 确保是字符串
            "trunkUserId": params.get("trunkUserId", ""),
            "channelId": params.get("channelId", "0000"),
            "relativeurl": "com.hcb.channel.checkPlateNoInfo",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def check_is_not_car_num(self, params):
        """检查是否可申办"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "carNum": params.get("carNum", ""),
            "channelId": params.get("channelId", "0000"),
            "relativeurl": "com.hcb.checkIsNotCarNum",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def check_channel_use_address(self, params):
        """检查渠道使用地址"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "channelId": params.get("channelId", "0000"),
            "province": params.get("province", ""),
            "city": params.get("city", ""),
            "relativeurl": "com.hcb.checkChannelUseAddress",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def check_phone(self, params):
        """校验手机号"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "phone": params.get("phone", ""),
            "channelId": params.get("channelId", "0000"),
            "verifyCode": params.get("code", ""),  # 修正参数名为verifyCode
            "relativeurl": "com.hcb.channel.checkPhone",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def user_apply_issue(self, params):
        """用户申办问题上报"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "issue": params.get("issue", ""),
            "userId": params.get("userId", ""),
            "relativeurl": "com.hcb.userApplyIssue",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def ocr_identity_card(self, params):
        """身份证OCR识别"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "image": params.get("image", ""),
            "cardSide": params.get("cardSide", "front"),
            "relativeurl": "com.hcb.ocrIdentityCard",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def ocr_driver_license(self, params):
        """行驶证OCR识别"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "image": params.get("image", ""),
            "relativeurl": "com.hcb.ocrDriverLicense",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def query_rong_bang_account(self, params):
        """查询融邦账户"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "idCard": params.get("idCard", ""),
            "relativeurl": "com.hcb.queryRongBangAccount",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def user_sign_count(self, params):
        """用户签约次数"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "userId": params.get("userId", ""),
            "relativeurl": "com.hcb.userSignCount",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def get_dic_info(self, params):
        """获取字典信息"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "dicType": params.get("dicType", ""),
            "relativeurl": "com.hcb.getDicInfo",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def traffic_query(self, params):
        """交通违章查询"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "truckEtcApplyId": params.get("truckEtcApplyId", ""),
            "licenseUrl": params.get("licenseUrl", ""),
            "backLicenseUrl": params.get("backLicenseUrl", ""),
            "carHeadUrl": params.get("carHeadUrl", ""),
            "roadTransportUrl": params.get("roadTransportUrl", ""),
            "plateColor": params.get("plateColor", "1"),
            "name": params.get("name", ""),
            "vin": params.get("vin", ""),
            "vehicleAxles": params.get("vehicleAxles", ""),
            "vehicleWheels": params.get("vehicleWheels", ""),
            "registerDate": params.get("registerDate", ""),
            "issueDate": params.get("issueDate", ""),
            "model": params.get("model", ""),
            "carType": params.get("carType", ""),
            "businessScope": params.get("businessScope", ""),
            "vehicleType": params.get("vehicleType", ""),
            "vehicleEngineno": params.get("vehicleEngineno", ""),
            "approvedCount": params.get("approvedCount", ""),
            "totalMass": params.get("totalMass", ""),
            "weightLimits": params.get("weightLimits", ""),
            "permittedTowweight": params.get("permittedTowweight", ""),
            "unladenMass": params.get("unladenMass", ""),
            "usePurpose": params.get("usePurpose", "货运"),
            "long": params.get("long", ""),
            "width": params.get("width", ""),
            "height": params.get("height", ""),
            "channelId": params.get("channelId", "0000"),
            "productId": params.get("productId", ""),
            "ex_factory_time": params.get("ex_factory_time", ""),
            "fuel_type": params.get("fuel_type", ""),
            "fuel_name": params.get("fuel_name", ""),
            "engine_power": params.get("engine_power", ""),
            "wheelbase": params.get("wheelbase", ""),
            "businessLicenseNumber": params.get("businessLicenseNumber", ""),
            "roadTransportationPermitCardNumber": params.get("roadTransportationPermitCardNumber", ""),
            "isTractor": params.get("isTractor"),
            "carNum": params.get("carNum", ""),  # 使用carNum而不是plateNo
            "relativeurl": "com.hcb.trafficQuery",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def get_user_is_bind(self, params):
        """获取用户绑定状态"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "idCard": params.get("idCard", ""),
            "relativeurl": "com.hcb.bank.getUserIsBind",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def get_and_check_token(self, params):
        """获取并校验token"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "openId": params.get("openId", ""),
            "relativeurl": "com.hcb.getAndCheckToken",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def save_car_video_info(self, params):
        """保存车辆视频信息"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "truckEtcApplyId": params.get("truckEtcApplyId", ""),
            "videoUrl": params.get("videoUrl", ""),
            "relativeurl": "com.hcb.saveCarVideoInfo",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def submit_obu_order(self, params):
        """提交OBU订单"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "orderId": params.get("orderId", ""),  # 修正为正确的参数名
            "obuInfo": params.get("obuInfo", ""),
            "relativeurl": "com.hcb.submitObuOrder",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        }) 

    def get_operator_list(self, params):
        """获取运营商列表"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "channelId": params.get("channelId", "0000"),
            "relativeurl": "com.hcb.channel.getOperatorList",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def get_product_list_by_operator(self, params):
        """根据运营商获取产品列表 - 使用getBankList接口"""
        return self.get_bank_list(params) 
    
    def get_user_info_by_openid(self, params):
        """根据openId获取用户信息"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "openId": params.get("openId", ""),
            "relativeurl": "com.hcb.getUserInfoByOpenId",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def get_user_info_by_idcard(self, params):
        """根据身份证获取用户信息"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "idCode": params.get("idCode", ""),
            "relativeurl": "com.hcb.getUserInfoByIdCard",
            "caller": "chefuAPP", 
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def get_user_info_by_phone(self, params):
        """根据手机号获取用户信息"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "phone": params.get("phone", ""),
            "relativeurl": "com.hcb.getUserInfoByPhone",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        })
    
    def bind_user_vehicle(self, params):
        """用户车辆绑定接口"""
        return self.post("/hcbapi/gateWay/pubCtrl.do", {
            "userInfoId": params.get("userInfoId", ""),
            "truckUserId": params.get("truckUserId", ""),
            "truckEtcApplyId": params.get("truckEtcApplyId", ""),
            "carNum": params.get("carNum", ""),
            "relativeurl": "com.hcb.bindUserVehicle",
            "caller": "chefuAPP",
            "timestamp": params.get("timestamp"),
            "hashcode": params.get("hashcode")
        }) 