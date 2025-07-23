# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMessageBox
from worker.etc.core import Core
from worker.etc.worker_thread import WorkerQThread
from worker.etc.param_validator import validate_and_complete_params
from worker.etc.result_handler import handle_result
from ui.utils.base_ui_util import append_log, update_progress

def start_etc_apply_flow(params, ui):
    """
    启动ETC申办主流程，所有业务逻辑、进度、日志等都在这里处理。
    :param params: 参数字典
    :param ui: UI主窗口对象（用于信号、日志、进度等回调）
    """
    try:
        params = validate_and_complete_params(params)
    except ValueError as e:
        QMessageBox.warning(None, "参数错误", str(e))
        return
    def progress_callback(percent, msg):
        # 通过信号更新UI进度条和日志
        if hasattr(ui, 'progress_signal'):
            ui.progress_signal.emit(percent, msg)
        if hasattr(ui, 'log_signal'):
            ui.log_signal.emit(msg)
    def run_to_step6():
        browser_cookies = {
            "JSESSIONID": "62513d79-39c2-4559-9afc-bc4deb4af7a0",
            "ETCAdmin-Token": "eyJhbGciOiJIUzUxMiJ9.eyJ1c2VyX2tleSI6IjEzN2Y1MWVhMjAwOTRjZTNiNDg5YjdjMDgzMTg1ODNlIiwidXNlcl9pZCI6MSwidXNlcm5hbWUiOiJhZG1pbiJ9.WjWNVQ1_PLu76QI_LnTZRtJLKfD331zRGdxDxfa6a94QoWeVWYSfr5kqT-pMAPh-gfuLDsCqgKEujsuAH9JaGw",
            "ETCAdmin-Expires-In": "180",
            "FmAdmin-Token": "eyJhbGciOiJIUzUxMiJ9.eyJ1c2VyX2tleSI6IjI3OTI2MWI0ZDk0ZjQ2Mzk5ZDg3YmQ5OWJjOWUzM2U1IiwidXNlcl9pZCI6MSwidXNlcm5hbWUiOiJhZG1pbiJ9.V9GHIfv4r4J5bqADlo7gYJZYd6YYGxRVkwd4qdyk1aRzTq9g0qNJrZ9Ai6SRKYWTgeBpmZBLF-Kp-eT2k_TljQ",
            "FmAdmin-Expires-In": "180",
            "Admin-Token": "eyJhbGciOiJIUzUxMiJ9.eyJsb2dpbl91c2VyX2tleSI6IjFkYmM1NDk0LWI4YWYtNGU2OC05ODk2LWJiMzllZDlhMWJlMCJ9.SDPVu-PA3odiIvCUNe-rKe6TH2KlXobquC4Br4gll7I_8dkVs83T5IJwK61yESOFLXd-Wwm_CsGgS_cNudbs9A"
        }
        worker = Core(params=params, progress_callback=progress_callback, base_url="http://788360p9o5.yicp.fun", browser_cookies=browser_cookies)
        # 分步执行前6步
        worker.step1_check_car_num()
        worker.step2_check_is_not_car_num()
        worker.step3_get_channel_use_address()
        worker.step4_get_optional_service_list()
        worker.step5_submit_car_num()
        worker.step6_protocol_add()
        # 赋值给UI
        ui.worker = worker
        ui.worker_order_id = worker.order_id
        ui.worker_sign_order_id = worker.sign_order_id
        ui.worker_verify_code_no = worker.verify_code_no
        return None
    if not hasattr(ui, 'worker_thread_list'):
        ui.worker_thread_list = []
    ui.worker_thread_list = [t for t in ui.worker_thread_list if t.isRunning()]
    ui.worker_thread = WorkerQThread(run_to_step6)
    ui.worker_thread_list.append(ui.worker_thread)
    # 直接连接到UI信号，避免重复处理
    ui.worker_thread.log_signal.connect(ui.log_signal.emit)
    ui.worker_thread.progress_signal.connect(ui.progress_signal.emit)
    ui.worker_thread.finished_signal.connect(lambda _: show_verify_dialog(ui))
    ui.worker_thread.start()

def show_verify_dialog(ui):
    """
    弹出验证码输入对话框，处理验证码获取和后续签约流程。
    """
    def on_get_code(dialog):
        # 只保留验证码相关的用户提示日志
        def run_step7():
            try:
                res = ui.worker.run_step7_get_code(ui.worker_order_id, ui.worker_sign_order_id)
                ui.worker_sign_order_id = res['sign_order_id']
                ui.worker_verify_code_no = res['verify_code_no']
                return True
            except Exception as e:
                return False
        ui.worker_thread_list = [t for t in ui.worker_thread_list if t.isRunning()]
        ui.worker_thread = WorkerQThread(run_step7)
        ui.worker_thread_list.append(ui.worker_thread)
        ui.worker_thread.log_signal.connect(ui.log_signal.emit)
        ui.worker_thread.progress_signal.connect(ui.progress_signal.emit)
        def on_finished(success):
            if success:
                dialog.start_timer()
                append_log(ui.log_text, "验证码已发送，请查收短信")
            else:
                append_log(ui.log_text, "获取验证码失败，请重试")
                dialog.get_code_btn.setEnabled(True)
                dialog.get_code_btn.setText("获取验证码")
        ui.worker_thread.finished_signal.connect(on_finished)
        ui.worker_thread.start()
    def on_confirm(code):
        # 不再追加“输入验证码：xxx，开始签约校验及后续流程...”日志
        def run_8_to_end():
            ui.worker.run_step8_to_end(code, ui.worker_order_id, ui.worker_sign_order_id, ui.worker_verify_code_no)
            return None
        ui.worker_thread_list = [t for t in ui.worker_thread_list if t.isRunning()]
        ui.worker_thread = WorkerQThread(run_8_to_end)
        ui.worker_thread_list.append(ui.worker_thread)
        ui.worker_thread.log_signal.connect(ui.log_signal.emit)
        ui.worker_thread.progress_signal.connect(ui.progress_signal.emit)
        ui.worker_thread.finished_signal.connect(lambda _: handle_result("申办流程全部完成！", ui))
        ui.worker_thread.start()
    from ui.components.verify_code_dialog import VerifyCodeDialog
    dialog = VerifyCodeDialog(ui, on_get_code=on_get_code, on_confirm=on_confirm)
    dialog.exec_()

def validate_params(params, form_fields):
    for label, key, _, required in form_fields:
        if required and not params.get(key):
            return False
    return True

def show_required_warning():
    QMessageBox.warning(None, "提示", "有必填项未填写！") 