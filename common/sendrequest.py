import json
import allure
import pytest
import requests
import urllib3
import time

from conf import setting
from common.recordlog import logs
from requests import utils
from common.readyaml import ReadYamlData
from requests.packages.urllib3.exceptions import InsecureRequestWarning


class SendRequest:
    """
    接口请求封装类
    主要功能：
    1. 封装 GET / POST 请求
    2. 统一处理请求异常
    3. 记录接口请求与响应日志
    4. 处理 Cookie 并写入 yaml 文件
    """

    def __init__(self, cookie=None):
        """
        初始化方法
        :param cookie: 初始 cookie，可选
        """
        self.cookie = cookie
        # 读取/写入 yaml 数据的工具类
        self.read = ReadYamlData()

    def get(self, url, data, header):
        """
        发送 GET 请求
        :param url: 接口地址
        :param data: 请求参数（None 或 dict）
        :param header: 请求头
        :return: response_dict（响应信息字典）
        """
        # 禁用 HTTPS 证书告警
        requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        try:
            # 无参数 GET 请求
            if data is None:
                response = requests.get(url, headers=header, cookies=self.cookie, verify=False)
            # 带参数 GET 请求
            else:
                response = requests.get(url, data, headers=header, cookies=self.cookie, verify=False)
        except requests.RequestException as e:
            logs.error(e)
            return None
        except Exception as e:
            logs.error(e)
            return None
        # 响应时间/毫秒
        res_ms = response.elapsed.microseconds / 1000
        # 响应时间/秒
        res_second = response.elapsed.total_seconds()
        response_dict = dict()

        # 接口响应状态码
        response_dict['code'] = response.status_code
        # 接口响应文本
        response_dict['text'] = response.text
        try:
            response_dict['body'] = response.json().get('body')
        except Exception:
            response_dict['body'] = ''
        response_dict['res_ms'] = res_ms
        response_dict['res_second'] = res_second
        return response_dict

    def post(self, url, data, header):
        """
        发送 POST 请求
        :param url:
        :param data: verify=False忽略SSL证书验证
        :param header:
        :return:
        """
        # 控制台输出InsecureRequestWarning错误
        requests.packages.urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        try:
            if data is None:
                response = requests.post(url, header, cookies=self.cookie, verify=False)
            else:
                response = requests.post(url, data, headers=header, cookies=self.cookie, verify=False)
        except requests.RequestException as e:
            logs.error(e)
            return None
        except Exception as e:
            logs.error(e)
            return None
        # 响应时间/毫秒
        res_ms = response.elapsed.microseconds / 1000
        # 响应时间/秒
        res_second = response.elapsed.total_seconds()
        response_dict = dict()
        # 接口响应状态码
        response_dict['code'] = response.status_code
        # 接口响应文本
        response_dict['text'] = response.text
        try:
            response_dict['body'] = response.json().get('body')
        except Exception:
            response_dict['body'] = ''
        response_dict['res_ms'] = res_ms
        response_dict['res_second'] = res_second
        return response_dict

    def send_request(self, **kwargs):
        """
        通用请求方法（基于 requests.session）
        支持所有 HTTP 方法（GET/POST/PUT/DELETE 等）
        :param kwargs: requests.request 所需参数
        :return: Response 对象
        """
        session = requests.session()
        result = None
        cookie = {}
        try:
            # 发送请求
            result = session.request(**kwargs)
            # 从响应中获取 cookie
            set_cookie = requests.utils.dict_from_cookiejar(result.cookies)
            if set_cookie:
                # 将 cookie 写入 yaml 文件，供后续接口使用
                cookie['Cookie'] = set_cookie
                self.read.write_yaml_data(cookie)
                logs.info("cookie：%s" % cookie)
            logs.info("接口返回信息：%s" % result.text if result.text else result)
        except requests.exceptions.ConnectionError:
            logs.error("ConnectionError--连接异常")
            pytest.fail("接口请求异常，可能是request的连接数过多或请求速度过快导致程序报错！")
        except requests.exceptions.HTTPError:
            logs.error("HTTPError--http异常")
        except requests.exceptions.RequestException as e:
            logs.error(e)
            pytest.fail("请求异常，请检查系统或数据是否正常！")
        return result

    def run_main(self, name, url, case_name, header, method, cookies=None, file=None, **kwargs):
        """
        接口主入口方法（测试框架调用
        :param name: 接口名
        :param url: 接口地址
        :param case_name: 测试用例
        :param header:请求头
        :param method:请求方法
        :param cookies：默认为空
        :param file: 上传文件接口
        :param kwargs: 请求参数，根据yaml文件的参数类型
        :return:
        """

        try:
            # 收集报告日志
            logs.info('接口名称：%s' % name)
            logs.info('请求地址：%s' % url)
            logs.info('请求方式：%s' % method)
            logs.info('测试用例名称：%s' % case_name)
            logs.info('请求头：%s' % header)
            logs.info('Cookie：%s' % cookies)
            # 将请求参数转换为 JSON 字符串（用于报告展示）
            req_params = json.dumps(kwargs, ensure_ascii=False)

            # 判断请求参数类型并写入 Allure 报告
            if "data" in kwargs.keys():
                allure.attach(req_params, '请求参数', allure.attachment_type.TEXT)
                logs.info("请求参数：%s" % kwargs)
            elif "json" in kwargs.keys():
                allure.attach(req_params, '请求参数', allure.attachment_type.TEXT)
                logs.info("请求参数：%s" % kwargs)
            elif "params" in kwargs.keys():
                allure.attach(req_params, '请求参数', allure.attachment_type.TEXT)
                logs.info("请求参数：%s" % kwargs)
        except Exception as e:
            logs.error(e)
        # time.sleep(0.5)
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        response = self.send_request(method=method,
                                     url=url,
                                     headers=header,
                                     cookies=cookies,
                                     files=file,
                                     timeout=setting.API_TIMEOUT,
                                     verify=False,
                                     **kwargs)
        return response
