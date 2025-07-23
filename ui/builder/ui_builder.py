from PyQt5.QtWidgets import QPushButton, QLabel, QProgressBar, QTextEdit, QVBoxLayout, QFormLayout, QLineEdit, QHBoxLayout, QComboBox
from ui.utils.form_fields import FORM_FIELDS

def build_product_row(ui):
    ui.product_edit = QLineEdit()
    ui.product_edit.setReadOnly(True)
    ui.product_btn = QPushButton("选择产品")
    layout = QHBoxLayout()
    layout.addWidget(ui.product_edit)
    layout.addWidget(ui.product_btn)
    return "产品", layout

def build_plate_province_row(ui):
    ui.plate_province_edit = QLineEdit()
    ui.plate_province_edit.setReadOnly(True)
    ui.plate_province_btn = QPushButton("选择")
    layout = QHBoxLayout()
    layout.addWidget(ui.plate_province_edit)
    layout.addWidget(ui.plate_province_btn)
    return "车牌省份", layout

def build_plate_letter_row(ui):
    ui.plate_letter_edit = QLineEdit()
    ui.plate_letter_btn = QPushButton("选择字母")
    layout = QHBoxLayout()
    layout.addWidget(ui.plate_letter_edit)
    layout.addWidget(ui.plate_letter_btn)
    return "车牌字母", layout

def build_plate_number_row(ui):
    ui.plate_number_edit = QLineEdit()
    ui.plate_number_random_btn = QPushButton("随机")
    layout = QHBoxLayout()
    layout.addWidget(ui.plate_number_edit)
    layout.addWidget(ui.plate_number_random_btn)
    return "车牌号码", layout

def build_plate_color_row(ui):
    ui.plate_color_combo = QComboBox()
    ui.plate_color_combo.addItems(["蓝色", "黄色", "绿色", "白色", "黑色"])
    ui.plate_color_combo.setCurrentText("蓝色")
    return "车牌颜色", ui.plate_color_combo

def build_vin_row(ui):
    ui.vin_edit = QLineEdit()
    ui.vin_btn = QPushButton("自动获取VIN")
    layout = QHBoxLayout()
    layout.addWidget(ui.vin_edit)
    layout.addWidget(ui.vin_btn)
    return "VIN码", layout

def build_apply_button_row(ui):
    ui.gen_btn = QPushButton("一键申办ETC")
    return ui.gen_btn

def build_progress_row(ui):
    ui.progress_label = QLabel("进度：等待操作")
    ui.progress_bar = QProgressBar()
    ui.progress_bar.setMinimum(0)
    ui.progress_bar.setMaximum(100)
    ui.progress_bar.setValue(0)
    return ui.progress_label, ui.progress_bar

def build_log_row(ui):
    label = QLabel("详细日志：")
    ui.log_text = QTextEdit()
    ui.log_text.setReadOnly(True)
    ui.log_text.setMinimumHeight(180)
    return label, ui.log_text

def build_full_ui(ui):
    layout = QVBoxLayout()
    form_layout = QFormLayout()
    # 统一声明和布局
    for build_row in [
        build_product_row,
        build_plate_province_row,
        build_plate_letter_row,
        build_plate_number_row,
        build_plate_color_row,
        build_vin_row
    ]:
        label, widget = build_row(ui)
        form_layout.addRow(label, widget)
    # 其它字段
    for label, key, default, _ in FORM_FIELDS:
        if key in ['plate_province', 'plate_letter', 'plate_number', 'vin', 'product']:
            continue
        edit = QLineEdit(default)
        ui.inputs[key] = edit
        form_layout.addRow(label, edit)
    layout.addLayout(form_layout)
    # 移除保存四要素按钮
    # layout.addWidget(build_save_button_row(ui))
    layout.addWidget(build_apply_button_row(ui))
    # 注释或删除一键入库按钮相关代码
    # layout.addWidget(build_save_to_db_button_row(ui))
    progress_label, progress_bar = build_progress_row(ui)
    layout.addWidget(progress_label)
    layout.addWidget(progress_bar)
    log_label, log_text = build_log_row(ui)
    layout.addWidget(log_label)
    layout.addWidget(log_text)
    ui.setLayout(layout)
    # 绑定inputs
    ui.inputs['plate_province'] = ui.plate_province_edit
    ui.inputs['plate_letter'] = ui.plate_letter_edit
    ui.inputs['plate_number'] = ui.plate_number_edit
    ui.inputs['vin'] = ui.vin_edit
    ui.inputs['product'] = ui.product_edit 