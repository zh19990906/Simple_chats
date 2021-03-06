import pymysql

pymysql.install_as_MySQLdb()  # 解决py3版本报错没有mysqldb

import uuid
import redis
import time
import random
import string
import json
import os

from datetime import datetime
from flask import Flask, request, make_response, render_template, send_from_directory, redirect, url_for
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
    chat_only_name = db.Column(db.VARCHAR(255), unique=True)  # 聊天室唯一名称标识
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
    chat_only_name = db.Column(db.VARCHAR(255), unique=False)  # 聊天室名字
    spoke_man = db.Column(db.VARCHAR(255), unique=False)  # 发言人
    spoke_time = db.Column(db.VARCHAR(255), unique=False)  # 发言时间戳
    spoken_text = db.Column(db.TEXT, unique=False)  # 发言内容
    content_time = db.Column(db.DateTime, unique=False, default=datetime.now, onupdate=datetime.now)  # 时间

    # repr()方法显示一个可读字符串
    def __repr__(self):
        return 'chat_only_name:%s' % self.chat_only_name

    pass


# 签到信息表
class Sign_in(db.Model):
    # 定义表名
    __tablename__ = 'sign_in'
    # 定义列对象
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_email = db.Column(db.VARCHAR(255), unique=False)  # 邮箱
    integral = db.Column(db.Integer, unique=False)  # 积分
    content_time = db.Column(db.DateTime, unique=False, default=datetime.now, onupdate=datetime.now)  # 时间

    # repr()方法显示一个可读字符串
    def __repr__(self):
        return 'user_email:%s' % self.user_email


# 积分统计表
class Integrals(db.Model):
    # 定义表名
    __tablename__ = 'integrals'
    # 定义列对象
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_email = db.Column(db.VARCHAR(255), unique=False)  # 邮箱
    integral_all = db.Column(db.Integer, unique=False, default=0)  # 累积积分
    content_time = db.Column(db.DateTime, unique=False, default=datetime.now, onupdate=datetime.now)  # 时间

    # repr()方法显示一个可读字符串
    def __repr__(self):
        return 'user_email:%s' % self.user_email


# 获取所有聊天室
def get_all_content():
    di = Chat_Room.query.filter_by(char_run='t').all()
    if di:
        data = []
        for i in di:
            content_data = {}
            content_data['chat_name'] = i.chat_name
            content_data['chat_only_name'] = i.chat_only_name
            content_data['char_make_time'] = i.char_make_time
            data.append(content_data)
        return data
    else:
        return []
    pass


# 根据名字获取邮箱
def get_username_email(username):
    di = db.session.query(Users).filter(Users.user_name == username).first()
    return di.user_email


# 签到
def get_sign(user_email, integral):
    Sign = Sign_in(user_email=user_email, integral=integral)
    db.session.add(Sign)
    db.session.commit()


# 查询积分表是否有该用户
def get_integrals_user(user_email):
    count = db.session.query(func.count(Integrals.user_email)).filter(Integrals.user_email == user_email).scalar()
    if count:
        # 存在
        return True
    else:
        # 不存在
        return False


# 添加用户
def set_integrals_user(user_email):
    Integral = Integrals(user_email=user_email)
    db.session.add(Integral)
    db.session.commit()


# 积分更新
def set_integrals(user_email, integral):
    data = db.session.query(Integrals).filter(Integrals.user_email == user_email).first()
    data.integral_all += integral
    db.session.add(data)
    db.session.commit()
    pass


# 积分查询
def get_integrals(user_email):
    di = db.session.query(Integrals).filter(Integrals.user_email == user_email).first()
    return {"user_email": di.user_email, "integral_all": di.integral_all, "content_time": di.content_time}


# mysql数据存储
def mysql_content_in(chat_only_name, spoke_man, spoke_time, spoken_text):
    user = Chat_content(chat_only_name=chat_only_name, spoke_man=spoke_man, spoke_time=spoke_time,
                        spoken_text=spoken_text)
    db.session.add(user)
    db.session.commit()
    pass


# redis存储聊天内容
def set_redis_content(chat_only_name, text):
    pool = redis.ConnectionPool(
        host=app.config.get('REDIS_HOST'),
        port=app.config.get('REDIS_PORT'),
        db=app.config.get('REDIS_DB_SIMPLE'),
        password=app.config.get('REDIS_PASSWORD', None)
    )
    r = redis.Redis(connection_pool=pool)
    r.sadd(chat_only_name, text)
    pass


# redis 获取当前的聊天
def get_redis_content(chat_only_name):
    pool = redis.ConnectionPool(
        host=app.config.get('REDIS_HOST'),
        port=app.config.get('REDIS_PORT'),
        db=app.config.get('REDIS_DB_SIMPLE'),
        password=app.config.get('REDIS_PASSWORD', None),
        decode_responses=True
    )
    r = redis.Redis(connection_pool=pool)
    data_set = r.smembers(chat_only_name)
    return data_set


# redis 签到人员存储
def set_redis_sign(email):
    pool = redis.ConnectionPool(
        host=app.config.get('REDIS_HOST'),
        port=app.config.get('REDIS_PORT'),
        db=app.config.get('REDIS_SIGN_IN_DB'),
        password=app.config.get('REDIS_PASSWORD', None)
    )
    r = redis.Redis(connection_pool=pool)
    return r.sadd(app.config.get('REDIS_SIGN_IN_NAME'), email)
    pass


# redis 签到人员获取
def get_redis_sign():
    pool = redis.ConnectionPool(
        host=app.config.get('REDIS_HOST'),
        port=app.config.get('REDIS_PORT'),
        db=app.config.get('REDIS_SIGN_IN_DB'),
        password=app.config.get('REDIS_PASSWORD', None),
        decode_responses=True
    )
    r = redis.Redis(connection_pool=pool)
    return r.smembers(app.config.get('REDIS_SIGN_IN_NAME'))
    pass


# set 转成list  list中存储dict
def content_set_list(data):
    set_list = set(data)
    # print("103869292@qq.com" in set_list)
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


# 聊天室名字校验
def chat_name_check(chat_only_name):
    count = db.session.query(func.count(Chat_Room.chat_only_name)).filter(Chat_Room.chat_only_name == chat_only_name) \
        .filter(Chat_Room.char_run == 't').scalar()
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


# 跳转到登录页
@app.route('/')
def hello_world():
    # 首次运行需要讲下面这行解开注释，这样运行访问主页时会自动创建表格
    db.create_all()
    return render_template('login.html')


# 跳转到注册页
@app.route('/logon')
def logons():
    # db.create_all()
    return render_template('logon.html')


# 转发登录
@app.route('/login')
def logins():
    return render_template('login.html')


# 聊天详情页
@app.route('/chatroom/<chat_only_name>')
def chatroom_only(chat_only_name):
    # db.create_all()
    token = request.cookies.get("token")
    if token:
        data = {'chat_only_name': chat_only_name}
        return render_template('chatroom.html', data=data)
    else:
        return render_template('login.html')


# 转发
@app.route('/chatroom/')
def forward():
    # db.create_all()
    token = request.cookies.get("token")
    if token:
        return redirect(url_for('choice'))
    else:
        return render_template('login.html')


# 登录后进行跳转
@app.route('/choice')
def choice():
    token = request.cookies.get("token")
    if token:
        username = get_redis_token(token=token)
        content_data = get_all_content()
        user_email = get_username_email(username=username)
        # print(get_redis_sign())
        # user_signs = content_set_list(get_redis_sign())
        if user_email in set(get_redis_sign()):
            integral_state = 0
        else:
            integral_state = 1
        data = {}
        data['content_data'] = content_data
        data['username'] = username
        data['integral_state'] = integral_state
        return render_template('choice_room.html', data=data)
    else:
        return render_template('login.html')


# 进入房间主页
@app.route('/api/chatroom/check', methods=['POST'])
def chartroom():
    token = request.cookies.get("token")
    if token:
        # 获取到聊天室的唯一名称
        chat_only_name = request.json.get("chat_only_name")
        if chat_name_check(chat_only_name=chat_only_name):
            data = {'chat_only_name': chat_only_name}
            return {"chat_only_data": data}, 200
        else:
            return 'Hello World!', 333
    else:
        return 'Hello World!', 300


# 注册
@app.route('/api/logon', methods=['POST'])
def Logon():
    try:
        username = request.json.get('username', None)
        email = request.json.get('email', None)
        if username and email:
            # 过滤一下空格以及一些词语
            if ' ' in username or ' ' in email or 'root' in username or 'root' in email or 'admin' in username or \
                    'admin' in email:
                return 'Hello World!', 500
            # 这里的重复检测其实可以使用redis进行检测增加系统检测速度
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
    except Exception as e:
        print(e)
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
            # token 过期
            return 'Hello World!', 430
        pass
    else:
        # 无token
        return 'Hello World!', 500


# 签到
@app.route('/api/sign/in', methods=["POST"])
def signs_in():
    token = request.cookies.get("token")
    if token:
        username = get_redis_token(token=token)
        user_email = get_username_email(username=username)
        if set_redis_sign(email=user_email):
            if not get_integrals_user(user_email=user_email):
                set_integrals_user(user_email=user_email)
            integral = random.randint(0, 100)
            get_sign(user_email=user_email, integral=integral)
            set_integrals(user_email=user_email, integral=integral)
            date = {"integral": integral}
            return date, 200
        else:
            return 'Hello World!', 443
    else:
        return 'Hello World!', 500


# 注销
@app.route('/api/logout', methods=['POST'])
def logout():
    token = request.cookies.get("token")
    if token:
        del_redis_token(token=token)
        resp = make_response("del success")
        resp.delete_cookie('token')
        resp.delete_cookie('name')
        return resp, 200
    else:
        return 'Hello World!', 363
    pass


# 聊天室获取
@app.route('/api/content/all', methods=['POST'])
def content_all():
    token = request.cookies.get("token")
    if token:
        username = get_redis_token(token=token)
        user_email = get_username_email(username=username)
        user_signs = content_set_list(get_redis_sign())
        if user_email in user_signs:
            integral_state = 0
        else:
            integral_state = 1
        content_data = get_all_content()
        # print({"content_data": content_data, "integral_state": integral_state})
        if content_data:
            return {"content_data": content_data, "integral_state": integral_state}, 200
            pass
        else:
            return {"content_data": [], "integral_state": integral_state}, 200
    else:
        return 'Hello World!', 300


# 聊天消息存储
@app.route('/api/speak', methods=["POST"])
def speak():
    token = request.cookies.get("token")
    if token:
        chat_only_name = request.json.get("chat_only_name")
        spoke_man = get_redis_token(token)
        spoke_time = str(int(time.time()))
        spoken_text = request.json.get("spoken_text")
        if chat_only_name and spoke_man and spoke_time and spoken_text:
            if 'rm' in spoken_text:
                resp = make_response("del success")
                resp.delete_cookie('token')
                resp.delete_cookie('name')
                return resp, 500
            text = json_str({"chat_only_name": chat_only_name, "spoke_man": spoke_man, "spoke_time": spoke_time,
                             "spoken_text": spoken_text})
            mysql_content_in(chat_only_name=chat_only_name, spoke_man=spoke_man, spoke_time=spoke_time,
                             spoken_text=spoken_text)
            set_redis_content(chat_only_name=chat_only_name, text=text)
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
    # print(request.json.get("texts"))
    if token:
        chat_only_name = request.json.get("chat_only_name")
        if chat_only_name:
            data = get_redis_content(chat_only_name=chat_only_name)
            data = content_set_list(data)
            # data数据进行处理 然后排序
            data = time_set(data=data)
            # print(data)
            data = sorted(data, key=lambda list1: list1["spoke_time"], reverse=True)
            data = time_make(data)
            username = get_redis_token(token=token)
            return {"data": data, "username": username}, 200

        else:
            return 'Hello World!', 400
        pass
    else:
        return 'Hello World!', 300


@app.route('/favicon.ico')  # 设置icon
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/ico'),  # 对于当前文件所在路径,比如这里是static下的favicon.ico
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=7788)
