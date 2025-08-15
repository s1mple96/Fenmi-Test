# -*- coding: utf-8 -*-
# -------------------------------------------------------------
# ETC测试工具集主窗口（WinForm）
# 支持多Tab，主Tab为数据库造数，预留更多工具扩展
# 详细中文注释，便于维护和协作
# -------------------------------------------------------------
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from PyQt5.QtGui import QIcon
from apps.data_generator.ui.data_gen_widget import DataGenWidget
from apps.etc_apply.main_window import EtcApplyWidget  # 新增ETC申办Tab

class MainWin(QMainWindow):
    """
    主窗口，集成多个工具Tab，主Tab为数据库造数
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ETC自助申办工具')
        
        # 设置窗口图标
        try:
            # 优先尝试ICO格式图标
            ico_path = os.path.join(os.path.dirname(__file__), 'apps', 'etc_apply', 'config', 'logo.ico')
            png_path = os.path.join(os.path.dirname(__file__), 'apps', 'etc_apply', 'config', 'logo.png')
            
            if os.path.exists(ico_path):
                self.setWindowIcon(QIcon(ico_path))
                print(f"[INFO] 主窗口使用ICO图标: {ico_path}")
            elif os.path.exists(png_path):
                self.setWindowIcon(QIcon(png_path))
                print(f"[INFO] 主窗口使用PNG图标: {png_path}")
            else:
                print(f"[WARNING] Logo文件不存在: {ico_path} 或 {png_path}")
        except Exception as e:
            print(f"[WARNING] 设置窗口图标失败: {e}")
            
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
