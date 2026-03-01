import json
import re
from json.decoder import JSONDecodeError

import allure
import jsonpath

from common.assertions import Assertions
from common.debugtalk import DebugTalk
from common.readyaml import get_testcase_yaml, ReadYamlData
from common.recordlog import logs
from common.sendrequest import SendRequest
from conf.operationConfig import OperationConfig
from conf.setting import FILE_PATH


class RequestBase:

    def __init__(self):
        self.run = SendRequest()
        self.conf = OperationConfig()
        self.read = ReadYamlData()
        self.asserts = Assertions()

    def replace_load(self, data):
        """yaml数据替换解析"""
        str_data = data
        if not isinstance(data, str):
            str_data = json.dumps(data, ensure_ascii=False)
            # print('从yaml文件获取的原始数据：', str_data)
        for i in range(str_data.count('${')):
            if '${' in str_data and '}' in str_data:
                start_index = str_data.index('$')
                end_index = str_data.index('}', start_index)
                ref_all_params = str_data[start_index:end_index + 1]
                # 取出yaml文件的函数名
                func_name = ref_all_params[2:ref_all_params.index("(")]
                # 取出函数里面的参数
                func_params = ref_all_params[ref_all_params.index("(") + 1:ref_all_params.index(")")]
                # 传入替换的参数获取对应的值,类的反射----getattr,setattr,del....
                extract_data = getattr(DebugTalk(), func_name)(*func_params.split(',') if func_params else "")

                if extract_data and isinstance(extract_data, list):
                    extract_data = ','.join(e for e in extract_data)
                str_data = str_data.replace(ref_all_params, str(extract_data))
                # print('通过解析后替换的数据：', str_data)

        # 还原数据
        if data and isinstance(data, dict):
            data = json.loads(str_data)
        else:
            data = str_data
        return data

    def specification_yaml(self, base_info, test_case):
        """
        接口请求处理基本方法
        :param base_info: yaml文件里面的baseInfo
        :param test_case: yaml文件里面的testCase
        :return:
        """
        try:
            params_type = ['data', 'json', 'params']
            url_host = self.conf.get_section_for_data('api_envi', 'host')
            api_name = base_info['api_name']
            allure.attach(api_name, f'接口名称：{api_name}', allure.attachment_type.TEXT)
            url = url_host + base_info['url']
            allure.attach(api_name, f'接口地址：{url}', allure.attachment_type.TEXT)
            method = base_info['method']
            allure.attach(api_name, f'请求方法：{method}', allure.attachment_type.TEXT)
            header = self.replace_load(base_info['header'])
            allure.attach(api_name, f'请求头：{header}', allure.attachment_type.TEXT)
            # 处理cookie
            cookie = None
            if base_info.get('cookies') is not None:
                cookie = eval(self.replace_load(base_info['cookies']))
            case_name = test_case.pop('case_name')
            allure.attach(api_name, f'测试用例名称：{case_name}', allure.attachment_type.TEXT)
            # 处理断言
            val = self.replace_load(test_case.get('validation'))
            test_case['validation'] = val
            validation = eval(test_case.pop('validation'))
            # 处理参数提取
            extract = test_case.pop('extract', None)
            extract_list = test_case.pop('extract_list', None)
            # 处理接口的请求参数
            for key, value in test_case.items():
                if key in params_type:
                    test_case[key] = self.replace_load(value)

            # 处理文件上传接口
            file, files = test_case.pop('files', None), None
            if file is not None:
                for fk, fv in file.items():
                    allure.attach(json.dumps(file), '导入文件')
                    files = {fk: open(fv, mode='rb')}

            res = self.run.run_main(name=api_name, url=url, case_name=case_name, header=header, method=method,
                                    file=files, cookies=cookie, **test_case)
            status_code = res.status_code
            allure.attach(self.allure_attach_response(res.json()), '接口响应信息', allure.attachment_type.TEXT)

            try:
                res_json = json.loads(res.text)  # 把json格式转换成字典字典
                if extract is not None:
                    self.extract_data(extract, res.text)
                if extract_list is not None:
                    self.extract_data_list(extract_list, res.text)
                # 处理断言
                self.asserts.assert_result(validation, res_json, status_code)
            except JSONDecodeError as js:
                logs.error('系统异常或接口未请求！')
                raise js
            except Exception as e:
                logs.error(e)
                raise e

        except Exception as e:
            raise e

    @classmethod
    def allure_attach_response(cls, response):
        # 判断响应是否为字典类型
        if isinstance(response, dict):
            # 将字典转换为格式化的 JSON 字符串
            # ensure_ascii=False: 保证中文等非 ASCII 字符正常显示
            allure_response = json.dumps(response, ensure_ascii=False, indent=4)
        else:
            # 非字典类型（如字符串、bytes 等）直接使用原数据
            allure_response = response
        # 返回处理后的响应内容，用于 allure 报告附件挂载
        return allure_response

    def extract_data(self, testcase_extarct, response):
        """
        从接口返回值中提取指定字段，并将提取结果写入YAML文件
        使用jsonpath语法定位JSON格式返回值中的目标数据
        :param testcase_extarct: dict类型，testcase文件yaml中配置的extract节点数据
                                 结构示例: {"token": "$.data.token", "user_id": "$.data.id"}
        :param response: str类型，接口请求后返回的原始响应文本（JSON格式字符串）
        :return: None
        """
        try:
            # 遍历提取配置中的每一组 变量名-jsonpath表达式
            for key, value in testcase_extarct.items():
                # 判断值是否包含$符号，识别是否为jsonpath提取表达式
                if '$' in value:
                    # 1. 将接口返回的JSON字符串解析为Python列表
                    # 2. 使用jsonpath表达式提取目标数据，取第一个匹配结果
                    #    jsonpath.jsonpath()返回列表，[0]取第一个元素
                    ext_json = jsonpath.jsonpath(json.loads(response), value)[0]
                    # 判断是否成功提取到数据
                    if ext_json:
                        # 构造提取结果字典：{变量名: 提取到的值}
                        extarct_data = {key: ext_json}
                        # 记录提取成功的日志
                        logs.info('提取接口的返回值：', extarct_data)
                    else:
                        # 提取结果为空时，构造提示信息
                        extarct_data = {key: '未提取到数据，请检查接口返回值是否为空！'}

                    # 将提取结果写入YAML文件（供后续用例使用）
                    self.read.write_yaml_data(extarct_data)

        # 捕获所有异常并记录错误日志
        except Exception as e:
            logs.error(f"提取接口返回值时发生异常：{e}")

    def extract_data_list(self, testcase_extract_list, response):
        """
        提取多个参数，json提取，提取结果以列表形式返回
        参数说明：
        :param testcase_extract_list: yaml文件中的extract_list信息，格式为字典类型
        :param response: 接口的实际返回值,字符串类型(str)
        :return: 无返回值，提取结果直接写入yaml文件
        """
        try:
            # 遍历extract_list字典中的所有键值对
            for key, value in testcase_extract_list.items():
                # 判断是否使用jsonpath表达式（以"$"开头的路径表达式）
                if "$" in value:
                    # 将接口返回的字符串响应转换为json格式
                    # 使用jsonpath从json数据中提取指定路径的值
                    ext_json = jsonpath.jsonpath(json.loads(response), value)

                    # 增加提取判断：如果jsonpath返回结果不为空，则提取成功
                    if ext_json:
                        # 将提取结果保存为字典格式，key为参数名，value为提取值
                        extract_date = {key: ext_json}
                    else:
                        # 如果未提取到数据，设置默认提示信息
                        extract_date = {key: "未提取到数据，该接口返回结果可能为空"}

                    # 记录日志，输出提取到的参数信息
                    logs.info('json提取到参数：%s' % extract_date)
                    # 将提取结果写入yaml文件中保存
                    self.read.write_yaml_data(extract_date)

        # 异常处理：捕获所有可能的异常
        except:
            # 记录错误日志，提示用户检查yaml文件中extract_list表达式配置
            logs.error('接口返回值提取异常，请检查yaml文件extract_list表达式是否正确！')


if __name__ == '__main__':
    case_info = get_testcase_yaml(FILE_PATH['YAML'] + '/LoginAPI/login.yaml')[0]
    # print(case_info)
    req = RequestBase()
    # res = req.specification_yaml(case_info)
    res = req.specification_yaml(case_info)
    print(res)
