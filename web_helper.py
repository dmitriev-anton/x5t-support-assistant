from checker import check_logged_in
from flask import Flask, render_template, request, escape, session, copy_current_request_context
#from threading import Thread
import pymssql
from time import sleep

class ConnectionError(Exception):
    pass

class UseDatabase:

    def __init__(self, config: dict) -> None:
        self.configuration = config

    def __enter__(self) -> 'cursor':
        try:
            self.conn = pymssql.connect(**self.configuration)
            self.cursor = self.conn.cursor()
            return self.cursor
        except pymssql.connector.errors.InterfaceError as err:
            raise ConnectionError(err)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

def to_sql_adapter (entr_string :str, delimiter:str='') -> str:
#функция забирает из строки записи состоящие из символов 0-9\/_ и
# ставит их через запятую выделяя каждое "слово" ставя cимвол delimiter до и после "слова"
    import re
    result = ''
    entr_list = re.findall('[\w0-9-\\\_\/\*\(\)]+', str(entr_string))
    for i in entr_list:
        result = result + delimiter + i + delimiter + ","
    return result[0:len(result)-1]


app = Flask(__name__)
app.config['dbconfig'] = {'host':'192.168.136.202', 'database':'priem-x5-db'}

@app.route('/')
@app.route('/entry')
def entry_page() -> 'html':
    return render_template('entry.html',
                           the_title='Race Completer')

@app.route('/page1')
@check_logged_in
def page1() -> str:
    return 'Main'

#GoCargo Race Completer
@app.route('/page2', methods=['GET', 'POST'])
@check_logged_in
def page2() -> 'html':
    @copy_current_request_context
    def race_completer(req: 'flask_request') -> str:
        sleep(15)
        with UseDatabase(app.config['dbconfig']) as cursor:
            _SQL = """update tasklists set state = 'completed' 
                                where (state <> 'cancelled') and ordernumberotd in (%S)"""
            _test = """select orderonumberotd, state from tasklists where ordernumberotd in (%S)"""

        for strings in req.form['phrase']:
            if strings not in ['', ' ', '\n']:
                result = result + to_sql_adapter(strings, "'") + ','
        otds = result[0:len(result) - 1]
        cursor.execute(_test, otds)
        contents = cursor.fetchall()
        return contents


    phrase = request.form['phrase']
    for strings in phrase:
        if strings not in ['', ' ', '\n']:
            result = result + to_sql_adapter(strings, "'") + ','
    otds = result[0:len(result) - 1]

    contents = race_completer(otds)
    letters = """ob's Done"""
    title = """Races completed"""

    return render_template('results.html',
                           the_phrase=phrase,
                           the_letters=letters,
                           the_title=title,
                           the_results=contents, )


@app.route('/page3')
@check_logged_in
def page3() -> str:
    return 'ORD monitors'

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
