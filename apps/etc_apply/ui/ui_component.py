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
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QEvent, QPoint
from PyQt5.QtGui import QFont, QPixmap, QDragEnterEvent, QDropEvent
from common.mysql_util import MySQLUtil
from common.path_util import resource_path
from apps.etc_apply.services.core_service import CoreService


# ==================== 验证码对话框 ====================

class VerifyCodeDialog(QDialog):
    """验证码输入对话框"""
    def __init__(self, parent=None, on_get_code=None, on_confirm=None):
        super().__init__(parent)
        self.setWindowTitle("验证码")
        self.setFixedSize(300, 200)
        self.on_get_code = on_get_code
        self.on_confirm = on_confirm
        
        # 从配置文件获取倒计时时间
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
        from apps.etc_apply.ui.ui_styles import ui_styles
        self.setStyleSheet(ui_styles.get_draggable_group_normal_style())
        print("拖拽组件样式设置完成")

    def dragEnterEvent(self, event: QDragEnterEvent):
        print(f"拖拽进入事件被触发，组件标题: {self.title()}")
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            from apps.etc_apply.ui.ui_styles import ui_styles
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
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            print(f"拖拽的文件路径: {file_path}")
            if os.path.isfile(file_path):
                print("文件存在，发送信号")
                # 确保标题不被修改
                self.setTitle(self.original_title)
                self.file_dropped.emit(file_path)
            else:
                print("文件不存在")
                QMessageBox.warning(self, "警告", "请拖拽有效的文件！")
        else:
            print("没有获取到文件URL")

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
        # 在创建完所有按钮后高亮选中的字母
        self.highlight_selected(self.selected_letter)

    def select_and_accept(self, letter):
        print(f"[DEBUG] 用户点击了字母按钮: {letter}")
        self.selected_letter = letter
        self.highlight_selected(letter)
        self.accept()

    def highlight_selected(self, letter):
        from apps.etc_apply.ui.ui_styles import ui_styles
        print(f"[DEBUG] 高亮字母: {letter}")
        for k, btn in self.letter_buttons.items():
            if k == letter:
                print(f"[DEBUG] 设置按钮 {k} 为选中样式")
                btn.setStyleSheet(ui_styles.get_selected_button_style())
            else:
                print(f"[DEBUG] 设置按钮 {k} 为普通样式")
                btn.setStyleSheet(ui_styles.get_normal_button_style())

    def setup_enter_key(self):
        """设置回车键默认选择Z"""
        pass  # 通过重写keyPressEvent来实现
    
    def keyPressEvent(self, event):
        """处理按键事件"""
        print(f"[DEBUG] 按键事件被触发: {event.key()}")
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # 回车键默认选择Z
            print("[DEBUG] 用户按了回车键，默认选择Z")
            self.selected_letter = 'Z'
            self.accept()
            event.accept()  # 标记事件已处理
        else:
            super().keyPressEvent(event)
    
    def get_selected_letter(self):
        return self.selected_letter

# ==================== 省份选择对话框 ====================

# 全部省份数据：简称、全名、拼音
PROVINCE_DATA = [
    ("京", "北京", "beijing"),
    ("津", "天津", "tianjin"),
    ("沪", "上海", "shanghai"),
    ("渝", "重庆", "chongqing"),
    ("冀", "河北", "hebei"),
    ("豫", "河南", "henan"),
    ("云", "云南", "yunnan"),
    ("辽", "辽宁", "liaoning"),
    ("黑", "黑龙江", "heilongjiang"),
    ("湘", "湖南", "hunan"),
    ("皖", "安徽", "anhui"),
    ("鲁", "山东", "shandong"),
    ("新", "新疆", "xinjiang"),
    ("苏", "江苏", "jiangsu"),
    ("浙", "浙江", "zhejiang"),
    ("赣", "江西", "jiangxi"),
    ("鄂", "湖北", "hubei"),
    ("桂", "广西", "guangxi"),
    ("甘", "甘肃", "gansu"),
    ("晋", "山西", "shanxi"),
    ("蒙", "内蒙古", "neimenggu"),
    ("陕", "陕西", "shanxi"),
    ("吉", "吉林", "jilin"),
    ("闽", "福建", "fujian"),
    ("贵", "贵州", "guizhou"),
    ("青", "青海", "qinghai"),
    ("藏", "西藏", "xizang"),
    ("川", "四川", "sichuan"),
    ("宁", "宁夏", "ningxia"),
    ("琼", "海南", "hainan"),
    ("粤", "广东", "guangdong"),
    ("港", "香港", "xianggang"),
    ("澳", "澳门", "aomen"),
    ("台", "台湾", "taiwan"),
]

class ProvinceDialog(QDialog):
    """省份选择对话框（热门+搜索+高亮已选）"""
    def __init__(self, parent=None, selected_province=None):
        super().__init__(parent)
        self.setWindowTitle("选择省份")
        self.setFixedSize(650, 440)
        self.selected_province = selected_province
        self.province_buttons = {}  # 简称: 按钮
        self.init_ui()
        # 只高亮已选省份，不填充搜索框
        self.highlight_selected(self.selected_province)

    def init_ui(self):
        layout = QVBoxLayout()

        # 标题
        title_label = QLabel("请选择省份")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        layout.addWidget(title_label)

        # 搜索框
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入省份简称/全名/拼音快速查找")
        self.search_edit.textChanged.connect(self.update_province_buttons)
        search_layout.addWidget(QLabel("搜索："))
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)

        # 热门省份
        hot_label = QLabel("热门省份：")
        hot_label.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        layout.addWidget(hot_label)
        self.hot_row = QHBoxLayout()
        layout.addLayout(self.hot_row)

        # 省份按钮区
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout(self.grid_widget)
        layout.addWidget(self.grid_widget)
        self.setLayout(layout)
        self.update_province_buttons()

    def update_province_buttons(self):
        # 清空原有按钮
        for i in reversed(range(self.grid_layout.count())):
            w = self.grid_layout.itemAt(i).widget()
            if w:
                w.setParent(None)
        for i in reversed(range(self.hot_row.count())):
            w = self.hot_row.itemAt(i).widget()
            if w:
                w.setParent(None)
        self.province_buttons = {}

        # 获取热门省份配置
        ui_config = CoreService.get_ui_config()
        hot_provinces = ui_config.get('hot_provinces', ['苏', '桂', '黑', '蒙', '湘', '川'])

        # 搜索过滤
        keyword = self.search_edit.text().strip().lower()
        filtered = []
        for abbr, full, pinyin in PROVINCE_DATA:
            if (not keyword or
                keyword in abbr.lower() or
                keyword in full.lower() or
                keyword in pinyin.lower()):
                filtered.append((abbr, full, pinyin))

        # 热门区
        for abbr in hot_provinces:
            found = [item for item in filtered if item[0] == abbr]
            if found:
                abbr, full, pinyin = found[0]
                btn = QPushButton(f"{abbr}（{full}）")
                btn.setFixedSize(90, 35)
                btn.clicked.connect(lambda checked, p=abbr: self.select_and_accept(p))
                self.province_buttons[abbr] = btn
                self.hot_row.addWidget(btn)

        # 其余省份区
        max_cols = 7
        row, col = 0, 0
        for abbr, full, pinyin in filtered:
            if abbr in hot_provinces:
                continue
            btn = QPushButton(f"{abbr}（{full}）")
            btn.setFixedSize(90, 35)
            btn.clicked.connect(lambda checked, p=abbr: self.select_and_accept(p))
            self.province_buttons[abbr] = btn
            self.grid_layout.addWidget(btn, row, col)
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
        # 高亮已选
        self.highlight_selected(self.selected_province)

    def select_and_accept(self, abbr):
        self.selected_province = abbr
        self.highlight_selected(abbr)
        self.accept()

    def highlight_selected(self, abbr):
        for k, btn in self.province_buttons.items():
            if k == abbr:
                btn.setStyleSheet("background-color: #409EFF; color: white; font-weight: bold; border:2px solid #0057b7;")
            else:
                btn.setStyleSheet("")

    def accept(self):
        if not self.selected_province:
            QMessageBox.warning(self, "警告", "请先选择一个省份！")
            return
        super().accept()

    def get_selected_province(self):
        return self.selected_province

# ==================== 产品选择对话框 ====================

class ProductSelectDialog(QDialog):
    """产品选择对话框"""
    # 类变量，用于记住用户的选择
    _last_operator = None
    _last_product = None
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("选择产品")
        self.setFixedSize(400, 250)  # 增加高度以容纳提示语
        layout = QVBoxLayout()
        
        # 添加测试专用渠道提示标签
        business_config = CoreService.get_business_config()
        default_verify_code = business_config.get('default_verify_code', '13797173255')
        warning_text = f'⚠️ 【测试专用渠道手机号】：{default_verify_code} 请勿擅自修改系统数据！'
        
        warning_label = QLabel(warning_text)
        from apps.etc_apply.ui.ui_styles import ui_styles
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
            # 提取所有运营商编码
            operator_codes = sorted(set(row['operator_code'] for row in rows))
            print(f"可用运营商: {operator_codes}")
            
            self.operator_combo.clear()
            self.operator_combo.addItems(operator_codes)
            
            # 设置运营商选择（优先使用上次选择，否则使用默认值）
            business_config = CoreService.get_business_config()
            default_operator = self._last_operator if self._last_operator else business_config.get('default_operator_code', 'TXB')
            operator_index = self.operator_combo.findText(default_operator)
            
            if operator_index >= 0:
                self.operator_combo.setCurrentIndex(operator_index)
                print(f"设置运营商为{default_operator}，索引: {operator_index}")
                # 直接加载产品，不触发运营商切换事件（避免弹出Mock确认对话框）
                self._load_products_for_operator(default_operator)
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