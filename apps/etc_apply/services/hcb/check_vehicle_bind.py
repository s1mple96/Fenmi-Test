#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
车辆绑定状态检查工具
用于验证ETC车辆是否已正确绑定到用户
"""
import sys
import os

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from common.mysql_util import MySQLUtil
from apps.etc_apply.services.hcb.truck_core_service import TruckCoreService


def check_vehicle_bind_status():
    """检查车辆绑定状态"""
    print("=" * 60)
    print("           ETC车辆绑定状态检查")
    print("=" * 60)
    
    # 获取用户输入
    print("\n请选择查询方式：")
    print("1. 按手机号查询")
    print("2. 按身份证号查询")
    print("3. 按车牌号查询")
    print("4. 按货车用户ID查询")
    
    choice = input("请选择（1-4）: ").strip()
    
    try:
        # 连接数据库
        conf = TruckCoreService.get_hcb_mysql_config()
        db = MySQLUtil(**conf)
        db.connect()
        
        if choice == "1":
            # 按手机号查询
            phone = input("请输入手机号: ").strip()
            if not phone:
                print("❌ 手机号不能为空！")
                return
            
            # 查找用户ID
            sql_user = """
            SELECT USER_ID, NAME, ID_CODE FROM hcb.hcb_userinfo 
            WHERE PHONE = %s AND FLAG = '1' 
            ORDER BY CREATE_TIME DESC
            """
            users = db.query_all(sql_user, (phone,))
            
            if not users:
                print(f"❌ 未找到手机号为 {phone} 的用户")
                # 查找是否有基于手机号的标识
                user_id_pattern = f"phone_{phone}"
                sql_bind = """
                SELECT BINDCARREL_ID, USERINFO_ID, TRUCKUSER_ID, CREATE_TIME 
                FROM hcb.hcb_bindcarrel 
                WHERE USERINFO_ID LIKE %s AND FLAG = '1'
                """
                binds = db.query_all(sql_bind, (f"{user_id_pattern}%",))
                if binds:
                    print(f"✅ 找到基于手机号标识的绑定记录：")
                    for bind in binds:
                        print(f"   绑定ID: {bind[0]}")
                        print(f"   用户标识: {bind[1]}")
                        print(f"   货车用户ID: {bind[2]}")
                        print(f"   绑定时间: {bind[3]}")
                        
                        # 查询对应的车牌信息
                        sql_truck = """
                        SELECT CAR_NUM FROM hcb.hcb_truck_user 
                        WHERE USER_ID = %s AND FLAG = '1'
                        """
                        truck = db.query_one(sql_truck, (bind[2],))
                        if truck:
                            print(f"   绑定车牌: {truck[0]}")
                        print()
                return
            
            print(f"✅ 找到 {len(users)} 个用户记录：")
            for i, user in enumerate(users, 1):
                user_id = user[0]
                name = user[1]
                id_code = user[2]
                print(f"\n--- 用户 {i} ---")
                print(f"用户ID: {user_id}")
                print(f"姓名: {name}")
                print(f"身份证: {id_code}")
                
                # 查询绑定记录
                sql_bind = """
                SELECT BINDCARREL_ID, TRUCKUSER_ID, CREATE_TIME 
                FROM hcb.hcb_bindcarrel 
                WHERE USERINFO_ID = %s AND FLAG = '1'
                ORDER BY CREATE_TIME DESC
                """
                binds = db.query_all(sql_bind, (user_id,))
                
                if binds:
                    print(f"✅ 找到 {len(binds)} 个车辆绑定记录：")
                    for bind in binds:
                        print(f"   绑定ID: {bind[0]}")
                        print(f"   货车用户ID: {bind[1]}")
                        print(f"   绑定时间: {bind[2]}")
                        
                        # 查询车牌信息
                        sql_truck = """
                        SELECT CAR_NUM FROM hcb.hcb_truck_user 
                        WHERE USER_ID = %s AND FLAG = '1'
                        """
                        truck = db.query_one(sql_truck, (bind[1],))
                        if truck:
                            print(f"   绑定车牌: {truck[0]}")
                else:
                    print("❌ 没有车辆绑定记录")
        
        elif choice == "2":
            # 按身份证号查询
            id_code = input("请输入身份证号: ").strip()
            if not id_code:
                print("❌ 身份证号不能为空！")
                return
            
            sql_user = """
            SELECT USER_ID, NAME, PHONE FROM hcb.hcb_userinfo 
            WHERE ID_CODE = %s AND FLAG = '1'
            ORDER BY CREATE_TIME DESC
            """
            users = db.query_all(sql_user, (id_code,))
            
            if not users:
                print(f"❌ 未找到身份证号为 {id_code} 的用户")
                return
            
            # 处理查询结果（同手机号查询逻辑）
            print(f"✅ 找到 {len(users)} 个用户记录：")
            for user in users:
                user_id = user[0]
                name = user[1]
                phone = user[2]
                print(f"\n用户ID: {user_id}")
                print(f"姓名: {name}")
                print(f"手机号: {phone}")
                
                # 查询绑定记录
                sql_bind = """
                SELECT BINDCARREL_ID, TRUCKUSER_ID, CREATE_TIME 
                FROM hcb.hcb_bindcarrel 
                WHERE USERINFO_ID = %s AND FLAG = '1'
                ORDER BY CREATE_TIME DESC
                """
                binds = db.query_all(sql_bind, (user_id,))
                
                if binds:
                    print(f"✅ 找到 {len(binds)} 个车辆绑定记录：")
                    for bind in binds:
                        print(f"   绑定ID: {bind[0]}")
                        print(f"   货车用户ID: {bind[1]}")
                        print(f"   绑定时间: {bind[2]}")
                        
                        # 查询车牌信息
                        sql_truck = """
                        SELECT CAR_NUM FROM hcb.hcb_truck_user 
                        WHERE USER_ID = %s AND FLAG = '1'
                        """
                        truck = db.query_one(sql_truck, (bind[1],))
                        if truck:
                            print(f"   绑定车牌: {truck[0]}")
                else:
                    print("❌ 没有车辆绑定记录")
        
        elif choice == "3":
            # 按车牌号查询
            car_num = input("请输入车牌号: ").strip()
            if not car_num:
                print("❌ 车牌号不能为空！")
                return
            
            # 先找到车辆对应的货车用户ID
            sql_truck = """
            SELECT USER_ID, NAME, PHONE, ID_CODE FROM hcb.hcb_truck_user 
            WHERE CAR_NUM = %s AND FLAG = '1'
            ORDER BY CREATE_TIME DESC
            """
            trucks = db.query_all(sql_truck, (car_num,))
            
            if not trucks:
                print(f"❌ 未找到车牌号为 {car_num} 的车辆记录")
                return
            
            print(f"✅ 找到 {len(trucks)} 个车辆记录：")
            for truck in trucks:
                truck_user_id = truck[0]
                name = truck[1]
                phone = truck[2]
                id_code = truck[3]
                print(f"\n--- 车辆信息 ---")
                print(f"货车用户ID: {truck_user_id}")
                print(f"车主姓名: {name}")
                print(f"手机号: {phone}")
                print(f"身份证: {id_code}")
                
                # 查询绑定记录
                sql_bind = """
                SELECT BINDCARREL_ID, USERINFO_ID, CREATE_TIME 
                FROM hcb.hcb_bindcarrel 
                WHERE TRUCKUSER_ID = %s AND FLAG = '1'
                ORDER BY CREATE_TIME DESC
                """
                binds = db.query_all(sql_bind, (truck_user_id,))
                
                if binds:
                    print(f"✅ 找到 {len(binds)} 个用户绑定记录：")
                    for bind in binds:
                        print(f"   绑定ID: {bind[0]}")
                        print(f"   用户ID: {bind[1]}")
                        print(f"   绑定时间: {bind[2]}")
                else:
                    print("❌ 此车辆未绑定到任何用户")
        
        elif choice == "4":
            # 按货车用户ID查询
            truck_user_id = input("请输入货车用户ID: ").strip()
            if not truck_user_id:
                print("❌ 货车用户ID不能为空！")
                return
            
            # 查询车辆信息
            sql_truck = """
            SELECT CAR_NUM, NAME, PHONE, ID_CODE FROM hcb.hcb_truck_user 
            WHERE USER_ID = %s AND FLAG = '1'
            """
            truck = db.query_one(sql_truck, (truck_user_id,))
            
            if not truck:
                print(f"❌ 未找到货车用户ID为 {truck_user_id} 的记录")
                return
            
            car_num = truck[0]
            name = truck[1]
            phone = truck[2]
            id_code = truck[3]
            
            print(f"\n--- 车辆信息 ---")
            print(f"车牌号: {car_num}")
            print(f"车主姓名: {name}")
            print(f"手机号: {phone}")
            print(f"身份证: {id_code}")
            
            # 查询绑定记录
            sql_bind = """
            SELECT BINDCARREL_ID, USERINFO_ID, CREATE_TIME 
            FROM hcb.hcb_bindcarrel 
            WHERE TRUCKUSER_ID = %s AND FLAG = '1'
            ORDER BY CREATE_TIME DESC
            """
            binds = db.query_all(sql_bind, (truck_user_id,))
            
            if binds:
                print(f"✅ 找到 {len(binds)} 个用户绑定记录：")
                for bind in binds:
                    print(f"   绑定ID: {bind[0]}")
                    print(f"   用户ID: {bind[1]}")
                    print(f"   绑定时间: {bind[2]}")
                    
                    # 如果用户ID不是标识格式，查询用户详细信息
                    if not (bind[1].startswith('phone_') or bind[1].startswith('wx_') or bind[1].startswith('id_')):
                        sql_user = """
                        SELECT NAME, PHONE, ID_CODE FROM hcb.hcb_userinfo 
                        WHERE USER_ID = %s AND FLAG = '1'
                        """
                        user = db.query_one(sql_user, (bind[1],))
                        if user:
                            print(f"   用户姓名: {user[0]}")
                            print(f"   用户手机: {user[1]}")
                            print(f"   用户身份证: {user[2]}")
            else:
                print("❌ 此车辆未绑定到任何用户")
        
        else:
            print("❌ 无效的选择")
            return
        
        db.close()
        
    except Exception as e:
        print(f"\n❌ 查询过程中发生异常: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        check_vehicle_bind_status()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户取消操作")
    except Exception as e:
        print(f"\n❌ 程序运行异常: {str(e)}")
    
    input("\n按回车键退出...") 