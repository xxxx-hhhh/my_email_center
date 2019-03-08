# -*- coding:utf-8 -*-

import os
import pandas as pd
from jinja2.filters import do_mark_safe
from flask import render_template, render_template_string

# 渲染文件内容到邮件正文
def render_html(filename):
    title = os.path.basename(filename).split('.')[0]
    if filename.endswith('.csv'):
        data = {title: pd.read_csv(filename, encoding='utf-8')}
    else:
        data = pd.read_excel(filename, sheet_name=None)
    html = ''
    for k, v in data.iteritems():
        html = html + \
               '<div class="table_caption">' + k + '</div><br>' + \
               '<div>' + v.to_html(escape=True, index=False) + '</div><br>'
    html = render_template('email/render_html.html', title=title, content=html)
    return html


# 用户自定义渲染的模板
# title : 生成的文件名; tables : 元组列表, (sheetname,table);
def custom_render(filename, custom_template):
    custom_template = '{% extends "email/custom_render.html" %}' + custom_template
    title = os.path.basename(filename).split('.')[0]
    if filename.endswith('.csv'):
        tables = [(title, pd.read_csv(filename, encoding='utf-8').to_html(escape=True, index=False))]
    else:
        tables = [(sn, do_mark_safe(df.to_html(escape=True, index=False))) for sn, df in pd.read_excel(filename, sheet_name=None).iteritems()]
    html = render_template_string(custom_template, filename=title, tables=tables)
    return html