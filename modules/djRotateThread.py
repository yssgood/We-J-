from threading import Thread, Event, Lock

class DJRotateThread(Thread):
	def __init__(self, event):
		Thread.__init__(self)
		self.djIndex = 0
		self.clients = []
		self.stop = event
		self.mutex = Lock()

	def run(self):
		while not self.stop.wait(120):
			try:
				self.mutex.acquire()
				if len(self.clients) > 0:
					self.djIndex = (self.djIndex + 1) % len(self.clients)
					print('DJ Index: ' + str(self.djIndex))
			finally:
				self.mutex.release()

	def getIndex(self):
		return self.djIndex

	def getClients(self):
		return self.clients

	def getThreadMutex(self):
		return self.mutex