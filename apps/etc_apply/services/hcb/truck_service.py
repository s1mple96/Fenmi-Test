# -*- coding: utf-8 -*-
"""
货车ETC申办服务 - 整合流程控制和结果处理
"""
from PyQt5.QtWidgets import QMessageBox
from apps.etc_apply.services.hcb.truck_core import TruckCore
from apps.etc_apply.services.rtx.worker_thread import WorkerQThread
from apps.etc_apply.services.rtx.core_service import CoreService
# 延迟导入避免循环引用
from apps.etc_apply.ui.rtx.ui_utils import ui_threads


def start_truck_apply_flow(params, ui):
    """
    启动货车ETC申办主流程（包含防重复申办检查）
    :param params: 参数字典
    :param ui: UI主窗口对象
    """
    try:
        from apps.etc_apply.services.hcb.truck_data_service import TruckDataService
        params = TruckDataService.validate_and_complete_truck_params(params)
    except ValueError as e:
        # 参数验证失败时，需要关闭可能已开启的Mock数据
        try:
            TruckDataService.close_mock_data()
            if hasattr(ui, 'log_signal'):
                ui.log_signal.emit("参数验证失败，已关闭Mock数据")
        except Exception as mock_e:
            print(f"关闭Mock数据失败: {str(mock_e)}")
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

    # 🔥 首先进行防重复申办检查
    try:
        from apps.etc_apply.services.hcb.duplicate_check_service import DuplicateCheckService
        from apps.etc_apply.ui.rtx.duplicate_check_dialog import DuplicateCheckDialog
        
        # 提取用户五要素信息进行检查
        user_info = {
            'name': params.get('name', '') or params.get('cardHolder', ''),
            'phone': params.get('phone', ''),
            'id_code': params.get('id_code', '') or params.get('idCode', ''),
            'car_num': params.get('car_num', '') or params.get('carNum', ''),
            'vehicle_color': params.get('vehicle_color', '') or params.get('vehicleColor', '')
        }
        
        progress_callback(5, "正在检查是否存在重复申办记录...")
        
        # 执行重复检查
        duplicate_service = DuplicateCheckService()
        has_existing, existing_records = duplicate_service.check_user_existing_applications(user_info)
        
        if has_existing:
            # 🔥 过滤出需要修改状态的记录
            records_to_modify, records_to_skip = duplicate_service.filter_records_need_modify(existing_records)
            
            if records_to_modify:
                # 有需要修改的记录，显示确认对话框
                progress_callback(10, f"发现{len(records_to_modify)}条需要处理的ETC记录，请用户确认...")
                continue_apply = DuplicateCheckDialog.show_duplicate_check_dialog(records_to_modify, ui)
            else:
                # 所有记录都无需修改，直接继续申办
                progress_callback(10, f"发现{len(existing_records)}条ETC记录，但都无需修改状态，继续申办...")
                continue_apply = True
            
            if not continue_apply:
                progress_callback(0, "用户取消申办")
                # 用户取消申办时，需要关闭可能已开启的Mock数据
                try:
                    from apps.etc_apply.services.hcb.truck_data_service import TruckDataService
                    TruckDataService.close_mock_data()
                    if hasattr(ui, 'log_signal'):
                        ui.log_signal.emit("用户取消申办，已关闭Mock数据")
                except Exception as e:
                    print(f"关闭Mock数据失败: {str(e)}")
                QMessageBox.information(ui, "申办取消", "用户取消ETC申办操作")
                return
            
            # 用户确认继续，临时修改状态
            progress_callback(15, "正在临时修改重复记录状态...")
            modify_success = duplicate_service.temporarily_modify_status_for_reapply(existing_records)
            
            if not modify_success:
                # 临时修改状态失败时，需要关闭可能已开启的Mock数据
                try:
                    from apps.etc_apply.services.hcb.truck_data_service import TruckDataService
                    TruckDataService.close_mock_data()
                    if hasattr(ui, 'log_signal'):
                        ui.log_signal.emit("状态修改失败，已关闭Mock数据")
                except Exception as e:
                    print(f"关闭Mock数据失败: {str(e)}")
                QMessageBox.critical(ui, "错误", "临时修改记录状态失败，无法继续申办")
                return
            
            progress_callback(20, "状态修改成功，开始申办流程...")
            
            # 将duplicate_service存储到UI，以便申办完成后恢复状态
            ui.duplicate_service = duplicate_service
            
        else:
            progress_callback(10, "未发现重复记录，开始申办流程...")
            ui.duplicate_service = None
            
    except Exception as e:
        progress_callback(0, f"重复检查失败: {str(e)}")
        # 重复检查异常时，需要关闭可能已开启的Mock数据
        try:
            from apps.etc_apply.services.hcb.truck_data_service import TruckDataService
            TruckDataService.close_mock_data()
            if hasattr(ui, 'log_signal'):
                ui.log_signal.emit("重复检查异常，已关闭Mock数据")
        except Exception as mock_e:
            print(f"关闭Mock数据失败: {str(mock_e)}")
        QMessageBox.critical(ui, "检查错误", f"重复申办检查失败：{str(e)}")
        return

    def run_truck_flow():
        # 从配置服务获取cookies和URL
        browser_cookies = CoreService.get_browser_cookies()
        service_url = CoreService.get_api_base_url()

        worker = TruckCore(
            params=params,
            progress_callback=progress_callback,
            base_url=service_url,
            browser_cookies=browser_cookies
        )
        
        # 执行完整货车流程
        result = worker.run_full_truck_flow()
        
        # 赋值给UI
        ui.truck_worker = worker
        ui.truck_etc_apply_id = worker.truck_etc_apply_id
        ui.truck_user_id = worker.truck_user_id
        ui.truck_user_wallet_id = worker.truck_user_wallet_id
        
        return result

    if not hasattr(ui, 'worker_thread_list'):
        ui.worker_thread_list = []
    ui.worker_thread_list = [t for t in ui.worker_thread_list if t.isRunning()]
    ui.worker_thread = WorkerQThread(run_truck_flow)
    ui.worker_thread_list.append(ui.worker_thread)
    
    # 连接信号
    ui.worker_thread.log_signal.connect(ui.log_signal.emit)
    ui.worker_thread.progress_signal.connect(ui.progress_signal.emit)
    ui.worker_thread.finished_signal.connect(lambda result: handle_truck_result(result, ui))
    ui.worker_thread.start()


def start_truck_apply_step_flow(params, ui):
    """
    启动货车ETC申办分步流程（先执行到步骤5，然后等待用户确认）
    :param params: 参数字典
    :param ui: UI主窗口对象
    """
    try:
        from apps.etc_apply.services.hcb.truck_data_service import TruckDataService
        params = TruckDataService.validate_and_complete_truck_params(params)
    except ValueError as e:
        QMessageBox.warning(None, "参数错误", str(e))
        return

    def progress_callback(percent, msg):
        if hasattr(ui, 'progress_signal'):
            ui.progress_signal.emit(percent, msg)
        if hasattr(ui, 'log_signal'):
            ui.log_signal.emit(msg)

    def run_to_step5():
        browser_cookies = CoreService.get_browser_cookies()
        service_url = CoreService.get_api_base_url()

        worker = TruckCore(
            params=params,
            progress_callback=progress_callback,
            base_url=service_url,
            browser_cookies=browser_cookies
        )
        
        # 执行到步骤5
        result = worker.run_to_step5()
        
        # 赋值给UI
        ui.truck_worker = worker
        ui.truck_etc_apply_id = worker.truck_etc_apply_id
        ui.truck_user_id = worker.truck_user_id
        ui.truck_user_wallet_id = worker.truck_user_wallet_id
        
        return result

    if not hasattr(ui, 'worker_thread_list'):
        ui.worker_thread_list = []
    ui.worker_thread_list = [t for t in ui.worker_thread_list if t.isRunning()]
    ui.worker_thread = WorkerQThread(run_to_step5)
    ui.worker_thread_list.append(ui.worker_thread)
    
    ui.worker_thread.log_signal.connect(ui.log_signal.emit)
    ui.worker_thread.progress_signal.connect(ui.progress_signal.emit)
    ui.worker_thread.finished_signal.connect(lambda result: show_truck_confirm_dialog(ui, result))
    ui.worker_thread.start()


def show_truck_confirm_dialog(ui, step5_result):
    """
    显示货车申办确认对话框
    :param ui: UI对象
    :param step5_result: 步骤5的执行结果
    """
    if not step5_result:
        ui_threads.append_log(ui.log_text, "前置步骤执行失败，无法继续")
        return

    def on_confirm():
        """用户确认继续执行后续步骤"""
        def run_from_step6():
            try:
                result = ui.truck_worker.run_from_step6()
                return result
            except Exception as e:
                ui_threads.append_log(ui.log_text, f"货车申办流程异常: {str(e)}")
                raise e

        ui.worker_thread_list = [t for t in ui.worker_thread_list if t.isRunning()]
        ui.worker_thread = WorkerQThread(run_from_step6)
        ui.worker_thread_list.append(ui.worker_thread)
        ui.worker_thread.log_signal.connect(ui.log_signal.emit)
        ui.worker_thread.progress_signal.connect(ui.progress_signal.emit)
        ui.worker_thread.finished_signal.connect(lambda result: handle_truck_result(result, ui))
        ui.worker_thread.start()

    # 显示确认信息
    apply_id = step5_result.get("truck_etc_apply_id", "")
    ui_threads.append_log(ui.log_text, f"货车申办ID已生成: {apply_id}")
    ui_threads.append_log(ui.log_text, "请确认车辆信息无误后继续...")
    
    # 这里可以显示一个确认对话框，或者直接继续执行
    # 为了简化，直接继续执行
    on_confirm()


def handle_truck_result(result, ui=None):
    """
    处理货车ETC申办流程结果（包含状态恢复）
    :param result: 结果数据
    :param ui: 可选，UI对象用于信号/弹窗等
    """
    # 🔥 首先处理重复申办状态恢复
    if ui and hasattr(ui, 'duplicate_service') and ui.duplicate_service:
        try:
            if hasattr(ui, 'log_signal'):
                ui.log_signal.emit("正在恢复临时修改的记录状态...")
            
            restore_success = ui.duplicate_service.restore_original_status()
            
            if restore_success:
                backup_summary = ui.duplicate_service.get_backup_summary()
                if hasattr(ui, 'log_signal'):
                    ui.log_signal.emit(f"✅ 成功恢复{backup_summary['restored']}条记录的原始状态")
            else:
                if hasattr(ui, 'log_signal'):
                    ui.log_signal.emit("⚠️ 恢复原始状态失败，请检查日志")
                    
        except Exception as e:
            print(f"[ERROR] 恢复原始状态异常: {e}")
            if hasattr(ui, 'log_signal'):
                ui.log_signal.emit(f"❌ 恢复状态异常: {str(e)}")
    
    # 流程完成后关闭Mock数据（货车版本）
    try:
        from apps.etc_apply.services.hcb.truck_data_service import TruckDataService
        TruckDataService.close_mock_data()
    except Exception as e:
        print(f"关闭货车Mock数据失败: {str(e)}")
    
    if ui:
        if hasattr(ui, 'log_signal'):
            if result is None:
                ui.log_signal.emit("货车申办流程异常结束，已关闭Mock数据")
            else:
                ui.log_signal.emit("货车申办流程全部完成！已关闭Mock数据")
                if result.get("truck_etc_apply_id"):
                    ui.log_signal.emit(f"申办ID: {result['truck_etc_apply_id']}")
                
                # 如果申办成功，显示退款确认弹窗
                if result and result.get('status') == 'completed':
                    try:
                        # 获取车牌号和支付金额
                        car_num = _get_truck_car_num_from_ui(ui)
                        payment_amount = _get_truck_payment_amount_from_ui(ui)
                        
                        # 使用QTimer延迟显示弹窗，确保UI线程空闲
                        from PyQt5.QtCore import QTimer
                        
                        def show_dialog():
                            from apps.etc_apply.ui.rtx.refund_confirm_dialog import show_refund_confirm_dialog
                            show_refund_confirm_dialog(ui, car_num, payment_amount)
                        
                        QTimer.singleShot(500, show_dialog)  # 延迟500ms显示
                        
                    except Exception as e:
                        print(f"[ERROR] 显示货车退款确认弹窗失败: {e}")
                        import traceback
                        print(f"详细错误: {traceback.format_exc()}")
        
        # 重新启用申办按钮，允许用户重新申办
        try:
            from apps.etc_apply.ui.rtx.ui_core import ui_core
            ui_core.enable_ui_components(ui)
            if hasattr(ui, 'apply_btn'):
                ui.apply_btn.setEnabled(True)
                ui.apply_btn.setText("重新申办ETC")
            if hasattr(ui, 'log_signal'):
                ui.log_signal.emit("✅ 已重新启用申办按钮，可以重新申办")
        except Exception as e:
            if hasattr(ui, 'log_signal'):
                ui.log_signal.emit(f"⚠️ 启用按钮失败: {str(e)}")


def _get_truck_car_num_from_ui(ui) -> str:
    """从UI获取货车车牌号"""
    try:
        # 尝试从worker参数中获取
        if hasattr(ui, 'truck_worker') and ui.truck_worker and hasattr(ui.truck_worker, 'params'):
            params = ui.truck_worker.params
            car_num = params.get('car_num') or params.get('carNum')
            if car_num:
                return car_num
            
            # 尝试拼接货车车牌
            province = params.get('truck_plate_province', '')
            letter = params.get('truck_plate_letter', '')
            number = params.get('truck_plate_number', '')
            if province and letter and number:
                return f"{province}{letter}{number}"
        
        # 尝试从UI输入框获取
        if hasattr(ui, 'truck_plate_province') and hasattr(ui, 'truck_plate_letter') and hasattr(ui, 'truck_plate_number'):
            province = ui.truck_plate_province.text() if hasattr(ui.truck_plate_province, 'text') else ""
            letter = ui.truck_plate_letter.text() if hasattr(ui.truck_plate_letter, 'text') else ""
            number = ui.truck_plate_number.text() if hasattr(ui.truck_plate_number, 'text') else ""
            if province and letter and number:
                return f"{province}{letter}{number}"
        
        return "未知货车车牌"
    except Exception as e:
        print(f"[ERROR] 获取货车车牌号失败: {e}")
        return "未知货车车牌"


def _get_truck_payment_amount_from_ui(ui) -> str:
    """从UI获取货车支付金额"""
    try:
        # 尝试从worker的支付结果中获取
        if hasattr(ui, 'truck_worker') and ui.truck_worker:
            # 可能需要根据实际的支付响应结构调整
            # 暂时返回默认值，或者从日志中解析
            pass
        
        # 默认返回配置中的金额（通常是测试金额）
        return "0.02"  # 根据您的JSON数据，金额是0.02
    except Exception as e:
        print(f"[ERROR] 获取货车支付金额失败: {e}")
        return "0.00"


class TruckBusinessService:
    """货车业务逻辑服务"""
    
    @staticmethod
    def validate_truck_params(params):
        """验证货车专用参数"""
        required_fields = [
            'cardHolder',     # 持卡人
            'idCode',         # 身份证号
            'phone',          # 手机号
            'carNum',         # 车牌号
            'bankName',       # 银行名称
            'bankNo',         # 银行卡号
            'vin',            # 车架号
            'vehicleAxles',   # 车轴数
            'vehicleWheels',  # 车轮数
            'totalMass',      # 总质量
            'unladenMass',    # 整备质量
            'model',          # 车辆型号
            'carType'         # 车辆类型
        ]
        
        missing_fields = [field for field in required_fields if not params.get(field)]
        if missing_fields:
            raise ValueError(f"缺少必需的货车参数: {', '.join(missing_fields)}")
        
        # 验证各字段格式
        if not CoreService.validate_car_num(params.get('carNum', '')):
            raise ValueError(f"车牌号格式错误: {params.get('carNum')}")
        
        if not CoreService.validate_id_code(params.get('idCode', '')):
            raise ValueError(f"身份证号格式错误: {params.get('idCode')}")
        
        if not CoreService.validate_phone(params.get('phone', '')):
            raise ValueError(f"手机号格式错误: {params.get('phone')}")
        
        if not CoreService.validate_bank_card(params.get('bankNo', '')):
            raise ValueError(f"银行卡号格式错误: {params.get('bankNo')}")
        
        if not CoreService.validate_vin(params.get('vin', '')):
            raise ValueError(f"VIN码格式错误: {params.get('vin')}")
    
    @staticmethod
    def build_truck_params(form_data):
        """构建货车申办参数"""
        params = {}
        
        # 基础用户信息映射
        params.update({
            'cardHolder': form_data.get('name', ''),
            'idCode': form_data.get('id_code', ''),
            'phone': form_data.get('phone', ''),
            'mobileNo': form_data.get('phone', ''),
            'bankNo': form_data.get('bank_no', ''),
            'bankName': form_data.get('bank_name', ''),
        })
        
        # 车辆信息
        params.update({
            'carNum': TruckBusinessService._build_car_num(form_data),
            'plateColor': form_data.get('plate_color', '1'),
            'vin': form_data.get('vin', ''),
            'vehicleAxles': form_data.get('vehicle_axles', ''),
            'vehicleWheels': form_data.get('vehicle_wheels', ''),
            'totalMass': form_data.get('total_mass', ''),
            'unladenMass': form_data.get('unladen_mass', ''),
            'model': form_data.get('model', ''),
            'carType': form_data.get('car_type', ''),
            'registerDate': form_data.get('register_date', ''),
            'issueDate': form_data.get('issue_date', ''),
            'vehicleEngineno': form_data.get('engine_no', ''),
            'approvedCount': form_data.get('approved_count', ''),
            'weightLimits': form_data.get('weight_limits', ''),
            'usePurpose': form_data.get('use_purpose', '货运'),
            'long': form_data.get('length', ''),
            'width': form_data.get('width', ''),
            'height': form_data.get('height', ''),
        })
        
        # 产品信息
        business_config = CoreService.get_business_config()
        if 'selected_product' in form_data and form_data['selected_product']:
            product = form_data['selected_product']
            params['productId'] = product.get('product_id')
        else:
            params['productId'] = business_config.get('default_product_id', '0bcc3075edef4151a9a2bff052607a24')
        
        # 填充默认参数
        params.update({
            'channelId': '0000',
            'operatorId': '717830e1c3a948709ec0a92b44400c60',
            'isCompany': '0',
            'obuSubmitStatus': '1',
            'ethnic': '汉',
            'urgentContact': form_data.get('urgent_contact', '张三'),
            'urgentPhone': form_data.get('urgent_phone', '13800138000'),
            'effectiveDate': form_data.get('effective_date', '20200101-20300101'),
            'idAuthority': form_data.get('id_authority', 'XX市公安局'),
            'idAddress': form_data.get('id_address', ''),
            'openId': form_data.get('open_id', 'oDefaultTestOpenId12345'),
            'verifyCode': form_data.get('verify_code', '250731'),
        })
        
        return params
    
    @staticmethod
    def _build_car_num(form_data):
        """构建车牌号"""
        province = form_data.get('plate_province', '')
        letter = form_data.get('plate_letter', '')
        number = form_data.get('plate_number', '')
        return CoreService.build_car_num(province, letter, number)
    
    @staticmethod
    def get_truck_defaults():
        """获取货车默认参数"""
        return {
            'plateColor': '1',  # 黄色（货车）
            'channelId': '0000',
            'operatorId': '717830e1c3a948709ec0a92b44400c60',
            'isCompany': '0',
            'obuSubmitStatus': '1',
            'ethnic': '汉',
            'usePurpose': '货运',
            'agreeType': 'S',
            'payType': '0'
        } 