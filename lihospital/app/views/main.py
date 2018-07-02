from flask import Blueprint, render_template,session
from flask_login import current_user
from app.models import Queue, User, Doctor
from datetime import datetime,date,time,timedelta

# main = Blueprint('main', __name__)


# @main.route('/')
# def index():
#     t = datetime.utcnow()
#     if not current_user:
#     return render_template('main/index.html')
#     else:
#         queue = Queue.query.filter(Queue.user_id == current_user.id)
#         t =datetime.utcnow()
#         return render_template('main/index.html', queue=queue, t=t)
# from flask import Blueprint, render_template


main = Blueprint('main', __name__)


@main.route('/')
def index():
    t = datetime.utcnow()
    session.pop('username', None)
    return render_template('main/index.html', t=t)
@main.route('/help/')
def help():
    return render_template('common/help.html')