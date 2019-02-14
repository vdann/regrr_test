"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from flask import redirect
from flask import session
from flask import request
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


app.secret_key = '100' #os.urandom(12)

#############################################################
import os
from flask import send_from_directory

@app.route('/favicon.png')
def favicon():
	return send_from_directory(os.path.join(app.root_path, 'static'),
		'favicon.png', mimetype='image/png')

#############################################################

@app.route('/')
#@app.route('/home')
#@app.route('/index.html')
def home():
	user_id = session.get('user_id')
	if not user_id:
		return redirect('/login')

	patients = [
		make_patient('Петров Петр Петрович', '9. Отделение анестезиологии-реанимации', '01.01.1980'),
		make_patient('Иванов Иван Иванович', '4. Хирургическое отделение абдоминальной онкологии', '02.02.1960'),
		make_patient('Сидоров Сидор Сидорович', '4. Хирургическое отделение абдоминальной онкологии', '12.02.1970'),
	]

	db_session = db.Session()
	query = db_session.query(db.User).filter(
		db.User.id.in_([user_id])
		)

	result = query.first()

	data = {
		'username': result.username,
		'patients': patients 
	}

	str = json.dumps(data, indent=4,  ensure_ascii=False)
	str = render_template('index.html', data = str)
	return str

#############################################################
@app.route('/login', methods=['GET'])
def login():
	return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_admin_login():
	username = request.form['username']
	password = request.form['password']

	db_session = db.Session()

	query = db_session.query(db.User).filter(
		db.User.username.in_([username]),
		db.User.password.in_([password])
		)

	result = query.first()
	if result:
		session['user_id'] = result.id
		return redirect('/')
	
	return render_template('login.html',
		display_error = True,
		password = password,
		username = username)

@app.route("/logout")
def logout():
	session['user_id'] = None
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

	return redirect('/')


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
