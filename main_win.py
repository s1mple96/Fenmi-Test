# -*- coding: utf-8 -*-
# -------------------------------------------------------------
# ETC测试工具集主窗口（WinForm）
# 支持多Tab，主Tab为数据库造数，预留更多工具扩展
# 详细中文注释，便于维护和协作
# -------------------------------------------------------------
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from winform.data_gen_widget import DataGenWidget
from winform.etc_apply_widget import EtcApplyWidget  # 新增ETC申办Tab

class MainWin(QMainWindow):
    """
    主窗口，集成多个工具Tab，主Tab为数据库造数
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle('分米测试工具集')
        self.setGeometry(300, 200, 1000, 600)
        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        """
        初始化主界面Tab布局，主Tab为数据库造数，新增ETC申办Tab，预留更多Tab
        """
        self.tabs = QTabWidget()
        self.tabs.addTab(DataGenWidget(), '数据库造数')
        self.tabs.addTab(EtcApplyWidget(), '申办ETC')  # 新增ETC申办Tab
        # 预留更多工具集Tab
        self.tabs.addTab(QTabWidget(), '更多工具（待扩展）')
        self.setCentralWidget(self.tabs)

if __name__ == '__main__':
    # 程序入口，启动主窗口
    app = QApplication(sys.argv)
    win = MainWin()
    win.show()
    sys.exit(app.exec_())
