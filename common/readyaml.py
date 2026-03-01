import yaml
import traceback
import os

from common.recordlog import logs
from conf.operationConfig import OperationConfig
from conf.setting import FILE_PATH
from yaml.scanner import ScannerError


def get_testcase_yaml(file):
    # 1. 初始化一个空列表，用来存放最终整理好的测试用例数据
    testcase_list = []

    try:
        # 2. 以只读模式、utf-8编码打开传入的YAML文件
        with open(file, 'r', encoding='utf-8') as f:
            # 3. 安全加载YAML文件内容，把YAML格式转成Python的字典/列表
            data = yaml.safe_load(f)

            # 4. 判断加载出来的数据长度是否小于等于1（说明是单组测试用例结构）
            if len(data) <= 1:
                # 5. 取数据的第一个元素（因为data是列表，[0]是第一个元素）
                yam_data = data[0]
                # 6. 从第一个元素中获取"baseInfo"（基础信息），比如接口地址、请求方式等
                base_info = yam_data.get('baseInfo')

                # 7. 遍历"testCase"（测试用例）里的每一条用例
                for ts in yam_data.get('testCase'):
                    # 8. 把基础信息和单条测试用例打包成一个列表
                    param = [base_info, ts]
                    # 9. 把这个打包好的用例添加到最终列表里
                    testcase_list.append(param)

                # 10. 返回整理好的测试用例列表
                return testcase_list
            else:
                # 11. 如果数据长度大于1，直接返回原始数据
                return data
    # 12. 捕获编码错误：文件不是UTF-8格式时触发
    except UnicodeDecodeError:
        logs.error(
            f"[{file}]文件编码格式错误，--尝试使用utf-8编码解码YAML文件时发生了错误，请确保你的yaml文件是UTF-8格式！")
    # 13. 捕获文件不存在错误：文件路径错了/文件删了时触发
    except FileNotFoundError:
        logs.error(f'[{file}]文件未找到，请检查路径是否正确')
    # 14. 捕获其他所有未知错误：比如YAML格式写错了、数据结构不对等
    except Exception as e:
        logs.error(f'获取【{file}】文件数据时出现未知错误: {str(e)}')

class ReadYamlData:
    """
    【类功能说明】
    专门用于读写接口测试中YAML格式的测试数据文件
    核心能力：加载指定YAML文件，返回结构化的Python数据（列表/字典）
    """
    def __init__(self, yaml_file=None):
        """
            【初始化方法】
            创建类实例时自动执行，用于初始化类的核心属性
            :param yaml_file: 可选参数，传入需要读取的YAML文件路径（如："test_case.yaml"）
            """
        # 如果传入了YAML文件路径，就保存到实例属性中，供后续读取使用
        if yaml_file is not None:
            self.yaml_file = yaml_file  # 实例属性：存储YAML文件路径
        else:
            pass  # 未传入文件路径时，暂不处理（可优化为抛出提示，避免后续报错）

        # 初始化配置操作类实例（原代码中用于处理配置相关逻辑）
        self.conf = OperationConfig()
        # 初始化存储YAML数据的属性，初始值为None，读取文件后会赋值
        self.yaml_data = None

    @property  # 装饰器：将下方的方法伪装成"属性"，调用时无需加括号
    def get_yaml_data(self):
        """
        核心方法】
        读取并返回YAML文件中的测试用例数据
        :return: 返回解析后的Python数据（通常是list）
        【异常处理】
        读取文件失败时（如文件不存在/格式错误），会记录详细错误日志，避免程序崩溃
        """
        try:
            # 1. 安全打开YAML文件：
            # - 'r'：只读模式；encoding='utf-8'：保证中文内容不出现乱码
            # - with语句：自动关闭文件，避免资源泄露
            with open(self.yaml_file, 'r', encoding='utf-8') as f:
                # 2. 解析YAML文件：
                # yaml.safe_load()：安全加载YAML内容，避免恶意代码执行（比load更安全）
                self.yaml_data = yaml.safe_load(f)
                # 3. 返回解析后的数据（供外部调用）
                return self.yaml_data
        except Exception:
            # 捕获所有异常，记录详细错误信息（包括报错行、错误类型）
            # traceback.format_exc()：输出完整的异常堆栈信息，方便定位问题
            logs.error(str(traceback.format_exc()))
            # 可选：抛出异常或返回空列表，避免后续代码因None报错


    def write_yaml_data(self, value):
        """
        将数据写入 YAML 文件（追加写入）
    主要用途：
    - 接口返回值提取
    - 接口之间的参数关联（如 token、cookie 等）
        写入规则说明：
    1. 写入数据必须是 dict 类型
    2. allow_unicode=True：支持中文写入
    3. sort_keys=False：保持字典原有顺序

        :param value: 需要写入的数据，必须为 dict
        :return:
        """

        file = None
        # extract.yaml 文件路径（用于接口关联数据存储）
        file_path = FILE_PATH['EXTRACT']

        # 如果文件路径不存在，则尝试创建
        if not os.path.exists(file_path):
            os.system(file_path)
        try:
            # 以追加模式打开文件，避免覆盖已有数据
            file = open(file_path, 'a', encoding='utf-8')
            # 判断写入的数据类型是否为 dict
            if isinstance(value, dict):
                # 将字典转换为 YAML 格式字符串
                write_data = yaml.dump(value, allow_unicode=True, sort_keys=False)
                file.write(write_data)
            else:
                logs.info('写入[extract.yaml]的数据必须为dict格式')
        except Exception:
            #把这次异常从头到尾发生了什么，原原本本记录下来
            logs.error(str(traceback.format_exc()))
        finally:
            file.close()

    def clear_yaml_data(self):
        """
        清空extract.yaml文件数据
        :param filename: yaml文件名
        :return:
        作用：在测试执行前清空接口依赖数据
       避免上一次测试残留的数据影响本次测试结果
        """
        # 以写入模式打开 extract.yaml 文件
        # 使用 'w' 模式会自动清空文件内容
        with open(FILE_PATH['EXTRACT'], 'w') as f:
            # truncate() 明确将文件内容截断为 0 字节（双重保险）
            f.truncate()

    def get_extract_yaml(self, node_name, second_node_name=None):
        """
        用于读取接口提取的变量值
        :param node_name:
        :return:
        """
        if os.path.exists(FILE_PATH['EXTRACT']):
            pass
        else:
            logs.error('extract.yaml不存在')
            file = open(FILE_PATH['EXTRACT'], 'w')
            file.close()
            logs.info('extract.yaml创建成功！')
        try:
            with open(FILE_PATH['EXTRACT'], 'r', encoding='utf-8') as rf:
                ext_data = yaml.safe_load(rf)
                if second_node_name is None:
                    return ext_data[node_name]
                else:
                    return ext_data[node_name][second_node_name]
        except Exception as e:
            logs.error(f"【extract.yaml】没有找到：{node_name},--%s" % e)

