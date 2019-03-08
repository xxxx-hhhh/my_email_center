# -*- coding:utf-8 -*-

import os
import time
import shutil

from flask import current_app

def create_statement_dir(mission):
    dir_name = os.path.join(current_app.config['SCRIPT_MISSION_DIRECTION'], mission.comment)
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)
    return True


# 查找目录下最新的文件
def new_file(dir, mission):
    lists = os.listdir(dir)
    if lists:
        if mission.type == 'email_mission':
            lists = filter(lambda fn:fn.startswith(mission.filename_prefix), lists)  # email_mission 所有的报表都在同一个文件夹下, 需要根据前缀先筛选
        if lists:
            lists.sort(key=lambda fn: os.path.getmtime(os.path.join(dir, fn)))
            file_new = os.path.join(dir, lists[-1])
            if not mission.update_time or os.path.getmtime(file_new) > time.mktime(mission.update_time.timetuple()):
                return file_new

def remove_file(mission):
    if mission.type == 'email_mission':
        files = filter(lambda x:x.startswith(mission.filename_prefix), os.listdir(current_app.config['EMAIL_MISSION_DIRECTION']))
        [os.remove(os.path.join(current_app.config['EMAIL_MISSION_DIRECTION'], file)) for file in files]
    elif mission.type == 'script_mission':
        dir_name = os.path.join(current_app.config['SCRIPT_MISSION_DIRECTION'], mission.comment)
        script = os.path.join(current_app.config['UPLOADED_SCRIPTS_DEST'], mission.filename)
        if os.path.isdir(dir_name):
            shutil.rmtree(dir_name)
        [os.remove(script) if os.path.isfile(script) else None]
    return True


