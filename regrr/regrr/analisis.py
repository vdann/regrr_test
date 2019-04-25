"""
Описание анализов
"""

import json

############################################################

tests_all = [{
		#id: 1,
		'name': 'АЛТ',
		#result: '', // 24,00
		'unit': 'Ед/л',
		'refs': '0,00 - 55,00'
	},
	{
		#id: 2,
		'name': 'АСТ',
		#result: '', // 19,00
		'unit': 'Ед/л',
		'refs': '5,00 - 34,00'
	},
	{
		#id: 3,
		'name': 'Белок общий',
		#result: '', // 44,00
		'unit': 'г/л',
		'refs': '63,00 - 83,00'
	},
	{
		#id: 4,
		'name': 'Билирубин общий',
		#result: '', // 6,00
		'unit': 'мкмоль/л',
		'refs': '3,40 - 20,50'
	},
	{
		#id: 5,
		'name': 'Глюкоза',
		#result: '', // 6,19
		'unit': 'мкмоль/л',
		'refs': '3,89 - 5,83'
	},
	{
		#id: 6,
		'name': 'Креатинин',
		#result: '', // 52,20
		'unit': 'мкмоль/л',
		'refs': '63,60 - 110,50'
	},
	{
		#id: 7,
		'name': 'Клубочковая фильтрация CKD-EPI Креатинин',
		#result: '', // 111,56
		'unit': 'мл/мин.1.73м^2',
		'refs': '> 60,00'
	},
	{
		id: 8,
		'name': 'Мочевина',
		#result: '', // 3,30
		'unit': 'мкмоль/л',
		'refs': '3,00 - 9,20'
	},
	{
		id: 9,
		'name': 'С-реактивный белок',
		#result: '', // 61,90
		'unit': 'мг/л',
		'refs': '0,00 - 5,00'
	},
	]

############################################################
def num_to_str(num, digits):
	return '{:.{}f}'.format(num, digits)

############################################################
class RuleTYPES:
	RANGE = 'RANGE'
	LESS = 'LESS'
	MORE = 'MORE'

############################################################
class Rules:

	TYPES = RuleTYPES()

	def __init__(self):
		self.rules = {}

	def add(self, name, unit, type, digits, v1, v2=None):
		if self.rules.get(name):
			throw ('!')

		refs = None
		if type == self.TYPES.RANGE:
			refs = '{:.{}f} - {:.{}f}'.format(v1, digits, v2, digits)
		elif type == self.TYPES.LESS:
			refs = '< {:.{}f}'.format(v1, digits)
		elif type == self.TYPES.MORE:
			refs = '> {:.{}f}'.format(v1, digits)
		else:
			throw ('!')
			

		rule = {
			'name': name,
			'unit': unit,
			'type': type,
			'digits': digits,
			'v1': v1,
			'v2': v2,
			'refs': refs
		}

		self.rules[name] = rule

	def get(self, name):
		r = self.rules.get(name)
		if not r:
			throw ('!')
		return r;


############################################################

rules = Rules()

# Клинический_анализ_крови
rules.add('Лейкоциты', 'x10<sup>9</sup>/л', Rules.TYPES.RANGE, 2, 4, 9);
rules.add('Эритроциты', 'x10<sup>12</sup>/л', Rules.TYPES.RANGE, 2, 4, 5);
rules.add('Гемоглобин', 'г/л', Rules.TYPES.RANGE, 0, 130, 160);
rules.add('Гематокрит', '%', Rules.TYPES.RANGE, 0, 40, 48);
rules.add('Средний объем эритроцита', 'фл', Rules.TYPES.RANGE, 2, 80, 100);
rules.add('Среднее содержание гемоглобина в эритроците', 'пг', Rules.TYPES.RANGE, 2, 27, 31);
rules.add('Средняя концентрация гемоглобина в эритроците', 'г/л', Rules.TYPES.RANGE, 0, 320, 370);
rules.add('Стандартное отклонение относительной ширины распределения эритроцитов по объему', 'фл', Rules.TYPES.RANGE, 2, 37.00, 54.00);
rules.add('Коэффициент вариации относительной ширины распределения эритроцитов по объему', '%', Rules.TYPES.RANGE, 2, 10, 20);
rules.add('Тромбоциты', 'x10<sup>9</sup>/л', Rules.TYPES.RANGE, 0, 180, 320);
rules.add('Относительная ширина распределения тромбоцитов по объему', '%', Rules.TYPES.RANGE, 2, 10, 20);
rules.add('Средний объем тромбоцитов', 'фл', Rules.TYPES.RANGE, 2, 7.4, 10.4);
rules.add('Процент содержания крупных тромбоцитов', '%', Rules.TYPES.RANGE, 2, 13.00, 37.00);
rules.add('Тромбокрит', '%', Rules.TYPES.RANGE, 2, 0.15, 0.4);

rules.add('Нормобласты абс.', 'x10<sup>9</sup>/л', Rules.TYPES.RANGE, 2, 0, 0);
rules.add('Нормобласты %', '%', Rules.TYPES.RANGE, 2, 0, 0);

rules.add('Нейрофилы абс.', 'x10<sup>9</sup>/л', Rules.TYPES.RANGE, 2, 2.04, 5.80);
rules.add('Нейрофилы %', '%', Rules.TYPES.RANGE, 2, 48, 78);

rules.add('Лимфоциты абс.', 'x10<sup>9</sup>/л', Rules.TYPES.RANGE, 2, 1.2, 3);
rules.add('Лимфоциты %', '%', Rules.TYPES.RANGE, 2, 19, 37);

rules.add('Моноциты абс.', 'x10<sup>9</sup>/л', Rules.TYPES.RANGE, 2, 0.09, 0.6);
rules.add('Моноциты %', '%', Rules.TYPES.RANGE, 2, 3, 11);

rules.add('Эозинофилы абс.', 'x10<sup>9</sup>/л', Rules.TYPES.RANGE, 2, 0.02, 0.3);
rules.add('Эозинофилы %', '%', Rules.TYPES.RANGE, 2, 0.5, 5);

rules.add('Базофилы абс.', 'x10<sup>9</sup>/л', Rules.TYPES.RANGE, 2, 0.0, 0.065);
rules.add('Базофилы %', '%', Rules.TYPES.RANGE, 2, 0, 1);

rules.add('Незр. гранулоциты абс.', 'x10<sup>9</sup>/л', Rules.TYPES.RANGE, 2, 0, 0);
rules.add('Незр. гранулоциты %', '%', Rules.TYPES.RANGE, 2, 0, 0);

# Биохимические исследования
rules.add('АЛТ', 'Ед/л', Rules.TYPES.RANGE, 2, 0, 55);
rules.add('АСТ', 'Ед/л', Rules.TYPES.RANGE, 2, 5, 34);
rules.add('Альфа-Амилаза', 'Ед/л', Rules.TYPES.RANGE, 2, 25.00, 125.00);
rules.add('Белок общий', 'г/л', Rules.TYPES.RANGE, 2, 63, 83);
rules.add('Билирубин общий', 'мкмоль/л', Rules.TYPES.RANGE, 2, 3.40, 20.50);
rules.add('Билирубин прямой', 'мкмоль/л', Rules.TYPES.RANGE, 2, 0.00, 8.60);
rules.add('Глюкоза', 'мкмоль/л', Rules.TYPES.RANGE, 2, 3.89, 5.83);
rules.add('Креатинин', 'мкмоль/л', Rules.TYPES.RANGE, 2, 63.60, 110.50);
#rules.add('Клубочковая фильтрация CKD-EPI Креатинин', 'мл/мин.1.73м^2', Rules.TYPES.RANGE, 2, 0, 55);
rules.add('Клубочковая фильтрация CKD-EPI Креатинин', 'мл/мин.1.73м<sup>2</sup>', Rules.TYPES.MORE, 2, 60.00);
rules.add('Липаза', 'Ед/л', Rules.TYPES.RANGE, 2, 8.00, 78.00);
rules.add('Мочевина', 'мкмоль/л', Rules.TYPES.RANGE, 2, 3.00, 9.20);
rules.add('С-реактивный белок', 'мг/л', Rules.TYPES.RANGE, 2, 0.00, 5.00);

# Гемостаз
rules.add('Протромбиновое время', 'сек', Rules.TYPES.RANGE, 2, 9.80, 12.10);
rules.add('МНО (международное нормализов. отношение)', '', Rules.TYPES.RANGE, 2, 0.85, 1.15);
rules.add('Процент протромбина по Квику', '%', Rules.TYPES.RANGE, 1, 70, 130);

# Общий анализ мочи
rules.add('pH', '', Rules.TYPES.RANGE, 2, 4.50, 7.50);
rules.add('Уделный вес', '', Rules.TYPES.RANGE, 3, 1.010, 1.025);

rules_Клинический_анализ_крови = [
	'Лейкоциты',
	'Эритроциты',
	'Гемоглобин',
	'Гематокрит',
	'Средний объем эритроцита',
	'Среднее содержание гемоглобина в эритроците',
	'Средняя концентрация гемоглобина в эритроците',
	'Стандартное отклонение относительной ширины распределения эритроцитов по объему',
	'Коэффициент вариации относительной ширины распределения эритроцитов по объему',
	'Тромбоциты',
	'Относительная ширина распределения тромбоцитов по объему',
	'Средний объем тромбоцитов',
	'Процент содержания крупных тромбоцитов',
	'Тромбокрит',
	'Нормобласты %',
	'Нормобласты абс.',
	'Нейрофилы абс.',
	'Нейрофилы %',
	'Лимфоциты абс.',
	'Лимфоциты %',
	'Моноциты абс.',
	'Моноциты %',
	'Эозинофилы абс.',
	'Эозинофилы %',
	'Базофилы абс.',
	'Базофилы %',
	'Незр. гранулоциты абс.',
	'Незр. гранулоциты %'
	]

tests_Клинический_анализ_крови = []
for r in rules_Клинический_анализ_крови:
	tests_Клинический_анализ_крови.append(rules.get(r))

rules_Биохимические_исследования = [
	'АЛТ',
	'АСТ',
	'Альфа-Амилаза',
	'Белок общий',
	'Билирубин общий',
	'Билирубин прямой',
	'Глюкоза',
	'Креатинин',
	'Клубочковая фильтрация CKD-EPI Креатинин',
	'Липаза',
	'Мочевина',
	'С-реактивный белок'
	]

tests_Биохимические_исследования = []
for r in rules_Биохимические_исследования:
	tests_Биохимические_исследования.append(rules.get(r))

# Гемостаз
rules_Гемостаз = [
	'Протромбиновое время',
	'МНО (международное нормализов. отношение)',
	'Процент протромбина по Квику'
	]

tests_Гемостаз = []
for r in rules_Гемостаз:
	tests_Гемостаз.append(rules.get(r))

# Общий_анализ_мочи
rules_Общий_анализ_мочи = [
	'pH',
	'Уделный вес',
	]

tests_Общий_анализ_мочи = []
for r in rules_Общий_анализ_мочи:
	tests_Общий_анализ_мочи.append(rules.get(r))

	
# 1 Биохимические_исследования
# 2 Гемостаз
# 3 Клинический_анализ_крови
# 4 Общий анализ мочи

pass
############################################################
