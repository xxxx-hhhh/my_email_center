# -*- coding:utf-8 -*-

import re
import time
import psutil

# 获取运行中的任务状态
def mission_status():
    mission_status = {}
    script_regex = re.compile(r'^/tmp/email_center/static/scripts/.+?\.py$')
    dir_regex = re.compile(r'^/tmp/email_center/static/script_mission_statements/(\d+?)$')
    for i in psutil.process_iter():
        cmdline = i.cmdline()
        if len(cmdline) == 3 and cmdline[0] == 'python' and script_regex.match(cmdline[1]):
            comment = dir_regex.match(cmdline[2]).group(1)
            mission_status[comment] = round(i.memory_percent(), 3)
    return mission_status

# 杀死任务进程
def kill_mission(comment):
    mission = '/tmp/email_center/static/script_mission_statements/%s' % comment
    for i in psutil.process_iter():
        cmdline = i.cmdline()
        if len(cmdline) == 3 and cmdline[2] == mission:
            i.kill()
            return True

# 内存占用
def memory_percent():
    process_mp = []
    for process in psutil.process_iter():
        # pid, cmd, memory_percent, run_time
        process_mp.append((
             str(process.pid),
             ' '.join(process.cmdline()),
             round(process.memory_percent(), 3),
             round((time.time() - process.create_time()) / 60., 3)
        ))
    process_mp = sorted(process_mp, key=lambda x:x[2], reverse=True)
    process_mp = map(lambda x:(x[0], x[1], str(x[2]), str(x[3])), process_mp)
    return process_mp