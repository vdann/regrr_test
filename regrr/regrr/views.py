"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from flask import redirect
from flask import session
from flask import request
from regrr import app

import json


def make_patient(fullname, department, date_of_birth):
	return {
		'fullname': fullname,
		'department': department,
		'date_of_birth': date_of_birth,
	}


app.secret_key = '100' #os.urandom(12)

@app.route('/')
@app.route('/home')
@app.route('/index.html')
def home():
	if not session.get('logged_in'):
		return redirect('/login')

	patients = [
		make_patient('Петров Петр Петрович', '9. Отделение анестезиологии-реанимации', '01.01.1980'),
		make_patient('Иванов Иван Иванович', '4. Хирургическое отделение абдоминальной онкологии', '02.02.1960'),
		make_patient('Сидоров Сидор Сидорович', '4. Хирургическое отделение абдоминальной онкологии', '12.02.1970'),
	]

	data = {
		'username': 'server',
		'patients': patients 
	}

	str = json.dumps(data, indent=4,  ensure_ascii=False)
	str = render_template('index.html', data = str)
	return str

@app.route('/login', methods=['GET'])
def login():
	return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_admin_login():
	password = request.form['password']
	username = request.form['username']
	if username == 'user' and password == 'user':
		session['logged_in'] = True
		return redirect('/')
	
	return render_template('login.html',
		display_error = True,
		password = password,
		username = username)

@app.route("/logout")
def logout():
	session['logged_in'] = False
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
