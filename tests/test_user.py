import sys
import hashlib
import pymysql.cursors
sys.path.append("..")

from modules.user import User

# Configure MySQL
conn = pymysql.connect(host='localhost', 
						port=3306, # Change to your MySQL port
						user='root', # Change to your MySQL user
						password='root', # Change to your MySQL password
						db='WEJ',
						charset='utf8mb4',
						cursorclass=pymysql.cursors.DictCursor)

email1 = "erlichbachman@wej.com"
username1 = "ErlichBachman"
password1 = "aSuperSecretPassword!!!"

email2 = "bertramgilfoyle@wej.com"
username2 = "BertramGilfoyle"
password2 = "fufd89nHD8!!!?hddkdid344"

songID1 = "887fgf7ergf8e"
songID2 = "chds763ndsuds"
songID3 = "djhgds7678wev"
songID4 = "hsdjhdsj78732"

def test_insertRegisterDetails():
	User.insertRegisterDetails(email1, username1, password1, conn)
	assert User.checkIfUserExists(email1, conn) == {'email': 'erlichbachman@wej.com', 'username': 'ErlichBachman', 'password': 'd580f2b03d5e33995eebc2f66e0b048c05f8cc2204064ff2310a6a90303b7fb1'}
	User.insertRegisterDetails(email2, username2, password2, conn)
	assert User.checkIfUserExists(email2, conn) == {'email': 'bertramgilfoyle@wej.com', 'username': 'BertramGilfoyle', 'password': 'f834fc414a284e71c755343c50cdfb78b769087b88bba487a0a80577cf8c5d77'}

def test_validateUser():
	assert User.validateUser(email1, password1, conn) == {'email': 'erlichbachman@wej.com', 'username': 'ErlichBachman', 'password': 'd580f2b03d5e33995eebc2f66e0b048c05f8cc2204064ff2310a6a90303b7fb1'}
	assert User.validateUser(email2, password2, conn) == {'email': 'bertramgilfoyle@wej.com', 'username': 'BertramGilfoyle', 'password': 'f834fc414a284e71c755343c50cdfb78b769087b88bba487a0a80577cf8c5d77'}

def test_fetchUsername():
	assert User.fetchUsername(email1, conn) == username1
	assert User.fetchUsername(email2, conn) == username2

def test_saveSong():
	User.saveSong(email1, songID1, conn)
	User.saveSong(email2, songID2, conn)
	User.saveSong(email1, songID3, conn)
	assert User.getSavedSongs(email1, conn) == [{'email': 'erlichbachman@wej.com', 'songID': '887fgf7ergf8e'}, {'email': 'erlichbachman@wej.com', 'songID': 'djhgds7678wev'}]
	assert User.getSavedSongs(email2, conn) == [{'email': 'bertramgilfoyle@wej.com', 'songID': 'chds763ndsuds'}]

def test_checkForDuplicateSavedSong():
	assert User.checkForDuplicateSavedSong(email1, songID1, conn) == {'email': 'erlichbachman@wej.com', 'songID': '887fgf7ergf8e'}
	assert User.checkForDuplicateSavedSong(email1, songID4, conn) == None
	assert User.checkForDuplicateSavedSong(email2, songID4, conn) == None