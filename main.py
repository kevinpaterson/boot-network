__author__ = 'Steve Cassidy'

from bottle import Bottle, template, static_file, request, response, HTTPError
import interface
import users
from database import COMP249Db


application = Bottle()

@application.route('/')
def index(failed=False):
    db = COMP249Db()

    current_user = users.session_user(db)
    if current_user:
        html = get_form("logout")
    else:
        html = get_form("login")
        if failed:
            html += "Login Failed, please try again"

    posts = interface.post_list(db)

    for post in posts:
        html += format_post(post)

    return template('general', title="Welcome to Psst!", content=html)


def get_form(type):
    if type == "login":
        form = """
            <form id='loginform' method='post' action='/login'>
            <input type='text' name='nick'>
            <input type='password' name='password'>
            <input type='submit' value='Login' >
            </form>
        """
    if type == "logout":
        form = """
            Logged in as %s
            <form id='logoutform' method='post' action='/logout'>
            <input type='submit' value='logout' >
            </form>
            <form id='postform' method='post' action='/post'>
            <input type='text' name='post'>
            <input type='submit' value='post'>
            </form>
        """ % users.session_user(COMP249Db())
    return form

@application.post('/login')
def login():
    db = COMP249Db()

    usernick = request.forms.get('nick')
    password = request.forms.get('password')

    if users.check_login(db, usernick, password):
        users.generate_session(db, usernick)
        response.set_header('Location', '/')
        response.status = 303
        return 'Redirect to /'
    else:
        response.status = 200
        return index(True)

@application.post('/logout')
def logout():
    db = COMP249Db()
    users.delete_session(db, users.session_user(db))
    response.set_header('Location', '/')
    response.status = 303
    return 'Redirect to /'

@application.post('/post')
def new_post():
    db = COMP249Db()
    message = request.forms.get('post')
    interface.post_add(db, users.session_user(db), message)

    response.set_header('Location', '/')
    response.status = 303
    return 'Redirect to /'

def format_post(post):
    # id, timestamp, usernick, users.avatar, content
    html = "<article>\n"
    html += "<a href='/users/" + post[2] + "'><b>" + post[2] + "</b></a>" + "<br>\n" # Username

    content = interface.post_to_html(post[4])
    html += content + "<br>\n" # content

    html += "<i>" + post[1] + "</i>" + "<br>\n" # timestamp
    html += "</article>\n"
    return html

@application.route('/static/<filename:path>')
def static(filename):

    return static_file(filename=filename, root='static')



@application.route('/users/<name:path>')
def user_page(name):
    db = COMP249Db()

    posts = interface.post_list(db, name)
    html = ""

    if users.session_user(db):
        html += get_form("logout")

    for post in posts:
        html += format_post(post)

    avatar = ""
    if posts:
        avatar += '<div id="avatar"><img src="' + posts[0][3] + '" alt="avatar"></div>'

    title = name + "'s Profile"
    return template('users', title=title, root="users/" + name, content=html, avatar=avatar)

@application.route('/mentions/<name:path>')
def mentions(name):

    db = COMP249Db()

    posts = interface.post_list_mentions(db, name)
    html = ""

    if users.session_user(db):
        html += get_form("logout")

    for post in posts:
        html += format_post(post)

    avatar = '<img src="' + posts[0][3] + '" alt="avatar">'

    title = name + "'s Mentions"
    return template('general', title=title, root="mentions/" + name, content=html)

@application.route('/tag/<tag:path>')
def tags(tag):

    db = COMP249Db()

    posts = interface.post_list_mentions(db, tag)
    html = ""

    if users.session_user(db):
        html += get_form("logout")

    for post in posts:
        html += format_post(post)

    avatar = '<img src="' + posts[0][3] + '" alt="avatar">'

    title = "Pssts about " + tag
    return template('general', title=title, root="tag/" + tag, content=html)


if __name__ == '__main__':
    application.run(debug=True)