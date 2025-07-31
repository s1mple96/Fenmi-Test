import datetime
import os
import threading
import time
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog, Toplevel, Label, Button

import requests

os.environ['NO_PROXY'] = 'qyapi.weixin.qq.com'

# Jenkins配置（请填写你的信息）
JENKINS_URL = 'http://192.168.1.77:8899/jenkins/'
JENKINS_USER = 'test'
JENKINS_TOKEN = '11bf3a7a8d63ec59261bbff8204b62c189'

# 企业微信机器人Webhook
WECHAT_WEBHOOK = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=c6afa257-0628-4ef6-bc1e-f7fffb550bb3'


# 测试机器人
# WECHAT_WEBHOOK = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=1f787608-ecc2-4667-a030-c9fc93b01ad5'


# 获取Jenkins CSRF crumb
def get_jenkins_crumb():
    crumb_url = f"{JENKINS_URL}crumbIssuer/api/json"
    try:
        resp = requests.get(crumb_url, auth=(JENKINS_USER, JENKINS_TOKEN), timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return {data['crumbRequestField']: data['crumb']}
    except Exception:
        pass
    return {}


# 获取所有Jenkins项目名
def get_jenkins_jobs():
    api_url = f"{JENKINS_URL}api/json"
    try:
        resp = requests.get(api_url, auth=(JENKINS_USER, JENKINS_TOKEN), timeout=10)
        resp.raise_for_status()
        jobs = resp.json().get('jobs', [])
        return [job['name'] for job in jobs]
    except Exception as e:
        return []


# 触发Jenkins构建，返回queueId
def trigger_build(job_name):
    build_url = f"{JENKINS_URL}job/{job_name}/buildWithParameters"
    headers = get_jenkins_crumb()
    data = {
        "BRANCH": "origin/test",
        "deploy_env": "test"
    }
    resp = requests.post(build_url, auth=(JENKINS_USER, JENKINS_TOKEN), headers=headers, data=data,
                         allow_redirects=False, proxies={"http": None, "https": None})
    print(f"DEBUG: {job_name} status={resp.status_code}, text={resp.text}")
    if resp.status_code in (201, 200, 202):
        queue_url = resp.headers.get('Location')
        if queue_url:
            # queue_url 可能是相对路径
            if queue_url.startswith('/'):
                queue_url = JENKINS_URL.rstrip('/') + queue_url
            return True, queue_url
        else:
            return True, None
    return False, None


# 通过queueUrl获取build number
def get_build_number_from_queue(queue_url):
    for _ in range(60):  # 最多等10分钟
        try:
            resp = requests.get(queue_url + 'api/json', auth=(JENKINS_USER, JENKINS_TOKEN),
                                proxies={"http": None, "https": None})
            if resp.status_code == 200:
                data = resp.json()
                if 'executable' in data and data['executable'] and 'number' in data['executable']:
                    return data['executable']['number']
                if data.get('cancelled'):
                    return None
        except Exception:
            pass
        time.sleep(2)
    return None


# 获取指定build number的状态
def get_build_status_by_number(job_name, build_number):
    url = f"{JENKINS_URL}job/{job_name}/{build_number}/api/json"
    try:
        resp = requests.get(url, auth=(JENKINS_USER, JENKINS_TOKEN), proxies={"http": None, "https": None})
        if resp.status_code == 200:
            data = resp.json()
            return data.get('result'), data.get('building'), data
    except Exception:
        pass
    return None, None, None


# 获取最后一次构建编号
def get_last_build_number(job_name):
    url = f"{JENKINS_URL}job/{job_name}/api/json"
    try:
        resp = requests.get(url, auth=(JENKINS_USER, JENKINS_TOKEN), proxies={"http": None, "https": None})
        if resp.status_code == 200:
            data = resp.json()
            return data.get('lastBuild', {}).get('number')
    except Exception:
        pass
    return None


# 企业微信通知
def send_wechat_msg(content):
    data = {
        "msgtype": "text",
        "text": {"content": content}
    }
    try:
        resp = requests.post(
            WECHAT_WEBHOOK,
            json=data,
            timeout=5,
            proxies={"http": None, "https": None}
        )
        print(f"WECHAT DEBUG: status={resp.status_code}, text={resp.text}")
        return resp.status_code == 200
    except Exception as e:
        print(f"WECHAT ERROR: {e}")
        return False


def send_wechat_msg_markdown(success_jobs, fail_jobs):
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    msg = '【Jenkins通知】\n\n**构建结果如下：**\n'
    if success_jobs:
        msg += '> 🟢 **成功项目：**\n'
        for job in success_jobs:
            msg += f'> - 【{job}】\n'
    if fail_jobs:
        msg += '> 🔴 **失败项目：**\n'
        for job in fail_jobs:
            msg += f'> - 【{job}】\n'
    msg += f'---\n_通知时间：{now}_'
    data = {
        "msgtype": "markdown",
        "markdown": {"content": msg}
    }
    try:
        resp = requests.post(
            WECHAT_WEBHOOK,
            json=data,
            timeout=5,
            proxies={"http": None, "https": None}
        )
        print(f"WECHAT DEBUG: status={resp.status_code}, text={resp.text}")
        return resp.status_code == 200
    except Exception as e:
        print(f"WECHAT ERROR: {e}")
        return False


def send_wechat_msg_list_style(build_results):
    msg = (
        "# 🚀 Jenkins构建结果通知\n"
        "---\n"
        "**构建结果：**\n"
    )
    for job, (status, finish_time) in build_results.items():
        state = '✅成功' if status == 'SUCCESS' else '❌失败'
        msg += f"- {job}  {state}  {finish_time}\n"
    msg += "---\n> 如有失败请及时关注Jenkins日志详情。"
    data = {
        "msgtype": "markdown",
        "markdown": {"content": msg}
    }
    try:
        resp = requests.post(
            WECHAT_WEBHOOK,
            json=data,
            timeout=5,
            proxies={"http": None, "https": None}
        )
        print(f"WECHAT DEBUG: status={resp.status_code}, text={resp.text}")
        return resp.status_code == 200
    except Exception as e:
        print(f"WECHAT ERROR: {e}")
        return False


def send_wechat_msg_custom(build_info_list, build_results):
    msg = "🚀 Jenkins构建结果通知\n\n构建结果：\n"
    for job, build_number in build_info_list:
        status, finish_time = build_results.get(job, ('未知', ''))
        state = "构建成功" if status == 'SUCCESS' else "构建失败"
        log_url = f"{JENKINS_URL}job/{job}/{build_number}/console"
        msg += f"【{job}】{state}  时间：{finish_time}  [日志]({log_url})\n"
    msg += "\n如有失败请及时关注Jenkins日志详情。"
    data = {
        "msgtype": "markdown",
        "markdown": {"content": msg}
    }
    try:
        resp = requests.post(
            WECHAT_WEBHOOK,
            json=data,
            timeout=5,
            proxies={"http": None, "https": None}
        )
        print(f"WECHAT DEBUG: status={resp.status_code}, text={resp.text}")
        return resp.status_code == 200
    except Exception as e:
        print(f"WECHAT ERROR: {e}")
        return False


def send_wechat_msg_grouped(build_results, skipped_jobs, commit_msgs_map):
    msg = "# 🚀 **[Jenkins]构建通知**\n---\n构建结果如下：\n\n"
    success_jobs = []
    fail_jobs = []
    finish_times = []
    for job, (status, finish_time) in build_results.items():
        if finish_time:
            finish_times.append(finish_time)
        if status == 'SUCCESS':
            success_jobs.append(job)
        else:
            fail_jobs.append(job)
    if success_jobs:
        msg += "🟢成功项目：\n"
        for job in success_jobs:
            msg += f"- [{job}]\n"
            # 展示提交人信息
            if job in commit_msgs_map and commit_msgs_map[job]:
                for cm in commit_msgs_map[job]:
                    msg += f"    - 代码提交说明：{cm}\n"
        msg += "\n"
    if fail_jobs:
        msg += "🔴失败项目：\n"
        for job in fail_jobs:
            msg += f"- [{job}]\n"
            # 展示提交人信息
            if job in commit_msgs_map and commit_msgs_map[job]:
                for cm in commit_msgs_map[job]:
                    msg += f"    - 代码提交说明：{cm}\n"
        msg += "\n"
    if skipped_jobs:
        msg += "⏭️跳过项目：\n"
        for job in skipped_jobs:
            msg += f"- [{job}]\n"
        msg += "\n"
    msg += "---\n"
    if finish_times:
        last_time = max(finish_times)
        msg += f"完成时间：{last_time}\n"
    else:
        msg += "完成时间：无\n"
    msg += "💡 tip：可以开始测试了，请注意代码的[**提交说明**]和[**需求编号**]是否与TAPD一致\n"
    data = {
        "msgtype": "markdown",
        "markdown": {"content": msg}
    }
    try:
        resp = requests.post(
            WECHAT_WEBHOOK,
            json=data,
            timeout=5,
            proxies={"http": None, "https": None}
        )
        print(f"WECHAT DEBUG: status={resp.status_code}, text={resp.text}")
        return resp.status_code == 200
    except Exception as e:
        print(f"WECHAT ERROR: {e}")
        return False


# 提取项目简写
def extract_project_keys(text):
    # 支持空格、英文逗号、中文逗号、中文顿号等混合分隔符
    import re
    match = re.search(r'发版项目[:：\s]+([\w\-\s,，、]+)', text)
    if match:
        keys_str = match.group(1).strip()
        keys = re.split(r'[ ,，、]+', keys_str)
        return [k for k in keys if k]
    # 兜底：提取所有可能的项目名
    return re.findall(r'[a-zA-Z0-9\-]+', text)


# 模糊匹配
def fuzzy_match(key, job_list):
    for job in job_list:
        if key.lower() in job.lower():
            return job
    return None


# 多选弹窗
class MultiSelectDialog(simpledialog.Dialog):
    def __init__(self, parent, title, options):
        self.options = list(options)
        self.selected = []
        self.result = None
        self._result_set = False
        super().__init__(parent, title)

    def body(self, master):
        tk.Label(master, text='匹配到多个项目，请选择要构建的项目：').pack(anchor='w')
        self.vars = []
        for opt in self.options:
            var = tk.BooleanVar()
            cb = tk.Checkbutton(master, text=opt, variable=var)
            cb.pack(anchor='w')
            self.vars.append((var, opt))
        return None

    def apply(self):
        if not self._result_set:
            self.selected = [opt for var, opt in self.vars if var.get()]
            self.result = self.selected
            self._result_set = True

    def cancel(self, event=None):
        if not self._result_set:
            self.result = None
            self._result_set = True
        super().cancel(event)


# 自定义弹窗，按钮为“跳过”和“继续”
def ask_skip_or_continue(root, job):
    result = {'skip': None}

    def on_skip():
        result['skip'] = True
        win.destroy()

    def on_continue():
        result['skip'] = False
        win.destroy()

    win = Toplevel(root)
    win.title('提示')
    Label(win, text=f'项目【{job}】当前正在构建中，是否跳过本次构建？').pack(padx=20, pady=10)
    btn_frame = tk.Frame(win)
    btn_frame.pack(pady=10)
    Button(btn_frame, text='跳过', width=10, command=on_skip).pack(side='left', padx=10)
    Button(btn_frame, text='继续', width=10, command=on_continue).pack(side='left', padx=10)
    win.grab_set()
    win.wait_window()
    return result['skip']


# 获取commit message从日志
def get_commit_message_from_log(job_name, build_number):
    import re
    url = f"{JENKINS_URL}job/{job_name}/{build_number}/consoleText"
    try:
        resp = requests.get(url, auth=(JENKINS_USER, JENKINS_TOKEN), proxies={"http": None, "https": None})
        if resp.status_code == 200:
            log = resp.text
            # 匹配所有 commit message: "xxx"，不区分大小写
            matches = re.findall(r'commit message: "([\s\S]+?)"', log, re.IGNORECASE)
            if matches:
                return matches
    except Exception:
        pass
    return []


# 构建主流程
class JenkinsBuilderApp:
    def __init__(self, root):
        self.root = root
        self.root.title('Jenkins一键构建工具')
        self.root.geometry('600x400')

        tk.Label(root, text='请粘贴发版备注文本：').pack(anchor='w', padx=10, pady=5)
        self.input_text = scrolledtext.ScrolledText(root, height=5)
        self.input_text.pack(fill='x', padx=10)

        self.build_btn = tk.Button(root, text='一键构建', command=self.on_build)
        self.build_btn.pack(pady=10)

        tk.Label(root, text='日志输出：').pack(anchor='w', padx=10, pady=5)
        self.log_text = scrolledtext.ScrolledText(root, height=12, state='disabled')
        self.log_text.pack(fill='both', expand=True, padx=10, pady=(0, 10))

        self.job_list = []
        self.refresh_jobs()

    def log(self, msg):
        self.log_text.config(state='normal')
        self.log_text.insert('end', msg + '\n')
        self.log_text.see('end')
        self.log_text.config(state='disabled')

    def refresh_jobs(self):
        self.log('正在获取Jenkins项目列表...')
        self.job_list = get_jenkins_jobs()
        if self.job_list:
            self.log(f'获取到{len(self.job_list)}个项目。')
        else:
            self.log('获取Jenkins项目失败，请检查配置。')

    def on_build(self):
        text = self.input_text.get('1.0', 'end').strip()
        if not text:
            messagebox.showwarning('提示', '请输入或粘贴发版备注文本！')
            return
        self.build_btn.config(state='disabled')
        self.log('开始解析项目简写...')
        keys = extract_project_keys(text)
        if not keys:
            self.log('未提取到任何项目简写。')
            self.build_btn.config(state='normal')
            return
        self.log(f'提取到项目简写：{keys}')
        # 匹配所有简写对应的项目（去除-和_后再比对）
        all_matched = {}
        for key in keys:
            matched = []
            key_norm = key.replace('-', '').replace('_', '').lower()
            for job in self.job_list:
                job_norm = job.replace('-', '').replace('_', '').lower()
                if key_norm in job_norm:
                    matched.append(job)
            all_matched[key] = matched
        # 输出匹配到的项目
        for key in keys:
            if all_matched[key]:
                self.log(f'简写【{key}】匹配到的项目有：')
                for job in all_matched[key]:
                    self.log(f'  {job}')
            else:
                self.log(f'简写【{key}】未匹配到任何Jenkins项目。')
        skipped_jobs = []
        selected_jobs = []

        def select_jobs_for_key(key, matched):
            if not matched:
                return []
            if len(matched) == 1:
                return [matched[0]]
            print(f'弹窗前 self.root.update()')
            self.root.update()
            dlg = MultiSelectDialog(self.root, f'选择构建项目 - {key}', matched)
            self.root.update()
            print(f'弹窗后 dlg.result: {dlg.result}')
            if dlg.result is None:
                print('select_jobs_for_key: 用户取消')
                return None  # 用户取消
            print(f'select_jobs_for_key: 用户选择 {dlg.result}')
            return dlg.result  # 可能为空列表，表示未选

        for key in keys:
            matched = all_matched[key]
            jobs = select_jobs_for_key(key, matched)
            if jobs is None:
                self.log('用户取消了操作。')
                self.build_btn.config(state='normal')
                return
            if not jobs:
                self.log(f'简写【{key}】未选择任何项目，已跳过。')
                skipped_jobs.append(key)
                continue
            selected_jobs.extend(jobs)
        if selected_jobs:
            jobs_str = '\n'.join([f'【{job}】' for job in selected_jobs])
            self.log(f'需要构建的项目有：\n{jobs_str}')
        else:
            self.log('未选择任何需要构建的项目。')
            self.build_btn.config(state='normal')
            return
        # 先批量询问所有项目是否跳过
        to_build = []
        for job in selected_jobs:
            last_build_number = get_last_build_number(job)
            building = False
            if last_build_number:
                _, building, _ = get_build_status_by_number(job, last_build_number)
            if building:
                skip = ask_skip_or_continue(self.root, job)
                if skip:
                    self.log(f'项目【{job}】正在构建中，已跳过。')
                    skipped_jobs.append(job)
                    continue
            to_build.append(job)
        if not to_build:
            self.log('没有需要构建的项目。')
            self.build_btn.config(state='normal')
            return
        # 启动后台线程
        threading.Thread(target=self.build_projects, args=(to_build, skipped_jobs), daemon=True).start()

    def build_projects(self, to_build, skipped_jobs):
        try:
            build_info_list = []  # [(job, build_number)]
            # 并发触发所有 to_build 项目
            trigger_results = []  # [(job, queue_url)]
            for job in to_build:
                self.log(f'开始构建项目：{job} ...')
                ok, queue_url = trigger_build(job)
                if not ok:
                    self.log(f'触发构建失败：{job}')
                    continue
                self.log(f'已触发构建：{job}，等待分配构建编号...')
                trigger_results.append((job, queue_url))
            if not trigger_results:
                self.log('没有成功触发任何项目的构建。')
                return
            # 并发轮询所有queue_url获取build_number
            build_info_list = []  # [(job, build_number)]
            for job, queue_url in trigger_results:
                build_number = None
                if queue_url:
                    build_number = get_build_number_from_queue(queue_url)
                if build_number:
                    self.log(f'项目【{job}】本次构建编号：{build_number}')
                    build_info_list.append((job, build_number))
                else:
                    self.log(f'未能获取到项目【{job}】的构建编号，可能未成功进入构建队列。')
            if not build_info_list:
                self.log('没有成功触发任何项目的构建。')
                return
            self.log('所有项目已触发构建，开始后台轮询状态...')
            # 轮询所有项目状态
            build_results = {}  # job: (status, finish_time)
            commit_msgs_map = {}  # job: [commit messages]
            for _ in range(60):  # 最多等10分钟
                all_done = True
                for job, build_number in build_info_list:
                    if job in build_results:
                        continue
                    result, building, build_info = get_build_status_by_number(job, build_number)
                    if building:
                        all_done = False
                        continue
                    if result:
                        finish_time = ''
                        commit_msgs = []
                        if build_info:
                            if build_info.get('timestamp') and build_info.get('duration') is not None:
                                finish_ms = build_info['timestamp'] + build_info['duration']
                                import datetime
                                finish_dt = datetime.datetime.fromtimestamp(finish_ms / 1000)
                                finish_time = finish_dt.strftime('%Y-%m-%d %H:%M:%S')
                            for cs in build_info.get('changeSets', []):
                                for item in cs.get('items', []):
                                    cm = item.get('msg', '')
                                    if cm:
                                        commit_msgs.append(cm)
                        if not commit_msgs:
                            commit_msgs = get_commit_message_from_log(job, build_number)
                        build_results[job] = (result, finish_time)
                        commit_msgs_map[job] = commit_msgs
                    else:
                        all_done = False
                if all_done:
                    break
                time.sleep(10)
            send_wechat_msg_grouped(build_results, skipped_jobs, commit_msgs_map)
            msg = '# 🚀 **[Jenkins]构建通知**\n---\n构建结果如下：\n'
            if build_results:
                for job, (status, finish_time) in build_results.items():
                    state = '✅成功' if status == 'SUCCESS' else '❌失败'
                    msg += f'- [{job}]  {state}  {finish_time}\n'
                    # 显示提交人信息
                    if job in commit_msgs_map and commit_msgs_map[job]:
                        for cm in commit_msgs_map[job]:
                            msg += f'    - 提交说明：{cm}\n'
            self.log(msg.strip())
            self.log('所有项目处理完毕。')

            # 构建完成3秒后自动关闭主窗口
            def close_window():
                try:
                    self.root.destroy()
                except Exception:
                    pass

            self.root.after(3000, close_window)
        finally:
            self.build_btn.config(state='normal')


if __name__ == '__main__':
    # 启动主程序
    root = tk.Tk()
    app = JenkinsBuilderApp(root)
    root.mainloop()
