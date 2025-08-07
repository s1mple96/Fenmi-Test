# -*- coding: utf-8 -*-
"""
选择对话框模块 - 包含车牌字母选择和省份选择对话框
"""
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, QGroupBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from apps.etc_apply.services.rtx.core_service import CoreService


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
        layout = QVBoxLayout()
        title_label = QLabel("请选择省份")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        layout.addWidget(title_label)

        # 获取热门省份配置
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