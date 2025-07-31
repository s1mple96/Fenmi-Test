# -*- coding: utf-8 -*-
# -------------------------------------------------------------
# 数据库批量造数主界面（WinForm Tab）
# 实现数据库/表切换、字段规则配置、批量插入、进度条、规则缓存等功能
# 详细中文注释，便于维护和协作
# -------------------------------------------------------------
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QLineEdit, QListWidget, QMessageBox, QSplitter, QTableWidget, QTableWidgetItem, QHBoxLayout, QComboBox, QHeaderView, QProgressBar, QScrollArea
)
from PyQt5.QtCore import Qt
import os
import json
from common.mysql_util import MySQLUtil
from common.data_factory import DataFactory
from apps.data_generator.services.data_gen_worker import DataGenInsertWorker
from datetime import datetime, timedelta
import random

# 读取数据库连接配置（仅取第一个MySQL配置）
def get_mysql_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'connections.json')
    with open(config_path, 'r', encoding='utf-8') as f:
        configs = json.load(f)
    for item in configs:
        if item['type'] == 'mysql':
            host, port = item['address'].split(':')
            return {
                'host': host,
                'port': int(port),
                'user': item['username'],
                'password': item['password'],
                'database': 'test'  # 默认库，后续可切换
            }
    raise Exception('未找到MySQL连接信息')

# 用户自定义日期格式转strftime格式
# 如 YYYYMMDD -> %Y%m%d
#    YYYY-MM-DD -> %Y-%m-%d
def user_date_format_to_strftime(fmt):
    fmt = fmt.replace('YYYY', '%Y').replace('MM', '%m').replace('DD', '%d')
    return fmt

# 根据造数规则生成示例数据
def get_rule_example(rule, field, ftype, extra=None):
    """
    根据规则、字段名、类型、额外参数生成示例值
    """
    if rule == '随机姓名':
        return DataFactory.random_name()
    elif rule == '随机手机号':
        return DataFactory.random_phone()
    elif rule == '随机身份证':
        return DataFactory.random_id_number()
    elif rule == '随机车牌':
        return DataFactory.random_plate_number()['plate_number']
    elif rule == '随机ETC号':
        return DataFactory.random_etc_number()
    elif rule == '随机OBN号':
        return DataFactory.random_obn_number()
    elif rule == '随机设备号':
        return DataFactory.random_device_id()
    elif rule == '随机订单号':
        return DataFactory.random_order_id()
    elif rule == '随机银行卡号':
        return DataFactory.random_bank_card()
    elif rule == '随机银行地址':
        return DataFactory.random_bank_address()
    elif rule == '固定值':
        return extra if extra is not None else 'test'
    elif rule == '枚举值':
        return extra if extra is not None else '0,1'
    elif rule == '随机日期':
        fmt = extra if extra else 'YYYY-MM-DD'
        strftime_fmt = user_date_format_to_strftime(fmt)
        dt = datetime.now() - timedelta(days=random.randint(0, 3650))
        try:
            return dt.strftime(strftime_fmt)
        except Exception:
            return dt.strftime('%Y-%m-%d')
    elif rule == '自增主键（自动生成）':
        return '自增主键（自动生成）'
    else:
        # 自动识别类型
        ftype_low = ftype.lower()
        fname = field.lower()
        if 'int' in ftype_low:
            if 'bigint' in ftype_low:
                return str(9999999999)
            return str(12345)
        if 'decimal' in ftype_low or 'float' in ftype_low or 'double' in ftype_low:
            return '123.45'
        if 'date' in ftype_low and 'time' not in ftype_low:
            return '2023-01-01'
        if 'datetime' in ftype_low or 'timestamp' in ftype_low:
            return '2023-01-01 12:00:00'
        if 'char' in ftype_low or 'text' in ftype_low:
            if 'name' in fname:
                return DataFactory.random_name()
            if 'phone' in fname:
                return DataFactory.random_phone()
            if 'id' in fname and 'card' not in fname:
                return DataFactory.random_id_number()
            if 'plate' in fname:
                return DataFactory.random_plate_number()['plate_number']
            if 'etc' in fname:
                return DataFactory.random_etc_number()
            if 'obn' in fname:
                return DataFactory.random_obn_number()
            if 'device' in fname:
                return DataFactory.random_device_id()
            if 'order' in fname:
                return DataFactory.random_order_id()
            if 'card' in fname:
                return DataFactory.random_bank_card()
            if 'bank' in fname:
                return DataFactory.random_bank_address()
            return 'teststr'
        return 'test'

class DataGenWidget(QWidget):
    """
    数据库造数主界面，支持数据库/表切换、表名筛选、字段造数规则配置、批量插入等功能
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        # 当前选中数据库、表
        self.current_db = None
        self.current_table = None
        self.all_tables = []
        self.worker = None
        self.pk_fields = set()
        self.auto_inc_fields = set()
        self.splitter = None
        self.left_width = 180
        self.mid_width = 220
        self._splitter_initialized = False
        self.extra_inputs = {}  # 记录可编辑输入框
        self.table_rule_cache = {}  # {(db, table): [(rule, extra), ...]} 规则缓存
        self.tabs = None
        self.init_ui()

    def get_max_text_width(self, items, font):
        """
        计算列表最大文本宽度，用于自适应宽度
        """
        from PyQt5.QtGui import QFontMetrics
        metrics = QFontMetrics(font)
        maxlen = max([metrics.width(str(i)) for i in items]) if items else 100
        return maxlen + 30

    def init_ui(self):
        """
        初始化主界面布局，分三栏：数据库、表、字段规则
        """
        main_layout = QVBoxLayout()
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setHandleWidth(1)

        # 左侧：数据库列表
        left_widget = QWidget()
        left_layout = QVBoxLayout()
        self.db_list = QListWidget()
        self.db_list.setStyleSheet('QListWidget { text-align:left; }')
        self.db_list.itemClicked.connect(self.handle_db_selected)
        left_layout.addWidget(QLabel('数据库列表'))
        left_layout.addWidget(self.db_list)
        self.refresh_db_btn = QPushButton('刷新数据库')
        self.refresh_db_btn.clicked.connect(self.handle_refresh_databases)
        left_layout.addWidget(self.refresh_db_btn)
        left_widget.setLayout(left_layout)
        self.splitter.addWidget(left_widget)

        # 中间：表筛选+表列表
        mid_widget = QWidget()
        mid_layout = QVBoxLayout()
        self.table_filter = QLineEdit()
        self.table_filter.setPlaceholderText('输入表名关键字筛选')
        mid_layout.addWidget(self.table_filter)
        self.table_list = QListWidget()
        self.table_list.setStyleSheet('QListWidget { text-align:left; }')
        self.table_list.itemClicked.connect(self.handle_table_selected)
        mid_layout.addWidget(QLabel('表列表'))
        mid_layout.addWidget(self.table_list)
        self.refresh_table_btn = QPushButton('刷新表')
        self.refresh_table_btn.clicked.connect(self.handle_refresh_tables)
        mid_layout.addWidget(self.refresh_table_btn)
        mid_widget.setLayout(mid_layout)
        self.splitter.addWidget(mid_widget)

        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 0)
        self.splitter.setStretchFactor(2, 1)

        # 右侧：表结构和造数规则（用QScrollArea包裹，内容紧凑）
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout()
        self.right_layout.setSpacing(6)
        self.right_label = QLabel('请选择表进行批量造数...')
        self.right_layout.addWidget(self.right_label)
        self.table_struct = QTableWidget()
        self.table_struct.setColumnCount(4)
        self.table_struct.setHorizontalHeaderLabels(['字段名', '类型', '造数规则', '示例'])
        self.table_struct.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_struct.hide()
        self.right_layout.addWidget(self.table_struct)
        hbox = QHBoxLayout()
        self.count_input = QLineEdit()
        self.count_input.setPlaceholderText('生成/插入数量，默认1000')
        hbox.addWidget(QLabel('数量:'))
        hbox.addWidget(self.count_input)
        self.right_layout.addLayout(hbox)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        self.right_layout.addWidget(self.progress_bar)
        btn_hbox = QHBoxLayout()
        self.gen_btn = QPushButton('批量生成并插入数据')
        self.gen_btn.clicked.connect(self.handle_gen_data)
        self.gen_btn.hide()
        btn_hbox.addWidget(self.gen_btn)
        self.cancel_btn = QPushButton('取消')
        self.cancel_btn.clicked.connect(self.handle_cancel)
        self.cancel_btn.hide()
        btn_hbox.addWidget(self.cancel_btn)
        self.right_layout.addLayout(btn_hbox)
        self.right_widget.setLayout(self.right_layout)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.right_widget)
        self.splitter.addWidget(scroll)

        main_layout.addWidget(self.splitter)
        self.setLayout(main_layout)
        self.handle_refresh_databases()
        self._splitter_initialized = False

    def set_splitter_sizes(self):
        """
        设置三栏宽度自适应
        """
        total_width = self.width() if self.width() > 0 else 1200
        self.splitter.setSizes([
            self.left_width,
            self.mid_width,
            max(400, total_width - self.left_width - self.mid_width)
        ])
        self._splitter_initialized = True

    def showEvent(self, event):
        super().showEvent(event)
        if not self._splitter_initialized:
            self.set_splitter_sizes()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.set_splitter_sizes()

    def handle_refresh_databases(self):
        """
        刷新数据库列表，并自适应宽度
        """
        self.db_list.clear()
        try:
            dbs = MySQLUtil.get_databases(get_mysql_config())
            width = self.get_max_text_width(dbs, self.db_list.font())
            self.left_width = width
            self.db_list.setFixedWidth(width)
            self.refresh_db_btn.setFixedWidth(width)
            for db in dbs:
                self.db_list.addItem(db)
            self.set_splitter_sizes()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'获取数据库失败：{e}')

    def handle_db_selected(self, item):
        """
        选中数据库后，刷新表列表
        """
        dbname = item.text()
        self.current_db = dbname
        self.handle_refresh_tables()

    def handle_refresh_tables(self):
        """
        刷新表列表，并自适应宽度
        """
        self.table_list.clear()
        if not self.current_db:
            return
        try:
            self.all_tables = MySQLUtil.get_tables(get_mysql_config(), self.current_db)
            width = self.get_max_text_width(self.all_tables, self.table_list.font())
            self.mid_width = width
            self.table_list.setFixedWidth(width)
            self.refresh_table_btn.setFixedWidth(width)
            self.table_filter.setFixedWidth(width)
            self.filter_tables()
            self.set_splitter_sizes()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'获取表失败：{e}')

    def filter_tables(self):
        """
        根据关键字筛选表名
        """
        keyword = self.table_filter.text().strip().lower()
        self.table_list.clear()
        for t in self.all_tables:
            if keyword in t.lower():
                self.table_list.addItem(t)

    def handle_table_selected(self, item):
        """
        选中表后，展示表结构和造数规则
        """
        table = item.text()
        self.current_table = table
        self.show_table_struct()

    def show_table_struct(self):
        """
        展示表字段、类型、造数规则、示例，支持规则缓存和主键检测
        """
        self.right_label.setText(f'当前表：{self.current_table}')
        fields = MySQLUtil.get_table_fields(get_mysql_config(), self.current_db, self.current_table)
        self.pk_fields = set(MySQLUtil.get_table_primary_keys(get_mysql_config(), self.current_db, self.current_table))
        self.auto_inc_fields = set()
        self.extra_inputs = {}
        for field in fields:
            if 'auto_increment' in field.get('Extra', '').lower():
                self.auto_inc_fields.add(field['Field'])
        self.table_struct.setRowCount(len(fields))
        self.fields = [field['Field'] for field in fields]
        self.types = [field['Type'] for field in fields]
        # 恢复缓存
        cache_key = (self.current_db, self.current_table)
        cache = self.table_rule_cache.get(cache_key, None)
        for i, field in enumerate(fields):
            self.table_struct.setItem(i, 0, QTableWidgetItem(field['Field']))
            self.table_struct.setItem(i, 1, QTableWidgetItem(field['Type']))
            if field['Field'] in self.auto_inc_fields:
                # 自增主键不可编辑
                rule_box = QComboBox()
                rule_box.addItem('自增主键（自动生成）')
                rule_box.setEnabled(False)
                self.table_struct.setCellWidget(i, 2, rule_box)
                self.table_struct.setItem(i, 3, QTableWidgetItem(get_rule_example('自增主键（自动生成）', field['Field'], field['Type'])))
            else:
                rule_box = QComboBox()
                rule_box.addItems([
                    '自动识别', '随机姓名', '随机手机号', '随机身份证', '随机车牌', '随机ETC号', '随机OBN号', '随机设备号', '随机订单号',
                    '随机银行卡号', '随机银行地址', '随机日期', '枚举值', '固定值'
                ])
                # 绑定当前行，避免lambda late binding问题
                def on_rule_change(rule, row=i, f=field['Field'], t=field['Type']):
                    self.set_example_widget(row, rule, f, t)
                rule_box.currentTextChanged.connect(on_rule_change)
                self.table_struct.setCellWidget(i, 2, rule_box)
                # 恢复缓存
                if cache and i < len(cache):
                    rule, extra = cache[i]
                    idx = rule_box.findText(rule)
                    if idx != -1:
                        rule_box.setCurrentIndex(idx)
                    self.set_example_widget(i, rule, field['Field'], field['Type'], extra)
                else:
                    self.set_example_widget(i, '自动识别', field['Field'], field['Type'])
        self.table_struct.show()
        self.gen_btn.show()
        self.cancel_btn.hide()
        self.progress_bar.hide()
        self.progress_bar.setValue(0)

    def set_example_widget(self, row, rule, field, ftype, extra_val=None):
        """
        设置示例列为可编辑输入框或只读内容
        """
        from PyQt5.QtWidgets import QLineEdit
        self.table_struct.setCellWidget(row, 3, None)
        if rule in ['固定值', '枚举值', '随机日期']:
            edit = QLineEdit()
            if rule == '固定值':
                edit.setPlaceholderText('请输入固定值')
            elif rule == '枚举值':
                edit.setPlaceholderText('如: 0,1,2 或 男,女,未知')
            elif rule == '随机日期':
                edit.setPlaceholderText('如: YYYY-MM-DD, YYYYMMDD')
                edit.setText('YYYY-MM-DD')
            if extra_val:
                edit.setText(extra_val)
            def on_text_change(val, r=row, ru=rule, f=field, t=ftype):
                self.extra_inputs[r] = edit
            edit.textChanged.connect(on_text_change)
            self.table_struct.setCellWidget(row, 3, edit)
            self.extra_inputs[row] = edit
        else:
            self.table_struct.setItem(row, 3, QTableWidgetItem(get_rule_example(rule, field, ftype)))
            if row in self.extra_inputs:
                del self.extra_inputs[row]

    def update_example(self, row, rule, field, ftype, extra_val=None):
        """
        外部调用，更新示例列
        """
        self.set_example_widget(row, rule, field, ftype, extra_val)

    def handle_gen_data(self):
        """
        批量生成并插入数据，支持进度条、规则缓存
        """
        try:
            count = int(self.count_input.text()) if self.count_input.text().strip() else 1000
            rules = []
            fields_to_insert = []
            types_to_insert = []
            extras = []
            for i in range(self.table_struct.rowCount()):
                field = self.fields[i]
                if field in self.auto_inc_fields:
                    continue
                fields_to_insert.append(field)
                types_to_insert.append(self.types[i])
                rule = self.table_struct.cellWidget(i, 2).currentText()
                rules.append(rule)
                if rule in ['固定值', '枚举值', '随机日期'] and i in self.extra_inputs:
                    extras.append(self.extra_inputs[i].text())
                else:
                    extras.append(None)
            # 缓存当前表的规则和输入内容
            cache_key = (self.current_db, self.current_table)
            cache_val = []
            for i in range(self.table_struct.rowCount()):
                rule = self.table_struct.cellWidget(i, 2).currentText()
                extra = self.extra_inputs[i].text() if (rule in ['固定值', '枚举值', '随机日期'] and i in self.extra_inputs) else None
                cache_val.append((rule, extra))
            self.table_rule_cache[cache_key] = cache_val
            self.progress_bar.setValue(0)
            self.progress_bar.show()
            self.cancel_btn.show()
            self.gen_btn.setEnabled(False)
            # 启动造数插入线程
            self.worker = DataGenInsertWorker(
                get_mysql_config(),
                self.current_db,
                self.current_table,
                fields_to_insert,
                types_to_insert,
                rules,
                count,
                extras
            )
            self.worker.progress.connect(self.progress_bar.setValue)
            self.worker.finished.connect(self.handle_finished)
            self.worker.error.connect(self.handle_error)
            self.worker.start()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'启动插入失败：{e}')
            self.progress_bar.hide()

    def handle_cancel(self):
        """
        取消批量插入任务
        """
        if self.worker:
            self.worker.stop()
            self.cancel_btn.setEnabled(False)

    def handle_finished(self, msg):
        """
        插入完成回调，恢复按钮状态
        """
        self.progress_bar.setValue(100)
        self.gen_btn.setEnabled(True)
        self.cancel_btn.hide()
        QMessageBox.information(self, '完成', msg)
        self.progress_bar.hide()

    def handle_error(self, msg):
        """
        插入出错回调，恢复按钮状态
        """
        self.gen_btn.setEnabled(True)
        self.cancel_btn.hide()
        QMessageBox.critical(self, '错误', msg)
        self.progress_bar.hide()
