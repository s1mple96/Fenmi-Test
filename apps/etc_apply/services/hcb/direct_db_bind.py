#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接数据库操作车辆绑定工具 - 修复错误的phone_标识绑定
"""
import sys
import os
import uuid
from datetime import datetime

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from common.mysql_util import MySQLUtil
from apps.etc_apply.services.hcb.truck_core_service import TruckCoreService


def direct_db_bind():
    """直接数据库操作绑定车辆"""
    print("=" * 70)
    print("             货车ETC绑定修复工具")
    print("=" * 70)
    
    print("\n🔍 功能说明：")
    print("用于修复车辆绑定中使用了错误用户ID的问题")
    print("错误格式: phone_xxxxxxxxx 或 wx_xxxxxxxxx")
    print("修复为: 真实的 hcb_userinfo.USERINFO_ID")
    
    print("\n📋 使用步骤：")
    print("1. 查看当前错误绑定状态 - 找出错误的绑定记录")
    print("2. 查找真实用户ID - 基于手机号或身份证查找")
    print("3. 清理错误绑定 + 创建正确绑定 - 一键修复")
    print("4. 仅清理错误绑定 - 只删除错误记录")
    
    choice = input("\n请选择操作（1-4）: ").strip()
    
    try:
        # 连接数据库
        conf = TruckCoreService.get_hcb_mysql_config()
        db = MySQLUtil(**conf)
        db.connect()
        
        # 根据用户选择执行不同操作
        if choice == "1":
            # 查看当前绑定状态
            print("\n=== 查看当前错误绑定状态 ===")
            
            # 查询所有包含错误前缀的绑定记录
            sql_error_bindings = """
            SELECT b.BINDCARREL_ID, b.USERINFO_ID, b.TRUCKUSER_ID, 
                   t.CAR_NUM, t.NAME as truck_name, t.ID_CODE as truck_id_code, 
                   t.ETC_SN, t.OBU_NO, t.PHONE as truck_phone
            FROM hcb.hcb_bindcarrel b
            LEFT JOIN hcb.hcb_truckuser t ON b.TRUCKUSER_ID = t.TRUCKUSER_ID
            WHERE b.FLAG = '1' AND (b.USERINFO_ID LIKE 'phone_%' OR b.USERINFO_ID LIKE 'wx_%')
            ORDER BY b.CREATE_TIME DESC
            LIMIT 20
            """
            error_bindings = db.query(sql_error_bindings)
            
            if error_bindings:
                print(f"\n🔍 找到 {len(error_bindings)} 个错误绑定记录:")
                for i, binding in enumerate(error_bindings, 1):
                    print(f"\n  {i}. ❌ 错误绑定:")
                    print(f"     绑定ID: {binding['BINDCARREL_ID']}")
                    print(f"     错误用户ID: {binding['USERINFO_ID']}")
                    print(f"     货车用户ID: {binding['TRUCKUSER_ID']}")
                    print(f"     车牌: {binding['CAR_NUM'] or '未知'}")
                    print(f"     货车用户: {binding['truck_name'] or '未知'}")
                    print(f"     手机号: {binding['truck_phone'] or '未知'}")
                    print(f"     ETC: {binding['ETC_SN'] or '未分配'}")
                    print(f"     OBU: {binding['OBU_NO'] or '未分配'}")
            else:
                print("✅ 未发现错误的绑定记录 (phone_ 或 wx_ 前缀)")
        
        elif choice == "2":
            # 查找真实用户ID
            print("\n=== 查找真实用户ID ===")
            search_type = input("请选择查询方式：\n1. 手机号\n2. 身份证\n3. OpenID\n请选择（1-3）: ").strip()
            
            if search_type == "1":
                phone = input("请输入手机号: ").strip()
                if phone:
                    sql_user = """
                    SELECT USERINFO_ID, USERNAME, PHONE, ID_CODE, OPENID, STATUS, CREATE_TIME
                    FROM hcb.hcb_userinfo 
                    WHERE PHONE = %s AND STATUS = '1' 
                    ORDER BY CREATE_TIME DESC
                    """
                    users = db.query(sql_user, (phone,))
                    
                    if users:
                        print(f"\n✅ 找到 {len(users)} 个用户记录:")
                        for i, user in enumerate(users, 1):
                            print(f"\n  {i}. 用户ID: {user['USERINFO_ID']}")
                            print(f"     用户名: {user['USERNAME'] or '未设置'}")
                            print(f"     手机号: {user['PHONE']}")
                            print(f"     身份证: {user['ID_CODE'] or '未设置'}")
                            print(f"     状态: {'正常' if user['STATUS'] == '1' else '异常'}")
                            print(f"     创建时间: {user['CREATE_TIME']}")
                    else:
                        print(f"❌ 未找到手机号 {phone} 对应的用户记录")
            
            elif search_type == "2":
                id_code = input("请输入身份证号: ").strip()
                if id_code:
                    sql_user = """
                    SELECT USERINFO_ID, USERNAME, PHONE, ID_CODE, OPENID, STATUS, CREATE_TIME
                    FROM hcb.hcb_userinfo 
                    WHERE ID_CODE = %s AND STATUS = '1' 
                    ORDER BY CREATE_TIME DESC
                    """
                    users = db.query(sql_user, (id_code,))
                    
                    if users:
                        print(f"\n✅ 找到 {len(users)} 个用户记录:")
                        for i, user in enumerate(users, 1):
                            print(f"\n  {i}. 用户ID: {user['USERINFO_ID']}")
                            print(f"     用户名: {user['USERNAME'] or '未设置'}")
                            print(f"     手机号: {user['PHONE'] or '未设置'}")
                            print(f"     身份证: {user['ID_CODE']}")
                            print(f"     状态: {'正常' if user['STATUS'] == '1' else '异常'}")
                            print(f"     创建时间: {user['CREATE_TIME']}")
                    else:
                        print(f"❌ 未找到身份证号 {id_code} 对应的用户记录")
            
            elif search_type == "3":
                openid = input("请输入OpenID: ").strip()
                if openid:
                    sql_user = """
                    SELECT USERINFO_ID, USERNAME, PHONE, ID_CODE, OPENID, STATUS, CREATE_TIME
                    FROM hcb.hcb_userinfo 
                    WHERE OPENID = %s AND STATUS = '1' 
                    ORDER BY CREATE_TIME DESC
                    """
                    users = db.query(sql_user, (openid,))
                    
                    if users:
                        print(f"\n✅ 找到 {len(users)} 个用户记录:")
                        for i, user in enumerate(users, 1):
                            print(f"\n  {i}. 用户ID: {user['USERINFO_ID']}")
                            print(f"     用户名: {user['USERNAME'] or '未设置'}")
                            print(f"     手机号: {user['PHONE'] or '未设置'}")
                            print(f"     身份证: {user['ID_CODE'] or '未设置'}")
                            print(f"     OpenID: {user['OPENID']}")
                            print(f"     状态: {'正常' if user['STATUS'] == '1' else '异常'}")
                            print(f"     创建时间: {user['CREATE_TIME']}")
                    else:
                        print(f"❌ 未找到OpenID {openid} 对应的用户记录")
            else:
                print("❌ 无效选择")
                
        elif choice == "3":
            # 清理错误绑定 + 创建正确绑定
            print("\n=== 清理错误绑定 + 创建正确绑定 ===")
            
            truck_user_id = input("请输入货车用户ID: ").strip()
            error_user_id = input("请输入要清理的错误用户ID (如: phone_15818376788): ").strip()
            real_user_id = input("请输入真实的用户ID: ").strip()
            
            if truck_user_id and error_user_id and real_user_id:
                print(f"\n⚠️  即将执行:")
                print(f"   删除错误绑定: {error_user_id} <-> {truck_user_id}")
                print(f"   创建正确绑定: {real_user_id} <-> {truck_user_id}")
                
                confirm = input("\n确认执行吗？(y/N): ").strip().lower()
                
                if confirm in ['y', 'yes']:
                    # 删除错误绑定
                    sql_delete = "DELETE FROM hcb.hcb_bindcarrel WHERE USERINFO_ID = %s AND TRUCKUSER_ID = %s"
                    deleted_count = db.execute(sql_delete, (error_user_id, truck_user_id))
                    print(f"✅ 已删除 {deleted_count} 个错误绑定记录")
                    
                    # 创建新的正确绑定
                    bindcarrel_id = str(uuid.uuid4()).replace('-', '')
                    create_time = datetime.now().strftime('%Y%m%d%H%M%S')
                    
                    sql_insert = """
                    INSERT INTO hcb.hcb_bindcarrel 
                    (BINDCARREL_ID, USERINFO_ID, TRUCKUSER_ID, CREATE_TIME, FLAG) 
                    VALUES (%s, %s, %s, %s, '1')
                    """
                    
                    db.execute(sql_insert, (bindcarrel_id, real_user_id, truck_user_id, create_time))
                    print(f"✅ 已创建新的绑定记录")
                    print(f"   绑定ID: {bindcarrel_id}")
                    print(f"   用户ID: {real_user_id}")
                    print(f"   货车用户ID: {truck_user_id}")
                    print(f"   创建时间: {create_time}")
                else:
                    print("❌ 操作已取消")
            else:
                print("❌ 输入信息不完整")
        
        elif choice == "4":
            # 仅清理错误绑定
            print("\n=== 仅清理错误绑定（不重新绑定）===")
            
            truck_user_id = input("请输入货车用户ID: ").strip()
            error_user_id = input("请输入要清理的错误用户ID (如: phone_15818376788): ").strip()
            
            if truck_user_id and error_user_id:
                print(f"\n⚠️  即将删除错误绑定:")
                print(f"   错误用户ID: {error_user_id}")
                print(f"   货车用户ID: {truck_user_id}")
                
                confirm = input("\n确认删除吗？(y/N): ").strip().lower()
                
                if confirm in ['y', 'yes']:
                    sql_delete = "DELETE FROM hcb.hcb_bindcarrel WHERE USERINFO_ID = %s AND TRUCKUSER_ID = %s"
                    deleted_count = db.execute(sql_delete, (error_user_id, truck_user_id))
                    print(f"✅ 已删除 {deleted_count} 个错误绑定记录")
                else:
                    print("❌ 操作已取消")
            else:
                print("❌ 输入信息不完整")
        
        else:
            print("❌ 无效选择")
        
        db.close()
        
    except Exception as e:
        print(f"\n❌ 操作失败: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        direct_db_bind()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户取消操作")
    except Exception as e:
        print(f"\n❌ 程序异常: {str(e)}")
    
    input("\n按回车键退出...") 