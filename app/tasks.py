# -*- coding:utf-8 -*-

import os
import json
import time
import random
import traceback
import subprocess
from functools import wraps
from retry import retry
from datetime import datetime

from .utils.email import send_email
from .utils.file_util import new_file
from .models import ScriptMission, EmailMission
from . import db, redis, glogger




# 定义需要重试的Exception
class NoFileException(Exception):
    pass

# 定义捕获最大重试次数失败的装饰器
def max_retries_catch(func):
    @wraps(func)
    def decorater(comment):
        try:
            return func(comment)
        except NoFileException:
            mission = EmailMission.query.filter(EmailMission.comment == comment).first()
            mission.log(u"Can't find new file which prefix is %s, have try %d times!" \
                        % (mission.filename_prefix, db.app.config['RETRY_TIMES']), if_send_email=True)
    return decorater

# 任务锁装饰器， 防止重复执行同一任务
def task_lock(func):
    @wraps(func)
    def decorater(comment):
        locking = False   # 只有上锁的进程有资格去解锁， 使用这个变量作为标记
        try:
            if (redis.get('task_%s' % comment) or '0') == '0':
                redis.set('task_%s' % comment, '1', ex=3600)  # 上锁， 这个锁默认只会存在3600秒
                locking = True
                glogger.info('task_%s get lock' % comment)
                return func(comment)
            else:
                glogger.info('task_%s locking' % comment)
        except:
            glogger.error(traceback.format_exc())
        finally:
            if locking:
                redis.set('task_%s' % comment, '0')
                glogger.info('task_%s release lock' % comment)
    return decorater

# 毫秒级随机延时避让装饰器（由于这个避让本身也可能导致任务重复执行，必须确保值较小）
def random_delay(min=150., max=300.):
    '''
    :param min: float, 随机避让最小时长，单位：毫秒 
    :param max: float, 随机避让最大时长，单位：毫秒
    '''
    def decorater_1(func):
        @wraps(func)
        def decorater_2(*args, **kwargs):
            time.sleep(random.uniform(min/1000., max/1000.))
            return func(*args, **kwargs)
        return decorater_2
    return decorater_1



# 执行脚本并且发送邮件
@random_delay(min=0., max=3000.)
@task_lock
def script_task(comment):
    app = db.app
    with app.app_context():
        start_time = datetime.now()
        mission = ScriptMission.query.filter(ScriptMission.comment==comment).first()
        if not mission:
            return
        filename = os.path.join(app.config['UPLOADED_SCRIPTS_DEST'], mission.filename)
        statement_direction = os.path.join(app.config['SCRIPT_MISSION_DIRECTION'], mission.comment)
        popen_instance = subprocess.Popen('python %s %s' % (filename, statement_direction),
                                          shell=True,
                                          stderr=subprocess.PIPE,
                                          stdout=subprocess.PIPE)
        out, err = popen_instance.communicate()
        retcode = popen_instance.poll()
        if not retcode:
            # 仅执行脚本不发送邮件
            if mission.content.strip().startswith('<%no_email%>'):
                mission.update()  # 顺利完成后
                mission.log(u'Successful(without send email)!', start_time)
                return

            # 执行脚本且发送邮件
            file = new_file(statement_direction, mission)
            if not file:
                mission.log(u"can't find new statement", start_time, if_send_email=True)
                return
            if redis.get('task_%s' % comment) == '1':  # 如果任务还是不慎多次执行只能在发送邮件时尽量减少重复发送的可能
                send_email(app, mission, mission.caption, mission.content, json.loads(mission.recipient), json.loads(mission.cc), file)
                mission.update()  # 顺利完成后
                mission.log(u'Successful!', start_time)
            else:
                mission.log(u'It seems the mission has executed ever!', start_time)
                return
        elif retcode > 0:
            # error
            mission.log(err, start_time, if_send_email=True)
        elif retcode < 0:
            # killed
            mission.log(u'mission was killed by other process(kill signal %s)' % -retcode, start_time, if_send_email=True)

# 从特定路径获取
@random_delay(min=0., max=3000.)
@task_lock
@max_retries_catch
@retry(NoFileException, tries=db.app.config['RETRY_TIMES'], delay=db.app.config['RETRY_INTERVAL'])
def email_task(comment):
    app = db.app
    with app.app_context():
        mission = EmailMission.query.filter(EmailMission.comment == comment).first()
        if not mission:
            return
        file = new_file(app.config['EMAIL_MISSION_DIRECTION'], mission)
        if not file:
            raise NoFileException("Can't find new file which prefix is '%s'" % mission.filename_prefix)
        if redis.get('task_%s' % comment) == '1':  # 如果任务还是不慎多次执行只能在发送邮件时尽量减少重复发送的可能
            send_email(app, mission, mission.caption, mission.content, json.loads(mission.recipient), json.loads(mission.cc), file)
            mission.update()
            mission.log(u'Successful!')
        else:
            mission.log(u'It seems the mission has executed ever!')
            return






