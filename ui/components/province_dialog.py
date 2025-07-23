# -*- coding: utf-8 -*-
"""
省份选择对话框（支持热门+搜索+高亮已选，含全部省份）
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QGridLayout, QMessageBox, QLineEdit, QWidget
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

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

# 热门省份简称
HOT_PROVINCES = ["苏", "桂", "黑", "蒙", "湘", "川"]

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
        # 不再添加确定/取消按钮区域

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
        for abbr in HOT_PROVINCES:
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
            if abbr in HOT_PROVINCES:
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

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    dialog = ProvinceDialog(selected_province="苏")
    if dialog.exec_() == QDialog.Accepted:
        selected = dialog.get_selected_province()
        print(f"选中的省份: {selected}")
    sys.exit() 