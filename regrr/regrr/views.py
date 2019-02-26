"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from flask import redirect
from flask import session
from flask import request
from flask import url_for
from flask import abort
from flask import jsonify

import werkzeug.exceptions as exceptions

from regrr import app
from regrr import mail

import regrr.models as db

#############################################################
import json
def make_patient(fullname, department, date_of_birth):
	return {
		'fullname': fullname,
		'department': department,
		'date_of_birth': date_of_birth,
	}


#############################################################
import os
from flask import send_from_directory

@app.route('/favicon.png')
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static'),
		'favicon.png', mimetype='image/png')

#############################################################
path_non_login = [
	'/favicon.png',
	'/login'
	]

SESSION_KEY_USER = 'user'

def make_menu_item (href, text):
	return {
		'href': href,
		'text': text
		}

def make_menu_subitems (text, submenus):
	return {
		'text': text,
		'submenus': submenus
		}


menus_all = [
	make_menu_item('/feedback', 'Связь'),
	make_menu_subitems(
		'Макеты', [
				make_menu_item('/static/_design/index.html', 'Главная'),
				make_menu_item('/static/_design/link.html', 'Связь'),
				make_menu_item('/static/_design/login.html', 'Login'),
				make_menu_item('/static/_design/patient.html', 'Пациент'),
				make_menu_item('/static/_design/profile.html', 'Профиль'),
				make_menu_item('/static/_design/settings.html', 'Настройки'),
				make_menu_item('/static/_design/tests.html', 'Тесты'),
				make_menu_item('/static/_design/tests_viewer.html', 'Test viewer'),
				make_menu_item('/static/_design/test_national_early_warning_score.html', 'Test NEWS'),
				make_menu_item('/static/_design/test_geneva_risk_score_for_vte.html', 'Test VTE'),
			]
		),
	make_menu_subitems(
		'Исходный шаблон Editorial', [
				make_menu_item('/static/_design/editorial/index.html', 'index'),
				make_menu_item('/static/_design/editorial/generic.html', 'generic'),
				make_menu_item('/static/_design/editorial/elements.html', 'elements'),
			]
		)
	]


menus_admin = [
	make_menu_item('/', 'Пользователи')
	]
menus_admin.extend(menus_all)


menus_user = [
	make_menu_item('/', 'Пациенты')
	]
menus_user.extend(menus_all)



@app.before_request
def before_request():
	path = request.path
	if path.startswith('/static') or path in path_non_login:
		# print('before_request static:' + path)
		return
	
	user_info = session.get(SESSION_KEY_USER)
	if not user_info:
		# print('before_request fail:' + path)
		return redirect('/login')

	# print('before_request ok:' + path)

#############################################################
@app.route('/')
def index():

	user_info = session.get(SESSION_KEY_USER)

	title = ''
	menus = []
	data = {}
	isAdmin = False

	username = user_info.get('username')
	user_role = user_info.get('role')

	user_role = user_info.get('role')
	if user_role == db.UserRole.ADMIN:

		isAdmin = True
		title = 'Пользователи'
		menus = menus_admin

		users = []

		db_session = db.Session()
		db_users = db_session.query(db.User).all()
		for db_user in db_users:
			users.append(db_user.toJson())
		
		data['users'] = users

	elif user_role == db.UserRole.USER:
		title = 'Пациенты'
		menus = menus_user

		patients = []

		db_session = db.Session()
		db_patients = db_session.query(db.Patient).all()
		for db_patient in db_patients:
			patients.append(db_patient.toJson())

		data['patients'] = patients

	else:
		abort(500)

	data['username'] = username
	data = 'data = ' + json.dumps(data, indent=4,  ensure_ascii=False) + ';'
	server = {
		'title': title,
		'username': username,
		'isAdmin': isAdmin,
		'data': data,
		'menus': menus
	}

	str = render_template('index.html', server = server)
	return str

#############################################################
@app.route('/login', methods=['GET'])
def login():
	next = request.referrer or ''
	return render_template('login.html',
		next = next)

@app.route('/login', methods=['POST'])
def login_post():
	username = request.form['username']
	password = request.form['password']
	remember = bool(request.form.get('remember'))
	next = request.form['next']

	db_session = db.Session()
	query = db_session.query(db.User).filter(
		db.User.username.in_([username]),
		db.User.password.in_([password])
		)

	result = query.first()
	if not result:
		return render_template('login.html',
			display_error = True,
			password = password,
			username = username,
			remember = 'checked' if remember else '',
			next = next)

	user_lite = {
		'id': result.id,
		'username': result.username,
		'role': result.role
	}

	session[SESSION_KEY_USER] = user_lite
	session.permanent = remember
	session.modified = True

	path = (next or url_for('index'))
	return redirect(path)


@app.route("/logout")
def logout():
	session[SESSION_KEY_USER] = None
	session.permanent = False
	session.modified = True
	return redirect('/')

@app.route("/profile")
def profile():

	user_info = session.get(SESSION_KEY_USER)

	title = 'Профиль'
	menus = []
	data = {}
	isAdmin = False

	username = user_info.get('username')
	user_role = user_info.get('role')

	if user_role == db.UserRole.ADMIN:
		isAdmin = True
		menus = menus_admin
	else:
		menus = menus_user


	data['username'] = username
	data = 'data = ' + json.dumps(data, indent=4,  ensure_ascii=False) + ';'
	server = {
		'title': title,
		'username': username,
		'isAdmin': isAdmin,
		'data': data,
		'menus': menus
	}

	return render_template('profile.html', server = server)

################################################################
@app.route('/user/<username>', methods=['GET'])
def user_view(username):

	user_info = session.get(SESSION_KEY_USER)
	user_role = user_info.get('role')
	if user_role != db.UserRole.ADMIN:
		exceptions.abort(403)

	server = {
		'username': user_info.get('username'),
		'menus': menus_admin,
		'title': username
	}
	data = {}

	db_session = db.Session()
	db_user = db_session.query(db.User).filter(
		db.User.username.in_([username])
		)
	db_user = db_user.first()
	
	if not db_user:
		server['isOk'] = False
	else:
		server['isOk'] = True
		data = db_user.toJson()

	data = 'data = ' + json.dumps(data, indent=4,  ensure_ascii=False) + ';'
	server['data'] = data

	str = render_template('user.html', server = server)
	return str

################################################################
@app.route('/user_add', methods=['GET'])
def user_add():

	user_info = session.get(SESSION_KEY_USER)
	user_role = user_info.get('role')
	if user_role != db.UserRole.ADMIN:
		exceptions.abort(403)

	username = user_info.get('username')

	title = 'Добавить нового пользователя'
	menus = menus_admin
	data = {}

	data['username'] = username
	data = 'data = ' + json.dumps(data, indent=4,  ensure_ascii=False) + ';'

	server = {
		'title': title,
		'username': username,
		'data': data,
		'menus': menus
	}

	str = render_template('user_add.html', server = server)
	return str


@app.route('/user_add', methods=['POST'])
def user_add_post():

	user_info = session.get(SESSION_KEY_USER)
	user_role = user_info.get('role')
	if user_role != db.UserRole.ADMIN:
		exceptions.abort(403)

	username = request.form.get('username')
	password = username #request.form['password']
	lastname = request.form.get('lastname')
	firstname = request.form.get('firstname')
	middlename = request.form.get('middlename')
	date_of_birth = request.form.get('date_of_birth')
	position = request.form.get('position')
	email = request.form.get('email')

	user = db.User(username, password, db.UserRole.USER, lastname, firstname, middlename, position, email)

	db_session = db.Session()
	db_session.add(user)
	db_session.commit()

	return redirect('/')

################################################################
@app.route('/patient/<id>', methods=['GET'])
def patient_view(id):

	user_info = session.get(SESSION_KEY_USER)
	user_role = user_info.get('role')
	if user_role != db.UserRole.USER:
		exceptions.abort(403)

	server = {
		'username': user_info.get('username'),
		'menus': menus_user,
		'title': id
	}
	data = {}

	db_session = db.Session()
	db_patient = db_session.query(db.Patient).filter(
		db.Patient.id.in_([id])
		)
	db_patient = db_patient.first()
	
	if not db_patient:
		server['isOk'] = False
	else:
		server['isOk'] = True
		data = db_patient.toJson()

	data = 'data = ' + json.dumps(data, indent=4,  ensure_ascii=False) + ';'
	server['data'] = data

	str = render_template('patient.html', server = server)
	return str

################################################################
@app.route('/patient_add', methods=['GET'])
def patient_add():

	user_info = session.get(SESSION_KEY_USER)
	user_role = user_info.get('role')
	if user_role != db.UserRole.USER:
		exceptions.abort(403)

	username = user_info.get('username')

	title = 'Добавить нового пациента'
	menus = menus_user
	data = {}

	data['username'] = username
	data = 'data = ' + json.dumps(data, indent=4,  ensure_ascii=False) + ';'

	server = {
		'title': title,
		'username': username,
		'data': data,
		'menus': menus
	}

	str = render_template('patient_add.html', server = server)
	return str


@app.route('/patient_add', methods=['POST'])
def patient_add_post():

	user_info = session.get(SESSION_KEY_USER)
	user_role = user_info.get('role')
	if user_role != db.UserRole.USER:
		exceptions.abort(403)

	#username = request.form.get('username')
	#password = username #request.form['password']
	lastname = request.form.get('lastname')
	firstname = request.form.get('firstname')
	middlename = request.form.get('middlename')
	date_of_birth = request.form.get('date_of_birth')
	departament = request.form.get('departament')
	#email = request.form.get('email')

	patient = db.Patient(lastname, firstname, middlename, departament, date_of_birth)

	db_session = db.Session()
	db_session.add(patient)
	db_session.commit()

	return redirect('/')


################################################################
@app.route('/api/v1.0/test_username', methods=['POST'])
def api_test_username():
	if not request.json:
		abort(400)

	username = request.json.get('username')
	if not username or username == '':
		abort(400)

	db_session = db.Session()
	query = db_session.query(db.User).filter(
		db.User.username.in_([username]))
	result = query.first() == None
	return jsonify({'result': result})

################################################################
@app.route('/feedback', methods=['GET'])
def feedback():
	user_info = session.get(SESSION_KEY_USER)

	title = 'Связь'
	menus = []
	data = {}
	isAdmin = False

	username = user_info.get('username')
	user_role = user_info.get('role')

	if user_role == db.UserRole.ADMIN:
		isAdmin = True
		menus = menus_admin
	else:
		menus = menus_user


	data['username'] = username
	data = 'data = ' + json.dumps(data, indent=4,  ensure_ascii=False) + ';'
	server = {
		'title': title,
		'username': username,
		'isAdmin': isAdmin,
		'data': data,
		'menus': menus
	}

	return render_template('feedback.html', server = server)


@app.route('/feedback_result', methods=['GET'])
def feedback_result():
	user_info = session.get(SESSION_KEY_USER)

	title = 'Связь'
	menus = []
	data = {}
	isAdmin = False

	username = user_info.get('username')
	user_role = user_info.get('role')

	if user_role == db.UserRole.ADMIN:
		isAdmin = True
		menus = menus_admin
	else:
		menus = menus_user

	data['username'] = username
	data = 'data = ' + json.dumps(data, indent=4,  ensure_ascii=False) + ';'
	server = {
		'title': title,
		'username': username,
		'isAdmin': isAdmin,
		'data': data,
		'menus': menus
	}

	return render_template('feedback_result.html', server = server)



from flask_mail import Message

@app.route('/feedback', methods=['POST'])
def feedback_post():

	user_info = session.get(SESSION_KEY_USER)
	user_role = user_info.get('role')
	username = user_info.get('username')

	feedback_title = request.form.get('feedback-title')
	feedback_message = request.form.get('feedback-message')

	title = '[reqrr] от: {username}, тема: {feedback_title}'.format(username=username,
		feedback_title=feedback_title)
	
	recipients = app.config.get('APP_ADMIN_MAILS')
	msg = Message(title, recipients = recipients)
	msg.body = feedback_message
	msg.html = feedback_message
	mail.send(msg)

	return redirect('/feedback_result')


################################################################
@app.route('/contact')
def contact():
	"""Renders the contact page."""
	return render_template('contact.html',
		title='Contact',
		year=datetime.now().year,
		message='Your contact page.')

@app.route('/about')
def about():
	"""Renders the about page."""
	return render_template('about.html',
		title='About',
		year=datetime.now().year,
		message='Your application description page.')
