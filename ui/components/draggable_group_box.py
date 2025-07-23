# -*- coding: utf-8 -*-
"""
支持拖拽的QGroupBox组件
"""

import os
from PyQt5.QtWidgets import QGroupBox, QMessageBox, QWidget, QVBoxLayout, QLabel, QTextEdit, QPushButton, QApplication
from PyQt5.QtCore import pyqtSignal, Qt, QPoint, QEvent
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

class ExamplePopup(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent, Qt.Window | Qt.Tool)
        self.setWindowTitle("四要素文件格式样例")
        self.setFixedSize(320, 200)
        layout = QVBoxLayout()
        label = QLabel("支持TXT格式示例：")
        layout.addWidget(label)
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        example = (
            "姓名: 张三\n"
            "身份证: 440011XXXXXXXXXXXX\n"
            "手机号: 13221630502\n"
            "银行卡号: 6222XXXXXXXXXXXXXXX"
        )
        self.text.setText(example)
        layout.addWidget(self.text)
        copy_btn = QPushButton("一键复制")
        copy_btn.clicked.connect(self.copy_example)
        layout.addWidget(copy_btn)
        self.setLayout(layout)
    def copy_example(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.text.toPlainText())
        QMessageBox.information(self, "复制成功", "样例内容已复制到剪贴板！")

class DraggableGroupBox(QGroupBox):
    file_dropped = pyqtSignal(str)
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setAcceptDrops(True)
        self.init_style()
        self.example_popup = None
        # 安装事件过滤器用于捕获标题点击
        self.installEventFilter(self)
    def init_style(self):
        self.setStyleSheet("""
            QGroupBox {
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #4CAF50;
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 10px;
                    font-weight: bold;
                    background-color: #E8F5E8;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #2E7D32;
                }
            """)
        else:
            event.ignore()
    def dragLeaveEvent(self, event):
        self.init_style()
    def dropEvent(self, event: QDropEvent):
        self.init_style()
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if os.path.isfile(file_path):
                self.file_dropped.emit(file_path)
            else:
                QMessageBox.warning(self, "警告", "请拖拽有效的文件！")
    def eventFilter(self, obj, event):
        # 捕获鼠标点击标题区域
        if obj is self and event.type() == QEvent.MouseButtonRelease:
            pos = event.pos()
            # 标题区域高度约为30像素，且x在整个宽度内
            if 0 <= pos.y() <= 30:
                self.show_example_popup()
                return True
        return super().eventFilter(obj, event)
    def show_example_popup(self):
        if self.example_popup is None:
            self.example_popup = ExamplePopup(self)
        # 居中弹出
        parent = self.parentWidget() or self
        center_x = (parent.width() - self.example_popup.width()) // 2
        center_y = (parent.height() - self.example_popup.height()) // 2
        self.example_popup.move(parent.mapToGlobal(QPoint(center_x, center_y)))
        self.example_popup.show()
        self.example_popup.raise_()
        self.example_popup.activateWindow() 