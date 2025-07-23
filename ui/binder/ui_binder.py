from ui.utils.ui_util import (
    handle_select_province,
    handle_select_plate_letter,
    handle_random_plate_number,
    handle_get_vin,
    handle_save_four_elements,
    handle_apply,
    handle_select_product,
    handle_save_to_db,
    fill_default_values,
)
from ui.components.drag_drop_widget import FourElementsParser
from PyQt5.QtWidgets import QMessageBox


def bind_all_signals(ui, handlers):
    ui.plate_province_btn.clicked.connect(lambda: handlers['select_province'](ui))
    ui.plate_letter_btn.clicked.connect(lambda: handlers['select_plate_letter'](ui))
    ui.plate_number_random_btn.clicked.connect(lambda: handlers['random_plate_number'](ui))
    ui.vin_btn.clicked.connect(lambda: handlers['get_vin'](ui))
    # ui.save_btn.clicked.connect(lambda: handlers['save_four_elements'](ui))
    ui.gen_btn.clicked.connect(lambda: handlers['apply'](ui))
    ui.product_btn.clicked.connect(lambda: handlers['select_product'](ui))
    
    # 绑定拖拽事件
    if hasattr(ui, 'four_elements_group'):
        ui.four_elements_group.file_dropped.connect(lambda file_path: handle_drag_drop(ui, file_path))


def get_default_handlers():
    return {
        'select_province': handle_select_province,
        'select_plate_letter': handle_select_plate_letter,
        'random_plate_number': handle_random_plate_number,
        'get_vin': handle_get_vin,
        'save_four_elements': handle_save_four_elements,
        'apply': handle_apply,
        'select_product': handle_select_product,
    }


def handle_drag_drop(ui, file_path):
    """处理文件拖拽事件"""
    try:
        # 解析四要素文件
        elements = FourElementsParser.parse_file(file_path)
        
        if not elements:
            QMessageBox.warning(ui, "警告", "未能从文件中解析出四要素信息！")
            return
        
        # 填充四要素字段
        filled_count = 0
        for key, value in elements.items():
            if key in ui.inputs:
                ui.inputs[key].setText(value)
                filled_count += 1
        
        # 显示成功消息
        if filled_count > 0:
            QMessageBox.information(ui, "成功", f"已自动填充 {filled_count} 个字段！\n\n解析结果：\n" + 
                                  "\n".join([f"{k}: {v}" for k, v in elements.items()]))
        else:
            QMessageBox.warning(ui, "警告", "未能找到匹配的字段进行填充！")
            
    except Exception as e:
        QMessageBox.critical(ui, "错误", f"解析文件失败：{str(e)}")

def bind_all_signals_and_shortcuts(ui):
    handlers = get_default_handlers()
    bind_all_signals(ui, handlers)
    # 可扩展快捷键等
