import json
import datetime
import pymysql.cursors
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import Flask, render_template, request, session, redirect

from modules.user import User
from modules.group import Group

app = Flask(__name__)
app.secret_key = 'SomethingSuperSecretThatYoullNeverEverGuess'

socketio = SocketIO(app, manage_session=False)

leaveGroups = []
activeGroups = []

conn = pymysql.connect(host='localhost',
						port=3306,
						user='root',
						password='root',
						db='WEJ',
						charset='utf8mb4',
						cursorclass=pymysql.cursors.DictCursor)

from threading import Thread, Event, Lock
clients = []

class DJRotateThread(Thread):
	def __init__(self, event):
		Thread.__init__(self)
		self.stopped = event
		self.djIndex = 0

	def run(self):
		while not self.stopped.wait(10):
			mutex.acquire()
			try:
				if len(clients) > 0:
					self.djIndex = (self.djIndex + 1) % len(clients)
					print(self.djIndex)
			finally:
				mutex.release()

	def getIndex(self):
		return self.djIndex

mutex = Lock()
stopFlag = Event()
thread = DJRotateThread(stopFlag)

@app.route('/')
def index():
	try:
		session['email']
		return redirect('/home')
	except:
		return render_template('index.html')

@app.route('/register')
def register():
	try:
		session['email']
		return redirect('/home')
	except:
		return render_template('register.html')

def checkIfUserExists(conn, email):
	cursor = conn.cursor()
	query = 'SELECT * FROM User WHERE email = %s LIMIT 1'
	cursor.execute(query, email)
	data = cursor.fetchone()
	cursor.close()
	return data

@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
	email = request.form['email']
	username = request.form['username']
	password = request.form['password']
	if not checkIfUserExists(conn, email):
		newUser = User(email, username)
		newUser.insertRegisterDetails(conn, password)
		session['email'] = email
		session['username'] = username
		return redirect('/home')
	else:
		error = 'User already exists, please enter another email'
		return render_template('register.html', error=error)

@app.route('/login')
def login():
	try:
		session['email']
		return redirect('/home')
	except:
		return render_template('login.html')

@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
	email = request.form['email']
	password = request.form['password']
	newUser = User(email)
	if newUser.validateUser(conn, password):
		newUser.fetchAndUpdateUsername(conn)
		session['email'] = email
		session['username'] = newUser.username
		return redirect('/home')
	else:
		error = 'Incorrect Login, Please enter again'
		return render_template('login.html', error=error)

@app.route('/logout')
def logout():
	try:
		session.clear()
	except:
		pass
	return redirect('/')

@app.route('/createGroup')
def createGroup():
	try:
		session['email']
		return render_template('createGroup.html')
	except:
		return render_template('login.html', email=email)

@app.route('/createGroupAuth', methods=['GET', 'POST'])
def createGroupAuth():
	try:
		session['group']
		print(session['group'])
		error = 'You are already part of a group!'
		return render_template('createGroup.html', error=error)
	except:
		email = session['email']
		groupName = request.form['GroupName']
		newGroup = Group(email, groupName, session['username'])
		if not newGroup.checkIfGroupExists(conn):
			newGroup.insertGroupDetails(conn)
			activeGroups.append(newGroup)
			session['group'] = newGroup.name
			print(activeGroups)
			thread.start()
			return redirect('/group')
		else:
			error = 'A group with this name already exists! Please try again.'
			return render_template('createGroup.html', error=error)

@app.route('/availableGroups')
def availableGroups():
	try:
		session['email']
		return render_template('availableGroups.html',
							   activeGroups=activeGroups)
	except:
		return redirect('/login')

@app.route('/group')
def group():
	try:
		session['email']
		session['group']
		return render_template('groupPage.html', group=session['group'])
	except:
		return redirect('/login')

@app.route('/joinGroup/<group>', methods=['GET', 'POST'])
def joinGroup(group):
	try:
		session['email']
		session['group'] = group
		return redirect('/group')
	except:
		return redirect('/login')

@socketio.on('joinGroup', namespace='/group')
def joinGroup(message):
	group = session['group']
	mutex.acquire()
	try:
		print(clients)
		clients.append(request.sid)
		print(clients)
	finally:
		mutex.release()
	join_room(group)
	emit('update',
		 {'msg': datetime.datetime.now().strftime('[%I:%M:%S %p] ')
		 + session['username'] + ' entered the group.'}, room=group)

@socketio.on('broadcastSong', namespace='/group')
def fetchSong(message):
	group = session['group']
	emit('message', {'msg': message['msg']}, room=group)

@socketio.on('sendMessage', namespace='/group')
def sendMessage(message):
	group = session['group']
	emit('update',
		 {'msg': datetime.datetime.now().strftime('[%I:%M:%S %p] ')
		 + session['username'] + ': ' + message['msg']}, room=group)

@socketio.on('leaveGroup', namespace='/group')
def leaveGroup(message):
	global leftGroup
	group = session['group']
	mutex.acquire()
	try:
		print(clients)
		clients.remove(request.sid)
		print(clients)
	finally:
		mutex.release()
	leaveGroups.append([session['email'], True])
	leave_room(group)
	emit('update',
		 {'msg': datetime.datetime.now().strftime('[%I:%M:%S %p] ')
		 + session['username'] + ' left the group.'}, room=group)

@socketio.on('disconnect', namespace='/group')
def disconnect():
	try:
		leaveGroup(None)
		logout()
	except:
		pass

@app.route('/isDJ/<socketID>', methods=['GET', 'POST'])
def isDJ(socketID):
	socketID = socketID[8:]
	mutex.acquire()
	try:
		if socketID == clients[thread.getIndex()]:
			return json.dumps({'isDJ': True})
	finally:
		mutex.release()
	return json.dumps({'isDJ': False})

@app.route('/home')
def home():
	try:
		session['email']
		for index, data in enumerate(leaveGroups):
			if data[0] == session['email'] and data[1] is True:
				session.pop('group')
				del leaveGroups[index]
	except:
		return redirect('/login')
	return render_template('home.html')

if __name__ == '__main__':
	socketio.run(app)