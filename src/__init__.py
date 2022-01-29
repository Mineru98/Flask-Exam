# -*- coding:utf-8 -*-
import os
from datetime import datetime, date, timedelta
from werkzeug.utils import secure_filename
from flask import Flask, g, request, url_for, Response, make_response, session, render_template
from flask_restplus import Api, Resource, fields

app = Flask(__name__)
api = Api(app, version='0.0.1', title='API title',
          description='A simple API',
          )
ns = api.namespace('custom', description='operations')
app.config.SWAGGER_UI_DOC_EXPANSION = 'full'
# request content의 용량 제한
app.config.update(MAX_CONTENT_LENGTH=1024*1024)
# session 보안 설정
# app.secret_key = '!f09wi!@dfjaslk'
# or
app.config.update(
    SECRET_KEY='!f09wi!@dfjaslk',
    SESSION_COOKIE_NAME='web_flask_session',
    PERMANENT_SESSION_LIFETIME=timedelta(31)
)
# 이스케이프 처리
# app.jinja_env.trim_blocks = True
app.debug = True

# 비밀번호 : 단방향 암호화만 허용
# 주민번호 및 계좌 번호 : 양방향 암호화까지 허용


@ns.route("/")
@ns.response(200, 'Found')
@ns.response(404, 'Not found')
@ns.response(500, 'Internal Error')
class Algorithnm(Resource):
    @ns.doc('get')
    def get(sef):
        return "Hello, World!", 200


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
            file_path = os.path.join(app.root_path, endpoint, filename)
            values['v'] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


# preprocessor :  컨택스트가 구동 될 때 시작해 됨
@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


# 해당 경로에 최초 요청에 대해서 선처리
@app.before_first_request
def before_first_request():
    pass


# 해당 경로에 요청 처리 전에 처리
# Web Filter 처리가 필요한 경우
# 디비 커넥션을 실행하는 경우 사용
@app.before_request
def before_request():
    pass


# 해당 경로에 대한 요청 처리
@app.route("/")
def index():
    return "Hello, World!", 200


@app.route("/tmpl")
def t():
    return render_template("index.html", title="Title")


# 해당 경로에 대한 요청 처리 이후에 대한 처리
# 디비 커넥션을 종료하는 경우 사용
@app.after_request
def after_request(return_val):
    return return_val


# 요청이 다 끝나고 나서 처리
@app.teardown_request
def teardown_request(error):
    print("Close")


# Application Context 내용이 다 끝나고 나서 처리
@app.teardown_appcontext
def teardown_appcontext(error):
    print("Finish")


@app.before_request
def before_request_chapter1():
    """
    g(Application Context)는 전역 변수 개념이다.
    하나의 요청 처리 단위에서 공유 되는 변수로 쓰임.
    예를 들면 before_request 어노테이션에서 특정 url에서는 요청 헤더에 Authencation 부분을 확인 후
    해당 부분에서 서버 접근 KEY가 없으면 접근을 막기 위해서 g 값에 redirect 라는 속성을 추가 후
    실제 로직을 처리하는 함수에서 g의 redirect 속성을 확인 후 False인 경우에만 해당 로직을 처리하고
    아닌 경우는 403 에러를 발생하는 로직처리 할 때 사용 가능할 것 처럼 보임.
    """
    if request.path == "/chapter1":
        g.user = 'Anonymous' if not request.authorization else request.authorization[
            'username']


@app.route("/chapter1")
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


@app.route("/rp")
def rp():
    # 같은 필드 값으로 여러개가 들어오는 경우 제일 처음에 들어온 값만 인정함.
    q = request.args.get('q')
    return "q= %s" % str(q)


@app.route("/rp/list")
def rp_list():
    # 같은 필드 값으로 여러개가 들어오는 경우 리스트 형태로 받음
    q = request.args.getlist('q')
    return "q= %s" % str(q)


# WSGI(WebServer Gateway Interface)
@app.route("/test_wsgi")
def wsgi_test():
    def application(environ, start_response):
        # F12 개발자 도구 열어서 내용 확인해보면 됨.
        body = 'The request medthod was %s' % environ['REQUEST_METHOD']
        headers = [('Content-Type', 'text/plane'),
                   ('Content-Length', str(len(body)))]
        start_response('200 OK', headers)
        return [body]
    return make_response(application)


@app.route("/method/get", methods=["GET"])
def getMethod():
    if request.method == "GET":
        # GET의 query 처리
        q = request.args.get('q')
        return "q : %s" % q, 200


@app.route("/method/get/list", methods=["GET"])
def getListMethod():
    if request.method == "GET":
        # GET의 query 처리
        q = request.args.getlist('q')
        return "q : %s" % q, 200


@app.route("/method/post/form", methods=["POST"])
def postFormMethod():
    if request.method == "POST":
        # GET의 form 처리
        filename = request.form.get("filename")
        print(type(filename))
        if len(filename) > 1024:
            return make_response(filename)
        else:
            return filename, 201


@app.route("/method/post/file", methods=["POST"])
def postFileMethod():
    if request.method == "POST":
        file = request.files['file']
        filename = secure_filename(file.filename)
        return 'Upload %s' % filename, 201


@app.route("/method/post/json", methods=["POST"])
def postJsonMethod():
    if request.method == "POST":
        # GET의 body(json) 처리
        if request.is_json == True:
            body = request.get_json()
            return "body : %s" % body, 201
        else:
            return "", 404


@app.route("/wc")
def wc():
    key = request.args.get('key')
    val = request.args.get('val')
    res = Response("SET COOKIE")
    res.set_cookie(key, val)
    return make_response(res)


@app.route("/rc")
def rc():
    key = request.args.get('key')
    val = request.cookies.get(key)
    return "cookie['" + key + "'] = " + str(val)


@app.route("/reqenv")
def reqenv():
    return ('REQUEST_METHOD: %(REQUEST_METHOD) s <br>'
            'SCRIPT_NAME: %(SCRIPT_NAME) s <br>'
            'PATH_INFO: %(PATH_INFO) s <br>'
            'QUERY_STRING: %(QUERY_STRING) s <br>'
            'SERVER_NAME: %(SERVER_NAME) s <br>'
            'SERVER_PORT: %(SERVER_PORT) s <br>'
            'SERVER_PROTOCOL: %(SERVER_PROTOCOL) s <br>'
            'wsgi.version: %(wsgi.version) s <br>'
            'wsgi.url_scheme: %(wsgi.url_scheme) s <br>'
            'wsgi.input: %(wsgi.input) s <br>'
            'wsgi.errors: %(wsgi.errors) s <br>'
            'wsgi.multithread: %(wsgi.multithread) s <br>'
            'wsgi.multiprocess: %(wsgi.multiprocess) s <br>'
            'wsgi.run_once: %(wsgi.run_once) s') % request.environ


def ymd(fmt):
    def trans(date_str):
        return datetime.strptime(date_str, fmt)
    return trans


@app.route("/dt")
def dt():
    datestr = request.values.get('date', date.today(), type=ymd('%Y-%m-%d'))
    return "우리나라 시간 형식: " + str(datestr)


@app.route("/setsess")
def setsess():
    session['Token'] = '123X'
    return "Session 설정 완료"


@app.route("/getsess")
def getsess():
    if session.get('Token'):
        return session.get("Token")
    else:
        return "Session 없음"


@app.route("/delsess")
def delsess():
    if session.get('Token'):
        del session['Token']
    return "Session 삭제 완료"
