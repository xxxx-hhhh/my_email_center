# -*- coding:utf-8 -*-

from app import create_app, db
from app.models import Mission, ScriptMission, EmailMission, MissionLog, User

import os
from flask_script import Shell, Manager
from flask_migrate import Migrate, MigrateCommand


app = create_app(os.environ.get('EMAIL_CENTER_CONFIG_TYPE') or 'development')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db,
                Mission=Mission, ScriptMission=ScriptMission,
                EmailMission=EmailMission, MissionLog=MissionLog,
                User=User)
manager.add_command('shell', Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()

# if __name__ != '__main__':
#     error_log = os.path.join(app.config['BASEDIR'], 'static', 'gunicorn_logging', 'error.log')
#     handler = TimedRotatingFileHandler(error_log, when='D', interval=1, backupCount=30)
#     gunicorn_logger = logging.getLogger('gunicorn.error')
#     gunicorn_logger.handlers = [handler]




# 在使用gunicorn作为http服务器后, gunicorn 跟 flask本身的loger其实已经不共通了.
# 这里实现的功能是将gunicorn.error的handler附加到flask的logger上去, 之后flask记录的log也会被同步到gunicorn.error日志中
# 这个功能在我们这个实现里并没有必要 --||
# if __name__ != '__main__':
#     gunicorn_logger = logging.getLogger('gunicorn.error')
#     app.logger.handlers.extend(gunicorn_logger.handlers)
#     app.logger.setLevel(gunicorn_logger.level)
