import pymysql.cursors

class User:
	def __init__(self, email):
		self.email = email

	def insertRegisterDetails(self, conn, username, password):
		cursor = conn.cursor()
		query = 'INSERT INTO User(email, username, password) VALUES(%s, %s, %s)'
		cursor.execute(query, (self.email, username, password))
		conn.commit()
		cursor.close()