# -*- coding: utf-8 -*-
import time

import pytest

from common.readyaml import ReadYamlData
from base.removefile import remove_file
from common.feishuRobot import send_fs_msg
from conf.setting import fs_msg

import warnings
# 初始化 YAML 数据读取对象
yfd = ReadYamlData()


@pytest.fixture(scope="session", autouse=True)
def clear_extract():
    """
        pytest 会话级别的前置处理（整个测试只执行一次）
        作用：
        1. 忽略 HTTPS 相关的 ResourceWarning 警告
        2. 清空 YAML 中缓存的提取数据（接口依赖数据）
        3. 清理 allure 报告临时目录中的历史文件
        """
    # 禁用HTTPS告警，ResourceWarning
    warnings.simplefilter('ignore', ResourceWarning)
    # 清空 YAML 文件中的历史提取数据（避免数据污染）
    yfd.clear_yaml_data()
    # 删除 allure 临时报告目录下的指定类型文件
    remove_file("./report/temp", ['json', 'txt', 'attach', 'properties'])


def generate_test_summary(terminalreporter):
    """
    生成 pytest 测试执行结果的摘要信息

    :param terminalreporter: pytest 内置终端报告对象
    :return: 测试结果摘要字符串
    """
    # 收集的测试用例总数
    total = terminalreporter._numcollected
    # 各类测试结果统计
    passed = len(terminalreporter.stats.get('passed', []))
    failed = len(terminalreporter.stats.get('failed', []))
    error = len(terminalreporter.stats.get('error', []))
    skipped = len(terminalreporter.stats.get('skipped', []))
    # 测试执行总时长（秒）
    duration = time.time() - terminalreporter._sessionstarttime
    # 拼接测试结果摘要信息
    summary = f"""
    开心商城自动化测试结果，通知如下，
    请着重关注测试失败的接口，具体执行结果如下：
    测试用例总数：{total}
    测试通过数：{passed}
    测试失败数：{failed}
    错误数量：{error}
    跳过执行数量：{skipped}
    执行总时长：{duration}
    """
    print(summary)
    return summary


"""
    pytest 钩子函数
    在所有测试执行完成后自动触发
    作用：
    1. 汇总测试执行结果
    2. 根据配置决定是否发送钉钉通知
"""
def pytest_terminal_summary(terminalreporter):
    """自动收集pytest框架执行的测试结果并打印摘要信息"""
    summary = generate_test_summary(terminalreporter)
    if fs_msg:
        send_fs_msg(summary)
