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

from sqlalchemy_pagination import paginate

from regrr import app
from regrr import mail

import regrr.models as db
import regrr.helper_view as helper_view

APP_NAME = 'Реестр результатов анализов и&nbsp;тестирования'

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


menus_all = []
menus_all.append(make_menu_item('/feedback', 'Связь'))

"""
menus_all.append(
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
		)
	)
menus_all.append(
	make_menu_subitems(
		'Исходный шаблон Editorial', [
				make_menu_item('/static/_design/editorial/index.html', 'index'),
				make_menu_item('/static/_design/editorial/generic.html', 'generic'),
				make_menu_item('/static/_design/editorial/elements.html', 'elements'),
			]
		)
	)
"""



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

	#db_session = db.Session()
	#db_query = db_session.query(db.User).get(user_info.get('id'))
	#user = db_query.first()
	#db_session.add(user)
	#db_session.commit()

	# print('before_request ok:' + path)

#############################################################
@app.route('/')
def index():

	user_info = session.get(SESSION_KEY_USER)

	page_num = request.args.get('page', 1, type=int)
	page_size = 10

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
		#db_users = db_session.query(db.User).all()
		db_users = db_session.query(db.User)
		pagination = paginate(db_users, page_num, page_size)

		for db_user in pagination.items:
			users.append(db_user.toJson())
		
		data['users'] = users
		jpagination = helper_view.pagination_ext(pagination, page_num, page_size, 'index')
		data['pagination'] = jpagination


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
		'menus': menus,
		'pagination': jpagination
	}

	str = render_template('index.html', server = server)
	return str

#############################################################
@app.route('/2')
def index2():

	user_info = session.get(SESSION_KEY_USER)

	page_num = request.args.get('page', 1, type=int)
	page_size = 10

APP_NAME

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
		#db_users = db_session.query(db.User).all()
		db_users = db_session.query(db.User)
		pagination = paginate(db_users, page_num, page_size)

		for db_user in pagination.items:
			users.append(db_user.toJson())
		
		data['users'] = users
		jpagination = helper_view.pagination_ext(pagination, page_num, page_size, 'index')
		data['pagination'] = jpagination


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
		'menus': menus,
		'pagination': jpagination
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

	result.date_of_last_visit = datetime.utcnow()
	db_session.commit()


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

@app.route("/profile", methods=['GET'])
def profile():

	user_info = session.get(SESSION_KEY_USER)

	title = 'Профиль'
	menus = []
	data = {}
	isAdmin = False

	username = user_info.get('username')
	user_role = user_info.get('role')

	db_session = db.Session()
	db_query = db_session.query(db.User).filter(
		db.User.id == user_info.get('id')
		)
	db_query = db_query.first()

	if user_role == db.UserRole.ADMIN:
		isAdmin = True
		menus = menus_admin
	else:
		menus = menus_user


	# data['username'] = username
	data = db_query.toJson()
	data = 'data = ' + json.dumps(data, indent=4,  ensure_ascii=False) + ';'
	server = {
		'title': title,
		'username': username,
		'isAdmin': isAdmin,
		'data': data,
		'menus': menus
	}

	return render_template('profile.html', server = server)

@app.route("/profile", methods=['POST'])
def profile_post():

	if not request.json:
		# abort(400)
		return jsonify({'result': False, 'errors': ['invalid json']})

	user_info = session.get(SESSION_KEY_USER)

	db_session = db.Session()
	db_query = db_session.query(db.User).get(user_info.get('id'))

	db_query.lastname = request.json.get('lastname', '-')
	db_query.firstname = request.json.get('firstname', '-')
	db_query.middlename = request.json.get('middlename', '-')

	db_query.position = request.json.get('position', '-')
	db_query.email = request.json.get('email', '-')
	
	db_session.commit()

	return jsonify({'result': True})

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

AnalysisTypes = [
	db.AnalysisType.Тест_NEWS,
	db.AnalysisType.Тест_VTE
]

def make_nbsp(text):
	return text.replace(' ', '&nbsp;')

def make_breadcrumb(text, href = None):
	return { 'text': text, 'href': href }

def make_prevnext(prev_href = None, prev_title = None, next_href = None, next_title = None):
	prevnext = {}

	if prev_href:
		prev = {}
		prev['href'] = prev_href
		prev['title'] = prev_title
		prevnext['prev'] = prev

	if next_href:
		next = {}
		next['href'] = next_href
		next['title'] = next_title
		prevnext['next'] = next

	return prevnext

################################################################
@app.route('/patient/<patient_id>', methods=['GET'])
def patient_view(patient_id):

	user_info = session.get(SESSION_KEY_USER)
	user_role = user_info.get('role')
	if user_role != db.UserRole.USER:
		exceptions.abort(403)

	server = {
		'username': user_info.get('username'),
		'menus': menus_user
	}
	data = {}

	prevnext = None
	breadcrumbs = []
	breadcrumbs.append(make_breadcrumb('Пациенты', url_for('index')))

	db_session = db.Session()
	db_patient = db_session.query(db.Patient).filter(
		db.Patient.id == patient_id
		)
	db_patient = db_patient.first()
	
	if not db_patient:
		title = "Пациент, #%s, не найден!" % patient_id
		server['isOk'] = False
		server['title'] = title
		breadcrumbs.append(make_breadcrumb(title))
		server['prevnext'] = make_prevnext()
	else:
		title = "%s (#%s)" % (db_patient.getFullname(), patient_id)
		server['isOk'] = True
		server['title'] = title
		breadcrumbs.append(make_breadcrumb(make_nbsp(title)))

		server['patient'] = db_patient.toJson()
		data = db_patient.toJson()

		analysis_types = []
		for item in AnalysisTypes:
			analysis_types.append({
					'id': int(item),
					'text':  db.AnalysisTypeStr[item]
				})

		server['analysis_types'] = analysis_types

		db_query = db_session.query(db.Patient).filter(
			db.Patient.id < patient_id
			).order_by(db.Patient.id.desc()).first()

		prev_href = None
		prev_title = None
		if db_query:
			prev_href = url_for('patient_view', patient_id=db_query.id)
			prev_title = db_query.getFullname()


		db_query = db_session.query(db.Patient).filter(
			db.Patient.id > patient_id
			).order_by(db.Patient.id.asc()).first()

		next_href = None
		next_title = None
		if db_query:
			next_href = url_for('patient_view', patient_id=db_query.id)
			next_title = db_query.getFullname()

		server['prevnext'] = make_prevnext(prev_href, prev_title, next_href, next_title)

	data = 'data = ' + json.dumps(data, indent=4,  ensure_ascii=False) + ';'
	server['data'] = data
	server['breadcrumbs'] = breadcrumbs

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
	department = request.form.get('department')
	#email = request.form.get('email')
	diagnosis = request.form.get('diagnosis')

	if not date_of_birth:
		date_of_birth = '01.01.1900'

	patient = db.Patient(lastname, firstname, middlename, date_of_birth, department, diagnosis)

	db_session = db.Session()
	db_session.add(patient)
	db_session.commit()

	return redirect('/')

################################################################

@app.route('/patient/<patient_id>/analysis_type/<analysis_type>/analysis', methods=['GET'])
def patient_analysis_type_analyzes_viewer(patient_id, analysis_type):
	"""Просмотр анализов заданного типа"""

	user_info = session.get(SESSION_KEY_USER)
	user_role = user_info.get('role')
	if user_role != db.UserRole.USER:
		exceptions.abort(403)

	analysis_type = int(analysis_type)

	server = {}
	server['patient_id'] = patient_id
	server['analysis_type'] = analysis_type
	server['username'] = user_info.get('username')
	server['menus'] = menus_user

	breadcrumbs = []
	breadcrumbs.append(make_breadcrumb('Пациенты', url_for('index')))

	data = {}

	db_session = db.Session()
	db_patient = db_session.query(db.Patient).filter(
		db.Patient.id.in_([patient_id])
		)
	db_patient = db_patient.first()
	
	if not db_patient:
		title = "Пациент, #%s, не найден!" % patient_id
		server['isOk'] = False
		server['title'] = title
		breadcrumbs.append(make_breadcrumb(make_nbsp(title)))
	else:
		title = "%s (#%s)" % (db_patient.getFullname(), patient_id)
		server['isOk'] = True
		server['title'] = title
		server['analysis_type_str'] = db.AnalysisTypeStr.get(analysis_type)
		server['patient'] = db_patient

		breadcrumbs.append(make_breadcrumb(make_nbsp(title), url_for('patient_view', patient_id=patient_id)))
		breadcrumbs.append(make_breadcrumb(make_nbsp(db.AnalysisTypeStr.get(analysis_type))))

		db_query = db_session.query(db.Analysis, db.User.lastname, db.User.firstname, db.User.middlename).filter(
			#db.Analysis.type.in_([analysis_type]),
			#db.Analysis.patient_id.in_([patient_id]),
			db.Analysis.type == analysis_type,
			db.Analysis.patient_id == patient_id,
			db.Analysis.user_id == db.User.id
		).order_by(db.Analysis.id.desc())

		janalyzes = []
		for db_item in db_query:
			jAnalysis = db_item.Analysis.toJson()
			jAnalysis['user'] = db.makeLastnameAndInitials(db_item.lastname, db_item.firstname, db_item.middlename)
			janalyzes.append(jAnalysis)

		#data = db_patient.toJson()
		data['patient_id'] = patient_id
		data['analysis_type'] = analysis_type
		data['analyzes'] = janalyzes


	data = 'data = ' + json.dumps(data, indent=4,  ensure_ascii=False) + ';'
	server['data'] = data
	server['breadcrumbs'] = breadcrumbs

	str = render_template('analysis_type.html', server = server)
	return str


@app.route('/patient/<patient_id>/analysis_type/<analysis_type>/analysis/<analysis_id>', methods=['GET'])
def patient_analysis_type_analysis_viewer(patient_id, analysis_type, analysis_id):
	"""Просмотр анализа с фильтрацией по типам"""

	user_info = session.get(SESSION_KEY_USER)
	user_role = user_info.get('role')
	if user_role != db.UserRole.USER:
		exceptions.abort(403)

	analysis_type = int(analysis_type)

	server = {}
	server['patient_id'] = patient_id
	server['analysis_type'] = analysis_type
	server['analysis_id'] = analysis_id
	server['username'] = user_info.get('username')
	server['menus'] = menus_user

	breadcrumbs = []
	breadcrumbs.append(make_breadcrumb('Пациенты', url_for('index')))

	data = {}

	db_session = db.Session()
	db_patient = db_session.query(db.Patient).filter(
		db.Patient.id.in_([patient_id])
		)
	db_patient = db_patient.first()
	
	if not db_patient:
		title = "Пациент, #%s, не найден!" % patient_id
		server['isOk'] = False
		server['title'] = title
		breadcrumbs.append(make_breadcrumb(make_nbsp(title)))
	else:
		title = "%s (#%s)" % (db_patient.getFullname(), patient_id)
		server['isOk'] = True
		server['title'] = title
		server['analysis_type_str'] = db.AnalysisTypeStr.get(analysis_type)
		server['patient'] = db_patient

		db_query = db_session.query(db.Analysis, db.User.lastname, db.User.firstname, db.User.middlename).filter(
			#db.Analysis.type.in_([analysis_type]),
			#db.Analysis.patient_id.in_([patient_id]),
			db.Analysis.id == analysis_id,
			db.Analysis.type == analysis_type,
			db.Analysis.patient_id == patient_id,
			db.Analysis.user_id == db.User.id
		).first()

		if db_query:
			data = db_query.Analysis.toJson()
			data['user'] = db.makeLastnameAndInitials(db_query.lastname, db_query.firstname, db_query.middlename)
			data['analysis_type'] = analysis_type


		breadcrumbs.append(make_breadcrumb(make_nbsp(title), url_for('patient_view', patient_id=patient_id)))
		breadcrumbs.append(make_breadcrumb(make_nbsp(db.AnalysisTypeStr.get(analysis_type)),
			url_for('patient_analysis_type_analyzes_viewer', patient_id=patient_id, analysis_type=analysis_type)))
		breadcrumbs.append(make_breadcrumb(make_nbsp('#%s' % analysis_id)))


	data = 'data = ' + json.dumps(data, indent=4,  ensure_ascii=False) + ';'
	server['data'] = data
	server['breadcrumbs'] = breadcrumbs

	str = render_template('analysis_type_analysis.html', server = server)
	return str


@app.route('/patient/<patient_id>/analysis_type/<analysis_type>/analysis_add', methods=['GET'])
def patient_analysis_type_analysis_add(patient_id, analysis_type):
	"""Добавить анализ (форма)"""

	user_info = session.get(SESSION_KEY_USER)
	user_role = user_info.get('role')
	if user_role != db.UserRole.USER:
		exceptions.abort(403)

	analysis_type = int(analysis_type)

	server = {
		'patient_id': patient_id,
		'analysis_type': analysis_type,
		'username': user_info.get('username'),
		'menus': menus_user
	}
	data = {}

	db_session = db.Session()
	db_patient = db_session.query(db.Patient).filter(
		db.Patient.id.in_([patient_id])
		)
	db_patient = db_patient.first()
	
	if not db_patient:
		server['isOk'] = False
		server['title'] = "Пациент, #%s, не найден!" % id
	elif analysis_type not in AnalysisTypes:
		server['isOk'] = False
		server['title'] = "Данный анализ не реализован"
	else:
		server['isOk'] = True
		server['title'] = "%s %s %s (#%s)" % (db_patient.lastname, db_patient.firstname, db_patient.middlename, patient_id)
		server['analysis_type_str'] = db.AnalysisTypeStr.get(analysis_type)
		server['patient'] = db_patient

		data['patient_id'] = patient_id
		data['analysis_type'] = analysis_type

	data = 'data = ' + json.dumps(data, indent=4,  ensure_ascii=False) + ';'
	server['data'] = data

	str = ''
	if analysis_type == db.AnalysisType.Тест_NEWS:
		str = render_template('analysis_add.html', server = server)
	elif analysis_type == db.AnalysisType.Тест_VTE:
		str = render_template('analysis_add_6.html', server = server)
	
	return str

@app.route('/patient/<patient_id>/analysis_type/<analysis_type>/analysis_add', methods=['POST'])
def patient_analysis_type_analysis_add_post(patient_id, analysis_type):
	"""Добавить анализ (данные)"""

	if not request.json:
		abort(400)

	# patient_id = int(request.json.get('patient_id'))
	# analysis_type = int(request.json.get('analysis_type'))
	result = request.json.get('result')

	data = {}
	data['analysis_type'] = analysis_type
	data['points'] = request.json.get('points')
	data['isRed'] = request.json.get('isRed')
	data['items'] = request.json.get('items')
	data = json.dumps(data)
	
	if not patient_id or patient_id == '':
		abort(400)

	user_info = session.get(SESSION_KEY_USER)

	user_id = user_info.get('id')

	db_session = db.Session()
	
	analysis = db.Analysis(user_id, patient_id, analysis_type, result, data)
	db_session.add(analysis)
	db_session.commit()

	#result = query.first() == None
	result = True
	return jsonify({'result': result})



@app.route('/patient/<patient_id>/analysis/<analysis_id>', methods=['GET'])
def patient_analysis_viewer(patient_id, analysis_id):
	"""Просмотр анализа по id (Не реализовано)"""
	return 'Не реализовано'

import json

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
@app.route('/service_app_info')
def test_system():
	t = app
	t = dir(app)
	return jsonify(t)

# import inspect
from flask import escape

@app.route('/service_app_routes')
def routes():
	'''Возвравщает список url-маршрутов'''
	rules = []

	# mm = inspect.getmembers(app.url_map, inspect.ismethod)
	# rr = app.url_map.iter_rules()

	for item in app.url_map._rules_by_endpoint.items():
		rule = item[1][0].rule
		methods = item[1][0].methods
		methods = ', '.join(sorted(methods))
		endpoint = item[0]

		route = '{:40s} {:25s} {}'.format(endpoint, methods, escape(rule))
		rules.append(route)

	'''
	list = []
	sort_by_rule = operator.itemgetter(2)
	for endpoint, methods, rule in sorted(rules, key=sort_by_rule):
		route = '{:50s} {:25s} {}'.format(endpoint, methods, rule)
		list.append(route)
	'''

	str = '<pre>' + '\n'.join(rules) + '</pre>'
	return str
