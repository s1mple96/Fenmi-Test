import threading
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt, QMetaObject, Q_ARG

def append_log(log_text, msg):
    try:
        if threading.current_thread() is threading.main_thread():
            log_text.append(msg)
            log_text.moveCursor(log_text.textCursor().End)
        else:
            QMetaObject.invokeMethod(log_text, "append", Qt.QueuedConnection, Q_ARG(str, msg))
            QMetaObject.invokeMethod(log_text, "moveCursor", Qt.QueuedConnection, Q_ARG(int, log_text.textCursor().End))
    except Exception as e:
        print(f"append_log异常: {e}")

def update_progress(progress_bar, progress_label, percent, msg):
    try:
        if threading.current_thread() is threading.main_thread():
            progress_bar.setValue(percent)
            progress_label.setText(f"进度：{msg}")
        else:
            QMetaObject.invokeMethod(progress_bar, "setValue", Qt.QueuedConnection, Q_ARG(int, percent))
            QMetaObject.invokeMethod(progress_label, "setText", Qt.QueuedConnection, Q_ARG(str, f"进度：{msg}"))
    except Exception as e:
        print(f"update_progress异常: {e}") 