# -*- coding: utf-8 -*-
"""
拖拽文件组件，支持四要素文件拖拽自动填充
"""

import os
import re
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QPixmap, QPainter, QColor, QFont

class DragDropWidget(QWidget):
    """
    文件拖拽组件，支持拖拽四要素文件自动填充
    """
    file_dropped = pyqtSignal(str)  # 文件拖拽信号
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumSize(200, 100)
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        
        # 创建拖拽提示标签
        self.label = QLabel("拖拽四要素文件到这里\n支持 .txt, .csv, .json 格式")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #cccccc;
                border-radius: 10px;
                padding: 20px;
                background-color: #f9f9f9;
                color: #666666;
                font-size: 14px;
            }
        """)
        
        layout.addWidget(self.label)
        self.setLayout(layout)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.label.setStyleSheet("""
                QLabel {
                    border: 2px dashed #4CAF50;
                    border-radius: 10px;
                    padding: 20px;
                    background-color: #E8F5E8;
                    color: #2E7D32;
                    font-size: 14px;
                }
            """)
        else:
            event.ignore()
            
    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #cccccc;
                border-radius: 10px;
                padding: 20px;
                background-color: #f9f9f9;
                color: #666666;
                font-size: 14px;
            }
        """)
        
    def dropEvent(self, event: QDropEvent):
        """文件拖拽释放事件"""
        self.label.setStyleSheet("""
            QLabel {
                border: 2px dashed #cccccc;
                border-radius: 10px;
                padding: 20px;
                background-color: #f9f9f9;
                color: #666666;
                font-size: 14px;
            }
        """)
        
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if os.path.isfile(file_path):
                self.file_dropped.emit(file_path)
            else:
                QMessageBox.warning(self, "警告", "请拖拽有效的文件！")

class FourElementsParser:
    """
    四要素解析器，支持多种格式的文件解析
    """
    
    @staticmethod
    def parse_file(file_path):
        """
        解析四要素文件
        返回格式: {"name": "姓名", "id_code": "身份证号", "phone": "手机号", "bank_no": "银行卡号"}
        """
        try:
            ext = os.path.splitext(file_path)[1].lower()
            
            if ext == '.txt':
                return FourElementsParser.parse_txt(file_path)
            elif ext == '.csv':
                return FourElementsParser.parse_csv(file_path)
            elif ext == '.json':
                return FourElementsParser.parse_json(file_path)
            else:
                raise ValueError(f"不支持的文件格式: {ext}")
                
        except Exception as e:
            raise Exception(f"解析文件失败: {str(e)}")
    
    @staticmethod
    def parse_txt(file_path):
        """解析TXT文件"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        
        # 尝试多种分隔符
        separators = ['\t', ',', '|', ';', ' ']
        lines = []
        
        for sep in separators:
            if sep in content:
                lines = [line.strip() for line in content.split('\n') if line.strip()]
                break
        
        if not lines:
            # 如果没有分隔符，尝试按行解析
            lines = [line.strip() for line in content.split('\n') if line.strip()]
        
        return FourElementsParser.extract_elements(lines)
    
    @staticmethod
    def parse_csv(file_path):
        """解析CSV文件"""
        import csv
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            lines = [row for row in reader if any(cell.strip() for cell in row)]
        
        return FourElementsParser.extract_elements(lines)
    
    @staticmethod
    def parse_json(file_path):
        """解析JSON文件"""
        import json
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 支持多种JSON格式
        if isinstance(data, dict):
            return FourElementsParser.extract_from_dict(data)
        elif isinstance(data, list) and len(data) > 0:
            return FourElementsParser.extract_from_dict(data[0])
        else:
            raise ValueError("JSON格式不支持")
    
    @staticmethod
    def extract_elements(lines):
        """从行数据中提取四要素"""
        elements = {}
        
        for line in lines:
            if isinstance(line, list):
                # CSV格式，line是列表
                text = ' '.join(line)
            else:
                # 普通文本格式
                text = str(line)
            
            # 提取身份证号
            id_match = re.search(r'\d{17}[\dXx]', text)
            if id_match and 'id_code' not in elements:
                elements['id_code'] = id_match.group()
            
            # 提取手机号
            phone_match = re.search(r'1[3-9]\d{9}', text)
            if phone_match and 'phone' not in elements:
                elements['phone'] = phone_match.group()
            
            # 提取银行卡号
            bank_match = re.search(r'\d{16,19}', text)
            if bank_match and 'bank_no' not in elements:
                bank_no = bank_match.group()
                # 简单验证银行卡号长度
                if 16 <= len(bank_no) <= 19:
                    elements['bank_no'] = bank_no
            
            # 提取姓名（2-4个中文字符）
            name_match = re.search(r'[\u4e00-\u9fa5]{2,4}', text)
            if name_match and 'name' not in elements:
                elements['name'] = name_match.group()
        
        return elements
    
    @staticmethod
    def extract_from_dict(data):
        """从字典中提取四要素"""
        elements = {}
        
        # 常见的字段名映射
        field_mapping = {
            'name': ['name', '姓名', 'user_name', 'username', 'real_name'],
            'id_code': ['id_code', 'idCode', '身份证', '身份证号', 'id_number', 'idNumber'],
            'phone': ['phone', '手机号', '手机', 'mobile', 'tel', 'telephone'],
            'bank_no': ['bank_no', 'bankNo', '银行卡号', '银行卡', 'card_number', 'cardNumber']
        }
        
        for key, possible_names in field_mapping.items():
            for name in possible_names:
                if name in data and data[name]:
                    elements[key] = str(data[name])
                    break
        
        return elements 