"""
The flask application package.
"""

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

import regrr.views
