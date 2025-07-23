import os
import paramiko
import random
import datetime
import requests
import pymysql
import time
import json

# 流程配置
PROCESS_CONFIG = {
    'operator': 'TXB',  # 运营商选择：TXB-RTX通行宝，JS_ETC-江苏ETC
    'generate_bill': True,  # 是否执行生成账单文件
    'insert_db': True,  # 是否执行插入数据库记录
    'trigger_job': True,  # 是否执行触发路费解析定时任务
    'trigger_bill_job': True,  # 是否执行触发账单计费任务
    'trigger_deduct_job': True,  # 是否执行触发扣费任务
    'process_count': 1,  # 执行次数
    'bill_amount': 1200  # 账单金额（分）
}

# 清理配置
CLEANUP_CONFIG = {
    'delete_bill_files': False  # 是否删除生成的账单文件
}

# API配置
API_BASE_URL = 'http://788360p9o5.yicp.fun'
API_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6'
}

# 运营商配置
OPERATOR_CONFIGS = {
    'TXB': {
        'name': '通行宝',
        'SSH_HOST': '192.168.1.60',
        'SSH_PORT': 22,
        'SSH_USER': 'root',
        'SSH_PASSWORD': 'fenmi123',
        'BILL_DIR': '/diskdata2/rtx/bill/TXB/',
        'CAR_NUM': '苏ZZZZZ8',
        'BILL_DATE': '20250716',
        'DB_CONFIG': {
            'host': '192.168.1.60',
            'port': 3306,
            'user': 'root',
            'password': 'fm123456',
            'database': 'rtx'
        },
        'BILL_CONTENT': lambda bill_date, car_num, amount: (
            f"{bill_date}^1^{amount}^1^{amount}\n"
            f"{bill_date}^4413031521{bill_date}{random.randint(10000000, 99999999)}^{car_num}^0^1^3201352080000054^{amount}^{bill_date}^223017^江苏三桥站^0^2,3,,江苏东善桥站,279^{bill_date}^223017"
        )
    },
    'JS_ETC': {
        'name': '江苏ETC',
        'SSH_HOST': '192.168.1.60',
        'SSH_PORT': 22,
        'SSH_USER': 'root',
        'SSH_PASSWORD': 'fenmi123',
        'BILL_DIR': '/diskdata2/rtx/bill/new_etc/',
        'CAR_NUM': '苏Z19996',
        'BILL_DATE': '20250530',
        'DB_CONFIG': {
            'host': '192.168.1.60',
            'port': 3306,
            'user': 'root',
            'password': 'fm123456',
            'database': 'fenmi_etc'
        },
        'DB_TABLE': 'etc_deduct_record_txb_2025',
        'BILL_CONTENT': lambda bill_date, car_num, amount: (
            f"{bill_date}^1^{amount}^1^{amount}\n"
            f"{bill_date}^4413031521{bill_date}{random.randint(10000000, 99999999)}^{car_num}^0^1^3201072280104255^{amount}^{bill_date}^223017^惠州大亚湾万达广场1^0^2,3,,惠州大亚湾万达广场停车场1,279^{bill_date}^223017\n"
        )
    }
}


class RoadFeeCreator:
    def __init__(self, operator='TXB'):
        self.operator = operator
        self.config = OPERATOR_CONFIGS[operator]
        self.session = requests.Session()
        self.token = None
        self.uuid = None
        self.captcha_code = None
        self.generated_files = []  # 用于存储生成的文件名

    def get_captcha(self):
        """获取验证码"""
        url = f"{API_BASE_URL}/rtx-admin/captchaImage"
        headers = {
            **API_HEADERS,
            'Referer': f'{API_BASE_URL}/login?redirect=%2Findex'
        }
        response = self.session.get(url, headers=headers)

        # 打印响应内容用于调试
        print(f"验证码接口响应状态码: {response.status_code}")
        print(f"验证码接口响应内容: {response.text}")

        # 断言响应状态码
        assert response.status_code == 200, f"获取验证码失败，状态码：{response.status_code}"

        try:
            # 解析响应数据
            data = response.json()
            print(f"验证码接口解析后的数据: {data}")

            # 断言响应数据结构
            assert 'data' in data, "验证码响应缺少data字段"
            assert 'uuid' in data['data'], "验证码响应缺少uuid字段"
            assert 'img' in data['data'], "验证码响应缺少img字段"

            self.uuid = data['data']['uuid']
            self.captcha_code = "0"  # 使用万能验证码

            return True
        except json.JSONDecodeError as e:
            print(f"验证码接口响应不是有效的JSON格式: {str(e)}")
            raise AssertionError("验证码接口响应格式错误")

    def login(self):
        """登录获取token"""
        url = f"{API_BASE_URL}/rtx-admin/login"
        headers = {
            **API_HEADERS,
            'Content-Type': 'application/json',
            'Origin': API_BASE_URL,
            'Referer': f'{API_BASE_URL}/login?redirect=%2Findex'
        }
        data = {
            "username": "admin",
            "password": "mf888769*",
            "code": "0",  # 这里需要实现验证码识别，暂时使用固定值
            "uuid": self.uuid
        }
        response = self.session.post(url, headers=headers, json=data)

        # 打印响应内容用于调试
        print(f"登录接口响应状态码: {response.status_code}")
        print(f"登录接口响应内容: {response.text}")

        # 断言响应状态码
        assert response.status_code == 200, f"登录失败，状态码：{response.status_code}"

        try:
            # 解析响应数据
            data = response.json()
            print(f"登录接口解析后的数据: {data}")

            # 检查登录是否成功
            if data['code'] != 200:
                raise AssertionError(f"登录失败：{data['msg']}")

            # 检查data字段是否存在
            if data['data'] is None:
                raise AssertionError("登录响应data字段为空")

            # 检查token字段
            if 'token' not in data['data']:
                raise AssertionError("登录响应缺少token字段")

            self.token = data['data']['token']
            return True
        except json.JSONDecodeError as e:
            print(f"登录接口响应不是有效的JSON格式: {str(e)}")
            raise AssertionError("登录接口响应格式错误")

    def trigger_job(self):
        """触发定时任务"""
        url = f"{API_BASE_URL}/rtx-quartz/monitor/job/run"
        headers = {
            **API_HEADERS,
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.token}',
            'Origin': API_BASE_URL,
            'Referer': f'{API_BASE_URL}/monitor/job'
        }
        data = {
            "jobId": 210,
            "jobGroup": "DEFAULT"
        }
        response = self.session.put(url, headers=headers, json=data)

        # 断言响应状态码
        assert response.status_code == 200, f"触发定时任务失败，状态码：{response.status_code}"

        # 解析响应数据
        data = response.json()

        # 断言响应数据结构
        assert 'code' in data, "定时任务响应缺少code字段"
        assert data['code'] == 200, f"触发定时任务失败，错误码：{data['code']}"

        return True

    def trigger_bill_job(self):
        """触发账单计费任务"""
        url = f"{API_BASE_URL}/rtx-quartz/monitor/job/run"
        headers = {
            **API_HEADERS,
            'Content-Type': 'application/json;charset=UTF-8',
            'Authorization': f'Bearer {self.token}',
            'Origin': API_BASE_URL,
            'Referer': f'{API_BASE_URL}/monitor/job'
        }
        data = {
            "jobId": 208,
            "jobGroup": "DEFAULT"
        }
        response = self.session.put(url, headers=headers, json=data)

        # 断言响应状态码
        assert response.status_code == 200, f"触发账单计费任务失败，状态码：{response.status_code}"

        # 解析响应数据
        data = response.json()

        # 断言响应数据结构
        assert 'code' in data, "账单计费任务响应缺少code字段"
        assert data['code'] == 200, f"触发账单计费任务失败，错误码：{data['code']}"

        return True

    def trigger_deduct_job(self):
        """触发扣费任务"""
        url = f"{API_BASE_URL}/rtx-quartz/monitor/job/run"
        headers = {
            **API_HEADERS,
            'Content-Type': 'application/json;charset=UTF-8',
            'Authorization': f'Bearer {self.token}',
            'Origin': API_BASE_URL,
            'Referer': f'{API_BASE_URL}/monitor/job'
        }
        data = {
            "jobId": 204,
            "jobGroup": "DEFAULT"
        }

        response = self.session.put(url, headers=headers, json=data)

        # 断言响应状态码
        assert response.status_code == 200, f"触发扣费任务失败，状态码：{response.status_code}"

        # 解析响应数据
        data = response.json()

        # 断言响应数据结构
        assert 'code' in data, "扣费任务响应缺少code字段"
        assert data['code'] == 200, f"触发扣费任务失败，错误码：{data['code']}"

        return True

    def generate_unique_filename(self, bill_dir, bill_date, sftp):
        """生成唯一的文件名"""
        base_filename = f'FMKC-TXB_QLQSMX_{bill_date}'
        for i in range(1, 100):  # 从1到99
            filename = f'{base_filename}_{i:02d}.txt'
            try:
                sftp.stat(os.path.join(bill_dir, filename))
            except FileNotFoundError:
                return filename
        raise Exception("无法生成唯一文件名，已尝试1-99")

    def generate_bill_file(self):
        """生成账单文件（多运营商适配）"""
        try:
            bill_date = self.config['BILL_DATE']
            car_num = self.config['CAR_NUM']
            bill_dir = self.config['BILL_DIR']
            bill_amount = PROCESS_CONFIG['bill_amount']

            print(f"正在准备生成账单文件...")
            print(f"运营商: {self.config['name']}")
            print(f"服务器: {self.config['SSH_HOST']}:{self.config['SSH_PORT']}")
            print(f"目录: {bill_dir}")
            print(f"用户名: {self.config['SSH_USER']}")

            print(f"开始连接服务器...")
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                print(f"尝试SSH连接: {self.config['SSH_HOST']}:{self.config['SSH_PORT']}")
                ssh.connect(
                    hostname=self.config['SSH_HOST'],
                    port=self.config['SSH_PORT'],
                    username=self.config['SSH_USER'],
                    password=self.config['SSH_PASSWORD'],
                    timeout=10
                )
                print(f"服务器连接成功")

                print(f"开始上传文件...")
                sftp = ssh.open_sftp()

                # 检查目录是否存在和权限
                try:
                    dir_stat = sftp.stat(bill_dir)
                    print(f"目标目录存在: {bill_dir}")
                    print(f"目录权限: {oct(dir_stat.st_mode)}")
                    print(f"目录所有者: {dir_stat.st_uid}")
                    print(f"目录所属组: {dir_stat.st_gid}")
                except FileNotFoundError:
                    print(f"目标目录不存在，尝试创建: {bill_dir}")
                    try:
                        sftp.mkdir(bill_dir)
                        print(f"成功创建目录: {bill_dir}")
                    except Exception as e:
                        print(f"创建目录失败: {str(e)}")
                        raise

                # 生成唯一文件名
                filename = self.generate_unique_filename(bill_dir, bill_date, sftp)
                remote_path = bill_dir.rstrip('/') + '/' + filename
                print(f"上传路径: {remote_path}")

                # 生成文件内容
                content = self.config['BILL_CONTENT'](bill_date, car_num, bill_amount)

                # 创建临时文件
                temp_path = remote_path + '.tmp'
                print(f"尝试创建临时文件: {temp_path}")

                # 确保内容是字符串
                if not isinstance(content, str):
                    content = str(content)

                # 将内容转换为字节
                content_bytes = content.encode('utf-8')
                print(f"内容字节长度: {len(content_bytes)}")

                try:
                    # 使用BytesIO创建内存中的文件对象
                    from io import BytesIO
                    file_obj = BytesIO(content_bytes)

                    # 使用putfo方法上传文件
                    print("开始上传文件...")
                    sftp.putfo(file_obj, temp_path)
                    print(f"临时文件上传成功: {temp_path}")

                    # 验证远程文件
                    remote_stat = sftp.stat(temp_path)
                    print(f"远程文件大小: {remote_stat.st_size} 字节")

                    # 重命名临时文件为目标文件
                    print(f"尝试重命名文件...")
                    sftp.rename(temp_path, remote_path)
                    print(f"文件重命名成功: {remote_path}")

                    self.generated_files.append(filename)
                    print(f"账单文件上传成功: {remote_path}")
                    return filename

                except Exception as e:
                    print(f"文件上传错误: {str(e)}")
                    print(f"错误类型: {type(e)}")
                    # 尝试获取更详细的错误信息
                    try:
                        stdin, stdout, stderr = ssh.exec_command(f'ls -la {bill_dir}')
                        print(f"目录权限信息:")
                        print(stdout.read().decode())
                        print(f"错误信息:")
                        print(stderr.read().decode())
                    except Exception as e2:
                        print(f"获取目录信息失败: {str(e2)}")

                    # 清理临时文件
                    try:
                        sftp.remove(temp_path)
                        print(f"远程临时文件清理成功")
                    except:
                        print("远程临时文件清理失败或不存在")
                    raise
                finally:
                    # 关闭文件对象
                    file_obj.close()

            except paramiko.AuthenticationException as e:
                print(f"认证失败: 用户名或密码错误 - {str(e)}")
                raise
            except paramiko.SSHException as ssh_exception:
                print(f"SSH连接错误: {str(ssh_exception)}")
                raise
            except Exception as e:
                print(f"文件上传错误: {str(e)}")
                print(f"错误类型: {type(e)}")
                raise
            finally:
                if 'sftp' in locals():
                    sftp.close()
                if 'ssh' in locals():
                    ssh.close()
                    print("SSH连接已关闭")

        except Exception as e:
            print(f"生成账单文件失败: {str(e)}")
            print(f"错误类型: {type(e)}")
            raise

    def insert_db_record(self, filename):
        """插入数据库记录"""
        # 将YYYYMMDD格式转换为YYYY-MM-DD格式
        bill_date = self.config['BILL_DATE']
        bill_date_formatted = f"{bill_date[:4]}-{bill_date[4:6]}-{bill_date[6:]}"

        # 生成一个在合理范围内的id
        id = random.randint(1, 999999999)

        # 将金额从分转换为元
        bill_amount_fen = float(PROCESS_CONFIG['bill_amount'])
        bill_amount_yuan = bill_amount_fen / 100

        conn = pymysql.connect(**self.config['DB_CONFIG'])
        cursor = conn.cursor()

        try:
            if self.operator == 'TXB':
                sql = """
                INSERT INTO `rtx`.`rtx_bill_file_analyze_record` 
                (`id`, `create_time`, `update_time`, `update_by`, `create_by`, `operator_code`, 
                `file_date`, `download_time`, `file_type`, `file_path`, `backup_file_path`, 
                `file_name`, `file_charset`, `file_size`, `oss_url`, `file_analyze_status`, 
                `clear_date`, `file_total_num`, `file_total_fee`, `deduct_total_num`, 
                `deduct_total_fee`, `file_refund_total_num`, `file_refund_total_fee`, 
                `deduct_refund_total_num`, `deduct_refund_total_fee`, `send_etc_total_num`, 
                `send_etc_total_fee`, `analyze_time`, `remark`, `backhaul_flag`, `analyze_count`) 
                VALUES 
                (%s, %s, %s, '', 'auto', 'TXB', %s, %s, 1, 
                '/diskdata2/rtx/bill/TXB/', NULL, %s, '', '722', 
                'rtx/bill/XTK/2025/1/9/', 1, %s, 1, %s, NULL, NULL, 
                NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, 0, 0)
                """
                current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                cursor.execute(sql, (id, current_time, current_time, bill_date_formatted, current_time, filename,
                                     bill_date_formatted, bill_amount_yuan))
            elif self.operator == 'JS_ETC':
                sql = f"""
                INSERT INTO {self.config['DB_CONFIG']['database']}.{self.config['DB_TABLE']} 
                (id, create_by, update_by, create_time, update_time, bill_date, trading_number, 
                car_num, plate_color, total_fee, service_fee, fee, media_type, card_id, obu_id, 
                en_station_name, ex_station_name, en_time, ex_time, service_type, deduct_time, 
                status, file_path, bill_status, etc_user_id, operator_code, pay_complete_time, 
                file_date, pay_way, callback_flag, callback_msg, bill_year, coupon_deduction_money, 
                user_coupon_id, real_pay_fee, user_wallet_id) 
                VALUES 
                (%s, null, null, %s, %s, %s, '', %s, '0', %s, 0.10, 0.10, '1', 
                '32011234188759745120', '3201123453504221', '亚历山大', '惠州大亚湾万达广场停车场1', 
                %s, %s, '2', %s, 2, %s, 0, 1927558973856796673, 'TXB', null, %s, '5', null, null, 
                2025, 0.00, 0, %s, 1909143820685631489)
                """
                current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                en_time = f"{bill_date_formatted} 07:09:23"
                ex_time = f"{bill_date_formatted} 16:30:17"
                cursor.execute(sql, (id, current_time, current_time, bill_date_formatted,
                                     self.config['CAR_NUM'], bill_amount_yuan,
                                     en_time, ex_time, current_time, filename,
                                     bill_date_formatted, bill_amount_yuan))
            else:
                raise ValueError(f"不支持的运营商类型: {self.operator}")

            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def delete_bill_files(self):
        """删除生成的账单文件"""
        if not self.generated_files:
            return

        print("\n开始删除生成的账单文件...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self.config['SSH_HOST'], username=self.config['SSH_USER'], password=self.config['SSH_PASSWORD'])

        try:
            for filename in self.generated_files:
                remote_path = os.path.join(self.config['BILL_DIR'], filename)
                try:
                    ssh.exec_command(f'rm -f {remote_path}')
                    print(f"已删除文件: {filename}")
                except Exception as e:
                    print(f"删除文件 {filename} 失败: {str(e)}")
        finally:
            ssh.close()
            self.generated_files = []  # 清空文件列表
        print("账单文件删除完成")

    def execute(self):
        """执行完整流程"""
        try:
            # 3. 生成账单文件
            if PROCESS_CONFIG['generate_bill']:
                print("开始生成账单文件...")
                filename = self.generate_bill_file()
                print(f"账单文件生成成功: {filename}")

                # 4. 插入数据库记录
                if PROCESS_CONFIG['insert_db']:
                    print("开始插入数据库记录...")
                    self.insert_db_record(filename)
                    print("数据库记录插入成功")

            # 5. 触发定时任务
            if PROCESS_CONFIG['trigger_job']:
                print("开始触发定时任务...")
                self.trigger_job()
                print("定时任务触发成功")

            # 6. 触发账单计费任务
            if PROCESS_CONFIG['trigger_bill_job']:
                print("开始触发账单计费任务...")
                self.trigger_bill_job()
                print("账单计费任务触发成功")

            # 7. 触发扣费任务
            if PROCESS_CONFIG['trigger_deduct_job']:
                print("等待5秒后执行扣费任务...")
                time.sleep(5)
                print("等待完成，开始执行扣费任务")
                self.trigger_deduct_job()
                print("扣费任务执行完成")

            print("所有操作已完成")
            return True

        except AssertionError as e:
            print(f"接口响应断言失败: {str(e)}")
            return False
        except Exception as e:
            print(f"执行过程中发生错误: {str(e)}")
            return False


def main():
    # 使用配置中的运营商
    operator = PROCESS_CONFIG['operator']
    if operator not in OPERATOR_CONFIGS:
        print(f"错误：不支持的运营商 {operator}")
        print("支持的运营商：")
        for op, config in OPERATOR_CONFIGS.items():
            print(f"- {op}（{config['name']}）")
        return

    creator = RoadFeeCreator(operator=operator)
    print(f"\n当前选择的运营商: {OPERATOR_CONFIGS[operator]['name']}")

    # 先执行登录操作
    print("开始获取验证码...")
    creator.get_captcha()
    print("获取验证码成功")

    print("开始登录...")
    creator.login()
    print("登录成功")

    # 执行循环流程
    for i in range(PROCESS_CONFIG['process_count']):
        print(f"\n开始执行第 {i + 1} 次流程...")
        if creator.execute():
            print(f"第 {i + 1} 次流程执行成功")
        else:
            print(f"第 {i + 1} 次流程执行失败")
        # 每次执行完后等待1秒
        if i < PROCESS_CONFIG['process_count'] - 1:  # 如果不是最后一次执行
            print("等待1秒后执行下一次流程...")
            time.sleep(1)

    print("\n所有流程执行完成")

    # 所有流程执行完成后，如果需要删除账单文件
    if CLEANUP_CONFIG['delete_bill_files']:
        print("\n开始清理账单文件...")
        creator.delete_bill_files()
        print("账单文件清理完成")


if __name__ == "__main__":
    main()
