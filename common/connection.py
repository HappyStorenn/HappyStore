import traceback

import clickhouse_sqlalchemy
import pymysql
import redis
import sys
import pymongo
import paramiko
import pandas as pd
from clickhouse_sqlalchemy import make_session, exceptions
from sqlalchemy import create_engine
from conf.operationConfig import OperationConfig
from common.recordlog import logs


conf = OperationConfig()


class ConnectMysql:

    def __init__(self):

        mysql_conf = {
            'host': conf.get_section_mysql('host'),
            'port': int(conf.get_section_mysql('port')),
            'user': conf.get_section_mysql('username'),
            'password': conf.get_section_mysql('password'),
            'database': conf.get_section_mysql('database')
        }

        try:
            self.conn = pymysql.connect(**mysql_conf, charset='utf8')
            # cursor=pymysql.cursors.DictCursor,将数据库表字段显示，以key-value形式展示
            self.cursor = self.conn.cursor(cursor=pymysql.cursors.DictCursor)
            logs.info("""成功连接到mysql---
            host：{host}
            port：{port}
            db：{database}
            """.format(**mysql_conf))
        except Exception as e:
            logs.error(f"except:{e}")

    def close(self):
        if self.conn and self.cursor:
            self.cursor.close()
            self.conn.close()
        return True

    def query_all(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            res = self.cursor.fetchall()

            keys = ''
            values = []
            for item in res:
                keys = list(item.keys())

            for ite in res:
                values.append(list(ite.values()))

            for val in values:
                # lst_format = [
                #     keys,
                #     val
                # ]
                lst_format = [
                    val
                ]

                return lst_format
                # return print_table(lst_format)

        except Exception as e:
            logs.error(e)
        finally:
            self.close()

    def delete(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            logs.info('删除成功')
        except Exception as e:
            logs.error(e)
        finally:
            self.close()


