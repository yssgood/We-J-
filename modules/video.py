import pymysql.cursors
import hashlib

class Video:
	def __init__(self, email, link):
		self.email = email
		self.link = link
