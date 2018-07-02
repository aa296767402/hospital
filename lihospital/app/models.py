from flask import current_app
from app.extensions import db, login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from datetime import time,timezone,datetime


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32))
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(64), unique=True)
    confirmed = db.Column(db.Boolean, default=0)
    # 头像
    icon = db.Column(db.String(64), default='default.jpeg')


    queues = db.relationship('Queue', backref='user', lazy='dynamic')
    tel = db.Column(db.String(11), unique=True)
    sex = db.Column(db.String(8))
    is_delete = db.Column(db.Boolean, default=0)


    @property
    def password(self):
        raise AttributeError('不能访问密码属性')

    @password.setter
    def password(self, password):
        # 密码需要加密后存储
        self.password_hash = generate_password_hash(password)

    # 校验密码
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # 生成账户激活的token
    def generate_activate_token(self, expires_in=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expires_in)
        return s.dumps({'id': self.id})

    # 校验账户激活的token
    @staticmethod
    def check_activate_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        u = User.query.get(data['id'])
        if not u:
            return False
        if not u.confirmed:
            u.confirmed = True
            db.session.add(u)
        return True


# 该装饰器其实就是一个回调函数
@login_manager.user_loader
def loader_user(uid):
    return User.query.get(uid)


class Stores(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), index=True)
    sort = db.Column(db.String(8))
    guige = db.Column(db.String(64))
    come_sourse = db.Column(db.String(64))
    amount = db.Column(db.Integer)
    input_time = db.Column(db.DateTime, default=datetime.now())
    is_delete = db.Column(db.Boolean, default=0)


class Doctor(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))
    age = db.Column(db.Integer)
    dirc = db.Column(db.String(64))
    intr = db.Column(db.String(128))
    tel=db.Column(db.String(11), unique=True)
    addr = db.Column(db.String(64))
    is_rest = db.Column(db.Boolean, default=0)
    is_delete = db.Column(db.Boolean, default=0)
    # queues = db.relationship('Queue', backref='doctor', lazy='dynamic')

    @property
    def password(self):
        raise AttributeError('不能访问密码属性')

    @password.setter
    def password(self, password):
        # 密码需要加密后存储
        self.password_hash = generate_password_hash(password)

    # 校验密码
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)




class Queue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(8))
    sex = db.Column(db.String(8))
    age = db.Column(db.Integer)
    addr = db.Column(db.String(64))
    tel = db.Column(db.String(11), unique=True)
    desc=db.Column(db.String(140))
    submit_time = db.Column(db.DateTime, default=datetime.now())
    doc_desc = db.Column(db.String(128), nullable=True)
    treat = db.Column(db.String(128), nullable=True)
    for_time1 = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'))
    doctor_name = db.Column(db.String(64))
    is_delete = db.Column(db.Boolean, default=0)
# class text(db.Model):
#     id = db.Column(db.Integ
#     submit_time = db.Column(db.DateTime, default=datetime.now())
# usertodoc = db.Table('usertodoc',
#     db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
#     db.Column('doctor_id', db.Integer, db.ForeignKey('doctor.id'))
# )

# class Useranddoc(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     user_id = db.Column(db.Integer)
#     doctor_id =db.Column(db.Integer)
# class admin(UserMixin, db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     name = db.Column(db.String(64))
#     password_hash = db.Column(db.String(128))
#
#     @property
#     def password(self):
#         raise AttributeError('不能访问密码属性')
#
#     @password.setter
#     def password(self, password):
#         # 密码需要加密后存储
#         self.password_hash = generate_password_hash(password)


class Admins(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    password_hash = db.Column(db.String(128))


    @property
    def password(self):
        raise AttributeError('不能访问密码属性')

    @password.setter
    def password(self, password):
        # 密码需要加密后存储
        self.password_hash = generate_password_hash(password)


    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id =db.Column(db.Integer)
    doc_id = db.Column(db.Integer)
    user_msg = db.Column(db.String(128))
    doc_msg = db.Column(db.String(128))
    user_name= db.Column(db.String(8))
    doc_name= db.Column(db.String(8))
    user_time = db.Column(db.DateTime, default=datetime.now())
    doc_time = db.Column(db.DateTime, default=datetime.now())
    isdelete= db.Column(db.Boolean,default=0)