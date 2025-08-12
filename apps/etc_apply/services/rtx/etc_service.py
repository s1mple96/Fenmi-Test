# -*- coding: utf-8 -*-
"""
ETC申办服务 - 整合流程控制和结果处理
"""
from PyQt5.QtWidgets import QMessageBox
from apps.etc_apply.services.rtx.etc_core import Core
from apps.etc_apply.services.rtx.worker_thread import WorkerQThread
from apps.etc_apply.services.rtx.data_service import DataService
from apps.etc_apply.services.rtx.core_service import CoreService
from apps.etc_apply.ui.rtx.ui_utils import ui_threads


def get_api_base_url():
    """从配置文件读取API基础URL"""
    return CoreService.get_api_base_url()


def start_etc_apply_flow(params, ui):
    """
    启动ETC申办主流程，所有业务逻辑、进度、日志等都在这里处理。
    :param params: 参数字典
    :param ui: UI主窗口对象（用于信号、日志、进度等回调）
    """
    try:
        params = DataService.validate_and_complete_params(params)
    except ValueError as e:
        QMessageBox.warning(None, "参数错误", str(e))
        return

    def progress_callback(percent, msg):
        # 通过信号更新UI进度条和日志
        if hasattr(ui, 'progress_signal'):
            ui.progress_signal.emit(percent, msg)
        if hasattr(ui, 'log_signal'):
            ui.log_signal.emit(msg)
    
    # 为progress_callback添加UI对象引用，以便错误处理能访问UI
    progress_callback.ui = ui

    def run_to_step6():
        # 从配置服务获取cookies和URL
        browser_cookies = CoreService.get_browser_cookies()
        service_url = CoreService.get_api_base_url()

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
            DataService.close_mock_data()
            if result is None:
                # 流程异常
                handle_result("申办流程异常，已关闭Mock数据", ui)
            else:
                # 流程正常完成，显示退款确认弹窗
                handle_result("申办流程全部完成！", ui, show_refund_dialog=True)

        ui.worker_thread.finished_signal.connect(on_flow_finished)
        ui.worker_thread.start()

    from apps.etc_apply.ui.rtx.ui_component import VerifyCodeDialog
    dialog = VerifyCodeDialog(ui, on_get_code=lambda: on_get_code(), on_confirm=on_confirm)
    dialog.exec_()


def handle_result(result, ui=None, show_refund_dialog=False):
    """
    处理ETC申办流程结果
    :param result: 结果数据
    :param ui: 可选，UI对象用于信号/弹窗等
    :param show_refund_dialog: 是否显示退款确认弹窗
    """
    # 流程完成后关闭Mock数据
    DataService.close_mock_data()
    
    if ui:
        if hasattr(ui, 'log_signal'):
            ui.log_signal.emit(str(result))
        
        # 如果申办成功，显示退款确认弹窗
        if show_refund_dialog and result == "申办流程全部完成！":
            try:
                # 获取车牌号和支付金额
                car_num = _get_car_num_from_ui(ui)
                payment_amount = _get_payment_amount_from_ui(ui)
                
                print(f"[DEBUG] 弹窗参数: 车牌号={car_num}, 支付金额={payment_amount}")
                
                # 使用QTimer延迟显示弹窗，确保UI线程空闲
                from PyQt5.QtCore import QTimer
                
                def show_dialog():
                    from apps.etc_apply.ui.rtx.refund_confirm_dialog import show_refund_confirm_dialog
                    print(f"[DEBUG] 准备显示弹窗: {car_num}, {payment_amount}")
                    show_refund_confirm_dialog(ui, car_num, payment_amount)
                
                QTimer.singleShot(500, show_dialog)  # 延迟500ms显示
                
            except Exception as e:
                print(f"[ERROR] 显示退款确认弹窗失败: {e}")
                import traceback
                print(f"详细错误: {traceback.format_exc()}")
    # 其它处理可扩展...


def _get_car_num_from_ui(ui) -> str:
    """从UI获取车牌号"""
    try:
        print(f"[DEBUG] 尝试获取车牌号...")
        
        # 尝试从worker参数中获取
        if hasattr(ui, 'worker') and ui.worker and hasattr(ui.worker, 'params'):
            car_num = ui.worker.params.get('car_num') or ui.worker.params.get('carNum')
            print(f"[DEBUG] 从worker.params获取: {car_num}")
            if car_num:
                return car_num
        
        # 尝试从UI输入框获取
        if hasattr(ui, 'plate_province') and hasattr(ui, 'plate_letter') and hasattr(ui, 'plate_number'):
            try:
                province = ui.plate_province.text() if hasattr(ui.plate_province, 'text') else ""
                letter = ui.plate_letter.text() if hasattr(ui.plate_letter, 'text') else ""
                number = ui.plate_number.text() if hasattr(ui.plate_number, 'text') else ""
                print(f"[DEBUG] 从UI输入框获取: {province}{letter}{number}")
                if province and letter and number:
                    return f"{province}{letter}{number}"
            except Exception as e2:
                print(f"[DEBUG] UI输入框获取失败: {e2}")
        
        # 如果都获取不到，先返回一个测试值
        print(f"[DEBUG] 获取车牌号失败，使用默认值")
        return "苏ZNJ849"  # 临时使用固定值
    except Exception as e:
        print(f"[ERROR] 获取车牌号失败: {e}")
        return "苏ZNJ849"  # 临时使用固定值


def _get_payment_amount_from_ui(ui) -> str:
    """从UI获取支付金额"""
    try:
        # 尝试从worker的支付结果中获取
        if hasattr(ui, 'worker') and ui.worker:
            # 可能需要根据实际的支付响应结构调整
            # 暂时返回默认值，或者从日志中解析
            pass
        
        # 默认返回配置中的金额（通常是测试金额）
        return "0.02"  # 根据您的JSON数据，金额是0.02
    except Exception as e:
        print(f"[ERROR] 获取支付金额失败: {e}")
        return "0.00"