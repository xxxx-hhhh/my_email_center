# -*- coding:utf-8 -*-

import six
import json
import psutil
import traceback
from threading import Thread
from flask import request, render_template, redirect, url_for, flash, abort

from . import api
from .. import db, scripts, glogger
from ..tasks import script_task, email_task
from ..utils import file_util, scheduler_util, process_util
from .forms import ScriptMissionForm, EmailMissionForm, ModifyMissionForm, UserForm
from ..models import Mission, ScriptMission, EmailMission, MissionLog, User



# 主页
@api.route('/', methods=['GET'])
def index():
    type = request.args.get('type', 'script_mission')
    mission_cls = {
        'script_mission': ScriptMission,
        'email_mission': EmailMission
    }.get(type, ScriptMission)
    page = request.args.get('page', 1, type=int)
    pagination = mission_cls.query.order_by(mission_cls.create_time.desc()).paginate(
        page=page,
        per_page=15,
        error_out=False
    )
    missions = pagination.items
    mission_comments = {'comments': [str(m.comment) for m in missions]}   # 当前页的任务编码
    return render_template('index.html', missions=missions, type=type, pagination=pagination, page=page, mission_comments=mission_comments)


# 创建任务
@api.route('/create_mission', methods=['POST', 'GET'])
def create_mission():
    type = request.args.get('type', 'script_mission')
    page = request.args.get('page', 1)
    form = {
        'script_mission': ScriptMissionForm,
        'email_mission': EmailMissionForm
    }.get(type, ScriptMissionForm)()
    if form.validate_on_submit():
        mission_cls = {
            'script_mission': ScriptMission,
            'email_mission': EmailMission
        }.get(type, ScriptMission)
        mission = mission_cls(caption=form.caption.data,
                          name=form.name.data,
                          recipient=json.dumps(list(set(form.recipient.data.strip().split('/')))),
                          cc=json.dumps(list(set(form.cc.data.strip().split('/')))) if form.cc.data.strip() else json.dumps([]),
                          content=form.content.data,
                          crond=form.crond.data,
                          valid=form.valid.data,
                          user_id=form.user.data if form.user.data else None)
        if type == 'email_mission':
            mission.filename_prefix = form.filename_prefix.data
        else:
            mission.filename = scripts.save(form.file.data)
            file_util.create_statement_dir(mission)  # 创建存放报表的文件夹
        try:
            with db.session.begin_nested():
                scheduler_util.add_mission(mission)
                db.session.add(mission)
        except:
            glogger.error(traceback.format_exc())
            file_util.remove_file(mission)
            flash(u'任务创建过程发生错误')
            return redirect(url_for('api.index', type=type, page=page))
        flash(u'任务创建成功')
        return redirect(url_for('api.index', type=type, page=page))
    return render_template('create_mission.html', form=form, type=type)


# 修改任务
@api.route('/modify_mission', methods=['GET', 'POST'])
def modify_mission():
    form = ModifyMissionForm()
    comment = request.args.get('comment', '')
    page = request.args.get('page', 1)
    if request.method == 'GET' and not comment:
        abort(404)

    mission = Mission.query.filter(Mission.comment == comment).first()
    if not mission:
        abort(404)
    if form.validate_on_submit():
        try:
            with db.session.begin_nested():
                mission.crond = form.crond.data
                mission.recipient = json.dumps(list(set(form.recipient.data.strip().split('/'))))
                mission.cc = json.dumps(list(set(form.cc.data.strip().split('/')))) if form.cc.data.strip() else json.dumps([]),
                mission.caption = form.caption.data
                mission.content = form.content.data
                mission.user_id = form.user.data if form.user.data else None
                db.session.add(mission)
                if scheduler_util.modify_mission(mission):flash(u'任务修改成功')
        except:
            glogger.error(traceback.format_exc())
            flash(u'任务修改过程发生错误')
        return redirect(url_for('api.index', type=mission.type, page=page))

    form.crond.data = mission.crond
    form.recipient.data = '/'.join(json.loads(mission.recipient))
    form.cc.data = '/'.join(json.loads(mission.cc))
    form.caption.data = mission.caption
    form.content.data = mission.content
    form.user.data = mission.user_id if mission.user_id else 0
    return render_template('modify_mission.html', mission=mission, form=form)


# 恢复任务
@api.route('/resume_mission', methods=['GET'])
def resume_mission():
    comment = request.args.get('comment', '')
    page = request.args.get('page', 1)
    mission = Mission.query.filter(Mission.comment == comment).first()
    mission.valid = True
    if scheduler_util.resume_mission(mission):flash(u'任务已恢复')
    db.session.add(mission)
    db.session.commit()
    return redirect(url_for('api.index', type=mission.type, page=page))


# 暂停任务
@api.route('/pause_mission', methods=['GET'])
def pause_mission():
    comment = request.args.get('comment', '')
    page = request.args.get('page', 1)
    mission = Mission.query.filter(Mission.comment == comment).first()
    mission.valid = False
    if scheduler_util.pause_mission(mission):flash(u'任务已暂停')
    db.session.add(mission)
    db.session.commit()
    return redirect(url_for('api.index', type=mission.type, page=page))


# 删除任务
@api.route('/remove_mission', methods=['GET'])
def remove_mission():
    comment = request.args.get('comment', '')
    page = request.args.get('page', 1)
    mission = Mission.query.filter(Mission.comment==comment).first()
    if not mission:
        abort(404)
    scheduler_util.remove_mission(mission)
    file_util.remove_file(mission)
    mission.logs.delete()
    db.session.delete(mission)
    db.session.commit()
    flash(u'任务已删除')
    return redirect(url_for('api.index', type=mission.type, page=page))


# 任务日志
@api.route('/mission_logs', methods=['GET'])
def mission_logs():
    comment = request.args.get('comment', '')
    mission = Mission.query.filter(Mission.comment==comment).first()
    if not mission:
        abort(404)
    page = request.args.get('page', 1, type=int)
    pagination = mission.logs.order_by(MissionLog.end_time.desc()).paginate(
        page=page,
        per_page=10,
        error_out=False
    )
    logs = pagination.items
    return render_template('logs.html', logs=logs, comment=comment, type=mission.type, pagination=pagination, page=page)


# 执行任务(用于补发或者测试)
@api.route('/execute_mission', methods=['GET'])
def execute_mission():
    comment = request.args.get('comment', '')
    page = request.args.get('page', 1)
    mission = Mission.query.filter(Mission.comment==comment).first()
    thr = Thread(target=email_task if mission.type=='email_mission' else script_task, args=[comment, ])
    thr.start()
    flash(u'任务已执行')
    return redirect(url_for('api.index', type=mission.type, page=page))


# 获取任务运行状态
@api.route('/mission_status', methods=['GET', 'POST'])
def misssion_status():
    mission_status = process_util.mission_status()
    if request.method == 'POST':
        comments = request.json.get('comments', [])
        def f(i):
            del mission_status[i]
        [f(each) for each in mission_status if each not in comments]
    return json.dumps(mission_status)


# 获取系统状态（系统内存占用情况，运行中的任务进程）
@api.route('/system_status', methods=['GET', 'POST'])
def system_status():
    if request.method == 'POST':
        vm = psutil.virtual_memory()
        system_status ={
            'available': round(vm.available / 1024. / 1024., 3),    # 剩余内存大小
            'used': round(vm.active / 1024. / 1024., 3),    # 已使用内存大小
            'memory_percent': '%.3f%%' % vm.percent,           # 内存使用百分比
        }
        mission_status = sorted(process_util.mission_status().items(), key=lambda x:x[1], reverse=True)
        mission_status = map(lambda x:(x[0], str(x[1])), mission_status)
        process_memory_percent = process_util.memory_percent()
        data = json.dumps({
            'system_status': system_status,
            'mission_status': mission_status,
            'top5_memory_percent': process_memory_percent[:5],
        })
        return data
    else:
        return render_template('system_status.html')

# 杀死任务进程
@api.route('/kill_mission', methods=['GET'])
def kill_mission():
    comment = request.args.get('comment', None)
    if comment:
        if process_util.kill_mission(comment):
            flash(u'已经杀死编号为%s的任务进程' % comment)
        else:
            flash(u'未找到相应的进程')
    return redirect(url_for('api.system_status'))


# 用户管理页面
@api.route('/user_admin', methods=['GET', 'POST'])
def user_admin():
    users = User.query.all()
    form = UserForm()
    if form.validate_on_submit():
        name = form.name.data
        email = form.email.data
        User.object_from(name, email)
        flash(u'Add user successful!')
        return redirect(url_for('api.user_admin'))
    for field, errors in six.iteritems(form.errors):
        for error in errors:
            flash(field + ' : ' + error, category='error')
    return render_template('user_admin.html', users=users, form=form)


# 删除用户
@api.route('/user_delete', methods=['GET'])
def user_delete():
    email = request.args.get('email')
    if email:
        try:
            u = User.query.filter(User.email==email).first()
            if u:
                db.session.delete(u)
                db.session.commit()
                flash(u'成功删除用户')
            else:
                flash(u'不存在的用户')
        except:
            glogger.error(traceback.format_exc())
            db.session.rollback()
            flash(u'删除用户过程出错', 'error')
    else:
        flash(u'传参有误')
    return redirect(url_for('api.user_admin'))









