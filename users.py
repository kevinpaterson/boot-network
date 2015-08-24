"""
@author:
"""

import bottle, uuid

# this variable MUST be used as the name for the cookie used by this application
COOKIE_NAME = 'sessionid'

def check_login(db, usernick, password):
    """returns True if password matches stored"""

    cursor = db.cursor()

    password = db.crypt(password)
    sql = "SELECT password FROM users"
    stored_password = cursor.execute(sql + " WHERE nick = '%s'" % usernick).fetchall()

    if stored_password == []:
        return False

    return password == stored_password[0][0]

def generate_session(db, usernick):
    """create a new session and add a cookie to the request object (bottle.request)
    user must be a valid user in the database, if not, return None
    There should only be one session per user at any time, if there
    is already a session active, use the existing sessionid in the cookie
    """
    cur = db.cursor()
    cur.execute("SELECT nick FROM users WHERE nick='%s'" % usernick)

    row = cur.fetchone()
    if not row:
        return None

    session_id = bottle.request.get_cookie(COOKIE_NAME)
    if session_id:
        bottle.response.set_cookie(COOKIE_NAME, session_id)

    cur.execute("SELECT sessionid, usernick FROM sessions WHERE usernick=?", (usernick, ))

    row = cur.fetchone()
    if not row:
        session_id = str(uuid.uuid4())
        cur.execute("INSERT INTO sessions VALUES (?, ?)", (session_id, usernick))
        db.commit()
        bottle.response.set_cookie(COOKIE_NAME, session_id)




def delete_session(db, usernick):
    """remove all session table entries for this user"""

    cur = db.cursor()

    cur.execute("DELETE FROM sessions WHERE usernick='%s'" % usernick)

    bottle.response.delete_cookie(COOKIE_NAME)

def session_user(db):
    """try to
    retrieve the user from the sessions table
    return usernick or None if no valid session is present"""

    session_id = bottle.request.get_cookie(COOKIE_NAME)

    cur = db.cursor()

    cur.execute("SELECT usernick FROM sessions WHERE sessionid=?", (session_id, ))

    row = cur.fetchone()
    if not row:
        return None

    return row[0]