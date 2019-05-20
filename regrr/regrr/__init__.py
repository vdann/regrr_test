"""
The flask application package.
"""
from datetime import timedelta

from flask import Flask
app = Flask(__name__)

'''
{% => (%
{{ => ((
'''
app.jinja_options = Flask.jinja_options.copy()
app.jinja_options.update(dict(
	block_start_string='(%',
	block_end_string='%)',
	variable_start_string='((',
	variable_end_string='))',
	comment_start_string='(#',
	comment_end_string='#)',
))

from jinja2 import Markup
import os

class customutil:
	def __init__(self, flask_app):
		self.flask_app = flask_app

	def include_raw(self, filename, wrap='{}'):
		filename = os.path.join(self.flask_app.root_path, filename)
		f = open(filename, 'rb')
		source = f.read()
		#source = app.jinja_loader.get_source(app.jinja_env, filename)
		#source = source[0]
		source = wrap.format(source.decode())
		markup = Markup(source)
		return markup

	def include_script_inline(self, filename):
		wrap='''<script>
{}
</script>'''
		return self.include_raw(filename, wrap)


app.config['TEMPLATES_AUTO_RELOAD'] = True
app.permanent_session_lifetime = timedelta(days=365)
app.secret_key = '100' #os.urandom(12)
app.url_map.strict_slashes = False

app.jinja_env.globals.update(customutil=customutil(app))

#app.debug = True
'''
app.config['MAIL_SERVER'] = 'smtp.yandex.ru'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'regrr.noreply@ya.ru'
app.config['MAIL_DEFAULT_SENDER'] = 'regrr.noreply@ya.ru'
app.config['MAIL_PASSWORD'] = '654321Q!'
'''

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
#app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'regrr.noreply@gmail.com'
app.config['MAIL_DEFAULT_SENDER'] = 'regrr.noreply@gmail.com'
app.config['MAIL_PASSWORD'] = '654321Q!'


# administrator list
# app.config['APP_ADMIN_MAILS'] = ['vdann@ya.ru', 'gleb.manyagin@gmail.com']
app.config['APP_ADMIN_MAILS'] = ['vdann@ya.ru']

from flask_mail import Mail
mail = Mail(app)

from flask_moment import Moment
moment = Moment(app)

import regrr.views
