# flask配置
FLASKS_HOST='127.0.0.1'
FLASKS_PORT=5001
FLASKS_DEBUG=True
FLASK_SECRET_KEY='DYPu5X3Jq60qzxxZm3CN'



# mysql配置
MYSQL_USER='root'
MYSQL_PASSWORD='123456'
MYSQL_HOST='你的mysql地址'
MYSQL_POST=8975 # mysql端口
MYSQL_DATABASE='simple_chat' #mysql库


# redis配置
REDIS_HOST='redis的库地址'
REDIS_PORT=6379 # redis地址
REDIS_DB='0'
REDIS_DB_TOKEN='11' # 这个库最好是空的
REDIS_DB_USER_TOKEN='10' # 这个库最好是空的
REDIS_DB_SIMPLE='12' # 这个库最好是空的
REDIS_DECODE_RESPONSES=True # 会报错 所以不设置了
REDIS_PASSWORD='你的redis密码'


# tooken过期时间 单位：秒
TOOKEN_TIME_OUT=43200



# 签到配置
REDIS_SIGN_IN_DB='0'
REDIS_SIGN_IN_NAME='sign_in'
