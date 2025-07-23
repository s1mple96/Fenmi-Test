from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import QTimer

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
        self.start_timer()

    def start_timer(self):
        self.time_left = 60
        self.get_code_btn.setEnabled(False)
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