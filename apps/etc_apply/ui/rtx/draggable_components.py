# -*- coding: utf-8 -*-
"""
拖拽组件模块
"""
import os
from PyQt5.QtWidgets import QGroupBox, QWidget, QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from apps.etc_apply.ui.rtx.ui_styles import ui_styles


class DraggableGroupBox(QGroupBox):
    """支持拖拽的QGroupBox组件"""
    file_dropped = pyqtSignal(str)
    
    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        print(f"创建拖拽组件: {title}")
        self.setAcceptDrops(True)
        self.init_style()
        self.original_title = title  # 保存原始标题
        self.installEventFilter(self)
        print(f"拖拽组件初始化完成，标题: {self.title()}")
        # 递归禁用所有子控件的拖拽
        self._disable_child_drops(self)

    def _disable_child_drops(self, widget):
        for child in widget.findChildren(QWidget):
            child.setAcceptDrops(False)
            self._disable_child_drops(child)

    def init_style(self):
        self.setStyleSheet(ui_styles.get_draggable_group_normal_style())
        print("拖拽组件样式设置完成")

    def dragEnterEvent(self, event: QDragEnterEvent):
        print(f"拖拽进入事件被触发，组件标题: {self.title()}")
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(ui_styles.get_draggable_group_drag_enter_style())
            print("拖拽文件被接受")
        else:
            event.ignore()
            print("拖拽内容被拒绝")

    def dragLeaveEvent(self, event):
        print(f"拖拽离开事件被触发，组件标题: {self.title()}")
        self.init_style()

    def dropEvent(self, event: QDropEvent):
        print(f"文件拖拽事件被触发，组件标题: {self.title()}")
        self.init_style()
        
        # 获取MIME数据
        mime_data = event.mimeData()
        print(f"MIME数据类型: {mime_data.formats()}")
        
        # 检查是否有URL
        if mime_data.hasUrls():
            urls = mime_data.urls()
            print(f"获取到URL数量: {len(urls)}")
            
            if urls:
                file_url = urls[0]
                print(f"第一个URL: {file_url.toString()}")
                
                # 尝试获取本地文件路径
                file_path = file_url.toLocalFile()
                print(f"本地文件路径: {file_path}")
                
                if file_path:
                    if os.path.isfile(file_path):
                        print(f"文件存在，发送信号: {file_path}")
                        # 确保标题不被修改
                        self.setTitle(self.original_title)
                        self.file_dropped.emit(file_path)
                    else:
                        print(f"文件不存在: {file_path}")
                        QMessageBox.warning(self, "警告", f"文件不存在: {file_path}")
                else:
                    print("无法获取本地文件路径")
                    QMessageBox.warning(self, "警告", "无法获取文件路径，请确保拖拽的是本地文件")
            else:
                print("URL列表为空")
                QMessageBox.warning(self, "警告", "没有获取到文件URL")
        else:
            print("MIME数据中没有URL")
            print(f"可用的MIME格式: {mime_data.formats()}")
            QMessageBox.warning(self, "警告", "请拖拽文件而不是文件夹或其他内容")

    def eventFilter(self, obj, event):
        # 移除弹窗功能，不再需要
        return super().eventFilter(obj, event) 