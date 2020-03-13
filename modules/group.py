import pymysql.cursors
from threading import Event

from modules.djRotateThread import DJRotateThread

class Group:
	def __init__(self, name, creatorUsername):
		self.name = name;
		self.creatorUsername = creatorUsername;
		self.currentSong = None;
		self.thread = DJRotateThread(Event());

	@staticmethod
	def insertGroupDetails(ownerEmail, name, conn):
		cursor = conn.cursor()
		query = 'INSERT INTO MusicGroup(ownerEmail, groupName) VALUES(%s, %s)'
		cursor.execute(query, (ownerEmail, name))
		conn.commit()
		cursor.close()

	@staticmethod
	def checkIfGroupExists(name, conn):
		cursor = conn.cursor()
		query = 'SELECT * FROM MusicGroup WHERE groupName = %s LIMIT 1'
		cursor.execute(query, (name))
		data = cursor.fetchone()
		cursor.close()
		return data

	@staticmethod
	def removeGroup(name, conn):
		cursor = conn.cursor()
		query = 'DELETE FROM MusicGroup WHERE groupName = %s'
		cursor.execute(query, (name))
		conn.commit()
		cursor.close()

	def getName(self):
		return self.name

	def getClients(self):
		return self.thread.getClients()

	def getThreadIndex(self):
		return self.thread.getIndex()

	def getCurrentSong(self):
		return self.currentSong

	def setCurrentSong(self, currentSong):
		self.currentSong = currentSong

	def startDJRotateThread(self):
		self.thread.start()

	def getMutex(self):
		return self.thread.getThreadMutex()