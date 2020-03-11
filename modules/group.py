import pymysql.cursors

class Group:
	def __init__(self, email, name):
		self.email = email
		self.name = name

	def insertGroupDetails(self, conn, name):
		cursor = conn.cursor()
		query = 'INSERT INTO MusicGroup(email, groupName) VALUES(%s, %s)'
		cursor.execute(query, (self.email, self.name))
		conn.commit()
		cursor.close()

	def checkMusicGroup(self, conn):
		cursor = conn.cursor()
		query = 'SELECT * FROM MusicGroup WHERE email = %s'
		cursor.execute(query, (self.email))
		data = cursor.fetchone()
		cursor.close()
		return data

