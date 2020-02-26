import pymysql.cursors
import hashlib

class User:
	def __init__(self, email):
		self.email = email

	def insertRegisterDetails(self, conn, password):
		cursor = conn.cursor()
		query = 'INSERT INTO User(email, password) VALUES(%s, %s)'
		password = hashlib.sha256(password.encode()).hexdigest()
		cursor.execute(query, (self.email, password))
		conn.commit()
		cursor.close()

	def checkUser(self, conn, password):
		cursor = conn.cursor()
		password = hashlib.sha256(password.encode()).hexdigest()
		query = 'SELECT * FROM User WHERE email = %s and password = %s LIMIT 1'
		cursor.execute(query, (self.email, password))
		data = cursor.fetchone()
		cursor.close()
		return data