import datetime
oneday = datetime.timedelta(days=1)
# today = datetime.date.today()
tomorrow = datetime.date.today() + oneday
ttomorrow= datetime.date.today() + oneday+oneday
print(str(tomorrow)+'23654')

#设置cookie
# resp = redirect(url_for('doctor.dealqueue'))
# resp.set_cookie('name', form.name.data)
# return resp
#
# name = request.cookies.get('name', None)
#设置分页
# page = request.args.get('page', 1, type=int)
# queue = Queue.query.filter(Queue.doctor_id == current_user.id).order_by(Queue.id) .paginate(page=page, per_page=3, error_out=False)
#         posts = queue.items
#         return render_template('doctor/mypatient.html', queue = queue,  posts = posts,endpoint1='doctor.docdeal', endpoint2='doctor.dealqueue')

# {% from 'common/macro.html' import pagination_show%}
# < div
''''<div
style = "margin-left: 200px; margin-top: 500px; position: absolute" >
{{pagination_show(queue, 'doctor.mypatient')}} </div>
'''
# from datetime import datetime,date,time,timedelta
# # today = date.today()
# today = datetime.utcnow()
# print(today)