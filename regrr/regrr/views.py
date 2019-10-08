"""
Routes and views for the flask application.
"""

import json

import pdfkit

from sqlalchemy import or_

from datetime import datetime
from dateutil import parser

from flask import redirect
from flask import session
from flask import request
from flask import url_for
from flask import abort
from flask import jsonify
from flask import make_response

import werkzeug.exceptions as exceptions
from sqlalchemy_pagination import paginate

from regrr import app
from regrr import mail

import regrr.models as db
import regrr.helper_view as helper_view

import regrr.analisis as analisis_rules


SESSION_KEY_USER = 'user'
APP_NAME = 'Реестр результатов анализов и&nbsp;тестирования'

helper_view.PageData.app_name = APP_NAME

#############################################################
def int_no_exc(s):
	try:
		return int(s)
	except ValueError:
		return 0

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



menus_all = []
menus_all.append(helper_view.PageData.make_menu_item('/feedback', 'Связь'))

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
	helper_view.PageData.make_menu_item('/', 'Пользователи')
	]
menus_admin.extend(menus_all)


menus_user = [
	helper_view.PageData.make_menu_item('/', 'Пациенты'),
	helper_view.PageData.make_menu_item('/archive', 'Архив')
	]
menus_user.extend(menus_all)


pageDataRoles = {
	db.UserRole.ADMIN: {
		'menus': menus_admin,
		'style_ext': '_red'
	},
	db.UserRole.USER: {
		'menus': menus_user,
		'style_ext': ''
	}
}

#pageDataRoles[user_role]

#############################################################
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

	username = user_info.get('username')
	user_role = user_info.get('role')

	if user_role == db.UserRole.ADMIN:

		pageData = helper_view.PageData('Пользователи', username, menus_admin, menucur='/', style_ext='_red')
		pageData.add_breadcrumb(pageData.title)

		server = pageData.to_dict()
		server['isAdmin'] = True

		data = {}
		data['users_offset'] = (page_num - 1) * page_size

		with db.session_scope() as db_session:
			db_users = db_session.query(db.User)
			pagination = paginate(db_users, page_num, page_size)

			users = []
			for db_user in pagination.items:
				users.append(db_user.toJson())

			data['users'] = users
			server['pagination'] = helper_view.pagination_ext(pagination, page_num, page_size, 'index')

		server['data'] = helper_view.data_to_json(data)
		str = helper_view.render_template_ext('index.html', server = server)
		return str


	elif user_role == db.UserRole.USER:

		pageData = helper_view.PageData('Пациенты', username, menus_user, menucur='/')
		pageData.add_breadcrumb(pageData.title)

		server = pageData.to_dict()
		server['isAdmin'] = False

		data = {}
		data['patients_offset'] = (page_num - 1) * page_size

		with db.session_scope() as db_session:
			db_patients = db_session.query(db.Patient).filter(db.Patient.status != db.PatientStatus.ARCHIVE)
			pagination = paginate(db_patients, page_num, page_size)

			patients = []
			for db_patient in pagination.items:
				patients.append(db_patient.toJson())

			data['patients'] = patients
			server['pagination'] = helper_view.pagination_ext(pagination, page_num, page_size, 'index')
		
		server['data'] = helper_view.data_to_json(data)
		str = helper_view.render_template_ext('index.html', server = server)
		return str

	abort(500)


#############################################################
@app.route('/login', methods=['GET'])
def login():
	next = request.referrer or ''
	str = helper_view.render_template_ext('login.html', next = next)
	return str

################################################################
@app.route('/login', methods=['POST'])
def login_post():
	username = request.form['username']
	password = request.form['password']
	remember = bool(request.form.get('remember'))
	next = request.form['next']

	user_lite = None

	with db.session_scope() as db_session:
		query = db_session.query(db.User).filter(
			db.User.username.in_([username]),
			db.User.password.in_([password])
			)
		result = query.first()
		if result:
			result.date_of_last_visit = datetime.utcnow()
			user_lite = {
				'id': result.id,
				'username': result.username,
				'role': result.role
			}
	
	if not user_lite:
		return helper_view.render_template_ext('login.html',
			display_error = True,
			password = password,
			username = username,
			remember = 'checked' if remember else '',
			next = next)

	session[SESSION_KEY_USER] = user_lite
	session.permanent = remember
	session.modified = True

	path = (next or url_for('index'))
	return redirect(path)


################################################################
@app.route("/logout")
def logout():
	session[SESSION_KEY_USER] = None
	session.permanent = False
	session.modified = True
	return redirect('/')


################################################################
@app.route("/profile", methods=['GET'])
def profile():

	user_info = session.get(SESSION_KEY_USER)

	username = user_info.get('username')
	user_role = user_info.get('role')

	pageData = helper_view.PageData('Профиль', username, menus_user)
	pageData.add_breadcrumb(pageData.title)

	isAdmin = False
	if user_role == db.UserRole.ADMIN:
		isAdmin = True
		pageData.menus = menus_admin
		pageData.style_ext = '_red'

	server = pageData.to_dict()
	server['isAdmin'] = isAdmin
	data = {}

	with db.session_scope() as db_session:
		db_query = db_session.query(db.User).filter(
			db.User.id == user_info.get('id')
			)
		db_query = db_query.first()
		data = db_query.toJson()

	server['data'] = helper_view.data_to_json(data)
	str = helper_view.render_template_ext('profile.html', server = server)
	return str

################################################################
def result_true(data=None, messages=None):
	result = { 'result': True }
	if data:
		result['data'] = data
	if messages:
		result['messages'] = messages
	return jsonify(result)

def result_false(errors):
	result = { 'result': False }
	if errors:
		result['errors'] = errors
	return jsonify(result)

################################################################
@app.route("/profile", methods=['POST'])
def profile_post():

	if not request.json:
		# abort(400)
		return result_false(['invalid json'])

	user_info = session.get(SESSION_KEY_USER)

	with db.session_scope() as db_session:
		db_query = db_session.query(db.User).get(user_info.get('id'))

		db_query.lastname = request.json.get('lastname', '-')
		db_query.firstname = request.json.get('firstname', '-')
		db_query.middlename = request.json.get('middlename', '-')
		db_query.position = request.json.get('position', '-')
		db_query.email = request.json.get('email', '-')
	
	return result_true()


################################################################
@app.route("/profile_change_password", methods=['POST'])
def profile_change_password_post():

	if not request.json:
		# abort(400)
		return result_false(['invalid json'])

	user_info = session.get(SESSION_KEY_USER)

	password_old = request.json['password_old']
	password_new = request.json['password_new']

	if password_new == '':
		return result_false(['Пароль не может быть пустым!'])

	if password_new == password_old:
		return result_false(['Старый и новый пароли не должны совпадать!'])

	errors = []

	with db.session_scope() as db_session:
		db_query = db_session.query(db.User).get(user_info.get('id'))
		if (db_query.password != password_old):
			errors.append('Не правильный старый пароль!')
		else:
			db_query.password = password_new
	
	if len(errors):
		return result_false(errors)

	return result_true();

################################################################
@app.route("/search", methods=['GET'])
def search():

	user_info = session.get(SESSION_KEY_USER)

	username = user_info.get('username')
	user_role = user_info.get('role')

	pageData = helper_view.PageData('Поиск', username, menus_user)
	pageData.add_breadcrumb(pageData.title)

	isAdmin = False
	if user_role == db.UserRole.ADMIN:
		isAdmin = True
		pageData.menus = menus_admin
		pageData.style_ext = '_red'

	server = pageData.to_dict()
	server['isAdmin'] = isAdmin
	data = {}

	with db.session_scope() as db_session:
		db_query = db_session.query(db.User).filter(
			db.User.id == user_info.get('id')
			)
		db_query = db_query.first()
		data = db_query.toJson()

	server['data'] = helper_view.data_to_json(data)
	str = helper_view.render_template_ext('search.html', server = server)
	return str

################################################################
def search_result(user_role, query):
	data = {}
	if not query or query == '':
		return data

	data['query'] = query
	#query = '%' + query.lower() + '%';
	query = '%' + query + '%';
	results = []

	if user_role == db.UserRole.ADMIN:
		with db.session_scope() as db_session:
			db_query = db_session.query(db.User).filter(
				or_(db.User.id.ilike(query),
					db.User.firstname.ilike(query),
					db.User.lastname.ilike(query),
					db.User.middlename.ilike(query)
					)
				)
			db_query = db_query.all()
			for db_item in db_query:
				results.append({
					'text': "%s (#%s)" % (db_item.getFullname(), db_item.username),
					'url': url_for('user_view', username=db_item.username)
					})
		data['results'] = results
		return data

	if user_role == db.UserRole.USER:
		with db.session_scope() as db_session:
			db_query = db_session.query(db.Patient).filter(
				or_(db.Patient.id.ilike(query),
					db.Patient.firstname.ilike(query),
					db.Patient.lastname.ilike(query),
					db.Patient.middlename.ilike(query)
					)
				)
			db_query = db_query.all()
			for db_item in db_query:
				results.append({
					'text': "%s (#%s)" % (db_item.getFullname(), db_item.id),
					'url': url_for('patient_view', patient_id=db_item.id)
					})
		data['results'] = results
		return data

	return data


@app.route("/search", methods=['POST'])
def search_post():

	query = request.form.get('query')

	user_info = session.get(SESSION_KEY_USER)

	username = user_info.get('username')
	user_role = user_info.get('role')

	pageData = helper_view.PageData('Поиск', username, menus_user)
	pageData.add_breadcrumb(pageData.title)

	if user_role == db.UserRole.ADMIN:
		pageData.menus = menus_admin
		pageData.style_ext = '_red'
		server = pageData.to_dict()
	elif user_role == db.UserRole.USER:
		server = pageData.to_dict()
	else:
		abort(500)

	data = search_result(user_role, query)
	server['data'] = helper_view.data_to_json(data)
	str = helper_view.render_template_ext('search.html', server = server)
	return str


################################################################
@app.route('/user/<username>', methods=['GET'])
def user_view(username):

	user_info = session.get(SESSION_KEY_USER)
	user_role = user_info.get('role')
	if user_role != db.UserRole.ADMIN:
		exceptions.abort(403)

	pageData = helper_view.PageData(username, user_info.get('username'), menus_admin, menucur='/', style_ext='_red')
	pageData.add_breadcrumb('Пользователи', '/')
	pageData.add_breadcrumb(pageData.title)

	isOk = False
	data = {}

	with db.session_scope() as db_session:
		db_user = db_session.query(db.User).filter(
			db.User.username == username
			)
		db_user = db_user.first()

		if db_user:
			isOk = True
			data = db_user.toJson()

			db_query = db_session.query(db.User).filter(
				db.User.id < db_user.id
				).order_by(db.User.id.desc()).first()
			if db_query:
				pageData.set_prev(url_for('user_view', username=db_query.username), db_query.getFullname())

			db_query = db_session.query(db.User).filter(
				db.User.id > db_user.id
				).order_by(db.User.id.asc()).first()
			if db_query:
				pageData.set_next(url_for('user_view', username=db_query.username), db_query.getFullname())

	server = pageData.to_dict()
	server['isOk'] = isOk
	server['data'] = helper_view.data_to_json(data)

	str = helper_view.render_template_ext('user.html', server = server)
	return str

################################################################
@app.route('/user_add', methods=['GET'])
def user_add():

	user_info = session.get(SESSION_KEY_USER)
	user_role = user_info.get('role')
	if user_role != db.UserRole.ADMIN:
		exceptions.abort(403)

	username = user_info.get('username')

	pageData = helper_view.PageData('Добавить нового пользователя', username, menus_admin, menucur='/', style_ext='_red')
	pageData.add_breadcrumb('Пользователи', '/')
	pageData.add_breadcrumb(pageData.title)

	server = pageData.to_dict()

	data = {}
	data['username'] = username
	server['data'] = helper_view.data_to_json(data)

	str = helper_view.render_template_ext('user_add.html', server = server)
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

	with db.session_scope() as db_session:
		db_session.add(user)

	return redirect('/')

AnalysisTypes = [
	db.AnalysisType.Биохимические_исследования,
	db.AnalysisType.Гемостаз,
	db.AnalysisType.Клинический_анализ_крови,
	db.AnalysisType.Общий_анализ_мочи,
	db.AnalysisType.Тест_NEWS,
	db.AnalysisType.Тест_VTE,
	db.AnalysisType.Дополнительно
]

from dateutil.relativedelta import relativedelta

def yearsago(years, from_date=None):
    if from_date is None:
        from_date = datetime.now()
    return from_date - relativedelta(years=years)

################################################################
@app.route('/patient/<patient_id>', methods=['GET'])
def patient_view(patient_id):

	user_info = session.get(SESSION_KEY_USER)
	user_role = user_info.get('role')
	if user_role != db.UserRole.USER:
		exceptions.abort(403)

	#pageData = helper_view.PageData(None, user_info.get('username'), menus_user, menucur='/')
	pageData = helper_view.PageData(None, user_info.get('username'), menus_user)
	pageData.add_breadcrumb('Пациенты', '/')

	j_patient = None
	patient_fullname = None

	with db.session_scope() as db_session:
		db_patient = db_session.query(db.Patient).filter(
			db.Patient.id == patient_id
			)
		db_patient = db_patient.first()
		if db_patient:
			j_patient = db_patient.toJson(True)
			patient_fullname = db_patient.getFullname()

			db_query = db_session.query(db.Patient).filter(
				db.Patient.id < patient_id
				).order_by(db.Patient.id.desc()).first()
			if db_query:
				pageData.set_prev(url_for('patient_view', patient_id=db_query.id), db_query.getFullname())
			else:
				pageData.set_prev()

			db_query = db_session.query(db.Patient).filter(
				db.Patient.id > patient_id
				).order_by(db.Patient.id.asc()).first()
			if db_query:
				pageData.set_next(url_for('patient_view', patient_id=db_query.id), db_query.getFullname())
			else:
				pageData.set_next()


	if not j_patient:
		pageData.title = patient_id
		pageData.add_breadcrumb(pageData.title)
		pageData.message = '<h2>Пациент, <b>"#%s"</b>, не найден!</h2>' % patient_id
		str = helper_view.render_template_ext('page_message.html', server=pageData.to_dict())
		return str


	pageData.title = "%s (#%s)" % (patient_fullname, patient_id)
	pageData.add_breadcrumb(pageData.title)
	server = pageData.to_dict()

	server['isOk'] = True

	date_of_birth = j_patient['date_of_birth']
	#date_of_birth2 = parser.parse(date_of_birth)
	"""
	date_of_birth2 = datetime.strptime(date_of_birth, '%d.%m.%Y')
	
	now = datetime.now()
	delta = now - date_of_birth2

	d = relativedelta(now, date_of_birth2)

	#yearsago(date_of_birth2.year)
	#j_patient['age'] = delta.years

	j_patient['date_of_birth'] = date_of_birth2

	j_patient['date_of_birth_str'] = date_of_birth2.strftime('%d.%m.%Y')
	"""
	server['patient'] = j_patient

	analysis_types = []
	for item in AnalysisTypes:
		analysis_types.append({
				'id': int(item),
				'text':  db.AnalysisTypeStr[item]
			})

	server['analysis_types'] = analysis_types

	server['PatientStatus'] = db.PatientStatus

	data = {}
	#data['username'] = username
	data['patient'] = j_patient
	server['data'] = helper_view.data_to_json(data)

	str = helper_view.render_template_ext('patient.html', server = server)
	return str


################################################################
@app.route('/patient_add', methods=['GET'])
def patient_add():

	user_info = session.get(SESSION_KEY_USER)
	user_role = user_info.get('role')
	if user_role != db.UserRole.USER:
		exceptions.abort(403)

	username = user_info.get('username')

	pageData = helper_view.PageData('Добавить нового пациента', username, menus_user, menucur='/')
	pageData.add_breadcrumb('Пациенты', '/')
	pageData.add_breadcrumb(pageData.title)
	server = pageData.to_dict()

	str = helper_view.render_template_ext('patient_add.html', server = server)
	return str


################################################################
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
	gender = request.form.get('gender', int(db.Gender.NOT_SPECIFIED))
	date_of_birth = request.form.get('date_of_birth')
	department = request.form.get('department')
	#email = request.form.get('email')
	diagnosis = request.form.get('diagnosis')

	if not date_of_birth:
		date_of_birth = '01.01.1900'

	patient_id = None
	patient = db.Patient(lastname, firstname, middlename, gender, date_of_birth, department, diagnosis)
	with db.session_scope() as db_session:
		db_session.add(patient)
		db_session.commit()
		patient_id = patient.id

	return redirect(url_for('patient_view', patient_id=patient_id))

sorts = {}
def addSortField(dbColumn):
	name = str(dbColumn)
	sorts[name] = [dbColumn.asc(), db.Analysis.id.asc()]
	sorts[name + '__desc'] = [dbColumn.desc(), db.Analysis.id.desc()]
	
sorts['date_of_creation'] = [db.Analysis.date_of_creation.asc(), db.Analysis.id.asc()]
sorts['date_of_creation__desc'] = [db.Analysis.date_of_creation.desc(), db.Analysis.id.desc()]

sorts['date_receipt_example'] = [db.Analysis.date_receipt_example.asc(), db.Analysis.id.asc()]
sorts['date_receipt_example__desc'] = [db.Analysis.date_receipt_example.desc(), db.Analysis.id.desc()]

sorts['date_delivery_biomaterial'] = [db.Analysis.date_delivery_biomaterial.asc(), db.Analysis.id.asc()]
sorts['date_delivery_biomaterial__desc'] = [db.Analysis.date_delivery_biomaterial.desc(), db.Analysis.id.desc()]

sorts['date_completion'] = [db.Analysis.date_completion.asc(), db.Analysis.id.asc()]
sorts['date_completion__desc'] = [db.Analysis.date_completion.desc(), db.Analysis.id.desc()]
sort_def = sorts['date_of_creation__desc']

################################################################
@app.route('/patient/<patient_id>/analysis_type/<analysis_type>/analysis', methods=['GET'])
def patient_analysis_type_analyzes_viewer(patient_id, analysis_type):
	"""Просмотр анализов заданного типа"""

	user_info = session.get(SESSION_KEY_USER)
	user_role = user_info.get('role')
	if user_role != db.UserRole.USER:
		exceptions.abort(403)

	page_num = request.args.get('page', 1, type=int)
	page_size = 10

	sort = request.args.get('sort')
	sort = sorts.get(sort, sort_def)

	analysis_type_int = int_no_exc(analysis_type)
	analysis_type_str = db.AnalysisTypeStr.get(analysis_type_int)

	patient_fullname = None
	janalyzes = None
	jpagination = None
	
	with db.session_scope() as db_session:
		db_patient = db_session.query(db.Patient).filter(
			db.Patient.id == patient_id
			)
		db_patient = db_patient.first()
		if db_patient:
			patient_fullname = db_patient.getFullname()

			if analysis_type_str:
				db_query = db_session.query(db.Analysis, db.User.lastname, db.User.firstname, db.User.middlename).filter(
					db.Analysis.type == analysis_type,
					db.Analysis.patient_id == patient_id,
					db.Analysis.user_id == db.User.id
				).order_by(*sort)

				pagination = paginate(db_query, page_num, page_size)

				janalyzes = []
				for db_item in pagination.items:
					jAnalysis = db_item.Analysis.toJson()
					jAnalysis['user'] = db.make_lastname_and_initials(db_item.lastname, db_item.firstname, db_item.middlename)
					janalyzes.append(jAnalysis)

				jpagination = helper_view.pagination_ext(pagination, page_num, page_size,
					'patient_analysis_type_analyzes_viewer', patient_id=patient_id, analysis_type=analysis_type)


	username = user_info.get('username')
	pageData = helper_view.PageData(None, username, menus_user, menucur='/')
	pageData.add_breadcrumb('Пациенты', '/')

	if not patient_fullname:
		pageData.title = "#%s" % patient_id
		pageData.add_breadcrumb(pageData.title)
		if analysis_type_str:
			pageData.add_breadcrumb(analysis_type_str)
		else:
			pageData.add_breadcrumb('Неизвестный анализ #%s' % analysis_type)

		pageData.message = '<h2>Пациент, <b>"#%s"</b>, не найден!</h2>' % patient_id
		str = helper_view.render_template_ext('page_message.html', server=pageData.to_dict())
		return str


	patient_label = "%s (#%s)" % (patient_fullname, patient_id)
	pageData.add_breadcrumb(helper_view.str_nbsp(patient_label), url_for('patient_view', patient_id=patient_id))


	if not analysis_type_str:
		pageData.title = 'Неизвестный анализ #%s' % analysis_type
		pageData.add_breadcrumb(pageData.title)
		pageData.message = '<h2>Неизвестный анализ <b>"#%s"</b>!</h2>' % analysis_type
		str = helper_view.render_template_ext('page_message.html', server=pageData.to_dict())
		return str


	pageData.title = analysis_type_str
	pageData.add_breadcrumb(helper_view.str_nbsp(pageData.title))

	server = pageData.to_dict()

	#server['isOk'] = True
	#server['analysis_type_str'] = analysis_type_str

	server['patient_id'] = patient_id
	server['analysis_type'] = analysis_type
	server['pagination'] = jpagination

	data = {}
	data['patient_id'] = patient_id
	data['analysis_type'] = analysis_type
	data['analyzes'] = janalyzes
	data['analyzes_offset'] = (page_num - 1) * page_size

	settings = {}
	settings['is_hide_empty'] = True
	data['settings'] = settings

	if analysis_type_int == db.AnalysisType.Биохимические_исследования:
		data['tests'] = analisis_rules.tests_Биохимические_исследования
	elif analysis_type_int == db.AnalysisType.Гемостаз:
		data['tests'] = analisis_rules.tests_Гемостаз
	elif analysis_type_int == db.AnalysisType.Клинический_анализ_крови:
		data['tests'] = analisis_rules.tests_Клинический_анализ_крови
	elif analysis_type_int == db.AnalysisType.Общий_анализ_мочи:
		data['tests'] = analisis_rules.tests_Общий_анализ_мочи
	elif analysis_type_int == db.AnalysisType.Дополнительно:
		data['tests'] = analisis_rules.tests_Дополнительно


	server['data'] = helper_view.data_to_json(data)

	str = helper_view.render_template_ext('patient_analysis_type.html', server = server)
	return str


#############################################################
@app.route('/patient/<patient_id>/analysis_type/<analysis_type>/analysis/<analysis_id>', methods=['GET'])
def patient_analysis_type_analysis_viewer(patient_id, analysis_type, analysis_id):
	"""Просмотр анализа с фильтрацией по типам"""

	user_info = session.get(SESSION_KEY_USER)
	user_role = user_info.get('role')
	if user_role != db.UserRole.USER:
		exceptions.abort(403)

	page_num = request.args.get('page', 1, type=int)
	page_size = 10

	analysis_id_int = int_no_exc(analysis_id)
	analysis_type_int = int_no_exc(analysis_type)
	analysis_type_str = db.AnalysisTypeStr.get(analysis_type_int)

	patient_fullname = None
	data = None

	username = user_info.get('username')
	pageData = helper_view.PageData(None, username, menus_user, menucur='/')
	pageData.add_breadcrumb('Пациенты', '/')

	with db.session_scope() as db_session:
		db_patient = db_session.query(db.Patient).filter(
			db.Patient.id == patient_id
			)
		db_patient = db_patient.first()
		if db_patient:
			patient_fullname = db_patient.getFullname()

			if analysis_type_str:
				db_query = db_session.query(db.Analysis, db.User.lastname, db.User.firstname, db.User.middlename).filter(
					db.Analysis.id == analysis_id,
					db.Analysis.type == analysis_type,
					db.Analysis.patient_id == patient_id,
					db.Analysis.user_id == db.User.id
				).first()

				if db_query:
					data = db_query.Analysis.toJson()
					data['user'] = db.make_lastname_and_initials(db_query.lastname, db_query.firstname, db_query.middlename)
					data['analysis_type'] = analysis_type

					db_query = db_session.query(db.Analysis).filter(
						db.Analysis.id > analysis_id,
						db.Analysis.type == analysis_type,
						db.Analysis.patient_id == patient_id,
						db.Analysis.user_id == db.User.id
						).order_by(db.Analysis.id.asc()).first()
					if db_query:
						u = url_for('patient_analysis_type_analysis_viewer',
							patient_id=patient_id, analysis_type=analysis_type, analysis_id=db_query.id)
						pageData.set_prev(u)
					else:
						pageData.set_prev()


					db_query = db_session.query(db.Analysis).filter(
						db.Analysis.id < analysis_id,
						db.Analysis.type == analysis_type,
						db.Analysis.patient_id == patient_id,
						db.Analysis.user_id == db.User.id
						).order_by(db.Analysis.id.desc()).first()
					if db_query:
						u = url_for('patient_analysis_type_analysis_viewer',
							patient_id=patient_id, analysis_type=analysis_type, analysis_id=db_query.id)
						pageData.set_next(u)
					else:
						pageData.set_next()


	if not patient_fullname:
		pageData.title = "#%s" % patient_id
		pageData.add_breadcrumb(pageData.title)
		pageData.add_breadcrumb(analysis_type_str if analysis_type_str else 'Неизвестный анализ #%s' % analysis_type)
		pageData.add_breadcrumb('#%s' % analysis_id)
		server = pageData.to_dict()
		server['message'] = '<h2>Пациент, <b>"#%s"</b>, не найден!</h2>' % patient_id
		str = helper_view.render_template_ext('page_message.html', server = server)
		return str


	patient_label = "%s (#%s)" % (patient_fullname, patient_id)
	pageData.add_breadcrumb(helper_view.str_nbsp(patient_label), url_for('patient_view', patient_id=patient_id))


	if not analysis_type_str:
		pageData.title = "#%s" % patient_id
		pageData.add_breadcrumb(pageData.title)
		pageData.message = '<h2>Пациент, <b>"#%s"</b>, не найден!</h2>' % patient_id
		str = helper_view.render_template_ext('page_message.html', server = pageData.to_dict())
		return str


	analysis_type_url = url_for('patient_analysis_type_analyzes_viewer',
		patient_id=patient_id, analysis_type=analysis_type)

	pageData.add_breadcrumb(analysis_type_str, analysis_type_url)
	pageData.add_breadcrumb('#%s' % analysis_id)
	pageData.title = '%s #%s' % (analysis_type_str, analysis_id)


	if not data:
		server = pageData.to_dict()
		server['message'] = '<h2>%s, <b>"#%s"</b>, не найден!</h2>' % (analysis_type_str, analysis_id)
		str = helper_view.render_template_ext('page_message.html', server = server)
		return str

	if analysis_type_int == db.AnalysisType.Биохимические_исследования:
		data['tests'] = analisis_rules.tests_Биохимические_исследования
	elif analysis_type_int == db.AnalysisType.Гемостаз:
		data['tests'] = analisis_rules.tests_Гемостаз
	elif analysis_type_int == db.AnalysisType.Клинический_анализ_крови:
		data['tests'] = analisis_rules.tests_Клинический_анализ_крови
	elif analysis_type_int == db.AnalysisType.Общий_анализ_мочи:
		data['tests'] = analisis_rules.tests_Общий_анализ_мочи
	elif analysis_type_int == db.AnalysisType.Дополнительно:
		data['tests'] = analisis_rules.tests_Дополнительно

	settings = {}
	settings['is_hide_empty'] = True
	data['settings'] = settings

	server = pageData.to_dict()
	server['isOk'] = True
	server['data'] = helper_view.data_to_json(data)
	server['patient_id'] = patient_id
	server['analysis_type'] = analysis_type


	str = helper_view.render_template_ext('patient_analysis_type_analysis.html', server = server)
	return str


#############################################################
@app.route('/patient/<patient_id>/analysis_type/<analysis_type>/analysis_print/<analysis_id>', methods=['GET'])
def patient_analysis_type_analysis_print(patient_id, analysis_type, analysis_id):
	"""Просмотр версии анализа для печати с фильтрацией по типам"""

	user_info = session.get(SESSION_KEY_USER)
	user_role = user_info.get('role')
	if user_role != db.UserRole.USER:
		exceptions.abort(403)

	page_num = request.args.get('page', 1, type=int)
	page_size = 10

	analysis_id_int = int_no_exc(analysis_id)
	analysis_type_int = int_no_exc(analysis_type)
	analysis_type_str = db.AnalysisTypeStr.get(analysis_type_int)

	patient_fullname = None
	patient_lastname_and_initials = None
	patient_json = None
	data = None

	username = user_info.get('username')
	pageData = helper_view.PageData(None, username, menus_user, menucur='/')
	pageData.add_breadcrumb('Пациенты', '/')

	with db.session_scope() as db_session:
		db_patient = db_session.query(db.Patient).filter(
			db.Patient.id == patient_id
			)
		db_patient = db_patient.first()
		if db_patient:
			patient_fullname = db_patient.getFullname()
			patient_lastname_and_initials = db_patient.getLastnameAndInitials()
			patient_json = db_patient.toJson(True)

			if analysis_type_str:
				db_query = db_session.query(db.Analysis, db.User.lastname, db.User.firstname, db.User.middlename).filter(
					db.Analysis.id == analysis_id,
					db.Analysis.type == analysis_type,
					db.Analysis.patient_id == patient_id,
					db.Analysis.user_id == db.User.id
				).first()

				if db_query:
					data = db_query.Analysis.toJson()
					data['user'] = db.make_lastname_and_initials(db_query.lastname, db_query.firstname, db_query.middlename)
					data['analysis_type'] = analysis_type

					db_query = db_session.query(db.Analysis).filter(
						db.Analysis.id > analysis_id,
						db.Analysis.type == analysis_type,
						db.Analysis.patient_id == patient_id,
						db.Analysis.user_id == db.User.id
						).order_by(db.Analysis.id.asc()).first()
					if db_query:
						u = url_for('patient_analysis_type_analysis_viewer',
							patient_id=patient_id, analysis_type=analysis_type, analysis_id=db_query.id)
						pageData.set_prev(u)
					else:
						pageData.set_prev()


					db_query = db_session.query(db.Analysis).filter(
						db.Analysis.id < analysis_id,
						db.Analysis.type == analysis_type,
						db.Analysis.patient_id == patient_id,
						db.Analysis.user_id == db.User.id
						).order_by(db.Analysis.id.desc()).first()
					if db_query:
						u = url_for('patient_analysis_type_analysis_viewer',
							patient_id=patient_id, analysis_type=analysis_type, analysis_id=db_query.id)
						pageData.set_next(u)
					else:
						pageData.set_next()


	if not patient_fullname:
		pageData.title = "#%s" % patient_id
		pageData.add_breadcrumb(pageData.title)
		pageData.add_breadcrumb(analysis_type_str if analysis_type_str else 'Неизвестный анализ #%s' % analysis_type)
		pageData.add_breadcrumb('#%s' % analysis_id)
		server = pageData.to_dict()
		server['message'] = '<h2>Пациент, <b>"#%s"</b>, не найден!</h2>' % patient_id
		str = helper_view.render_template_ext('page_message.html', server = server)
		return str


	patient_label = "%s (#%s)" % (patient_fullname, patient_id)
	pageData.add_breadcrumb(helper_view.str_nbsp(patient_label), url_for('patient_view', patient_id=patient_id))


	if not analysis_type_str:
		pageData.title = "#%s" % patient_id
		pageData.add_breadcrumb(pageData.title)
		pageData.message = '<h2>Пациент, <b>"#%s"</b>, не найден!</h2>' % patient_id
		str = helper_view.render_template_ext('page_message.html', server = pageData.to_dict())
		return str


	analysis_type_url = url_for('patient_analysis_type_analyzes_viewer',
		patient_id=patient_id, analysis_type=analysis_type)

	pageData.add_breadcrumb(analysis_type_str, analysis_type_url)
	pageData.add_breadcrumb('#%s' % analysis_id)
	pageData.title = '%s #%s' % (analysis_type_str, analysis_id)


	if not data:
		server = pageData.to_dict()
		server['message'] = '<h2>%s, <b>"#%s"</b>, не найден!</h2>' % (analysis_type_str, analysis_id)
		str = helper_view.render_template_ext('page_message.html', server = server)
		return str

	server = pageData.to_dict()
	server['isOk'] = True
	server['patient'] = patient_json
	server['patient_id'] = patient_id
	server['patient_lastname_and_initials'] = patient_lastname_and_initials
	#server['patient_gender'] = patient_gender
	server['analysis_type'] = analysis_type
	server['analysis_type_str'] = analysis_type_str


	if analysis_type_int == db.AnalysisType.Биохимические_исследования:
		data['tests'] = analisis_rules.tests_Биохимические_исследования
	elif analysis_type_int == db.AnalysisType.Гемостаз:
		data['tests'] = analisis_rules.tests_Гемостаз
	elif analysis_type_int == db.AnalysisType.Клинический_анализ_крови:
		data['tests'] = analisis_rules.tests_Клинический_анализ_крови
	elif analysis_type_int == db.AnalysisType.Общий_анализ_мочи:
		data['tests'] = analisis_rules.tests_Общий_анализ_мочи
	elif analysis_type_int == db.AnalysisType.Дополнительно:
		data['tests'] = analisis_rules.tests_Дополнительно

	data['patient'] = patient_json
	data['analysis_type_str'] = analysis_type_str
	#server['data'] = data
	server['data'] = helper_view.data_to_json(data)


	str = helper_view.render_template_ext('patient_analysis_type_analysis_pdf.html', server = server)
	# str = str.encode("utf-8")
	return str

	wkhtmltopdf = os.path.join(app.root_path, 'bin\\wkhtmltox-0.12.5-1.mxe-cross-win64\\wkhtmltopdf.exe')
	configuration = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf)
	pdf = pdfkit.from_string(str, False, configuration=configuration)

	response = make_response(pdf)
	response.headers.set('Content-Type', 'application/pdf')
	response.headers.set('Content-Disposition', 'attachment', filename='analisis %s.pdf' % analysis_id)
	return response

#############################################################
@app.route('/patient/<patient_id>/analysis_type/<analysis_type>/analysis_add', methods=['GET'])
def patient_analysis_type_analysis_add(patient_id, analysis_type):
	"""Форма добавления анализа"""

	user_info = session.get(SESSION_KEY_USER)
	user_role = user_info.get('role')
	if user_role != db.UserRole.USER:
		exceptions.abort(403)

	analysis_type_int = int_no_exc(analysis_type)
	analysis_type_str = db.AnalysisTypeStr.get(analysis_type_int)

	patient_fullname = None
	
	with db.session_scope() as db_session:
		db_patient = db_session.query(db.Patient).filter(
			db.Patient.id == patient_id
			)
		db_patient = db_patient.first()
		if db_patient:
			patient_fullname = db_patient.getLastnameAndInitials()
	

	username = user_info.get('username')
	pageData = helper_view.PageData(None, username, menus_user, menucur='/')
	pageData.add_breadcrumb('Пациенты', '/')

	if not patient_fullname:
		pageData.title = "#%s" % patient_id
		pageData.add_breadcrumb(pageData.title)
		pageData.add_breadcrumb(analysis_type_str if analysis_type_str else 'Неизвестный анализ #%s' % analysis_type)
		pageData.add_breadcrumb('Новый')
		pageData.message = '<h2>Пациент, <b>"#%s"</b>, не найден!</h2>' % patient_id
		str = helper_view.render_template_ext('page_message.html', server = pageData.to_dict())
		return str


	patient_label = "%s (#%s)" % (patient_fullname, patient_id)
	pageData.add_breadcrumb(helper_view.str_nbsp(patient_label), url_for('patient_view', patient_id=patient_id))

	if not analysis_type_str:
		pageData.title = 'Неизвестный анализ #%s' % analysis_type
		pageData.add_breadcrumb(helper_view.str_nbsp(pageData.title))
		pageData.add_breadcrumb('Новый')
		pageData.message = '<h2>Неизвестный анализ <b>"#%s"</b>!</h2>' % analysis_type
		str = helper_view.render_template_ext('page_message.html', server = pageData.to_dict())
		return str

	analysis_type_url = url_for('patient_analysis_type_analyzes_viewer',
		patient_id=patient_id, analysis_type=analysis_type)
	pageData.add_breadcrumb(analysis_type_str, analysis_type_url)
	pageData.add_breadcrumb('Новый')
	pageData.title = "%s - Новый" % analysis_type_str

	server = pageData.to_dict()
	server['patient_id'] = patient_id
	server['analysis_type'] = analysis_type
	server['analysis_type_str'] = analysis_type_str

	data = {}
	data['patient_id'] = patient_id
	data['analysis_type'] = analysis_type
	data['analysis_str'] = analysis_type_str

	str = ''
	if analysis_type_int == db.AnalysisType.Биохимические_исследования:
		data['tests'] = analisis_rules.tests_Биохимические_исследования
		server['data'] = helper_view.data_to_json(data)
		str = helper_view.render_template_ext('patient_analysis_add_1.html', server = server)
	elif analysis_type_int == db.AnalysisType.Гемостаз:
		data['tests'] = analisis_rules.tests_Гемостаз
		server['data'] = helper_view.data_to_json(data)
		str = helper_view.render_template_ext('patient_analysis_add_1.html', server = server)
	elif analysis_type_int == db.AnalysisType.Клинический_анализ_крови:
		data['tests'] = analisis_rules.tests_Клинический_анализ_крови
		server['data'] = helper_view.data_to_json(data)
		str = helper_view.render_template_ext('patient_analysis_add_1.html', server = server)
	elif analysis_type_int == db.AnalysisType.Общий_анализ_мочи:
		data['tests'] = analisis_rules.tests_Общий_анализ_мочи
		server['data'] = helper_view.data_to_json(data)
		str = helper_view.render_template_ext('patient_analysis_add_1.html', server = server)
	elif analysis_type_int == db.AnalysisType.Биохимические_исследования:
		data['tests'] = analisis_rules.tests_Биохимические_исследования
		server['data'] = helper_view.data_to_json(data)
		str = helper_view.render_template_ext('patient_analysis_add_1.html', server = server)
	elif analysis_type_int == db.AnalysisType.Тест_NEWS:
		server['data'] = helper_view.data_to_json(data)
		str = helper_view.render_template_ext('patient_analysis_add_5.html', server = server)
	elif analysis_type_int == db.AnalysisType.Тест_VTE:
		server['data'] = helper_view.data_to_json(data)
		str = helper_view.render_template_ext('patient_analysis_add_6.html', server = server)
	elif analysis_type_int == db.AnalysisType.Дополнительно:
		data['tests'] = analisis_rules.tests_Дополнительно
		server['data'] = helper_view.data_to_json(data)
		str = helper_view.render_template_ext('patient_analysis_add_1.html', server = server)
	
	return str

@app.route('/patient/<patient_id>/analysis_type/<analysis_type>/analysis_add', methods=['POST'])
def patient_analysis_type_analysis_add_post(patient_id, analysis_type):
	"""Добавить анализ (данные)"""

	if not request.json:
		abort(400)

	# patient_id = int(request.json.get('patient_id'))

	analysis_type_int = int_no_exc(analysis_type)
	analysis_type_str = db.AnalysisTypeStr.get(analysis_type_int)

	if not analysis_type_str:
		abort(400)

	kwargs = {}

	if (
		analysis_type_int == db.AnalysisType.Биохимические_исследования
		or analysis_type_int == db.AnalysisType.Гемостаз
		or analysis_type_int == db.AnalysisType.Клинический_анализ_крови
		or analysis_type_int == db.AnalysisType.Общий_анализ_мочи
		or analysis_type_int == db.AnalysisType.Дополнительно
		):
		result = ''
		data = request.json
		
		params = data.get('params', {})
		kwargs['date_receipt_example'] = params.pop('date_receipt_example', None)
		kwargs['date_delivery_biomaterial'] = params.pop('date_delivery_biomaterial', None)
		kwargs['date_completion'] = params.pop('date_completion', None)

	else:
		result = request.json.get('result')
		
		data = {}
		data['items'] = request.json.get('items')
		data['points'] = request.json.get('points')
		data['isRed'] = request.json.get('isRed')

	data['analysis_type'] = analysis_type_int

	data = json.dumps(data)
	
	if not patient_id or patient_id == '':
		abort(400)

	user_info = session.get(SESSION_KEY_USER)
	user_id = user_info.get('id')

	#analysis_id = None
	analysis = db.Analysis(user_id, patient_id, analysis_type, result, data, **kwargs)
	with db.session_scope() as db_session:
		db_session.add(analysis)
		db_session.commit()
		analysis_id = analysis.id

	#result = query.first() == None
	result = True
	return jsonify({
		'result': result,
		'analysis_id': analysis_id
		})



@app.route('/patient/<patient_id>/analysis/<analysis_id>', methods=['GET'])
def patient_analysis_viewer(patient_id, analysis_id):
	"""Просмотр анализа по id (Не реализовано)"""
	return 'Не реализовано'

################################################################
@app.route('/archive', methods=['GET'])
def archive_patients():
	"""Просмотр пациентов в архиве"""

	user_info = session.get(SESSION_KEY_USER)

	page_num = request.args.get('page', 1, type=int)
	page_size = 10

	username = user_info.get('username')
	user_role = user_info.get('role')

	if user_role == db.UserRole.ADMIN:
		exceptions.abort(403)

	elif user_role == db.UserRole.USER:

		pageData = helper_view.PageData('Архив', username, menus_user, menucur='/archive')
		pageData.add_breadcrumb(pageData.title)

		server = pageData.to_dict()

		data = {}
		data['patients_offset'] = (page_num - 1) * page_size

		with db.session_scope() as db_session:
			db_patients = db_session.query(db.Patient).filter(
				db.Patient.status == db.PatientStatus.ARCHIVE)
			pagination = paginate(db_patients, page_num, page_size)

			patients = []
			for db_patient in pagination.items:
				patients.append(db_patient.toJson())

			data['patients'] = patients
			server['pagination'] = helper_view.pagination_ext(pagination, page_num, page_size, 'archive_patients')
		
		server['data'] = helper_view.data_to_json(data)
		str = helper_view.render_template_ext('archive_patients.html', server = server)
		return str

	abort(500)


import json

################################################################
@app.route('/api/v1.0/test_username', methods=['POST'])
def api_test_username():
	if not request.json:
		abort(400)

	username = request.json.get('username')
	if not username or username == '':
		abort(400)

	with db.session_scope() as db_session:
		query = db_session.query(db.User).filter(
			db.User.username.in_([username]))
		result = query.first() == None

	return jsonify({'result': result})

@app.route('/api/v1.0/search', methods=['POST'])
def api_search():
	if not request.json:
		abort(400)

	query = request.json.get('query', '')
	if query == '':
		abort(400)

	user_info = session.get(SESSION_KEY_USER)
	user_role = user_info.get('role')

	data = search_result(user_role, query)
	return jsonify(data)

@app.route('/api/v1.0/patient/<patient_id>/status', methods=['POST'])
def api_patient_status(patient_id):
	if not request.json:
		abort(400)

	status = request.json.get('status', None)
	if status == None:
		abort(400)

	if status not in db.PatientStatus._value2member_map_:
		abort(400)

	user_info = session.get(SESSION_KEY_USER)
	user_role = user_info.get('role')

	result = False
	with db.session_scope() as db_session:
		db_patient = db_session.query(db.Patient).filter(
			db.Patient.id == patient_id
			)
		db_patient = db_patient.first()
		if db_patient:
			if db_patient.status == status:
				result = True
			else:
				db_patient.status = status
				result = True
				db_session.commit()

	return jsonify({'result': result})

################################################################
@app.route('/feedback', methods=['GET'])
def feedback():
	"""Связь"""

	user_info = session.get(SESSION_KEY_USER)
	username = user_info.get('username')
	user_role = user_info.get('role')

	pageData = helper_view.PageData(feedback.__doc__, username, menus_user, menucur='/feedback')
	pageData.add_breadcrumb(pageData.title)

	if user_role == db.UserRole.ADMIN:
		pageData.menus = menus_admin
		pageData.style_ext = '_red'

	server = pageData.to_dict()
	str = helper_view.render_template_ext('feedback.html', server = server)
	return str


@app.route('/feedback_result', methods=['GET'])
def feedback_result():
	"""Связь"""

	user_info = session.get(SESSION_KEY_USER)
	username = user_info.get('username')
	user_role = user_info.get('role')

	pageData = helper_view.PageData(feedback.__doc__, username, menus_user, menucur='/feedback')
	pageData.add_breadcrumb(pageData.title)

	if user_role == db.UserRole.ADMIN:
		pageData.menus = menus_admin
		pageData.style_ext = '_red'

	server = pageData.to_dict()
	str = helper_view.render_template_ext('feedback_result.html', server = server)
	return str



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

@app.route('/doc')
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
