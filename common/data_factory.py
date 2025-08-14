# -*- coding: utf-8 -*-
# -------------------------------------------------------------
# ETC业务常用测试数据生成工具类
# 支持车牌、姓名、身份证、手机号、设备号、订单号、ETC号、OBN号、银行卡号、银行地址等
# -------------------------------------------------------------
import random
from faker import Faker

fake = Faker('zh_CN')

class DataFactory:
    """
    ETC业务常用测试数据生成工具类
    """
    # 省份简称与ETC/OBN前缀映射
    PROVINCE_PREFIX = {
        '京': '1100', '津': '1200', '沪': '3100', '渝': '5000',
        '冀': '1300', '豫': '4100', '云': '5300', '辽': '2100', '黑': '2300',
        '湘': '4301', '皖': '3401', '鲁': '3700', '新': '6500', '苏': '3201',
        '浙': '3300', '赣': '3600', '鄂': '4200', '桂': '4501', '甘': '6200',
        '晋': '1400', '蒙': '1501', '陕': '6100', '吉': '2200', '闽': '3500',
        '贵': '5200', '青': '6300', '藏': '5400', '川': '5101', '宁': '6400', '琼': '4600'
    }
    PROVINCE_LIST = list(PROVINCE_PREFIX.keys())
    COLOR_TYPES = [
        {'color': '蓝色', 'length': 7},
        {'color': '黄色', 'length': 7},
        {'color': '绿色', 'length': 8},
        {'color': '白色', 'length': random.choice([6,7])},
        {'color': '黑色', 'length': 7}
    ]

    @staticmethod
    def random_plate_number(province: str = None, color: str = None, prefix: str = None) -> dict:
        """
        生成合规的中国大陆车牌号，支持蓝、黄、绿、白、黑色，自动适配后端校验
        :param province: 省份简称，如'粤'、'京'等
        :param color: 车牌颜色
        :param prefix: 车牌第二位字母
        :return: {'plate_number': '粤A12345', 'color': '蓝色'}
        """
        provinces = '京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼'
        letters = 'ABCDEFGHJKLMNPQRSTUVWXYZ'
        # 修复：如果province不是字符串或不在provinces，直接随机
        province_code = province if isinstance(province, str) and province in provinces else random.choice(provinces)
        color_types = ['蓝色', '黄色', '绿色', '白色', '黑色']
        color = color if color in color_types else random.choices(color_types, weights=[60, 15, 15, 5, 5])[0]
        letter = prefix if (isinstance(prefix, str) and prefix in letters) else random.choice(letters)

        if color == '蓝色':
            while True:
                tail = ''.join(random.choices(letters + '0123456789', k=5))
                if any(c.isdigit() for c in tail):
                    break
            plate_number = f"{province_code}{letter}{tail}"
        elif color == '黄色':
            while True:
                tail = ''.join(random.choices(letters + '0123456789', k=5))
                if any(c.isdigit() for c in tail):
                    break
            suffix = random.choice(['', '学', '挂'])
            plate_number = f"{province_code}{letter}{tail[:5-len(suffix)]}{suffix}"
        elif color == '绿色':
            d_or_f = random.choice(['D', 'F'])
            while True:
                tail = ''.join(random.choices(letters + '0123456789', k=5))
                if any(c.isdigit() for c in tail):
                    break
            plate_number = f"{province_code}{letter}{d_or_f}{tail}"
        elif color == '白色':
            length = random.choice([6, 7])
            if length == 6:
                while True:
                    tail = ''.join(random.choices(letters + '0123456789', k=4))
                    if any(c.isdigit() for c in tail):
                        break
                plate_number = f"{province_code}{letter}{tail}"
            else:
                while True:
                    tail = ''.join(random.choices(letters + '0123456789', k=5))
                    if any(c.isdigit() for c in tail):
                        break
                plate_number = f"{province_code}{letter}{tail}"
        elif color == '黑色':
            z = 'Z'
            region = random.choice(['港', '澳'])
            digits = ''.join(random.choices('0123456789', k=4))
            plate_number = f"{province_code}{z}{region}{digits}"
        else:
            plate_number = f"{province_code}{letter}00000"  # fallback

        return {'plate_number': plate_number, 'color': color, 'province': province_code}

    @staticmethod
    def random_name() -> str:
        return fake.name()

    @staticmethod
    def random_id_number() -> str:
        return fake.ssn()

    @staticmethod
    def random_phone() -> str:
        return fake.phone_number()

    @staticmethod
    def random_bank_card() -> str:
        """生成随机银行卡号（16~19位）"""
        length = random.choice([16, 17, 18, 19])
        return '6' + ''.join(random.choices('0123456789', k=length-1))

    @staticmethod
    def random_etc_number(province: str = '苏', length: int = 20) -> str:
        prefix = DataFactory.PROVINCE_PREFIX.get(province, '3200')
        suffix_len = length - len(prefix)
        suffix = ''.join(random.choices('0123456789', k=suffix_len))
        return prefix + suffix

    @staticmethod
    def random_obn_number(province: str = '苏', length: int = 16) -> str:
        prefix = DataFactory.PROVINCE_PREFIX.get(province, '3200')
        suffix_len = length - len(prefix)
        suffix = ''.join(random.choices('0123456789', k=suffix_len))
        return prefix + suffix

    @staticmethod
    def random_snowflake_id():
        import time
        import random
        # 时间戳+随机数，保证唯一性（简化版雪花ID）
        return int(str(int(time.time() * 1000)) + str(random.randint(100, 999)))

    @staticmethod
    def random_device_id() -> str:
        """生成随机设备ID"""
        return ''.join(random.choices('0123456789ABCDEF', k=16))
    
    @staticmethod
    def random_order_id() -> str:
        """生成随机订单号"""
        import time
        timestamp = str(int(time.time()))
        random_suffix = ''.join(random.choices('0123456789', k=6))
        return f"ORD{timestamp}{random_suffix}"
    
    @staticmethod
    def random_bank_address() -> str:
        """生成随机银行地址"""
        cities = ['北京', '上海', '广州', '深圳', '杭州', '南京', '苏州', '成都']
        streets = ['中山路', '解放路', '人民路', '建设路', '和平路', '胜利路', '东风路', '西湖路']
        return f"{random.choice(cities)}市{random.choice(streets)}{random.randint(1, 999)}号"

    def random_car_info(self, province='苏', color='蓝色'):
        """
        生成一组车辆信息，包括车牌号和颜色
        :param province: 省份简称
        :param color: 车牌颜色
        :return: dict, 如 {'plate_number': '苏A12345', 'color': '蓝色'}
        """
        info = self.random_plate_number(province=province, color=color)
        return {
            'plate_number': info['plate_number'],
            'color': info['color'],
            'province': info.get('province', province)
        }
