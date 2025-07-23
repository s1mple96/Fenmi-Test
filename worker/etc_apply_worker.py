# -*- coding: utf-8 -*-
"""
申办江苏客车ETC流程自动化worker
- 支持参数化（车牌、身份证、银行卡等）
- 可集成utils.data_factory自动生成测试数据
- 适合WinForm/命令行/批量造数等场景
- 支持详细日志、数据库校验、批量申办、命令行参数
"""
import requests
import logging
import sys
from utils.data_factory import DataFactory

# 如需数据库校验请确保utils/mysql_util.py存在并实现MysqlUtil
try:
    from utils.mysql_util import MysqlUtil
except ImportError:
    MysqlUtil = None
import traceback
from datetime import datetime
# 移除 set_task, get_task 导入


class EtcApplyWorker:
    def __init__(self, params=None, progress_callback=None, base_url=None, log_file=None):
        """
        :param params: dict, 申办参数（如车牌、身份证、银行卡等），为空则自动生成
        :param progress_callback: 进度回调函数(percent:int, msg:str)
        :param base_url: 接口基础URL
        :param log_file: 日志文件路径
        """
        self.progress_callback = progress_callback
        self.base_url = base_url or "http://788360p9o5.yicp.fun"  # TODO: 替换为实际接口地址
        self.df = DataFactory()
        self.params = params or self._generate_params()
        self.session = requests.Session()
        self.order_id = None
        self.sign_order_id = None
        self.verify_code_no = None
        # 日志配置
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        if not self.logger.handlers:  # 只在第一次添加handler，防止日志重复
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            # 控制台输出
            ch = logging.StreamHandler(sys.stdout)
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)
            # 文件输出
            if log_file:
                fh = logging.FileHandler(log_file, encoding='utf-8')
                fh.setFormatter(formatter)
                self.logger.addHandler(fh)

    def _log(self, msg):
        self.logger.info(msg)

    def _generate_params(self):
        """自动生成一套测试数据"""
        car_info = self.df.random_car_info(province='苏', color='蓝色')
        return {
            "carNum": car_info['plate_number'],
            "vehicleColor": "0",  # 蓝色
            "truckchannelId": "0000",
            "channelId": "0000",
            "province": "广东省",
            "city": "深圳市",
            "productId": "1503564182627360770",
            "operatorCode": "TXB",
            "orderType": "0",
            "handleLocation": "广东省,深圳市,龙岗区",
            "tempCarNumFlag": "0",
            "bidOrderType": "1",
            "protocolId": "1480429588403593218",
            "signingImage": "https://img.jiaduobaoapp.com/images/files/2025/07/07/175185352707236.png",
            "protocolType": 0,
            "idCardUrl": "https://img.jiaduobaoapp.com/images/files/2025/07/07/175185335686382.jpg",
            "backIdCardUrl": "https://img.jiaduobaoapp.com/images/files/2025/07/07/1751853438620143.jpg",
            "cardHolder": self.df.random_name(),
            "idCode": self.df.random_id_number(),
            "idcardValidity": "2016.10.25-2026.10.25",
            "idAddress": "广东省龙川县龙母镇张乐村委会下乐汉村97号",
            "urgentContact": self.df.random_name(),
            "urgentPhone": self.df.random_phone(),
            "bindBankUrl": "",
            "bindBankName": "中国工商银行",
            "bindBankNo": self.df.random_bank_card(),
            "bankCode": "ICBC",
            "bindBankPhone": self.df.random_phone(),
            "bankCardType": "01",
            "bankChannelCode": "QUICK_COMBINED_PAY",
            "code": "184263",  # 验证码
            "bankCardInfoId": "1440968899762982912",
            "isAgree": 1,
            "licenseUrl": "https://img.jiaduobaoapp.com/images/files/2025/07/07/175185367647574.png",
            "backLicenseUrl": "https://img.jiaduobaoapp.com/images/files/2025/07/07/175185368337190.jpg",
            "carHeadUrl": "https://img.jiaduobaoapp.com/images/files/2025/07/07/175185369119853.png",
            "vehicleType": "小型轿车",
            "model": "长安牌SC1031GDD53",
            "vin": "WDDMH4DB4JJ476833",
            "engineNum": "18505834",
            "useCharacter": "非营运",
            "owner": self.df.random_name(),
            "registerDate": "20181029",
            "issueDate": "20181029",
            "approvedPassengerCapacity": 5,
            "length": 4660,
            "wide": 1775,
            "high": 1500,
            "grossMass": 2030,
            "unladenMass": 1454,
            "approvedLoad": "",
            "licenseVerifyFlag": 0,
            "updateCkg": "1",
            "addr": "湖南省湘潭县易俗河镇湘江路居委会"
        }

    def _update_progress(self, percent, msg):
        if self.progress_callback:
            self.progress_callback(percent, msg)
        self._log(f"[{percent}%] {msg}")

    def _post(self, path, data):
        url = self.base_url + path
        self._log(f"【接口请求】{path}\n参数: {data}")
        try:
            resp = self.session.post(url, json=data)
            resp.raise_for_status()
            res = resp.json()
            self._log(f"【接口响应】{path}\n返回: {res}")
        except Exception as e:
            tb = traceback.format_exc()
            self._log(f"【接口异常】{path}\n参数: {data}\n错误: {e}\n堆栈: {tb}")
            raise Exception(f"接口异常: {url}, 参数: {data}, 错误: {e}")
        if res.get('code') != 200:
            self._log(f"【接口失败】{path}\n参数: {data}\n返回: {res}")
            raise Exception(f"接口失败: {url}, 参数: {data}, 返回: {res}")
        return res

    def run(self, check_db=False):
        p = self.params
        try:
            self._update_progress(5, "1. 校验车牌")
            self._post("/rtx-app/apply/checkCarNum", {
                "carNum": p["carNum"],
                "vehicleColor": p["vehicleColor"],
                "truckchannelId": p["truckchannelId"]
            })

            self._update_progress(10, "2. 校验是否可申办")
            self._post("/rtx-app/apply/order/checkIsNotCarNum", {
                "channelId": p["channelId"],
                "carNum": p["carNum"]
            })

            self._update_progress(15, "3. 获取渠道地址")
            self._post("/rtx-app/apply/order/getChannelUseAddress", {
                "channelId": p["channelId"],
                "province": p["province"],
                "city": p["city"]
            })

            self._update_progress(20, "4. 获取可选服务")
            self._post("/rtx-app/service/optionalServiceList", {
                "productId": p["productId"],
                "orderId": "",
                "channelId": p["channelId"]
            })

            self._update_progress(30, "5. 提交车牌")
            res5 = self._post("/rtx-app/apply/submitCarNum", {
                "operatorCode": p["operatorCode"],
                "truckchannelId": p["truckchannelId"],
                "productId": p["productId"],
                "orderType": p["orderType"],
                "handleLocation": p["handleLocation"],
                "carNum": p["carNum"],
                "vehicleColor": p["vehicleColor"],
                "terminalId": "",
                "tempCarNumFlag": p["tempCarNumFlag"],
                "bidOrderType": p["bidOrderType"]
            })
            self.order_id = res5["data"]["orderId"]

            self._update_progress(40, "6. 协议签署")
            self._post("/rtx-app/protocol/add", {
                "orderId": self.order_id,
                "protocolId": p["protocolId"],
                "signingImage": p["signingImage"],
                "protocolType": p["protocolType"]
            })

            self._update_progress(50, "7. 提交身份和银行卡信息")
            res7 = self._post("/rtx-app/apply/submitIdentityWithBankSign", {
                "productId": p["productId"],
                "idCardUrl": p["idCardUrl"],
                "backIdCardUrl": p["backIdCardUrl"],
                "cardHolder": p["cardHolder"],
                "idCode": p["idCode"],
                "idcardValidity": p["idcardValidity"],
                "idAddress": p["idAddress"],
                "urgentContact": p["urgentContact"],
                "urgentPhone": p["urgentPhone"],
                "bindBankUrl": p["bindBankUrl"],
                "bindBankName": p["bindBankName"],
                "bindBankNo": p["bindBankNo"],
                "bankCode": p["bankCode"],
                "bindBankPhone": p["bindBankPhone"],
                "bankCardType": p["bankCardType"],
                "bankChannelCode": p["bankChannelCode"],
                "code": "",  # 第一次不传验证码
                "bankCardInfoId": p["bankCardInfoId"],
                "isAgree": p["isAgree"],
                "orderId": self.order_id
            })
            self.sign_order_id = res7["data"]["signOrderId"]
            self.verify_code_no = res7["data"]["verifyCodeNo"]

            self._update_progress(60, "8. 签约校验")
            self._post("/rtx-app/withhold/signCheck", {
                "productId": p["productId"],
                "verifyCode": p["code"],
                "bankCardNo": p["bindBankNo"],
                "bindBankPhone": p["bindBankPhone"],
                "idCode": p["idCode"],
                "verifyCodeNo": self.verify_code_no,
                "signOrderId": self.sign_order_id,
                "location": "2"
            })

            self._update_progress(70, "9. 保存车辆信息")
            res_vehicle = self._post("/rtx-app/apply/saveVehicleInfo", {
                "productId": p["productId"],
                "licenseUrl": p["licenseUrl"],
                "backLicenseUrl": p["backLicenseUrl"],
                "carHeadUrl": p["carHeadUrl"],
                "plateNum": p["carNum"],
                "vehicleType": p["vehicleType"],
                "model": p["model"],
                "vin": p["vin"],
                "engineNum": p["engineNum"],
                "useCharacter": p["useCharacter"],
                "owner": p["owner"],
                "registerDate": p["registerDate"],
                "issueDate": p["issueDate"],
                "vehicleColor": p["vehicleColor"],
                "approvedPassengerCapacity": p["approvedPassengerCapacity"],
                "length": p["length"],
                "wide": p["wide"],
                "high": p["high"],
                "grossMass": p["grossMass"],
                "unladenMass": p["unladenMass"],
                "approvedLoad": p["approvedLoad"],
                "licenseVerifyFlag": p["licenseVerifyFlag"],
                "updateCkg": p["updateCkg"],
                "addr": p["addr"],
                "orderId": self.order_id
            })
            # 保存etccardUserId供后续步骤用
            if res_vehicle and res_vehicle.get("data") and res_vehicle["data"].get("etccardUserId"):
                self.params["etccardUserId"] = res_vehicle["data"]["etccardUserId"]

            self._update_progress(80, "10. 可选服务更新")
            self._post("/rtx-app/service/optionalServiceUpdate", {
                "orderId": self.order_id
            })
            verify_code_today = datetime.now().strftime("%y%m%d")
            self._update_progress(85, "11. 代扣支付")
            self._post("/rtx-app/withhold/old/pay", {
                "bankCardNo": p["bindBankNo"],
                "etcCardUserId": p.get("etccardUserId", ""),
                "productId": p["productId"],
                "applyOrderId": self.order_id,
                "verifyCode": verify_code_today,
                "phoneNumber": p["bindBankPhone"]
            })

            self._update_progress(100, "申办流程完成！")
            if check_db and MysqlUtil:
                self.check_db()
        except Exception as e:
            self._update_progress(-1, f"流程失败: {e}")
            raise

    def check_db(self):
        """数据库校验：以order_id查rtx_etcapply_order表"""
        if not MysqlUtil:
            self._log("未找到MysqlUtil，无法校验数据库！")
            return
        db = MysqlUtil()
        sql = f"SELECT * FROM rtx_etcapply_order WHERE order_id='{self.order_id}'"
        result = db.query(sql)
        self._log(f"数据库校验结果: {result}")

    def run_until_step6(self):
        """
        只执行前6步，返回order_id、sign_order_id、verify_code_no（第7步前的上下文）
        """
        p = self.params
        try:
            self._update_progress(0, "准备开始申办流程")
            self._update_progress(5, "1. 校验车牌")
            self._post("/rtx-app/apply/checkCarNum", {
                "carNum": p["carNum"],
                "vehicleColor": p["vehicleColor"],
                "truckchannelId": p["truckchannelId"]
            })
            self._update_progress(10, "2. 校验是否可申办")
            self._post("/rtx-app/apply/order/checkIsNotCarNum", {
                "channelId": p["channelId"],
                "carNum": p["carNum"]
            })
            self._update_progress(15, "3. 获取渠道地址")
            self._post("/rtx-app/apply/order/getChannelUseAddress", {
                "channelId": p["channelId"],
                "province": p["province"],
                "city": p["city"]
            })
            self._update_progress(20, "4. 获取可选服务")
            self._post("/rtx-app/service/optionalServiceList", {
                "productId": p["productId"],
                "orderId": "",
                "channelId": p["channelId"]
            })
            self._update_progress(30, "5. 提交车牌")
            res5 = self._post("/rtx-app/apply/submitCarNum", {
                "operatorCode": p["operatorCode"],
                "truckchannelId": p["truckchannelId"],
                "productId": p["productId"],
                "orderType": p["orderType"],
                "handleLocation": p["handleLocation"],
                "carNum": p["carNum"],
                "vehicleColor": p["vehicleColor"],
                "terminalId": "",
                "tempCarNumFlag": p["tempCarNumFlag"],
                "bidOrderType": p["bidOrderType"]
            })
            self.order_id = res5["data"]["orderId"]
            self._update_progress(40, "6. 协议签署")
            self._post("/rtx-app/protocol/add", {
                "orderId": self.order_id,
                "protocolId": p["protocolId"],
                "signingImage": p["signingImage"],
                "protocolType": p["protocolType"]
            })
            # 返回上下文，供第7步用
            return {
                "order_id": self.order_id,
                "sign_order_id": None,
                "verify_code_no": None
            }
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            self._update_progress(-1, f"流程失败: {e}\n{tb}")
            raise

    def run_step7_get_code(self, order_id, sign_order_id):
        """
        单独执行第7步，返回verify_code_no
        """
        p = self.params
        try:
            self._update_progress(50, "7. 提交身份和银行卡信息")
            res7 = self._post("/rtx-app/apply/submitIdentityWithBankSign", {
                "productId": p["productId"],
                "idCardUrl": p["idCardUrl"],
                "backIdCardUrl": p["backIdCardUrl"],
                "cardHolder": p["cardHolder"],
                "idCode": p["idCode"],
                "idcardValidity": p["idcardValidity"],
                "idAddress": p["idAddress"],
                "urgentContact": p["urgentContact"],
                "urgentPhone": p["urgentPhone"],
                "bindBankUrl": p["bindBankUrl"],
                "bindBankName": p["bindBankName"],
                "bindBankNo": p["bindBankNo"],
                "bankCode": p["bankCode"],
                "bindBankPhone": p["bindBankPhone"],
                "bankCardType": p["bankCardType"],
                "bankChannelCode": p["bankChannelCode"],
                "code": "",  # 第一次不传验证码
                "bankCardInfoId": p["bankCardInfoId"],
                "isAgree": p["isAgree"],
                "orderId": order_id
            })
            sign_order_id = res7["data"]["signOrderId"]
            verify_code_no = res7["data"]["verifyCodeNo"]
            return {
                "sign_order_id": sign_order_id,
                "verify_code_no": verify_code_no
            }
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            self._update_progress(-1, f"获取验证码失败: {e}\n{tb}")
            raise

    def run_step8_to_end(self, verify_code, order_id, sign_order_id, verify_code_no):
        """
        输入验证码后，自动执行第8~11步，日志完整输出
        """
        p = self.params
        try:
            self._update_progress(60, "8. 签约校验")
            self._post("/rtx-app/withhold/signCheck", {
                "productId": p["productId"],
                "verifyCode": verify_code,
                "bankCardNo": p["bindBankNo"],
                "bindBankPhone": p["bindBankPhone"],
                "idCode": p["idCode"],
                "verifyCodeNo": verify_code_no,
                "signOrderId": sign_order_id,
                "location": "2"
            })
            self._update_progress(70, "9. 保存车辆信息")
            res_vehicle = self._post("/rtx-app/apply/saveVehicleInfo", {
                "productId": p["productId"],
                "licenseUrl": p["licenseUrl"],
                "backLicenseUrl": p["backLicenseUrl"],
                "carHeadUrl": p["carHeadUrl"],
                "plateNum": p["carNum"],
                "vehicleType": p["vehicleType"],
                "model": p["model"],
                "vin": p["vin"],
                "engineNum": p["engineNum"],
                "useCharacter": p["useCharacter"],
                "owner": p["owner"],
                "registerDate": p["registerDate"],
                "issueDate": p["issueDate"],
                "vehicleColor": p["vehicleColor"],
                "approvedPassengerCapacity": p["approvedPassengerCapacity"],
                "length": p["length"],
                "wide": p["wide"],
                "high": p["high"],
                "grossMass": p["grossMass"],
                "unladenMass": p["unladenMass"],
                "approvedLoad": p["approvedLoad"],
                "licenseVerifyFlag": p["licenseVerifyFlag"],
                "updateCkg": p["updateCkg"],
                "addr": p["addr"],
                "orderId": order_id
            })
            if res_vehicle and res_vehicle.get("data") and res_vehicle["data"].get("etccardUserId"):
                self.params["etccardUserId"] = res_vehicle["data"]["etccardUserId"]
            self._update_progress(80, "10. 可选服务更新")
            self._post("/rtx-app/service/optionalServiceUpdate", {
                "orderId": order_id
            })
            verify_code_today = datetime.now().strftime("%y%m%d")
            self._update_progress(85, "11. 代扣支付")
            self._post("/rtx-app/withhold/old/pay", {
                "bankCardNo": p["bindBankNo"],
                "etcCardUserId": p.get("etccardUserId", ""),
                "productId": p["productId"],
                "applyOrderId": order_id,
                "verifyCode": verify_code_today,
                "phoneNumber": p["bindBankPhone"]
            })
            self._update_progress(90, "12. 绑定申办")
            self._post("/rtx-app/apply/bindApplication", {
                "orderId": order_id,
                "productId": p["productId"],
                "issueFalg": None
            })
            self._update_progress(100, "申办流程完成！")
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            self._update_progress(-1, f"后续流程失败: {e}\n{tb}")
            raise


# 批量申办
def batch_apply(n, params=None, base_url=None, log_file=None):
    for i in range(n):
        try:
            worker = EtcApplyWorker(params=params, base_url=base_url, log_file=log_file)
            worker.run()
        except Exception as e:
            print(f"第{i + 1}次申办失败: {e}")


# 命令行参数支持
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--carNum', type=str, help='车牌号')
    parser.add_argument('--idCode', type=str, help='身份证号')
    parser.add_argument('--bindBankNo', type=str, help='银行卡号')
    parser.add_argument('--n', type=int, default=1, help='申办次数')
    parser.add_argument('--log_file', type=str, help='日志文件')
    parser.add_argument('--base_url', type=str, help='接口基础URL')
    parser.add_argument('--check_db', action='store_true', help='流程后校验数据库')
    args = parser.parse_args()
    params = {k: v for k, v in vars(args).items() if v and k not in ['n', 'log_file', 'base_url', 'check_db']}
    if args.n > 1:
        batch_apply(args.n, params=params, base_url=args.base_url, log_file=args.log_file)
    else:
        worker = EtcApplyWorker(params=params, base_url=args.base_url, log_file=args.log_file)
        worker.run(check_db=args.check_db)
