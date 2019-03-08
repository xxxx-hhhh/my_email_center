# -*- coding:utf-8 -*-

from . import db
from .utils.email import notice_user

import time
from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, Text, String, Boolean, ForeignKey


# 任务基类
class Mission(db.Model):
    __tablename__ = 'missions'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, doc=u"ID")
    name = Column(String(64), nullable=False, unique=True, index=True, doc=u'任务名称(用户只能通过这个字段识别任务)')
    caption = Column(String(64), nullable=False, doc=u'邮件标题')
    recipient = Column(String(1024), nullable=False, doc=u'收件人')
    cc = Column(String(1024), doc=u'抄送人')
    content = Column(Text, doc=u'邮件正文')
    crond = Column(String(64), nullable=False, doc=u'定时参数')
    valid = Column(Boolean, default=True, doc=u'是否有效')
    create_time = Column(DateTime, default=datetime.now, index=True, doc=u'创建时间')
    comment = Column(String(64), unique=True, index=True, nullable=False, doc=u'任务标识(由系统生成)')
    update_time = Column(DateTime, doc=u'上次执行的时间')

    user_id = Column(Integer, ForeignKey('users.id'))
    logs = db.relationship('MissionLog', backref='mission', lazy='dynamic')
    type = Column(String(64))

    __mapper_args__ = {
        'polymorphic_identity': 'mission',
        'polymorphic_on': type
    }

    def __init__(self, *args, **kwargs):
        super(Mission, self).__init__(*args, **kwargs)
        self.comment = str(long(time.time() * 1000))

    def update(self):
        self.update_time = datetime.now()
        db.session.add(self)
        db.session.commit()

    def log(self, info, start_time=None, if_send_email=False):
        log = MissionLog(start_time=start_time, end_time=datetime.now(), content=info.decode('utf-8'))
        self.logs.append(log)
        db.session.add_all([self, log])
        db.session.commit()

        # 发生错误时应该发邮件提醒创建者
        if if_send_email:
            app = db.app
            with app.app_context():
                notice_user(db.app, self, info.decode('utf-8'), log.end_time)



# todo: 函数文件必须满足接收参数output_dir  # 输出的文件路径
class ScriptMission(Mission):
    __tablename__ = 'script_missions'

    id = Column(Integer, ForeignKey('missions.id'), primary_key=True, doc=u'ID')
    filename = Column(String(64), nullable=False, unique=True, doc=u'脚本文件名')

    __mapper_args__ = {
        'polymorphic_identity': 'script_mission'
    }


# todo: 待获取的文件必须存储在EMAIL_MISSION_DIRECTION 指定的文件夹中
class EmailMission(Mission):
    __tablename__ = 'email_missions'

    id = Column(Integer, ForeignKey('missions.id'), primary_key=True, doc=u'ID')
    # file_dir = Column(String(128), nullable=False, doc=u'待发送的文件路径')
    filename_prefix = Column(String(64), nullable=False, unique=True, index=True, doc=u'待发送的文件名前缀')

    __mapper_args__ = {
        'polymorphic_identity': 'email_mission'
    }


# 脚本执行日志
class MissionLog(db.Model):
    __tablename__ = 'mission_logs'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, doc=u"ID")
    start_time = Column(DateTime, doc=u'脚本开始执行时间')    # 邮件型任务由于仅有获取文件并执行的过程， 所以默认为空
    end_time = Column(DateTime, nullable=False, default=datetime.now, doc=u'脚本结束时间')
    content = Column(Text, doc=u'日志内容')

    mission_id = Column(Integer, ForeignKey('missions.id'))


##################################

# 用户类
class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True, doc=u"ID")
    name = Column(String(64), unique=True, nullable=False, doc=u'用户名')
    email = Column(String(64), unique=True, nullable=False, doc=u'邮箱地址')
    create_time = Column(DateTime, default=datetime.now, doc=u'创建时间')
    missions = db.relationship('Mission', backref='user', lazy='dynamic')

    @classmethod
    def object_from(cls, name, email):
        new_user = cls(name=name, email=email)
        db.session.add(new_user)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise e

