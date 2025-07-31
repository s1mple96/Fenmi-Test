# -*- coding: utf-8 -*-
"""
UI工具管理器 - 统一管理UI构建、线程和解析工具
"""
import threading
import csv
import json
import os
from typing import Dict, Optional
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QComboBox, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QProgressBar, QTextEdit, QGridLayout
from PyQt5.QtCore import Qt, QMetaObject
from PyQt5.QtGui import QFont

from apps.etc_apply.ui import ui_events
from apps.etc_apply.ui.ui_core import ui_core
from apps.etc_apply.ui.ui_styles import ui_styles
from apps.etc_apply.services.log_service import LogService


class UIBuilder:
    """UI构建器 - 统一管理UI组件构建"""
    
    def __init__(self):
        self.log_service = LogService("ui_builder")
    
    def build_full_ui(self, ui) -> None:
        """构建完整的UI界面"""
        try:
            # 创建主布局
            main_layout = QVBoxLayout()
            main_layout.setSpacing(15)
            main_layout.setContentsMargins(15, 15, 15, 15)
            
            # 构建产品信息区域
            product_widget = self.build_product_section(ui)
            main_layout.addWidget(product_widget)
            
            # 构建四要素信息区域
            form_widget = self.build_form_section(ui)
            main_layout.addWidget(form_widget)
            
            # 构建操作按钮区域
            button_widget = self.build_button_section(ui)
            main_layout.addWidget(button_widget)
            
            # 构建进度区域
            progress_widget = self.build_progress_section(ui)
            main_layout.addWidget(progress_widget)
            
            # 构建日志区域
            log_widget = self.build_log_section(ui)
            main_layout.addWidget(log_widget)
            
            # 删除拖拽区域
            # 不再添加 build_drag_section
            
            ui.setLayout(main_layout)
            self.log_service.info("UI构建完成")
            
        except Exception as e:
            self.log_service.error(f"UI构建失败: {e}")
            raise
    
    def build_product_section(self, ui) -> QGroupBox:
        """构建产品信息区域"""
        product_group = QGroupBox("车辆信息")
        product_layout = QGridLayout()
        product_layout.setSpacing(10)
        
        # 产品选择
        product_label = QLabel("产品:")
        product_label.setStyleSheet(ui_styles.get_label_style())
        ui.product_edit = QLineEdit()
        ui.product_edit.setPlaceholderText("请选择产品")
        ui.product_edit.setAcceptDrops(False)  # 禁用拖拽
        ui.select_product_btn = QPushButton("选择产品")
        ui.select_product_btn.setStyleSheet(ui_styles.get_button_style())
        
        product_layout.addWidget(product_label, 0, 0)
        product_layout.addWidget(ui.product_edit, 0, 1)
        product_layout.addWidget(ui.select_product_btn, 0, 2)
        
        # 车牌省份
        province_label = QLabel("车牌省份:")
        province_label.setStyleSheet(ui_styles.get_label_style())
        ui.plate_province_edit = QLineEdit()
        ui.plate_province_edit.setPlaceholderText("请选择省份")
        ui.plate_province_edit.setAcceptDrops(False)  # 禁用拖拽
        ui.select_province_btn = QPushButton("选择")
        ui.select_province_btn.setStyleSheet(ui_styles.get_button_style())
        
        product_layout.addWidget(province_label, 1, 0)
        product_layout.addWidget(ui.plate_province_edit, 1, 1)
        product_layout.addWidget(ui.select_province_btn, 1, 2)
        
        # 车牌字母
        letter_label = QLabel("车牌字母:")
        letter_label.setStyleSheet(ui_styles.get_label_style())
        ui.plate_letter_edit = QLineEdit()
        ui.plate_letter_edit.setPlaceholderText("请选择字母")
        ui.plate_letter_edit.setAcceptDrops(False)  # 禁用拖拽
        ui.select_letter_btn = QPushButton("选择字母")
        ui.select_letter_btn.setStyleSheet(ui_styles.get_button_style())
        
        product_layout.addWidget(letter_label, 2, 0)
        product_layout.addWidget(ui.plate_letter_edit, 2, 1)
        product_layout.addWidget(ui.select_letter_btn, 2, 2)
        
        # 车牌号码
        number_label = QLabel("车牌号码:")
        number_label.setStyleSheet(ui_styles.get_label_style())
        ui.plate_number_edit = QLineEdit()
        ui.plate_number_edit.setPlaceholderText("请输入车牌号码")
        ui.plate_number_edit.setAcceptDrops(False)  # 禁用拖拽
        ui.random_plate_btn = QPushButton("随机")
        ui.random_plate_btn.setStyleSheet(ui_styles.get_button_style())
        
        product_layout.addWidget(number_label, 3, 0)
        product_layout.addWidget(ui.plate_number_edit, 3, 1)
        product_layout.addWidget(ui.random_plate_btn, 3, 2)
        
        # 车牌颜色
        color_label = QLabel("车牌颜色:")
        color_label.setStyleSheet(ui_styles.get_label_style())
        ui.plate_color_combo = QComboBox()
        ui.plate_color_combo.addItems(ui_styles.get_plate_colors())
        ui.plate_color_combo.setCurrentText("蓝色")
        ui.plate_color_combo.setAcceptDrops(False)  # 禁用拖拽
        
        product_layout.addWidget(color_label, 4, 0)
        product_layout.addWidget(ui.plate_color_combo, 4, 1)
        
        # VIN码
        vin_label = QLabel("VIN码:")
        vin_label.setStyleSheet(ui_styles.get_label_style())
        ui.vin_edit = QLineEdit()
        ui.vin_edit.setPlaceholderText("请输入VIN码")
        ui.vin_edit.setAcceptDrops(False)  # 禁用拖拽
        ui.get_vin_btn = QPushButton("自动获取VIN")
        ui.get_vin_btn.setStyleSheet(ui_styles.get_button_style())
        
        product_layout.addWidget(vin_label, 5, 0)
        product_layout.addWidget(ui.vin_edit, 5, 1)
        product_layout.addWidget(ui.get_vin_btn, 5, 2)
        
        # 设置列宽比例
        product_layout.setColumnStretch(1, 1)
        
        product_group.setLayout(product_layout)
        return product_group
    
    def build_form_section(self, ui) -> QGroupBox:
        """构建四要素信息区域（支持拖拽）"""
        from apps.etc_apply.ui.ui_component import DraggableGroupBox
        from apps.etc_apply.ui.ui_events import ui_events  # 修复未定义异常
        form_group = DraggableGroupBox("四要素信息 (支持拖拽文件自动填充)")
        form_layout = QGridLayout()
        form_layout.setSpacing(10)  # 与车辆信息区域保持相同的间距
        
        # 添加四要素字段
        four_elements_fields = [
            ("姓名", "name", "", True),
            ("身份证", "id_code", "", True),
            ("手机号", "phone", "", True),
            ("银行卡号", "bank_no", "", True)
        ]
        
        for i, (label, field_name, default_value, is_required) in enumerate(four_elements_fields):
            # 创建标签
            label_widget = QLabel(label)
            label_widget.setStyleSheet(ui_styles.get_label_style())
            form_layout.addWidget(label_widget, i, 0)
            
            # 创建输入框
            input_widget = QLineEdit()
            input_widget.setAcceptDrops(False)  # 禁用拖拽，避免与父组件冲突
            form_layout.addWidget(input_widget, i, 1)
            
            # 保存到inputs字典
            ui.inputs[field_name] = input_widget
        
        # 添加保存按钮
        ui.save_four_elements_btn = QPushButton("保存四要素")
        ui.save_four_elements_btn.setStyleSheet(ui_styles.get_button_style())
        form_layout.addWidget(ui.save_four_elements_btn, len(four_elements_fields), 1)
        
        # 设置列宽比例，与车辆信息区域保持一致
        form_layout.setColumnStretch(1, 1)
        
        form_group.setLayout(form_layout)
        # 绑定拖拽信号
        form_group.file_dropped.connect(lambda file_path: ui_events.handle_drag_drop(ui, file_path))
        return form_group
    
    def build_button_section(self, ui) -> QWidget:
        """构建操作按钮区域"""
        button_container = QWidget()
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建主要操作按钮
        ui.apply_btn = QPushButton("一键申办ETC")
        ui.apply_btn.setStyleSheet(ui_styles.get_button_style())
        ui.apply_btn.setMinimumHeight(35)  # 进一步减小按钮高度
        ui.apply_btn.setMaximumHeight(40)  # 设置最大高度
        ui.apply_btn.setFont(QFont("Microsoft YaHei", 9, QFont.Bold))  # 进一步减小字体大小
        
        button_layout.addWidget(ui.apply_btn)
        
        button_container.setLayout(button_layout)
        return button_container
    
    def build_progress_section(self, ui) -> QWidget:
        """构建进度区域"""
        progress_container = QWidget()
        progress_layout = QVBoxLayout()
        progress_layout.setSpacing(5)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建进度标签
        ui.progress_label = QLabel("进度: 等待操作")
        ui.progress_label.setStyleSheet("font-weight: bold; color: #333;")
        progress_layout.addWidget(ui.progress_label)
        
        # 创建进度条
        ui.progress_bar = QProgressBar()
        ui.progress_bar.setStyleSheet(ui_styles.get_progress_bar_style())
        ui.progress_bar.setRange(0, 100)
        ui.progress_bar.setValue(0)
        progress_layout.addWidget(ui.progress_bar)
        
        progress_container.setLayout(progress_layout)
        return progress_container
    
    def build_log_section(self, ui) -> QGroupBox:
        """构建日志区域"""
        log_group = QGroupBox("详细日志:")
        log_layout = QVBoxLayout()
        log_layout.setSpacing(5)
        
        # 创建日志文本框
        ui.log_text = QTextEdit()
        ui.log_text.setStyleSheet(ui_styles.get_text_edit_style())
        ui.log_text.setReadOnly(True)
        ui.log_text.setMinimumHeight(200)
        log_layout.addWidget(ui.log_text)
        
        log_group.setLayout(log_layout)
        return log_group


class UIThreadManager:
    """UI线程管理器 - 统一管理线程安全操作"""
    
    def __init__(self):
        self.log_service = LogService("ui_thread")
    
    def update_ui_state(self, ui, state_method: str, *args) -> None:
        """线程安全的UI状态更新"""
        try:
            if threading.current_thread() is threading.main_thread():
                getattr(ui_core, state_method)(ui, *args)
            else:
                # 使用QTimer.singleShot进行线程安全的调用
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(0, lambda: getattr(ui_core, state_method)(ui, *args))
        except Exception as e:
            self.log_service.error(f"update_ui_state异常: {e}")
    
    def safe_call(self, ui, method_name: str, *args) -> None:
        """线程安全的方法调用"""
        try:
            if threading.current_thread() is threading.main_thread():
                getattr(ui_core, method_name)(ui, *args)
            else:
                # 使用QTimer.singleShot进行线程安全的调用
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(0, lambda: getattr(ui_core, method_name)(ui, *args))
        except Exception as e:
            self.log_service.error(f"safe_call异常: {method_name} - {e}")
    
    def safe_event_call(self, ui, method_name: str, *args) -> None:
        """线程安全的事件调用"""
        try:
            if threading.current_thread() is threading.main_thread():
                getattr(ui_events, method_name)(ui, *args)
            else:
                # 使用QTimer.singleShot进行线程安全的调用
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(0, lambda: getattr(ui_events, method_name)(ui, *args))
        except Exception as e:
            self.log_service.error(f"safe_event_call异常: {method_name} - {e}")

    def append_log(self, log_widget, message: str) -> None:
        """线程安全的日志追加"""
        try:
            if threading.current_thread() is threading.main_thread():
                log_widget.append(message)
            else:
                # 使用QTimer.singleShot进行线程安全的调用
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(0, lambda: log_widget.append(message))
        except Exception as e:
            self.log_service.error(f"append_log异常: {e}")


class UIParser:
    """UI解析器 - 统一管理文件解析功能"""
    
    def __init__(self):
        self.log_service = LogService("ui_parser")
    
    def parse_txt_file(self, file_path: str) -> Optional[Dict[str, str]]:
        """解析TXT文件"""
        try:
            elements = {}
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for line in lines:
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    if key and value:
                        elements[key] = value
            
            self.log_service.info(f"TXT文件解析完成: {len(elements)} 个字段")
            return elements if elements else None
            
        except Exception as e:
            self.log_service.error(f"TXT文件解析失败: {e}")
            return None
    
    def parse_csv_file(self, file_path: str) -> Optional[Dict[str, str]]:
        """解析CSV文件"""
        try:
            elements = {}
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    elements.update(row)
                    break  # 只取第一行
            
            self.log_service.info(f"CSV文件解析完成: {len(elements)} 个字段")
            return elements if elements else None
            
        except Exception as e:
            self.log_service.error(f"CSV文件解析失败: {e}")
            return None
    
    def parse_json_file(self, file_path: str) -> Optional[Dict[str, str]]:
        """解析JSON文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 如果是列表，取第一个元素
            if isinstance(data, list) and data:
                elements = data[0]
            else:
                elements = data
            
            # 确保所有值都是字符串
            elements = {k: str(v) for k, v in elements.items()}
            
            self.log_service.info(f"JSON文件解析完成: {len(elements)} 个字段")
            return elements if elements else None
            
        except Exception as e:
            self.log_service.error(f"JSON文件解析失败: {e}")
            return None
    
    def parse_file(self, file_path: str) -> Optional[Dict[str, str]]:
        """解析文件（自动识别格式）"""
        try:
            if not os.path.isfile(file_path):
                self.log_service.error(f"文件不存在: {file_path}")
                return None
            
            file_ext = os.path.splitext(file_path)[1].lower()
            
            if file_ext == '.txt':
                return self.parse_txt_file(file_path)
            elif file_ext == '.csv':
                return self.parse_csv_file(file_path)
            elif file_ext == '.json':
                return self.parse_json_file(file_path)
            else:
                self.log_service.error(f"不支持的文件格式: {file_ext}")
                return None
                
        except Exception as e:
            self.log_service.error(f"文件解析失败: {e}")
            return None
    
    def validate_elements(self, elements: Dict[str, str]) -> bool:
        """验证解析出的四要素数据"""
        if not elements:
            return False
        
        # 检查是否包含必要的四要素字段
        required_keys = ['name', 'id_code', 'phone', 'bank_no']
        found_keys = [key for key in required_keys if key in elements and elements[key].strip()]
        
        return len(found_keys) >= 2  # 至少包含2个必要字段


# 创建全局工具管理器实例
ui_builder = UIBuilder()
ui_threads = UIThreadManager()
ui_parser = UIParser()

# 为了兼容性，保留原有的函数名
def build_full_ui(ui):
    """构建完整UI（兼容性函数）"""
    return ui_builder.build_full_ui(ui)

def update_ui_state(ui, state_method, *args):
    """更新UI状态（兼容性函数）"""
    return ui_threads.update_ui_state(ui, state_method, *args)

def parse_file(file_path):
    """解析文件（兼容性函数）"""
    return ui_parser.parse_file(file_path) 