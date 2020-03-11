import pymysql.cursors

class Group:
	def __init__(self, email, username, name):
		self.email = email
		self.username = username
		self.name = name

	def insertGroupDetails(self, conn):
		cursor = conn.cursor()
		query = 'INSERT INTO MusicGroup(email, username, groupName) VALUES(%s, %s, %s)'
		cursor.execute(query, (self.email, self.username, self.name))
		conn.commit()
		cursor.close()

	def checkMusicGroup(self, conn):
		cursor = conn.cursor()
		query = 'SELECT * FROM MusicGroup WHERE email = %s'
		cursor.execute(query, (self.email))
		data = cursor.fetchone()
		cursor.close()
		return data

