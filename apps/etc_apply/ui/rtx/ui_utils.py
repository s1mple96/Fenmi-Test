# -*- coding: utf-8 -*-
"""
UI工具管理器 - 统一管理UI构建、线程和解析工具
"""
import threading
import csv
import json
import os
from typing import Dict, Optional
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QComboBox, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QProgressBar, QTextEdit, QGridLayout, QScrollArea
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from apps.etc_apply.ui.rtx import ui_events
from apps.etc_apply.ui.rtx.ui_core import ui_core
from apps.etc_apply.ui.rtx.ui_styles import ui_styles
from apps.etc_apply.services.rtx.log_service import LogService


class UIBuilder:
    """UI构建器 - 统一管理UI组件构建"""
    
    def __init__(self):
        self.log_service = LogService("ui_builder")
    
    def build_full_ui(self, ui) -> None:
        """构建完整的UI界面"""
        try:
            # 检查是否已有Tab容器
            if hasattr(ui, 'passenger_layout') and hasattr(ui, 'truck_layout'):
                # 使用Tab模式构建UI
                self.build_tab_ui(ui)
            else:
                # 使用传统模式构建UI
                self.build_traditional_ui(ui)
            
            self.log_service.info("UI构建完成")
            
        except Exception as e:
            self.log_service.error(f"UI构建失败: {e}")
    
    def build_traditional_ui(self, ui) -> None:
        """构建传统UI（无Tab）"""
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
            
        ui.setLayout(main_layout)
    
    def build_tab_ui(self, ui) -> None:
        """构建Tab模式UI"""
        # 构建客车Tab内容
        self.build_passenger_tab(ui)
        
        # 构建货车Tab内容
        self.build_truck_tab(ui)
        
        # 构建共享区域（按钮、进度、日志）
        self.build_shared_sections(ui)
    
    def build_passenger_tab(self, ui) -> None:
        """构建客车Tab内容"""
        # 构建产品信息区域
        product_widget = self.build_passenger_product_section(ui)
        ui.passenger_layout.addWidget(product_widget)
        
        # 构建车辆信息区域
        vehicle_widget = self.build_product_section(ui)
        ui.passenger_layout.addWidget(vehicle_widget)
        
        # 构建四要素信息区域
        form_widget = self.build_form_section(ui)
        ui.passenger_layout.addWidget(form_widget)
        
        ui.passenger_layout.addStretch()
    
    def build_truck_product_section(self, ui) -> QGroupBox:
        """构建货车产品选择区域"""
        product_group = QGroupBox("产品信息")
        product_layout = QGridLayout()
        product_layout.setSpacing(10)
        product_layout.setColumnStretch(1, 1)
        
        # 产品选择
        product_label = QLabel("产品:")
        product_label.setStyleSheet(ui_styles.get_label_style())
        ui.truck_product_edit = QLineEdit()
        ui.truck_product_edit.setPlaceholderText("请选择货车产品")
        ui.truck_product_edit.setAcceptDrops(False)  # 禁用拖拽
        ui.truck_select_product_btn = QPushButton("选择产品")
        ui.truck_select_product_btn.setStyleSheet(ui_styles.get_button_style())
        
        product_layout.addWidget(product_label, 0, 0)
        product_layout.addWidget(ui.truck_product_edit, 0, 1)
        product_layout.addWidget(ui.truck_select_product_btn, 0, 2)
        
        product_group.setLayout(product_layout)
        return product_group
    
    def build_truck_tab(self, ui) -> None:
        """构建货车Tab内容"""
        # 创建滚动区域
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # 创建滚动内容容器
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        
        # 构建货车产品选择区域
        product_group = self.build_truck_product_section(ui)
        scroll_layout.addWidget(product_group)
        
        # 构建货车表单组（分组显示）
        basic_group = self.build_truck_basic_section(ui)
        scroll_layout.addWidget(basic_group)
        
        vehicle_group = self.build_truck_vehicle_section(ui)
        scroll_layout.addWidget(vehicle_group)
        
        truck_specific_group = self.build_truck_specific_section(ui)
        scroll_layout.addWidget(truck_specific_group)
        
        scroll_layout.addStretch()
        
        # 设置滚动区域内容
        scroll_area.setWidget(scroll_content)
        
        # 添加到货车Tab布局
        ui.truck_layout.addWidget(scroll_area)
    
    def build_shared_sections(self, ui) -> None:
        """构建共享区域（按钮、进度、日志）"""
        # 构建操作按钮区域
        button_widget = self.build_button_section(ui)
        ui.main_layout.addWidget(button_widget)
        
        # 构建进度区域
        progress_widget = self.build_progress_section(ui)
        ui.main_layout.addWidget(progress_widget)
        
        # 构建日志区域
        log_widget = self.build_log_section(ui)
        ui.main_layout.addWidget(log_widget)
    
    def build_truck_basic_section(self, ui) -> QGroupBox:
        """构建货车基础信息区域（使用独立字段名，支持拖拽）"""
        from apps.etc_apply.ui.rtx.ui_component import DraggableGroupBox
        from apps.etc_apply.ui.rtx.ui_events import ui_events
        
        basic_group = DraggableGroupBox("基础信息 (支持拖拽文件自动填充)")
        basic_layout = QGridLayout()
        basic_layout.setSpacing(10)
        basic_layout.setColumnStretch(1, 1)
        
        # 货车专用的基础字段（使用独立前缀）
        basic_fields = [
            ("truck_name", "持卡人姓名", "", True),
            ("truck_id_code", "身份证号", "", True),
            ("truck_phone", "手机号", "", True),
            ("truck_bank_no", "银行卡号", "", True),
            ("truck_bank_name", "银行名称", "", True)
        ]
        
        row = 0
        for field_name, label, default_value, required in basic_fields:
            # 创建标签
            label_widget = QLabel(label + ("*" if required else ""))
            
            # 创建输入控件
            input_widget = QLineEdit()
            input_widget.setAcceptDrops(False)  # 禁用拖拽，避免与父组件冲突
            if default_value:
                input_widget.setText(default_value)
            
            # 存储到inputs字典（使用货车专用字段名）
            ui.inputs[field_name] = input_widget
            
            # 添加到布局
            basic_layout.addWidget(label_widget, row, 0)
            basic_layout.addWidget(input_widget, row, 1)
            row += 1
        
        # 添加保存五要素按钮（货车专用）
        ui.truck_save_four_elements_btn = QPushButton("保存五要素")
        ui.truck_save_four_elements_btn.setStyleSheet(ui_styles.get_button_style())
        basic_layout.addWidget(ui.truck_save_four_elements_btn, row, 1)
        
        basic_group.setLayout(basic_layout)
        
        # 绑定拖拽信号
        basic_group.file_dropped.connect(lambda file_path: ui_events.handle_drag_drop(ui, file_path))
        
        return basic_group
    
    def build_truck_vehicle_section(self, ui) -> QGroupBox:
        """构建货车车辆信息区域（复用+扩展客车字段）"""
        vehicle_group = QGroupBox("车辆信息")
        vehicle_layout = QGridLayout()
        vehicle_layout.setSpacing(10)
        vehicle_layout.setColumnStretch(1, 1)
        
        # 复用客车的车牌字段
        row = 0
        
        # 车牌省份（使用默认样式，与客车一致，添加选择按钮）
        province_label = QLabel("车牌省份*")
        ui.truck_plate_province_edit = QLineEdit()
        ui.truck_plate_province_edit.setText("苏")
        ui.truck_plate_province_edit.setPlaceholderText("请选择省份")
        ui.truck_plate_province_edit.setAcceptDrops(False)  # 禁用拖拽
        ui.truck_select_province_btn = QPushButton("选择")
        ui.truck_select_province_btn.setStyleSheet(ui_styles.get_button_style())
        ui.inputs['plate_province'] = ui.truck_plate_province_edit
        
        vehicle_layout.addWidget(province_label, row, 0)
        vehicle_layout.addWidget(ui.truck_plate_province_edit, row, 1)
        vehicle_layout.addWidget(ui.truck_select_province_btn, row, 2)
        row += 1
        
        # 车牌字母（使用默认样式，与客车一致，添加选择按钮）
        letter_label = QLabel("车牌字母*")
        ui.truck_plate_letter_edit = QLineEdit()
        ui.truck_plate_letter_edit.setText("Z")
        ui.truck_plate_letter_edit.setPlaceholderText("请选择字母")
        ui.truck_plate_letter_edit.setAcceptDrops(False)  # 禁用拖拽
        ui.truck_select_letter_btn = QPushButton("选择字母")
        ui.truck_select_letter_btn.setStyleSheet(ui_styles.get_button_style())
        ui.inputs['plate_letter'] = ui.truck_plate_letter_edit
        
        vehicle_layout.addWidget(letter_label, row, 0)
        vehicle_layout.addWidget(ui.truck_plate_letter_edit, row, 1)
        vehicle_layout.addWidget(ui.truck_select_letter_btn, row, 2)
        row += 1
        
        # 车牌号码（使用默认样式，与客车一致，添加随机按钮）
        number_label = QLabel("车牌号码*")
        ui.truck_plate_number_edit = QLineEdit()
        ui.truck_plate_number_edit.setText("72HD7")
        ui.truck_plate_number_edit.setPlaceholderText("请输入车牌号码")
        ui.truck_plate_number_edit.setAcceptDrops(False)  # 禁用拖拽
        ui.truck_random_plate_btn = QPushButton("随机")
        ui.truck_random_plate_btn.setStyleSheet(ui_styles.get_button_style())
        ui.inputs['plate_number'] = ui.truck_plate_number_edit
        
        vehicle_layout.addWidget(number_label, row, 0)
        vehicle_layout.addWidget(ui.truck_plate_number_edit, row, 1)
        vehicle_layout.addWidget(ui.truck_random_plate_btn, row, 2)
        row += 1
        
        # 车牌颜色（货车固定为黄色，使用默认样式）
        color_label = QLabel("车牌颜色")
        ui.truck_plate_color_combo = QComboBox()
        ui.truck_plate_color_combo.addItems(["黄色"])
        ui.truck_plate_color_combo.setCurrentText("黄色")
        ui.truck_plate_color_combo.setEnabled(False)  # 货车固定黄色，不可修改
        
        vehicle_layout.addWidget(color_label, row, 0)
        vehicle_layout.addWidget(ui.truck_plate_color_combo, row, 1)
        row += 1
        
        # VIN码（复用客车字段，使用默认样式，添加自动获取按钮）
        vin_label = QLabel("VIN码*")
        ui.truck_vin_edit = QLineEdit()
        ui.truck_vin_edit.setPlaceholderText("请输入VIN码")
        ui.truck_vin_edit.setAcceptDrops(False)  # 禁用拖拽
        ui.truck_get_vin_btn = QPushButton("自动获取VIN")
        ui.truck_get_vin_btn.setStyleSheet(ui_styles.get_button_style())
        ui.inputs['vin'] = ui.truck_vin_edit
        
        vehicle_layout.addWidget(vin_label, row, 0)
        vehicle_layout.addWidget(ui.truck_vin_edit, row, 1)
        vehicle_layout.addWidget(ui.truck_get_vin_btn, row, 2)
        row += 1
        
        # 车辆型号
        model_label = QLabel("车辆型号*")
        ui.truck_model_edit = QLineEdit()
        ui.truck_model_edit.setPlaceholderText("请输入车辆型号")
        ui.truck_model_edit.setText("EQ1180GZ5DJ1")  # 默认货车型号
        ui.truck_model_edit.setAcceptDrops(False)
        ui.inputs['model'] = ui.truck_model_edit
        
        vehicle_layout.addWidget(model_label, row, 0)
        vehicle_layout.addWidget(ui.truck_model_edit, row, 1)
        row += 1
        
        # 车辆类型（下拉框）
        car_type_label = QLabel("车辆类型*")
        ui.truck_car_type_combo = QComboBox()
        truck_types = [
            "货车", "重型货车", "中型货车", "轻型货车", "微型货车",
            "厢式货车", "罐式货车", "平板货车", "自卸货车", "牵引车",
            "半挂车", "全挂车", "专用货车", "危险品运输车", "冷藏车"
        ]
        ui.truck_car_type_combo.addItems(truck_types)
        ui.truck_car_type_combo.setCurrentText("货车")
        ui.inputs['car_type'] = ui.truck_car_type_combo
        
        vehicle_layout.addWidget(car_type_label, row, 0)
        vehicle_layout.addWidget(ui.truck_car_type_combo, row, 1)
        row += 1
        
        # 注册日期
        register_date_label = QLabel("注册日期*")
        ui.truck_register_date_edit = QLineEdit()
        ui.truck_register_date_edit.setPlaceholderText("格式：YYYYMMDD")
        ui.truck_register_date_edit.setText("20200515")  # 默认注册日期（修复格式）
        ui.truck_register_date_edit.setAcceptDrops(False)
        ui.inputs['register_date'] = ui.truck_register_date_edit
        
        vehicle_layout.addWidget(register_date_label, row, 0)
        vehicle_layout.addWidget(ui.truck_register_date_edit, row, 1)
        row += 1
        
        # 发证日期
        issue_date_label = QLabel("发证日期*")
        ui.truck_issue_date_edit = QLineEdit()
        ui.truck_issue_date_edit.setPlaceholderText("格式：YYYYMMDD")
        ui.truck_issue_date_edit.setText("20200520")  # 默认发证日期（修复格式）
        ui.truck_issue_date_edit.setAcceptDrops(False)
        ui.inputs['issue_date'] = ui.truck_issue_date_edit
        
        vehicle_layout.addWidget(issue_date_label, row, 0)
        vehicle_layout.addWidget(ui.truck_issue_date_edit, row, 1)
        row += 1
        
        # 发动机号
        engine_no_label = QLabel("发动机号*")
        ui.truck_engine_no_edit = QLineEdit()
        ui.truck_engine_no_edit.setPlaceholderText("请输入发动机号")
        ui.truck_engine_no_edit.setText("4DX23-140E5A")  # 默认发动机号
        ui.truck_engine_no_edit.setAcceptDrops(False)
        ui.inputs['engine_no'] = ui.truck_engine_no_edit
        
        vehicle_layout.addWidget(engine_no_label, row, 0)
        vehicle_layout.addWidget(ui.truck_engine_no_edit, row, 1)
        row += 1
        
        vehicle_group.setLayout(vehicle_layout)
        return vehicle_group
    
    def build_truck_specific_section(self, ui) -> QGroupBox:
        """构建货车专用信息区域"""
        specific_group = QGroupBox("货车专用信息")
        specific_layout = QGridLayout()
        specific_layout.setSpacing(10)
        specific_layout.setColumnStretch(1, 1)
        
        # 货车专用字段
        truck_specific_fields = [
            ("vehicle_axles", "车轴数", True, "2"),
            ("vehicle_wheels", "车轮数", True, "4"),
            ("total_mass", "总质量(kg)", True, "18000"),
            ("unladen_mass", "整备质量(kg)", True, "7500"),
            ("approved_count", "核定载人数", True, "3"),
            ("weight_limits", "载质量(kg)", True, "10500"),
            ("length", "长(mm)", True, "8995"),
            ("width", "宽(mm)", True, "2496"),
            ("height", "高(mm)", True, "3800"),
            ("urgent_contact", "紧急联系人", False, "张三"),
            ("urgent_phone", "紧急联系电话", False, "13800138000"),
            ("effective_date", "身份证有效期", False, "20200101-20300101"),
            ("id_authority", "发证机关", False, "XX市公安局"),
            ("id_address", "身份证地址", False, ""),
        ]
        
        row = 0
        for field_info in truck_specific_fields:
            field_name = field_info[0]
            label = field_info[1]
            required = field_info[2]
            default_value = field_info[3] if len(field_info) > 3 else ""
            
            # 使用默认样式，与客车一致
            field_label = QLabel(label + ("*" if required else ""))
            field_edit = QLineEdit()
            if default_value:
                field_edit.setText(default_value)
            ui.inputs[field_name] = field_edit
            
            specific_layout.addWidget(field_label, row, 0)
            specific_layout.addWidget(field_edit, row, 1)
            row += 1
        
        specific_group.setLayout(specific_layout)
        
        # 隐藏货车专用信息区域
        specific_group.setVisible(False)
        specific_group.setMaximumHeight(0)  # 设置高度为0，完全隐藏
        
        return specific_group
    
    def build_passenger_product_section(self, ui) -> QGroupBox:
        """构建客车产品信息区域"""
        product_group = QGroupBox("产品信息")
        product_layout = QGridLayout()
        product_layout.setSpacing(10)
        product_layout.setColumnStretch(1, 1)
        
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
        
        product_group.setLayout(product_layout)
        return product_group
    
    def build_product_section(self, ui) -> QGroupBox:
        """构建车辆信息区域（移除产品选择）"""
        vehicle_group = QGroupBox("车辆信息")
        vehicle_layout = QGridLayout()
        vehicle_layout.setSpacing(10)
        vehicle_layout.setColumnStretch(1, 1)
        
        # 车牌省份
        province_label = QLabel("车牌省份:")
        province_label.setStyleSheet(ui_styles.get_label_style())
        ui.plate_province_edit = QLineEdit()
        ui.plate_province_edit.setPlaceholderText("请选择省份")
        ui.plate_province_edit.setAcceptDrops(False)  # 禁用拖拽
        ui.select_province_btn = QPushButton("选择")
        ui.select_province_btn.setStyleSheet(ui_styles.get_button_style())
        
        vehicle_layout.addWidget(province_label, 0, 0)
        vehicle_layout.addWidget(ui.plate_province_edit, 0, 1)
        vehicle_layout.addWidget(ui.select_province_btn, 0, 2)
        
        # 车牌字母
        letter_label = QLabel("车牌字母:")
        letter_label.setStyleSheet(ui_styles.get_label_style())
        ui.plate_letter_edit = QLineEdit()
        ui.plate_letter_edit.setPlaceholderText("请选择字母")
        ui.plate_letter_edit.setAcceptDrops(False)  # 禁用拖拽
        ui.select_letter_btn = QPushButton("选择字母")
        ui.select_letter_btn.setStyleSheet(ui_styles.get_button_style())
        
        vehicle_layout.addWidget(letter_label, 1, 0)
        vehicle_layout.addWidget(ui.plate_letter_edit, 1, 1)
        vehicle_layout.addWidget(ui.select_letter_btn, 1, 2)
        
        # 车牌号码
        number_label = QLabel("车牌号码:")
        number_label.setStyleSheet(ui_styles.get_label_style())
        ui.plate_number_edit = QLineEdit()
        ui.plate_number_edit.setPlaceholderText("请输入车牌号码")
        ui.plate_number_edit.setAcceptDrops(False)  # 禁用拖拽
        ui.random_plate_btn = QPushButton("随机")
        ui.random_plate_btn.setStyleSheet(ui_styles.get_button_style())
        
        vehicle_layout.addWidget(number_label, 2, 0)
        vehicle_layout.addWidget(ui.plate_number_edit, 2, 1)
        vehicle_layout.addWidget(ui.random_plate_btn, 2, 2)
        
        # 车牌颜色
        color_label = QLabel("车牌颜色:")
        color_label.setStyleSheet(ui_styles.get_label_style())
        ui.plate_color_combo = QComboBox()
        # 修复车牌颜色数据获取
        try:
            ui.plate_color_combo.addItems(ui_styles.get_plate_colors())
        except Exception as e:
            # 如果获取失败，使用默认值
            ui.plate_color_combo.addItems(["蓝色", "黄色", "绿色", "白色", "黑色"])
        ui.plate_color_combo.setCurrentText("蓝色")
        ui.plate_color_combo.setAcceptDrops(False)  # 禁用拖拽
        
        vehicle_layout.addWidget(color_label, 3, 0)
        vehicle_layout.addWidget(ui.plate_color_combo, 3, 1)
        
        # VIN码
        vin_label = QLabel("VIN码:")
        vin_label.setStyleSheet(ui_styles.get_label_style())
        ui.vin_edit = QLineEdit()
        ui.vin_edit.setPlaceholderText("请输入VIN码")
        ui.vin_edit.setAcceptDrops(False)  # 禁用拖拽
        ui.get_vin_btn = QPushButton("自动获取VIN")
        ui.get_vin_btn.setStyleSheet(ui_styles.get_button_style())
        
        vehicle_layout.addWidget(vin_label, 4, 0)
        vehicle_layout.addWidget(ui.vin_edit, 4, 1)
        vehicle_layout.addWidget(ui.get_vin_btn, 4, 2)
        
        vehicle_group.setLayout(vehicle_layout)
        return vehicle_group
    
    def build_form_section(self, ui) -> QGroupBox:
        """构建五要素信息区域（支持拖拽）"""
        from apps.etc_apply.ui.rtx.ui_component import DraggableGroupBox
        from apps.etc_apply.ui.rtx.ui_events import ui_events  # 修复未定义异常
        form_group = DraggableGroupBox("五要素信息 (支持拖拽文件自动填充)")
        form_layout = QGridLayout()
        form_layout.setSpacing(10)  # 与车辆信息区域保持相同的间距
        
        # 添加五要素字段
        five_elements_fields = [
            ("姓名", "name", "", True),
            ("身份证", "id_code", "", True),
            ("手机号", "phone", "", True),
            ("银行卡号", "bank_no", "", True),
            ("银行名称", "bank_name", "", True)
        ]
        
        for i, (label, field_name, default_value, is_required) in enumerate(five_elements_fields):
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
        ui.save_four_elements_btn = QPushButton("保存五要素")
        ui.save_four_elements_btn.setStyleSheet(ui_styles.get_button_style())
        form_layout.addWidget(ui.save_four_elements_btn, len(five_elements_fields), 1)
        
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