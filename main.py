import random
import telebot

from os import system
from telebot import types
from config import TOKENS
from parser import Habr, OpenWeather
from data import Clients

debug = 0
bot	  = telebot.TeleBot(TOKENS['bot'], parse_mode=None)
db 	  = Clients()
habr: Habr = None

def auth(func):
	'''Test auth function'''
	def wrapper(message: types.Message):
		if message.from_user.id != 1032616286:
			return bot.reply_to(message, 'Отказано в доступе')
		return func(message)
	return wrapper


@bot.message_handler(commands=['start', 'help'])
def start(message: types.Message):
	bot.send_message(message.chat.id, f'''Привет { message.from_user.first_name }, я бот парсер и вот что я умею:
		/start или /help - помощь в использовании бота
		/search [запрос] - осуществляет поиск по сайту habr.com
		/weather [город] - отправляет данные об  погоде в указаном городе(beta)
	Помимо этого я умею:
		/getfile [имя]   - отправляет файл json с информацией которую вы искали
		/random  - отправляет рандомное число
		/name    - отправляет ваш имя в telegram
		/id 	 - отправляет ваш идентификатор в telegram
		Введите команду, что бы я её выполнил!''') # random [от до] - позже реализовать


@bot.message_handler(commands=['getfile'])
def getfile(message: types.Message):
	cond = habr.getInfo()
	if len(cond) > 0:
		name = habr.getFile()
		with open(name, 'rb') as f:
			bot.send_document(message.chat.id, f)
		system(f'rm { name }')


@bot.message_handler(commands=['search'])
@auth
def search(message: types.Message):
	global habr
	habr = Habr()

	mess = message.text.replace('/search', '').strip()
	otv = bot.send_message(message.chat.id, 'Подождите, идет выполнение...')
	res = habr.search(mess)
	

	if len(mess) > 1 and res:
		info   = ''
		inline = types.InlineKeyboardMarkup()
		item1  = types.InlineKeyboardButton(text='Далее', callback_data='next')
		item2  = types.InlineKeyboardButton(text='Стоп', callback_data='stop')
		inline.add(item1, item2)
		
		try:
			for i in range(10):
				out = habr.each()
				info += out
			# otv = bot.send_message(message.chat.id, info, reply_markup=inline)
			bot.edit_message_text(info, otv.chat.id, otv.id, reply_markup=inline)
		except Exception as e:
			bot.reply_to(message, 'Введите текст верно!')
	elif not res and habr.getError() != '':
		bot.send_message(message.chat.id, habr.getError())
	else:
		bot.reply_to(message, 'Мало символов для поиска!')


@bot.callback_query_handler(func=lambda call: True)
@auth
def answer(call: types.CallbackQuery):
	global habr
	bot.answer_callback_query(callback_query_id=call.id)
	try:
		if call.data == 'next':
			if habr != None or habr.getNext() != '':
				info   = ''
				inline = types.InlineKeyboardMarkup()
				item1  = types.InlineKeyboardButton(text='Далее', callback_data='next')
				item2  = types.InlineKeyboardButton(text='Стоп', callback_data='stop')
				inline.add(item1, item2)

				for i in range(10):
					out = habr.each()
					if out: info += out
				bot.send_message(call.message.chat.id, info, reply_markup=inline)
			else:
				bot.reply_to(call.message, 'Данные обновлены, сделайте повторный поиск!')
		elif call.data == 'stop':
			habr.clearInfo().clearNext()
			bot.send_message(call.message.chat.id, f'Прервано...')
	except Exception as e:
		bot.send_message(call.message.chat.id, f'Прервано...')
		if debug:
			print(e)


@bot.message_handler(commands=['weather'])
def weather(message: types.Message):
	mess = message.text.replace('/weather', '').strip()
	if mess != '' and len(mess) > 2:
		ow = OpenWeather(mess, TOKENS['weather'])
		bot.send_message(message.chat.id, ow.getInfo())
	else: bot.send_message(message.chat.id, 'Короткое название города.\nВведите название города снова!')


# future for distribution
@bot.message_handler(commands=['subscribe', 'unsubscribe'])
def login(message: types.Message):
	log = db.select(message.from_user.id, 'subscribe')
	if log == 0: # unsubscribe
		if message.text == 'unsubscribe':
			bot.reply_to(message, 'Вы уже отписанны!')
		db.update('subscribe', True, message.from_user.id)
	elif log == 1: # subscribe
		if message.text == 'subscribe':
			bot.reply_to(message, 'Вы уже подписанны!')
		db.update('subscribe', False, message.from_user.id)
	else: # no user
		if message.text == 'unsubscribe':
			bot.reply_to(message, 'Вы и так отписанны!')
		db.insert(message.from_user.id, True)


@bot.message_handler(func=lambda message: True)
def commands(message: types.Message):
	if message.text == '/id':
		bot.send_message(message.chat.id, f'Ваш идентификатор { message.from_user.id }')
	elif message.text == '/name':
		bot.send_message(message.chat.id, f'Ваше имя { message.from_user.first_name }')
	elif message.text == '/random':
		bot.send_message(message.chat.id, f'Ваше число { random.randint(0, 1000) }')
	else: bot.reply_to(message, 'Неизвестная команда!')


if __name__ == '__main__':
	print('Bot work...')
	bot.infinity_polling()
