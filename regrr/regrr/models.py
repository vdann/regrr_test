
import os
import time
from datetime import datetime
from contextlib import contextmanager

import sqlalchemy as sa
import sqlalchemy.ext.declarative
import sqlalchemy.orm
#from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref
from sqlalchemy import exc


########################################################################
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

DB_VERSION = 2

########################################################################
def utc_to_local(utc):
	epoch = time.mktime(utc.timetuple())
	offset = datetime.fromtimestamp (epoch) - datetime.utcfromtimestamp (epoch)
	return utc + offset

def datetime_to_str(utc):
	return utc_to_local(utc).strftime("%d.%m.%Y %H:%M:%S")

def datetime_to_str_date_hms(utc):
	return utc_to_local(utc).strftime("%d.%m.%Y %H:%M:%S")

def datetime_to_str_date_hm(utc):
	return utc_to_local(utc).strftime("%d.%m.%Y %H:%M")

def datetime_to_str_date(utc):
	return utc_to_local(utc).strftime("%d.%m.%Y")

########################################################################
def make_lastname_and_initials(lastname, firstname, middlename):
	str = "{} {}.{}.".format(lastname, firstname[0], middlename[0])
	return str

########################################################################
from enum import Enum, IntEnum, unique
@unique
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
		j['date_of_creation'] = datetime_to_str(self.date_of_creation)
		j['date_of_last_visit'] = datetime_to_str(self.date_of_last_visit)
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

	def getFullname(self):
		str = "{} {} {}".format(self.lastname, self.firstname, self.middlename)
		return str


@unique
class ClassifEnum(Enum):

	def __init__(self, value, label, label_short):

		if not hasattr(self.__class__, '_int_to_member_'):
			self.__class__._int_to_member_ = {}
		
		self._value_ = value
		self.label = label
		self.label_short = label_short

		self.__class__._int_to_member_[value] = self

	def __int__(self):
		return self.value

	@classmethod
	def from_int(cls, num):
		return cls._int_to_member_.get(num, None)

@unique
class Gender(ClassifEnum):
	NOT_SPECIFIED = (0, 'не указан', '-')
	MALE = (1, 'мужcкой', 'М')
	FEMALE = (2, 'женский', 'Ж')

gender2 = Gender.from_int(0)
gender2 = Gender.from_int(1)
gender2 = Gender.from_int(2)


@unique
class PatientStatus(IntEnum):
	NORMAL = 1
	ARCHIVE = 2

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
	gender = sa.Column(sa.Integer)

	date_of_birth = sa.Column(sa.String)

	department = sa.Column(sa.String) # отделение
	diagnosis = sa.Column(sa.String) # диагноз
	status = sa.Column(sa.String)


	#----------------------------------------------------------------------
	def __init__(self,#username, password, role,
		lastname, firstname, middlename,
		gender,
		date_of_birth,
		department,
		diagnosis):
		""""""

		if isinstance(gender, Gender):
			gender = int(gender)

		#self.username = username
		#self.password = password
		#self.role = role
		self.lastname = lastname
		self.firstname = firstname
		self.middlename = middlename
		self.gender = gender
		self.date_of_birth = date_of_birth
		self.department = department
		self.diagnosis = diagnosis
		self.status = PatientStatus.NORMAL

	def __repr__(self):
		return "<Patient (id: %s, %s %s %s)>" % (self.id, self.lastname, self.firstname, self.middlename)

	def toJson(self, isStr=False):
		j = {}
		j['id'] = self.id
		#j['username'] = self.username
		#j['password'] = self.password
		#j['role'] = self.role
		j['lastname'] = self.lastname
		j['firstname'] = self.firstname
		j['middlename'] = self.middlename
		j['gender'] = self.gender
		j['date_of_birth'] = self.date_of_birth
		j['department'] = self.department
		j['diagnosis'] = self.diagnosis
		j['status'] = self.status

		if isStr:
			j['gender_str'] = Gender.from_int(self.gender).label
			j['gender_str_short'] = Gender.from_int(self.gender).label_short

		return j
	
	def getLastnameAndInitials(self):
		str = "{} {}. {}.".format(self.lastname, self.firstname[0], self.middlename[0])
		return str

	def getFullname(self):
		str = "{} {} {}".format(self.lastname, self.firstname, self.middlename)
		return str


class AnalysisType(IntEnum):
	Биохимические_исследования = 1
	Гемостаз = 2
	Клинический_анализ_крови = 3
	Общий_анализ_мочи = 4
	#Биохимический_анализ_крови = 2
	#Коагулограмма = 3
	#Общий_анализ_мочи = 4
	Тест_NEWS = 5
	Тест_VTE = 6
	Дополнительно = 7


AnalysisTypeStr = {
	AnalysisType.Биохимические_исследования: 'Биохимические исследования',
	AnalysisType.Гемостаз: 'Гемостаз',
	AnalysisType.Клинический_анализ_крови: 'Клинический анализ крови',
	AnalysisType.Общий_анализ_мочи: 'Общий анализ мочи. Химические свойства',
	#AnalysisType.Коагулограмма: 'Коагулограмма',
	#AnalysisType.Общий_анализ_мочи: 'Общий анализ мочи',
	AnalysisType.Тест_NEWS: 'Тест NEWS',
	AnalysisType.Тест_VTE: 'Тест VTE',
	AnalysisType.Дополнительно: 'Дополнительно',
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
		j['date_of_creation'] = datetime_to_str(self.date_of_creation)
		j['result'] = self.result
		j['data'] = self.data
		return j

########################################################################
# create tables
Base.metadata.create_all(engine)

########################################################################
Session = sa.orm.sessionmaker(bind=engine)

########################################################################
@contextmanager
def session_scope(): 
	"""
		Пример использования

		def run_my_program():
		with session_scope() as session:
			session.query(FooBar).update({"x": 5})
			session.query(ThingTwo).update({"q": 18})
	"""

	session = Session()
	try:
		yield session
		session.commit()
	except:
		session.rollback()
		raise
	finally:
		session.close()


########################################################################
def initAdmin():
	"""Инициализация БД"""

	isOk = True

	try:
		session = Session()
	
		query = session.query(Metadata).filter(Metadata.key.in_(['version']))
		version = query.first()
		version = int(version.value)
		if version != DB_VERSION:
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

	metadata_version = Metadata('version', str(DB_VERSION))
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
		patient = Patient('Набиев', 'Гасан', 'Набиевич', Gender.MALE, '01.01.1980', '9. Отделение анестезиологии-реанимации', 'Диагноз 1')
		session.add(patient)
		
		patient = Patient('Воробъев', 'Илья', 'Игоревич', Gender.MALE, '02.02.1965', '4. Хирургическое отделение абдоминальной онкологии', 'Диагноз 2')
		session.add(patient)

		patient = Patient('Зырянов', 'Станислав', 'Александрович', Gender.MALE, '12.03.1970', '4. Хирургическое отделение абдоминальной онкологии', 'Диагноз 3')
		session.add(patient)

		patient = Patient('Зырянова', 'Станислава', 'Александровна', Gender.FEMALE, '12.03.1971', '4. Хирургическое отделение абдоминальной онкологии', 'Диагноз 3')
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


	# инициализация для проверки пагинации
	resultPatients = session.query(Patient).count()
	if resultPatients < 10:
		for i in range(1, 80):
			patient = Patient('Набиев' + str(i), 'Гасан', 'Набиевич', Gender.NOT_SPECIFIED, '01.01.1980', '9. Отделение анестезиологии-реанимации', 'Диагноз 1')
			session.add(patient)


	resultAnalyzes = session.query(Analysis).count()
	if resultAnalyzes < 10:

		user = session.query(User).filter(
			User.role.in_([UserRole.USER])).first()
		patient = session.query(Patient).first()

		json_data = '''{"points":8,"isRed":true,"items":[{"name":"Respiratory Rate","label":"≤8","points":3},{"name":"Oxygen Saturations","label":"94-95%","points":1},{"name":"Any Supplemental Oxygen","label":"No","points":0},{"name":"Temperature","label":"38.1-39°C&nbsp;/&nbsp;100.5-102.2°F","points":1},{"name":"Systolic Blood Pressure","label":"111-219","points":0},{"name":"Heart Rate","label":"≥131","points":3},{"name":"AVPU Score (Alert, Voice, Pain, Unresponsive)","label":"A","points":0}]}'''

		for i in range(1, 80):
			analysis = Analysis(user.id, patient.id, AnalysisType.Тест_NEWS, '8 points (red)', json_data)
			session.add(analysis)

		
	session.commit()

initAdmin()

if True: #__name__ == "__main__":
	initTestUsers()
