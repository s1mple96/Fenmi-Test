# -*- coding: utf-8 -*-
# -------------------------------------------------------------
# vin17.com首页VIN爬虫工具
# 抓取"最近查询的车辆识别代号（VIN）"区域所有VIN号，保存到data/vin_list.txt
# 支持手动运行和import调用，详细中文注释
# -------------------------------------------------------------
import os
import re
import requests
from bs4 import BeautifulSoup

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
VIN_FILE = os.path.join(DATA_DIR, 'vin_list.txt')


def get_recent_vins(save_file: bool = True) -> list:
    """
    抓取vin17.com首页最近查询的VIN号，返回VIN列表，并可保存到文件
    :param save_file: 是否保存到data/vin_list.txt
    :return: VIN号列表
    """
    url = 'https://vin17.com/'
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, 'html.parser')
    # 通过正则匹配17位VIN号（大写字母和数字）
    vin_pattern = re.compile(r'\b[A-HJ-NPR-Z0-9]{17}\b')
    vins = set()
    for tag in soup.find_all(text=vin_pattern):
        for vin in vin_pattern.findall(tag):
            vins.add(vin)
    vin_list = sorted(vins)
    if save_file:
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        with open(VIN_FILE, 'w', encoding='utf-8') as f:
            for vin in vin_list:
                f.write(vin + '\n')
    return vin_list


def get_latest_vin():
    """
    获取最近抓取的一个VIN号（如无则返回空字符串）
    """
    vins = get_recent_vins(save_file=False)
    return vins[-1] if vins else ""


if __name__ == '__main__':
    vins = get_recent_vins()
    print(f'共抓取到{len(vins)}个VIN号，已保存到 {VIN_FILE}')
    for vin in vins:
        print(vin) 