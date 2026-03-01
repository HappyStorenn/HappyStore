# 导入Python内置的文件操作模块，用于文件复制等操作
import shutil
# 导入pytest测试框架，用于执行自动化测试用例
import pytest
# 导入Python内置的操作系统接口模块，用于执行系统命令、路径操作等
import os
# 导入Python内置的浏览器控制模块，用于自动打开生成的测试报告
import webbrowser
# 从自定义配置文件setting.py中导入报告类型配置项（REPORT_TYPE）
from conf.setting import REPORT_TYPE

# 主程序入口，仅当脚本直接运行时才执行以下代码
if __name__ == '__main__':

    # 判断配置文件中指定的报告类型是否为allure
    if REPORT_TYPE == 'allure':
        # 调用pytest的主函数执行测试用例，传入一系列运行参数
        pytest.main(
            [
                '-s',          # 显示测试用例中的打印输出（禁用捕获）
                '-v',          # 详细输出模式，显示每个测试用例的执行结果
                '--alluredir=./report/temp',  # 指定allure报告临时数据的生成目录
                './testcase',  # 指定要执行的测试用例所在目录
                '--clean-alluredir',  # 执行前清空allure报告临时目录，避免旧数据干扰
                '--junitxml=./report/results.xml'  # 生成junit格式的xml测试结果文件
            ]
        )

        # 将environment.xml文件（包含测试环境信息）复制到allure临时目录，用于在报告中展示环境信息
        shutil.copy('./environment.xml', './report/temp')
        # 执行系统命令，启动allure服务并打开测试报告（自动弹出浏览器）
        os.system(f'allure serve ./report/temp')

    # 判断配置文件中指定的报告类型是否为tm（自定义的tmreport报告）
    elif REPORT_TYPE == 'tm':
        # 调用pytest的主函数执行测试用例，生成tm格式的HTML测试报告
        pytest.main([
            '-vs',  # 结合-s和-v的功能，显示打印输出+详细执行信息
            '--pytest-tmreport-name=testReport.html',  # 指定tm报告的文件名
            '--pytest-tmreport-path=./report/tmreport'  # 指定tm报告的生成路径
        ])
        # 拼接tm报告的绝对路径，并调用系统默认浏览器在新标签页中打开该报告
        webbrowser.open_new_tab(os.getcwd() + '/report/tmreport/testReport.html')