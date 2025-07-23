import pytest
from utils.requestsUtil import RequestsUtil
from utils.log_util import LogUtil

logger = LogUtil.get_logger('test_requestsUtil')

class TestRequestsUtil:
    def test_get(self):
        response = RequestsUtil.get('https://httpbin.org/get', params={'test': 'value'})
        logger.info(f'GET请求返回: {response.status_code}, 内容: {response.text[:100]}')
        assert response.status_code == 200
        assert response.json()['args']['test'] == 'value'

    def test_post(self):
        response = RequestsUtil.post('https://httpbin.org/post', json={'key': 'value'})
        logger.info(f'POST请求返回: {response.status_code}, 内容: {response.text[:100]}')
        assert response.status_code == 200
        assert response.json()['json']['key'] == 'value'

    def test_put(self):
        response = RequestsUtil.put('https://httpbin.org/put', json={'put': 'yes'})
        logger.info(f'PUT请求返回: {response.status_code}, 内容: {response.text[:100]}')
        assert response.status_code == 200
        assert response.json()['json']['put'] == 'yes'

    def test_delete(self):
        response = RequestsUtil.delete('https://httpbin.org/delete')
        logger.info(f'DELETE请求返回: {response.status_code}, 内容: {response.text[:100]}')
        assert response.status_code == 200

    def test_request(self):
        response = RequestsUtil.request('GET', 'https://httpbin.org/get', params={'foo': 'bar'})
        logger.info(f'REQUEST方法返回: {response.status_code}, 内容: {response.text[:100]}')
        assert response.status_code == 200
        assert response.json()['args']['foo'] == 'bar'

    def test_download_file(self, tmp_path):
        url = 'https://httpbin.org/image/png'
        save_path = tmp_path / 'test.png'
        RequestsUtil.download_file(url, str(save_path))
        logger.info(f'文件下载到: {save_path}, 文件大小: {save_path.stat().st_size}')
        assert save_path.exists()
        assert save_path.stat().st_size > 0
