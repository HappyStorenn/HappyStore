def generate_module_id():
    """
    生成测试模块编号，为了保证allure报告的顺序与pytest设定的执行顺序保持一致
    格式: M01_, M02_, ..., M999_
    :return: 生成器对象，每次调用返回下一个模块编号
    """
    for i in range(1, 1000):
        # 生成模块编号，M开头，后面跟两位数字（不足两位补0），最后加下划线
        module_id = 'M' + str(i).zfill(2) + '_'
        yield module_id

def generate_testcase_id():
    """
    生成测试用例编号
    格式: C01_, C02_, ..., C9999_
    :return: 生成器对象，每次调用返回下一个测试用例编号
    """
    for i in range(1, 10000):
        # 生成用例编号，C开头，后面跟两位数字（不足两位补0），最后加下划线
        case_id = 'C' + str(i).zfill(2) + '_'
        yield case_id

# 创建模块ID生成器实例
m_id = generate_module_id()

# 创建测试用例ID生成器实例
c_id = generate_testcase_id()