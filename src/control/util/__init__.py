# -*- coding:utf-8 -*-
import os
from datetime import datetime, date
from werkzeug.utils import secure_filename
from flask import Flask, g, request, url_for, Response, make_response, Blueprint

util_router = Blueprint('util', __name__)


def dated_url_for(endpoint, **values):
    """
    static 폴더에 업로드 해둔 파일들을 수정했을 때 캐싱 된 내용 때문에
    변경된 사항이 제대로 적용이 안되는 경우가 있다.
    그런 경우에 해당 파일의 수정일을 가져와서 수정일이 바뀌면 url 주소에
    쿼리 값을 추가하여 버저닝이 되는 형식으로 사용하면
    static 파일들이 수정되더라도 바로 적용해서 사용이 가능함.
    """
    if endpoint == 'static':
        filename = values.get('filename', None)
        print(filename)
        if filename:
            file_path = os.path.join(util_router.root_path, endpoint, filename)
            values['v'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


# preprocessor :  컨택스트가 구동 될 때 시작해 됨
@util_router.app_context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


# 해당 경로에 최초 요청에 대해서 선처리
@util_router.before_app_first_request
def before_first_request():
    pass


# 해당 경로에 대한 요청 처리
@util_router.route("/")
def index():
    return "Hello, World!", 200


# 해당 경로에 대한 요청 처리 이후에 대한 처리
# 디비 커넥션을 종료하는 경우 사용
@util_router.after_app_request
def after_app_request(return_val):
    return return_val


# 요청이 다 끝나고 나서 처리
@util_router.teardown_app_request
def teardown_app_request(error):
    print("Close")


# 해당 경로에 요청 처리 전에 처리
# Web Filter 처리가 필요한 경우
# 디비 커넥션을 실행하는 경우 사용
@util_router.before_app_request
def before_app_request():
    pass


@util_router.before_request
def before_request_chapter1():
    """
    g(Application Context)는 전역 변수 개념이다.
    하나의 요청 처리 단위에서 공유 되는 변수로 쓰임.
    예를 들면 before_request 어노테이션에서 특정 url에서는 요청 헤더에 Authencation 부분을 확인 후
    해당 부분에서 서버 접근 KEY가 없으면 접근을 막기 위해서 g 값에 redirect 라는 속성을 추가 후
    실제 로직을 처리하는 함수에서 g의 redirect 속성을 확인 후 False인 경우에만 해당 로직을 처리하고
    아닌 경우는 403 에러를 발생하는 로직처리 할 때 사용 가능할 것 처럼 보임.
    """
    if request.path == "/util/chapter1":
        g.user = 'Anonymous' if not request.authorization else request.authorization[
            'username']


@util_router.route("/chapter1")
def chapter1():
    """
    Response() : 커스텀 응답 객체 생성
    첫번째 인자 : Response Body
    두번째 인자 : Response Statu Code
    세번째 인자 : Header Value

    make_response() : 일반 스트링으로 데이터를 보낼 경우 데이터가
    큰 경우는 처리하는데 서버와 클라이언트 모두 느려지기 때문.
    """
    res = Response("Custom Response", 200, {'user': g.user})
    return make_response(res)


# WSGI(WebServer Gateway Interface)
@util_router.route("/test_wsgi")
def wsgi_test():
    def application(environ, start_response):
        body = 'The request medthod was %s' % environ['REQUEST_METHOD']
        headers = [('Content-Type', 'text/plane'),
                   ('Content-Length', str(len(body)))]
        start_response('200 OK', headers)
        return [body]
    return make_response(application)


@util_router.route("/method/get", methods=["GET"])
def getMethod():
    if request.method == "GET":
        # GET의 query 처리
        q = request.args.get('q')
        return "q : %s" % q, 200


@util_router.route("/method/get/list", methods=["GET"])
def getListMethod():
    if request.method == "GET":
        # GET의 query 처리
        q = request.args.getlist('q')
        return "q : %s" % q, 200


@util_router.route("/method/post/form", methods=["POST"])
def postFormMethod():
    if request.method == "POST":
        # GET의 form 처리
        filename = request.form.get("filename")
        print(type(filename))
        if len(filename) > 1024:
            return make_response(filename)
        else:
            return filename, 201


@util_router.route("/method/post/file", methods=["POST"])
def postFileMethod():
    if request.method == "POST":
        file = request.files['file']
        filename = secure_filename(file.filename)
        return 'Upload %s' % filename, 201


@util_router.route("/method/post/json", methods=["POST"])
def postJsonMethod():
    if request.method == "POST":
        # GET의 body(json) 처리
        if request.is_json == True:
            body = request.get_json()
            return "body : %s" % body, 201
        else:
            return "", 404


def ymd(fmt):
    """
    서버가 실행이 되고 최초 당시에는 프로세스 상에 해당 함수가 올라가지 않고
    최초의 누군가가 /dt로 들어와 ymd를 실행해 줘야 해당 함수가 프로세스에 올라가서
    그 이후의 작업에서는 이미 올려진 상태에서 돌아간다.
    """
    def trans(date_str):
        return datetime.strptime(date_str, fmt)
    return trans


@util_router.route("/dt")
def dt():
    datestr = request.args.get("date", date.today(), type=ymd("%Y-%m-%d"))
    return "우리나라 시간 형식 : " + str(datestr)


@util_router.route("/header", methods=["GET"])
def headerProcess():
    if request.method == "GET":
        res = Response("header")
        res.headers.add("HeaderTest", 1)
        return make_response(res)


@util_router.route("/cookie", methods=["GET", "POST"])
def cookieProcess():
    if request.method == "GET":
        request.cookies.get("CookieTest", None)
        res = Response("cookie")
        return make_response(res)
    else:
        res = Response("cookie")
        res.set_cookie("CookieTest", 2)
        return make_response(res)
