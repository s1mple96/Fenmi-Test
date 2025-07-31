# -*- coding: utf-8 -*-
# -------------------------------------------------------------
# requests 工具类，封装常用 HTTP 请求方法
# 支持 GET/POST/PUT/DELETE/下载等，便于接口自动化
# -------------------------------------------------------------
import requests
from typing import Optional, Dict, Any, Union

class RequestsUtil:
    @staticmethod
    def get(url: str, params: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        """
        发送GET请求
        :param url: 请求地址
        :param params: 查询参数
        :param headers: 请求头
        :param kwargs: 其他 requests 支持的参数
        :return: Response对象
        """
        return requests.get(url, params=params, headers=headers, **kwargs)

    @staticmethod
    def post(url: str, data: Optional[Union[Dict[str, Any], str]] = None, json: Optional[Dict[str, Any]] = None,
             headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        """
        发送POST请求
        :param url: 请求地址
        :param data: form表单数据
        :param json: json数据
        :param headers: 请求头
        :param kwargs: 其他 requests 支持的参数
        :return: Response对象
        """
        return requests.post(url, data=data, json=json, headers=headers, **kwargs)

    @staticmethod
    def put(url: str, data: Optional[Union[Dict[str, Any], str]] = None, json: Optional[Dict[str, Any]] = None,
            headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        """
        发送PUT请求
        :param url: 请求地址
        :param data: form表单数据
        :param json: json数据
        :param headers: 请求头
        :param kwargs: 其他 requests 支持的参数
        :return: Response对象
        """
        return requests.put(url, data=data, json=json, headers=headers, **kwargs)

    @staticmethod
    def delete(url: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> requests.Response:
        """
        发送DELETE请求
        :param url: 请求地址
        :param headers: 请求头
        :param kwargs: 其他 requests 支持的参数
        :return: Response对象
        """
        return requests.delete(url, headers=headers, **kwargs)

    @staticmethod
    def request(method: str, url: str, **kwargs) -> requests.Response:
        """
        通用请求方法
        :param method: 请求方法（GET/POST/PUT/DELETE等）
        :param url: 请求地址
        :param kwargs: 其他 requests 支持的参数
        :return: Response对象
        """
        return requests.request(method, url, **kwargs)

    @staticmethod
    def download_file(url: str, save_path: str, headers: Optional[Dict[str, str]] = None, **kwargs) -> None:
        """
        下载文件
        :param url: 文件下载地址
        :param save_path: 保存路径
        :param headers: 请求头
        :param kwargs: 其他 requests 支持的参数
        """
        with requests.get(url, headers=headers, stream=True, **kwargs) as r:
            r.raise_for_status()
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
