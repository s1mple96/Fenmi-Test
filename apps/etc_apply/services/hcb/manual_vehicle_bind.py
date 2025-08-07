#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动车辆绑定工具
用于在ETC申办完成后手动绑定车辆到用户账户
"""
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from apps.etc_apply.services.hcb.truck_data_service import TruckDataService


def manual_bind_vehicle():
    """手动绑定车辆工具"""
    print("=" * 60)
    print("           ETC车辆手动绑定工具")
    print("=" * 60)
    
    # 获取用户输入
    print("\n请输入以下信息完成车辆绑定：")
    
    phone = input("手机号码（优先使用，推荐）: ").strip()
    if not phone:
        phone = None
    
    openid = input("微信OpenID（可选，直接回车跳过）: ").strip()
    if not openid:
        openid = None
    
    id_code = input("身份证号码: ").strip()
    if not id_code:
        print("❌ 身份证号码不能为空！")
        return
    
    truck_user_id = input("货车用户ID（从申办结果中获取）: ").strip()
    if not truck_user_id:
        print("❌ 货车用户ID不能为空！")
        return
    
    truck_etc_apply_id = input("申办ID（从申办结果中获取）: ").strip()
    if not truck_etc_apply_id:
        print("❌ 申办ID不能为空！")
        return
    
    car_num = input("车牌号码: ").strip()
    if not car_num:
        print("❌ 车牌号码不能为空！")
        return
    
    print("\n" + "-" * 60)
    print("确认绑定信息:")
    if phone:
        print(f"手机号: {phone}")
    print(f"身份证号: {id_code}")
    print(f"车牌号: {car_num}")
    print(f"货车用户ID: {truck_user_id}")
    print(f"申办ID: {truck_etc_apply_id}")
    if openid:
        print(f"微信OpenID: {openid}")
    
    confirm = input("\n确认绑定？(y/N): ").strip().lower()
    if confirm != 'y':
        print("❌ 取消绑定")
        return
    
    try:
        print("\n⏳ 正在执行绑定...")
        
        # 调用绑定方法（优先使用手机号）
        result = TruckDataService.manual_bind_user_vehicle(
            phone=phone,
            openid=openid,
            id_code=id_code,
            truck_user_id=truck_user_id,
            truck_etc_apply_id=truck_etc_apply_id,
            car_num=car_num
        )
        
        if result.get('success'):
            print("\n✅ 车辆绑定成功！")
            print(f"绑定关系ID: {result['bindcarrel_id']}")
            print(f"用户ID: {result['userinfo_id']}")
            print(f"货车用户ID: {result['truckuser_id']}")
            print(f"绑定时间: {result['create_time']}")
        else:
            print(f"\n❌ 绑定失败: {result.get('message', '未知错误')}")
            if result.get('error'):
                print(f"详细错误: {result['error']}")
        
    except Exception as e:
        print(f"\n❌ 绑定过程中发生异常: {str(e)}")


if __name__ == "__main__":
    try:
        manual_bind_vehicle()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户取消操作")
    except Exception as e:
        print(f"\n❌ 程序运行异常: {str(e)}")
    
    input("\n按回车键退出...") 