from threading import Thread, Event, Lock

class DJRotateThread(Thread):
	def __init__(self, event):
		Thread.__init__(self)
		self.djIndex = 0
		self.clients = []
		self.stop = event

	def run(self):
		while not self.stop.wait(10):
			try:
				if len(self.clients) > 0:
					self.djIndex = (self.djIndex + 1) % len(self.clients)
					print(self.djIndex)
			finally:
				pass

	def getIndex(self):
		return self.djIndex

	def getClients(self):
		return self.clients