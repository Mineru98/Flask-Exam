# -*- coding:utf-8 -*-
import os
from flask import Flask, g, request, url_for, Response, make_response, jsonify

app = Flask(__name__)
app.debug = True


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


# WSGI(WebServer Gateway Interface)
@app.route("/test_wsgi")
def wsgi_test():
    def application(environ, start_response):
        body = 'The request medthod was %s' % environ['REQUEST_METHOD']
        headers = [('Content-Type', 'text/plane'),
                   ('Content-Length', str(len(body)))]
        start_response('200 OK', headers)
        return [body]
    return make_response(application)