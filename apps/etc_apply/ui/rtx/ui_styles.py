# -*- coding: utf-8 -*-
"""
UI样式管理器 - 统一管理UI样式和字段配置
"""
from typing import List, Tuple
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QComboBox, QVBoxLayout, QHBoxLayout, QLabel, QGroupBox, QProgressBar, QTextEdit, QScrollArea
from PyQt5.QtCore import Qt
from apps.etc_apply.ui.rtx.ui_core import ui_core


class UIStyleManager:
    """UI样式管理器 - 统一管理UI样式和字段配置"""
    
    def __init__(self):
        self.form_fields = ui_core.get_form_fields()
        self.plate_colors = ui_core.get_plate_colors()
    
    # ==================== 样式生成方法 ====================
    
    def get_warning_label_style(self) -> str:
        """获取警告标签样式"""
        config = ui_core.get_style_config('warning_label')
        return (
            f"QLabel {{ "
            f"color: {config.get('color', 'red')}; "
            f"font-weight: {config.get('font_weight', 'bold')}; "
            f"font-size: {config.get('font_size', '14px')}; "
            f"padding: {config.get('padding', '8px')}; "
            f"background-color: {config.get('background_color', '#fff3cd')}; "
            f"border: {config.get('border', '1px solid #ffeaa7')}; "
            f"border-radius: {config.get('border_radius', '3px')}; "
            f"}}"
        )
    
    def get_label_style(self) -> str:
        """获取标签样式"""
        return (
            "QLabel {"
            "color: #333333;"
            "font-size: 12px;"
            "font-weight: bold;"
            "padding: 5px;"
            "}"
        )
    
    def get_input_style(self) -> str:
        """获取输入框样式"""
        return (
            "QLineEdit {"
            "border: 2px solid #cccccc;"
            "border-radius: 5px;"
            "padding: 4px 8px;"  # 减小上下padding，保持左右padding
            "font-size: 12px;"  # 减小字体大小
            "background-color: white;"
            "min-height: 20px;"  # 设置最小高度
            "}"
            "QLineEdit:focus {"
            "border: 2px solid #409EFF;"
            "}"
        )
    
    def get_draggable_group_normal_style(self) -> str:
        """获取可拖拽组件的正常样式"""
        config = ui_core.get_style_config('draggable_group', 'normal')
        return (
            f"QGroupBox {{ "
            f"border: {config.get('border', '2px solid #cccccc')}; "
            f"border-radius: {config.get('border_radius', '8px')}; "
            f"margin-top: {config.get('margin_top', '5px')}; "  # 减少margin-top
            f"padding-top: {config.get('padding_top', '5px')}; "  # 减少padding-top
            f"font-weight: {config.get('font_weight', 'bold')}; "
            f"}} "
            f"QGroupBox::title {{ "
            f"subcontrol-origin: margin; "
            f"left: 10px; "
            f"padding: 0 5px 0 5px; "
            f"}}"
        )
    
    def get_draggable_group_drag_enter_style(self) -> str:
        """获取可拖拽组件的拖拽进入样式"""
        config = ui_core.get_style_config('draggable_group', 'drag_enter')
        return (
            f"QGroupBox {{ "
            f"border: {config.get('border', '2px solid #4CAF50')}; "
            f"border-radius: {config.get('border_radius', '8px')}; "
            f"margin-top: {config.get('margin_top', '5px')}; "  # 减少margin-top
            f"padding-top: {config.get('padding_top', '5px')}; "  # 减少padding-top
            f"font-weight: {config.get('font_weight', 'bold')}; "
            f"background-color: {config.get('background_color', '#E8F5E8')}; "
            f"}} "
            f"QGroupBox::title {{ "
            f"subcontrol-origin: margin; "
            f"left: 10px; "
            f"padding: 0 5px 0 5px; "
            f"color: {config.get('title_color', '#2E7D32')}; "
            f"}}"
        )
    
    def get_selected_button_style(self) -> str:
        """获取选中按钮样式"""
        return (
            "background-color: #409EFF; "
            "color: white; "
            "font-weight: bold; "
            "border: 2px solid #0057b7;"
        )
    
    def get_normal_button_style(self) -> str:
        """获取普通按钮样式"""
        return ""
    
    def get_progress_bar_style(self) -> str:
        """获取进度条样式"""
        return (
            "QProgressBar {"
            "border: 2px solid grey;"
            "border-radius: 5px;"
            "text-align: center;"
            "}"
            "QProgressBar::chunk {"
            "background-color: #4CAF50;"
            "border-radius: 3px;"
            "}"
        )
    
    def get_dialog_title_style(self) -> str:
        """获取对话框标题样式"""
        return (
            "QLabel {"
            "font-family: 'Microsoft YaHei';"
            "font-size: 14px;"
            "font-weight: bold;"
            "}"
        )
    
    def get_form_field_style(self) -> str:
        """获取表单字段样式"""
        return (
            "QLineEdit {"
            "border: 1px solid #ccc;"
            "border-radius: 3px;"
            "padding: 5px;"
            "}"
            "QLineEdit:focus {"
            "border: 1px solid #409EFF;"
            "}"
        )
    
    def get_button_style(self) -> str:
        """获取按钮样式 - 使用默认样式"""
        return ""
    
    def get_combo_box_style(self) -> str:
        """获取下拉框样式"""
        return (
            "QComboBox {"
            "border: 1px solid #ccc;"
            "border-radius: 3px;"
            "padding: 5px;"
            "background-color: white;"
            "}"
            "QComboBox:focus {"
            "border: 1px solid #409EFF;"
            "}"
            "QComboBox::drop-down {"
            "border: none;"
            "}"
            "QComboBox::down-arrow {"
            "image: none;"
            "border-left: 5px solid transparent;"
            "border-right: 5px solid transparent;"
            "border-top: 5px solid #666;"
            "}"
        )
    
    def get_text_edit_style(self) -> str:
        """获取文本编辑框样式"""
        return (
            "QTextEdit {"
            "border: 1px solid #ccc;"
            "border-radius: 3px;"
            "padding: 5px;"
            "background-color: white;"
            "}"
            "QTextEdit:focus {"
            "border: 1px solid #409EFF;"
            "}"
        )
    
    def get_group_box_style(self) -> str:
        """获取分组框样式"""
        return (
            "QGroupBox {"
            "font-weight: bold;"
            "border: 1px solid #ccc;"
            "border-radius: 5px;"
            "margin-top: 10px;"
            "padding-top: 10px;"
            "}"
            "QGroupBox::title {"
            "subcontrol-origin: margin;"
            "left: 10px;"
            "padding: 0 5px 0 5px;"
            "}"
        )
    
    # ==================== 字段配置方法 ====================
    
    def get_form_fields(self) -> List[Tuple[str, str, str, bool]]:
        """获取表单字段配置"""
        return self.form_fields
    
    def get_plate_colors(self) -> List[str]:
        """获取车牌颜色选项"""
        return self.plate_colors
    
    def get_required_fields(self) -> List[str]:
        """获取必填字段列表"""
        return [field[1] for field in self.form_fields if field[3]]
    
    def get_optional_fields(self) -> List[str]:
        """获取可选字段列表"""
        return [field[1] for field in self.form_fields if not field[3]]
    
    def get_field_label(self, field_name: str) -> str:
        """获取字段标签"""
        for field in self.form_fields:
            if field[1] == field_name:
                return field[0]
        return field_name
    
    def get_field_default(self, field_name: str) -> str:
        """获取字段默认值"""
        for field in self.form_fields:
            if field[1] == field_name:
                return field[2]
        return ""
    
    def is_field_required(self, field_name: str) -> bool:
        """判断字段是否必填"""
        for field in self.form_fields:
            if field[1] == field_name:
                return field[3]
        return False
    
    # ==================== UI构建方法 ====================
    
    def create_form_field(self, field_name: str, parent: QWidget = None) -> QWidget:
        """创建表单字段"""
        label_text = self.get_field_label(field_name)
        default_value = self.get_field_default(field_name)
        is_required = self.is_field_required(field_name)
        
        # 创建容器
        container = QWidget(parent)
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建标签
        label = QLabel(label_text)
        if is_required:
            label.setText(f"{label_text} *")
            label.setStyleSheet("color: red;")
        layout.addWidget(label)
        
        # 创建输入框
        if field_name == 'vehicle_color':
            input_widget = QComboBox()
            input_widget.addItems(self.plate_colors)
            input_widget.setCurrentText(default_value)
        else:
            input_widget = QLineEdit()
            input_widget.setText(default_value)
            input_widget.setPlaceholderText(f"请输入{label_text}")
        
        input_widget.setStyleSheet(self.get_form_field_style())
        layout.addWidget(input_widget)
        
        return container
    
    def create_button(self, text: str, parent: QWidget = None) -> QPushButton:
        """创建按钮"""
        button = QPushButton(text, parent)
        button.setStyleSheet(self.get_button_style())
        return button
    
    def create_progress_bar(self, parent: QWidget = None) -> QProgressBar:
        """创建进度条"""
        progress_bar = QProgressBar(parent)
        progress_bar.setStyleSheet(self.get_progress_bar_style())
        progress_bar.setRange(0, 100)
        progress_bar.setValue(0)
        return progress_bar
    
    def create_text_edit(self, parent: QWidget = None) -> QTextEdit:
        """创建文本编辑框"""
        text_edit = QTextEdit(parent)
        text_edit.setStyleSheet(self.get_text_edit_style())
        text_edit.setReadOnly(True)
        return text_edit
    
    def create_group_box(self, title: str, parent: QWidget = None) -> QGroupBox:
        """创建分组框"""
        group_box = QGroupBox(title, parent)
        group_box.setStyleSheet(self.get_group_box_style())
        return group_box
    
    def create_scroll_area(self, parent: QWidget = None) -> QScrollArea:
        """创建滚动区域"""
        scroll_area = QScrollArea(parent)
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        return scroll_area
    
    def create_label(self, text: str, parent: QWidget = None) -> QLabel:
        """创建标签"""
        label = QLabel(text, parent)
        label.setWordWrap(True)
        return label
    
    def create_warning_label(self, text: str, parent: QWidget = None) -> QLabel:
        """创建警告标签"""
        label = QLabel(text, parent)
        label.setStyleSheet(self.get_warning_label_style())
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignCenter)
        return label
    
    def create_dialog_title(self, text: str, parent: QWidget = None) -> QLabel:
        """创建对话框标题"""
        label = QLabel(text, parent)
        label.setStyleSheet(self.get_dialog_title_style())
        label.setAlignment(Qt.AlignCenter)
        return label
    
    # ==================== 布局方法 ====================
    
    def create_vbox_layout(self) -> QVBoxLayout:
        """创建垂直布局"""
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)
        return layout
    
    def create_hbox_layout(self) -> QHBoxLayout:
        """创建水平布局"""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(0, 0, 0, 0)
        return layout
    
    def create_form_layout(self, fields: List[str], parent: QWidget = None) -> QWidget:
        """创建表单布局"""
        container = QWidget(parent)
        layout = QVBoxLayout(container)
        
        for field_name in fields:
            field_widget = self.create_form_field(field_name, container)
            layout.addWidget(field_widget)
        
        return container
    
    def create_button_layout(self, buttons: List[QPushButton], parent: QWidget = None) -> QWidget:
        """创建按钮布局"""
        container = QWidget(parent)
        layout = QHBoxLayout(container)
        
        for button in buttons:
            layout.addWidget(button)
        
        layout.addStretch()
        return container


# 创建全局样式管理器实例
ui_styles = UIStyleManager() 