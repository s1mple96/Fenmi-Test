import requests
import logging
import sys
import traceback
from apps.etc_apply.services.log_service import LogService
from apps.etc_apply.services.core_service import CoreService


class ApiClient:
    def __init__(self, base_url, log_file=None, cookies=None):
        self.base_url = base_url
        self.session = requests.Session()
        self.log_service = LogService("api_client", log_file)
        self.cookies = cookies or {}
        if self.cookies:
            self.session.cookies.update(self.cookies)

    def post(self, path, data, headers=None, cookies=None):
        url = self.base_url + path
        default_headers = {
            "User-Agent": "Mozilla/5.0 ...",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/json; charset=UTF-8",  # 统一为json
            "X-Requested-With": "XMLHttpRequest",
        }
        if headers:
            default_headers.update(headers)
        if not self.session.cookies and self.cookies:
            self.session.cookies.update(self.cookies)
        
        self.log_service.log_api_request(path, data)
        
        try:
            resp = self.session.post(url, json=data, headers=default_headers, cookies=cookies)  # 用json参数
            resp.raise_for_status()
            self.log_service.log_api_response(path, resp.text)
            try:
                response_data = resp.json()
                # 检查API响应状态 - 只有200是成功，其他都是业务错误
                if response_data.get("code") != 200:
                    # 提取业务错误信息
                    error_msg = response_data.get("msg") or response_data.get("message") or f"业务错误: {response_data.get('code')}"
                    self.log_service.error(f"{path} 调用失败 | URL: {url} | 错误码: {response_data.get('code')} | 错误信息: {error_msg}")
                    raise Exception(f"业务错误: {error_msg}")
                return response_data
            except Exception as e:
                if "业务错误" not in str(e) and "code" not in str(e):  # 避免重复错误信息
                    self.log_service.error(f"接口返回内容不是JSON: {resp.text}")
                    raise Exception(f"接口响应格式错误: {path} - 返回内容不是有效的JSON格式")
                raise e
        except Exception as e:
            # 区分网络错误和API错误
            if "Connection refused" in str(e) or "timeout" in str(e).lower():
                error_msg = CoreService.format_network_error(path, e)
            else:
                error_msg = CoreService.handle_exception_with_context(path, e)
            self.log_service.log_api_error(path, data, e)
            raise Exception(error_msg)

    # 业务高阶方法
    def check_car_num(self, params):
        return self.post("/rtx-app/apply/checkCarNum", {
            "carNum": params["carNum"],
            "vehicleColor": params["vehicleColor"],
            "truckchannelId": params["truckchannelId"]
        })

    def check_is_not_car_num(self, params):
        return self.post("/rtx-app/apply/order/checkIsNotCarNum", {
            "channelId": params["channelId"],
            "carNum": params["carNum"]
        })

    def get_channel_use_address(self, params):
        return self.post("/rtx-app/apply/order/getChannelUseAddress", {
            "channelId": params["channelId"],
            "province": params["province"],
            "city": params["city"]
        })

    def get_optional_service_list(self, params):
        return self.post("/rtx-app/service/optionalServiceList", {
            "productId": params["productId"],
            "orderId": "",
            "channelId": params["channelId"]
        })

    def submit_car_num(self, params):
        return self.post("/rtx-app/apply/submitCarNum", {
            "operatorCode": params["operatorCode"],
            "truckchannelId": params["truckchannelId"],
            "productId": params["productId"],
            "orderType": params["orderType"],
            "handleLocation": params["handleLocation"],
            "carNum": params["carNum"],
            "vehicleColor": params["vehicleColor"],
            "terminalId": "",
            "tempCarNumFlag": params["tempCarNumFlag"],
            "bidOrderType": params["bidOrderType"]
        })

    def protocol_add(self, order_id, params):
        return self.post("/rtx-app/protocol/add", {
            "orderId": order_id,
            "protocolId": params["protocolId"],
            "signingImage": params["signingImage"],
            "protocolType": params["protocolType"]
        })

    def submit_identity_with_bank_sign(self, order_id, params):
        return self.post("/rtx-app/apply/submitIdentityWithBankSign", {
            "productId": params["productId"],
            "idCardUrl": params["idCardUrl"],
            "backIdCardUrl": params["backIdCardUrl"],
            "cardHolder": params["cardHolder"],
            "idCode": params["idCode"],
            "idcardValidity": params["idcardValidity"],
            "idAddress": params["idAddress"],
            "urgentContact": params["urgentContact"],
            "urgentPhone": params["urgentPhone"],
            "bindBankUrl": params["bindBankUrl"],
            "bindBankName": params["bindBankName"],
            "bindBankNo": params["bindBankNo"],
            "bankCode": params["bankCode"],
            "bindBankPhone": params["bindBankPhone"],
            "bankCardType": params["bankCardType"],
            "bankChannelCode": params["bankChannelCode"],
            "code": "",
            "bankCardInfoId": params["bankCardInfoId"],
            "isAgree": params["isAgree"],
            "orderId": order_id
        })

    def sign_check(self, params, verify_code, verify_code_no, sign_order_id):
        return self.post("/rtx-app/withhold/signCheck", {
            "productId": params["productId"],  # 保持原始类型，不强制转换
            "verifyCode": verify_code,
            "bankCardNo": params["bindBankNo"],
            "bindBankPhone": params["bindBankPhone"],
            "idCode": params["idCode"],
            "verifyCodeNo": verify_code_no,
            "signOrderId": sign_order_id,
            "location": "2"
        })

    def save_vehicle_info(self, params, order_id):
        return self.post("/rtx-app/apply/saveVehicleInfo", {
            "productId": params["productId"],
            "licenseUrl": params["licenseUrl"],
            "backLicenseUrl": params["backLicenseUrl"],
            "carHeadUrl": params["carHeadUrl"],
            "plateNum": params["carNum"],
            "vehicleType": params["vehicleType"],
            "model": params["model"],
            "vin": params["vin"],
            "engineNum": params["engineNum"],
            "useCharacter": params["useCharacter"],
            "owner": params["owner"],
            "registerDate": params["registerDate"],
            "issueDate": params["issueDate"],
            "vehicleColor": params["vehicleColor"],
            "approvedPassengerCapacity": params["approvedPassengerCapacity"],
            "length": params["length"],
            "wide": params["wide"],
            "high": params["high"],
            "grossMass": params["grossMass"],
            "unladenMass": params["unladenMass"],
            "approvedLoad": params["approvedLoad"],
            "licenseVerifyFlag": params["licenseVerifyFlag"],
            "updateCkg": params["updateCkg"],
            "addr": params["addr"],
            "orderId": order_id
        })

    def optional_service_update(self, order_id):
        return self.post("/rtx-app/service/optionalServiceUpdate", {
            "orderId": order_id
        })

    def withhold_pay(self, params, order_id, verify_code):
        return self.post("/rtx-app/withhold/old/pay", {
            "bankCardNo": params["bindBankNo"],
            "etcCardUserId": params.get("etccardUserId", ""),
            "productId": params["productId"],  # 保持原始类型，不强制转换
            "applyOrderId": order_id,
            "verifyCode": verify_code,
            "phoneNumber": params["bindBankPhone"]
        })
