import json
import os
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QLineEdit
from utils.plate_util import random_plate_letter, random_plate_number
from utils.vin_util import get_next_vin
from utils.config_util import save_four_elements, FOUR_ELEMENTS_KEYS
from ui.components.province_dialog import ProvinceDialog
from ui.components.product_select_dialog import ProductSelectDialog
from ui.components.plate_letter_dialog import PlateLetterDialog


def excepthook(type, value, traceback):
    print("全局异常:", value)
    QMessageBox.critical(None, "程序异常", f"{value}")

def fill_form(inputs: dict, fields, data: dict):
    """根据字段配置和数据自动填充表单"""
    for _, k, _, _ in fields:
        if k in inputs:
            inputs[k].setText(data.get(k, ''))

def collect_form(inputs: dict):
    """收集所有输入控件的内容为dict"""
    return {k: w.text().strip() for k, w in inputs.items()}

def set_lineedit_value(lineedit, value):
    """设置QLineEdit的值"""
    lineedit.setText(value)

def handle_select_province(ui):
    # 获取当前输入框内容，只取第一个字作为省份简称
    current_abbr = ui.plate_province_edit.text().strip()[:1]
    dlg = ProvinceDialog(selected_province=current_abbr)
    if dlg.exec_() == dlg.Accepted:
        ui.plate_province_edit.setText(dlg.get_selected_province())

def handle_select_plate_letter(ui):
    current_letter = ui.plate_letter_edit.text().strip()[:1]
    dlg = PlateLetterDialog(selected_letter=current_letter)
    if dlg.exec_() == dlg.Accepted:
        ui.plate_letter_edit.setText(dlg.get_selected_letter())

def handle_random_plate_number(ui):
    ui.plate_number_edit.setText(random_plate_number())

def handle_get_vin(ui):
    if not hasattr(ui, 'vin_index'):
        ui.vin_index = 0
    vin, ui.vin_index = get_next_vin(ui.vin_index)
    ui.vin_edit.setText(vin)
    if hasattr(ui, 'log_text'):
        ui.log_text.append(f"已自动获取VIN: {vin}")

def handle_save_four_elements(ui):
    item = {k: ui.inputs[k].text().strip() for k in FOUR_ELEMENTS_KEYS}
    try:
        save_four_elements(item)
        QMessageBox.information(ui, "成功", "四要素保存成功！")
    except Exception as e:
        QMessageBox.critical(ui, "文件错误", f"保存四要素到json失败: {e}")

def build_car_num(province,letter,number):
    return f"{province}{letter}{number}"


def handle_save_to_db(ui):
    import uuid
    import datetime
    import random
    import os
    import json
    from utils.mysql_util import MySQLUtil

    # 车牌简称到省份全名映射
    PLATE_PREFIX_TO_PROVINCE = {
        "苏": "江苏",
        "湘": "湖南",
        "桂": "广西",
        "黑": "黑龙江",
        "蒙": "内蒙古",
        "皖": "安徽",
        "川": "四川",
        # ... 其它省份
    }
    # 省份与设备号前缀映射（纯数字）
    PROVINCE_CODE_MAP = {
        "江苏": "3201",
        "湖南": "4301",
        "广西": "4501",
        "黑龙江": "2301",
        "内蒙古": "1501",
        "安徽": "3401",
        "四川": "5101",
        # ... 其它省份
    }
    def generate_device_no(province, device_type):
        code = PROVINCE_CODE_MAP.get(province, "9999")
        length = 16 if device_type == "0" else 20
        remain = length - len(code)
        suffix = ''.join(random.choices("0123456789", k=remain))
        return code + suffix

    province = ui.inputs['plate_province'].text().strip()
    letter = ui.inputs['plate_letter'].text().strip()
    number = ui.inputs['plate_number'].text().strip()
    # 新增：将简称转换为省份全名
    province_name = PLATE_PREFIX_TO_PROVINCE.get(province, province)
    car_num = f"{province}{letter}{number}"
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    base_data = {
        "CARD_OPERATORS": "1",
        "STATUS": "1",
        "CAR_NUM": car_num,
        "STOCK_STATUS": "0",
        "SOURCE": "1",
        "REMARK": "激活设备不存在库存内",
        "CREATE_TIME": now,
        "DEVICE_CATEGORY": "0"
    }
    obn_no = generate_device_no(province_name, "0")
    etc_no = generate_device_no(province_name, "1")
    obn_data = base_data.copy()
    obn_data.update({
        "NEWSTOCK_ID": uuid.uuid4().hex,
        "INTERNAL_DEVICE_NO": obn_no,
        "EXTERNAL_DEVICE_NO": obn_no,
        "TYPE": "0"
    })
    etc_data = base_data.copy()
    etc_data.update({
        "NEWSTOCK_ID": uuid.uuid4().hex,
        "INTERNAL_DEVICE_NO": etc_no,
        "EXTERNAL_DEVICE_NO": etc_no,
        "TYPE": "1"
    })
    # 自动加载MySQL连接参数
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'connections.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        configs = json.load(f)
    mysql_conf = None
    for c in configs:
        if c.get('type') == 'mysql':
            host, port = c['address'].split(':')
            mysql_conf = {
                'host': host,
                'port': int(port),
                'user': c['username'],
                'password': c['password'],
                'database': 'hcb',
            }
            break
    if not mysql_conf:
        raise Exception("未找到MySQL连接配置！")
    db = MySQLUtil(**mysql_conf)
    db.connect()
    def insert_row(row):
        keys = ','.join(f'`{k}`' for k in row.keys())
        vals = ','.join(['%s'] * len(row))
        sql = f"INSERT INTO hcb_newstock ({keys}) VALUES ({vals})"
        db.execute(sql, tuple(row.values()))
    insert_row(obn_data)
    insert_row(etc_data)
    db.close()
    if hasattr(ui, 'log_text'):
        ui.log_text.append(f"OBN/ETC设备已直接插入数据库，车牌号: {car_num}\nOBN号: {obn_no}  ETC号: {etc_no}")

def handle_select_product(ui):
    dlg = ProductSelectDialog(ui)
    if dlg.exec_() == dlg.Accepted and dlg.selected_product:
        ui.product_edit.setText(dlg.selected_product.get('product_name', ''))
        ui.selected_product = dlg.selected_product

def handle_apply(ui):
    params = {k: w.text().strip() for k, w in ui.inputs.items()}
    # 拼接 carNum
    params['carNum'] = f"{params.get('plate_province', '')}{params.get('plate_letter', '')}{params.get('plate_number', '')}"
    # 字段映射
    params['cardHolder'] = params.get('name', '')
    params['idCode'] = params.get('id_code', '')
    params['bindBankPhone'] = params.get('phone', '')
    params['bindBankNo'] = params.get('bank_no', '')
    params['vehicleColor'] = params.get('vehicle_color', '')
    params['vin'] = params.get('vin', '')
    if hasattr(ui, 'selected_product') and ui.selected_product:
        params['productId'] = ui.selected_product.get('product_id')
    else:
        # 如果没有选择产品，使用默认值
        params['productId'] = 1503564182627360770
    # 自动补全所有业务必需但UI没有的字段
    params['truckchannelId'] = params.get('truckchannelId', '0000')
    params['channelId'] = params.get('channelId', '0000')
    params['orderType'] = params.get('orderType', '0')
    params['tempCarNumFlag'] = params.get('tempCarNumFlag', '0')
    params['bidOrderType'] = params.get('bidOrderType', '1')
    params['province'] = params.get('province', '广东省')
    params['city'] = params.get('city', '深圳市')
    params['handleLocation'] = params.get('handleLocation', '广东省,深圳市,龙岗区')
    params['protocolId'] = params.get('protocolId', '1480429588403593218')
    params['signingImage'] = params.get('signingImage', 'https://img.jiaduobaoapp.com/images/files/2025/07/07/175185352707236.png')
    params['protocolType'] = params.get('protocolType', 0)
    params['idCardUrl'] = params.get('idCardUrl', 'https://img.jiaduobaoapp.com/images/files/2025/07/07/175185335686382.jpg')
    params['backIdCardUrl'] = params.get('backIdCardUrl', 'https://img.jiaduobaoapp.com/images/files/2025/07/07/1751853438620143.jpg')
    params['idcardValidity'] = params.get('idcardValidity', '2016.10.25-2026.10.25')
    params['idAddress'] = params.get('idAddress', '广东省龙川县龙母镇张乐村委会下乐汉村97号')
    params['urgentContact'] = params.get('urgentContact', params.get('urgentContact', '测试员'))
    params['urgentPhone'] = params.get('urgentPhone', params.get('urgentPhone', '13316690083'))
    params['bindBankUrl'] = params.get('bindBankUrl', '')
    params['bindBankName'] = params.get('bindBankName', '中国工商银行')
    params['bankCode'] = params.get('bankCode', 'ICBC')
    params['bankCardType'] = params.get('bankCardType', '01')
    params['bankChannelCode'] = params.get('bankChannelCode', 'QUICK_COMBINED_PAY')
    params['code'] = params.get('code', '')
    params['bankCardInfoId'] = params.get('bankCardInfoId', '1440968899762982912')
    params['isAgree'] = params.get('isAgree', 1)
    params['licenseUrl'] = params.get('licenseUrl', 'https://img.jiaduobaoapp.com/images/files/2025/07/07/175185367647574.png')
    params['backLicenseUrl'] = params.get('backLicenseUrl', 'https://img.jiaduobaoapp.com/images/files/2025/07/07/175185368337190.jpg')
    params['carHeadUrl'] = params.get('carHeadUrl', 'https://img.jiaduobaoapp.com/images/files/2025/07/07/175185369119853.png')
    params['vehicleType'] = params.get('vehicleType', '小型轿车')
    params['model'] = params.get('model', '长安牌SC1031GDD53')
    params['engineNum'] = params.get('engineNum', '18505834')
    params['useCharacter'] = params.get('useCharacter', '非营运')
    params['owner'] = params.get('owner', params.get('name', ''))
    params['registerDate'] = params.get('registerDate', '20181029')
    params['issueDate'] = params.get('issueDate', '20181029')
    params['approvedPassengerCapacity'] = params.get('approvedPassengerCapacity', 5)
    params['length'] = params.get('length', 4660)
    params['wide'] = params.get('wide', 1775)
    params['high'] = params.get('high', 1500)
    params['grossMass'] = params.get('grossMass', 2030)
    params['unladenMass'] = params.get('unladenMass', 1454)
    params['approvedLoad'] = params.get('approvedLoad', '')
    params['licenseVerifyFlag'] = params.get('licenseVerifyFlag', 0)
    params['updateCkg'] = params.get('updateCkg', '1')
    params['addr'] = params.get('addr', '湖南省湘潭县易俗河镇湘江路居委会')
    # 继续补全其它可能缺失的字段
    params['operatorCode'] = params.get('operatorCode', 'TXB')
    from worker.etc.logic import start_etc_apply_flow
    start_etc_apply_flow(params, ui)

def fill_default_values(ui):
    """从config/default_values.json加载默认值并填充到输入框"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'config', 'default_values.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            defaults = json.load(f)
        for k, v in defaults.items():
            if k in ui.inputs:
                ui.inputs[k].setText(v)
            if k == 'vehicle_color' and hasattr(ui, 'plate_color_combo'):
                idx = ui.plate_color_combo.findText(v)
                if idx >= 0:
                    ui.plate_color_combo.setCurrentIndex(idx)
    except Exception as e:
        print(f"加载默认值失败: {e}")