import enum
import requests as r

from requests import Session
from bs4 import BeautifulSoup
from datetime import datetime

class Habr:
	__out = []
	__err = ''
	__url = 'https://habr.com/ru/'
	headers = {
		"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36"
	}
	
	_next = ''
	_data = None
	_html = None

	count = 0
	debug = False
	history = []

	def __init__(self, debug=False):
		self.r = Session()
		self.debug = debug

	'''parsing func'''
	def search(self, query: str):
		try:
			self.__out = []
			self.history.append(query)
			query 	   = query.replace(' ', '%20')
			self._data = self.r.get(self.__url + f'search/?q={ query }&target_type=posts&order=relevance', headers=self.headers)
			self._html = BeautifulSoup(self._data.text, 'html.parser')
			self._parse()
			return True
		except Exception as e:
			if self.debug: print(e)
			return False
	
	'''read html code'''
	def _parse(self):
		try:
			while True:
				none  = self._html.find_all('div', attrs={ 'data-test-id': 'empty-placeholder-text' })
				items = self._html.find_all('article')
				pag   = self._html.find_all('a', attrs={ 'id': 'pagination-next-page' })
				# tree1 = self._html.select('article>div>.tm-article-snippet__lead>div>div>div>img')
				# tree2 = self._html.select('article>div>.tm-article-snippet__lead>div>img')
				
				if none != []: raise none[0].text

				for item in items:
					self.__out.append({
						'text': item.h2.span.text,
						'link': self.__url + item.h2.a['href'].replace('/ru/', ''),
					})
				
				if pag == []:
					self.__err = 'end pagination'
					break
				else:
					self._next = pag[0]['href'].replace('/ru/', '')
					self._data = self.r.get(self.__url + self._next, headers=self.headers)
					self._html = BeautifulSoup(self._data.text, 'html.parser')
			return True

		except Exception as e:
			if self.debug:
				self.__err = e
				print(e)
			return False

	@staticmethod
	def version(): return '0.0.1'

	'''return errors'''
	def getError(self): return self.__err
	
	'''return all info like string'''
	def getInfo(self, txt=''):
		for i in self.__out: txt += f"{ i['text'] }:\n{ i['link'] }\n"
		return txt

	'''clear info'''
	def clearInfo(self):
		self.__out = []
		return self

	'''clear next for end parsing'''
	def clearNext(self):
		self._next = ''
		return self
	
	'''getter'''
	def getNext(self): return self._next

	'''generator info in list'''
	def each(self):
		i = self.count
		if i < len(self.__out):
			otv = f"{ self.__out[i]['text'] }:\n{ self.__out[i]['link'] }\n\n"
			self.count += 1
			return otv
		else:
			self.count = 0
			return False
	
	'''create json file and return her name'''
	def getFile(self, txt='['):
		if len(self.__out) > 0:
			with open(f'habr_{ self.history[-1] }.txt', 'w', encoding='utf-8') as f:
				for i in self.__out:
					txt += "\n\t{\n\t\ttext: %s,\n\t\tlink: %s\n\t},"%(i['text'], i['link'])
				txt += '\n]'
				f.write(txt)
		return f'habr_{ self.history[-1] }.txt'

	'''print all info'''
	def print(self):
		for i in self.__out:
			for j in i:
				print(f"{j}: {i[j]}")
			print('=' * 10)
		return self
	
	'''test all method'''
	def run(self):
		if self.debug:
			self.search(input('Найти '))
			print(self.getFile())
			# self.print()
		return self

class OpenWeather:
	emoji_to_smile = {
		"Clear": "Ясно \U00002600",
		"Clouds": "Облачно \U00002601",
		"Rain": "Дождь \U00002614",
		"Drizzle": "Морось \U00002614",
		"Thunderstorm": "Гроза \U000026A1",
		"Snow": "Снег \U0001F328",
		"Mist": "Туман \U0001F32B"
	}
	url    = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}&units=metric&lang={}'
	__info = ''
	def __init__(self, city: str, token=str):
		r = Session()
		data = r.get(self.url.format(city, token, 'ru'))
		data = data.json()
		data = self.foramt(data)
		self.__info = data

	# преобразовывает в нужный текст(берёт нужные данные)
	def foramt(self, data) -> str:
		city 	 = data['name']
		temp 	 = data['main']['temp']
		humidity = data['main']['humidity']
		pressure = data['main']['pressure']
		speed    = data['wind']['speed']
		weather  = data['weather'][0]['main']
		sunrise  = datetime.fromtimestamp(data['sys']['sunrise'])
		sunset   = datetime.fromtimestamp(data['sys']['sunset'])
		len_day  = sunset - sunrise
		
		otv = f'''Погода на { datetime.now().strftime('%Y-%m-%d %H:%M') }
В городе { city }\nТемпература { temp }C { self.emoji_to_smile[weather] }
Влажность { humidity }%\nДавление { pressure } мм.рт.ст.
Ветер { speed } м/с\nВосход солнца { sunrise }
Закат солнца { sunset }\nПродолжительность дня { len_day }
Хорошего дня!'''
		return otv

	# return info after method format
	def getInfo(self) -> str: return self.__info