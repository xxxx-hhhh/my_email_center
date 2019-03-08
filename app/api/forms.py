# -*- coding:utf-8 -*-

from .. import scripts, db
from ..models import Mission, ScriptMission, EmailMission, User

import re
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, TextAreaField, BooleanField, SubmitField, SelectField
from wtforms import ValidationError
from wtforms.validators import DataRequired, Length, Email
from apscheduler.triggers.cron import CronTrigger

# 脚本任务表单
class ScriptMissionForm(FlaskForm):
    caption = StringField(u'邮件标题', validators=[DataRequired(), Length(0, 64)])
    name = StringField(u'任务名称(唯一)', validators=[DataRequired(), Length(0, 64)])
    recipient = StringField(u'收件人(多个收件人使用 "/" 隔开)',
                            validators=[DataRequired(), Length(0, 1024)])
    cc = StringField(u'抄送人(多个抄送人使用 "/" 隔开)', validators=[Length(0, 1024)])
    content = TextAreaField(u'邮件正文')
    crond = StringField(u'定时参数', validators=[DataRequired(), Length(0, 64)])
    user = SelectField(u'任务创建人', coerce=int)
    file = FileField(u'脚本文件', validators=[FileAllowed(scripts, u'只能上传python脚本'), FileRequired(u'请上传脚本文件')])
    valid = BooleanField(u'是否有效', default=False)
    submit = SubmitField(u'提交')

    def __init__(self, *args, **kwargs):
        super(ScriptMissionForm, self).__init__(*args, **kwargs)
        self.user.choices = [(user.id, '%s(%s)' % (user.name, user.email)) for user in User.query.all()]
        self.user.choices.insert(0, (0, u'无'))

    def validate_name(self, field):
        if Mission.query.filter(Mission.name == field.data).first():
            raise ValidationError(u'存在同名任务(任务名称必须唯一)')


    def validate_crond(self, field):
        # 正则有点复杂， 只能使用这个方式实现
        try:
            CronTrigger.from_crontab(field.data)
        except:
            raise ValidationError(u'请输入正确的定时参数(参考crontab的定时参数)')

    def validate_recipient(self, field):
        regex = re.compile(r'^[^@ ]+@([^.@][^@]+)$', re.IGNORECASE)
        emails = field.data.strip().split('/')
        for email in emails:
            if not regex.match(email):
                raise ValidationError(u'请确保输入的邮箱格式都是正确的')

    def validate_cc(self, field):
        regex = re.compile(r'^[^@ ]+@([^.@][^@]+)$', re.IGNORECASE)
        emails = field.data.strip().split('/') if field.data.strip() else []
        for email in emails:
            if not regex.match(email):
                raise ValidationError(u'请确保输入的邮箱格式都是正确的')


# 邮件任务表单
class EmailMissionForm(FlaskForm):
    caption = StringField(u'邮件标题', validators=[DataRequired(), Length(0, 64)])
    name = StringField(u'任务名称(唯一)', validators=[DataRequired(), Length(0, 64)])
    recipient = StringField(u'收件人(多个收件人使用 "/" 隔开)',
                            validators=[DataRequired(), Length(0, 1024)])
    cc = StringField(u'抄送人(多个抄送人使用 "/" 隔开)', validators=[Length(0, 1024)])
    content = TextAreaField(u'邮件正文')
    # file_dir = StringField(u'待发送文件路径', validators=[DataRequired(), Length(0, 128)])        # todo: 让用户选择文件路径不妥当， 改为在指定路径获取
    filename_prefix = StringField(u'待发送文件名前缀', validators=[DataRequired(), Length(0, 64)])
    crond = StringField(u'定时参数', validators=[DataRequired(), Length(0, 64)])
    user = SelectField(u'任务创建人', coerce=int)
    valid = BooleanField(u'是否有效', default=False)
    submit = SubmitField(u'提交')

    def __init__(self, *args, **kwargs):
        super(EmailMissionForm, self).__init__(*args, **kwargs)
        self.user.choices = [(user.id, '%s(%s)' % (user.name, user.email)) for user in User.query.all()]
        self.user.choices.insert(0, (0, u'无'))

    def validate_name(self, field):
        if Mission.query.filter(Mission.name == field.data).first():
            raise ValidationError(u'存在同名任务(任务名称必须唯一)')

    def validate_crond(self, field):
        # 正则有点复杂， 只能使用这个方式实现
        try:
            CronTrigger.from_crontab(field.data)
        except:
            raise ValidationError(u'请输入正确的定时参数(参考crontab的定时参数)')

    def validate_recipient(self, field):
        regex = re.compile(r'^[^@ ]+@([^.@][^@]+)$', re.IGNORECASE)
        emails = field.data.strip().split('/')
        for email in emails:
            if not regex.match(email):
                raise ValidationError(u'请确保输入的邮箱格式都是正确的')

    def validate_cc(self, field):
        regex = re.compile(r'^[^@ ]+@([^.@][^@]+)$', re.IGNORECASE)
        emails = field.data.strip().split('/') if field.data.strip() else []
        for email in emails:
            if not regex.match(email):
                raise ValidationError(u'请确保输入的邮箱格式都是正确的')

    # def validate_file_dir(self, field):
    #     if not os.path.isdir(field.data):
    #         raise ValidationError(u'请确保是存在的路径')

    def validate_filename_prefix(self, field):
        prefix = db.session.query(EmailMission.filename_prefix).all()
        prefix = [each[0] for each in prefix]
        repeat = filter(lambda x: (x in field.data) or (field.data in x), prefix)
        if repeat:
            raise ValidationError(u'存在有包含关系的文件名前缀')


# 修改任务信息
class ModifyMissionForm(FlaskForm):
    # comment = StringField(u'任务标识', validators=[Length(0, 64)])
    crond = StringField(u'定时参数', validators=[DataRequired(), Length(0, 64)])
    recipient = StringField(u'收件人(多个收件人使用 "/" 隔开)',
                            validators=[DataRequired(), Length(0, 1024)])
    cc = StringField(u'抄送人(多个抄送人使用 "/" 隔开)', validators=[Length(0, 1024)])
    caption = StringField(u'邮件标题', validators=[DataRequired(), Length(0, 64)])
    content = TextAreaField(u'邮件正文')
    user = SelectField(u'任务创建人', coerce=int)
    submit = SubmitField(u'提交')

    def __init__(self, *args, **kwargs):
        super(ModifyMissionForm, self).__init__(*args, **kwargs)
        self.user.choices = [(user.id, '%s(%s)' % (user.name, user.email)) for user in User.query.all()]
        self.user.choices.insert(0, (0, u'无'))

    def validate_crond(self, field):
        # 正则有点复杂， 只能使用这个方式实现
        try:
            CronTrigger.from_crontab(field.data)
        except:
            raise ValidationError(u'请输入正确的定时参数(参考crontab的定时参数)')

    def validate_recipient(self, field):
        regex = re.compile(r'^[^@ ].+@([^.@][^@]+)$', re.IGNORECASE)
        emails = field.data.strip().split('/')
        for email in emails:
            if not regex.match(email):
                raise ValidationError(u'请确保输入的邮箱格式都是正确的')

    def validate_cc(self, field):
        regex = re.compile(r'^[^@ ]+@([^.@][^@]+)$', re.IGNORECASE)
        emails = field.data.strip().split('/') if field.data.strip() else []
        for email in emails:
            if not regex.match(email):
                raise ValidationError(u'请确保输入的邮箱格式都是正确的')

# 创建用户
class UserForm(FlaskForm):
    name = StringField(u'姓名', validators=[DataRequired()])
    email = StringField(u'邮箱', validators=[DataRequired(), Email()])
    submit = SubmitField(u'添加用户')

    def validate_name(self, field):
        if User.query.filter(User.name==field.data).first():
            raise ValidationError(u'存在同名用户, 请确保用户名唯一')

    def validate_email(self, field):
        if User.query.filter(User.email==field.data).first():
            raise ValidationError(u'存在相同的邮箱,请确保邮箱唯一')


