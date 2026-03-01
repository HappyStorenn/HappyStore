（1）首先安装本项目所需的依赖库：pip install -r requirements.txt
（2）环境配置:使用本地的python环境或者使用项目下的venv虚拟环境
代码结构：
- base 基础类封装
- common  公共方法封装
- conf  存放全局配置文件目录
- data  存放测试数据
- logs  存放测试日志目录
- report    测试报告生成目录
- testcase  存放测试用例文件
- venv  本框架使用的虚拟环境
- conftest.py 全局操作
- environment.xml allure测试报告总览显示内容
- extract.yaml 接口依赖参数存放文件
- pytest.ini pytest框架规范约束
- requirements.txt 本框架所使用的到的第三方库
- run.py 主程序入口
