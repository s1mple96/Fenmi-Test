# -*- coding: utf-8 -*-
"""
Tab切换组件 - 支持客车和货车模式切换
"""
from PyQt5.QtWidgets import (QWidget, QTabWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QComboBox, QPushButton, 
                             QGroupBox, QFormLayout, QScrollArea)
from PyQt5.QtCore import pyqtSignal, Qt
from apps.etc_apply.services.hcb.truck_data_service import TruckDataService
from apps.etc_apply.ui.rtx.ui_styles import UIStyleManager


class VehicleTabWidget(QTabWidget):
    """车辆类型Tab切换组件"""
    
    # 定义信号
    vehicle_type_changed = pyqtSignal(str)  # 车辆类型切换信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_ui = parent
        self.style_manager = UIStyleManager()
        
        # 创建客车和货车tab页
        self.init_tabs()
        
        # 绑定tab切换事件
        self.currentChanged.connect(self.on_tab_changed)
        
    def init_tabs(self):
        """初始化Tab页"""
        # 客车Tab（默认）
        self.passenger_tab = PassengerCarWidget(self.parent_ui)
        self.addTab(self.passenger_tab, "客车")
        
        # 货车Tab
        self.truck_tab = TruckWidget(self.parent_ui)
        self.addTab(self.truck_tab, "货车")
        
        # 设置默认选中客车
        self.setCurrentIndex(0)
        
    def on_tab_changed(self, index):
        """Tab切换事件处理"""
        if index == 0:
            vehicle_type = "passenger"
            self.vehicle_type_changed.emit("passenger")
        elif index == 1:
            vehicle_type = "truck"
            self.vehicle_type_changed.emit("truck")
        
        # 更新父UI的车辆类型标识
        if self.parent_ui:
            self.parent_ui.current_vehicle_type = vehicle_type
    
    def get_current_form_data(self):
        """获取当前Tab的表单数据"""
        current_widget = self.currentWidget()
        if hasattr(current_widget, 'get_form_data'):
            return current_widget.get_form_data()
        return {}
    
    def get_current_vehicle_type(self):
        """获取当前车辆类型"""
        return "passenger" if self.currentIndex() == 0 else "truck"


class PassengerCarWidget(QWidget):
    """客车表单组件（保持原有客车字段不变）"""
    
    def __init__(self, parent_ui=None):
        super().__init__()
        self.parent_ui = parent_ui
        self.inputs = {}
        self.init_ui()
    
    def init_ui(self):
        """初始化客车表单UI"""
        layout = QVBoxLayout(self)
        
        # 设置整体背景样式，与货车保持一致
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: 'Microsoft YaHei', Arial, sans-serif;
                font-size: 12px;
            }
        """)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # 基础信息组
        basic_group = self.create_basic_info_group()
        scroll_layout.addWidget(basic_group)
        
        # 车辆信息组
        vehicle_group = self.create_vehicle_info_group()
        scroll_layout.addWidget(vehicle_group)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
    
    def create_basic_info_group(self):
        """创建基础信息组"""
        group = QGroupBox("基础信息")
        # 应用统一的组件样式
        group.setStyleSheet(self.style_manager.get_group_box_style())
        layout = QFormLayout(group)
        
        # 客车基础字段（保持原有不变）
        fields = [
            ("name", "持卡人姓名", "text"),
            ("id_code", "身份证号", "text"),
            ("phone", "手机号", "text"),
            ("bank_no", "银行卡号", "text"),
        ]
        
        for field_name, label, field_type in fields:
            if field_type == "text":
                widget = QLineEdit()
                # 应用统一的输入框样式
                widget.setStyleSheet(self.style_manager.get_input_style())
                self.inputs[field_name] = widget
                label_widget = QLabel(label)
                # 应用统一的标签样式
                label_widget.setStyleSheet(self.style_manager.get_label_style())
                layout.addRow(label_widget, widget)
        
        return group
    
    def create_vehicle_info_group(self):
        """创建车辆信息组"""
        group = QGroupBox("车辆信息")
        # 应用统一的组件样式
        group.setStyleSheet(self.style_manager.get_group_box_style())
        layout = QFormLayout(group)
        
        # 客车车辆字段
        fields = [
            ("plate_province", "车牌省份", "text"),
            ("plate_letter", "车牌字母", "text"),
            ("plate_number", "车牌号码", "text"),
            ("vin", "车架号", "text"),
        ]
        
        for field_name, label, field_type in fields:
            if field_type == "text":
                widget = QLineEdit()
                # 应用统一的输入框样式
                widget.setStyleSheet(self.style_manager.get_input_style())
                self.inputs[field_name] = widget
                label_widget = QLabel(label)
                # 应用统一的标签样式
                label_widget.setStyleSheet(self.style_manager.get_label_style())
                layout.addRow(label_widget, widget)
        
        return group
    
    def get_form_data(self):
        """获取客车表单数据"""
        data = {}
        for field_name, widget in self.inputs.items():
            if isinstance(widget, QLineEdit):
                data[field_name] = widget.text().strip()
            elif isinstance(widget, QComboBox):
                data[field_name] = widget.currentText()
        return data


class TruckWidget(QWidget):
    """货车表单组件"""
    
    def __init__(self, parent_ui=None):
        super().__init__()
        self.parent_ui = parent_ui
        self.inputs = {}
        self.init_ui()
    
    def init_ui(self):
        """初始化货车表单UI"""
        layout = QVBoxLayout(self)
        
        # 设置整体背景样式，与客车保持一致
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f5f5;
                font-family: 'Microsoft YaHei', Arial, sans-serif;
                font-size: 12px;
            }
        """)
        
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # 基础信息组
        basic_group = self.create_basic_info_group()
        scroll_layout.addWidget(basic_group)
        
        # 车辆信息组
        vehicle_group = self.create_vehicle_info_group()
        scroll_layout.addWidget(vehicle_group)
        
        # 货车专用信息组
        truck_group = self.create_truck_specific_group()
        # 隐藏货车专用信息区域
        truck_group.setVisible(False)
        truck_group.setMaximumHeight(0)  # 设置高度为0，完全隐藏
        scroll_layout.addWidget(truck_group)
        
        scroll_area.setWidget(scroll_widget)
        scroll_area.setWidgetResizable(True)
        layout.addWidget(scroll_area)
    
    def create_basic_info_group(self):
        """创建基础信息组"""
        group = QGroupBox("基础信息")
        # 应用统一的组件样式
        group.setStyleSheet(self.style_manager.get_group_box_style())
        layout = QFormLayout(group)
        
        # 基础字段
        fields = [
            ("name", "持卡人姓名", "text"),
            ("id_code", "身份证号", "text"),
            ("phone", "手机号", "text"),
            ("bank_name", "银行名称", "text"),
            ("bank_no", "银行卡号", "text"),
            ("urgent_contact", "紧急联系人", "text"),
            ("urgent_phone", "紧急联系电话", "text"),
        ]
        
        for field_name, label, field_type in fields:
            if field_type == "text":
                widget = QLineEdit()
                # 应用统一的输入框样式
                widget.setStyleSheet(self.style_manager.get_input_style())
                self.inputs[field_name] = widget
                label_widget = QLabel(label)
                # 应用统一的标签样式
                label_widget.setStyleSheet(self.style_manager.get_label_style())
                layout.addRow(label_widget, widget)
        
        return group
    
    def create_vehicle_info_group(self):
        """创建车辆信息组"""
        group = QGroupBox("车辆信息")
        # 应用统一的组件样式
        group.setStyleSheet(self.style_manager.get_group_box_style())
        layout = QFormLayout(group)
        
        # 车辆字段
        fields = [
            ("plate_province", "车牌省份", "text"),
            ("plate_letter", "车牌字母", "text"),
            ("plate_number", "车牌号码", "text"),
            ("plate_color", "车牌颜色", "combo"),
            ("vin", "VIN码", "text"),
        ]
        
        for field_name, label, field_type in fields:
            if field_type == "text":
                widget = QLineEdit()
                # 应用统一的输入框样式
                widget.setStyleSheet(self.style_manager.get_input_style())
                self.inputs[field_name] = widget
                label_widget = QLabel(label)
                # 应用统一的标签样式
                label_widget.setStyleSheet(self.style_manager.get_label_style())
                layout.addRow(label_widget, widget)
            elif field_type == "combo":
                widget = QComboBox()
                # 应用统一的下拉框样式
                widget.setStyleSheet(self.style_manager.get_combo_box_style())
                widget.addItems(["蓝色", "黄色", "绿色", "白色", "黑色"])
                widget.setCurrentText("黄色")  # 货车默认黄色
                self.inputs[field_name] = widget
                label_widget = QLabel(label)
                # 应用统一的标签样式
                label_widget.setStyleSheet(self.style_manager.get_label_style())
                layout.addRow(label_widget, widget)
        
        return group
    
    def create_truck_specific_group(self):
        """创建货车专用信息组"""
        group = QGroupBox("货车专用信息")
        # 应用统一的组件样式
        group.setStyleSheet(self.style_manager.get_group_box_style())
        layout = QFormLayout(group)
        
        # 货车专用字段
        fields = [
            ("vehicle_axles", "车轴数", "number"),
            ("vehicle_wheels", "车轮数", "number"),
            ("total_mass", "总质量(kg)", "number"),
            ("unladen_mass", "整备质量(kg)", "number"),
            ("approved_count", "核定载人数", "number"),
            ("weight_limits", "载质量(kg)", "number"),
            ("length", "长(mm)", "number"),
            ("width", "宽(mm)", "number"),
            ("height", "高(mm)", "number"),
        ]
        
        # 获取货车默认值
        defaults = TruckDataService.get_truck_default_values()
        
        for field_name, label, field_type in fields:
            widget = QLineEdit()
            # 应用统一的输入框样式
            widget.setStyleSheet(self.style_manager.get_input_style())
            # 设置默认值
            if field_name in defaults:
                widget.setText(str(defaults[field_name]))
            self.inputs[field_name] = widget
            label_widget = QLabel(label)
            # 应用统一的标签样式
            label_widget.setStyleSheet(self.style_manager.get_label_style())
            layout.addRow(label_widget, widget)
        
        return group
    
    def get_form_data(self):
        """获取货车表单数据"""
        data = {}
        for field_name, widget in self.inputs.items():
            if isinstance(widget, QLineEdit):
                data[field_name] = widget.text().strip()
            elif isinstance(widget, QComboBox):
                data[field_name] = widget.currentText()
        
        # 将通用字段名映射为货车专用字段名
        field_mapping = {
            'name': 'truck_name',
            'id_code': 'truck_id_code', 
            'phone': 'truck_phone',
            'bank_name': 'truck_bank_name',
            'bank_no': 'truck_bank_no'
        }
        
        # 创建新的数据字典，使用货车专用字段名
        truck_data = {}
        for field_name, value in data.items():
            if field_name in field_mapping:
                truck_data[field_mapping[field_name]] = value
            else:
                truck_data[field_name] = value
        
        # 添加货车特有标识
        truck_data['vehicle_type'] = 'truck'
        truck_data['plate_color'] = '黄色'  # 货车默认黄色
        
        # 添加选择的产品信息
        if hasattr(self.parent_ui, 'selected_truck_product') and self.parent_ui.selected_truck_product:
            truck_data['selected_product'] = self.parent_ui.selected_truck_product
        
        return truck_data 