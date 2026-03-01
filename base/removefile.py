import os
from common.recordlog import logs


def remove_file(filepath, endlst):
    """
    删除指定目录下符合后缀条件的文件

    :param filepath: 需要清理的目录路径
    :param endlst: 文件后缀列表，例如：['json', 'txt', 'attach']
    :return: None
    """
    try:
        # 判断目录是否存在
        if os.path.exists(filepath):
            # 获取目录下的所有文件/文件夹名称
            dir_lst_files = os.listdir(filepath)
            # 遍历目录中的每一个文件
            for file_name in dir_lst_files:
                # 拼接文件的完整路径
                # 示例：./report/temp\test.json
                fpath = filepath + '\\' + file_name
                # endswith判断字符串是否以指定后缀结尾
                # 判断后缀参数是否为列表类型
                if isinstance(endlst, list):
                    # 遍历需要删除的文件后缀
                    for ft in endlst:
                        # endswith 判断文件名是否以指定后缀结尾
                        if file_name.endswith(ft):
                            # 删除符合条件的文件
                            os.remove(fpath)
                else:
                    # 如果传入的后缀不是 list 类型，抛出类型异常
                    raise TypeError('file Type error,must is list')
        else:
            # 如果目录不存在，则创建目录（避免后续程序报错）
            os.makedirs(filepath)
    except Exception as e:
        # 捕获异常并记录日志，避免因清理失败中断测试流程
        logs.error(e)


def remove_directory(path):
    """
    删除指定路径的文件或目录
    :param path: 需要删除的路径
    :return: None
    """
    try:
        # 判断路径是否存在
        if os.path.exists(path):
            # 删除指定路径
            # 注意：os.remove 只能删除文件，不能删除非空目录
            os.remove(path)
    except Exception as e:
        # 记录删除过程中的异常信息
        logs.error(e)
