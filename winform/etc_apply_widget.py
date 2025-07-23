import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QTextEdit, QLabel, QHBoxLayout, QMessageBox, QDialog, QGridLayout, QComboBox, QProgressBar
)
from PyQt5.QtCore import pyqtSignal, Qt, QTimer, QThread, QMetaObject, Q_ARG
import random
import string
from utils.data_factory import DataFactory
from worker.etc_apply_worker import EtcApplyWorker
import threading
from utils.vin_recent_spider import get_recent_vins, get_latest_vin
from utils.mysql_util import MySQLUtil
import json
import os

# 省份列表，可根据实际需求补充
PROVINCES = DataFactory.PROVINCE_LIST

def random_plate_letter():
    return random.choice(string.ascii_uppercase)

def random_plate_number(province=None, letter=None):
    # 用 DataFactory 生成车牌号，拆分省份、字母、号码
    plate_info = DataFactory.random_plate_number(province=province)
    plate = plate_info['plate_number']
    # 省份1字，字母1字，号码其余
    return plate[2:]

def resource_path(relative_path):
    """获取资源文件的绝对路径，兼容PyInstaller打包和源码运行"""
    if hasattr(sys, '_MEIPASS'):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class ProvinceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择省份")
        self.setFixedSize(400, 220)
        layout = QGridLayout()
        self.setLayout(layout)
        self.selected = None
        col_count = 6
        for idx, prov in enumerate(PROVINCES):
            btn = QPushButton(prov)
            btn.setFixedSize(50, 30)
            btn.clicked.connect(lambda _, p=prov: self.select_province(p))
            layout.addWidget(btn, idx // col_count, idx % col_count)
    def select_province(self, prov):
        self.selected = prov
        self.accept()

class VerifyCodeDialog(QDialog):
    def __init__(self, parent=None, on_get_code=None, on_confirm=None):
        super().__init__(parent)
        self.setWindowTitle("请输入验证码")
        self.setFixedSize(320, 120)
        self.on_get_code = on_get_code
        self.on_confirm = on_confirm
        self.timer = None
        self.time_left = 60
        layout = QVBoxLayout()
        input_layout = QHBoxLayout()
        self.code_edit = QLineEdit()
        self.code_edit.setPlaceholderText("请输入验证码")
        input_layout.addWidget(QLabel("验证码："))
        input_layout.addWidget(self.code_edit)
        layout.addLayout(input_layout)
        btn_layout = QHBoxLayout()
        self.get_code_btn = QPushButton("获取验证码")
        self.get_code_btn.clicked.connect(self.get_code)
        self.confirm_btn = QPushButton("确认")
        self.confirm_btn.clicked.connect(self.confirm)
        btn_layout.addWidget(self.get_code_btn)
        btn_layout.addWidget(self.confirm_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.confirm_btn.setEnabled(False)
    def get_code(self):
        if self.on_get_code:
            self.on_get_code(self)
        self.get_code_btn.setEnabled(False)
        self.time_left = 60
        self.get_code_btn.setText(f"重新获取({self.time_left}s)")
        if self.timer:
            self.timer.stop()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)
        self.confirm_btn.setEnabled(True)
    def update_timer(self):
        self.time_left -= 1
        if self.time_left > 0:
            self.get_code_btn.setText(f"重新获取({self.time_left}s)")
        else:
            self.timer.stop()
            self.get_code_btn.setEnabled(True)
            self.get_code_btn.setText("获取验证码")
    def confirm(self):
        code = self.code_edit.text().strip()
        if not code:
            QMessageBox.warning(self, "提示", "请输入验证码")
            return
        if self.on_confirm:
            self.on_confirm(code)
        self.accept()

class WorkerQThread(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(object)
    def __init__(self, worker_func, *args, **kwargs):
        super().__init__()
        self.worker_func = worker_func
        self.args = args
        self.kwargs = kwargs
    def run(self):
        try:
            result = self.worker_func(*self.args, **self.kwargs)
            self.finished_signal.emit(result)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            self.log_signal.emit(f"线程异常: {e}\n{tb}")
            self.finished_signal.emit(None)

class ProductSelectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择产品")
        self.setFixedSize(400, 150)
        layout = QVBoxLayout()
        self.combo = QComboBox()
        self.products = []
        self.selected_product = None
        layout.addWidget(QLabel("请选择产品："))
        layout.addWidget(self.combo)
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.load_products()
        self.combo.currentIndexChanged.connect(self.on_select)

    def load_products(self):
        # 自动读取config/connections.json
        config_path = resource_path('config/connections.json')
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
                    'database': 'rtx',
                }
                break
        if not mysql_conf:
            QMessageBox.critical(self, "错误", "未找到MySQL连接配置！")
            return
        try:
            db = MySQLUtil(**mysql_conf)
            db.connect()
            sql = ("select product_id,product_name,operator_code,status "
                   "from rtx_product "
                   "where PRODUCT_ID in "
                   "(select PRODUCT_ID from rtx_channel_company_profit "
                   "where channelcompany_id = 'd4949f0bc4c04a53987ac747287f3943')")
            rows = db.query(sql)
            db.close()
            if not rows:
                QMessageBox.warning(self, "提示", "未查到可选产品，请检查数据库配置和权限！")
                return
            self.products = rows
            for row in rows:
                self.combo.addItem(f"{row['product_name']}（{row['operator_code']}）", row)
            self.selected_product = rows[0]
        except Exception as e:
            QMessageBox.critical(self, "数据库错误", str(e))

    def on_select(self, idx):
        if 0 <= idx < len(self.products):
            self.selected_product = self.products[idx]

class EtcApplyWidget(QWidget):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(str)
    # 可定义信号与主窗口通信
    apply_submitted = pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.product_id = None
        self.operator_code = None
        self.product_name = None
        self.products = []
        self.init_product_info()
        self.init_ui()
        self.log_signal.connect(self.append_log)
        self.progress_signal.connect(self.progress_label.setText)
        self.worker_thread = None
        self.worker_thread_list = []  # 用于持有所有线程，防止被GC
        self.verify_dialog = None     # 用于持有弹窗对象，防止被GC
        self.vin_list = []           # VIN码列表
        self.vin_index = 0           # 当前VIN索引

    def init_product_info(self):
        # 自动读取config/connections.json
        config_path = resource_path('config/connections.json')
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
                    'database': 'rtx',
                }
                break
        if not mysql_conf:
            QMessageBox.critical(self, "错误", "未找到MySQL连接配置！")
            raise Exception("未找到MySQL连接配置！")
        try:
            db = MySQLUtil(**mysql_conf)
            db.connect()
            sql = ("select product_id,product_name,operator_code,status "
                   "from rtx_product "
                   "where PRODUCT_ID in "
                   "(select PRODUCT_ID from rtx_channel_company_profit "
                   "where channelcompany_id = 'd4949f0bc4c04a53987ac747287f3943')")
            rows = db.query(sql)
            db.close()
            if not rows:
                QMessageBox.warning(self, "提示", "未查到可选产品，请检查数据库配置和权限！")
                raise Exception("未查到可选产品")
            self.products = rows
            # 默认选中第一个产品
            self.product_id = rows[0]['product_id']
            self.operator_code = rows[0]['operator_code']
            self.product_name = rows[0]['product_name']
        except Exception as e:
            QMessageBox.critical(self, "数据库错误", str(e))
            raise

    def init_ui(self):
        layout = QVBoxLayout()
        # 产品选择显示区
        product_layout = QHBoxLayout()
        self.product_label = QLabel(f"产品：{self.product_name}（{self.operator_code}）")
        change_btn = QPushButton("更换产品")
        change_btn.clicked.connect(self.change_product)
        product_layout.addWidget(self.product_label)
        product_layout.addWidget(change_btn)
        product_layout.addStretch()
        layout.addLayout(product_layout)
        
        form_layout = QFormLayout()

        # 省份（弹窗选择）
        self.province_edit = QLineEdit('苏')
        self.province_edit.setReadOnly(True)
        province_btn = QPushButton("选择省份")
        province_btn.clicked.connect(self.choose_province)
        province_layout = QHBoxLayout()
        province_layout.addWidget(self.province_edit)
        province_layout.addWidget(province_btn)
        form_layout.addRow("省份", province_layout)

        # 车牌颜色选择
        self.plate_color_combo = QComboBox()
        self.plate_color_combo.addItems(["蓝色", "黄色", "绿色", "白色", "黑色"])
        self.plate_color_combo.setCurrentText("蓝色")
        plate_color_layout = QHBoxLayout()
        plate_color_layout.addWidget(QLabel("车牌颜色"))
        plate_color_layout.addWidget(self.plate_color_combo)
        form_layout.addRow(plate_color_layout)

        # 车牌号分三部分
        self.plate_province_edit = QLineEdit('苏')
        self.plate_province_edit.setFixedWidth(30)
        self.plate_province_edit.setReadOnly(True)
        self.plate_letter_edit = QLineEdit('Z')
        self.plate_letter_edit.setFixedWidth(30)
        self.plate_number_edit = QLineEdit('9T4P0')
        self.plate_number_edit.setFixedWidth(70)
        plate_btn = QPushButton("随机")
        plate_btn.clicked.connect(self.random_plate_number_only)
        plate_layout = QHBoxLayout()
        plate_layout.addWidget(self.plate_province_edit)
        plate_layout.addWidget(self.plate_letter_edit)
        plate_layout.addWidget(self.plate_number_edit)
        plate_layout.addWidget(plate_btn)
        form_layout.addRow("车牌号", plate_layout)

        # VIN码
        self.vin_edit = QLineEdit()
        vin_btn = QPushButton("自动获取VIN")
        vin_btn.clicked.connect(self.get_vin)
        vin_layout = QHBoxLayout()
        vin_layout.addWidget(self.vin_edit)
        vin_layout.addWidget(vin_btn)
        form_layout.addRow("VIN码", vin_layout)

        # 姓名
        self.name_edit = QLineEdit('')
        name_btn = QPushButton("随机")
        name_btn.clicked.connect(self.random_name)
        name_layout = QHBoxLayout()
        name_layout.addWidget(self.name_edit)
        name_layout.addWidget(name_btn)
        form_layout.addRow("姓名", name_layout)

        # 身份证
        self.id_edit = QLineEdit('')
        id_btn = QPushButton("随机")
        id_btn.clicked.connect(self.random_id)
        id_layout = QHBoxLayout()
        id_layout.addWidget(self.id_edit)
        id_layout.addWidget(id_btn)
        form_layout.addRow("身份证", id_layout)

        # 手机号
        self.phone_edit = QLineEdit('')
        phone_btn = QPushButton("随机")
        phone_btn.clicked.connect(self.random_phone)
        phone_layout = QHBoxLayout()
        phone_layout.addWidget(self.phone_edit)
        phone_layout.addWidget(phone_btn)
        form_layout.addRow("手机号", phone_layout)

        # 银行卡号
        self.bank_edit = QLineEdit('')
        bank_btn = QPushButton("随机")
        bank_btn.clicked.connect(self.random_bank)
        bank_layout = QHBoxLayout()
        bank_layout.addWidget(self.bank_edit)
        bank_layout.addWidget(bank_btn)
        form_layout.addRow("银行卡号", bank_layout)

        layout.addLayout(form_layout)

        # 生成按钮
        self.gen_btn = QPushButton("一键申办ETC")
        self.gen_btn.clicked.connect(self.on_apply)
        layout.addWidget(self.gen_btn)

        # 进度与日志
        self.progress_label = QLabel("进度：等待操作")
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_label)
        layout.addWidget(self.progress_bar)
        layout.addWidget(QLabel("详细日志："))
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(180)
        layout.addWidget(self.log_text)

        self.setLayout(layout)

    def choose_province(self):
        dlg = ProvinceDialog(self)
        if dlg.exec_() == QDialog.Accepted and dlg.selected:
            self.province_edit.setText(dlg.selected)
            self.plate_province_edit.setText(dlg.selected)

    def random_plate_number_only(self):
        # 只随机号码部分，省份和字母不变，颜色用当前选中
        province = self.plate_province_edit.text()
        letter = self.plate_letter_edit.text()
        color = self.plate_color_combo.currentText()
        plate_info = DataFactory.random_plate_number(province=province, color=color, prefix=letter)
        plate = plate_info['plate_number']
        # 只取号码部分
        self.plate_number_edit.setText(plate[2:])

    def random_name(self):
        self.name_edit.setText(DataFactory.random_name())

    def random_id(self):
        self.id_edit.setText(DataFactory.random_id_number())

    def random_phone(self):
        self.phone_edit.setText(DataFactory.random_phone())

    def random_bank(self):
        self.bank_edit.setText(DataFactory.random_bank_card())

    def get_vin(self):
        try:
            # 如果vin_list为空或已用完，重新获取
            if not self.vin_list or self.vin_index >= len(self.vin_list):
                self.vin_list = get_recent_vins()
                self.vin_index = 0
            # 取下一个VIN
            if self.vin_list:
                vin = self.vin_list[self.vin_index % len(self.vin_list)]
                self.vin_index += 1
                self.vin_edit.setText(vin)
                self.append_log(f"已自动获取VIN: {vin}")
            else:
                self.append_log("未能获取到VIN码，请检查爬虫或数据源")
        except Exception as e:
            self.append_log(f"获取VIN码异常: {e}")

    def on_apply(self):
        # 组合车牌号
        plate_province = self.plate_province_edit.text().strip()
        plate_letter = self.plate_letter_edit.text().strip()
        plate_number = self.plate_number_edit.text().strip()
        plate_color = self.plate_color_combo.currentText()
        params = {
            "carNum": plate_province + plate_letter + plate_number,
            "province": self.province_edit.text().strip(),
            "vin": self.vin_edit.text().strip(),
            # 实名四要素
            "cardHolder": self.name_edit.text().strip(),
            "idCode": self.id_edit.text().strip(),
            "bindBankNo": self.bank_edit.text().strip(),
            "bindBankPhone": self.phone_edit.text().strip(),
            # 兼容老参数
            "name": self.name_edit.text().strip(),
            "phone": self.phone_edit.text().strip(),
            "plate_province": plate_province,
            "plate_letter": plate_letter,
            "plate_number": plate_number,
            "vehicleColor": str(["蓝色", "黄色", "绿色", "白色", "黑色"].index(plate_color)),
        }
        # 检查缺失字段
        missing = []
        field_map = {
            "province": "省份",
            "plate_province": "车牌省份",
            "plate_letter": "车牌字母",
            "plate_number": "车牌号码",
            "vin": "VIN码",
            "cardHolder": "姓名",
            "idCode": "身份证",
            "bindBankPhone": "手机号",
            "bindBankNo": "银行卡号"
        }
        for k, v in params.items():
            if k in field_map and not v:
                missing.append(field_map.get(k, k))
        if missing:
            QMessageBox.warning(self, "提示", f"请先填写：{', '.join(missing)}")
            return
        self.append_log("开始申办ETC流程...")
        self.progress_label.setText("进度：正在申办...")
        self.worker_params = params
        self.worker_order_id = None
        self.worker_sign_order_id = None
        self.worker_verify_code_no = None
        self.worker = None
        def progress_callback(percent, msg):
            self.progress_signal.emit(f"进度：{msg}")
            self.log_signal.emit(msg)
            self.update_progress(percent, msg)
        def run_to_step6():
            worker = EtcApplyWorker(params=self.worker_params, progress_callback=progress_callback, base_url="http://788360p9o5.yicp.fun")
            res = worker.run_until_step6()
            self.worker = worker
            self.worker_order_id = res['order_id']
            self.worker_sign_order_id = res['sign_order_id']
            self.worker_verify_code_no = res['verify_code_no']
            return None
        # 清理已结束线程
        self.worker_thread_list = [t for t in self.worker_thread_list if t.isRunning()]
        self.worker_thread = WorkerQThread(run_to_step6)
        self.worker_thread_list.append(self.worker_thread)
        self.worker_thread.log_signal.connect(self.log_signal.emit)
        self.worker_thread.progress_signal.connect(self.progress_signal.emit)
        self.worker_thread.finished_signal.connect(lambda _: self.show_verify_dialog())
        self.worker_thread.start()

    def show_verify_dialog(self):
        def on_get_code(dialog):
            self.log_signal.emit("正在获取验证码...")
            def progress_callback(percent, msg):
                try:
                    self.progress_signal.emit(f"进度：{msg}")
                    self.log_signal.emit(msg)
                    self.update_progress(percent, msg)
                except Exception as e:
                    print(f"progress_callback异常: {e}")
            def run_step7():
                try:
                    res = self.worker.run_step7_get_code(self.worker_order_id, self.worker_sign_order_id)
                    self.worker_sign_order_id = res['sign_order_id']
                    self.worker_verify_code_no = res['verify_code_no']
                    return True  # 成功
                except Exception as e:
                    # 失败时不倒计时
                    return False
            # 清理已结束线程
            self.worker_thread_list = [t for t in self.worker_thread_list if t.isRunning()]
            self.worker_thread = WorkerQThread(run_step7)
            self.worker_thread_list.append(self.worker_thread)
            self.worker_thread.log_signal.connect(self.log_signal.emit)
            self.worker_thread.progress_signal.connect(self.progress_signal.emit)
            def on_finished(success):
                try:
                    if success:
                        dialog.start_timer()
                        self.log_signal.emit("验证码已发送，请查收短信")
                    else:
                        self.log_signal.emit("获取验证码失败，请重试")
                        dialog.get_code_btn.setEnabled(True)
                        dialog.get_code_btn.setText("获取验证码")
                except Exception as e:
                    print(f"on_finished异常: {e}")
            self.worker_thread.finished_signal.connect(on_finished)
            self.worker_thread.start()
        def on_confirm(code):
            self.log_signal.emit(f"输入验证码：{code}，开始签约校验及后续流程...")
            def progress_callback(percent, msg):
                self.progress_signal.emit(f"进度：{msg}")
                self.log_signal.emit(msg)
                self.update_progress(percent, msg)
            def run_8_to_end():
                self.worker.run_step8_to_end(code, self.worker_order_id, self.worker_sign_order_id, self.worker_verify_code_no)
                return None
            # 清理已结束线程
            self.worker_thread_list = [t for t in self.worker_thread_list if t.isRunning()]
            self.worker_thread = WorkerQThread(run_8_to_end)
            self.worker_thread_list.append(self.worker_thread)
            self.worker_thread.log_signal.connect(self.log_signal.emit)
            self.worker_thread.progress_signal.connect(self.progress_signal.emit)
            self.worker_thread.finished_signal.connect(lambda _: self.log_signal.emit("申办流程全部完成！"))
            self.worker_thread.start()
        self.verify_dialog = VerifyCodeDialog(self, on_get_code=on_get_code, on_confirm=on_confirm)
        self.verify_dialog.exec_()

    def append_log(self, msg):
        try:
            if threading.current_thread() is threading.main_thread():
                self.log_text.append(msg)
                self.log_text.moveCursor(self.log_text.textCursor().End)
            else:
                QMetaObject.invokeMethod(self.log_text, "append", Qt.QueuedConnection, Q_ARG(str, msg))
                QMetaObject.invokeMethod(self.log_text, "moveCursor", Qt.QueuedConnection, Q_ARG(int, self.log_text.textCursor().End))
        except Exception as e:
            print(f"append_log异常: {e}")

    def update_progress(self, percent, msg):
        try:
            if threading.current_thread() is threading.main_thread():
                self.progress_bar.setValue(percent)
                self.progress_label.setText(f"进度：{msg}")
            else:
                QMetaObject.invokeMethod(self.progress_bar, "setValue", Qt.QueuedConnection, Q_ARG(int, percent))
                QMetaObject.invokeMethod(self.progress_label, "setText", Qt.QueuedConnection, Q_ARG(str, f"进度：{msg}"))
        except Exception as e:
            print(f"update_progress异常: {e}")

    def change_product(self):
        dlg = ProductSelectDialog(self)
        # 只传递已有产品列表，避免重复查库
        dlg.products = self.products
        dlg.combo.clear()
        for row in self.products:
            dlg.combo.addItem(f"{row['product_name']}（{row['operator_code']}）", row)
        dlg.selected_product = self.products[0]
        if dlg.exec_() == QDialog.Accepted and dlg.selected_product:
            self.product_id = dlg.selected_product['product_id']
            self.operator_code = dlg.selected_product['operator_code']
            self.product_name = dlg.selected_product['product_name']
            self.product_label.setText(f"产品：{self.product_name}（{self.operator_code}）")
        else:
            QMessageBox.warning(self, "提示", "未更换产品，仍使用当前产品")

# 全局异常钩子
def excepthook(type, value, traceback):
    print("全局异常:", value)
    QMessageBox.critical(None, "程序异常", f"{value}")
sys.excepthook = excepthook

# 测试用
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    w = EtcApplyWidget()
    w.show()
    sys.exit(app.exec_()) 