import json
import datetime
import pymysql.cursors
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import Flask, render_template, request, session, redirect

from modules.user import User
from modules.group import Group

app = Flask(__name__)
app.secret_key = 'SomethingSuperSecretThatYoullNeverEverGuess'

socketio = SocketIO()
socketio.init_app(app)

leaveGroups = []
activeGroups = []

conn = pymysql.connect(host='localhost',
						port=3306,
						user='root',
						password='root',
						db='WEJ',
						charset='utf8mb4',
						cursorclass=pymysql.cursors.DictCursor)

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
			newGroup.startDJRotateThread()
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

def getGroupObject(name):
	for group in activeGroups:
		if group.getName() == name:
			return group
	return None

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
	group = getGroupObject(session['group'])
	clients = group.getClients()
	try:
		print(clients)
		clients.append(request.sid)
		print(clients)
	finally:
		pass
	join_room(session['group'])
	emit('update',
		 {'msg': datetime.datetime.now().strftime('[%I:%M:%S %p] ')
		 + session['username'] + ' entered the group.'}, room=session['group'])
	if group.getCurrentSong():
		emit('video', {'msg': group.getCurrentSong()}, room=request.sid)

@socketio.on('broadcastSong', namespace='/group')
def fetchSong(message):
	group = getGroupObject(session['group'])
	group.setCurrentSong(message['msg'])
	emit('video', {'msg': message['msg']}, room=session['group'])

@socketio.on('sendMessage', namespace='/group')
def sendMessage(message):
	emit('update',
		 {'msg': datetime.datetime.now().strftime('[%I:%M:%S %p] ')
		 + session['username'] + ': ' + message['msg']}, room=session['group'])

def removeGroup(group):
	cursor = conn.cursor()
	query = 'DELETE FROM MusicGroup WHERE groupName = %s'
	cursor.execute(query, (group.getName()))
	conn.commit()
	cursor.close()
	activeGroups.remove(group)

@socketio.on('leaveGroup', namespace='/group')
def leaveGroup(message):
	group = getGroupObject(session['group'])
	clients = group.getClients()
	try:
		print(clients)
		clients.remove(request.sid)
		print(clients)
		print(activeGroups)
		if not clients:
			removeGroup(group)
		print(activeGroups)
	finally:
		pass
	leaveGroups.append([session['email'], True])
	leave_room(session['group'])
	emit('update',
		 {'msg': datetime.datetime.now().strftime('[%I:%M:%S %p] ')
		 + session['username'] + ' left the group.'}, room=session['group'])

@socketio.on('disconnect', namespace='/group')
def disconnect():
	print("DISCONNECTED")
	try:
		leaveGroup(None)
		logout()
	except:
		pass

@app.route('/isDJ/<socketID>', methods=['GET', 'POST'])
def isDJ(socketID):
	socketID = socketID[8:]
	try:
		group = getGroupObject(session['group'])
		clients = group.getClients()
		if socketID == clients[group.getThreadIndex()]:
			return json.dumps({'isDJ': True})
	finally:
		pass
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