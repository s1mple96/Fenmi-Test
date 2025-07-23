import sys  # 导入系统模块，用于程序入口和异常钩子
import os  # 导入操作系统模块

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5.QtWidgets import QDialog, QToolButton
from PyQt5.QtCore import pyqtSignal, QSize, Qt, QPoint, QEvent
from PyQt5.QtGui import QIcon
from ui.binder.ui_binder import bind_all_signals_and_shortcuts
from ui.builder.ui_builder import build_full_ui
from ui.utils.ui_util import excepthook, fill_default_values
from ui.components.draggable_group_box import ExamplePopup

class EtcApplyWidget(QDialog):  # ETC申办主界面类，继承自QWidget
    """
    ETC申办主界面，仅负责UI控件声明、布局、信号绑定、主流程触发。
    所有数据加载、保存、默认值、业务逻辑等全部抽离到ui/worker/utils等专用模块。
    """
    log_signal = pyqtSignal(str)  # 日志信号
    progress_signal = pyqtSignal(int, str)  # 百分比, 消息
    apply_submitted = pyqtSignal(dict)  # 申办完成信号

    def __init__(self, parent=None):  # 构造函数
        super().__init__(parent)  # 初始化父类
        self.inputs = {}  # 输入控件字典
        build_full_ui(self)  # 构建完整UI（所有控件和布局）
        bind_all_signals_and_shortcuts(self)  # 绑定所有信号和快捷键
        fill_default_values(self)  # 自动填充默认值
        # 绑定日志信号处理
        self.log_signal.connect(self.handle_log_message)
        self.progress_signal.connect(self.handle_progress_message)
        self._window_ready = False
        # 已彻底移除help_btn相关代码
        self.setWindowFlags(
            Qt.Window |
            Qt.WindowMinimizeButtonHint |
            Qt.WindowCloseButtonHint |
            Qt.WindowContextHelpButtonHint
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

    def show_example_popup(self):
        if not hasattr(self, '_example_popup') or self._example_popup is None:
            self._example_popup = ExamplePopup(self)
        # 居中弹出
        center_x = (self.width() - self._example_popup.width()) // 2
        center_y = (self.height() - self._example_popup.height()) // 2
        self._example_popup.move(self.mapToGlobal(QPoint(center_x, center_y)))
        self._example_popup.show()
        self._example_popup.raise_()
        self._example_popup.activateWindow()

    def event(self, event):
        CONTEXT_HELP = getattr(QEvent, "ContextHelpRequest", 0x000E)  # 0x000E=14
        if event.type() == CONTEXT_HELP and getattr(self, '_window_ready', False):
            self.show_example_popup()
            return True
        return super().event(event)


sys.excepthook = excepthook  # 设置全局异常钩子

if __name__ == "__main__":  # 程序入口
    from PyQt5.QtWidgets import QApplication  # 导入应用程序类
    import PyQt5
    import platform

    print("PyQt5 version:", PyQt5.QtCore.PYQT_VERSION_STR)
    print("Qt version:", PyQt5.QtCore.QT_VERSION_STR)
    print("OS:", platform.system(), platform.release())
    app = QApplication(sys.argv)  # 创建应用实例
    w = EtcApplyWidget()  # 创建主窗口
    w.show()  # 显示主窗口
    sys.exit(app.exec_())  # 进入主事件循环 



    