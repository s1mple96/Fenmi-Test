# -*- coding: utf-8 -*-
"""
UI核心管理器 - 统一管理UI配置、状态和验证
"""
import json
import os
import re
from typing import Dict, Any, List, Tuple, Optional
from enum import Enum
from PyQt5.QtWidgets import QWidget, QPushButton, QLineEdit, QComboBox, QMessageBox
from apps.etc_apply.services.core_service import CoreService
from apps.etc_apply.services.log_service import LogService


class UIState(Enum):
    """UI状态枚举"""
    INITIAL = "initial"
    LOADING = "loading"
    READY = "ready"
    PROCESSING = "processing"
    SUCCESS = "success"
    ERROR = "error"
    DISABLED = "disabled"


class UICoreManager:
    """UI核心管理器 - 统一管理UI配置、状态和验证"""
    
    def __init__(self):
        self.log_service = LogService("ui_core")
        self._ui_states = {}
        self._component_states = {}
        
        # 从配置文件加载UI配置
        self._load_ui_config()
    
    def _load_ui_config(self):
        """从配置文件加载UI配置"""
        ui_config = CoreService.get_ui_config()
        
        # 对话框配置
        self.DIALOG_CONFIGS = {
            'verify_code': {
                'title': '请输入验证码',
                'size': (320, 120),
                'timer_duration': ui_config.get('verify_code_timer_duration', 60)
            },
            'plate_letter': {
                'title': '选择车牌字母',
                'size': (420, 260),
                'max_cols': 7
            },
            'province': {
                'title': '选择省份',
                'size': (650, 440),
                'hot_provinces': ui_config.get('hot_provinces', ['苏', '桂', '黑', '蒙', '湘', '川'])
            },
            'product': {
                'title': '选择产品',
                'size': (400, 250),
                'warning_text': f'⚠️ 【测试专用渠道手机号】：{CoreService.get_business_config().get("default_verify_code", "13797173255")} 请勿擅自修改系统数据！'
            }
        }
        
        # 样式配置
        self.STYLE_CONFIGS = {
            'warning_label': {
                'color': 'red',
                'font_weight': 'bold',
                'font_size': '14px',
                'padding': '8px',
                'background_color': '#fff3cd',
                'border': '1px solid #ffeaa7',
                'border_radius': '3px'
            },
            'draggable_group': {
                'normal': {
                    'border': '2px solid #cccccc',
                    'border_radius': '8px',
                    'margin_top': '10px',
                    'padding_top': '10px',
                    'font_weight': 'bold'
                },
                'drag_enter': {
                    'border': '2px solid #4CAF50',
                    'border_radius': '8px',
                    'margin_top': '10px',
                    'padding_top': '10px',
                    'font_weight': 'bold',
                    'background_color': '#E8F5E8'
                }
            }
        }
        
        # 表单字段配置
        self.FORM_FIELDS = [
            ("姓名", "name", "", True),
            ("身份证", "id_code", "", True),
            ("手机号", "phone", "", True),
            ("银行卡号", "bank_no", "", True),
            ("车牌省份", "plate_province", ui_config.get('default_province', '苏'), False),
            ("车牌字母", "plate_letter", ui_config.get('default_letter', 'Z'), False),
            ("车牌号码", "plate_number", ui_config.get('default_plate_number', '9T4P0'), False),
            ("VIN码", "vin", "", False),
        ]
        
        # 车牌颜色选项
        vehicle_colors = CoreService.get_vehicle_colors()
        self.PLATE_COLORS = list(vehicle_colors.keys())
        
        # 省份数据
        self.PROVINCE_DATA = [
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
        
        # 字母列表
        self.LETTERS = [chr(i) for i in range(ord('A'), ord('Z')+1)]
    
    # ==================== 配置管理方法 ====================
    
    def get_dialog_config(self, dialog_type: str) -> Dict[str, Any]:
        """获取对话框配置"""
        return self.DIALOG_CONFIGS.get(dialog_type, {})
    
    def get_style_config(self, style_type: str, variant: str = None) -> Dict[str, Any]:
        """获取样式配置"""
        if variant:
            return self.STYLE_CONFIGS.get(style_type, {}).get(variant, {})
        return self.STYLE_CONFIGS.get(style_type, {})
    
    def get_form_fields(self) -> List[Tuple[str, str, str, bool]]:
        """获取表单字段配置"""
        return self.FORM_FIELDS
    
    def get_plate_colors(self) -> List[str]:
        """获取车牌颜色选项"""
        return self.PLATE_COLORS
    
    def get_province_data(self) -> List[Tuple[str, str, str]]:
        """获取省份数据"""
        return self.PROVINCE_DATA
    
    def get_letters(self) -> List[str]:
        """获取字母列表"""
        return self.LETTERS
    
    def get_hot_provinces(self) -> List[str]:
        """获取热门省份"""
        return self.DIALOG_CONFIGS['province']['hot_provinces']
    
    def get_mysql_config(self) -> Dict[str, Any]:
        """获取MySQL配置 - 使用统一的配置服务"""
        return CoreService.get_mysql_config()
    
    def get_selected_product(self) -> Optional[Dict[str, Any]]:
        """获取当前选择的产品"""
        return getattr(self, 'selected_product', None)
    
    def set_selected_product(self, product: Dict[str, Any]) -> None:
        """设置当前选择的产品"""
        self.selected_product = product
    
    # ==================== 状态管理方法 ====================
    
    def set_ui_state(self, ui: QWidget, state: UIState) -> None:
        """设置UI整体状态"""
        self._ui_states[id(ui)] = state
        self.log_service.info(f"UI状态变更: {state.value}")
    
    def get_ui_state(self, ui: QWidget) -> UIState:
        """获取UI整体状态"""
        return self._ui_states.get(id(ui), UIState.INITIAL)
    
    def set_component_state(self, component_id: str, state: UIState) -> None:
        """设置组件状态"""
        self._component_states[component_id] = state
        self.log_service.info(f"组件状态变更: {component_id} -> {state.value}")
    
    def get_component_state(self, component_id: str) -> UIState:
        """获取组件状态"""
        return self._component_states.get(component_id, UIState.INITIAL)
    
    def enable_ui_components(self, ui: QWidget, component_ids: List[str] = None) -> None:
        """启用UI组件"""
        if component_ids is None:
            # 启用所有常见组件
            for attr_name in dir(ui):
                if attr_name.endswith('_btn') or attr_name.endswith('_edit') or attr_name.endswith('_combo'):
                    component = getattr(ui, attr_name, None)
                    if isinstance(component, (QPushButton, QLineEdit, QComboBox)):
                        component.setEnabled(True)
        else:
            # 启用指定组件
            for component_id in component_ids:
                component = getattr(ui, component_id, None)
                if component:
                    component.setEnabled(True)
        
        self.set_ui_state(ui, UIState.READY)
    
    def disable_ui_components(self, ui: QWidget, component_ids: List[str] = None) -> None:
        """禁用UI组件"""
        if component_ids is None:
            # 禁用所有常见组件
            for attr_name in dir(ui):
                if attr_name.endswith('_btn') or attr_name.endswith('_edit') or attr_name.endswith('_combo'):
                    component = getattr(ui, attr_name, None)
                    if isinstance(component, (QPushButton, QLineEdit, QComboBox)):
                        component.setEnabled(False)
        else:
            # 禁用指定组件
            for component_id in component_ids:
                component = getattr(ui, component_id, None)
                if component:
                    component.setEnabled(False)
        
        self.set_ui_state(ui, UIState.DISABLED)
    
    def set_processing_state(self, ui: QWidget) -> None:
        """设置处理中状态"""
        # 禁用所有按钮
        for attr_name in dir(ui):
            if attr_name.endswith('_btn'):
                component = getattr(ui, attr_name, None)
                if isinstance(component, QPushButton):
                    component.setEnabled(False)
        
        self.set_ui_state(ui, UIState.PROCESSING)
    
    def set_success_state(self, ui: QWidget) -> None:
        """设置成功状态"""
        self.set_ui_state(ui, UIState.SUCCESS)
    
    def set_error_state(self, ui: QWidget) -> None:
        """设置错误状态"""
        self.set_ui_state(ui, UIState.ERROR)
    
    def update_progress(self, ui: QWidget, percent: int, message: str) -> None:
        """更新进度条"""
        if hasattr(ui, 'progress_bar') and hasattr(ui, 'progress_label'):
            ui.progress_bar.setValue(percent)
            ui.progress_label.setText(f"进度：{message}")
    
    def append_log(self, ui: QWidget, message: str) -> None:
        """添加日志信息"""
        if hasattr(ui, 'log_text'):
            ui.log_text.append(message)
            # 滚动到底部
            cursor = ui.log_text.textCursor()
            cursor.movePosition(cursor.End)
            ui.log_text.setTextCursor(cursor)
    
    def clear_log(self, ui: QWidget) -> None:
        """清空日志"""
        if hasattr(ui, 'log_text'):
            ui.log_text.clear()
    
    def set_button_text(self, ui: QWidget, button_name: str, text: str) -> None:
        """设置按钮文本"""
        button = getattr(ui, button_name, None)
        if isinstance(button, QPushButton):
            button.setText(text)
    
    def set_input_value(self, ui: QWidget, input_name: str, value: str) -> None:
        """设置输入框值"""
        input_widget = getattr(ui, input_name, None)
        if isinstance(input_widget, QLineEdit):
            input_widget.setText(value)
    
    def get_input_value(self, ui: QWidget, input_name: str) -> str:
        """获取输入框值"""
        input_widget = getattr(ui, input_name, None)
        if isinstance(input_widget, QLineEdit):
            return input_widget.text().strip()
        return ""
    
    def set_combo_value(self, ui: QWidget, combo_name: str, value: str) -> None:
        """设置下拉框值"""
        combo = getattr(ui, combo_name, None)
        if isinstance(combo, QComboBox):
            index = combo.findText(value)
            if index >= 0:
                combo.setCurrentIndex(index)
    
    def get_combo_value(self, ui: QWidget, combo_name: str) -> str:
        """获取下拉框值"""
        combo = getattr(ui, combo_name, None)
        if isinstance(combo, QComboBox):
            return combo.currentText()
        return ""
    
    def reset_ui_state(self, ui: QWidget) -> None:
        """重置UI状态"""
        # 清空所有输入框
        for attr_name in dir(ui):
            if attr_name.endswith('_edit'):
                component = getattr(ui, attr_name, None)
                if isinstance(component, QLineEdit):
                    component.clear()
        
        # 重置进度条
        if hasattr(ui, 'progress_bar'):
            ui.progress_bar.setValue(0)
        
        if hasattr(ui, 'progress_label'):
            ui.progress_label.setText("进度：等待操作")
        
        # 清空日志
        self.clear_log(ui)
        
        # 启用所有组件
        self.enable_ui_components(ui)
        
        self.set_ui_state(ui, UIState.INITIAL)
    
    def save_ui_state(self, ui: QWidget) -> Dict[str, Any]:
        """保存UI状态"""
        state = {
            'ui_state': self.get_ui_state(ui).value,
            'inputs': {},
            'progress': 0,
            'log_count': 0
        }
        
        # 保存输入框值
        for attr_name in dir(ui):
            if attr_name.endswith('_edit'):
                component = getattr(ui, attr_name, None)
                if isinstance(component, QLineEdit):
                    state['inputs'][attr_name] = component.text().strip()
        
        # 保存进度
        if hasattr(ui, 'progress_bar'):
            state['progress'] = ui.progress_bar.value()
        
        # 保存日志行数
        if hasattr(ui, 'log_text'):
            state['log_count'] = ui.log_text.document().lineCount()
        
        return state
    
    def restore_ui_state(self, ui: QWidget, state: Dict[str, Any]) -> None:
        """恢复UI状态"""
        # 恢复输入框值
        for input_name, value in state.get('inputs', {}).items():
            self.set_input_value(ui, input_name, value)
        
        # 恢复进度
        if 'progress' in state and hasattr(ui, 'progress_bar'):
            ui.progress_bar.setValue(state['progress'])
        
        # 恢复UI状态
        if 'ui_state' in state:
            try:
                ui_state = UIState(state['ui_state'])
                self.set_ui_state(ui, ui_state)
            except ValueError:
                self.set_ui_state(ui, UIState.INITIAL)
    
    # ==================== 验证处理方法 ====================
    
    def validate_required_fields(self, ui, required_fields: List[str]) -> bool:
        """验证必填字段"""
        missing_fields = []
        for field in required_fields:
            if field in ui.inputs:
                value = ui.inputs[field].text().strip()
                if not value:
                    missing_fields.append(field)
        
        if missing_fields:
            field_names = ", ".join(missing_fields)
            error_msg = f"以下字段为必填项：{field_names}"
            self.log_service.error(f"必填字段验证失败: {missing_fields}")
            QMessageBox.warning(ui, "验证失败", error_msg)
            return False
        
        return True
    
    def validate_car_number(self, car_number: str) -> bool:
        """验证车牌号码格式"""
        if not car_number:
            return False
        
        # 使用配置文件中的验证规则
        validation_config = CoreService.get_validation_config()
        pattern = validation_config.get('car_number_pattern', r'^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵青藏川宁琼粤港澳台][A-Z][A-Z0-9]{5}$')
        return bool(re.match(pattern, car_number))
    
    def validate_id_code(self, id_code: str) -> bool:
        """验证身份证号码格式"""
        if not id_code:
            return False
        
        # 使用配置文件中的验证规则
        validation_config = CoreService.get_validation_config()
        pattern = validation_config.get('id_code_pattern', r'^\d{17}[\dXx]$')
        return bool(re.match(pattern, id_code))
    
    def validate_phone(self, phone: str) -> bool:
        """验证手机号码格式"""
        if not phone:
            return False
        
        # 使用配置文件中的验证规则
        validation_config = CoreService.get_validation_config()
        pattern = validation_config.get('phone_pattern', r'^1[3-9]\d{9}$')
        return bool(re.match(pattern, phone))
    
    def validate_bank_card(self, bank_card: str) -> bool:
        """验证银行卡号格式"""
        if not bank_card:
            return False
        
        # 使用配置文件中的验证规则
        validation_config = CoreService.get_validation_config()
        pattern = validation_config.get('bank_card_pattern', r'^\d{13,19}$')
        return bool(re.match(pattern, bank_card))
    
    def validate_vin(self, vin: str) -> bool:
        """验证VIN码格式"""
        if not vin:
            return False
        
        # 使用配置文件中的验证规则
        validation_config = CoreService.get_validation_config()
        pattern = validation_config.get('vin_pattern', r'^[A-Z0-9]{17}$')
        return bool(re.match(pattern, vin))
    
    def validate_form_data(self, form_data: Dict[str, str]) -> Tuple[bool, List[str]]:
        """验证表单数据"""
        errors = []
        
        # 验证必填字段
        required_fields = ['name', 'id_code', 'phone', 'bank_no']
        for field in required_fields:
            if field not in form_data or not form_data[field].strip():
                errors.append(f"{field} 为必填项")
        
        # 验证身份证号码
        if 'id_code' in form_data and form_data['id_code'].strip():
            if not self.validate_id_code(form_data['id_code']):
                errors.append("身份证号码格式不正确")
        
        # 验证手机号码
        if 'phone' in form_data and form_data['phone'].strip():
            if not self.validate_phone(form_data['phone']):
                errors.append("手机号码格式不正确")
        
        # 验证银行卡号
        if 'bank_no' in form_data and form_data['bank_no'].strip():
            if not self.validate_bank_card(form_data['bank_no']):
                errors.append("银行卡号格式不正确")
        
        # 验证车牌号码（如果填写了省份、字母、号码）
        if all(key in form_data for key in ['plate_province', 'plate_letter', 'plate_number']):
            province = form_data.get('plate_province', '').strip()
            letter = form_data.get('plate_letter', '').strip()
            number = form_data.get('plate_number', '').strip()
            
            if province and letter and number:
                car_number = province + letter + number
                if not self.validate_car_number(car_number):
                    errors.append("车牌号码格式不正确")
        
        # 验证VIN码
        if 'vin' in form_data and form_data['vin'].strip():
            if not self.validate_vin(form_data['vin']):
                errors.append("VIN码格式不正确")
        
        return len(errors) == 0, errors
    
    def validate_ui_form(self, ui) -> bool:
        """验证UI表单数据"""
        try:
            # 收集表单数据
            form_data = {}
            for key, widget in ui.inputs.items():
                form_data[key] = widget.text().strip()
            
            # 验证数据
            is_valid, errors = self.validate_form_data(form_data)
            
            if not is_valid:
                error_msg = "\n".join(errors)
                self.log_service.error(f"表单验证失败: {errors}")
                QMessageBox.warning(ui, "验证失败", f"请检查以下问题：\n{error_msg}")
                return False
            
            self.log_service.info("表单验证通过")
            return True
            
        except Exception as e:
            self.log_service.error(f"表单验证异常: {e}")
            QMessageBox.critical(ui, "验证错误", f"表单验证时发生错误: {e}")
            return False
    
    def validate_file_path(self, file_path: str) -> bool:
        """验证文件路径"""
        return os.path.isfile(file_path)
    
    def validate_file_extension(self, file_path: str, allowed_extensions: List[str] = None) -> bool:
        """验证文件扩展名"""
        if allowed_extensions is None:
            ui_config = CoreService.get_ui_config()
            allowed_extensions = ui_config.get('allowed_file_extensions', ['.txt', '.csv', '.json'])
        
        file_ext = os.path.splitext(file_path)[1].lower()
        return file_ext in allowed_extensions
    
    def validate_product_selection(self, selected_product: Optional[Dict[str, Any]]) -> bool:
        """验证产品选择"""
        if not selected_product:
            return False
        
        required_keys = ['product_id', 'product_name', 'operator_code']
        return all(key in selected_product for key in required_keys)
    
    def show_validation_error(self, ui, title: str, message: str) -> None:
        """显示验证错误信息"""
        self.log_service.error(f"验证错误: {title} - {message}")
        QMessageBox.warning(ui, title, message)
    
    def show_validation_success(self, ui, title: str, message: str) -> None:
        """显示验证成功信息"""
        self.log_service.info(f"验证成功: {title} - {message}")
        QMessageBox.information(ui, title, message)


# 创建全局UI核心管理器实例
ui_core = UICoreManager() 