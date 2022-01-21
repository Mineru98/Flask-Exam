# -*- coding:utf-8 -*-
from flask import Flask
from src.control import auth, post, util

app = Flask(__name__)
app.debug = True
app.secret_key = "12fuew09jfs"


# Application Context 내용이 다 끝나고 나서 처리
@app.teardown_appcontext
def teardown_appcontext(error):
    print("Finish")


app.register_blueprint(auth.auth_router, url_prefix="/auth")
app.register_blueprint(post.post_router, url_prefix="/post")
app.register_blueprint(util.util_router, url_prefix="/util")
