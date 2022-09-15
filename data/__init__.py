import sqlite3 as sql

class Clients:
	def __init__(self):
		self.__db  = sql.connect('users.db')
		self.__cur = self.__db.cursor()

	def insert(self, tele_id: str, subsc: int) -> bool:
		self.__cur.execute('insert into user(telegram_id, subscribe) values(?,?);', (tele_id, subsc))
		self.__db.commit()
	def update(self, field: str, value: str|int, where: int) -> bool:
		self.__cur.execute(f'update user set { field }=? where telegram_id=?;', (value, where))
		self.__db.commit()
	def select(self, tele_id: str=-1, field:str='*') -> bool:
		cond = f'SELECT {field} FROM user WHERE telegram_id={tele_id};'
		return self.__cur.execute(cond).fetchone()
	def fetch_all(self) -> bool:
		return self.__cur.execute('select * from user;').fetchall()

# if  __name__ == '__main__':
# 	a = Clients()
	# a.insert('1032616286', 0)
	# a.update('subscribe', True, 1032616286)
	# print(a.fetch_all())
	# print(a.select(1032616286, 'id'))
	