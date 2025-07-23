import random

from utils.data_factory import DataFactory


def build_stock_in_params(car_num):
    obn_no = f"OBN{random.randint(100000, 999999)}"
    etc_no = f"ETC{random.randint(100000, 999999)}"
    return {
        "car_num": car_num,
        "obn_no": obn_no,
        "etc_no": etc_no,
        # 可根据实际需求补充其它参数
    }


def generate_default_params():
    df = DataFactory()
    car_info = df.random_car_info(province='苏', color='蓝色')
    return {
        "carNum": car_info['plate_number'],
        "vehicleColor": "0",
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
        "cardHolder": df.random_name(),
        "idCode": df.random_id_number(),
        "idcardValidity": "2016.10.25-2026.10.25",
        "idAddress": "广东省龙川县龙母镇张乐村委会下乐汉村97号",
        "urgentContact": df.random_name(),
        "urgentPhone": df.random_phone(),
        "bindBankUrl": "",
        "bindBankName": "中国工商银行",
        "bindBankNo": df.random_bank_card(),
        "bankCode": "ICBC",
        "bindBankPhone": df.random_phone(),
        "bankCardType": "01",
        "bankChannelCode": "QUICK_COMBINED_PAY",
        "code": "184263",
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
        "owner": df.random_name(),
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
