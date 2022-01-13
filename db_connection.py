# coding=utf-8
"""
使用DBUtils数据库连接池中的连接，操作数据库
OperationalError: (2006, ‘MySQL server has gone away’)
"""
import datetime
from dbutils.pooled_db import PooledDB
import pymysql
import config


class MysqlClient(object):
    __pool = None

    def __init__(self, mincached=config.DB_MIN_CACHED, maxcached=config.DB_MAX_CACHED, maxshared=config.DB_MAX_SHARED,
                 maxconnections=config.DB_MAX_CONNECTIONS,
                 blocking=True, maxusage=config.DB_MAX_USAGE, setsession=config.DB_SET_SESSION, reset=True,
                 host=config.DB_TEST_HOST, port=3306, db=config.DB_TEST_DBNAME,
                 user=config.DB_TEST_USER, passwd=config.DB_TEST_PASSWORD, charset='utf8mb4'):
        """
        :param mincached:连接池中空闲连接的初始数量
        :param maxcached:连接池中空闲连接的最大数量
        :param maxshared:共享连接的最大数量
        :param maxconnections:创建连接池的最大数量
        :param blocking:超过最大连接数量时候的表现，为True等待连接数量下降，为false直接报错处理
        :param maxusage:单个连接的最大重复使用次数
        :param setsession:optional list of SQL commands that may serve to prepare
            the session, e.g. ["set datestyle to ...", "set time zone ..."]
        :param reset:how connections should be reset when returned to the pool
            (False or None to rollback transcations started with begin(),
            True to always issue a rollback for safety's sake)
        :param host:数据库ip地址
        :param port:数据库端口
        :param db:库名
        :param user:用户名
        :param passwd:密码
        :param charset:字符编码
        """

        if not self.__pool:
            self.__class__.__pool = PooledDB(pymysql,
                                             mincached, maxcached,
                                             maxshared, maxconnections, blocking,
                                             maxusage, setsession, reset,
                                             host=host, port=port, db=db,
                                             user=user, passwd=passwd,
                                             charset=charset,
                                             cursorclass=pymysql.cursors.DictCursor
                                             )
        self._conn = None
        self._cursor = None
        self.__get_conn()

    def __get_conn(self):
        self._conn = self.__pool.connection()
        self._cursor = self._conn.cursor()

    def close(self):
        try:
            self._cursor.close()
            self._conn.close()
        except Exception as e:
            print(e)

    def __execute(self, sql):
        count = self._cursor.execute(sql)
        return count

    def __commit(self):
        return self._conn.commit()

    @staticmethod
    def __dict_datetime_obj_to_str(result_dict):
        """把字典里面的datatime对象转成字符串，使json转换不出错"""
        if result_dict:
            result_replace = {k: v.__str__() for k, v in result_dict.items() if isinstance(v, datetime.datetime)}
            result_dict.update(result_replace)
        return result_dict

    def add_one(self, sql):
        """新增数据"""
        self.__execute(sql)
        self.__commit()

    def delete_one(self, sql):
        """删除单条数据"""
        self.__execute(sql)
        self.__commit()

    def edit_one(self, sql):
        """修改单条数据"""
        self.__execute(sql)
        self.__commit()

    def select_one(self, sql):
        """查询单个结果"""
        count = self.__execute(sql)
        result = self._cursor.fetchone()
        """:type result:dict"""
        result = self.__dict_datetime_obj_to_str(result)
        return result

    def select_many(self, sql):
        """
        查询多个结果
        :param sql: qsl语句
        :param param: sql参数
        :return: 结果数量和查询结果集
        """
        count = self.__execute(sql)
        result = self._cursor.fetchall()
        """:type result:list"""
        [self.__dict_datetime_obj_to_str(row_dict) for row_dict in result]
        return result

    def execute(self, sql):
        count = self.__execute(sql)
        return count

    def commit(self):
        self.__commit()

    def begin(self):
        """开启事务"""
        self._conn.autocommit(0)

    def end(self):
        """结束事务"""
        self._conn.rollback()

