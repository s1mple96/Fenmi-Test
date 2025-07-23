import requests
import time
import json
import base64
import urllib.parse
from datetime import datetime


#批量退款脚本

# 配置信息
BASE_URL = 'http://788360p9o5.yicp.fun'
CAPTCHA_URL = f'{BASE_URL}/fenmi/code'
LOGIN_URL = f'{BASE_URL}/fenmi/auth/login'
GOODS_NAME = ''  # 添加商品名称配置

# 登录信息
LOGIN_DATA = {
    "username": "admin",
    "password": "mf888769*",
    "code": "",  # 验证码为空
    "uuid": ""
}

# 基础请求头
base_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Connection': 'keep-alive',
    'Referer': 'http://788360p9o5.yicp.fun/fm_admin/login?redirect=%2FtransactionBill%2FpaymentOrder',
    'Origin': 'http://788360p9o5.yicp.fun',
    'dmType': 'admin',
    'isToken': 'false'
}

def process_captcha_result(captcha_str):
    """处理验证码结果，将浮点数转换为整数"""
    # 由于验证码已取消，直接返回空字符串
    return ""

def process_base64(img_base64):
    """处理base64字符串"""
    # 由于验证码已取消，直接返回空字符串
    return ""

def get_captcha():
    """获取验证码信息"""
    print("验证码已取消，直接返回空值")
    return {
        'uuid': '',
        'img': ''
    }

def recognize_captcha(img_base64, max_retries=3):
    """使用超级鹰识别验证码，带重试机制"""
    # 由于验证码已取消，直接返回空字符串
    return ""

def login():
    """登录获取token"""
    global headers  # 添加全局声明以修改headers
    
    # 准备登录数据
    login_data = LOGIN_DATA.copy()
    login_data['code'] = ""  # 验证码为空
    login_data['uuid'] = ""  # UUID为空
    
    print(f"登录请求数据: {json.dumps(login_data, ensure_ascii=False)}")
    
    # 准备登录请求头
    headers = base_headers.copy()
    headers['Content-Type'] = 'application/json;charset=UTF-8'
    
    print(f"登录请求头: {json.dumps(headers, ensure_ascii=False)}")
    
    # 发送登录请求
    response = requests.post(LOGIN_URL, headers=headers, json=login_data, verify=False)
    print(f"登录响应状态码: {response.status_code}")
    print(f"登录响应内容: {response.text}")
    
    if response.status_code == 200:
        result = response.json()
        if result.get('code') == 200 and result.get('success') == True:
            token = result.get('data', {}).get('access_token')
            if token:
                headers['Authorization'] = f'Bearer {token}'
                print("登录成功！")
                return True
    print("登录失败，请检查账号密码是否正确")
    return False

def get_payment_list(page_num=1, page_size=10):
    """获取支付订单列表"""
    url = f'{BASE_URL}/fenmi/pay/payTrade/list'
    # 获取当前日期
    today = datetime.now().strftime('%Y-%m-%d')

    params = {
        'pageNum': page_num,
        'pageSize': page_size,
        # 'createTime[0]': today,
        # 'createTime[1]': today,
        # 'startCreateTime': today,
        # 'endCreateTime': today,
        'goodsName': GOODS_NAME  # 添加商品名称参数
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, verify=False)
        print(f"获取订单列表响应状态码: {response.status_code}")
        print(f"获取订单列表响应内容: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 200:
                return result
            else:
                print(f"获取订单列表失败: {result.get('msg')}")
        elif response.status_code == 401:  # token过期
            print("Token已过期，尝试重新登录...")
            if login():
                return get_payment_list(page_num, page_size)
    except Exception as e:
        print(f"获取订单列表时发生错误: {str(e)}")
    return None

def process_refund(order):
    """处理单个订单退款"""
    url = f'{BASE_URL}/fenmi/pay/payTrade/manualRefund'
    data = {
        "id": order['id'],
        "orderDate": int(order['orderDate']),
        "bizOrderNo": order['bizOrderNo']
    }
    
    # 准备请求头
    refund_headers = headers.copy()
    refund_headers.update({
        'Content-Type': 'application/json;charset=UTF-8',
        'Origin': 'http://788360p9o5.yicp.fun',
        'Referer': 'http://788360p9o5.yicp.fun/fm_admin/transactionBill/paymentOrder'
    })
    
    print(f"退款请求URL: {url}")
    print(f"退款请求数据: {json.dumps(data, ensure_ascii=False)}")
    print(f"退款请求头: {json.dumps(refund_headers, ensure_ascii=False)}")
    
    response = requests.post(url, headers=refund_headers, json=data, verify=False)
    print(f"退款响应状态码: {response.status_code}")
    print(f"退款响应内容: {response.text}")
    
    if response.status_code == 401:  # token过期
        print("Token已过期，尝试重新登录...")
        if login():
            return process_refund(order)
    return response.json() if response.status_code == 200 else None

def main():
    """主函数"""
    if not login():
        print("登录失败，程序退出")
        return
    
    total_orders = 0
    refundable_orders = 0
    page_num = 1
    page_size = 10
    
    while True:
        result = get_payment_list(page_num, page_size)
        if not result or not result.get('rows'):
            break
            
        orders = result['rows']
        if not orders:
            break
            
        total_orders = result.get('total', 0)  # 使用API返回的总数
        for order in orders:
            if order.get('orderStatus') == 'SUCCESS' and order.get('refundTimes') == '0':  # 只处理支付成功且未退款的订单
                refundable_orders += 1
                print(f"处理订单: {order.get('bizOrderNo')}")
                process_refund(order)
                
        page_num += 1
        
    print(f"\n处理完成！")
    print(f"总订单数: {total_orders}")
    print(f"可退款订单数: {refundable_orders}")

if __name__ == '__main__':
    main() 