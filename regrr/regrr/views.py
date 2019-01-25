"""
Routes and views for the flask application.
"""

from datetime import datetime
from flask import render_template
from flask import redirect
from flask import session
from flask import request
from regrr import app

app.secret_key = '100' #os.urandom(12)

@app.route('/')
@app.route('/home')
@app.route('/index.html')
def home():
	if not session.get('logged_in'):
		return redirect('/static/_design/login.html')
	else:
		return redirect('/static/_design/index.html')

@app.route('/login', methods=['POST'])
def do_admin_login():
	password = request.form['password']
	username = request.form['username']
	if username == 'user' and password == 'user':
		session['logged_in'] = True

	return home()

@app.route("/logout")
def logout():
	session['logged_in'] = False
	return home()

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
