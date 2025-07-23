#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试获取Jenkins构建提交人信息的功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.components.ui_jenkins_builder import (
    get_commit_author_from_api,
    get_commit_author_from_log,
    get_commit_author,
    JENKINS_URL,
    JENKINS_USER,
    JENKINS_TOKEN
)

def test_get_commit_author():
    """测试获取提交人信息"""
    # 测试项目名和构建号（请根据实际情况修改）
    test_job = "test-hcb-api-server"  # 替换为实际的项目名
    test_build_number = 969    # 替换为实际的构建号
    
    print(f"测试项目: {test_job}")
    print(f"构建号: {test_build_number}")
    print("-" * 50)
    
    # 测试从API获取
    print("1. 从Jenkins API获取提交人信息:")
    try:
        authors_api = get_commit_author_from_api(test_job, test_build_number)
        if authors_api:
            print(f"   成功获取到 {len(authors_api)} 个提交人:")
            for i, author in enumerate(authors_api, 1):
                print(f"   {i}. 姓名: {author['name']}")
                if author['email']:
                    print(f"      邮箱: {author['email']}")
        else:
            print("   未获取到提交人信息")
    except Exception as e:
        print(f"   获取失败: {e}")
    
    print()
    
    # 测试从日志解析
    print("2. 从控制台日志解析提交人信息:")
    try:
        authors_log = get_commit_author_from_log(test_job, test_build_number)
        if authors_log:
            print(f"   成功解析到 {len(authors_log)} 个提交人:")
            for i, author in enumerate(authors_log, 1):
                print(f"   {i}. 姓名: {author['name']}")
                if author['email']:
                    print(f"      邮箱: {author['email']}")
        else:
            print("   未解析到提交人信息")
    except Exception as e:
        print(f"   解析失败: {e}")
    
    print()
    
    # 测试综合获取
    print("3. 综合获取提交人信息:")
    try:
        authors = get_commit_author(test_job, test_build_number)
        if authors:
            print(f"   成功获取到 {len(authors)} 个提交人:")
            for i, author in enumerate(authors, 1):
                print(f"   {i}. 姓名: {author['name']}")
                if author['email']:
                    print(f"      邮箱: {author['email']}")
        else:
            print("   未获取到提交人信息")
    except Exception as e:
        print(f"   获取失败: {e}")

def test_jenkins_connection():
    """测试Jenkins连接"""
    import requests
    
    print("测试Jenkins连接...")
    try:
        # 测试基本连接
        api_url = f"{JENKINS_URL}api/json"
        resp = requests.get(api_url, auth=(JENKINS_USER, JENKINS_TOKEN), timeout=10)
        print(f"Jenkins连接状态: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            jobs = data.get('jobs', [])
            print(f"可用项目数量: {len(jobs)}")
            if jobs:
                print("前5个项目:")
                for i, job in enumerate(jobs[:5], 1):
                    print(f"  {i}. {job['name']}")
        else:
            print(f"连接失败: {resp.text}")
    except Exception as e:
        print(f"连接异常: {e}")

if __name__ == "__main__":
    print("Jenkins提交人信息获取测试")
    print("=" * 50)
    
    # 先测试连接
    test_jenkins_connection()
    print()
    
    # 测试提交人信息获取
    test_get_commit_author()
    
    print("\n测试完成！")
    print("\n使用说明:")
    print("1. 请修改 test_job 和 test_build_number 为实际的项目名和构建号")
    print("2. 确保Jenkins配置正确（JENKINS_URL, JENKINS_USER, JENKINS_TOKEN）")
    print("3. 如果API获取失败，会自动尝试从日志解析") 