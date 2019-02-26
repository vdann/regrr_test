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


app.config['TEMPLATES_AUTO_RELOAD'] = True
app.permanent_session_lifetime = timedelta(days=365)
app.secret_key = '100' #os.urandom(12)

#app.debug = True
'''
app.config['MAIL_SERVER'] = 'smtp.yandex.ru'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'regrr.noreply@ya.ru'
app.config['MAIL_DEFAULT_SENDER'] = 'regrr.noreply@ya.ru'
app.config['MAIL_PASSWORD'] = '654321Q'
'''

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
#app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'regrr.noreply@gmail.com'
app.config['MAIL_DEFAULT_SENDER'] = 'regrr.noreply@gmail.com'
app.config['MAIL_PASSWORD'] = '654321Q!'


# administrator list
<<<<<<< HEAD
# app.config['APP_ADMIN_MAILS'] = ['vdann@ya.ru', 'gleb.manyagin@gmail.com']
app.config['APP_ADMIN_MAILS'] = ['vdann@ya.ru']
=======
app.config['APP_ADMIN_MAILS'] = ['vdann@ya.ru', 'gleb.manyagin@gmail.com']
>>>>>>> add_patients


from flask_mail import Mail
mail = Mail(app)
<<<<<<< HEAD
=======

>>>>>>> add_patients

import regrr.views
