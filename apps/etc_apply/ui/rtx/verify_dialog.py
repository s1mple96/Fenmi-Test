# -*- coding: utf-8 -*-
"""
验证码对话框模块
"""
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit
from PyQt5.QtCore import QTimer
from apps.etc_apply.services.rtx.core_service import CoreService


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