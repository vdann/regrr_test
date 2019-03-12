import os

import sqlalchemy as sa
import sqlalchemy.ext.declarative
#from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

from datetime import datetime

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

db_version = 2

########################################################################
from enum import IntEnum
class UserRole(IntEnum):
	ADMIN = 1
	USER = 2
	#PATIENT = 3

########################################################################
class Metadata(Base):
	"""Метаданные"""
	__tablename__ = "metadata"

	key = sa.Column(sa.String, primary_key=True, unique=True, index=True)
	value = sa.Column(sa.String)

	def __init__(self, key, value):
		""""""
		self.key = key
		self.value = value

	def __repr__(self):
		return "<Metadata (%s, %s)>" % (self.key, self.value)

import time

def utc2local (utc):
	epoch = time.mktime(utc.timetuple())
	offset = datetime.fromtimestamp (epoch) - datetime.utcfromtimestamp (epoch)
	return utc + offset

def makeLastnameAndInitials(lastname, firstname, middlename):
	str = "{} {}.{}.".format(lastname, firstname[0], middlename[0])
	return str

########################################################################
class User(Base):
	"""Пользователи"""
	__tablename__ = "users"

	id = sa.Column(sa.Integer, primary_key=True)
	username = sa.Column(sa.String(50), unique=True, index=True)
	password = sa.Column(sa.String(100), nullable=False)
	role = sa.Column(sa.Integer, nullable=False)

	lastname = sa.Column(sa.String(50), nullable=False)
	firstname = sa.Column(sa.String(50), nullable=False)
	middlename = sa.Column(sa.String(50), nullable=False)

	position = sa.Column(sa.String(200), nullable=False)

	email = sa.Column(sa.String(100))

	date_of_creation = sa.Column(sa.DateTime(), default=datetime.utcnow)
	#date_of_creation = sa.Column(sa.DateTime(), default=datetime.utcnow)
	date_of_last_visit = sa.Column(sa.DateTime(), default=datetime.utcnow)#, onupdate=datetime.utcnow)
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
		return "<User (id: %s, %s)>" % (self.id, self.username)


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
		j['date_of_creation'] = utc2local(self.date_of_creation).strftime("%Y-%m-%d %H:%M:%S") #isoformat()
		j['date_of_last_visit'] = utc2local(self.date_of_last_visit).strftime("%Y-%m-%d %H:%M:%S") #isoformat()
		return j

	def ping(self):
		self.date_of_last_visit = datetime.utcnow
		session = Session.object_session(self)
		#session = Session()
		session.add(self)
		session.commit()

	def getLastnameAndInitials(self):
		str = "{} {}.{}.".format(self.lastname, self.firstname[0], self.middlename[0])
		return str


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
	date_of_birth = sa.Column(sa.String)

	department = sa.Column(sa.String) # отделение
	diagnosis = sa.Column(sa.String) # диагноз


	#----------------------------------------------------------------------
	def __init__(self,#username, password, role,
		lastname, firstname, middlename,
		date_of_birth,
		department,
		diagnosis):
		""""""
		#self.username = username
		#self.password = password
		#self.role = role
		self.lastname = lastname
		self.firstname = firstname
		self.middlename = middlename
		self.date_of_birth = date_of_birth
		self.department = department
		self.diagnosis = diagnosis

	def __repr__(self):
		return "<Patient (id: %s, %s %s %s)>" % (self.id, self.lastname, self.firstname, self.middlename)

	def toJson(self):
		j = {}
		j['id'] = self.id
		#j['username'] = self.username
		#j['password'] = self.password
		#j['role'] = self.role
		j['lastname'] = self.lastname
		j['firstname'] = self.firstname
		j['middlename'] = self.middlename
		j['date_of_birth'] = self.date_of_birth
		j['department'] = self.department
		j['diagnosis'] = self.diagnosis
		return j
	
	def getLastnameAndInitials(self):
		str = "{} {}.{}.".format(self.lastname, self.firstname[0], self.middlename[0])
		return str

	def getFullname(self):
		str = "{} {} {}".format(self.lastname, self.firstname, self.middlename)
		return str


class AnalysisType(IntEnum):
	Клинический_анализ_крови = 1
	Биохимический_анализ_крови = 2
	Коагулограмма = 3
	Общий_анализ_мочи = 4
	Тест_NEWS = 5
	Тест_VTE = 6


AnalysisTypeStr = {
	AnalysisType.Клинический_анализ_крови: 'Клинический анализ крови',
	AnalysisType.Биохимический_анализ_крови: 'Биохимический анализ крови',
	AnalysisType.Коагулограмма: 'Коагулограмма',
	AnalysisType.Общий_анализ_мочи: 'Общий анализ мочи',
	AnalysisType.Тест_NEWS: 'Тест NEWS',
	AnalysisType.Тест_VTE: 'Тест VTE',
	}

########################################################################
class Analysis(Base):
	"""Анализы"""
	__tablename__ = "analyzes"

	id = sa.Column(sa.Integer, primary_key=True)
	user_id = sa.Column(sa.Integer) # кто добавил
	patient_id = sa.Column(sa.Integer) # для какого пациента

	type = sa.Column(sa.Integer) # тип анализа
	date_of_creation = sa.Column(sa.DateTime(), default=datetime.utcnow) # когда зарегистрирован

	result = sa.Column(sa.String) # результат
	data = sa.Column(sa.String) # данные

	#----------------------------------------------------------------------
	def __init__(self,
		user_id,
		patient_id,
		type,
		result,
		data):
		""""""
		self.user_id = user_id
		self.patient_id = patient_id
		self.type = type
		self.result = result
		self.data = data

	def __repr__(self):
		return "<Аnalysis (id: %s, user: %s, patient: %s, type: %s, result: %s)>" \
			% (self.id, self.user_id, self.patient_id, self.type, self.result)

	def toJson(self):
		j = {}
		j['id'] = self.id
		j['user_id'] = self.user_id
		j['patient_id'] = self.patient_id
		j['type'] = self.type
		j['date_of_creation'] = utc2local(self.date_of_creation).strftime("%Y-%m-%d %H:%M:%S") #isoformat()
		j['result'] = self.result
		j['data'] = self.data
		return j

########################################################################
# create tables
Base.metadata.create_all(engine)

# import datetime

########################################################################
import sqlalchemy.orm
from sqlalchemy import exc

Session = sa.orm.sessionmaker(bind=engine)

def initAdmin():

	isOk = True

	try:
		session = Session()
	
		query = session.query(Metadata).filter(Metadata.key.in_(['version']))
		version = query.first()
		version = int(version.value)
		if version != db_version:
			isOk = False

		if isOk:
			query = session.query(User).filter(User.username.in_(['admin']))
			query = query.first()
			if not query:
				isOk = False

		if isOk:
			query = session.query(Patient)
			query = query.first()

		if isOk:
			query = session.query(Analysis)
			query = query.first()
			

	except exc.SQLAlchemyError as err:
		print ("models.init: except exc.SQLAlchemyError", err)
		isOk = False
	except ValueError:
		print ("models.init: except ValueError")
		isOk = False
	except:
		print ("models.init: except")
		isOk = False

	if isOk:
		return

	Base.metadata.drop_all(engine)
	Base.metadata.create_all(engine)

	metadata_version = Metadata('version', str(db_version))
	session.add(metadata_version)

	user = User("admin", "admin", UserRole.ADMIN, '-', '-', '-', '-', 'admin@yan.ru')
	session.add(user)
	session.commit()


def initTestUsers():
	session = Session()

	resultUsers = session.query(User).all()
	if len(resultUsers) == 1:

		user = User("ivanov", "ivanov", UserRole.USER, 'Иванов', 'Иван', 'Иванович', 'Асистент', 'ivan@yan.ru')
		session.add(user)

		user = User("petrov", "petrov", UserRole.USER, 'Петров', 'Петр', 'Петрович', 'Заведующий', 'petrov@yan.ru')
		session.add(user)

		user = User("user", "user", UserRole.USER, 'Сергеев', 'Сергей', 'Сергеевич', 'Врач', 'user@yan.ru')
		session.add(user)


	resultPatients = session.query(Patient).all()
	if len(resultPatients) == 0:
		patient = Patient('Набиев', 'Гасан', 'Набиевич', '01.01.1980', '9. Отделение анестезиологии-реанимации', 'Диагноз 1')
		session.add(patient)
		
		patient = Patient('Воробъев', 'Илья', 'Игоревич', '02.02.1965', '4. Хирургическое отделение абдоминальной онкологии', 'Диагноз 2')
		session.add(patient)

		patient = Patient('Зырянов', 'Станислав', 'Александрович', '12.03.1970', '4. Хирургическое отделение абдоминальной онкологии', 'Диагноз 3')
		session.add(patient)

	resultAnalyzes = session.query(Analysis).all()
	if len(resultAnalyzes) == 0:

		user = session.query(User).filter(
			User.role.in_([UserRole.USER])).first()
		patient = session.query(Patient).first()

		json_data = '''{"points":8,"isRed":true,"items":[{"name":"Respiratory Rate","label":"≤8","points":3},{"name":"Oxygen Saturations","label":"94-95%","points":1},{"name":"Any Supplemental Oxygen","label":"No","points":0},{"name":"Temperature","label":"38.1-39°C&nbsp;/&nbsp;100.5-102.2°F","points":1},{"name":"Systolic Blood Pressure","label":"111-219","points":0},{"name":"Heart Rate","label":"≥131","points":3},{"name":"AVPU Score (Alert, Voice, Pain, Unresponsive)","label":"A","points":0}]}'''

		analysis = Analysis(user.id, patient.id, AnalysisType.Тест_NEWS, '8 points (red)', json_data)
		session.add(analysis)

		analysis = Analysis(user.id, patient.id, AnalysisType.Тест_NEWS, '7 points (red)', json_data)
		session.add(analysis)
		
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
