from flask import Flask, render_template, request, session, redirect
from flask_socketio import SocketIO, emit, join_room
import pymysql.cursors
import json

from modules.user import User
from modules.group import Group

# Initialize Flask
app = Flask(__name__)

socketio = SocketIO()
socketio.init_app(app)

app.secret_key = 'SomethingSuperSecretThatYoullNeverEverGuess'

activeUsers = []
activeGroups = []

# Configure MySQL
conn = pymysql.connect(host='localhost',
											 port=3306,
											 user='root',
											 password='root',
											 db='WEJ',
											 charset='utf8mb4',
											 cursorclass=pymysql.cursors.DictCursor)

'''
DJ Rotation Thread - Works for one group only right now.
'''
from threading import Thread, Event, Lock
clients = []

class DJRotateThread(Thread):
		def __init__(self, event):
				Thread.__init__(self)
				self.stopped = event
				self.djIndex = 0;

		def run(self):
				while not self.stopped.wait(10):
						mutex.acquire()
						try:
								if(len(clients) > 0):
										self.djIndex = (self.djIndex + 1) % len(clients)
										print(self.djIndex)
						finally:
								mutex.release()

		def getIndex(self):
			return self.djIndex

mutex = Lock()
stopFlag = Event()
thread = DJRotateThread(stopFlag)
'''
'''

@app.route('/')
def index():
	#user is already logged in
	try:
		print(session['email'])
		return redirect('/home')
	#user is not logged in
	except:
		return render_template('index.html')

@app.route('/register')
def register():
	#user is already logged in
	try:
		session['email']
		return redirect('/home')
	#user is not logged in
	except:
		return render_template('register.html')

def checkUserExist(conn, email):
	cursor = conn.cursor()
	query = 'SELECT * FROM User WHERE email = %s LIMIT 1'
	cursor.execute(query, (email))
	data = cursor.fetchone()
	cursor.close()
	return data

@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
	email = request.form['email']
	username = request.form['username']
	password = request.form['password']
	if not checkUserExist(conn, email):
		newUser = User(email, username)
		newUser.insertRegisterDetails(conn, password)
		activeUsers.append(newUser)
		session['email'] = email
		session['username'] = username
		print(activeUsers)
		return redirect('/home')
	else:
		error = "User already exists, please enter another email"
		return render_template("register.html", error = error)
 
@app.route('/login')
def login():
	#user is already logged in
	try:
		session['email']
		return redirect('/home')
	#user is not logged in
	except:
		return render_template('login.html')
 
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
		email = request.form['email']
		password = request.form['password']
		newUser = User(email)
		if(newUser.checkUser(conn, password)):
			newUser.updateUsername(conn)
			activeUsers.append(newUser)
			session['email'] = email
			session['username'] = newUser.username
			print(activeUsers)
			return redirect('/home')
		else:
			error = "Incorrect Login, Please enter again"
			return render_template("login.html", error = error)

@app.route('/logout')
def logout():
	activeUsers.remove(targetUser())
	session.pop('email')
	try:
		session.pop('group')
	except:
		pass
	print(activeUsers)
	return redirect('/')

@app.route('/createGroup')
def createGroup():
	#user is already logged in
	try:
		session['email']
		return render_template('creategroup.html')
	#user is not logged in
	except:
		return render_template('login.html', email=email)

@app.route('/createGroupAuth', methods=['GET', 'POST'])
def createGroupAuth():
		email = session['email']
		username = session['username']
		groupName = request.form['GroupName']
		newGroup = Group(email, username, groupName)
		if not(newGroup.checkMusicGroup(conn)):
			newGroup.insertGroupDetails(conn)
			activeGroups.append(newGroup)
			session['group'] = newGroup.name
			print(activeGroups)
			thread.start()
			return redirect('/group')
		else:
			error = "You already have a group."
			return render_template("creategroup.html", error = error)

@app.route('/groupsPage')
def groupsPage():
		#user is already logged in
	try:
		session['email']
		return render_template('groupsPage.html', activeGroups = activeGroups)
	#user is not logged in
	except:
		return redirect('/login')

@app.route('/group')
def group():
	#user is already logged in
	try:
		session['email']
		session['group']
		return render_template('groupPage.html', group=session['group'])
	#user is not logged in
	except:
		return redirect('/login')

@app.route('/joinGroup/<group>', methods=['GET', 'POST'])
def joinGroup(group):
	#user is already logged in
	try:
		session['email']
		session['group'] = group
		return redirect('/group')
	#user is not logged in
	except:
		return redirect('/login')

@socketio.on("joinGroup", namespace="/group")
def joinGroup(message):
	group = session['group']
	mutex.acquire()
	try:
		clients.append(request.sid)
	finally:
		mutex.release()
	join_room(group)
	emit('update', {'msg': session['username'] + ' entered the group.'}, room=group)

@socketio.on("broadcastSong", namespace="/group")
def fetchSong(message):
	group = session['group']
	emit('message', {'msg': message['msg']}, room=group)

@app.route('/isDJ/<socketID>', methods=['GET', 'POST'])
def isDJ(socketID):
	socketID = socketID[8:]
	mutex.acquire()
	try:
		if(socketID == clients[thread.getIndex()]):
			return json.dumps({'isDJ': True})
	finally:
		mutex.release()
	return json.dumps({'isDJ': False})

def targetUser():
	for user in activeUsers:
		if user.email == session['email']:
			return user
	return None

@app.route('/home')
def home():
	#user is logged in
	try:
		session['email']
	#user is not logged in
	except:
		return redirect('/login')
	return render_template('home.html')

if __name__ == '__main__':
	#app.run('127.0.0.1', 5000, debug=True)
	#app.run(host='0.0.0.0', port=5000, debug=True)
	socketio.run(app)
