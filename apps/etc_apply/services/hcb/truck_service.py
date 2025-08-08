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
    启动货车ETC申办主流程
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
        # 通过信号更新UI进度条和日志
        if hasattr(ui, 'progress_signal'):
            ui.progress_signal.emit(percent, msg)
        if hasattr(ui, 'log_signal'):
            ui.log_signal.emit(msg)
    
    # 为progress_callback添加UI对象引用，以便错误处理能访问UI
    progress_callback.ui = ui

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
    处理货车ETC申办流程结果
    :param result: 结果数据
    :param ui: 可选，UI对象用于信号/弹窗等
    """
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