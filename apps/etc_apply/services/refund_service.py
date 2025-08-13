#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ETC申办退款服务 - 基于批量退款脚本改造
在申办完成后自动执行退款操作
"""

import requests
import json
import os
from typing import Optional, Dict, Any

class RefundService:
    """退款服务类"""
    
    def __init__(self):
        self.config = self._load_config()
        self.base_url = self._get_api_base_url()
        self.captcha_url = f'{self.base_url}/fenmi/code'
        self.login_url = f'{self.base_url}/fenmi/auth/login'
        self.headers = self._get_base_headers()
        self.is_logged_in = False
        
        # 从配置文件读取登录信息
        refund_config = self.config.get('refund', {})
        login_config = refund_config.get('login', {})
        self.login_data = {
            "username": login_config.get('username', 'admin'),
            "password": login_config.get('password', 'mf888769*'),
            "code": "",  # 验证码为空
            "uuid": ""
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """加载ETC配置文件"""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'etc_config.json')
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"[REFUND] 配置文件加载成功: {config_path}")
            return config
        except Exception as e:
            print(f"[REFUND] 读取配置文件失败: {e}")
            print(f"[REFUND] 尝试读取的路径: {config_path}")
            return {}
    
    def _get_api_base_url(self) -> str:
        """从配置中获取API基础URL"""
        base_url = self.config.get('api', {}).get('base_url', 'http://788360p9o5.yicp.fun')
        print(f"[REFUND] API基础URL: {base_url}")
        return base_url
    
    def _get_base_headers(self) -> Dict[str, str]:
        """获取基础请求头"""
        return {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
            'Connection': 'keep-alive',
            'Referer': f'{self.base_url}/fm_admin/login?redirect=%2FtransactionBill%2FpaymentOrder',
            'Origin': f'{self.base_url}',
            'dmType': 'admin',
            'isToken': 'false'
        }
    
    def login(self) -> bool:
        """登录获取token"""
        try:
            # 准备登录数据
            login_data = self.login_data.copy()
            login_data['code'] = ""  # 验证码为空
            login_data['uuid'] = ""  # UUID为空
            
            print(f"[REFUND] 开始登录退款系统...")
            
            # 准备登录请求头
            headers = self.headers.copy()
            headers['Content-Type'] = 'application/json;charset=UTF-8'
            
            # 发送登录请求
            response = requests.post(self.login_url, headers=headers, json=login_data, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200 and result.get('success') == True:
                    token = result.get('data', {}).get('access_token')
                    if token:
                        self.headers['Authorization'] = f'Bearer {token}'
                        self.is_logged_in = True
                        print(f"[REFUND] 登录成功！")
                        return True
            
            print(f"[REFUND] 登录失败: {response.text}")
            return False
            
        except Exception as e:
            print(f"[REFUND] 登录过程发生错误: {e}")
            return False
    
    def get_payment_list_by_goods_name(self, goods_name: str, page_num: int = 1, page_size: int = 10) -> Optional[Dict[str, Any]]:
        """根据商品名称获取支付订单列表"""
        url = f'{self.base_url}/fenmi/pay/payTrade/list'
        
        params = {
            'pageNum': page_num,
            'pageSize': page_size,
            'goodsName': goods_name  # 使用车牌号作为商品名称搜索
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params, verify=False)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    return result
                else:
                    print(f"[REFUND] 获取订单列表失败: {result.get('msg')}")
            elif response.status_code == 401:  # token过期
                print(f"[REFUND] Token已过期，尝试重新登录...")
                if self.login():
                    return self.get_payment_list_by_goods_name(goods_name, page_num, page_size)
                    
        except Exception as e:
            print(f"[REFUND] 获取订单列表时发生错误: {str(e)}")
        return None
    
    def process_refund(self, order: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """处理单个订单退款"""
        url = f'{self.base_url}/fenmi/pay/payTrade/manualRefund'
        data = {
            "id": order['id'],
            "orderDate": int(order['orderDate']),
            "bizOrderNo": order['bizOrderNo']
        }
        
        # 准备请求头
        refund_headers = self.headers.copy()
        refund_headers.update({
            'Content-Type': 'application/json;charset=UTF-8',
            'Origin': f'{self.base_url}',
            'Referer': f'{self.base_url}/fm_admin/transactionBill/paymentOrder'
        })
        
        print(f"[REFUND] 处理退款订单: {order.get('bizOrderNo')}")
        
        try:
            response = requests.post(url, headers=refund_headers, json=data, verify=False)
            
            if response.status_code == 401:  # token过期
                print(f"[REFUND] Token已过期，尝试重新登录...")
                if self.login():
                    return self.process_refund(order)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 200:
                    print(f"[REFUND] ✅ 退款成功: {order.get('bizOrderNo')}")
                    return result
                else:
                    print(f"[REFUND] ❌ 退款失败: {result.get('msg')}")
            else:
                print(f"[REFUND] ❌ 退款请求失败，状态码: {response.status_code}")
            
        except Exception as e:
            print(f"[REFUND] 退款过程发生错误: {e}")
        
        return None
    
    def auto_refund_by_car_num(self, car_num: str) -> Dict[str, Any]:
        """
        根据车牌号自动退款
        :param car_num: 车牌号，用作商品名称搜索
        :return: 退款结果统计
        """
        print(f"[REFUND] 🚗 开始为车牌号 {car_num} 执行自动退款...")
        
        result_summary = {
            'car_num': car_num,
            'success': False,
            'total_orders': 0,
            'refundable_orders': 0,
            'refunded_orders': 0,
            'failed_orders': 0,
            'error_message': None
        }
        
        # 检查退款功能是否启用
        refund_config = self.config.get('refund', {})
        if not refund_config.get('auto_enabled', True):
            print(f"[REFUND] ⚠️ 自动退款功能已禁用，跳过退款")
            result_summary['error_message'] = "自动退款功能已禁用"
            return result_summary
        
        try:
            # 确保已登录
            if not self.is_logged_in:
                if not self.login():
                    result_summary['error_message'] = "登录失败"
                    return result_summary
            
            # 获取所有相关订单
            page_num = 1
            page_size = 50  # 增加每页数量，减少请求次数
            total_refundable = 0
            total_refunded = 0
            total_failed = 0
            
            while True:
                # 获取订单列表
                order_result = self.get_payment_list_by_goods_name(car_num, page_num, page_size)
                if not order_result or not order_result.get('rows'):
                    break
                
                orders = order_result['rows']
                if not orders:
                    break
                
                result_summary['total_orders'] = order_result.get('total', 0)
                
                # 处理可退款订单
                for order in orders:
                    # 只处理支付成功且未退款的订单
                    if order.get('orderStatus') == 'SUCCESS' and order.get('refundTimes') == '0':
                        total_refundable += 1
                        
                        # 执行退款
                        refund_result = self.process_refund(order)
                        if refund_result and refund_result.get('code') == 200:
                            total_refunded += 1
                        else:
                            total_failed += 1
                
                page_num += 1
                
                # 如果当前页订单数小于页面大小，说明已经是最后一页
                if len(orders) < page_size:
                    break
            
            # 更新结果统计
            result_summary.update({
                'success': True,
                'refundable_orders': total_refundable,
                'refunded_orders': total_refunded,
                'failed_orders': total_failed
            })
            
            print(f"[REFUND] 🎯 退款完成统计:")
            print(f"[REFUND]   车牌号: {car_num}")
            print(f"[REFUND]   总订单数: {result_summary['total_orders']}")
            print(f"[REFUND]   可退款订单: {total_refundable}")
            print(f"[REFUND]   成功退款: {total_refunded}")
            print(f"[REFUND]   失败退款: {total_failed}")
            
        except Exception as e:
            result_summary['error_message'] = str(e)
            print(f"[REFUND] ❌ 自动退款过程发生错误: {e}")
        
        return result_summary

# 全局退款服务实例
_refund_service = None

def get_refund_service() -> RefundService:
    """获取退款服务实例（单例模式）"""
    global _refund_service
    if _refund_service is None:
        _refund_service = RefundService()
    return _refund_service

def auto_refund_after_apply(car_num: str) -> Dict[str, Any]:
    """
    ETC申办完成后自动退款的便捷方法
    :param car_num: 车牌号
    :return: 退款结果
    """
    print(f"[REFUND] 🚀 启动ETC申办后自动退款: {car_num}")
    
    refund_service = get_refund_service()
    return refund_service.auto_refund_by_car_num(car_num) 