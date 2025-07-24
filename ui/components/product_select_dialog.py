from PyQt5.QtWidgets import QDialog, QVBoxLayout, QComboBox, QLabel, QHBoxLayout, QPushButton, QMessageBox
from PyQt5.QtCore import Qt
from utils.path_util import resource_path
from utils.mysql_util import MySQLUtil
import json, os

class ProductSelectDialog(QDialog):
    # 类变量，用于记住用户的选择
    _last_operator = None
    _last_product = None
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择产品")
        self.setFixedSize(400, 250)  # 增加高度以容纳提示语
        layout = QVBoxLayout()
        
        # 添加测试专用渠道提示标签
        warning_label = QLabel('⚠️ 【测试专用渠道手机号】：13797173255 请勿擅自修改系统数据！')
        warning_label.setStyleSheet('QLabel { color: red; font-weight: bold; font-size: 14px; padding: 8px; background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 3px; }')
        warning_label.setAlignment(Qt.AlignCenter)
        warning_label.setWordWrap(True)  # 允许文字换行
        layout.addWidget(warning_label)
        
        # 新增运营商下拉框
        self.operator_combo = QComboBox()
        layout.addWidget(QLabel("请选择运营商："))
        layout.addWidget(self.operator_combo)
        # 产品下拉框
        self.combo = QComboBox()
        layout.addWidget(QLabel("请选择产品："))
        layout.addWidget(self.combo)
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.on_ok_clicked)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        self.products = []
        self.filtered_products = []
        self.selected_product = None
        self.previous_operator = None  # 记录前一个选择的运营商
        self.mock_enabled = False  # 记录是否开启了Mock数据
        self.load_products()
        self.operator_combo.currentIndexChanged.connect(self.on_operator_changed)
        self.combo.currentIndexChanged.connect(self.on_select)

    def get_mysql_config(self):
        """获取MySQL连接配置"""
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
        return mysql_conf

    def update_mock_config(self, enable=True):
        """更新Mock数据配置"""
        try:
            mysql_conf = self.get_mysql_config()
            if not mysql_conf:
                return False
            
            db = MySQLUtil(**mysql_conf)
            db.connect()
            value = '1' if enable else '0'
            sql = "UPDATE rtx.sys_config t SET t.config_value = %s WHERE t.config_id = 55"
            db.execute(sql, (value,))
            db.close()
            return True
        except Exception as e:
            QMessageBox.critical(self, "数据库错误", f"更新Mock配置失败: {str(e)}")
            return False

    def load_products(self):
        mysql_conf = self.get_mysql_config()
        if not mysql_conf:
            QMessageBox.critical(self, "错误", "未找到MySQL连接配置！")
            return
        try:
            db = MySQLUtil(**mysql_conf)
            db.connect()
            
            # 查询所有可用的产品和运营商
            sql = ("select product_id,product_name,operator_code,status "
                   "from rtx_product "
                   "where PRODUCT_ID in "
                   "(select PRODUCT_ID from rtx_channel_company_profit "
                   "where channelcompany_id = 'd4949f0bc4c04a53987ac747287f3943') "
                   "and status = 1")  # 只查询状态为1的产品
            rows = db.query(sql)
            db.close()
            
            if not rows:
                QMessageBox.warning(self, "提示", "未查到可选产品，请检查数据库配置和权限！")
                return
            
            # 打印调试信息
            print(f"查询到 {len(rows)} 个产品:")
            for row in rows:
                print(f"  {row['product_name']} ({row['operator_code']})")
            
            self.products = rows
            # 提取所有运营商编码
            operator_codes = sorted(set(row['operator_code'] for row in rows))
            print(f"可用运营商: {operator_codes}")
            
            self.operator_combo.clear()
            self.operator_combo.addItems(operator_codes)
            
            # 设置运营商选择（优先使用上次选择，否则使用默认值）
            target_operator = self._last_operator if self._last_operator else 'TXB'
            operator_index = self.operator_combo.findText(target_operator)
            
            if operator_index >= 0:
                self.operator_combo.setCurrentIndex(operator_index)
                print(f"设置运营商为{target_operator}，索引: {operator_index}")
                # 直接加载产品，不触发运营商切换事件（避免弹出Mock确认对话框）
                self._load_products_for_operator(target_operator)
            else:
                # 如果找不到上次选择的运营商，使用TXB
                txb_index = self.operator_combo.findText('TXB')
                if txb_index >= 0:
                    self.operator_combo.setCurrentIndex(txb_index)
                    print(f"未找到上次选择的运营商，设置默认运营商为TXB，索引: {txb_index}")
                    self._load_products_for_operator('TXB')
                else:
                    # 如果找不到TXB，选择第一个
                    print("未找到TXB运营商，选择第一个")
                    self._load_products_for_operator(self.operator_combo.currentText())
        except Exception as e:
            QMessageBox.critical(self, "数据库错误", str(e))

    def on_operator_changed(self):
        current_operator = self.operator_combo.currentText()
        print(f"运营商切换为: {current_operator}")
        
        # 检查是否需要Mock数据
        if current_operator in ['LTK', 'MTK', 'XTK']:
            # 记录前一个选择
            if self.previous_operator and self.previous_operator not in ['LTK', 'MTK', 'XTK']:
                self.previous_operator = self.previous_operator
            else:
                # 如果没有前一个选择或前一个也是需要Mock的，设置为TXB
                self.previous_operator = 'TXB'
            
            # 弹出确认对话框
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("确认")
            msg_box.setText("该运营商需要【开通mock数据】请问是否继续？")
            msg_box.setIcon(QMessageBox.Question)
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.No)
            # 设置按钮文本为中文
            msg_box.button(QMessageBox.Yes).setText("继续")
            msg_box.button(QMessageBox.No).setText("取消")
            reply = msg_box.exec_()
            
            if reply == QMessageBox.Yes:
                # 用户选择继续，开启Mock数据
                if self.update_mock_config(True):
                    self.mock_enabled = True
                    QMessageBox.information(self, "提示", "Mock数据已开启")
                else:
                    # 如果开启失败，恢复到之前的选项
                    previous_index = self.operator_combo.findText(self.previous_operator)
                    if previous_index >= 0:
                        self.operator_combo.setCurrentIndex(previous_index)
                    return
            else:
                # 用户选择取消，恢复到之前的选项
                previous_index = self.operator_combo.findText(self.previous_operator)
                if previous_index >= 0:
                    self.operator_combo.setCurrentIndex(previous_index)
                return
        
        # 更新产品列表
        self.filtered_products = [row for row in self.products if row['operator_code'] == current_operator]
        print(f"找到 {len(self.filtered_products)} 个 {current_operator} 运营商的产品")
        
        self.combo.clear()
        for row in self.filtered_products:
            item_text = f"{row['product_name']}（{row['operator_code']}）"
            self.combo.addItem(item_text, row)
            print(f"  添加产品: {item_text}")
        
        if self.filtered_products:
            self.selected_product = self.filtered_products[0]
            print(f"默认选择第一个产品: {self.selected_product['product_name']}")
            
            # 优先使用上次选择的产品，否则使用默认逻辑
            if self._last_product and current_operator == self._last_operator:
                # 查找上次选择的产品
                for i, row in enumerate(self.filtered_products):
                    if row['product_name'] == self._last_product:
                        self.combo.setCurrentIndex(i)
                        self.selected_product = row
                        print(f"找到上次选择的产品，设置为索引 {i}: {row['product_name']}")
                        break
                else:
                    print("未找到上次选择的产品，使用默认逻辑")
                    self._set_default_product(current_operator)
            else:
                # 使用默认逻辑
                self._set_default_product(current_operator)
        else:
            self.selected_product = None
            print("没有找到任何产品")
        
        # 记录当前选择
        self.previous_operator = current_operator

    def _load_products_for_operator(self, operator):
        """直接加载指定运营商的产品，不触发Mock确认对话框"""
        current_operator = operator
        print(f"直接加载运营商产品: {current_operator}")
        
        # 更新产品列表
        self.filtered_products = [row for row in self.products if row['operator_code'] == current_operator]
        print(f"找到 {len(self.filtered_products)} 个 {current_operator} 运营商的产品")
        
        self.combo.clear()
        for row in self.filtered_products:
            item_text = f"{row['product_name']}（{row['operator_code']}）"
            self.combo.addItem(item_text, row)
            print(f"  添加产品: {item_text}")
        
        if self.filtered_products:
            self.selected_product = self.filtered_products[0]
            print(f"默认选择第一个产品: {self.selected_product['product_name']}")
            
            # 优先使用上次选择的产品，否则使用默认逻辑
            if self._last_product and current_operator == self._last_operator:
                # 查找上次选择的产品
                for i, row in enumerate(self.filtered_products):
                    if row['product_name'] == self._last_product:
                        self.combo.setCurrentIndex(i)
                        self.selected_product = row
                        print(f"找到上次选择的产品，设置为索引 {i}: {row['product_name']}")
                        break
                else:
                    print("未找到上次选择的产品，使用默认逻辑")
                    self._set_default_product(current_operator)
            else:
                # 使用默认逻辑
                self._set_default_product(current_operator)
        else:
            self.selected_product = None
            print("没有找到任何产品")
        
        # 记录当前选择
        self.previous_operator = current_operator

    def on_select(self, idx):
        if 0 <= idx < len(self.filtered_products):
            self.selected_product = self.filtered_products[idx]

    def _set_default_product(self, current_operator):
        """设置默认产品选择"""
        if current_operator == 'TXB':
            # 查找包含"江苏会员"的产品
            for i, row in enumerate(self.filtered_products):
                if "江苏会员" in row['product_name']:
                    self.combo.setCurrentIndex(i)
                    self.selected_product = row
                    print(f"找到江苏会员产品，设置为索引 {i}: {row['product_name']}")
                    break
            else:
                print("未找到江苏会员产品，使用第一个产品")
        else:
            print("使用第一个产品作为默认选择")

    def on_ok_clicked(self):
        """确定按钮点击事件，保存用户选择并接受对话框"""
        # 保存用户的选择
        if self.selected_product:
            ProductSelectDialog._last_operator = self.operator_combo.currentText()
            ProductSelectDialog._last_product = self.selected_product['product_name']
            print(f"保存用户选择: 运营商={self._last_operator}, 产品={self._last_product}, 产品ID={self.selected_product.get('product_id')}")
        self.accept()

    def reject(self):
        """用户取消对话框"""
        super().reject()

    def closeEvent(self, event):
        """关闭窗口事件"""
        event.accept() 