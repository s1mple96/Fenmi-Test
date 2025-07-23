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


def bind_all_signals(ui, handlers):
    ui.plate_province_btn.clicked.connect(lambda: handlers['select_province'](ui))
    ui.plate_letter_btn.clicked.connect(lambda: handlers['select_plate_letter'](ui))
    ui.plate_number_random_btn.clicked.connect(lambda: handlers['random_plate_number'](ui))
    ui.vin_btn.clicked.connect(lambda: handlers['get_vin'](ui))
    # ui.save_btn.clicked.connect(lambda: handlers['save_four_elements'](ui))
    ui.gen_btn.clicked.connect(lambda: handlers['apply'](ui))
    ui.product_btn.clicked.connect(lambda: handlers['select_product'](ui))


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


def bind_all_signals_and_shortcuts(ui):
    handlers = get_default_handlers()
    bind_all_signals(ui, handlers)
    # 可扩展快捷键等
