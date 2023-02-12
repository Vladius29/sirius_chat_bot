"""import mysql
"""
try:
	from telebot import types, TeleBot
	from mysql.connector import connection, errorcode, Error
except:
	print('Failed to import telebot or mysql-connector')
	from os import system

	system('pip install pyTelegramBotAPI')
	from telebot import types, TeleBot
	print('telebot installed')

	system('pip install mysql-connector-python')
	from mysql.connector import connection, errorcode
	print('mysql-connector installed')

from configparser import ConfigParser

# parsing config from config.ini file
conf = ConfigParser()
conf.read("config.ini")

"""
Структура базы данных:
mysql
Имя базы: bot
Только одна таблица - post
Имеет 4 столбца: заголовок, контент, id и подсказки
Подсказки — строка с ID постов, чьи кнопки будут под постом
Темы для подсказок выделены в посте курсивом

+------------------------+-------------------------+------------------+-----+
|         title          |         content         |       tips       | id  |
+------------------------+-------------------------+------------------+-----+
|     post 1 title       |     post 1 content      |    "ID1 ID2"     |  0  |
|     post 2 title       |     post 2 content      |    "ID4 ID9"     |  1  |
...

И всё
"""

# connecting to database
try:
	conn = connection.MySQLConnection(user=conf['conf']['dbuser'],
									  password=conf['conf']['dbpwd'],
									  database=conf['conf']['dbname'])
	print("DB connection success")

except Error as err:
	if err == errorcode.ER_ACCESS_DENIED_ERROR:
		print("DB connection error! Wrong username or password")
	if err == errorcode.ER_BAD_DB_ERROR:
		print("DB connection error! Wrong database")


class Bot(TeleBot):

	def __init__(self, token: str):
		super().__init__(token)
		self.cursor = conn.cursor()
		self.id_title_dict = {  # Matches between id and title
			0: "1. Главное меню",
			1: "2. Банки и банковские услуги",
			2: "3. Физические и юридические лица",
			3: "4. Банковские карты"
		}

	def get_post_by_id(self, query: int):
		self.cursor.execute(
			f'SELECT title, content, tips FROM post WHERE id={query}')

		for (title, content, tips) in self.cursor:
			return title, str(content), tips

	def show_post(self, msg):
		try:
			markup = types.ReplyKeyboardMarkup()  # Deleting old buttons
			if msg.text[0] == '/':  # For /start function, there`s no way to do it better
				post = self.get_post_by_id(0)
			else:
				post = self.get_post_by_id(int(msg.text[0]) - 1)  # Defining current post

			for tip in post[2].split():	 # Adding tips to the markup
				markup.add(types.KeyboardButton(self.id_title_dict[int(tip)]))

			bot.send_message(msg.chat.id,  # Send content and add new buttons
				f"*{post[0]}*\n\n"
				f"{post[1]}",
				parse_mode="Markdown",
				reply_markup=markup)

		except:
			markup = types.ReplyKeyboardMarkup()
			markup.add(types.KeyboardButton("Главное меню"))
			self.send_message(msg.chat.id,  # Send content and add new buttons
				 f"*Упс...* Похоже, этого поста ещё нет. \n"
				 "Возможно, скоро его добавят, так что загляните позже *<3*",
				 parse_mode="Markdown",
				 reply_markup=markup)

# running bot
bot = Bot(conf['conf']['token'])
print(f"Bot start success")

# starting message
@bot.message_handler(commands=['start'])
def main_menu(msg):
	bot.show_post(msg)

# answering all messages
@bot.message_handler(content_types=['text'])
def main_menu(msg):
	bot.show_post(msg)


"""@bot.message_handler(commands=['chat', 'чат'])
def secret(message):
	if message.chat.id == 5604527660:
		bot.send_message(928090810, f'Чат: {message.text[5:]}')
	else:
		bot.send_message(5604527660, f'Чат: {message.text[5:]}')
	print(message.chat.id, "chat", message.text[5:], "\n")"""

# infinite loop and db closing
bot.infinity_polling()
conn.close()
