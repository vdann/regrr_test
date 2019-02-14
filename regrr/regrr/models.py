import os

import sqlalchemy as sa
import sqlalchemy.ext.declarative
#from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

basedir = os.path.abspath(os.path.dirname(__file__))

db_file = '../data/tutorial.db'
db_file = os.path.join(basedir, db_file)
db_file = os.path.abspath(db_file)

db_path = os.path.dirname(db_file)
if not os.path.exists(db_path):
	os.makedirs(db_path)

db_file = 'sqlite:///' + db_file

engine = sa.create_engine(db_file, echo=True)
Base = sa.ext.declarative.declarative_base()

########################################################################
from enum import IntEnum
class UserRole(IntEnum):
	ADMIN = 1
	USER = 2
	#PATIENT = 3

########################################################################
class User(Base):
	"""Пользователи"""
	__tablename__ = "users"

	id = sa.Column(sa.Integer, primary_key=True)
	username = sa.Column(sa.String, unique=True, index=True)
	password = sa.Column(sa.String)
	role = sa.Column(sa.Integer)

	lastname = sa.Column(sa.String)
	firstname = sa.Column(sa.String)
	middlename = sa.Column(sa.String)
	email = sa.Column(sa.String)
	#date_of_birth = sa.Column(sa.String)

	'''
	username: 'ivanov',
	: 'Иванов',
	firstname: 'Иван',
	: 'Иванович',
	date_of_birth: '01.01.1980',
	: 'ivanov@yan.ru',
	'''

	#----------------------------------------------------------------------
	def __init__(self, username, password, role,
		lastname, firstname, middlename, email):
		""""""
		self.username = username
		self.password = password
		self.role = role
		self.lastname = lastname
		self.firstname = firstname
		self.middlename = middlename
		self.email = email

# create tables
Base.metadata.create_all(engine)

########################################################################
import sqlalchemy.orm

Session = sa.orm.sessionmaker(bind=engine)
session = Session()

query = session.query(User).filter(User.username.in_(['admin']))
result = query.first()
if not result:

	user = User("admin", "admin", UserRole.ADMIN, '-', '-', '-', 'admin@yan.ru')
	session.add(user)

	session.commit()


	#if __name__ == "__main__":

	import datetime
	Session = sa.orm.sessionmaker(bind=engine)
	session = Session()

	query = session.query(User).filter(User.username.in_(['user']))
	result = query.first()
	if not result:
		user = User("user", "user", UserRole.USER, 'Userov', 'User', 'Userovich', 'user@yan.ru')
		session.add(user)

		user = User("ivanov", "ivanov", UserRole.USER, 'Иванов', 'Иван', 'Иванович', 'ivan@yan.ru')
		session.add(user)

		user = User("petrov", "petrov", UserRole.USER, 'Петров', 'Петр', 'Петрович', 'petrov@yan.ru')
		session.add(user)

	session.commit()

