from flask import Blueprint, render_template, redirect, url_for, flash, current_app, session, request
from app.forms import RegisterForm, LoginForm, UploadForm, ChangemmForm, RegisterdocForm, Addstores, CheckqueueForm, CheckDocandPat,StoreCheckForm, Changestore
from app.models import User, generate_password_hash, Doctor, Queue, Stores,Admins
from app.extensions import db, photos
from app.mail import send_mail
from flask_login import login_user, logout_user, login_required, current_user
from PIL import Image
import os
from datetime import datetime,date,time,timedelta
# today = date.today()
today = datetime.utcnow()


admin = Blueprint('admin', __name__)

@admin.route('/help/')
def help():
    return render_template('admin/help.html')
#管理员登陆
@admin.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        u = Admins.query.filter(Admins.name == form.username.data).first()
        if not u:
            flash('无效的用户名')
        elif u.verify_password(form.password.data):
            # 用户登录，顺便可以完成记住我的功能，还可以指定有效时间
            login_user(u)

            session['username'] = form.username.data
            # flash('登录成功')
            return redirect(request.args.get('next') or url_for('admin.index'))
        else:
            flash('无效的密码')
    return render_template('admin/login.html', form=form)

@admin.route('/')
def index():
    # try:
    #     name = Admins.query.filter(Admins.name == session.get('username')).first()
    # except:
    #     flash('请到对应页面登录')
    #     session.pop('username')
    #     return redirect(url_for('main.index'))
    name = Admins.query.filter(Admins.name == session.get('username')).first()
    if name:
        return render_template('admin/main.html')
    else:
        flash('请到对应页面登录')
        session.pop('username', None)
        return redirect(url_for('main.index'))


@admin.route('/profile/')
@login_required
def profile():
    name = Admins.query.filter(Admins.name == session.get('username')).first()
    if name:
        # users =User.query.all()
        doctors= Doctor.query.all()
        doctor = Doctor.query.filter(Doctor.is_rest ==0)
        print(session.get('username'))
        docsnum = 0
        docnum=0
        for i in doctors:
            if i:
                docsnum = docsnum+1
        for doc in doctor:
            if doc:
                docnum = docnum+1
        return render_template('admin/profile.html', nums=docsnum, num = docnum)
    else:
        flash('请到对应页面登录')
        session.pop('username', None)
        return redirect(url_for('main.index'))

# 客户查询医生信息
@admin.route('/doctorinfo/')
@login_required
def doctorinfo():
    name = Admins.query.filter(Admins.name == session.get('username')).first()
    if name:
        users = Doctor.query.all()
        return render_template('admin/doctorinfo.html', users=users, endpoint1='admin.deldoc')
    else:
        flash('请到对应页面登录')
        session.pop('username')
        return redirect(url_for('main.index'))

@admin.route('/change_mm/', methods=['POST', 'GET'])
@login_required
def change_mm():
    name = Admins.query.filter(Admins.name == session.get('username')).first()
    if name:
        form = ChangemmForm()
        if form.validate_on_submit():
            if current_user.verify_password(form.oldmm.data):
                current_user.password_hash = generate_password_hash(form.newmm.data)
                db.session.add(current_user)
                db.session.commit()
                flash('密码修改成功')
                logout_user()
                return redirect(url_for('admin.login'))
            else:
                flash('原密码错误')
        return render_template('admin/change_mima.html', form = form)
    else:
        flash('请到对应页面登录')
        session.pop('username', None)
        return redirect(url_for('main.index'))

#医生注册
# @admin.route('/register/', methods=['GET', 'POST'])
# def register():
#     form = RegisterdocForm()
#     if form.validate_on_submit():
#         # 根据表单数据创建User对象
#         u = Doctor(name=form.name.data,
#                  password=form.password.data,
#             )
#         # 然后保存到数据库中
#         db.session.add(u)
#         # 此时还没有提交，所以新用户没有id值，需要手动提交
#         db.session.commit()
#         # 准备token
#         # 发送激活邮件
#         # token = u.generate_activate_token()
#         # url = url_for('user.activate', token=token, _external=True)
#         # send_mail(form.email.data, '账户激活', 'activate', username=form.username.data, url=url)
#         flash('医生已注册')
#         return redirect(url_for('admin.index'))
#     return render_template('admin/register.html', form=form)

# @admin.route('/changedoc/')
# def changedoc():
#     docctor = Doctor.query.all()
#     return render_template('admin/changedoc.html', docctor = docctor)

@admin.route('/deldoc/')
@login_required
def deldoc():
    id = request.args.get('id')
    doc =Doctor.query.filter(Doctor.id ==id).delete()
    return redirect(url_for('admin.doctorinfo'))


@login_required
@admin.route('/changedoc/')

def changedoc():
    name = Admins.query.filter(Admins.name == session.get('username')).first()
    if name:
        id = request.args.get('id')
        form = RegisterdocForm()
        doctor = Doctor.query.filter(Doctor.id == id).first()
        if form.validate_on_submit():
            doc = Doctor.query.filter(Doctor.id ==request.args.get('id')).first()
            doc.name=form.name.data
            doc.age = form.age.data,
            doc.tel = form.tel.data,
            doc.dirc = form.dirc.data,
            doc.intr = form.intr.data
            db.session.add(doc)
            db.session.commit()
            return redirect(url_for('admin.doctorinfo'))
        return render_template('admin/changedoc.html', doctor =doctor,form=form)
    else:
        flash('请到对应页面登录')
        session.pop('username', None)
        return redirect(url_for('main.index'))


@admin.route('/register/', methods=['GET', 'POST'])
def register():
    name = Admins.query.filter(Admins.name == session.get('username')).first()
    if name:
        form = RegisterdocForm()
        if form.validate_on_submit():
            # 根据表单数据创建User对象
            u = Doctor(name=form.name.data,
                     password=form.password.data,
                        age=form.age.data,
                       tel=form.tel.data,
                       intr=form.intr.data,
                       dirc=form.dirc.data,
                       addr=form.addr.data,
                       # identify=1,
                )
            # 然后保存到数据库中
            db.session.add(u)
            # 此时还没有提交，所以新用户没有id值，需要手动提交
            db.session.commit()
            # 准备token
            # 发送激活邮件
            # token = u.generate_activate_token()
            # url = url_for('user.activate', token=token, _external=True)
            # send_mail(form.email.data, '账户激活', 'activate', username=form.username.data, url=url)
            flash('医生已注册')
            return redirect(url_for('admin.index'))
        return render_template('admin/register.html', form=form)
    else:
        flash('请到对应页面登录')
        session.pop('username', None)
        return redirect(url_for('main.index'))

#管理员检查用户
@admin.route('/checkqueue/', methods=['GET', 'POST'])
def checkqueue():
    form = CheckqueueForm()
    u = Queue.query.filter(Queue.name == form.name.data).first()
    if form.validate_on_submit():
        if not u:
            flash('您输入的用户名有误')
            return redirect(url_for('admin.checkqueue'))
        if u:
            resp = redirect(url_for('admin.acheckqueue'))
            resp.set_cookie('name', form.name.data)
            return resp
    page = request.args.get('page', 1, type=int)
    queue = Queue.query.filter(Queue.id != None).filter(Queue.doc_desc == None).paginate(page=page, per_page=5, error_out=False)
    posts = queue.items
    return render_template('admin/checkqueue.html', queue = queue, posts = posts, form=form)
    # else:
    #     flash('请到对应页面登录')
    #     session.pop('username', None)
    #     return redirect(url_for('main.index'))

@login_required
@admin.route('/acheckqueue/')
def acheckqueue():
    name = request.cookies.get('name', None)
    user = Queue.query.filter(Queue.name == name)

    return render_template('admin/acheckqueue.html', user = user)

#查看库存
@login_required
@admin.route('/store/',  methods=['POST', 'GET'])
def store():
    name = Admins.query.filter(Admins.name == session.get('username')).first()
    if name:
        form = StoreCheckForm()
        if form.validate_on_submit():
            u = Stores.query.filter(Stores.name == form.name.data).first()
            if not u:
                flash('您输入的用户名有误')
                return redirect(url_for('admin.store'))
            if u:
                resp = redirect(url_for('admin.astore'))
                resp.set_cookie('name', form.name.data)
                return resp
        page = request.args.get('page', 1, type=int)
        stores = Stores.query.filter(Stores.id !=None).paginate(page=page, per_page=8, error_out=False)
        posts = stores.items
        return render_template('admin/store.html', stores=stores,endpoint1='admin.delstore', posts=posts, form=form, endpoint2='admin.changestore')
    else:
        flash('请到对应页面登录')
        session.pop('username', None)
        return redirect(url_for('main.index'))
#修改库存
@login_required
@admin.route('/changestore/',  methods=['POST', 'GET'])
def changestore():
    form = Changestore()
    if form.validate_on_submit():

        id = request.args.get('id')
        user = Stores.query.filter(Stores.id == id)
        store = Stores.query.filter(Stores.id == id).first()
        store.come_sourse = form.come_source.data
        store.amount = form.amount.data
        store.input_time = today
        db.session.add(store)
        db.session.commit()
        return redirect(url_for('admin.store'))
    id = request.args.get('id')
    user = Stores.query.filter(Stores.id == id)
    return render_template('admin/changestore.html', form=form, user=user)





@login_required
@admin.route('/astore/')
def astore():
    name = request.cookies.get('name', None)
    user = Stores.query.filter(Stores.name == name)
    return render_template('doctor/astore.html', user=user)

#删除库存
@login_required
@admin.route('/delstore/')
def delstore():

    id = request.args.get('id')
    store = Stores.query.filter(Stores.id == id ).delete()
    return redirect(url_for('admin.store'))

#增加库存
@login_required
@admin.route('/addstores/', methods=['GET', 'POST'])
def addstores():
    name = Admins.query.filter(Admins.name == session.get('username')).first()
    if name:
        form = Addstores()
        if form.validate_on_submit():
            store=Stores(
                name=form.name.data,
                sort = form.sort.data,
                guige=form.guige.data,
                come_sourse=form.come_source.data,
                amount=form.amount.data
            )
            db.session.add(store)
            db.session.commit()
            return redirect(url_for('admin.store'))
        return render_template('admin/addstores.html', form=form)
    else:
        flash('请到对应页面登录')
        session.pop('username', None)
        return redirect(url_for('main.index'))


#添加医生休息
@login_required
@admin.route('/docrest/')
def docrest():
    name = Admins.query.filter(Admins.name == session.get('username')).first()
    if name:
        users = Doctor.query.all()
        return render_template('admin/docrest.html', users=users, endpoint1='admin.rest',endpoint2='admin.delrest')
    else:
        flash('请到对应页面登录')
        session.pop('username', None)
        return redirect(url_for('main.index'))

#添加医生休息
@admin.route('/rest/')
@login_required
def rest():
    name = Admins.query.filter(Admins.name == session.get('username')).first()
    if name:
        id = request.args.get('id')
        doc =Doctor.query.filter(Doctor.id ==id).first()
        doc.is_rest = True
        db.session.add(doc)
        db.session.commit()
        return redirect(url_for('admin.doctorinfo'))
    else:
        flash('请到对应页面登录')
        session.pop('username', None)
        return redirect(url_for('main.index'))

#添加医生休息
@admin.route('/delrest/')
@login_required
def delrest():

    id = request.args.get('id')
    doc =Doctor.query.filter(Doctor.id ==id).first()
    doc.is_rest = False
    db.session.add(doc)
    db.session.commit()
    return redirect(url_for('admin.doctorinfo'))




#查询医生治疗用户的信息
@admin.route('/doctreat/', methods=['GET', 'POST'])
@login_required
def doctreat():
    name = Admins.query.filter(Admins.name == session.get('username')).first()
    if name:
        form = CheckDocandPat()
        if form.validate_on_submit():
            session['name'] = form.name.data
            return redirect(url_for('admin.adoctreat'))
        page = request.args.get('page', 1, type=int)
        queue = Queue.query.filter(Queue.doc_desc != None).paginate(page=page, per_page=7, error_out=False)
        posts = queue.items
        return render_template('admin/doctreat.html', queue=queue, form = form, posts = posts)
    else:
        flash('请到对应页面登录')
        session.pop('username', None)
        return redirect(url_for('main.index'))

@admin.route('/adoctreat/', methods=['GET', 'POST'])
@login_required
def adoctreat():
    name = session.get('name')
    print('***************************')
    print(name)
    queue1 = Queue.query.filter(Queue.name == name).filter(Queue.doc_desc!=None)
    page = request.args.get('page', 1, type=int)
    queue2 = Queue.query.filter(Queue.doctor_name == name).filter(Queue.doc_desc!=None).paginate(page=page, per_page=5, error_out=False)
    posts = queue2.items
    return render_template('admin/adoctreat.html', queue1=queue1,queue2=queue2, posts=posts)
#
# @admin.route('/pat_bdoctreat/', methods=['GET', 'POST'])
# @login_required
# def adoctreat():
#     name2 = request.cookies.get('name2', None)
#     if name2 !=None:
#         queue = Queue.query.filter(Queue.doctor_name == name2)
#         return render_template('admin/bdoctreat.html', queue=queue)
# if form.select.data == '用户':
#
#     resp = redirect(url_for('admin.pat_doctreat'))
#     resp.set_cookie('name1', form.name.data)
#     return resp
# else:
#     session['name2'] = form.username.data
#     return redirect(url_for('admin.doctreat'))



