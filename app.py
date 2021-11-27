import pymysql

pymysql.install_as_MySQLdb() # 解决py3版本报错没有mysqldb

import uuid
import redis
import time
import random
import string
import json

from datetime import datetime
from flask import Flask, request, make_response, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)
app.config.from_pyfile('config.py', silent=True)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@{}:{}/{}'.format(
    app.config.get('MYSQL_USER'),
    app.config.get('MYSQL_PASSWORD'),
    app.config.get('MYSQL_HOST'),
    app.config.get('MYSQL_POST'),
    app.config.get('MYSQL_DATABASE')
)
db = SQLAlchemy(app)


# 用户表
class Users(db.Model):
    # 定义表名
    __tablename__ = 'user'
    # 定义列对象
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.VARCHAR(255), unique=True)
    user_email = db.Column(db.VARCHAR(255), unique=True)
    user_new_visit = db.Column(db.DateTime, unique=False, onupdate=datetime.now, default=datetime.now)

    # repr()方法显示一个可读字符串
    def __repr__(self):
        return 'user_name:%s' % self.user_name


# 聊天室表
class Chat_Room(db.Model):
    # 定义表名
    __tablename__ = 'chat_room'
    # 定义列对象
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chat_name = db.Column(db.VARCHAR(255), unique=True)  # 聊天室名字
    char_run = db.Column(db.VARCHAR(255), unique=False, default='t')  # 是否可用
    char_make_time = db.Column(db.DateTime, unique=False, default=datetime.now)  # 创建时间
    char_last_time = db.Column(db.DateTime, unique=False, default=datetime.now, onupdate=datetime.now)  # 上次运行时间

    # repr()方法显示一个可读字符串
    def __repr__(self):
        return 'chat_name:%s' % self.chat_name

    pass


# 聊天内容表
class Chat_content(db.Model):
    # 定义表名
    __tablename__ = 'chat_content'
    # 定义列对象
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    chat_name = db.Column(db.VARCHAR(255), unique=False)  # 聊天室名字
    spoke_man = db.Column(db.VARCHAR(255), unique=False)  # 发言人
    spoke_time = db.Column(db.VARCHAR(255), unique=False)  # 发言时间戳
    spoken_text = db.Column(db.TEXT, unique=False)  # 发言内容
    content_time = db.Column(db.DateTime, unique=False, default=datetime.now, onupdate=datetime.now)  # 时间

    # repr()方法显示一个可读字符串
    def __repr__(self):
        return 'chat_name:%s' % self.chat_name

    pass


# 获取所有聊天室
def get_all_content():
    di = Chat_Room.query.filter_by(char_run='t').all()
    if di:
        data = []
        for i in di:
            content_data = {}
            content_data['chat_name'] = i.chat_name
            content_data['char_make_time'] = i.char_make_time
            data.append(content_data)
        return data
    else:
        return None
    pass


# mysql数据存储
def mysql_content_in(chat_name, spoke_man, spoke_time, spoken_text):
    user = Chat_content(chat_name=chat_name, spoke_man=spoke_man, spoke_time=spoke_time, spoken_text=spoken_text)
    db.session.add(user)
    db.session.commit()
    pass


# redis存储当天的数据内容
def set_redis_content(chat_room, text):
    pool = redis.ConnectionPool(
        host=app.config.get('REDIS_HOST'),
        port=app.config.get('REDIS_PORT'),
        db=app.config.get('REDIS_DB_SIMPLE'),
        password=app.config.get('REDIS_PASSWORD', None)
    )
    r = redis.Redis(connection_pool=pool)
    r.sadd(chat_room, text)
    pass


# redis 获取当前的聊天
def get_redis_content(chat_room):
    pool = redis.ConnectionPool(
        host=app.config.get('REDIS_HOST'),
        port=app.config.get('REDIS_PORT'),
        db=app.config.get('REDIS_DB_SIMPLE'),
        password=app.config.get('REDIS_PASSWORD', None),
        decode_responses=True
    )
    r = redis.Redis(connection_pool=pool)
    data_set = r.smembers(chat_room)
    return data_set


# set 转成list  list中存储dict
def content_set_list(data):
    set_list = set(data)
    data_list = []
    for i in set_list:
        try:
            data_list.append(json.loads(i))
        except Exception as e:
            print(e)
    return data_list
    pass


# json 转 str
def json_str(text):
    return json.dumps(text, ensure_ascii=False)


# 时间戳转换为时间
def time_make(data):
    for i in range(len(data)):
        data[i]['spoke_time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(data[i]['spoke_time'])))
    return data


# data 时间戳处理
def time_set(data):
    for i in range(len(data)):
        data[i]['spoke_time'] = int(data[i]['spoke_time'])
    return data

# 注册名存储
def mysql_username(user_name, user_email):
    user = Users(user_name=user_name, user_email=user_email)
    db.session.add(user)
    db.session.commit()
    pass


# 重复查询
def mysql_select(user_name, user_email):
    count = db.session.query(func.count(Users.user_name)).filter(Users.user_name == user_name).scalar()
    if count:
        return True
    else:
        count = db.session.query(func.count(Users.user_email)).filter(Users.user_email == user_email).scalar()
        if count:
            return True
        else:
            return False


# 获取注册名
def mysql_select_username(user_email):
    data = db.session.query(Users).filter(Users.user_email == user_email).first()
    if data:
        return data.user_name
    else:
        return None


# redis存储token
def set_redis_token(token, username):
    token_like = backups_redis_token(username=username)
    # print(token_like)
    if token_like:
        del_redis_token(token=token_like)
        pool = redis.ConnectionPool(
            host=app.config.get('REDIS_HOST'),
            port=app.config.get('REDIS_PORT'),
            db=app.config.get('REDIS_DB_TOKEN'),
            password=app.config.get('REDIS_PASSWORD', None)
        )
        r = redis.Redis(connection_pool=pool)
        r.set(str(token), str(username))
        r.expire(str(token), app.config.get('TOOKEN_TIME_OUT'))
        removal_redis_token(token=token, username=username)
        pass
    else:
        pool = redis.ConnectionPool(
            host=app.config.get('REDIS_HOST'),
            port=app.config.get('REDIS_PORT'),
            db=app.config.get('REDIS_DB_TOKEN'),
            password=app.config.get('REDIS_PASSWORD', None)
        )
        r = redis.Redis(connection_pool=pool)
        r.set(str(token), str(username))
        r.expire(str(token), app.config.get('TOOKEN_TIME_OUT'))
        removal_redis_token(token=token, username=username)
        pass


# redis根据token获取用户名
def get_redis_token(token):
    pool = redis.ConnectionPool(
        host=app.config.get('REDIS_HOST'),
        port=app.config.get('REDIS_PORT'),
        db=app.config.get('REDIS_DB_TOKEN'),
        password=app.config.get('REDIS_PASSWORD', None)
    )
    r = redis.Redis(connection_pool=pool)
    username = r.get(token)
    # r.connection_pool.disconnect()
    if username:
        return str(username, encoding="utf8")
    return username


# redis清除token
def del_redis_token(token):
    try:
        pool = redis.ConnectionPool(
            host=app.config.get('REDIS_HOST'),
            port=app.config.get('REDIS_PORT'),
            db=app.config.get('REDIS_DB_TOKEN'),
            password=app.config.get('REDIS_PASSWORD', None)
        )
        r = redis.Redis(connection_pool=pool)
        r.delete(token)
        return True
    except:
        return False


# redis防止同一用户多次登录 产生多个token
def removal_redis_token(token, username):
    pool = redis.ConnectionPool(
        host=app.config.get('REDIS_HOST'),
        port=app.config.get('REDIS_PORT'),
        db=app.config.get('REDIS_DB_USER_TOKEN'),
        password=app.config.get('REDIS_PASSWORD', None),

    )
    r = redis.Redis(connection_pool=pool)
    r.set(str(username), str(token))
    r.expire(str(username), app.config.get('TOOKEN_TIME_OUT'))


# redis备份库查询是否存在该用户的token
def backups_redis_token(username):
    pool = redis.ConnectionPool(
        host=app.config.get('REDIS_HOST'),
        port=app.config.get('REDIS_PORT'),
        db=app.config.get('REDIS_DB_USER_TOKEN'),
        password=app.config.get('REDIS_PASSWORD', None),
        decode_responses=app.config.get('REDIS_DECODE_RESPONSES', False)
    )
    r = redis.Redis(connection_pool=pool)

    key_list = r.keys()
    # print(key_list)
    # print(username)
    # print(r.get(username))
    if username in key_list:
        # print(123)
        return r.get(username)
    else:
        return ''


# 生成token
def make_redis_token(username):
    token = uuid.uuid3(uuid.NAMESPACE_DNS, str(username) + str(time.time() * 1000) + ''.join(
        random.sample(string.ascii_letters + string.digits, 24)))
    return str(token)


@app.route('/')
def hello_world():
    # db.create_all()
    return render_template('login.html')


@app.route('/logon')
def logons():
    # db.create_all()
    return render_template('logon.html')


@app.route('/login')
def logins():
    # db.create_all()
    return render_template('login.html')


@app.route('/chatroom')
def chartroom():
    return render_template('chatroom.html')


# 注册
@app.route('/api/logon', methods=['POST'])
def Logon():
    try:
        username = request.json.get('username', None)
        email = request.json.get('email', None)
        if username and email:
            if ' ' in username or ' ' in email:
                return 'Hello World!', 500
            if mysql_select(user_email=email, user_name=username):
                return 'Hello World!', 530
            else:
                mysql_username(user_email=email, user_name=username)
                token = make_redis_token(username=username)
                set_redis_token(token=token, username=username)
                resp = make_response("success")
                resp.set_cookie("token", token, max_age=43200)
                resp.set_cookie("name", username, max_age=43200)
                return resp, 200
            pass
        else:
            return 'Hello World!', 500
    except:
        return 'Hello World!', 590


# 登录
@app.route('/api/login', methods=['POST'])
def login():
    try:
        email = request.json.get('email', None)
        username = mysql_select_username(user_email=email)
        if username:
            token = make_redis_token(username=username)
            set_redis_token(token=token, username=username)
            resp = make_response("success")
            resp.set_cookie("token", token, max_age=43200)
            resp.set_cookie("name", username, max_age=43200)
            return resp, 200
        else:
            return 'Hello World!', 500
    except:
        return 'Hello World!', 590


# 获取登录状态
@app.route('/api/login/token', methods=['POST'])
def login_token():
    token = request.cookies.get("token")
    if token:
        username = get_redis_token(token)
        if username:
            return {'result': 1, 'username': username}, 200
        else:
            return 'Hello World!', 500
        pass
    else:
        return 'Hello World!', 500


# 注销
@app.route('/api/logout')
def logout():
    resp = make_response("del success")
    resp.delete_cookie('token')
    resp.delete_cookie('name')
    return resp, 200
    pass


# 聊天室获取
@app.route('/api/content/all', methods=['POST'])
def content_all():
    token = request.cookies.get("token")
    if token:
        content_data = get_all_content()
        if content_data:
            return {"content_data": content_data}, 200
            pass
        else:
            return {"content_data": []}, 200
    else:
        return 'Hello World!', 300


# 聊天消息存储
@app.route('/api/speak', methods=["POST"])
def speak():
    token = request.cookies.get("token")
    if token:
        chat_name = request.json.get("chat_name")
        spoke_man = get_redis_token(token)
        spoke_time = str(int(time.time()))
        spoken_text = request.json.get("spoken_text")
        if chat_name and spoke_man and spoke_time and spoken_text:
            if 'rm' in spoken_text:
                resp = make_response("del success")
                resp.delete_cookie('token')
                resp.delete_cookie('name')
                return resp, 500
            text = json_str({"chat_name": chat_name, "spoke_man": spoke_man, "spoke_time": spoke_time,
                             "spoken_text": spoken_text})
            mysql_content_in(chat_name=chat_name, spoke_man=spoke_man, spoke_time=spoke_time, spoken_text=spoken_text)
            set_redis_content(chat_room=chat_name, text=text)
            return 'Hello World!', 200
            pass
        else:
            return 'Hello World!', 400
        pass
    else:
        return 'Hello World!', 300


# 聊天历史查询
@app.route('/api/speak/log', methods=["POST"])
def speak_log():
    token = request.cookies.get("token")
    if token:
        chat_name = request.json.get("chat_name")
        if chat_name:
            data = get_redis_content(chat_name)
            data = content_set_list(data)
            # data数据进行处理 然后排序
            data = time_set(data=data)
            # print(data)
            data = sorted(data, key=lambda list1: list1["spoke_time"], reverse=True)
            data = time_make(data)
            return {"data": data}, 200

        else:
            return 'Hello World!', 400
        pass
    else:
        return 'Hello World!', 300


if __name__ == '__main__':
    app.run(debug=False,host='0.0.0.0',port=7788)
