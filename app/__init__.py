# -*— coding:utf-8 -*-

import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_uploads import UploadSet, configure_uploads
from flask_apscheduler import APScheduler
from flask_redis import FlaskRedis


from config import config

db = SQLAlchemy()
mail = Mail()
bootstrap = Bootstrap()
scripts = UploadSet('scripts', ('py',))
scheduler = APScheduler()
redis = FlaskRedis()

# 必须使用gunicorn的内置logger，否则自定义的一些输出会没法flush
glogger = logging.getLogger("gunicorn.error")

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    db.app = app   # amazing trick
    logging.basicConfig()

    db.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    scheduler.init_app(app)
    redis.init_app(app)

    configure_uploads(app, scripts)  # 初始化uploads
    scheduler.start()                # 启动定时器


    # 注册blueprint
    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    return app
