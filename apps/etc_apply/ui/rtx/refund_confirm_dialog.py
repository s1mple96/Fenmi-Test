# -*- coding: utf-8 -*-
"""
退款确认弹窗组件
"""

import sys
from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QFrame)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QIcon
from typing import Optional, Dict, Any


class RefundWorkerThread(QThread):
    """退款处理线程"""
    refund_finished = pyqtSignal(dict)  # 退款完成信号
    
    def __init__(self, car_num: str):
        super().__init__()
        self.car_num = car_num
        
    def run(self):
        """执行退款"""
        try:
            from apps.etc_apply.services.refund_service import auto_refund_after_apply
            result = auto_refund_after_apply(self.car_num)
            self.refund_finished.emit(result)
        except Exception as e:
            error_result = {
                'success': False,
                'error_message': str(e),
                'car_num': self.car_num
            }
            self.refund_finished.emit(error_result)


class RefundConfirmDialog(QDialog):
    """退款确认弹窗"""
    
    def __init__(self, parent=None, car_num: str = "", payment_amount: str = "0.00"):
        super().__init__(parent)
        self.car_num = car_num
        self.payment_amount = payment_amount
        self.refund_thread = None
        print(f"[DEBUG] RefundConfirmDialog 初始化: 车牌号={self.car_num}, 支付金额={self.payment_amount}")
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("申办支付确认")
        self.setModal(True)
        
        # 先设置最小尺寸，让内容自适应高度
        self.setMinimumSize(420, 300)
        self.resize(420, 300)  # 初始尺寸
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)  # 减小间距让内容紧凑
        
        # 标题区域
        title_frame = QFrame()
        title_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f8ff;
                border: 1px solid #4CAF50;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        
        title_layout = QVBoxLayout()
        title_layout.setContentsMargins(10, 8, 10, 8)
        
        # 成功图标和标题
        header_layout = QHBoxLayout()
        
        success_label = QLabel("🎉")
        success_label.setFont(QFont("Arial", 20))
        success_label.setAlignment(Qt.AlignCenter)
        
        title_label = QLabel("ETC申办完成！！！")
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title_label.setStyleSheet("color: #2E7D32;")
        
        header_layout.addWidget(success_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        title_layout.addLayout(header_layout)
        title_frame.setLayout(title_layout)
        main_layout.addWidget(title_frame)
        
        # 信息区域
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 15px;
            }
        """)
        
        info_layout = QVBoxLayout()
        info_layout.setContentsMargins(8, 8, 8, 8)  # 减小内边距
        info_layout.setSpacing(8)  # 减小间距
        
        # 车牌号信息行
        car_info_frame = QFrame()
        car_info_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 6px;
                margin: 2px 0;
                min-height: 20px;
            }
        """)
        car_info_layout = QHBoxLayout(car_info_frame)
        car_info_layout.setContentsMargins(8, 6, 8, 6)  # 减小内边距
        
        car_label = QLabel("车牌号:")
        car_label.setFont(QFont("Microsoft YaHei", 10))
        car_label.setStyleSheet("color: #666; background: none; border: none;")
        car_label.setFixedWidth(60)
        
        car_value = QLabel(self.car_num)
        car_value.setFont(QFont("Microsoft YaHei", 10, QFont.Bold))
        car_value.setStyleSheet("color: #1976D2; background: none; border: none;")
        
        car_info_layout.addWidget(car_label)
        car_info_layout.addWidget(car_value)
        car_info_layout.addStretch()
        
        # 支付金额信息行
        amount_info_frame = QFrame()
        amount_info_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 6px;
                margin: 2px 0;
                min-height: 20px;
            }
        """)
        amount_info_layout = QHBoxLayout(amount_info_frame)
        amount_info_layout.setContentsMargins(8, 6, 8, 6)  # 减小内边距
        
        amount_label = QLabel("支付金额:")
        amount_label.setFont(QFont("Microsoft YaHei", 10))
        amount_label.setStyleSheet("color: #666; background: none; border: none;")
        amount_label.setFixedWidth(60)
        
        amount_value = QLabel(f"¥ {self.payment_amount}")
        amount_value.setFont(QFont("Microsoft YaHei", 11, QFont.Bold))
        amount_value.setStyleSheet("color: #E91E63; background: none; border: none;")
        
        amount_info_layout.addWidget(amount_label)
        amount_info_layout.addWidget(amount_value)
        amount_info_layout.addStretch()
        
        info_layout.addWidget(car_info_frame)
        info_layout.addWidget(amount_info_frame)
        
        # 提示信息
        tip_frame = QFrame()
        tip_frame.setStyleSheet("""
            QFrame {
                background-color: #fff8e1;
                border: 1px solid #ffcc02;
                border-radius: 4px;
                padding: 6px;
                margin: 3px 0;
                min-height: 25px;
            }
        """)
        tip_layout = QHBoxLayout(tip_frame)
        tip_layout.setContentsMargins(8, 6, 8, 6)  # 减小内边距
        
        tip_icon = QLabel("💡")
        tip_icon.setFont(QFont("Arial", 14))
        tip_icon.setStyleSheet("background: none; border: none;")
        
        tip_text = QLabel("提示：申办已完成，您可以选择是否申请退款")
        tip_text.setFont(QFont("Microsoft YaHei", 9))
        tip_text.setStyleSheet("color: #666; background: none; border: none;")
        tip_text.setWordWrap(True)
        
        tip_layout.addWidget(tip_icon)
        tip_layout.addWidget(tip_text)
        
        info_layout.addWidget(tip_frame)
        info_frame.setLayout(info_layout)
        main_layout.addWidget(info_frame)
        
        # 询问区域
        question_label = QLabel("是否申请退款？")
        question_label.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        question_label.setStyleSheet("color: #333; margin: 8px 0;")
        question_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(question_label)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # 不退款按钮
        self.no_refund_btn = QPushButton("不退款")
        self.no_refund_btn.setFixedSize(120, 40)
        self.no_refund_btn.setFont(QFont("Microsoft YaHei", 10))
        self.no_refund_btn.setStyleSheet("""
            QPushButton {
                background-color: #f5f5f5;
                border: 2px solid #ccc;
                border-radius: 6px;
                color: #555;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
                border-color: #999;
            }
            QPushButton:pressed {
                background-color: #d5d5d5;
            }
        """)
        self.no_refund_btn.clicked.connect(self.reject_refund)
        
        # 申请退款按钮
        self.refund_btn = QPushButton("申请退款")
        self.refund_btn.setFixedSize(120, 40)
        self.refund_btn.setFont(QFont("Microsoft YaHei", 10))
        self.refund_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                border: 2px solid #4CAF50;
                border-radius: 6px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
                border-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                border-color: #cccccc;
                color: #666666;
            }
        """)
        self.refund_btn.clicked.connect(self.confirm_refund)
        
        button_layout.addStretch()
        button_layout.addWidget(self.no_refund_btn)
        button_layout.addWidget(self.refund_btn)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
        
        # 调整窗口大小以适应内容
        self.adjustSize()
        
        # 设置窗口居中到屏幕中央
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        self.move(x, y)
        
    def reject_refund(self):
        """选择不退款"""
        self.reject()
        
    def confirm_refund(self):
        """确认退款"""
        # 禁用按钮
        self.refund_btn.setEnabled(False)
        self.no_refund_btn.setEnabled(False)
        
        # 更新按钮文本
        self.refund_btn.setText("处理中...")
        
        # 启动退款线程
        self.refund_thread = RefundWorkerThread(self.car_num)
        self.refund_thread.refund_finished.connect(self.on_refund_finished)
        self.refund_thread.start()
        
    def on_refund_finished(self, result: Dict[str, Any]):
        """退款完成处理"""
        if result.get('success'):
            # 退款成功
            self.show_refund_result_dialog(True, result)
        else:
            # 退款失败
            error_msg = result.get('error_message', '未知错误')
            self.show_refund_result_dialog(False, result, error_msg)
        
        self.accept()
        
    def show_refund_result_dialog(self, success: bool, result: Dict[str, Any], error_msg: str = ""):
        """显示退款结果弹窗"""
        result_dialog = RefundResultDialog(self.parent(), success, result, error_msg)
        result_dialog.exec_()


class RefundResultDialog(QDialog):
    """退款结果弹窗"""
    
    def __init__(self, parent=None, success: bool = True, result: Dict[str, Any] = None, error_msg: str = ""):
        super().__init__(parent)
        self.success = success
        self.result = result or {}
        self.error_msg = error_msg
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("退款结果")
        self.setModal(True)
        self.setFixedSize(360, 280)
        
        # 设置窗口居中到屏幕中央
        from PyQt5.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()
        x = (screen.width() - 360) // 2
        y = (screen.height() - 280) // 2
        self.move(x, y)
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)
        
        # 结果标题（去掉图标）
        header_layout = QVBoxLayout()
        header_layout.setAlignment(Qt.AlignCenter)
        
        if self.success:
            title_text = "退款申请成功"
            title_color = "#4CAF50"
        else:
            title_text = "退款申请失败"
            title_color = "#F44336"
        
        title_label = QLabel(title_text)
        title_label.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        title_label.setStyleSheet(f"color: {title_color}; margin: 8px 0;")
        title_label.setAlignment(Qt.AlignCenter)
        
        header_layout.addWidget(title_label)
        
        main_layout.addLayout(header_layout)
        
        # 详细信息
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_text.setFixedHeight(100)
        info_text.setStyleSheet("""
            QTextEdit {
                background-color: #f9f9f9;
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                font-family: 'Microsoft YaHei';
                font-size: 9px;
            }
        """)
        
        if self.success:
            car_num = self.result.get('car_num', 'N/A')
            total_orders = self.result.get('total_orders', 0)
            refunded_orders = self.result.get('refunded_orders', 0)
            failed_orders = self.result.get('failed_orders', 0)
            
            info_content = f"""退款处理完成

车牌号: {car_num}
总订单数: {total_orders}
成功退款: {refunded_orders}
失败退款: {failed_orders}

💡 提示: 退款金额通常在1-3个工作日内到账，请耐心等待。"""
        else:
            info_content = f"""退款处理失败

错误信息: {self.error_msg}

💡 建议: 请稍后重试或联系客服处理。"""
            
        info_text.setPlainText(info_content)
        main_layout.addWidget(info_text)
        
        # 确定按钮
        ok_button = QPushButton("确定")
        ok_button.setFixedSize(80, 32)
        ok_button.setFont(QFont("Microsoft YaHei", 9))
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                border: none;
                border-radius: 4px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        ok_button.clicked.connect(self.accept)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)


def show_refund_confirm_dialog(parent, car_num: str, payment_amount: str = "0.00") -> bool:
    """
    显示退款确认弹窗
    :param parent: 父窗口
    :param car_num: 车牌号
    :param payment_amount: 支付金额
    :return: 是否选择了退款
    """
    dialog = RefundConfirmDialog(parent, car_num, payment_amount)
    result = dialog.exec_()
    return result == QDialog.Accepted 