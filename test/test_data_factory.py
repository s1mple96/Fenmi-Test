import pytest
from utils.data_factory import DataFactory

class TestDataFactory:
    def test_random_plate_number(self):
        result = DataFactory.random_plate_number()
        print('随机车牌号:', result)
        assert 'plate_number' in result and 'color' in result
        assert isinstance(result['plate_number'], str)
        assert isinstance(result['color'], str)

    def test_random_name(self):
        name = DataFactory.random_name()
        print('随机姓名:', name)
        assert isinstance(name, str)
        assert 2 <= len(name) <= 4

    def test_random_id_number(self):
        id_num = DataFactory.random_id_number()
        print('随机身份证号:', id_num)
        assert len(id_num) == 18

    def test_random_phone(self):
        phone = DataFactory.random_phone()
        print('随机手机号:', phone)
        assert len(phone) == 11

    def test_random_device_id(self):
        device_id = DataFactory.random_device_id()
        print('随机设备号:', device_id)
        assert len(device_id) == 16

    def test_random_order_id(self):
        order_id = DataFactory.random_order_id()
        print('随机订单号:', order_id)
        assert order_id.startswith('ETC')

    def test_random_car_info(self):
        car_info = DataFactory.random_car_info()
        print('随机车辆信息:', car_info)
        assert 'brand' in car_info and 'type' in car_info and 'color' in car_info
        assert 'plate_number' in car_info and 'plate_color' in car_info

    def test_random_etc_number(self):
        etc_num = DataFactory.random_etc_number()
        print('随机ETC号:', etc_num)
        assert etc_num.startswith('622') and len(etc_num) == 19

    def test_random_obn_number(self):
        obn_num = DataFactory.random_obn_number()
        print('随机OBN号:', obn_num)
        assert obn_num.startswith('9000') and len(obn_num) == 20

    def test_random_bank_card(self):
        card = DataFactory.random_bank_card()
        print('随机银行卡号:', card)
        assert card.startswith('62') and 16 <= len(card) <= 19

    def test_random_bank_address(self):
        addr = DataFactory.random_bank_address()
        print('随机银行地址:', addr)
        assert '分行' in addr
