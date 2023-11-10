from flask import Flask, session

from checker import check_logged_in

app = Flask(__name__)

@app.route('/')
def hello() -> str:
    return 'what the fucking webapp'

@app.route('/page1')
@check_logged_in
def page1() -> str:
    return 'Page 1 yeahMan'


@app.route('/page2')
@check_logged_in
def page2() -> str:
    return 'Page 2 yeahMan'


@app.route('/page3')
@check_logged_in
def page3() -> str:
    return 'Page 3 yeahMan'

@app.route('/login')
def do_login() -> str:
    session['logged_in'] = True
    return 'You are in now'

@app.route('/logout')
def do_logout() -> str:
    session.pop('logged_in')
    return 'You are out'

app.secret_key = 'SimplePasskey'

if __name__ == '__main__':
    app.run(debug=True)
