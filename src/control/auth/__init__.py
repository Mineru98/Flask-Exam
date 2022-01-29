# -*- coding:utf-8 -*-
from flask import Blueprint, Response, session, redirect, request, render_template
auth_router = Blueprint('auth', __name__)


@auth_router.route("/login", methods=['GET'])
def loginRenderingHtml():
    return render_template("login.html", document_title="Login - Container Manager")


@auth_router.route("/login", methods=['POST'])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    session['Token'] = username + ":" + password
    return redirect("/post")


@auth_router.route("/logout", methods=['POST'])
def logout():
    if session.get('Token'):
        res = Response('OK Logout')
        del session['Token']
        return res, 200
    elif request.method == "POST":
        res = Response('No Logout')
        return res, 402
