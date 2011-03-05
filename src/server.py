'''REST API for phsb-guide example'''
import time
import flask
import urlparse
import datetime

from flask import request
app = flask.Flask(__name__)

import model
import pubsubhubbub_publish as pshb

import feedparser

from feedformatter import Feed

from settings import HUB_URL, SECRET_KEY, SALT

app.secret_key = SECRET_KEY
model.set_salt(SALT)

def get_domain():
    '''
    return the domain from this server (for example http://localhost:8080)
    '''
    parts = urlparse.urlparse(request.url_root)

    return parts.scheme + "://" + parts.netloc

def parse_messages(data, timeline):
    '''
    return a list of model.Message objects from *data* which contains an atom
    feed as a string
    '''

    feed = feedparser.parse(data)

    msgs = []

    for entry in feed['entries']:
        author = entry.author
        text = entry.description
        date = datetime.datetime(*entry.updated_parsed[:7])

        if hasattr(entry, "tags"):
            tags = [tag.term[1:] for tag in entry.tags if tag.term.startswith('#')]
            mentions = [tag.term[1:] for tag in entry.tags if tag.term.startswith('@')]
        else:
            tags = []
            mentions = []

        dct = dict(text=text, created=date, tags=tags, mentions=mentions,
                user=author, timeline=timeline)

        msgs.append(model.Message.from_dict(dct))

    return msgs

def atom_list_response(items, title, path, author):
    feed = Feed()

    feed.feed["title"] = title
    feed.feed["link"] = get_domain() + path
    feed.feed["author"] = author

    for msg in items:
        item = {}
        item["title"] = "message from " + msg.user + " on " + msg.created.isoformat()
        item["link"] = get_domain() + "/m/" + str(msg.key())
        item["description"] = msg.text
        item["pubDate"] = msg.created.timetuple()
        item["guid"] = str(msg.key())
        item["author"] = msg.user

        item["category"] = ["#" + val for val in msg.tags]
        item["category"] += ["@" + val for val in msg.mentions]

        feed.items.append(item)

    body = feed.format_atom_string()
    return flask.Response(body, 200, mimetype="application/atom+xml")

def json_list_response(items):
    body = flask.json.dumps([item.to_json() for item in items])
    return flask.Response(body, 200, mimetype="application/json")

def response(status=200, content="", content_type="text/plain"):
    return flask.Response(response=content, status=status,
            content_type=content_type)

def not_found(content="not found", content_type="text/plain"):
    return response(404, content, content_type)

def unauthorized(content="unauthorized", content_type="text/plain"):
    return response(401, content, content_type)

def bad_request(content="bad request", content_type="text/plain"):
    return response(400, content, content_type)

def internal_error(content="internal error", content_type="text/plain"):
    return response(500, content, content_type)

# API methods

MIN_LIMIT = 1
MAX_LIMIT = 20

def fetch_messages_atom(title, path, author, offset=0, limit=20, **kwargs):
    messages = fetch_messages(offset=0, limit=20, **kwargs)
    return atom_list_response(messages, title, path, author)

def fetch_messages_json(offset=0, limit=20, **kwargs):
    messages = fetch_messages(offset=0, limit=20, **kwargs)
    return json_list_response(messages)

def fetch_messages(offset=0, limit=20, **kwargs):
    if offset < 0:
        return bad_request("invalid offset")

    if limit < MIN_LIMIT or limit > MAX_LIMIT:
        return bad_request("invalid limit")

    return model.Message.search(order="-created", offset=offset,
            limit=limit, **kwargs)

# HTML API

@app.route('/', methods=['GET'])
def index():
    return flask.render_template("index.html")

@app.route('/signup', methods=['GET'])
def show_signup():
    return flask.render_template("signup.html")

@app.route('/m/<key>/', methods=['GET'])
def show_message(key):
    msg = model.Message.from_key(key)

    if msg is None:
        return not_found()

    return flask.render_template("message.html", msg=msg)

## OLD SCHOOL API

@app.route('/signup', methods=['POST'])
def signup():
    form = request.form

    username = form['user']
    password = form['password']
    mail     = form['mail']
    name     = form.get('name', username)

    user = model.User(user=username, password=model.encrypt(password),
            mail=mail, name=name, bio="")
    user.save()

    return flask.redirect("/")

## JSON API

@app.route('/a/message/', methods=['POST'])
def create_message():
    msgdct  = flask.json.loads(request.data)

    if not 'user' in flask.session:
        return unauthorized()

    user = flask.session['user']

    if user != msgdct['user']:
        return bad_request("invalid user")

    msgdct['created'] = datetime.datetime.now()
    msgdct['tags'] = model.Message.extract_tags(msgdct['text'])
    msgdct['mentions'] = model.Message.extract_mentions(msgdct['text'])
    msgdct['timeline'] = user

    status, msg = model.Message.from_dict(msgdct)

    if not status:
        return bad_request(msg)

    msg.save()
    try:
        pshb.publish(HUB_URL, get_domain() + "/atom/messages/from/" + user + "/")
    except Exception, ex:
        app.logger.error("error sending ping to pubsubhubbub", ex)

    return flask.jsonify(**msg.to_json())


@app.route('/a/login/', methods=['POST'])
def login():
    msgdct  = flask.json.loads(request.data)
    username = msgdct['user']
    password = msgdct['password']

    users = model.User.search(user=username, password=model.encrypt(password))

    for user in model.User.search():
        app.logger.info("user %s pass %s", user.user, user.password)

    if users:
        app.logger.info("login succeeded for %s", users[0])
        status = True
    else:
        app.logger.error("login failed for %s", username)
        status = False

    flask.session['user'] = username

    return flask.jsonify(ok=status, user=username)

@app.route('/a/messages/', methods=['GET'])
def get_messages():
    return fetch_messages_json()

@app.route('/a/messages/<int:offset>/', methods=['GET'])
def get_messages_offset(offset):
    return fetch_messages_json(offset)

@app.route('/a/messages/<int:offset>/<int:limit>/', methods=['GET'])
def get_messages_offset_limit(offset, limit):
    return fetch_messages_json(offset, limit)

@app.route('/a/messages/tag/<tag>/', methods=['GET'])
def get_messages_by_tag_json(tag):
    return fetch_messages_json(0, 20, tags=tag)

@app.route('/a/messages/tag/<tag>/<int:offset>/<int:limit>/', methods=['GET'])
def get_messages_by_tag_limit_json(tag, offset, limit):
    return fetch_messages_json(offset, limit, tags=tag)

@app.route('/a/messages/to/<user>/', methods=['GET'])
def get_messages_to_user_json(user):
    return fetch_messages_json(0, 20, mentions=user)

@app.route('/a/messages/from/<user>/', methods=['GET'])
def get_messages_from_user_json(user):
    return fetch_messages_json(0, 20, user=user)

@app.route('/a/messages/from/<user>/<int:offset>/<int:limit>/', methods=['GET'])
def get_messages_from_user_limit_json(user, offset, limit):
    return fetch_messages_json(offset, limit, user=user)

@app.route('/a/messages/from/<user>/tag/<tag>/', methods=['GET'])
def get_messages_from_user_by_tag_json(user, tag):
    return fetch_messages_json(0, 20, user=user, tag=tag)

@app.route('/a/messages/to/<user>/tag/<tag>/', methods=['GET'])
def get_messages_to_user_by_tag_json(user, tag):
    return fetch_messages_json(0, 20, user=user, tag=tag)

@app.route('/a/timeline/<user>/', methods=['GET'])
def get_user_timeline_json(user):
    return fetch_messages_json(0, 20, timeline=user)

@app.route('/a/timeline/<user>/<int:offset>/<int:limit>/', methods=['GET'])
def get_user_timeline_limit_json(user, offset, limit):
    return fetch_messages_json(offset, limit, timeline=user)

## ATOM API

@app.route('/atom/messages/', methods=['GET'])
def get_messages_atom():
    return fetch_messages_atom("all messages", "/atom/messages/", get_domain())

@app.route('/atom/messages/tag/<tag>/', methods=['GET'])
def get_messages_by_tag_atom(tag):
    return fetch_messages_atom("messages with tag " + tag, "/atom/messages/tag/" + tag, get_domain(), tags=tag)

@app.route('/atom/messages/to/<user>/', methods=['GET'])
def get_messages_to_user_atom(user):
    return fetch_messages_atom("messages to user " + user, "/atom/messages/to/" + user, get_domain(), mentions=user)

@app.route('/atom/messages/from/<user>/', methods=['GET'])
def get_messages_from_user_atom(user):
    return fetch_messages_atom("messages from user " + user, "/atom/messages/from/" + user, get_domain(), user=user)

@app.route('/atom/messages/from/<user>/tag/<tag>/', methods=['GET'])
def get_messages_from_user_by_tag_atom(user, tag):
    return fetch_messages_atom("messages from user %s by tag %s" % (user, tag),
            "/atom/messages/from/%s/tag/%s" % (user, tag), get_domain(), user=user, tag=tag)

@app.route('/atom/messages/to/<user>/tag/<tag>/', methods=['GET'])
def get_messages_to_user_by_tag_atom(user, tag):
    return fetch_messages_atom("messages to user %s by tag %s" % (user, tag),
            "/atom/messages/to/%s/tag/%s" % (user, tag), get_domain(), user=user, tag=tag)

## PHSB code

@app.route('/p/notify/<user>/', methods=['POST'])
def receive_notification(user):
    # TODO: prove that the notification is valid (comes from phsb etc.)
    app.logger.info("receiving notification to user %s", user)
    data = request.stream.read()

    for ok, msg in parse_messages(data, user):
        if ok:
            msg.save()
            app.logger.info(str(msg))
        else:
            app.logger.error("error parsing message %s", msg)

    return "thanks!"

@app.route('/p/notify/<user>/', methods=['GET'])
def confirm_subscription(user):
    # TODO: check the challenge and confirm that it's a subscription we made
    app.logger.info("confirming subscription")
    if 'hub.challenge' in request.args:
        return request.args['hub.challenge']

    return bad_request('hub.challenge not present in request args')

if __name__ == '__main__':
    app.run()
