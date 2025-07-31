# -*- coding: utf-8 -*-
"""
UI事件处理 - 统一管理所有UI事件绑定和处理
"""
import threading
from typing import Dict, Any, Callable
from PyQt5.QtWidgets import QMessageBox
from common.plate_util import random_plate_number
from common.vin_util import get_next_vin
from apps.etc_apply.ui.rtx.ui_component import ProvinceDialog, ProductSelectDialog, PlateLetterDialog
from apps.etc_apply.ui.rtx.ui_utils import ui_parser
from apps.etc_apply.services.rtx.log_service import LogService
from apps.etc_apply.ui.rtx.ui_core import ui_core


class UIEventManager:
    """UI事件管理器 - 统一管理所有UI事件处理"""
    
    def __init__(self):
        self.log_service = LogService("ui_event")
    
    # ==================== 事件处理方法 ====================
    
    def handle_select_province(self, ui) -> None:
        """处理省份选择事件"""
        try:
            current_abbr = ui.plate_province_edit.text().strip()[:1]
            dlg = ProvinceDialog(selected_province=current_abbr)
            if dlg.exec_() == dlg.Accepted:
                selected_province = dlg.get_selected_province()
                ui.plate_province_edit.setText(selected_province)
                self.log_service.info(f"选择省份: {selected_province}")
        except Exception as e:
            self.log_service.error(f"省份选择失败: {e}")
            QMessageBox.critical(ui, "错误", f"省份选择失败: {e}")
    
    def handle_select_plate_letter(self, ui) -> None:
        """处理车牌字母选择事件"""
        try:
            # 总是默认选择Z，忽略输入框中的内容
            current_letter = 'Z'
            print(f"[DEBUG] 对话框打开时传递的字母: {current_letter}")
            dlg = PlateLetterDialog(selected_letter=current_letter)
            if dlg.exec_() == dlg.Accepted:
                selected_letter = dlg.get_selected_letter()
                # 确保selected_letter不为None
                if selected_letter is None:
                    selected_letter = 'Z'
                ui.plate_letter_edit.setText(selected_letter)
                self.log_service.info(f"选择车牌字母: {selected_letter}")
        except Exception as e:
            self.log_service.error(f"车牌字母选择失败: {e}")
            QMessageBox.critical(ui, "错误", f"车牌字母选择失败: {e}")
    
    def handle_random_plate_number(self, ui) -> None:
        """处理随机车牌号码生成事件"""
        try:
            plate_number = random_plate_number()
            ui.plate_number_edit.setText(plate_number)
            self.log_service.info(f"生成随机车牌号码: {plate_number}")
        except Exception as e:
            self.log_service.error(f"随机车牌号码生成失败: {e}")
            QMessageBox.critical(ui, "错误", f"随机车牌号码生成失败: {e}")
    
    def handle_get_vin(self, ui) -> None:
        """处理VIN码获取事件"""
        try:
            if not hasattr(ui, 'vin_index'):
                ui.vin_index = 0
            vin, ui.vin_index = get_next_vin(ui.vin_index)
            ui.vin_edit.setText(vin)
            self.log_service.info(f"自动获取VIN: {vin}")
            if hasattr(ui, 'log_text'):
                ui.log_text.append(f"已自动获取VIN: {vin}")
        except Exception as e:
            self.log_service.error(f"VIN码获取失败: {e}")
            QMessageBox.critical(ui, "错误", f"VIN码获取失败: {e}")
    
    def handle_save_four_elements(self, ui) -> None:
        """处理保存四要素按钮点击事件"""
        try:
            from PyQt5.QtWidgets import QFileDialog
            
            # 收集四要素数据
            four_elements_data = {}
            for field_name, input_widget in ui.inputs.items():
                value = input_widget.text().strip()
                if value:  # 只保存非空值
                    four_elements_data[field_name] = value
            
            if not four_elements_data:
                QMessageBox.warning(ui, "警告", "请先填写四要素信息！")
                return
            
            # 弹出文件保存对话框
            file_path, _ = QFileDialog.getSaveFileName(
                ui,
                "保存四要素文件",
                "四要素信息.txt",
                "文本文件 (*.txt);;所有文件 (*.*)"
            )
            
            if file_path:
                # 保存到文件
                with open(file_path, 'w', encoding='utf-8') as f:
                    for field_name, value in four_elements_data.items():
                        # 将英文字段名转换为中文显示
                        field_mapping = {
                            'name': '姓名',
                            'id_code': '身份证', 
                            'phone': '手机号',
                            'bank_no': '银行卡号'
                        }
                        chinese_name = field_mapping.get(field_name, field_name)
                        f.write(f"{chinese_name}: {value}\n")
                
                self.log_service.info(f"四要素信息已保存到: {file_path}")
                QMessageBox.information(ui, "成功", f"四要素信息已保存到:\n{file_path}")
            else:
                self.log_service.info("用户取消了保存操作")
                
        except Exception as e:
            self.log_service.error(f"保存四要素失败: {e}")
            QMessageBox.critical(ui, "错误", f"保存失败: {str(e)}")
    
    def handle_select_product(self, ui) -> None:
        """处理产品选择事件"""
        try:
            dlg = ProductSelectDialog(ui)
            if dlg.exec_() == dlg.Accepted and dlg.selected_product:
                selected_product = dlg.selected_product
                ui.product_edit.setText(selected_product.get('product_name', ''))
                ui.selected_product = selected_product
                
                product_id = selected_product.get('product_id')
                product_name = selected_product.get('product_name')
                operator_code = selected_product.get('operator_code')
                
                self.log_service.info(f"选择产品: {product_name} (ID: {product_id}, 运营商: {operator_code})")
                
                if hasattr(ui, 'log_text'):
                    ui.log_text.append(f"已选择产品: {product_name} (ID: {product_id}, 运营商: {operator_code})")
        except Exception as e:
            self.log_service.error(f"产品选择失败: {e}")
            QMessageBox.critical(ui, "错误", f"产品选择失败: {e}")
    
    def handle_apply(self, ui) -> None:
        """处理ETC申办事件"""
        try:
            # 先验证表单数据
            if not ui_core.validate_ui_form(ui):
                return
            
            # 设置处理中状态
            ui_core.set_processing_state(ui)
            
            from apps.etc_apply.services.rtx.data_service import DataService
            from apps.etc_apply.services.rtx.etc_service import start_etc_apply_flow
            
            params = DataService.build_apply_params_from_ui(ui)
            self.log_service.info("开始ETC申办流程")
            start_etc_apply_flow(params, ui)
            
        except Exception as e:
            self.log_service.error(f"ETC申办失败: {e}")
            ui_core.set_error_state(ui)
            QMessageBox.critical(ui, "参数错误", f"参数构建失败: {e}")
    
    def handle_drag_drop(self, ui, file_path: str) -> None:
        """处理文件拖拽事件"""
        print(f"拖拽事件处理函数被调用，文件路径: {file_path}")
        try:
            # 验证文件路径
            if not ui_core.validate_file_path(file_path):
                print("文件路径验证失败")
                ui_core.show_validation_error(ui, "文件错误", "文件不存在！")
                return
            
            # 验证文件扩展名
            if not ui_core.validate_file_extension(file_path):
                print("文件扩展名验证失败")
                ui_core.show_validation_error(ui, "文件格式错误", "只支持TXT、CSV、JSON格式的文件！")
                return
            
            print("开始解析文件")
            # 解析四要素文件
            elements = ui_parser.parse_file(file_path)
            print(f"解析结果: {elements}")
            
            if not elements:
                print("文件解析失败")
                ui_core.show_validation_error(ui, "解析失败", "未能从文件中解析出四要素信息！")
                return
            
            # 字段名映射：中文字段名 -> 英文字段名
            field_mapping = {
                '姓名': 'name',
                '身份证': 'id_code', 
                '手机号': 'phone',
                '银行卡号': 'bank_no',
                'name': 'name',
                'id_code': 'id_code',
                'phone': 'phone', 
                'bank_no': 'bank_no'
            }
            
            # 填充四要素字段
            filled_count = 0
            print(f"UI输入框: {list(ui.inputs.keys())}")
            for chinese_key, value in elements.items():
                # 查找对应的英文字段名
                english_key = field_mapping.get(chinese_key)
                print(f"处理字段: {chinese_key} -> {english_key}")
                if english_key and english_key in ui.inputs:
                    ui.inputs[english_key].setText(value)
                    filled_count += 1
                    self.log_service.info(f"填充字段 {chinese_key} -> {english_key}: {value}")
                    print(f"成功填充字段: {chinese_key} -> {english_key}: {value}")
                else:
                    print(f"字段映射失败: {chinese_key} -> {english_key}")
            
            if filled_count > 0:
                print(f"成功填充了 {filled_count} 个字段")
                self.log_service.info(f"从文件 {file_path} 中自动填充了 {filled_count} 个四要素字段")
                
                # 构建解析内容显示
                parsed_content = "解析内容：\n"
                for chinese_key, value in elements.items():
                    english_key = field_mapping.get(chinese_key)
                    if english_key and english_key in ui.inputs:
                        parsed_content += f"{chinese_key}: {value}\n"
                
                success_message = f"已从文件 {file_path} 中自动填充 {filled_count} 个四要素字段！\n\n{parsed_content}"
                ui_core.show_validation_success(ui, "成功", success_message)
            else:
                print("没有填充任何字段")
                ui_core.show_validation_error(ui, "填充失败", "未能识别文件中的四要素字段！")
            
        except Exception as e:
            print(f"拖拽处理异常: {e}")
            self.log_service.error(f"文件拖拽处理失败: {e}")
            QMessageBox.critical(ui, "错误", f"解析文件失败: {str(e)}")
    
    def collect_form_data(self, inputs: Dict[str, Any]) -> Dict[str, str]:
        """收集表单数据"""
        return {k: w.text().strip() for k, w in inputs.items()}
    
    # ==================== 事件绑定方法 ====================
    
    def bind_all_signals_and_shortcuts(self, ui) -> None:
        """绑定所有信号和快捷键"""
        try:
            # 绑定按钮点击事件
            if hasattr(ui, 'select_province_btn'):
                ui.select_province_btn.clicked.connect(lambda: self.handle_select_province(ui))
            
            if hasattr(ui, 'select_letter_btn'):
                ui.select_letter_btn.clicked.connect(lambda: self.handle_select_plate_letter(ui))
            
            if hasattr(ui, 'random_plate_btn'):
                ui.random_plate_btn.clicked.connect(lambda: self.handle_random_plate_number(ui))
            
            # 绑定获取VIN按钮事件
            if hasattr(ui, 'get_vin_btn'):
                ui.get_vin_btn.clicked.connect(lambda: self.handle_get_vin(ui))
            
            # 绑定选择产品按钮事件
            if hasattr(ui, 'select_product_btn'):
                ui.select_product_btn.clicked.connect(lambda: self.handle_select_product(ui))
            
            # 绑定保存四要素按钮事件
            if hasattr(ui, 'save_four_elements_btn'):
                ui.save_four_elements_btn.clicked.connect(lambda: self.handle_save_four_elements(ui))
            
            # 绑定产品选择事件
            if hasattr(ui, 'product_combo'):
                ui.product_combo.currentIndexChanged.connect(lambda: self.handle_select_product(ui))
            
            if hasattr(ui, 'apply_btn'):
                ui.apply_btn.clicked.connect(lambda: self.handle_apply(ui))
            
            # 绑定拖拽事件
            if hasattr(ui, 'drag_group'):
                print("找到拖拽组件，绑定事件")
                ui.drag_group.file_dropped.connect(lambda file_path: self.handle_drag_drop(ui, file_path))
                print("拖拽事件绑定完成")
            else:
                print("未找到拖拽组件")
            
            self.log_service.info("所有信号和快捷键绑定完成")
        except Exception as e:
            self.log_service.error(f"信号绑定失败: {e}")
    
    def bind_specific_event(self, ui, event_type: str, handler: Callable) -> None:
        """绑定特定事件"""
        try:
            if event_type == 'select_province':
                ui.select_province_btn.clicked.connect(handler)
            elif event_type == 'select_letter':
                ui.select_letter_btn.clicked.connect(handler)
            elif event_type == 'random_plate':
                ui.random_plate_btn.clicked.connect(handler)
            elif event_type == 'get_vin':
                ui.get_vin_btn.clicked.connect(handler)
            elif event_type == 'select_product':
                ui.product_combo.currentIndexChanged.connect(handler)
            elif event_type == 'apply':
                ui.apply_btn.clicked.connect(handler)
            elif event_type == 'drag_drop':
                ui.drag_group.file_dropped.connect(handler)
            
            self.log_service.info(f"绑定事件: {event_type}")
        except Exception as e:
            self.log_service.error(f"绑定事件失败: {event_type} - {e}")
    
    # ==================== 线程安全方法 ====================
    
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
                getattr(self, method_name)(ui, *args)
            else:
                # 使用QTimer.singleShot进行线程安全的调用
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(0, lambda: getattr(self, method_name)(ui, *args))
        except Exception as e:
            self.log_service.error(f"safe_call异常: {method_name} - {e}")


def excepthook(type, value, traceback):
    """全局异常处理"""
    print("全局异常:", value)
    QMessageBox.critical(None, "程序异常", f"{value}")


# 创建全局事件管理器实例
ui_events = UIEventManager() 