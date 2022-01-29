# -*- coding:utf-8 -*-
from flask import Blueprint, session

post_router = Blueprint('post', __name__)


@post_router.route("/")
def auth():
    token = session['Token']
    return token, 200
