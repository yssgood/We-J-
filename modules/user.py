import pymysql.cursors
import hashlib

class User:
	def __init__(self, email, username = None):
		self.email = email
		self.username = username

	def insertRegisterDetails(self, conn, password):
		cursor = conn.cursor()
		query = 'INSERT INTO User(email, username, password) VALUES(%s, %s, %s)'
		password = hashlib.sha256(password.encode()).hexdigest()
		cursor.execute(query, (self.email, self.username, password))
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

	def updateUsername(self, conn):
		cursor = conn.cursor()
		query = 'SELECT * FROM User WHERE email = %s LIMIT 1'
		cursor.execute(query, (self.email))
		data = cursor.fetchone()
		print(data)
		self.username = data['username']
		cursor.close()