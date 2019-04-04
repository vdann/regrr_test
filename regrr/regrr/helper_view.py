"""
Вспомогательные функции и классы
"""

from datetime import datetime
from flask import url_for
import json


############################################################
def str_remove_bom(str):
	"""Удаляет BOM-символы в начале строки (обнаружилась проблема с шаблонами)"""
	if str.startswith('\ufeff\ufeff'):
		str = str[2:]
	elif str.startswith('\ufeff'):
		str = str[1:]

	return str

def str_nbsp(text):
	return text.replace(' ', '&nbsp;')


############################################################
def url_for_ext(endpoint, **values):
	"""Удаляет page, при page == 1"""
	page = values.get('page')
	if (page == 1):
		values.pop('page', None)

	str = url_for(endpoint, **values)
	return str

############################################################
def pagination_ext(pagination, page_cur, page_size, endpoint, **values):
	"""Создает массив ссылок на основе объекта paginate from sqlalchemy_pagination"""

	page_first = 1
	page_last = pagination.pages


	jpagination = {} 
	values['page'] = page_cur
	jpagination['cur'] = url_for_ext(endpoint, **values)


	if pagination.has_previous:
		values['page'] = pagination.previous_page
		jpagination['prev'] = url_for_ext(endpoint, **values)

	if pagination.has_next:
		values['page'] = pagination.next_page
		jpagination['next'] = url_for_ext(endpoint, **values)

	#ii = []

	if page_last <= 7:
		ii = list(range(page_first, page_last + 1))

	elif page_cur <= 4:
		ii = list(range(page_first, 6))
		ii.append(None)
		ii.append(page_last)

	elif page_last - page_cur <= 3:
		ii = list(range(page_last - 4, page_last + 1))
		ii.insert(0, None)
		ii.insert(0, page_first)

	else:
		ii = []
		ii.append(page_first)
		ii.append(None)

		ii.append(page_cur - 1)
		ii.append(page_cur)
		ii.append(page_cur + 1)

		ii.append(None)
		ii.append(page_last)


	jlist = []
	for i in ii:
		if i == None:
			jlist.append(None)
		else:
			values['page'] = i
			jlist.append({ 'text': i, 'href': url_for_ext(endpoint, **values)})

	jpagination['list'] = jlist

	return jpagination

############################################################
def data_to_json(data):
	data = 'data = ' + json.dumps(data, indent=4,  ensure_ascii=False) + ';'
	return data

############################################################
class PageData:
	"""Содержит данные для отрисовки базового шаблона"""

	app_name = "[Не задано]"

	@staticmethod
	def make_menu_item (href, text, cls = None):
		"""Создает элемент меню"""
		item = {
			'href': href,
			'text': text,
			'cls': cls
		}
		return item

	@staticmethod
	def make_submenu (text, submenus):
		"""Создает подменю"""
		return {
			'text': text,
			'submenus': submenus
		}


	def __init__(self, title, username = None, menus = None, **kwargs):
		"""Constructor"""

		self.app_name = PageData.app_name
		self.title = title
		self.username = username

		self.menus = menus
		self.menucur = kwargs.get('menucur', None)
		self.style_ext = kwargs.get('style_ext', '')

		self.breadcrumbs = []
		self.prevnext = None

		self.year = datetime.now().year


	def add_breadcrumb(self, text, href = None):
		"""Добавляет элемент контекстной панели навигации"""
		self.breadcrumbs.append({
			'text': text,
			'href': href
		})


	def set_prev(self, href = None, title = None):
		"""Устанавливает ссылку на предыдущий элемент для страниц детального просмотра списков"""
		if self.prevnext == None:
			self.prevnext = {}

		prev = {}
		if href:
			prev['href'] = href
			prev['title'] = title

		self.prevnext['prev'] = prev


	def set_next(self, href = None, title = None):
		"""Устанавливает ссылку на следующий элемент для страниц детального просмотра списков"""
		if self.prevnext == None:
			self.prevnext = {}

		next = {}
		if href:
			next['href'] = href
			next['title'] = title

		self.prevnext['next'] = next
	

	def to_dict(self, dict_in = {}):

		dict_out = dict(dict_in, **self.__dict__)

		return dict_out

############################################################
