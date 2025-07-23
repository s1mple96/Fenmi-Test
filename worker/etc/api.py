import requests
import logging
import sys
import traceback


class ApiClient:
    def __init__(self, base_url, log_file=None, cookies=None):
        self.base_url = base_url
        self.session = requests.Session()
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            ch = logging.StreamHandler(sys.stdout)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)
            if log_file:
                fh = logging.FileHandler(log_file, encoding='utf-8')
                fh.setFormatter(formatter)
                self.logger.addHandler(fh)
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
        self.logger.info(f"【接口请求】{path}\n参数: {data}")
        try:
            resp = self.session.post(url, json=data, headers=default_headers, cookies=cookies)  # 用json参数
            resp.raise_for_status()
            self.logger.info(f"【接口响应】{path}\n内容: {resp.text}")
            try:
                return resp.json()
            except Exception:
                self.logger.error(f"接口返回内容不是JSON: {resp.text}")
                return {"raw": resp.text}
        except Exception as e:
            tb = traceback.format_exc()
            self.logger.error(f"【接口异常】{path}\n参数: {data}\n错误: {e}\n堆栈: {tb}")
            raise Exception(f"接口异常: {url}, 参数: {data}, 错误: {e}")
        if res.get('code') != 200:
            self.logger.error(f"【接口失败】{path}\n参数: {data}\n返回: {res}")
            raise Exception(f"接口失败: {url}, 参数: {data}, 返回: {res}")
        return res

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