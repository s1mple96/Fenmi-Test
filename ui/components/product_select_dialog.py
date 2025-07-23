from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QLabel, QHBoxLayout, QPushButton, QMessageBox
from utils.path_util import resource_path
from utils.mysql_util import MySQLUtil
import json, os

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
        config_path = resource_path(os.path.join('config', 'connections.json'))
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