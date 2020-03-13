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

@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
	email = request.form['email']
	username = request.form['username']
	password = request.form['password']
	if not User.checkIfUserExists(email, conn):
		User.insertRegisterDetails(email, username, password, conn)
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
	if User.validateUser(email, password, conn):
		session['email'] = email
		session['username'] = User.fetchUsername(email, conn)
		return redirect('/home')
	else:
		error = 'Incorrect Login, Please enter again'
		return render_template('login.html', error=error)

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

@app.route('/createGroup')
def createGroup():
	try:
		session['email']
		return render_template('createGroup.html')
	except:
		return render_template('login.html')

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
		if not Group.checkIfGroupExists(groupName, conn):
			Group.insertGroupDetails(email, groupName, conn)
			newGroup = Group(groupName, User.fetchUsername(session['email'], conn))
			activeGroups.append(newGroup)
			session['group'] = newGroup.name
			print(activeGroups)
			newGroup.startDJRotateThread()
			return redirect('/group')
		else:
			error = 'A group with this name already exists! Please try again.'
			return render_template('createGroup.html', error=error)

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

@app.route('/isDJ/<socketID>', methods=['GET', 'POST'])
def isDJ(socketID):
	socketID = socketID[8:]
	try:
		group = getGroupObject(session['group'])
		group.getMutex().acquire()
		clients = group.getClients()
		if socketID == clients[group.getThreadIndex()]:
			return json.dumps({'isDJ': True})
	finally:
		group.getMutex().release()
	return json.dumps({'isDJ': False})

@app.route('/saveSong/<songID>', methods=['GET', 'POST'])
def saveSong(songID):
	if (songID == "0") or (User.checkForDuplicateSavedSong(session['email'], songID, conn)):
		return json.dumps({'savedSong': False})
	else:
		User.saveSong(session['email'], songID, conn)
		return json.dumps({'savedSong': True})

@app.route('/getMemberCount')
def getMemberCount():
	try:
		group = getGroupObject(session['group'])
		group.getMutex().acquire()
		clients = group.getClients()
		jsonResponse = json.dumps({'memberCount': len(clients)})
	finally:
		group.getMutex().release()
	return jsonResponse

@socketio.on('joinGroup', namespace='/group')
def joinGroup(message):
	try:
		group = getGroupObject(session['group'])
		group.getMutex().acquire()
		clients = group.getClients()
		print(clients)
		clients.append(request.sid)
		print(clients)
	finally:
		group.getMutex().release()
	join_room(session['group'])
	emit('update',
		 {'msg': datetime.datetime.now().strftime('[%I:%M:%S %p] ')
		 + session['username'] + ' entered the group.'}, room=session['group'])
	if group.getCurrentSong():
		emit('video', {'msg': group.getCurrentSong()}, room=request.sid)

@socketio.on('sendMessage', namespace='/group')
def sendMessage(message):
	emit('update',
		 {'msg': datetime.datetime.now().strftime('[%I:%M:%S %p] ')
		 + session['username'] + ': ' + message['msg']}, room=session['group'])

@socketio.on('broadcastSong', namespace='/group')
def fetchSong(message):
	group = getGroupObject(session['group'])
	group.setCurrentSong(message['msg'])
	emit('video', {'msg': message['msg']}, room=session['group'])

@socketio.on('leaveGroup', namespace='/group')
def leaveGroup(message):
	try:
		group = getGroupObject(session['group'])
		group.getMutex().acquire()
		clients = group.getClients()
		print(clients)
		clients.remove(request.sid)
		print(clients)
		print(activeGroups)
		if not clients:
			Group.removeGroup(session['group'], conn)
			activeGroups.remove(group)
		print(activeGroups)
	finally:
		group.getMutex().release()
	leaveGroups.append([session['email'], True])
	leave_room(session['group'])
	emit('update',
		 {'msg': datetime.datetime.now().strftime('[%I:%M:%S %p] ')
		 + session['username'] + ' left the group.'}, room=session['group'])

@socketio.on('disconnect', namespace='/group')
def disconnect():
	print("DISCONNECTED")
	leaveGroup(None)
	logout()

def getGroupObject(name):
	for group in activeGroups:
		if group.getName() == name:
			return group
	return None

@app.route('/availableGroups')
def availableGroups():
	try:
		session['email']
		return render_template('availableGroups.html',
							   activeGroups=activeGroups)
	except:
		return redirect('/login')

@app.route('/savedSongs')
def getSavedSongs():
	return render_template('savedSongs.html', songs=User.getSavedSongs(session['email'], conn))

@app.route('/logout')
def logout():
	session.clear()
	return redirect('/')
'''
#404 errorhandler
@app.errorhandler(404)
def page_not_found(error):
	#render template when 404 error occurs
	return render_template('404error.html')

#unauthorized access errorhandler
@app.errorhandler(Exception)
def page_not_found(error):
	#render template when unauthorized access error occurs
	return render_template('unauthorizedAccess.html')
'''
if __name__ == '__main__':
	socketio.run(app)