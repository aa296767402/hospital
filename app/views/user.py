from flask import Blueprint, render_template, redirect, url_for, flash, current_app, session, request
from app.forms import RegisterForm, LoginForm, UploadForm, ChangemmForm, QueueForm,MessageForm, CheckDocandPat
from app.models import User, generate_password_hash, Queue, Doctor, Message
from app.extensions import db, photos
from app.mail import send_mail
from flask_login import login_user, logout_user, login_required, current_user
from PIL import Image
import os
from datetime import datetime,date,time,timedelta

# import datetime
oneday = timedelta(days=1)
today = date.today()

tomorrow = date.today() + oneday
ttomorrow= date.today() + oneday+oneday
tttomorrow = date.today() + oneday+ oneday+oneday


user = Blueprint('user', __name__)
@user.route('/help/')
def help():
    return render_template('user/help.html')
# u = User.query.filter(User.username == form.username.data).first()
#     if name.identify != 1:
#         flash('请到对应页面登录')
#         session.pop('username', None)
#         return redirect(url_for('main.index'))
@login_required
@user.route('/')
def index():
    name = User.query.filter(User.username == session.get('username')).first()
    if name:
        queue = Queue.query.filter(Queue.user_id == current_user.id).filter(Queue.treat == None)
        t = datetime.utcnow()
        return render_template('user/index.html', queue=queue, t=today)
    else:
        flash('请到对应页面登录')
        session.pop('username')
        return redirect(url_for('main.index'))


#登出
@login_required
@user.route('/logout/')
def logout():
    # 退出登录
    session.pop('username')
    logout_user()
    flash('您已退出登录')
    return redirect(url_for('main.index'))

#登录
@user.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        u = User.query.filter(User.username == form.username.data).first()
        if not u:
            flash('无效的用户名')
        elif u.confirmed == 0:
            flash('账户尚未激活，请激活后再登录')
        elif u.verify_password(form.password.data):
            # 用户登录，顺便可以完成记住我的功能，还可以指定有效时间
            session['username'] = form.username.data
            login_user(u)
            # flash('登录成功')
            return redirect(request.args.get('next') or url_for('user.index'))
        else:
            flash('无效的密码')
    return render_template('user/login.html', form=form)


#我的挂号
@user.route('/queue/',methods=['GET', 'POST'])
@login_required
def queue():
        form = QueueForm()
        addr = request.form.get('selectdoc')
        print(addr)
        print('***************************************************************')
        if form.validate_on_submit():
            q = Queue(
                name=form.name.data,
                age=form.age.data,
                sex=form.selectsex.data,
                tel=form.tele.data,
                desc=form.desc.data,
                for_time1=form.dataselect.data,
                user_id=current_user.id,
                addr=form.docselect.data
            )

            u= User(
                username=form.name.data
            )

            db.session.add(q)
            db.session.add(u)
            db.session.commit()
            flash('您已成功挂号排队')
            return redirect(url_for('user.index'))
        doc = Doctor.query.filter(Doctor.id!=None)
        return render_template('user/queue.html', form = form, doc=doc)
    # else:
    #     flash('请到对应页面登录')
    #     session.pop('username')
    #     return redirect(url_for('main.index'))


#查询挂号
@user.route('/myqueue/')
@login_required
def myqueue():
    name = User.query.filter(User.username == session.get('username')).first()
    if name:
        page = request.args.get('page', 1, type=int)
        queues = Queue.query.filter(Queue.treat == None).paginate(page=page, per_page=7, error_out=False)
        posts = queues.items
        return render_template('user/myqueue.html', queues = queues, endpoint='user.delqueue', posts=posts)
    else:
        flash('请到对应页面登录')
        session.pop('username')
        return redirect(url_for('main.index'))

#删除挂号
@user.route('/delqueue/')
@login_required
def delqueue():
    id = request.args.get('id')
    queue = Queue.query.filter(Queue.id ==id).delete()
    return redirect(url_for('user.myqueue'))



#注册
@user.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        # 根据表单数据创建User对象
        u = User(username=form.username.data,
                 password=form.password.data,
                 email=form.email.data,
                 sex = form.sex.data,
                 tel=form.tele.data,
                 )
        # 然后保存到数据库中
        db.session.add(u)
        # 此时还没有提交，所以新用户没有id值，需要手动提交
        db.session.commit()
        # 准备token
        # 发送激活邮件
        token = u.generate_activate_token()
        url = url_for('user.activate', token=token, _external=True)
        send_mail(form.email.data, '账户激活', 'activate', username=form.username.data, url=url)
        flash('激活邮件已发送至您的邮箱，请点击连接以完成激活')
        return redirect(url_for('main.index'))
    return render_template('user/register.html', form=form)

#激活
@user.route('/activate/<token>')
def activate(token):
    if User.check_activate_token(token):
        flash('激活成功')
        return redirect(url_for('user.login'))
    else:
        flash('激活失败')
        return redirect(url_for('main.index'))


# 用户详情
@login_required
@user.route('/profile/')
# @login_required
def profile():
    name = User.query.filter(User.username == session.get('username')).first()
    if name:
        img_url = photos.url(current_user.icon)
        users =User.query.all()
        return render_template('user/profile.html',img_url =img_url)
    else:
        flash('请到对应页面登录')
        session.pop('username')
        return redirect(url_for('main.index'))

# 客户查询医生信息
@login_required
@user.route('/doctorinfo/')
def doctorinfo():

    doctors = Doctor.query.all()
    return render_template('user/doctorinfo.html', doctors = doctors)


# 上传头像
@user.route('/change_icon/', methods=['GET','POST'])
def change_icon():
    form = UploadForm()
    if form.validate_on_submit():
        # 获取后缀
        suffix = os.path.splitext(form.icon.data.filename)[1]
        # 随机文件名
        filename = random_string() + suffix
        photos.save(form.icon.data, name=filename)
        # 生成缩略图
        pathname = os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], filename)
        img = Image.open(pathname)
        img.thumbnail((128, 128))
        img.save(pathname)
        # 删除原来的头像(不是默认头像时才需要删除)
        if current_user.icon != 'default.jpeg':
            os.remove(os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], current_user.icon))
        # 保存到数据库
        current_user.icon = filename
        db.session.add(current_user)
        return redirect(url_for('user.change_icon'))
    img_url = photos.url(current_user.icon)
    return render_template('user/change_icon.html', form=form, img_url=img_url)

#生成随机头像名
def random_string(length=32):
    import random
    base_str = 'abcdefghijklmnopqrstuvwxyz1234567890'
    return ''.join(random.choice(base_str) for i in range(length))

#更改密码
@login_required
@user.route('/change_mm/', methods=['POST', 'GET'])
def change_mm():
        form = ChangemmForm()
        if form.validate_on_submit():
            if current_user.verify_password(form.oldmm.data):
                current_user.password_hash = generate_password_hash(form.newmm.data)
                db.session.add(current_user)
                db.session.commit()
                flash('密码修改成功')
                logout_user()
                return redirect(url_for('user.login'))
            else:
                flash('原密码错误')
        return render_template('user/change_mima.html', form = form)
    # else:
    #     flash('请到对应页面登录')
    #     session.pop('username')
    #     return redirect(url_for('main.index'))

#看病历史
@login_required
@user.route('/history/', methods=['POST', 'GET'])
def history():
    name = User.query.filter(User.username == session.get('username')).first()
    if name:
        form = CheckDocandPat()
        u = Queue.query.filter(Queue.name == form.name.data).first()
        if form.validate_on_submit():
            if not u:
                flash('您输入的姓名有误，请重新输入')
                return redirect(url_for('user.history'))
            if u:
                resp = redirect(url_for('user.ahistory'))
                resp.set_cookie('name', form.name.data)
                return resp
        page = request.args.get('page', 1, type=int)
        queue = Queue.query.filter(Queue.user_id==current_user.id).filter(Queue.treat!=None).paginate(page=page, per_page=5, error_out=False)
        posts = queue.items
        return render_template('user/history.html' ,queue = queue, posts=posts, form=form)
    else:
        flash('请到对应页面登录')
        session.pop('username')
        return redirect(url_for('main.index'))

#看病历史
@login_required
@user.route('/ahistory/')
def ahistory():
    name = request.cookies.get('name', None)
    user = Queue.query.filter(Queue.name == name).filter(Queue.doc_desc != None)
    return render_template('user/ahistory.html', user=user)


#我的医生：
@login_required
@user.route('/mydoc/', methods=['POST', 'GET'])
def mydoc():
    name = User.query.filter(User.username == session.get('username')).first()
    if name:
        form = CheckDocandPat()
        u = Queue.query.filter(Queue.name == form.name.data).first()
        if form.validate_on_submit():
            if not u:
                flash('您输入的姓名有误，请重新输入')
                return redirect(url_for('user.history'))
            if u:
                resp = redirect(url_for('user.ahistory'))
                resp.set_cookie('name', form.name.data)
                return resp
        page = request.args.get('page', 1, type=int)
        queue = Queue.query.filter(Queue.user_id == current_user.id).filter(Queue.treat != None).paginate(page=page, per_page=5, error_out=False)
        posts = queue.items
        return render_template('user/mydoc.html',queue=queue, form = form, posts=posts)
    else:
        flash('请到对应页面登录')
        session.pop('username')
        return redirect(url_for('main.index'))


@user.route('/message/', methods=['POST', 'GET'])
@login_required
def message():
    doctor = Doctor.query.all()
    if request.method=='GET':
        return render_template('user/message.html', doctor=doctor)
    else:

        msg = Message(
            user_id=current_user.id,
            user_name=current_user.username,
            doc_name=request.form.get("selectdoc"),
            user_msg=request.form.get("leave"),
        )
        db.session.add(msg)
        db.session.commit()
        return redirect(url_for('user.mymessage'))
#
#
@user.route('/mymessage/')
@login_required
def mymessage():
    message = Message.query.filter(Message.doc_msg!=None)
    return render_template('user/mymessage.html', message=message)

@user.route('/messagehistory/')
@login_required
def messagehistory():
    message = Message.query.filter(Message.doc_msg==None)
    return render_template('user/messagehistory.html', message=message,endpoint2='user.rmmessage')

@user.route('/rmmessage/')
def rmmessage():
    id = request.args.get('id')
    msg = Message.query.filter(Message.id == id).delete()

    return redirect(url_for('user.mymessage'))