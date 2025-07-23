# -*- coding: utf-8 -*-
"""
支持拖拽的QGroupBox组件
"""

import os
from PyQt5.QtWidgets import QGroupBox, QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent

class DraggableGroupBox(QGroupBox):
    """
    支持文件拖拽的QGroupBox组件
    """
    file_dropped = pyqtSignal(str)  # 文件拖拽信号
    
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.setAcceptDrops(True)
        self.init_style()
        
    def init_style(self):
        """初始化样式"""
        self.setStyleSheet("""
            QGroupBox {
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """拖拽进入事件"""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QGroupBox {
                    border: 2px solid #4CAF50;
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 10px;
                    font-weight: bold;
                    background-color: #E8F5E8;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #2E7D32;
                }
            """)
        else:
            event.ignore()
            
    def dragLeaveEvent(self, event):
        """拖拽离开事件"""
        self.init_style()
        
    def dropEvent(self, event: QDropEvent):
        """文件拖拽释放事件"""
        self.init_style()
        
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if os.path.isfile(file_path):
                self.file_dropped.emit(file_path)
            else:
                QMessageBox.warning(self, "警告", "请拖拽有效的文件！") 