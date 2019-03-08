# -*- coding:utf-8 -*-

import traceback
from datetime import datetime
from flask import flash
from apscheduler.triggers.cron import CronTrigger

from .. import scheduler, db
from ..tasks import script_task, email_task

# 装饰器， 判断任务是否存在
def judge_exist(func):
    def decorator(mission):
        if not scheduler.get_job(id=mission.comment, jobstore='default'):
            # db.session.delete(mission)
            flash(u'这个任务存在错误, 请删除重建')
            return
        else:
            return func(mission)
    return decorator

def add_mission(mission):
    job = {
        'id': mission.comment,
        'func': email_task if mission.type=='email_mission' else script_task,
        'args': (mission.comment, ),
        'trigger': CronTrigger.from_crontab(mission.crond),
    }
    if not mission.valid:
        job['next_run_time'] = None # 表示暂停
    scheduler.add_job(**job)
    return True

@judge_exist
def modify_mission(mission):
    job = scheduler.get_job(id=mission.comment, jobstore='default')
    job.reschedule(trigger=CronTrigger.from_crontab(mission.crond))
    if not mission.valid:
        # reschedule 居然不允许传递next_run_time 参数， 只能使用再去检索一遍任务并且暂停的方式
        scheduler.pause_job(id=mission.comment, jobstore='default')
    return True

@judge_exist
def resume_mission(mission):
    scheduler.resume_job(id=mission.comment, jobstore='default')
    return True

@judge_exist
def pause_mission(mission):
    scheduler.pause_job(id=mission.comment, jobstore='default')
    return True

def remove_mission(mission):
    if not scheduler.get_job(id=mission.comment, jobstore='default'):
        return
    scheduler.remove_job(id=mission.comment, jobstore='default')
    return True
