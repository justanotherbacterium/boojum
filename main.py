# coding: utf-8
from pymongo import MongoClient
from flask import Flask, render_template, abort, request, url_for, redirect, request, jsonify, flash, session, session, g
from bson.json_util import dumps
from werkzeug import check_password_hash, generate_password_hash
from wtforms import Form, BooleanField, TextField, PasswordField, validators

class RegistrationForm(Form):
    username = TextField('Username', [validators.Length(min=4, max=25)])
    email = TextField('Email Address', [validators.Length(min=6, max=35)])
    password = PasswordField('New Password', [
        validators.Required(),
        validators.EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')
    accept_tos = BooleanField('I accept the TOS', [validators.Required()])

app = Flask(__name__)

client = MongoClient('localhost', 27017)

db = client['boojom']
tags = db.tags
objects = db.objects
users = db.users


@app.route("/")
def hello():
    _tags = tags.find()
    return render_template('index.html', show_tags=[tag['name'] for tag in _tags], show_objects=[obj['name'] for obj in objects.find()])

@app.route('/<tag>')
def tag_page(tag):
    current_tag = tags.find_one({'name': tag})
    if current_tag:
        return render_template('tag.html', name=current_tag['name'], id=current_tag['_id'])
    else:
        return render_template('404.html', show_name=tag)

@app.route('/tag/add')
def add_tag_page():
    name = request.args.get('name')
    #OMG_))
    if name == None:
        name = ''
    return render_template('add_tag.html', tag_name=name)

"""
получить коллекцию тегов в JSON,
У роута должно быть два параметра limit и offset, для слайса выборки
TODO:
стоит сменить url для API на
'api/tags' - метод GET и POST (чтобы можно было туда оправлить новый тег),
'api/tags/<name>' - методы GET, PUT, DELETE для работы с конкретным тегом
возможно понадобится
if request.method == 'POST':
    # почему-то после отправки стандартным способом не показывает тег, но если снова зайти на страницу то ОК - видно JSON
    tags.insert({'name': name})
    # https://gist.github.com/ibeex/3257877
    app.logger.info('params are: %s', request.query_string)
    return redirect('/'+name)
"""

@app.route('/api/tags/',  methods=['GET'])
def tags_list():
    resp = dumps(tags.find())
    return resp

@app.route('/api/tags/<name>', methods=['GET', 'PUT', 'DELETE'])
def get_tag(name):
    if request.method == 'GET':
        current_tag = tags.find_one({'name': name})
        app.logger.info('params are: %s', request.url)
        return dumps(current_tag)
    if request.method == 'PUT':
        tags.update({'name': name}, {'name': name})
    if request.method == 'DELETE':
        tags.remove({'name': name}, {justOne: true})


@app.route('/api/add/tag', methods=['POST'])
def add_tag():
    if request.method == 'POST':
        app.logger.info('name is: %s', request.form)
        name = request.form['name']
        tags.insert({'name': name})
        response = jsonify(message=str('OK'))
        response.status_code = 200
        return response


"""Auth"""
# @app.route('/register')
# def login_page():
#     return render_template('register.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    error = None
    if request.method == 'POST':
        if not request.form['username']:
            error = 'You have to enter a username'
        elif not request.form['email'] or '@' not in request.form['email']:
            error = 'You have to enter a valid email address'
        elif not request.form['password']:
            error = 'You have to enter a password'
        elif request.form['password'] != request.form['password2']:
            error = 'The two passwords do not match'
        else:
            username = request.form['username']
            email = request.form['username']
            password = generate_password_hash(request.form['password'])
            users.insert({'username': username, 'email': email, 'password': password})
            flash('You were successfully registered and can login now')
            return redirect('/login')
    if request.method == 'GET':
        return render_template('register.html', error=error)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        user = users.find_one({'username': request.form['username']})
        if user is None:
            error = 'Invalid username'
        elif not check_password_hash(user['password'],
                                     request.form['password']):
            error = 'Invalid password'
        else:
            flash('You were logged in, ' + user['username'])
            return redirect('/')
    if request.method == 'GET':
        return render_template('login.html', error=error)

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.run(debug=True)

"""
не пашит :-(
if app.debug:
    from flaskext.stylus2css import stylus2css
    stylus2css(app, css_folder='static/css', stylus_folder='stylus')
"""
