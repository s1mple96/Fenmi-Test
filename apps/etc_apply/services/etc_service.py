# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QMessageBox
from apps.etc_apply.services.etc_core import Core
from apps.etc_apply.services.worker_thread import WorkerQThread
from apps.etc_apply.services.valid_service import validate_and_complete_params
from apps.etc_apply.services.result_service import handle_result
from apps.etc_apply.ui.ui_utils import ui_threads
from apps.etc_apply.services.config_service import ConfigService


def get_api_base_url():
    """从配置文件读取API基础URL"""
    return ConfigService.get_api_base_url()


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
        # 从配置服务获取cookies和URL
        browser_cookies = ConfigService.get_browser_cookies()
        service_url = ConfigService.get_etc_service_url()

        worker = Core(
            params=params,
            progress_callback=progress_callback,
            base_url=service_url,
            browser_cookies=browser_cookies
        )
        # 分步执行前6步
        worker.step1_check_car_num()
        worker.step2_check_is_not_car_num()
        worker.step3_get_channel_use_address()
        worker.step4_get_optional_service_list()
        worker.step5_submit_car_num()
        worker.step6_protocol_add()
        # 赋值给UI
        ui.worker = worker
        ui.worker_order_id = worker.state.order_id
        ui.worker_sign_order_id = worker.state.sign_order_id
        ui.worker_verify_code_no = worker.state.verify_code_no
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

    def on_get_code():
        # 只保留验证码相关的用户提示日志
        def run_step7():
            try:
                res = ui.worker.run_step7_get_code(ui.worker_order_id, ui.worker_sign_order_id)
                ui.worker_sign_order_id = res['sign_order_id']
                ui.worker_verify_code_no = res['verify_code_no']
                # 同时更新worker.state中的值
                ui.worker.state.sign_order_id = res['sign_order_id']
                ui.worker.state.verify_code_no = res['verify_code_no']
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
                ui_threads.append_log(ui.log_text, "验证码已发送，请查收短信")
            else:
                ui_threads.append_log(ui.log_text, "获取验证码失败，请重试")
                dialog.get_code_btn.setEnabled(True)
                dialog.get_code_btn.setText("获取验证码")

        ui.worker_thread.finished_signal.connect(on_finished)
        ui.worker_thread.start()

    def on_confirm(code):
        # 不再追加"输入验证码：xxx，开始签约校验及后续流程..."日志
        def run_8_to_end():
            try:
                result = ui.worker.run_step8_to_end(code, ui.worker_order_id, ui.worker_sign_order_id,
                                                    ui.worker_verify_code_no)
                return result
            except Exception as e:
                # 记录异常日志
                ui_threads.append_log(ui.log_text, f"申办流程异常: {str(e)}")
                # 抛出异常，让流程停止
                raise e

        ui.worker_thread_list = [t for t in ui.worker_thread_list if t.isRunning()]
        ui.worker_thread = WorkerQThread(run_8_to_end)
        ui.worker_thread_list.append(ui.worker_thread)
        ui.worker_thread.log_signal.connect(ui.log_signal.emit)
        ui.worker_thread.progress_signal.connect(ui.progress_signal.emit)

        def on_flow_finished(result):
            from apps.etc_apply.services.result_service import close_mock_data
            close_mock_data()
            if result is None:
                # 流程异常
                handle_result("申办流程异常，已关闭Mock数据", ui)
            else:
                # 流程正常完成
                handle_result("申办流程全部完成！", ui)

        ui.worker_thread.finished_signal.connect(on_flow_finished)
        ui.worker_thread.start()

    from apps.etc_apply.ui.ui_component import VerifyCodeDialog
    dialog = VerifyCodeDialog(ui, on_get_code=lambda: on_get_code(), on_confirm=on_confirm)
    dialog.exec_()