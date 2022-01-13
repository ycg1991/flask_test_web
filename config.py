import os
from datetime import timedelta
import pymysql
SECRET_KEY = os.urandom(24)
PERMANENT_SESSION_LIFETIME = timedelta(days=7)

# 邮箱信息
mail_host = "smtp.163.com"
mail_user = "yangchenguang1011@163.com"
mail_pwd = "FIJWZPBMFCIUFSVJ"
sender = "yangchenguang1011@163.com"
listener = ["yangchenguang@gaodun.com"]
# 数据库信息
DB_TEST_HOST = "127.0.0.1"
DB_TEST_PORT = 3306
DB_TEST_DBNAME = "gd_test"
DB_TEST_USER = "root"
DB_TEST_PASSWORD = "root"

# 数据库连接编码
DB_CHARSET = "utf8"

# min_cached : 启动时开启的闲置连接数量(缺省值 0 开始时不创建连接)
DB_MIN_CACHED = 10
DB_MAX_CACHED = 30
# max_shared : 共享连接数允许的最大数量(缺省值 0 代表所有连接都是专用的)如果达到了最大数量,被请求为共享的连接将会被共享使用
DB_MAX_SHARED = 20


# max_connections : 创建连接池的最大数量(缺省值 0 代表不限制)
DB_MAX_CONNECTIONS = 100

# blocking : 设置在连接池达到最大数量时的行为(缺省值 0 或 False 代表返回一个错误<toMany......> 其他代表阻塞直到连接数减少,连接被分配)
DB_BLOCKING = True

# max_usage : 单个连接的最大允许复用次数(缺省值 0 或 False 代表不限制的复用).当达到最大数时,连接会自动重新连接(关闭和重新打开)
DB_MAX_USAGE = 100

# set_session : 一个可选的SQL命令列表用于准备每个会话，如["set datestyle to german", ...]
DB_SET_SESSION = None

# creator : 使用连接数据库的模块
DB_CREATOR = pymysql

