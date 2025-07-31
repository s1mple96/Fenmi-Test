#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复版本的打包脚本
确保配置文件被正确包含
"""

import subprocess
import sys
import os
import shutil

def main():
    print("🚀 修复版本打包脚本")
    print("="*50)
    
    # 检查必要文件
    required_files = [
        "apps/etc_apply/main_window.py",
        "config/app_config.json",
        "config/connections.json"
    ]
    
    for file_path in required_files:
        if not os.path.exists(file_path):
            print(f"❌ 缺少必要文件: {file_path}")
            return 1
    
    print("✅ 所有必要文件检查完成")
    
    # 清理之前的构建
    for dir_name in ["dist", "build"]:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"🧹 已清理目录: {dir_name}")
    
    # 删除旧的spec文件
    if os.path.exists("ETC申办工具.spec"):
        os.remove("ETC申办工具.spec")
        print("🧹 已删除旧的spec文件")
    
    # 构建打包命令
    cmd = [
        "pyinstaller",
        "--onefile",                    # 打包成单个文件
        "--windowed",                   # 不显示控制台窗口
        "--name", "ETC申办工具",        # 指定exe文件名
        "--add-data", "config;config",  # 添加配置文件
        "--add-data", "apps/etc_apply/ui;apps/etc_apply/ui",  # 添加UI文件
        "--add-data", "apps/etc_apply/services;apps/etc_apply/services",  # 添加服务文件
        "--add-data", "common;common",  # 添加公共文件
        "--hidden-import", "PyQt5.QtCore",
        "--hidden-import", "PyQt5.QtWidgets", 
        "--hidden-import", "PyQt5.QtGui",
        "--hidden-import", "PyQt5.QtNetwork",
        "--hidden-import", "pymysql",
        "--hidden-import", "requests",
        "--hidden-import", "json",
        "--hidden-import", "csv",
        "--hidden-import", "os",
        "--hidden-import", "sys",
        "--hidden-import", "threading",
        "--hidden-import", "datetime",
        "--hidden-import", "uuid",
        "--hidden-import", "random",
        "--collect-all", "PyQt5",
        "apps/etc_apply/main_window.py"
    ]
    
    print("🔨 开始打包...")
    print(f"📋 命令: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True)
        print("✅ 打包成功！")
        
        # 检查生成的文件
        exe_path = "dist/ETC申办工具.exe"
        if os.path.exists(exe_path):
            file_size = os.path.getsize(exe_path) / 1024 / 1024
            print(f"📁 exe文件位置: {exe_path}")
            print(f"📊 文件大小: {file_size:.1f} MB")
            
            # 复制配置文件到dist目录
            if os.path.exists("config"):
                config_dest = "dist/config"
                if os.path.exists(config_dest):
                    shutil.rmtree(config_dest)
                shutil.copytree("config", config_dest)
                print("📁 已复制配置文件到dist目录")
            
            print("\n" + "="*50)
            print("🎉 打包完成！")
            print("="*50)
            print("📋 使用说明:")
            print("   1. 进入 dist 目录")
            print("   2. 双击 'ETC申办工具.exe' 运行")
            print("   3. 配置文件已复制到dist/config目录")
            print("   4. 如需修改配置，可编辑dist/config目录中的文件")
            print("="*50)
            
            return 0
        else:
            print("❌ exe文件未生成")
            return 1
            
    except subprocess.CalledProcessError as e:
        print(f"❌ 打包失败，退出码: {e.returncode}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 