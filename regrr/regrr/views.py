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
from regrr import app

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


menus_all = [
	make_menu_item('/static/_design/index.html', '(Design) Главная'),
	make_menu_item('/static/_design/link.html', '(Design) Связь'),
	make_menu_item('/static/_design/login.html', '(Design) Login'),
	make_menu_item('/static/_design/patient.html', '(Design) Пациент'),
	make_menu_item('/static/_design/profile.html', '(Design) Профиль'),
	make_menu_item('/static/_design/settings.html', '(Design) Настройки'),
	make_menu_item('/static/_design/tests.html', '(Design) Тесты'),
	make_menu_item('/static/_design/tests_viewer.html', '(Design) Test viewer'),
	make_menu_item('/static/_design/test_national_early_warning_score.html', '(Design) Test NEWS'),
	make_menu_item('/static/_design/test_geneva_risk_score_for_vte.html', '(Design) Test VTE'),
	{
		'text': 'Исходный шаблон Editorial',
		'submenus': [
			make_menu_item('/static/_design/editorial/index.html', 'index'),
			make_menu_item('/static/_design/editorial/generic.html', 'generic'),
			make_menu_item('/static/_design/editorial/elements.html', 'elements'),
			]
	}]


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
		print('before_request static:' + path)
		return
	
	user_id = session.get(SESSION_KEY_USER)
	if not user_id:
		print('before_request fail:' + path)
		return redirect('/login')

	print('before_request ok:' + path)

#############################################################
@app.route('/')
def index():

	user_id = session.get(SESSION_KEY_USER)

	title = ''
	menus = []
	data = {}

	data['username'] = user_id.get('username')

	user_role = user_id.get('role')
	if user_role == db.UserRole.ADMIN:
		title = 'Пользователи'
		menus = menus_admin

		patients = []

		db_session = db.Session()
		users = db_session.query(db.User).all()
		for user in users:
			patients.append(make_patient(
				user.lastname + ' ' + user.firstname + ' ' + user.middlename,
				user.email,
				user.username))
		
		data['patients'] = patients

	elif user_role == db.UserRole.USER:
		title = 'Пациенты'
		menus = menus_user

		patients = []
		data['patients'] = patients

	else:
		abort(500)

	data = 'data = ' + json.dumps(data, indent=4,  ensure_ascii=False) + ';'

	server = {
		'title': title,
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
	#session['user_id'] = None

	'''
	username: 'ivanov',
	lastname: 'Иванов',
	firstname: 'Иван',
	middlename: 'Иванович',
	date_of_birth: '01.01.1980',
	email: 'ivanov@yan.ru',
	'''

	data = {}

	return render_template('profile.html', data = data)


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
