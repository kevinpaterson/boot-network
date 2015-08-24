"""
@author: 43264158
"""
import re


def post_to_html(content):
    """Convert a post to safe HTML, quote any HTML code, convert
    URLs to live links and spot any @mentions and turn
    them into links.  Return the HTML string"""

    html = str(content)

    html = html.replace("&", "&amp;")
    html = html.replace("<", "&lt;")
    html = html.replace(">", "&gt;")

    # links
    html = re.sub(r"(http://\S*)", r"<a href='\1'>\1</a>", html)
    # mentions
    html = re.sub(r"@(\w+\.*\w+)", r"<a href='/users/\1'>@\1</a>", html)
    # hashtags
    html = re.sub(r"#(\w*)", r"<a href='/tag/\1'>#\1</a>", html)

    return html


def post_list(db, usernick=None, limit=50):
    """Return a list of posts ordered by date
    db is a database connection (as returned by COMP249Db())
    if usernick is not None, return only posts by this user
    return at most limit posts (default 50)

    Returns a list of tuples (id, timestamp, usernick, avatar,  content)
    """
    cursor = db.cursor()
    sql = "SELECT id, timestamp, usernick, users.avatar, content FROM posts INNER JOIN users ON posts.usernick=users.nick"
    if usernick is not None:
        table = cursor.execute(sql + " WHERE usernick = '%s'" % usernick).fetchall()
    else:
        table = cursor.execute(sql).fetchall()

    return table[:limit]


def post_list_mentions(db, usernick, limit=50):
    """Return a list of posts that mention usernick, ordered by date
    db is a database connection (as returned by COMP249Db())
    return at most limit posts (default 50)

    Returns a list of tuples (id, timestamp, usernick, avatar,  content)
    """
    cursor = db.cursor()
    sql = "SELECT id, timestamp, usernick, users.avatar, content " \
          "FROM posts INNER JOIN users ON posts.usernick=users.nick"
    table = cursor.execute((sql + " WHERE content LIKE ?"), ('%'+usernick+'%', )).fetchall()

    return table[:limit]

def post_list_tags(db, tag, limit=50):
    """Return a list of posts that mention the hashtag, ordered by date
    db is a database connection (as returned by COMP249Db())
    return at most limit posts (default 50)

    Returns a list of tuples (id, timestamp, usernick, avatar,  content)
    """
    cursor = db.cursor()
    sql = "SELECT id, timestamp, usernick, users.avatar, content " \
          "FROM posts INNER JOIN users ON posts.usernick=users.nick"
    table = cursor.execute((sql + " WHERE content LIKE ?"), ('%'+tag+'%', )).fetchall()

    return table[:limit]


def post_add(db, usernick, message):
    """Add a new post to the database.
    The date of the post will be the current time and date.

    Return a the id of the newly created post or None if there was a problem"""

    if len(message) > 150:
        return None

    cursor = db.cursor()
    sql = "INSERT INTO posts (usernick, content) VALUES (?,?)"
    cursor.execute(sql, (usernick, message))
    db.commit()
    post_id = cursor.execute("SELECT id FROM posts ORDER BY id DESC LIMIT 1;").fetchone()
    return post_id[0]
