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

	position = sa.Column(sa.String)

	email = sa.Column(sa.String)
	#date_of_birth = sa.Column(sa.String)

	#----------------------------------------------------------------------
	def __init__(self, username, password, role,
		lastname, firstname, middlename, position, email):
		""""""
		self.username = username
		self.password = password
		self.role = role
		self.lastname = lastname
		self.firstname = firstname
		self.middlename = middlename
		self.position = position
		self.email = email

	def __repr__(self):
		return "<User(id: %s, %s)>" % (self.id, self.username)

	def toJson(self):
		j = {}
		j['id'] = self.id
		j['username'] = self.username
		#j['password'] = self.password
		#j['role'] = self.role
		j['lastname'] = self.lastname
		j['firstname'] = self.firstname
		j['middlename'] = self.middlename
		j['position'] = self.position
		j['email'] = self.email
		return j

########################################################################
class Patient(Base):
	"""Пациенты"""
	__tablename__ = "patients"

	id = sa.Column(sa.Integer, primary_key=True)
	#username = sa.Column(sa.String, unique=True, index=True)
	#password = sa.Column(sa.String)
	#role = sa.Column(sa.Integer)

	lastname = sa.Column(sa.String)
	firstname = sa.Column(sa.String)
	middlename = sa.Column(sa.String)

	department = sa.Column(sa.String)

	#email = sa.Column(sa.String)
	date_of_birth = sa.Column(sa.String)

	#----------------------------------------------------------------------
	def __init__(self,#username, password, role,
		lastname, firstname, middlename,
		department,
		date_of_birth):
		""""""
		#self.username = username
		#self.password = password
		#self.role = role
		self.lastname = lastname
		self.firstname = firstname
		self.middlename = middlename
		self.department = department
		self.date_of_birth = date_of_birth

	def __repr__(self):
		return "<Patient(id: %s, %s %s %s)>" % (self.id, self.lastname, self.firstname, self.middlename)

	def toJson(self):
		j = {}
		j['id'] = self.id
		#j['username'] = self.username
		#j['password'] = self.password
		#j['role'] = self.role
		j['lastname'] = self.lastname
		j['firstname'] = self.firstname
		j['middlename'] = self.middlename
		j['department'] = self.department
		j['date_of_birth'] = self.date_of_birth
		return j



# create tables
Base.metadata.create_all(engine)

# import datetime

########################################################################
import sqlalchemy.orm
from sqlalchemy import exc

Session = sa.orm.sessionmaker(bind=engine)

def initAdmin():

	result = None
	session = Session()
	try:
		query = session.query(User).filter(User.username.in_(['admin']))
		result = query.first()
	except exc.SQLAlchemyError:
		Base.metadata.drop_all(engine)
		Base.metadata.create_all(engine)

	if result:
		return

	user = User("admin", "admin", UserRole.ADMIN, '-', '-', '-', '-', 'admin@yan.ru')
	session.add(user)
	session.commit()


def initTestUsers():
	session = Session()

	resultUsers = session.query(User).all()
	if len(resultUsers) == 1:
		user = User("user", "user", UserRole.USER, 'Userov', 'User', 'Userovich', 'Врач', 'user@yan.ru')
		session.add(user)

		user = User("ivanov", "ivanov", UserRole.USER, 'Иванов', 'Иван', 'Иванович', 'Асистент', 'ivan@yan.ru')
		session.add(user)

		user = User("petrov", "petrov", UserRole.USER, 'Петров', 'Петр', 'Петрович', 'Заведующий', 'petrov@yan.ru')
		session.add(user)

	resultPatients = session.query(Patient).all()
	if len(resultPatients) != 3:
		patient = Patient('Петров', 'Петр', 'Петрович', '9. Отделение анестезиологии-реанимации', '01.01.1980')
		session.add(patient)
		
		patient = Patient('Иванов', 'Иван', 'Иванович', '4. Хирургическое отделение абдоминальной онкологии', '02.02.1965')
		session.add(patient)

		patient = Patient('Сидоров', 'Сидор', 'Сидорович', '4. Хирургическое отделение абдоминальной онкологии', '12.03.1970')
		session.add(patient)

		session.commit()

initAdmin()

if True: #__name__ == "__main__":
	initTestUsers()

	arrs = [
		['Лейкоциты', 'x10<sup>9</sup>/л', '4,00 - 9,00'],
		['Эритроциты', 'x10<sup>12</sup>/л', '4,00 - 5,00'],
		['Гемоглобин', 'г/л', '130 - 160'],
		['Гематокрит', '%', '40 - 48'],
		['Средний объем эритроцита', 'фл', '80,00 - 100,00'],
		['Среднее содержание гемоглобина в эритроците', 'пг', '27,00 - 31,00'],
		['Средняя концентрация гемоглобина в эритроците', 'г/л', '320 - 370'],
		['Коэффициент вариации относительной ширины распределения эритроцитов по объему', '%', '10,00 - 20,00'],
		['Тромбоциты', 'x10<sup>9</sup>/л', '180 - 320'],
		['Относительная ширина распределения тромбоцитов по объему', '%', '10,00 - 20,00'],
		['Средний объем тромбоцитов', 'фл', '7,40 - 10,40'],
		['Тромбокрит', '%', '0,15 - 0,40'],

		['АЛТ', 'Ед/л', '0,00 - 55,00'],
		['АСТ', 'Ед/л', '5,00 - 34,00'],
		['Белок общий', 'г/л', '63,00 - 83,00'],
		['Билирубин общий', 'мкмоль/л', '40 - 48'],
		['Глюкоза', 'мкмоль/л', '3,89 - 5,83'],
		['Креатинин', 'мкмоль/л', '63,60 - 110,50'],
		['Клубочковая фильтрация CKD-EPI Креатинин', 'мл/мин.1.73м^2', '> 60,00'],
		['Мочевина', 'мкмоль/л', '3,00 - 9,20'],
		['С-реактивный белок', 'мг/л', '0,00 - 5,00'],
	];
