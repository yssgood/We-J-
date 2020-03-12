import pymysql.cursors
from threading import Event

from modules.djRotateThread import DJRotateThread

class Group:
	def __init__(self, ownerEmail, name, creatorUsername):
		self.ownerEmail = ownerEmail
		self.name = name
		self.creatorUsername = creatorUsername
		self.thread = DJRotateThread(Event())

	def insertGroupDetails(self, conn):
		cursor = conn.cursor()
		query = 'INSERT INTO MusicGroup(ownerEmail, groupName) VALUES(%s, %s)'
		cursor.execute(query, (self.ownerEmail, self.name))
		conn.commit()
		cursor.close()

	def checkIfGroupExists(self, conn):
		cursor = conn.cursor()
		query = 'SELECT * FROM MusicGroup WHERE groupName = %s LIMIT 1'
		cursor.execute(query, (self.name))
		data = cursor.fetchone()
		cursor.close()
		return data

	def getName(self):
		return self.name

	def getClients(self):
		return self.thread.getClients()

	def getThreadIndex(self):
		return self.thread.getIndex()

	def startDJRotateThread(self):
		self.thread.start()