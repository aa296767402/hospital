from flask import Blueprint, render_template, redirect, url_for, flash, current_app, session, request, make_response
from app.forms import RegisterForm, LoginForm, UploadForm, ChangemmForm, DealqueueForm, CheckqueueForm,DocmsgForm, DocqueueForm, StoreCheckForm
from app.models import User, generate_password_hash,Doctor, Queue, Stores, Message
from app.extensions import db, photos
from app.mail import send_mail
from flask_login import login_user, logout_user, login_required, current_user
from PIL import Image
import os
from datetime import datetime,date,time,timedelta
today = date.today()
#

doctor = Blueprint('doctor', __name__)
@doctor.route('/help/')
def help():
    return render_template('doctor/help.html')
#首页
@doctor.route('/')
def index():
    name = Doctor.query.filter(Doctor.name == session.get('username')).first()
    if name:
        msg = Message.query.filter(Message.doc_name == session.get('username')).filter(Message.user_msg != None).filter(Message.doc_msg == None)
    # if current_user.identify == 1:
    #     flash('请到对应页面登录')
    #     return redirect(url_for('user.index'))
        t = datetime.utcnow()
        return render_template('doctor/main.html', msg=msg,t=t,endpoint='doctor.remessage')
    else:
        flash('请到对应页面登录')
        session.pop('username')
        return redirect(url_for('main.index'))

#查看留言
@doctor.route('/message/')
def message():
    name = Doctor.query.filter(Doctor.name == session.get('username')).first()
    if name:
        msg = Message.query.filter(Message.doc_name == session.get('username')).filter(Message.doc_msg == None).filter(Message.user_msg != None)
        return render_template('doctor/message.html', msg=msg,endpoint='doctor.remessage', endpoint2='doctor.rmmessage')
    else:
        session.pop('username', None)
        flash('请到对应页面登录')
        return redirect(url_for('main.index'))


#回复留言
@doctor.route('/remessage/', methods=['GET', 'POST'])
def remessage():
    name = Doctor.query.filter(Doctor.name == session.get('username')).first()
    if name:
        form = DocmsgForm()
        id = request.args.get('id')
        msg = Message.query.get(id)
        if form.validate_on_submit():
            message=Message.query.get(id)
            message.doc_msg=form.mssg.data
            db.session.add(message)
            db.session.commit()
            return redirect(url_for('doctor.messagehistory'))
        # queue = Queue.query.filter(Queue.id == id).delete()
        return render_template('doctor/remessage.html', msg=msg,form = form)
    else:
        session.pop('username', None)
        flash('请到对应页面登录')
        return redirect(url_for('main.index'))
#删除留言
@doctor.route('/rmmessage/')
def rmmessage():
    id = request.args.get('id')
    msg = Message.query.filter(Message.id==id).delete()


    return redirect(url_for('doctor.message'))

#留言历史
@doctor.route('/messagehistory/')
def messagehistory():
    msg = Message.query.filter(Message.doc_name == session.get('username')).filter(Message.user_msg != None).filter(Message.doc_msg != None)
    return render_template('doctor/messagehistory.html',msg=msg)


@doctor.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        u = Doctor.query.filter(Doctor.name == form.username.data).first()
        if not u:
            flash('无效的用户名')
        elif u.verify_password(form.password.data):
            login_user(u)
            session['username']= form.username.data
            # flash('登录成功')
            return redirect(request.args.get('next') or url_for('doctor.index'))
        else:
            flash('无效的密码')
    return render_template('doctor/login.html', form=form)


#更改密码
@doctor.route('/change_mm/', methods=['POST', 'GET'])
def change_mm():
    name = Doctor.query.filter(Doctor.name == session.get('username')).first()
    if name:
        form = ChangemmForm()
        if form.validate_on_submit():
            if current_user.verify_password(form.oldmm.data):
                current_user.password_hash = generate_password_hash(form.newmm.data)
                db.session.add(current_user)
                db.session.commit()
                flash('密码修改成功')
                logout_user()
                return redirect(url_for('doctor.index'))
            else:
                flash('原密码错误')
        return render_template('doctor/change_mima.html', form=form)
    else:
        session.pop('username', None)
        flash('请到对应页面登录')
        return redirect(url_for('main.index'))

#检查排队信息
@doctor.route('/checkqueue/', methods=['POST', 'GET'])
def checkqueue():
    name = Doctor.query.filter(Doctor.name == session.get('username')).first()
    if name:
        form= CheckqueueForm()
        name = form.name.data
        u = Queue.query.filter(Queue.name == form.name.data).first()
        if form.validate_on_submit():
            if not u:
                flash('您输入的用户名有误')
                return redirect(url_for('doctor.checkqueue'))
            if u:
                queues = Queue.query.filter(Queue.name==name)
                resp = redirect(url_for('doctor.dealqueue'))
                resp.set_cookie('name', form.name.data)
                return resp
            if id:
                q = Queue.query.get(id)
                db.session.delete(q)
                db.session.commit()
                return redirect(url_for('doctor.dealqueue'))
        page = request.args.get('page', 1, type=int)
        queue = Queue.query.filter(Queue.doc_desc == None).paginate(page=page, per_page=8, error_out=False)
        posts = queue.items
        return render_template('doctor/checkqueue.html',form = form,queue=queue, endpoint1='doctor.docdeal', endpoint2='doctor.delpatient', posts= posts)
    else:
        session.pop('username', None)
        flash('请到对应页面登录')
        return redirect(url_for('main.index'))
#诊断用户
@doctor.route('/dealqueue/', methods=['POST', 'GET'])
def dealqueue():
    name = Doctor.query.filter(Doctor.name == session.get('username')).first()
    if name:
        form = DealqueueForm()
        # def get_cookie():
            # name = request.cookies.get('name', 'none')
        name = request.cookies.get('name', None)
        queue = Queue.query.filter(Queue.name == name).filter(Queue.doc_desc == None)
        if form.validate_on_submit():
            u = Queue.query.filter(Queue.name == name).first()
            users = User.query.filter(User.username == name).first()
            form = DealqueueForm()

            if u:
                print("________________-")
                u.doc_desc=form.doc_desc.data
                u.treat=form.trate.data
                u.doctor_id = current_user.id
                u.doctor_name=session.get('username')
                db.session.add(u)
                db.session.commit()

                return redirect(url_for('doctor.checkqueue'))

        return render_template('doctor/dealqueue.html', queue=queue, form=form, )
    else:
        session.pop('username', None)
        flash('请到对应页面登录')
        return redirect(url_for('main.index'))
# @doctor.route('/dealqueue/', methods=['POST', 'GET'])
# def dealqueue():
#     form = DealqueueForm()
#     # def get_cookie():
#         # name = request.cookies.get('name', 'none')
#     name = request.cookies.get('name', None)
#         # return name
#     u = Queue.query.filter(Queue.name == name).first()
#     form = DealqueueForm()
#     queue = Queue.query.filter(Queue.name == name)
#     if form.validate_on_submit():
#         if u:
#             # qu = Queue(
#             #     doc_desc=form.doc_desc.data,
#             #     treat=form.trate.data
#             # )
#             # db.session.add(qu)
#             u.doc_desc=form.doc_desc.data
#             # db.session.add(u)
#             u.treat=form.trate.data
#             # db.session.add(u.desc)
#             db.session.add(u)
#             db.session.commit()
#             return redirect(url_for('doctor.index'))
#     return render_template('doctor/dealqueue.html', queue=queue, form=form)

@doctor.route('/docdeal/', methods=['POST', 'GET'])
def docdeal():
    name = Doctor.query.filter(Doctor.name == session.get('username')).first()
    if name:
        form = DealqueueForm()
        id = request.args.get('id')
        u = Queue.query.filter(Queue.id==id).first()
        queue = Queue.query.filter(Queue.id == id)
        if form.validate_on_submit():
            if u:
                u.doc_desc = form.doc_desc.data
                u.treat = form.trate.data
                u.doctor_id=current_user.id
                u.doctor_name = session.get('username')
                db.session.add(u)
                db.session.commit()
                return redirect(url_for('doctor.checkqueue'))
        return render_template('doctor/docdeal.html', queue=queue, form=form)
    else:
        session.pop('username', None)
        flash('请到对应页面登录')
        return redirect(url_for('main.index'))

# 删除挂号
@login_required
@doctor.route('/delpatient/')
def delpatient():
    name = Doctor.query.filter(Doctor.name == session.get('username')).first()
    if name:
        id = request.args.get('id')
        queue = Queue.query.filter(Queue.id ==id ).delete()
        return redirect(url_for('doctor.mypatient'))
    else:
        session.pop('username', None)
        flash('请到对应页面登录')
        return redirect(url_for('main.index'))


#删除排队表中的数据
 # id = request.args.get('id')
 #        if id:
 #            q = Queue.query.get(id)
 #            db.session.delete(q)
 #            db.session.commit()
 #            return redirect(url_for('doctor.dealqueue'))

@login_required
@doctor.route('/mypatient/')
def mypatient():
    name = Doctor.query.filter(Doctor.name == session.get('username')).first()
    if name:
        page = request.args.get('page', 1, type=int)
        queue = Queue.query.filter(Queue.doctor_name == session.get('username')).paginate(page=page, per_page=8, error_out=False)
        posts = queue.items
        return render_template('doctor/mypatient.html', queue = queue,  posts = posts,endpoint1='doctor.docdeal', endpoint2='doctor.dealqueue')

    else:
        session.pop('username', None)
        flash('请到对应页面登录')
        return redirect(url_for('main.index'))



@login_required
@doctor.route('/history/',  methods=['POST', 'GET'])
def history():
    name = Doctor.query.filter(Doctor.name == session.get('username')).first()
    if name:
        form = CheckqueueForm()
        u = Queue.query.filter(Queue.name == form.name.data).first()
        # if form.validate_on_submit():
        #     if not u:
        #         flash('您输入的用户名有误')
        #         return redirect(url_for('doctor.checkqueue'))
        #     if u:
        if form.validate_on_submit():
            if not u:
                flash('您输入的用户名有误')
                return redirect(url_for('doctor.history'))
            if u:
                resp = redirect(url_for('doctor.ahistory'))
                resp.set_cookie('name', form.name.data)
                return resp
        page = request.args.get('page', 1, type=int)
        queue = Queue.query.filter(Queue.doctor_name == session.get('username')).paginate(page=page, per_page=8, error_out=False)
        posts = queue.items
        print(current_user.id)
        return render_template('doctor/history.html', queue=queue, form= form, posts = posts)
    else:
        session.pop('username', None)
        flash('请到对应页面登录')
        return redirect(url_for('main.index'))
@login_required
@doctor.route('/ahistory/')
def ahistory():
    name = request.cookies.get('name', None)
    user = Queue.query.filter(Queue.name == name).filter(Queue.doc_desc!=None)
    return render_template('doctor/ahistory.html', user = user)


#医生信息
@login_required
@doctor.route('/doctorinfo/')
def doctorinfo():
    name = Doctor.query.filter(Doctor.name == session.get('username')).first()
    if name:
        doctors = Doctor.query.all()
        return render_template('doctor/doctorinfo.html', doctors=doctors)
    else:
        session.pop('username', None)
        flash('请到对应页面登录')
        return redirect(url_for('main.index'))

#医生个人信息
@login_required
@doctor.route('/profile/')
def profile():
    name = Doctor.query.filter(Doctor.name == session.get('username')).first()
    if name:
        doctor = Doctor.query.filter(Doctor.id == current_user.id).first()
        return render_template('doctor/profile.html', doctor = doctor)
    else:
        session.pop('username', None)
        flash('请到对应页面登录')
        return redirect(url_for('main.index'))

#查看库存信息
@login_required
@doctor.route('/store/',  methods=['POST', 'GET'])
def store():
    name = Doctor.query.filter(Doctor.name == session.get('username')).first()
    if name:
        form = StoreCheckForm()
        if form.validate_on_submit():
            u = Stores.query.filter(Stores.name == form.name.data).first()
            if not u:
                flash('您输入的用户名有误')
                return redirect(url_for('doctor.store'))
            if u:
                resp = redirect(url_for('doctor.astore'))
                resp.set_cookie('name', form.name.data)
                return resp
        page = request.args.get('page', 1, type=int)
        stores = Stores.query.filter(Stores.id != None).paginate(page=page, per_page=8, error_out=False)
        posts = stores.items
        return render_template('doctor/store.html', stores=stores, posts = posts, form= form)
    else:
        session.pop('username', None)
        flash('请到对应页面登录')
        return redirect(url_for('main.index'))

@login_required
@doctor.route('/astore/')
def astore():
    name = request.cookies.get('name', None)
    user = Stores.query.filter(Stores.name == name)
    return render_template('doctor/astore.html', user=user)


@login_required
@doctor.route('/queue/', methods=['GET', 'POST'])
def queue():
    form = DocqueueForm()
    if form.validate_on_submit():
        q = Queue(
            name=form.name.data,
            age=form.age.data,
            sex=form.selectsex.data,
            tel=form.tele.data,
            for_time1=today,
            user_id=current_user.id,
        )
        db.session.add(q)
        db.session.commit()
        flash('成功挂号排队')
        resp = redirect(url_for('doctor.dealqueue'))
        resp.set_cookie('name', form.name.data)
        return resp
    return render_template('doctor/queue.html', form = form)

