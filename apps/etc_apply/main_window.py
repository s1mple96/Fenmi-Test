import sys  # 导入系统模块，用于程序入口和异常钩子
import os  # 导入操作系统模块

# 添加项目根目录到 Python 路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from PyQt5.QtWidgets import QDialog, QPushButton, QHBoxLayout, QWidget, QVBoxLayout, QTabWidget
from PyQt5.QtCore import pyqtSignal, Qt
from apps.etc_apply.ui.rtx.ui_events import ui_events, excepthook
from apps.etc_apply.ui.rtx.ui_utils import ui_builder

class EtcApplyWidget(QDialog):  # ETC申办主界面类，继承自QWidget
    """
    ETC申办主界面，仅负责UI控件声明、布局、信号绑定、主流程触发。
    所有数据加载、保存、默认值、业务逻辑等全部抽离到ui/worker/utils等专用模块。
    """
    log_signal = pyqtSignal(str)  # 日志信号
    progress_signal = pyqtSignal(int, str)  # 百分比, 消息
    error_signal = pyqtSignal(str, str)  # 错误标题, 错误内容
    apply_submitted = pyqtSignal(dict)  # 申办完成信号

    def __init__(self, parent=None):  # 构造函数
        super().__init__(parent)  # 初始化父类
        self.inputs = {}  # 输入控件字典
        self.current_vehicle_type = "passenger"  # 当前车辆类型
        
        # 先创建Tab容器
        self.create_tab_container()
        
        # 构建完整UI（所有控件和布局）
        ui_builder.build_full_ui(self)
        
        ui_events.bind_all_signals_and_shortcuts(self)  # 绑定所有信号和快捷键
        
        # 设置窗口就绪标志
        self._window_ready = True
        # 绑定日志信号处理
        self.log_signal.connect(self.handle_log_message)
        self.progress_signal.connect(self.handle_progress_message)
        self.error_signal.connect(self.handle_error_message)
        # 已彻底移除help_btn相关代码
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowCloseButtonHint
        )

    def showEvent(self, event):
        super().showEvent(event)
        self._window_ready = True

    def handle_log_message(self, msg):
        """处理日志消息，实现倒序显示"""
        if hasattr(self, 'log_text') and self.log_text:
            current_text = self.log_text.toPlainText()
            if not current_text.endswith(msg):  # 简单去重
                # 在开头插入新日志，并添加换行符
                new_log = f"{msg}\n"
                self.log_text.setPlainText(new_log + current_text)

    def handle_progress_message(self, percent, msg):
        """处理进度消息"""
        if hasattr(self, 'progress_label') and self.progress_label:
            self.progress_label.setText(msg)
        if hasattr(self, 'progress_bar') and self.progress_bar:
            self.progress_bar.setValue(percent)

    def show_api_error(self, api_name, error_message, status_code=None):
        """显示API错误信息的便捷方法"""
        title = f"{api_name} 接口错误"
        
        # 构建简洁的错误内容
        if status_code:
            content = f"接口：{api_name}\n状态码：{status_code}\n错误信息：{error_message}"
        else:
            content = f"接口：{api_name}\n错误信息：{error_message}"
        
        # 发送错误信号到UI（这会触发handle_error_message显示对话框）
        self.error_signal.emit(title, content)
    
    def handle_error_message(self, title, error_content):
        """处理错误消息，在UI中显示详细错误信息"""
        from PyQt5.QtWidgets import QMessageBox, QTextEdit
        from PyQt5.QtCore import Qt
        import os
        
        # 创建详细错误对话框
        error_dialog = QMessageBox(self)
        error_dialog.setWindowTitle(title)
        error_dialog.setIcon(QMessageBox.Critical)
        
        # 设置主要错误信息（如果太长则显示简短版本）
        if len(error_content) > 200:
            # 如果错误内容很长，显示简短版本在主文本中
            lines = error_content.split('\n')
            short_content = lines[0] if lines else error_content[:200] + "..."
            error_dialog.setText(f"操作失败：{short_content}")
        else:
            error_dialog.setText(f"操作失败：{error_content}")
        
        # 检查错误内容是否已经包含调试信息
        if "📋 API调用详情" in error_content:
            # 如果错误内容已经包含详细的调试信息，直接使用
            detailed_content = error_content
        else:
            # 如果没有详细调试信息，构建基本的详细信息
            detailed_content = error_content
            
            # 检查是否有接口错误的基本信息（通过特定格式识别）
            if "接口错误" in title:
                detailed_content += "\n\n" + "="*50 + "\n"
                detailed_content += "📋 错误详情\n"
                detailed_content += "="*50 + "\n"
                detailed_content += "🔹 这是一个API接口调用错误\n"
                
                # 添加日志文件位置信息
                try:
                    # 获取当前exe所在目录
                    if hasattr(sys, 'frozen') and sys.frozen:
                        # 打包后的exe环境
                        exe_dir = os.path.dirname(sys.executable)
                        log_dir = os.path.join(exe_dir, 'log')
                    else:
                        # 开发环境
                        project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
                        log_dir = os.path.join(project_root, 'log')
                    
                    # 获取今天的日志文件名
                    from datetime import datetime
                    today_log = f"run_{datetime.now().strftime('%Y%m%d')}.log"
                    log_file_path = os.path.join(log_dir, today_log)
                    
                    detailed_content += f"🔹 详细日志文件位置: {log_file_path}\n"
                    if os.path.exists(log_file_path):
                        detailed_content += f"🔹 日志文件状态: 存在 ({os.path.getsize(log_file_path)} 字节)\n"
                    else:
                        detailed_content += f"🔹 日志文件状态: 不存在\n"
                    
                    detailed_content += f"🔹 如需更详细的调试信息，请查看上述日志文件\n"
                except Exception as e:
                    detailed_content += f"🔹 无法确定日志文件位置: {str(e)}\n"
        
        # 始终在详细信息中显示完整内容
        error_dialog.setDetailedText(detailed_content)
        
        # 设置对话框大小，确保能显示足够的信息
        error_dialog.setMinimumSize(500, 300)
        
        # 添加按钮
        error_dialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Close)
        error_dialog.setDefaultButton(QMessageBox.Ok)
        
        # 同时在日志中记录错误
        self.log_signal.emit(f"❌ {title}: {error_content}")
        
        # 显示对话框
        error_dialog.exec_()

    def create_tab_container(self):
        """创建Tab容器"""
        # 创建主布局
        self.main_layout = QVBoxLayout(self)
        
        # 创建Tab widget
        self.tab_widget = QTabWidget()
        
        # 创建客车Tab（默认）
        self.passenger_tab = QWidget()
        self.passenger_layout = QVBoxLayout(self.passenger_tab)
        
        # 创建货车Tab
        self.truck_tab = QWidget()
        self.truck_layout = QVBoxLayout(self.truck_tab)
        
        # 添加Tab页
        self.tab_widget.addTab(self.passenger_tab, "客车")
        self.tab_widget.addTab(self.truck_tab, "货车")
        
        # 绑定Tab切换事件
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # 将Tab widget添加到主布局
        self.main_layout.addWidget(self.tab_widget)
        
        # 设置当前Tab为客车
        self.tab_widget.setCurrentIndex(0)
    
    def on_tab_changed(self, index):
        """Tab切换事件处理"""
        if index == 0:
            self.current_vehicle_type = "passenger"
            self.log_signal.emit("切换到客车模式")
        elif index == 1:
            self.current_vehicle_type = "truck"
            self.log_signal.emit("切换到货车模式")
        
        # 根据车辆类型更新申办按钮文本
        if hasattr(self, 'apply_btn'):
            if self.current_vehicle_type == "truck":
                self.apply_btn.setText("货车申办")
            else:
                self.apply_btn.setText("客车申办")
        
        # 根据车辆类型更新保存按钮文本
        if hasattr(self, 'save_four_elements_btn'):
            if self.current_vehicle_type == "truck":
                self.save_four_elements_btn.setText("保存五要素")
            else:
                self.save_four_elements_btn.setText("保存五要素")
        
        # 货车专用保存按钮
        if hasattr(self, 'truck_save_four_elements_btn'):
            self.truck_save_four_elements_btn.setText("保存五要素")

    def get_current_form_data(self):
        """获取当前Tab的表单数据"""
        form_data = {}
        
        # 根据当前车辆类型收集对应的表单数据
        if self.current_vehicle_type == "passenger":
            # 收集客车表单数据（使用通用字段名）
            passenger_fields = [
                'name_edit', 'id_code_edit', 'phone_edit', 
                'bank_no_edit', 'bank_name_edit',
                'plate_province_edit', 'plate_letter_edit', 
                'plate_number_edit', 'vin_edit'
            ]
            
            for field_name in passenger_fields:
                if hasattr(self, field_name):
                    widget = getattr(self, field_name)
                    if hasattr(widget, 'text'):
                        form_data[field_name.replace('_edit', '')] = widget.text().strip()
                    elif hasattr(widget, 'currentText'):
                        form_data[field_name.replace('_edit', '')] = widget.currentText()
            
            # 收集产品信息
            if hasattr(self, 'product_edit'):
                form_data['product'] = self.product_edit.text().strip()
                
        elif self.current_vehicle_type == "truck":
            # 优先从inputs字典获取拖拽填充的数据
            if hasattr(self, 'inputs') and self.inputs:
                for field_name, widget in self.inputs.items():
                    if hasattr(widget, 'text'):
                        form_data[field_name] = widget.text().strip()
                    elif hasattr(widget, 'currentText'):
                        form_data[field_name] = widget.currentText()
            else:
                # 兼容旧版本，收集货车表单数据
                truck_fields = [
                    'truck_name_edit', 'truck_id_code_edit', 'truck_phone_edit', 
                    'truck_bank_no_edit', 'truck_bank_name_edit',
                    'truck_plate_province_edit', 'truck_plate_letter_edit', 
                    'truck_plate_number_edit', 'truck_vin_edit',
                    'truck_load_weight_edit', 'truck_length_edit', 'truck_width_edit', 'truck_height_edit'
                ]
                
                for field_name in truck_fields:
                    if hasattr(self, field_name):
                        widget = getattr(self, field_name)
                        if hasattr(widget, 'text'):
                            form_data[field_name.replace('_edit', '')] = widget.text().strip()
                        elif hasattr(widget, 'currentText'):
                            form_data[field_name.replace('_edit', '')] = widget.currentText()
                
                # 收集货车特有的下拉框数据
                truck_combo_fields = [
                    'truck_vehicle_color_combo', 'truck_vehicle_type_combo', 
                    'truck_use_purpose_combo', 'truck_axle_count_combo', 'truck_tire_count_combo'
                ]
                
                for field_name in truck_combo_fields:
                    if hasattr(self, field_name):
                        widget = getattr(self, field_name)
                        if hasattr(widget, 'currentText'):
                            form_data[field_name.replace('_combo', '')] = widget.currentText()
                
                # 收集产品信息
                if hasattr(self, 'truck_product_edit'):
                    form_data['product'] = self.truck_product_edit.text().strip()
        
        else:
            # 兼容传统模式，收集所有输入控件的数据
            for field_name, widget in getattr(self, 'inputs', {}).items():
                if hasattr(widget, 'text'):  # QLineEdit
                    form_data[field_name] = widget.text().strip()
                elif hasattr(widget, 'currentText'):  # QComboBox
                    form_data[field_name] = widget.currentText()
                else:
                    form_data[field_name] = str(widget)
        
        # 添加车辆类型标识
        form_data['vehicle_type'] = self.current_vehicle_type
        
        # 如果是货车模式，添加货车特有的默认值
        if self.current_vehicle_type == "truck":
            form_data['plate_color'] = '黄色'  # 货车默认黄色
            form_data['use_purpose'] = '货运'
        
            # 添加选择的货车产品信息
            if hasattr(self, 'selected_truck_product') and self.selected_truck_product:
                form_data['selected_product'] = self.selected_truck_product
                print(f"[DEBUG] 已添加选择的货车产品到表单数据: {self.selected_truck_product.get('NAME')} (ID: {self.selected_truck_product.get('ETCBANK_ID')})")
        
        return form_data

    def start_apply_flow(self):
        """启动申办流程（根据当前车辆类型）"""
        try:
            # 获取当前表单数据
            form_data = self.get_current_form_data()
            
            if self.current_vehicle_type == "truck":
                # 启动货车申办流程
                from apps.etc_apply.services.hcb.truck_service import start_truck_apply_flow
                from apps.etc_apply.services.hcb.truck_data_service import TruckDataService
                
                # 传递UI对象给TruckDataService，以便获取选择的产品
                params = TruckDataService._build_truck_params(self.get_current_form_data(), self)
                start_truck_apply_flow(params, self)
                
            else:
                # 启动客车申办流程（原有逻辑）
                from apps.etc_apply.services.rtx.etc_service import start_etc_apply_flow
                from apps.etc_apply.services.rtx.data_service import DataService
                
                params = DataService.build_apply_params_from_ui(self)
                start_etc_apply_flow(params, self)
                
        except Exception as e:
            # 使用新的错误显示机制
            error_message = str(e)
            self.show_api_error("启动申办流程", error_message)
            print(f"[ERROR] 启动申办流程失败: {error_message}")


sys.excepthook = excepthook  # 设置全局异常钩子

if __name__ == "__main__":  # 程序入口
    from PyQt5.QtWidgets import QApplication  # 导入应用程序类

    app = QApplication(sys.argv)  # 创建应用实例
    w = EtcApplyWidget()  # 创建主窗口
    w.show()  # 显示主窗口
    sys.exit(app.exec_())  # 进入主事件循环 



    