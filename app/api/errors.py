# -*- coding:utf-8 -*-

from . import api

import traceback
from flask import render_template


@api.app_errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404

@api.app_errorhandler(500)
def internal_server_error(e):
    return render_template('error/500.html', error_info=traceback.format_exc()), 500
