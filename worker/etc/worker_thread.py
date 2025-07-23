from PyQt5.QtCore import QThread, pyqtSignal

class WorkerQThread(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(object)
    def __init__(self, worker_func, *args, **kwargs):
        super().__init__()
        self.worker_func = worker_func
        self.args = args
        self.kwargs = kwargs
    def run(self):
        try:
            result = self.worker_func(*self.args, **self.kwargs)
            self.finished_signal.emit(result)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            self.log_signal.emit(f"线程异常: {e}\n{tb}")
            self.finished_signal.emit(None) 