import hashlib
import pymysql.cursors

class User:
	@staticmethod
	def insertRegisterDetails(email, username, password, conn):
		cursor = conn.cursor()
		query = 'INSERT INTO User(email, username, password) VALUES(%s, %s, %s)'
		password = hashlib.sha256(password.encode()).hexdigest()
		cursor.execute(query, (email, username, password))
		conn.commit()
		cursor.close()

	@staticmethod
	def checkIfUserExists(email, conn):
		cursor = conn.cursor()
		query = 'SELECT * FROM User WHERE email = %s LIMIT 1'
		cursor.execute(query, email)
		data = cursor.fetchone()
		cursor.close()
		return data

	@staticmethod
	def validateUser(email, password, conn):
		cursor = conn.cursor()
		password = hashlib.sha256(password.encode()).hexdigest()
		query = 'SELECT * FROM User WHERE email = %s and password = %s LIMIT 1'
		cursor.execute(query, (email, password))
		data = cursor.fetchone()
		cursor.close()
		return data

	@staticmethod
	def fetchUsername(email, conn):
		cursor = conn.cursor()
		query = 'SELECT * FROM User WHERE email = %s LIMIT 1'
		cursor.execute(query, (email))
		data = cursor.fetchone()
		cursor.close()
		try:
			return data['username']
		except:
			return None

	@staticmethod
	def saveSong(email, songID, conn):
		cursor = conn.cursor()
		query = 'INSERT INTO SavedSongs(email, songID) VALUES(%s, %s)'
		cursor.execute(query, (email, songID))
		conn.commit()
		cursor.close()

	@staticmethod
	def getSavedSongs(email, conn):
		cursor = conn.cursor()
		query = 'SELECT * FROM SavedSongs WHERE email = %s'
		cursor.execute(query, (email))
		data = cursor.fetchall()
		cursor.close()
		return data

	@staticmethod
	def checkForDuplicateSavedSong(email, songID, conn):
		cursor = conn.cursor()
		query = 'SELECT * FROM SavedSongs WHERE email = %s AND songID = %s LIMIT 1'
		cursor.execute(query, (email, songID))
		data = cursor.fetchone()
		cursor.close()
		return data