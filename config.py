# -*- coding:utf-8 -*-

import os
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor

class Config:
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_POOL_TIMEOUT = 30
    SQLALCHEMY_POOL_RECYCLE = 300

    SECRET_KEY = 'secret key'
    WTF_CSRF_ENABLED = True

    MAIL_DEBUG = False
    MAIL_SERVER = ''
    MAIL_PORT = 465
    MAIL_DEFAULT_SENDER = ""
    MAIL_USERNAME = ""
    MAIL_PASSWORD = ""
    MAIL_USE_SSL = True

    SCHEDULER_API_ENABLED = False # APS的api开关
    SCHEDULER_JOB_DEFAULTS = {
        'misfire_grace_time': 60,
        'coalesce': True,
    }
    SCHEDULER_EXECUTORS = {
        'default': ThreadPoolExecutor(30),
    }

    @classmethod
    def init_app(cls, app):
        if not os.path.isdir(app.config['UPLOADED_SCRIPTS_DEST']):
            os.makedirs(app.config['UPLOADED_SCRIPTS_DEST'])
        if not os.path.isdir(app.config['SCRIPT_MISSION_DIRECTION']):
            os.makedirs(app.config['SCRIPT_MISSION_DIRECTION'])
        if not os.path.isdir(app.config['EMAIL_MISSION_DIRECTION']):
            os.makedirs(app.config['EMAIL_MISSION_DIRECTION'])




class DevelopmentConfig(Config):
    RETRY_TIMES = 3
    RETRY_INTERVAL = 10
    REDIS_URL = 'redis://127.0.0.1:6379/0'

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123@localhost:3306/email_center?charset=utf8'
    SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url='mysql+pymysql://root:123@localhost:3306/email_center?charset=utf8',
					engine_options={'pool_recycle': 300, 'pool_timeout': 30, 'convert_unicode': True, 'pool_size': 10})
    }
   
    BASEDIR = '/tmp'
    UPLOADED_SCRIPTS_DEST = os.path.join(BASEDIR, 'email_center', 'static', 'scripts')  # 脚本存放位置
    SCRIPT_MISSION_DIRECTION = os.path.join(BASEDIR, 'email_center', 'static', 'script_mission_statements')  # 报表存放位置， 每一个任务生成的报表应该单独存放在一个文件夹
    EMAIL_MISSION_DIRECTION = os.path.join(BASEDIR, 'email_center', 'static', 'email_mission_statements')  # 邮件任务报表存放位置  

    DEBUG = True


class ProductionConfig(Config):
    RETRY_TIMES = 4
    RETRY_INTERVAL = 300
    REDIS_URL = 'redis://172.16.2.211:6379/0'
    
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123@localhost:3306/email_center?charset=utf8'
    SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url='mysql+pymysql://root:123@localhost:3306/email_center?charset=utf8',
					engine_options={'pool_recycle': 300, 'pool_timeout': 30, 'convert_unicode': True, 'pool_size': 10})
    }

    BASEDIR = '/tmp'
    UPLOADED_SCRIPTS_DEST = os.path.join(BASEDIR, 'email_center', 'static', 'scripts')  # 脚本存放位置
    SCRIPT_MISSION_DIRECTION = os.path.join(BASEDIR, 'email_center', 'static', 'script_mission_statements')  # 报表存放位置， 每一个任务生成的报表应该单独存放在一个文件夹
    EMAIL_MISSION_DIRECTION = os.path.join(BASEDIR, 'email_center', 'static', 'email_mission_statements')  # 邮件任务报表存放位置

    DEBUG = False



config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}
