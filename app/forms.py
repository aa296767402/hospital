from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField,TextAreaField,SelectField, RadioField
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms.validators import Length, EqualTo, Email, DataRequired, ValidationError
from app.models import User, Doctor
from app.extensions import photos
# from datetime import time,timezone,datetime, timedelta
import datetime
from wtforms.ext.sqlalchemy.fields import QuerySelectField
oneday = datetime.timedelta(days=1)
today = datetime.date.today()
tomorrow = datetime.date.today() + oneday
ttomorrow= datetime.date.today() + oneday+oneday
tttomorrow = datetime.date.today() + oneday+ oneday+oneday


# 用户注册
class RegisterForm(FlaskForm):
    username = StringField('用户名',  validators=[DataRequired(message='姓名不能为空')])
    sex = SelectField('性别：', choices=[('男', '男'), ('女', '女')])
    tele = StringField('电话：', validators=[Length(11, 11, message='请输入11位手机号')])
    password = PasswordField('密码', validators=[Length(4, 12, message='密码长度必须在4~12个字符之间')])
    confirm = PasswordField('确认密码', validators=[EqualTo('password', message='两次密码不一致')])
    email = StringField('邮箱', validators=[Email(message='无效的邮箱格式')])
    submit = SubmitField('立即注册')

    # 自定义验证函数，验证username
    def validate_username(self, field):
        if User.query.filter(User.username == field.data).first():
            raise ValidationError('该用户已注册，请选用其他名称')
        return True

    # 自定义验证函数，验证email
    def validate_email(self, field):
        if User.query.filter(User.email == field.data).first():
            raise ValidationError('该邮箱已注册，请选用其他邮箱')
        return True



#医生注册表单
class RegisterdocForm(FlaskForm):
    name = StringField('姓名', validators=[DataRequired(message='姓名不能为空')])
    password = PasswordField('密码', validators=[Length(4, 12, message='密码长度必须在4~12个字符之间')])
    age = StringField('年龄：', validators=[DataRequired(message='年龄不能为空')])
    tel = StringField('电话：', validators=[Length(11, 11, message='请输入11位手机号')])
    dirc = TextAreaField('研究方向：', validators=[DataRequired(message='方向不能为空')])
    intr = TextAreaField('工作经历：')
    addr = TextAreaField('地址：')
    submit = SubmitField('立即注册')

    # 自定义验证函数，验证username
    def validate_name(self, field):
        if Doctor.query.filter(Doctor.name == field.data).first():
            raise ValidationError('该用户名已注册，请选用其他名称')
        return True




# 用户登录表单
class LoginForm(FlaskForm):
    username = StringField('姓名', validators=[DataRequired(message='用户名不能为空')])
    password = PasswordField('密码', validators=[DataRequired(message='密码不能为空')])
    # remember = BooleanField('记住我')
    # sex = RadioField('性别', choices=[('男','男'),('女','女')])
    submit = SubmitField('立即登录')


# 上传头像表单
class UploadForm(FlaskForm):
    icon = FileField('我的头像', validators=[FileRequired('请选择文件'), FileAllowed(photos, '只能上传图片')])
    submit = SubmitField('上传')

class ChangemmForm(FlaskForm):
    oldmm = StringField('原密码', validators=[DataRequired(message='原密码不能为空')])
    newmm = PasswordField('新密码', validators=[Length(4, 12, message='密码长度在4到12个字符之间')])
    confirmmm = PasswordField('重新输入', validators=[EqualTo('newmm', message='您两次输入的密码不一致')])
    submit= SubmitField('确认修改')


class QueueForm(FlaskForm):
    lt = [('张三', '张三'), ('李四', '李四'), ('张珂', '张珂'), ('张花', '张花'), ('李峰', '李峰'), ('李晓', '李晓'), ('张鑫', '张鑫'), ]


    docselect = SelectField('选择医生：',choices=lt)
    dataselect = SelectField('选择就诊日期：', choices=[(str(tomorrow)+'上午8:00-11：30',str(tomorrow)+'上午8:00-11：30' ),(str(tomorrow)+'下午3:00-6:00', str(tomorrow) + '下午3:00-6:00' ), (str(ttomorrow)+'上午8:00-11：30',str(ttomorrow)+'上午8:00-11：30' ),(str(ttomorrow)+'下午3:00-6:00', str(ttomorrow) + '下午3:00-6:00' ), (str(tttomorrow)+'上午8:00-11：30',str(tttomorrow)+'上午8:00-11：30' ),(str(tttomorrow)+'下午3:00-6:00', str(tttomorrow) + '下午3:00-6:00' )])
    name = StringField('姓名：', validators=[DataRequired(message='姓名不能为空')])
    selectsex = SelectField('性别：', choices=[('男', '男'), ('女', '女')])
    age = StringField('年龄：', validators=[DataRequired(message='年龄不能为空')])
    tele = StringField('电话：',validators=[Length(11, 11, message='请输入11位手机号')])
    desc =TextAreaField('描述您的症状：',  validators=[DataRequired(message='请描述您的症状')])
    submit = SubmitField('确认排队')


class DealqueueForm(FlaskForm):
    doc_desc = StringField('诊断',validators=[DataRequired(message='诊断不能为空')] )
    trate = TextAreaField('治疗' ,validators=[DataRequired(message='诊断不能为空')])
    submit = SubmitField('确认提交')


class CheckqueueForm(FlaskForm):
    name=StringField('请输入患者姓名：',validators=[DataRequired(message='名字不能为空')])
    submit = SubmitField('查找')

class CheckDocandPat(FlaskForm):
    # select = SelectField('选择要查询的身份：', choices=[('医生','医生'),('用户', '用户')])
    name = StringField('请输入要查询的姓名：', validators=[DataRequired(message='名字不能为空')])

    submit = SubmitField('查找')

class Addstores(FlaskForm):
    name = StringField('药品名称：', validators=[DataRequired(message='名字不能为空')])
    sort = StringField('分类：', validators=[DataRequired(message='分类不能为空')])
    guige = StringField('规格：', validators=[DataRequired(message='规格不能为空')])
    come_source = StringField('来源：', validators=[DataRequired(message='来源不能为空')])
    amount = StringField('数量：', validators=[DataRequired(message='数量不能为空')])
    submit = SubmitField('提交')

class Changestore(FlaskForm):
    come_source = StringField('来源：', validators=[DataRequired(message='来源不能为空')])
    amount = StringField('数量：', validators=[DataRequired(message='数量不能为空')])
    submit = SubmitField('提交')

class MessageForm(FlaskForm):
    doc =StringField('用户名', )
    mssg= StringField('留言信息：',  validators=[DataRequired(message='名字不能为空')])
    submit = SubmitField('提交')

class DocmsgForm(FlaskForm):
    mssg = StringField('回复留言：', validators=[DataRequired(message='回复不能为空')])
    submit = SubmitField('提交')


class DocqueueForm(FlaskForm):
    name = StringField('姓名：', validators=[DataRequired(message='姓名不能为空')])
    selectsex = SelectField('性别：', choices=[('男', '男'), ('女', '女')])
    age = StringField('年龄：', validators=[DataRequired(message='年龄不能为空')])
    tele = StringField('电话：',validators=[Length(11, 11, message='请输入11位手机号')])
    submit = SubmitField('确认排队')

class StoreCheckForm(FlaskForm):
    name = StringField('请输入要查询的药品名字：', validators=[DataRequired(message='药品名字不能为空')])

    submit = SubmitField('查找')

