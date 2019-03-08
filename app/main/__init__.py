# -*- coding:utf-8 -*-

from flask import Blueprint

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    return 'who are u?'
