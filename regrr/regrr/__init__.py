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


import regrr.views
