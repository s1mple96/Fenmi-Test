# -*- coding: utf-8 -*-
"""
UI组件模块 - 包含各种可复用的UI组件
"""
import os
import json
from PyQt5.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QLineEdit, QComboBox, QGroupBox, QGridLayout,
    QMessageBox
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QDragEnterEvent, QDropEvent
from common.mysql_util import MySQLUtil
from common.path_util import resource_path


# ==================== 验证码对话框 ====================

class VerifyCodeDialog(QDialog):
    """验证码输入对话框"""
    def __init__(self, parent=None, on_get_code=None, on_confirm=None):
        from apps.etc_apply.services.rtx.core_service import CoreService
        super().__init__(parent)
        self.setWindowTitle("验证码")
        self.setFixedSize(300, 200)
        self.on_get_code = on_get_code
        self.on_confirm = on_confirm
        
        # 从配置文件获取倒计时时间
        from apps.etc_apply.services.rtx.core_service import CoreService
        ui_config = CoreService.get_ui_config()
        self.countdown = ui_config.get('verify_code_timer_duration', 60)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        
        # 验证码输入框
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("验证码："))
        self.code_edit = QLineEdit()
        self.code_edit.setPlaceholderText("请输入验证码")
        input_layout.addWidget(self.code_edit)
        layout.addLayout(input_layout)
        
        # 按钮布局 - 两个按钮在同一行
        btn_layout = QHBoxLayout()
        
        # 获取验证码按钮
        self.get_code_btn = QPushButton("获取验证码")
        self.get_code_btn.clicked.connect(self.get_code)
        self.get_code_btn.setMinimumWidth(100)  # 设置最小宽度
        btn_layout.addWidget(self.get_code_btn)
        
        # 确认按钮
        self.confirm_btn = QPushButton("确认")
        self.confirm_btn.clicked.connect(self.confirm)
        self.confirm_btn.setMinimumWidth(80)  # 设置最小宽度
        btn_layout.addWidget(self.confirm_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)

    def get_code(self):
        if self.on_get_code:
            self.on_get_code()
        self.start_timer()

    def start_timer(self):
        # 从配置文件获取倒计时时间
        from apps.etc_apply.services.rtx.core_service import CoreService
        ui_config = CoreService.get_ui_config()
        self.countdown = ui_config.get('verify_code_timer_duration', 60)
        self.get_code_btn.setEnabled(False)
        self.timer.start(1000)

    def update_timer(self):
        self.countdown -= 1
        self.get_code_btn.setText(f"重新获取({self.countdown}s)")
        if self.countdown <= 0:
            self.timer.stop()
            self.get_code_btn.setEnabled(True)
            self.get_code_btn.setText("获取验证码")

    def confirm(self):
        if self.on_confirm:
            self.on_confirm(self.code_edit.text())
        self.accept()


# ==================== 支持拖拽的QGroupBox组件 ====================

class DraggableGroupBox(QGroupBox):
    """支持拖拽的QGroupBox组件"""
    file_dropped = pyqtSignal(str)
    
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        print(f"创建拖拽组件: {title}")
        self.setAcceptDrops(True)
        self.init_style()
        self.original_title = title  # 保存原始标题
        self.installEventFilter(self)
        print(f"拖拽组件初始化完成，标题: {self.title()}")
        # 递归禁用所有子控件的拖拽
        self._disable_child_drops(self)

    def _disable_child_drops(self, widget):
        from PyQt5.QtWidgets import QWidget
        for child in widget.findChildren(QWidget):
            child.setAcceptDrops(False)
            self._disable_child_drops(child)

    def init_style(self):
        from apps.etc_apply.ui.rtx.ui_styles import ui_styles
        self.setStyleSheet(ui_styles.get_draggable_group_normal_style())
        print("拖拽组件样式设置完成")

    def dragEnterEvent(self, event: QDragEnterEvent):
        print(f"拖拽进入事件被触发，组件标题: {self.title()}")
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            from apps.etc_apply.ui.rtx.ui_styles import ui_styles
            self.setStyleSheet(ui_styles.get_draggable_group_drag_enter_style())
            print("拖拽文件被接受")
        else:
            event.ignore()
            print("拖拽内容被拒绝")

    def dragLeaveEvent(self, event):
        print(f"拖拽离开事件被触发，组件标题: {self.title()}")
        self.init_style()

    def dropEvent(self, event: QDropEvent):
        print(f"文件拖拽事件被触发，组件标题: {self.title()}")
        self.init_style()
        
        # 获取MIME数据
        mime_data = event.mimeData()
        print(f"MIME数据类型: {mime_data.formats()}")
        
        # 检查是否有URL
        if mime_data.hasUrls():
            urls = mime_data.urls()
            print(f"获取到URL数量: {len(urls)}")
            
            if urls:
                file_url = urls[0]
                print(f"第一个URL: {file_url.toString()}")
                
                # 尝试获取本地文件路径
                file_path = file_url.toLocalFile()
                print(f"本地文件路径: {file_path}")
                
                if file_path:
                    if os.path.isfile(file_path):
                        print(f"文件存在，发送信号: {file_path}")
                        # 确保标题不被修改
                        self.setTitle(self.original_title)
                        self.file_dropped.emit(file_path)
                    else:
                        print(f"文件不存在: {file_path}")
                        QMessageBox.warning(self, "警告", f"文件不存在: {file_path}")
                else:
                    print("无法获取本地文件路径")
                    QMessageBox.warning(self, "警告", "无法获取文件路径，请确保拖拽的是本地文件")
            else:
                print("URL列表为空")
                QMessageBox.warning(self, "警告", "没有获取到文件URL")
        else:
            print("MIME数据中没有URL")
            print(f"可用的MIME格式: {mime_data.formats()}")
            QMessageBox.warning(self, "警告", "请拖拽文件而不是文件夹或其他内容")

    def eventFilter(self, obj, event):
        # 移除弹窗功能，不再需要
        return super().eventFilter(obj, event)

# ==================== 车牌字母选择对话框 ====================

LETTERS = [chr(i) for i in range(ord('A'), ord('Z')+1)]

class PlateLetterDialog(QDialog):
    """车牌字母选择对话框（A~Z，点击即选中，无确定/取消按钮）"""
    def __init__(self, parent=None, selected_letter=None):
        super().__init__(parent)
        self.setWindowTitle("选择车牌字母")
        self.setFixedSize(420, 260)
        # 如果没有指定selected_letter，默认选择Z
        if selected_letter is None:
            selected_letter = 'Z'
        self.selected_letter = selected_letter if selected_letter in LETTERS else 'Z'
        self.letter_buttons = {}
        self.init_ui()
        # 设置回车键默认选择Z
        self.setup_enter_key()
        # 设置对话框为焦点，确保能接收键盘事件
        self.setFocus()

    def init_ui(self):
        layout = QVBoxLayout()
        title_label = QLabel("请选择车牌字母")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        layout.addWidget(title_label)

        grid_widget = QGridLayout()
        max_cols = 7
        row, col = 0, 0
        for letter in LETTERS:
            btn = QPushButton(letter)
            btn.setFixedSize(40, 40)
            btn.clicked.connect(lambda checked, l=letter: self.select_and_accept(l))
            self.letter_buttons[letter] = btn
            grid_widget.addWidget(btn, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        layout.addLayout(grid_widget)
        self.setLayout(layout)
        self.highlight_selected(self.selected_letter)

    def select_and_accept(self, letter):
        self.selected_letter = letter
        self.accept()

    def highlight_selected(self, letter):
        """高亮显示选中的字母"""
        for l, btn in self.letter_buttons.items():
            if l == letter:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: 2px solid #45a049;
                        border-radius: 5px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f0f0f0;
                        border: 1px solid #ccc;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: #e0e0e0;
                    }
                """)

    def setup_enter_key(self):
        """设置回车键默认选择Z"""
        self.highlight_selected('Z')

    def keyPressEvent(self, event):
        """处理键盘事件"""
        from PyQt5.QtCore import Qt
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            print("[DEBUG] 按键事件被触发:", event.key())
            print("[DEBUG] 用户按了回车键，默认选择Z")
            self.select_and_accept('Z')
        else:
            super().keyPressEvent(event)

    def get_selected_letter(self):
        return self.selected_letter


# ==================== 省份选择对话框 ====================

PROVINCES = [
    ("京", "北京"), ("津", "天津"), ("沪", "上海"), ("渝", "重庆"),
    ("冀", "河北"), ("豫", "河南"), ("云", "云南"), ("辽", "辽宁"),
    ("黑", "黑龙江"), ("湘", "湖南"), ("皖", "安徽"), ("鲁", "山东"),
    ("新", "新疆"), ("苏", "江苏"), ("浙", "浙江"), ("赣", "江西"),
    ("鄂", "湖北"), ("桂", "广西"), ("甘", "甘肃"), ("晋", "山西"),
    ("蒙", "内蒙古"), ("陕", "陕西"), ("吉", "吉林"), ("闽", "福建"),
    ("贵", "贵州"), ("青", "青海"), ("藏", "西藏"), ("川", "四川"),
    ("宁", "宁夏"), ("琼", "海南"), ("粤", "广东"), ("港", "香港"),
    ("澳", "澳门"), ("台", "台湾")
]

class ProvinceDialog(QDialog):
    """省份选择对话框"""
    def __init__(self, parent=None, selected_province=None):
        super().__init__(parent)
        self.setWindowTitle("选择省份")
        self.setFixedSize(650, 440)
        if selected_province is None:
            selected_province = '苏'
        self.selected_province = selected_province
        self.province_buttons = {}
        self.init_ui()

    def init_ui(self):
        from apps.etc_apply.services.rtx.core_service import CoreService
        layout = QVBoxLayout()
        title_label = QLabel("请选择省份")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        layout.addWidget(title_label)

        # 获取热门省份配置
        from apps.etc_apply.services.rtx.core_service import CoreService
        ui_config = CoreService.get_ui_config()
        hot_provinces = ui_config.get('hot_provinces', ['苏', '桂', '黑', '蒙', '湘', '川'])
        
        # 创建热门省份区域
        hot_group = QGroupBox("热门省份")
        hot_layout = QHBoxLayout()
        for abbr, name in PROVINCES:
            if abbr in hot_provinces:
                btn = QPushButton(f"{abbr}\n{name}")
                btn.setFixedSize(80, 50)
                btn.clicked.connect(lambda checked, a=abbr: self.select_and_accept(a))
                self.province_buttons[abbr] = btn
                hot_layout.addWidget(btn)
        hot_group.setLayout(hot_layout)
        layout.addWidget(hot_group)

        # 创建所有省份区域
        all_group = QGroupBox("所有省份")
        all_layout = QGridLayout()
        max_cols = 8
        row, col = 0, 0
        for abbr, name in PROVINCES:
            btn = QPushButton(f"{abbr}\n{name}")
            btn.setFixedSize(70, 45)
            btn.clicked.connect(lambda checked, a=abbr: self.select_and_accept(a))
            self.province_buttons[abbr] = btn
            all_layout.addWidget(btn, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1

        all_group.setLayout(all_layout)
        layout.addWidget(all_group)
        
        self.setLayout(layout)
        self.update_province_buttons()

    def update_province_buttons(self):
        # 清空原有按钮
        for abbr, btn in self.province_buttons.items():
            if abbr == self.selected_province:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border: 2px solid #45a049;
                        border-radius: 5px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: #f0f0f0;
                        border: 1px solid #ccc;
                        border-radius: 5px;
                    }
                    QPushButton:hover {
                        background-color: #e0e0e0;
                    }
                """)

    def select_and_accept(self, abbr):
        self.selected_province = abbr
        self.accept()

    def highlight_selected(self, abbr):
        self.selected_province = abbr
        self.update_province_buttons()

    def accept(self):
        super().accept()

    def get_selected_province(self):
        return self.selected_province


# ==================== 客车产品选择对话框 ====================

class ProductSelectDialog(QDialog):
    """产品选择对话框"""
    # 类变量，用于记住用户的选择
    _last_operator = None
    _last_product = None
    
    def __init__(self, parent=None):
        from apps.etc_apply.services.rtx.core_service import CoreService
        super().__init__(parent)
        self.setWindowTitle("选择产品")
        self.setFixedSize(400, 250)  # 增加高度以容纳提示语
        layout = QVBoxLayout()
        
        # 添加测试专用渠道提示标签
        business_config = CoreService.get_business_config()
        default_verify_code = business_config.get('default_verify_code', '13797173255')
        warning_text = f'⚠️ 【测试专用渠道手机号】：{default_verify_code} 请勿擅自修改系统数据！'
        
        warning_label = QLabel(warning_text)
        from apps.etc_apply.ui.rtx.ui_styles import ui_styles
        warning_label.setStyleSheet(ui_styles.get_warning_label_style())
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
        # 使用CoreService统一读取配置
        from apps.etc_apply.services.rtx.core_service import CoreService
        return CoreService.get_rtx_mysql_config()

    def update_mock_config(self, enable=True):
        """更新Mock数据配置"""
        from apps.etc_apply.services.rtx.core_service import CoreService
        try:
            mysql_conf = self.get_mysql_config()
            if not mysql_conf:
                return False
            
            business_config = CoreService.get_business_config()
            mock_config_id = business_config.get('mock_config_id', 55)
            
            db = MySQLUtil(**mysql_conf)
            db.connect()
            value = '1' if enable else '0'
            sql = f"UPDATE rtx.sys_config t SET t.config_value = %s WHERE t.config_id = {mock_config_id}"
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
            
            # 获取所有运营商
            operators = list(set(row['operator_code'] for row in rows))
            operators.sort()
            print(f"可用运营商: {operators}")
            
            # 设置运营商下拉框
            self.operator_combo.clear()
            self.operator_combo.addItems(operators)
            
            # 设置默认运营商
            if self._last_operator and self._last_operator in operators:
                index = operators.index(self._last_operator)
                self.operator_combo.setCurrentIndex(index)
                print(f"设置运营商为{self._last_operator}，索引: {index}")
            else:
                # 默认选择TXB
                if 'TXB' in operators:
                    index = operators.index('TXB')
                    self.operator_combo.setCurrentIndex(index)
                    print(f"设置运营商为TXB，索引: {index}")
            
            # 加载当前运营商的产品
            current_operator = self.operator_combo.currentText()
            self._load_products_for_operator(current_operator)
            
        except Exception as e:
            QMessageBox.critical(self, "数据库错误", f"加载产品失败: {str(e)}")

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
        from apps.etc_apply.services.rtx.core_service import CoreService
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


# ==================== 货车产品选择对话框 ====================

class TruckProductSelectDialog(QDialog):
    """货车产品选择对话框"""
    # 类变量，用于记住用户的选择
    _last_operator = None
    _last_product = None
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择货车产品")
        self.setFixedSize(400, 250)
        layout = QVBoxLayout()
        
        # 添加测试专用渠道提示标签
        from apps.etc_apply.services.rtx.core_service import CoreService
        business_config = CoreService.get_business_config()
        default_verify_code = business_config.get('default_verify_code', '13797173255')
        warning_text = f'⚠️ 【测试专用渠道手机号】：{default_verify_code} 请勿擅自修改系统数据！'
        
        warning_label = QLabel(warning_text)
        from apps.etc_apply.ui.rtx.ui_styles import ui_styles
        warning_label.setStyleSheet(ui_styles.get_warning_label_style())
        warning_label.setAlignment(Qt.AlignCenter)
        warning_label.setWordWrap(True)
        layout.addWidget(warning_label)
        
        # 运营商下拉框
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
        self.mock_enabled = False
        self.load_products()
        self.operator_combo.currentIndexChanged.connect(self.on_operator_changed)
        self.combo.currentIndexChanged.connect(self.on_select)

    def get_mysql_config(self):
        """获取MySQL连接配置"""
        from apps.etc_apply.services.rtx.core_service import CoreService
        return CoreService.get_hcb_mysql_config()

    def update_mock_config(self, enable=True):
        """更新Mock数据配置（货车版本）- 使用货车系统的hcb.sys_dictionaries表"""
        try:
            # 使用正确的货车数据服务
            from apps.etc_apply.services.hcb.truck_data_service import TruckDataService
            
            if enable:
                result = TruckDataService.enable_mock_data()
                if result:
                    print("货车Mock数据已启用（使用hcb.sys_dictionaries表）")
                    return True
                else:
                    print("启用货车Mock数据失败")
                    return False
            else:
                result = TruckDataService.close_mock_data()
                if result:
                    print("货车Mock数据已关闭（使用hcb.sys_dictionaries表）")
                    return True
                else:
                    print("关闭货车Mock数据失败")
                    return False
                    
        except Exception as e:
            QMessageBox.critical(self, "错误", f"更新Mock配置失败: {str(e)}")
            return False

    def enable_mock_data(self):
        """启用Mock数据配置（便捷方法）"""
        try:
            from apps.etc_apply.services.hcb.truck_data_service import TruckDataService
            result = TruckDataService.enable_mock_data()
            if result:
                self.mock_enabled = True
                print("✅ 货车Mock数据已启用")
                return True
            else:
                print("❌ 启用货车Mock数据失败")
                return False
        except Exception as e:
            print(f"❌ 启用货车Mock数据异常: {str(e)}")
            return False

    def close_mock_data(self):
        """关闭Mock数据配置（便捷方法）"""
        try:
            from apps.etc_apply.services.hcb.truck_data_service import TruckDataService
            result = TruckDataService.close_mock_data()
            if result:
                self.mock_enabled = False
                print("✅ 货车Mock数据已关闭")
                return True
            else:
                print("❌ 关闭货车Mock数据失败")
                return False
        except Exception as e:
            print(f"❌ 关闭货车Mock数据异常: {str(e)}")
            return False

    def load_products(self):
        """加载运营商列表（通过API）"""
        try:
            # 调用API获取运营商列表
            from apps.etc_apply.services.hcb.truck_api_client import TruckApiClient
            from apps.etc_apply.services.rtx.core_service import CoreService
            
            api_client = TruckApiClient()
            params = CoreService.generate_hcb_params("com.hcb.channel.getOperatorList")
            
            print("调用货车运营商列表API...")
            response = api_client.get_operator_list(params)
            
            if not response or 'rows' not in response:
                QMessageBox.warning(self, "提示", "获取运营商列表失败！")
                return
            
            operators_data = response['rows']
            if not operators_data:
                QMessageBox.warning(self, "提示", "未查到可用运营商！")
                return
            
            # 打印调试信息
            print(f"查询到 {len(operators_data)} 个运营商:")
            for operator in operators_data:
                print(f"  {operator.get('name', 'Unknown')} (ID: {operator.get('id', 'Unknown')})")
            
            self.operators = operators_data
            
            # 设置运营商下拉框
            self.operator_combo.clear()
            for operator in operators_data:
                operator_name = operator.get('name', 'Unknown')
                operator_id = operator.get('id', 'Unknown')
                # 只显示运营商名称，不显示ID
                display_text = operator_name
                self.operator_combo.addItem(display_text, operator)
                print(f"  添加运营商: {display_text}")
            
            # 设置默认运营商
            if self._last_operator:
                for i, operator in enumerate(operators_data):
                    if operator.get('id') == self._last_operator:
                        self.operator_combo.setCurrentIndex(i)
                        print(f"设置货车运营商为{self._last_operator}，索引: {i}")
                        break
                else:
                    # 如果找不到上次选择的运营商，选择第一个
                    if operators_data:
                        self.operator_combo.setCurrentIndex(0)
                        print(f"设置货车运营商为{operators_data[0].get('id')}，索引: 0")
            else:
                # 默认选择第一个
                if operators_data:
                    self.operator_combo.setCurrentIndex(0)
                    print(f"设置货车运营商为{operators_data[0].get('id')}，索引: 0")
            
            # 加载当前运营商的产品
            current_operator = self.operator_combo.currentData()
            if current_operator:
                self._load_products_for_operator(current_operator)
            
        except Exception as e:
            QMessageBox.critical(self, "API错误", f"加载货车运营商失败: {str(e)}")

    def on_operator_changed(self):
        current_operator = self.operator_combo.currentData()
        if not current_operator:
            return
            
        operator_id = current_operator.get('id')
        operator_name = current_operator.get('name')
        print(f"货车运营商切换为: {operator_name} (ID: {operator_id})")
        
        # 检查是否需要Mock数据（货车版本：根据运营商名称判断）
        mock_required_operators = ['蒙通卡', '龙通卡', '湘通卡']  # 货车需要mock的运营商，对应客车的MTK、LTK、XTK
        if operator_name in mock_required_operators:
            # 记录前一个选择
            if self.previous_operator and self.previous_operator.get('name') not in mock_required_operators:
                # 保持前一个选择
                pass
            else:
                # 如果没有前一个选择或前一个也是需要Mock的，设置默认运营商
                for i in range(self.operator_combo.count()):
                    item_data = self.operator_combo.itemData(i)
                    if item_data and item_data.get('name') not in mock_required_operators:
                        self.previous_operator = item_data
                        break
            
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
                    QMessageBox.information(self, "提示", "货车Mock数据已开启")
                else:
                    # 如果开启失败，恢复到之前的选项
                    if self.previous_operator:
                        for i in range(self.operator_combo.count()):
                            item_data = self.operator_combo.itemData(i)
                            if item_data and item_data.get('id') == self.previous_operator.get('id'):
                                self.operator_combo.setCurrentIndex(i)
                                break
                    return
            else:
                # 用户选择取消，恢复到之前的选项
                if self.previous_operator:
                    for i in range(self.operator_combo.count()):
                        item_data = self.operator_combo.itemData(i)
                        if item_data and item_data.get('id') == self.previous_operator.get('id'):
                            self.operator_combo.setCurrentIndex(i)
                            break
                return
        
        # 根据运营商ID查询产品
        self._load_products_for_operator(current_operator)

    def _load_products_for_operator(self, operator):
        """根据运营商ID查询货车产品"""
        from apps.etc_apply.services.rtx.core_service import CoreService
        operator_id = operator.get('id')
        operator_name = operator.get('name')
        print(f"根据运营商ID查询货车产品: {operator_name} (ID: {operator_id})")
        
        try:
            mysql_conf = self.get_mysql_config()
            if not mysql_conf:
                QMessageBox.critical(self, "错误", "未找到MySQL连接配置！")
                return
            
            db = MySQLUtil(**mysql_conf)
            db.connect()
            
            # 使用您提供的SQL查询货车产品，但根据运营商ID过滤
            sql = """
            select
                NAME,
                BANK_TYPE,
                YEAR_RATE,
                DAY_RATE,
                ACCOUNT_PERIOD,
                STATUS,
                CREATE_TIME,
                CREATE_BY,
                PIC_URL,
                BANK_CODE,
                DISCRIBE_PIC_URL,
                ETCBANK_ID
            from HCB_ETCBANK
            where STATUS = '1' and ETCBANK_ID in(
                select a.LOAN_BANKID from hcb_product a
                    left join hcb_channelproductgroupconfig b on a.PRODUCT_GROUP_CODE = b.product_group_code and b.source='1' and b.channel_id='0000'
                where a.STATUS = '1'
                    and b.extend_authority='1' and b.extend_open ='1' and b.business_type='0'
                    and a.IS_SELF_SERVICE_PRODUCT='0'
                    and a.PRODUCT_ID in(select PRODUCT_ID from hcb_channelcompanyprofit where CHANNELCOMPANY_ID= 'd4949f0bc4c04a53987ac747287f3943' and status='1')
                    and a.OPERATOR_ID = %s
                    and a.USER_TYPE = '0'
            )
            """
            rows = db.query(sql, (operator_id,))
            db.close()
            
            if not rows:
                print(f"未找到运营商 {operator_name} (ID: {operator_id}) 的货车产品")
                self.combo.clear()
                self.selected_product = None
                return
            
            # 打印调试信息
            print(f"查询到 {len(rows)} 个 {operator_name} 运营商的货车产品:")
            for row in rows:
                print(f"  {row['NAME']} (BANK_CODE: {row['BANK_CODE']})")
            
            self.filtered_products = rows
            
            # 设置产品下拉框
            self.combo.clear()
            for row in rows:
                # 只显示产品名称和运营商编码，不显示产品ID
                item_text = f"{row['NAME']}（{row['BANK_CODE']}）"
                self.combo.addItem(item_text, row)
                print(f"  添加货车产品: {item_text}")
            
            if self.filtered_products:
                self.selected_product = self.filtered_products[0]
                print(f"默认选择第一个货车产品: {self.selected_product['NAME']}")
                
                # 优先使用上次选择的产品
                if self._last_product and operator_id == self._last_operator:
                    for i, row in enumerate(self.filtered_products):
                        if row['NAME'] == self._last_product:
                            self.combo.setCurrentIndex(i)
                            self.selected_product = row
                            print(f"找到上次选择的货车产品，设置为索引 {i}: {row['NAME']}")
                            break
                    else:
                        print("未找到上次选择的货车产品，使用第一个产品")
                else:
                    print("使用第一个货车产品作为默认选择")
            else:
                self.selected_product = None
                print("没有找到任何货车产品")
            
            # 记录当前选择
            self.previous_operator = operator
            
        except Exception as e:
            QMessageBox.critical(self, "数据库错误", f"查询货车产品失败: {str(e)}")
            self.combo.clear()
            self.selected_product = None

    def on_select(self, idx):
        """产品选择变化时的处理"""
        if 0 <= idx < len(self.filtered_products):
            self.selected_product = self.filtered_products[idx]

    def on_ok_clicked(self):
        """确定按钮点击事件，保存用户选择并接受对话框"""
        # 保存用户的选择
        if self.selected_product:
            current_operator = self.operator_combo.currentData()
            operator_id = current_operator.get('id') if current_operator else None
            TruckProductSelectDialog._last_operator = operator_id
            TruckProductSelectDialog._last_product = self.selected_product['NAME']
            print(f"保存货车用户选择: 运营商ID={operator_id}, 产品={self.selected_product['NAME']}, 产品ID={self.selected_product.get('ETCBANK_ID')}")
        self.accept()

    def reject(self):
        """用户取消对话框"""
        super().reject()

    def closeEvent(self, event):
        """关闭窗口事件"""
        event.accept() 