import sys
import hashlib
import pymysql.cursors
sys.path.append("..")

from modules.user import User
from modules.group import Group

conn = pymysql.connect(host='localhost', 
						port=3306, # Change to your MySQL port
						user='root', # Change to your MySQL user
						password='root', # Change to your MySQL password
						db='WEJ',
						charset='utf8mb4',
						cursorclass=pymysql.cursors.DictCursor)

email1 = "erlichbachman@pp.com"
username1 = "ErlichBachman"
password1 = "aSuperSecretPassword!!!"
group1 = "Psychedelic Rock"
rating1 = 4

email2 = "bertramgilfoyle@pp.com"
username2 = "BertramGilfoyle"
password2 = "fufd89nHD8!!!?hddkdid344"
group2 = "Anton LaVey Chants"
rating2 = 5

email3 = "richardhendricks@pp.com"
password3 = "isduiodusdios!?"
group3 = "Hip Hop"

songID1 = "887fgf7ergf8e"
songID2 = "chds763ndsuds"
songID3 = "djhgds7678wev"
songID4 = "hsdjhdsj78732"

##########User Module Tests##########

def test_insertRegisterDetails():
	User.insertRegisterDetails(email1, username1, password1, conn)
	assert User.checkIfUserExists(email1, conn) == {'email': 'erlichbachman@pp.com', 'username': 'ErlichBachman', 'password': 'd580f2b03d5e33995eebc2f66e0b048c05f8cc2204064ff2310a6a90303b7fb1'}
	User.insertRegisterDetails(email2, username2, password2, conn)
	assert User.checkIfUserExists(email2, conn) == {'email': 'bertramgilfoyle@pp.com', 'username': 'BertramGilfoyle', 'password': 'f834fc414a284e71c755343c50cdfb78b769087b88bba487a0a80577cf8c5d77'}
	assert User.checkIfUserExists(email3, conn) == None

def test_validateUser():
	assert User.validateUser(email1, password1, conn) == {'email': 'erlichbachman@pp.com', 'username': 'ErlichBachman', 'password': 'd580f2b03d5e33995eebc2f66e0b048c05f8cc2204064ff2310a6a90303b7fb1'}
	assert User.validateUser(email2, password2, conn) == {'email': 'bertramgilfoyle@pp.com', 'username': 'BertramGilfoyle', 'password': 'f834fc414a284e71c755343c50cdfb78b769087b88bba487a0a80577cf8c5d77'}
	assert User.validateUser(email3, password3, conn) == None

def test_fetchUsername():
	assert User.fetchUsername(email1, conn) == username1
	assert User.fetchUsername(email2, conn) == username2
	assert User.fetchUsername(email3, conn) == None

def test_saveSong():
	User.saveSong(email1, songID1, conn)
	User.saveSong(email2, songID2, conn)
	User.saveSong(email1, songID3, conn)
	assert User.getSavedSongs(email1, conn) == [{'email': 'erlichbachman@pp.com', 'songID': '887fgf7ergf8e'}, {'email': 'erlichbachman@pp.com', 'songID': 'djhgds7678wev'}]
	assert User.getSavedSongs(email2, conn) == [{'email': 'bertramgilfoyle@pp.com', 'songID': 'chds763ndsuds'}]
	assert User.getSavedSongs(email3, conn) == ()

def test_checkForDuplicateSavedSong():
	assert User.checkForDuplicateSavedSong(email1, songID1, conn) == {'email': 'erlichbachman@pp.com', 'songID': '887fgf7ergf8e'}
	assert User.checkForDuplicateSavedSong(email1, songID4, conn) == None
	assert User.checkForDuplicateSavedSong(email2, songID4, conn) == None
	assert User.checkForDuplicateSavedSong(email3, songID4, conn) == None

##########Group Module Tests##########

def test_insertGroupDetails():
	Group.insertGroupDetails(email1, group1, conn)
	assert Group.checkIfGroupExists(group1, conn) == {'ownerEmail': 'erlichbachman@pp.com', 'groupName': 'Psychedelic Rock'}
	Group.insertGroupDetails(email2, group2, conn)
	assert Group.checkIfGroupExists(group2, conn) == {'ownerEmail': 'bertramgilfoyle@pp.com', 'groupName': 'Anton LaVey Chants'}
	assert Group.checkIfGroupExists(group3, conn) == None

def test_insertGroupRating():
	Group.insertGroupRating(email1, group1, rating1, conn)
	assert Group.getRatings(group1, conn) == [{'rating': 4}]
	Group.insertGroupRating(email2, group2, rating2, conn)
	assert Group.getRatings(group2, conn) == [{'rating': 5}]
	assert Group.getRatings(group3, conn) == ()

def test_checkIfGroupIsRated():
	assert Group.checkIfGroupIsRated(email1, group1, conn) == {'email': 'erlichbachman@pp.com', 'groupName': 'Psychedelic Rock', 'rating': 4}
	assert Group.checkIfGroupIsRated(email2, group2, conn) == {'email': 'bertramgilfoyle@pp.com', 'groupName': 'Anton LaVey Chants', 'rating': 5}
	assert Group.checkIfGroupIsRated(email3, group3, conn) == None

def test_removeGroup():
	Group.removeGroup(group1, conn)
	assert Group.checkIfGroupExists(group1, conn) == None
	Group.removeGroup(group2, conn)
	assert Group.checkIfGroupExists(group2, conn) == None
	assert Group.checkIfGroupExists(group3, conn) == None