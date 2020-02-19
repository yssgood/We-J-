import pymysql.cursors

class User:
	def __init__(self, email):
		self.email = email

	def insertRegisterDetails(self, conn, email, username, password):
		cursor = conn.cursor()
		query = 'INSERT INTO User(email, username, password) VALUES(%s, %s, %s)'
		cursor.execute(query, (email, username, password))
		conn.commit()
		cursor.close()