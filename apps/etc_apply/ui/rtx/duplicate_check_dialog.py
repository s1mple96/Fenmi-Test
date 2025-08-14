# -*- coding: utf-8 -*-
"""
重复申办确认对话框
显示用户已有的ETC记录，并询问是否继续申办
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                           QTextEdit, QLabel, QCheckBox, QScrollArea, 
                           QWidget, QFrame, QApplication)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor
from typing import List, Dict, Any


class DuplicateCheckDialog(QDialog):
    """重复申办确认对话框"""
    
    # 自定义信号
    continue_apply_signal = pyqtSignal(bool)  # True=继续申办，False=取消
    
    def __init__(self, existing_records: List[Dict], parent=None):
        super().__init__(parent)
        self.existing_records = existing_records
        self.result_continue = False
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("发现需要处理的ETC申办记录")
        self.setFixedSize(700, 600)
        self.setModal(True)
        
        # 设置窗口居中
        self.center_on_screen()
        
        # 主布局
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel("⚠️ 发现需要处理的ETC申办记录")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #e74c3c; margin-bottom: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 说明文字
        description_label = QLabel(
            "系统检测到该用户已有ETC相关记录，其中以下记录需要临时处理以允许重新申办："
        )
        description_label.setWordWrap(True)
        description_label.setStyleSheet("color: #2c3e50; font-size: 12px; margin-bottom: 10px;")
        main_layout.addWidget(description_label)
        
        # 记录显示区域
        self.create_records_display(main_layout)
        
        # 解决方案说明
        self.create_solution_info(main_layout)
        
        # 确认选项
        self.create_confirmation_options(main_layout)
        
        # 按钮区域
        self.create_buttons(main_layout)
        
        self.setLayout(main_layout)
        
        # 应用样式表
        self.apply_stylesheet()
    
    def center_on_screen(self):
        """将窗口居中显示"""
        screen = QApplication.desktop().screenGeometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def create_records_display(self, main_layout):
        """创建记录显示区域"""
        # 标题
        records_label = QLabel(f"📋 发现的ETC记录 ({len(self.existing_records)}条)")
        records_font = QFont()
        records_font.setPointSize(11)
        records_font.setBold(True)
        records_label.setFont(records_font)
        records_label.setStyleSheet("color: #34495e; margin-top: 10px;")
        main_layout.addWidget(records_label)
        
        # 滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)
        scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
        """)
        
        # 记录容器
        records_widget = QWidget()
        records_layout = QVBoxLayout(records_widget)
        records_layout.setSpacing(8)
        records_layout.setContentsMargins(10, 10, 10, 10)
        
        # 显示每条记录
        for i, record in enumerate(self.existing_records, 1):
            record_frame = self.create_record_frame(record, i)
            records_layout.addWidget(record_frame)
        
        records_widget.setLayout(records_layout)
        scroll_area.setWidget(records_widget)
        main_layout.addWidget(scroll_area)
    
    def create_record_frame(self, record: Dict, index: int) -> QFrame:
        """创建单个记录的显示框架"""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box)
        frame.setStyleSheet("""
            QFrame {
                border: 1px solid #d5dbdb;
                border-radius: 5px;
                background-color: white;
                padding: 8px;
            }
        """)
        
        layout = QVBoxLayout(frame)
        layout.setSpacing(4)
        layout.setContentsMargins(8, 8, 8, 8)
        
        # 记录标题
        table_name = "货车用户表" if record['table'] == 'hcb_truckuser' else "申办记录表"
        status_desc = self.get_status_description(record)
        
        title_text = f"{index}. 【{table_name}】车牌：{record.get('car_num', '未知')} | 状态：{status_desc}"
        title_label = QLabel(title_text)
        title_font = QFont()
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("color: #2c3e50; font-size: 11px;")
        layout.addWidget(title_label)
        
        # 详细信息
        details = []
        details.append(f"姓名：{record.get('name', '未知')}")
        details.append(f"手机号：{record.get('phone', '未知')}")
        details.append(f"身份证：{record.get('id_code', '未知')}")
        details.append(f"匹配类型：{record.get('match_type', '未知')}")
        
        if record.get('etc_sn'):
            details.append(f"ETC卡号：{record['etc_sn']}")
        if record.get('obu_no'):
            details.append(f"OBU号：{record['obu_no']}")
        if record.get('create_time'):
            details.append(f"创建时间：{record['create_time']}")
        
        details_text = " | ".join(details)
        details_label = QLabel(details_text)
        details_label.setWordWrap(True)
        details_label.setStyleSheet("color: #7f8c8d; font-size: 10px;")
        layout.addWidget(details_label)
        
        return frame
    
    def get_status_description(self, record: Dict) -> str:
        """获取状态描述"""
        if record['table'] == 'hcb_truckuser':
            status_map = {
                '0': '暂无ETC状态',
                '1': '正常', 
                '2': 'ETC黑名单',
                '3': '待激活',
                '4': '已注销'
            }
            return status_map.get(record['current_status'], f"未知状态({record['current_status']})")
        else:
            status_map = {
                '0': '未完成',
                '1': '已支付',
                '2': '初审中',
                '3': '待发行',
                '4': '发行中',
                '5': '配送中',
                '6': '已完成',
                '7': '已激活',
                '8': '已驳回',
                '10': '已注销',
                '11': '已发行'
            }
            return status_map.get(record['current_status'], f"未知状态({record['current_status']})")
    
    def create_solution_info(self, main_layout):
        """创建解决方案说明"""
        solution_label = QLabel("💡 解决方案")
        solution_font = QFont()
        solution_font.setPointSize(11)
        solution_font.setBold(True)
        solution_label.setFont(solution_font)
        solution_label.setStyleSheet("color: #27ae60; margin-top: 15px;")
        main_layout.addWidget(solution_label)
        
        solution_text = QTextEdit()
        solution_text.setReadOnly(True)
        solution_text.setMaximumHeight(80)
        solution_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #27ae60;
                border-radius: 5px;
                background-color: #e8f8f5;
                color: #1e8449;
                font-size: 11px;
                padding: 8px;
            }
        """)
        
        solution_content = """系统将采用以下方式处理这些记录：
1. 仅临时修改状态为"正常"的记录（货车用户表STATUS：正常→暂无ETC，申办记录表ETCSTATUS：已完成/已激活→已驳回）
2. 跳过已经是异常状态的记录（如：黑名单、已注销、已驳回等）
3. 允许正常进行ETC申办流程
4. 申办完成后自动恢复所有被修改记录的原始状态
5. 全程记录操作日志，确保数据安全性"""
        
        solution_text.setPlainText(solution_content)
        main_layout.addWidget(solution_text)
    
    def create_confirmation_options(self, main_layout):
        """创建确认选项"""
        self.confirm_checkbox = QCheckBox("我已了解上述情况，同意继续申办ETC")
        self.confirm_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 12px;
                color: #2c3e50;
                margin-top: 10px;
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #bdc3c7;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #27ae60;
                background-color: #27ae60;
            }
            QCheckBox::indicator:checked:enabled {
                background-color: #27ae60;
                border: 2px solid #27ae60;
                background-image: url(data:image/svg+xml;charset=utf-8,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 16 16' fill='white'%3E%3Cpath d='M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0z'/%3E%3C/svg%3E);
                background-repeat: no-repeat;
                background-position: center;
            }
            QCheckBox::indicator:hover:unchecked {
                border: 2px solid #3498db;
                background-color: #ecf0f1;
            }
            QCheckBox::indicator:hover:checked {
                border: 2px solid #2ecc71;
                background-color: #2ecc71;
            }
        """)
        main_layout.addWidget(self.confirm_checkbox)
        
        # 连接复选框状态变化信号
        self.confirm_checkbox.stateChanged.connect(self.on_checkbox_changed)
    
    def create_buttons(self, main_layout):
        """创建按钮区域"""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        button_layout.setContentsMargins(0, 20, 0, 0)
        
        # 取消按钮
        self.cancel_button = QPushButton("取消申办")
        self.cancel_button.setFixedSize(120, 35)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                border: none;
                border-radius: 5px;
                color: white;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
            QPushButton:pressed {
                background-color: #6c7b7d;
            }
        """)
        self.cancel_button.clicked.connect(self.on_cancel)
        
        # 继续按钮
        self.continue_button = QPushButton("继续申办")
        self.continue_button.setFixedSize(120, 35)
        self.continue_button.setEnabled(False)  # 初始状态禁用
        self.continue_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                border: none;
                border-radius: 5px;
                color: white;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover:enabled {
                background-color: #c0392b;
            }
            QPushButton:pressed:enabled {
                background-color: #a93226;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.continue_button.clicked.connect(self.on_continue)
        
        # 布局
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.continue_button)
        
        main_layout.addLayout(button_layout)
    
    def on_checkbox_changed(self, state):
        """复选框状态变化处理"""
        self.continue_button.setEnabled(state == Qt.Checked)
    
    def on_cancel(self):
        """取消申办"""
        self.result_continue = False
        self.continue_apply_signal.emit(False)
        self.reject()
    
    def on_continue(self):
        """继续申办"""
        self.result_continue = True
        self.continue_apply_signal.emit(True)
        self.accept()
    
    def apply_stylesheet(self):
        """应用窗口样式表"""
        self.setStyleSheet("""
            QDialog {
                background-color: #ecf0f1;
                font-family: 'Microsoft YaHei', Arial, sans-serif;
            }
        """)
    
    def get_result(self) -> bool:
        """获取用户选择结果"""
        return self.result_continue
    
    @staticmethod
    def show_duplicate_check_dialog(existing_records: List[Dict], parent=None) -> bool:
        """
        显示重复检查对话框
        :param existing_records: 现有记录列表
        :param parent: 父窗口
        :return: True=继续申办，False=取消
        """
        dialog = DuplicateCheckDialog(existing_records, parent)
        result = dialog.exec_()
        return dialog.get_result() if result == QDialog.Accepted else False 