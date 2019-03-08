# -*- coding:utf-8 -*-

from .. import mail, glogger
from .render_util import render_html, custom_render

import os
import time
import random
from retry import retry
from datetime import datetime
from flask_mail import Message
from smtplib import SMTPConnectError, SMTPAuthenticationError


# 发送邮件的时候记录一下日志
def log(func):
    def decorator(*args, **kwargs):
        tid = time.time()
        glogger.debug('prepare to send a email(tid={tid}) with arguments \n'
                     'function : {func_name} \n'
                     'args : {args} \n'
                     'kwargs : {kwargs}'.format(tid=tid, func_name=func.__name__, args=args, kwargs=kwargs))
        try:
            result = func(*args, **kwargs)
        except:
            glogger.debug('fail to send the email(tid={tid})'.format(tid=tid))
            raise
        else:
            glogger.debug('successful to send the email(tid={tid})'.format(tid=tid))
            return result
    return decorator

# 发送邮件
# 添加判断：如果邮件正文以 <%render_html%> 开头， 则将生成的文件渲染为html并且添加到邮件正文
# 添加判断：如果邮件正文以 <%no_email%> 开头， 则只跑脚本不发送邮件， 但是任务报错时仍然应该通知创建人
@log
@retry(exceptions=(SMTPAuthenticationError, SMTPConnectError), tries=3, delay=random.randint(3, 6), logger=glogger)
def send_email(app, mission, subject, content, recipients, cc, filename='test.xlsx'):
    if not recipients:
        return

    subject = subject + '    %s' % datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    msg = Message(subject, recipients=recipients, cc=cc)
    # msg.body = content
    if content.strip().startswith('<%render_html%>'):
        try:
            msg.html = render_html(filename)
        except Exception as e:
            mission.log('Render HTML Error: ' + e.message, if_send_email=True)
            raise e
    elif content.strip().startswith('<%custom_render%>'):
        try:
            msg.html = custom_render(filename, content.strip().lstrip('<%custom_render%>'))
        except Exception as e:
            mission.log('Render HTML Error: ' + e.message, if_send_email=True)
            raise e
    else:
        msg.html = content
        with open(filename, 'rb') as f:
            msg.attach(os.path.basename(filename), 'application/vnd.ms-excel', f.read())

    with app.app_context():
        mail.send(msg)

# 通知用户任务出错
@log
def notice_user(app, mission, message, timing):
    if not mission.user:
        return
    subject = u'[Email-Center] 错误发生通知'
    content = (
        u'<h3>任务编号: {comment} 发生错误</h3>\n'
        u'<h3>任务名称: {name}</h3>'
        u'<h3>{timing}</h3>'
        u'<h3>{message}</h3>'
    ).format(
           comment = mission.comment,
           name = mission.name,
           timing = timing.strftime('%Y-%m-%d %H:%M:%S'),
           message = message)
    recipient = [mission.user.email]
    msg = Message(subject, recipients=recipient)
    msg.html = content
    with app.app_context():
        mail.send(msg)

