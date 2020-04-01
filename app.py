import json
import datetime
import pymysql.cursors
from youtube_search import YoutubeSearch
from urllib.parse import parse_qs, urlparse
from flask_socketio import emit, join_room, leave_room, SocketIO
from flask import Flask, redirect, render_template, request, session

from modules.user import User
from modules.group import Group

app = Flask(__name__)
app.secret_key = 'SomethingSuperSecretThatYoullNeverEverGuess'

socketio = SocketIO()
socketio.init_app(app)

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
		error = 'User already exists, enter another email'
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
		return render_template('home.html')
	except:
		return redirect('/login')

@app.route('/createGroup')
def createGroup():
	try:
		session['email']
		return render_template('createGroup.html')
	except:
		return render_template('login.html')

@app.route('/createGroupAuth', methods=['GET', 'POST'])
def createGroupAuth():
	email = session['email']
	groupName = request.form['GroupName']
	if not Group.checkIfGroupExists(groupName, conn):
		Group.insertGroupDetails(email, groupName, conn)
		newGroup = Group(groupName, User.fetchUsername(session['email'], conn))
		activeGroups.append(newGroup)
		session['group'] = newGroup.name
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
		if not Group.checkIfGroupIsRated(session['email'], session['group'], conn):
			return render_template('groupPage.html', group=session['group'])
		else:
			return render_template('groupPage.html', group=session['group'], rated=True)
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

@app.route('/isDJ/<socketID>')
def isDJ(socketID):
	try:
		group = getGroupObject(session['group'])
		if group is None:
			return json.dumps({'isDJ': False})
		group.getMutex().acquire()
		clients = group.getClients()
		if socketID == clients[group.getThreadIndex()]:
			try:
				group.getMutex().release()
			except:
				pass
			return json.dumps({'isDJ': True})
	finally:
		try:
			group.getMutex().release()
		except:
			pass
	return json.dumps({'isDJ': False})

@app.route('/saveSong/<songID>', methods=['GET', 'POST'])
def saveSong(songID):
	try:
		if (songID == "0") or (User.checkForDuplicateSavedSong(session['email'], songID, conn)):
			return json.dumps({'savedSong': False})
		else:
			User.saveSong(session['email'], songID, conn)
			return json.dumps({'savedSong': True})
	except:
			return json.dumps({'savedSong': True})	

@app.route('/getMemberCount')
def getMemberCount():
	try:
		group = getGroupObject(session['group'])
		if group is None:
			return json.dumps({'memberCount': -1})
		group.getMutex().acquire()
		clients = group.getClients()
		jsonResponse = json.dumps({'memberCount': len(clients)})
	finally:
		try:
			group.getMutex().release()
		except:
			pass
	return jsonResponse

@app.route('/getRatingAverage')
def getRatingAverage():
	try:
		ratingSum = 0
		ratings = Group.getRatings(session['group'], conn)
		if len(ratings) == 0:
			return json.dumps({'averageRating': 5})
		for rating in ratings:
			ratingSum += rating['rating']
		return json.dumps({'averageRating': ratingSum / len(ratings)})
	except:
		return json.dumps({'averageRating': -1})

@socketio.on('joinGroup', namespace='/group')
def joinGroup(message):
	try:
		group = getGroupObject(session['group'])
		if group is None:
			return
		group.getMutex().acquire()
		clients = group.getClients()
		clients.append(request.sid)
	finally:
		try:
			group.getMutex().release()
		except:
			pass
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

@socketio.on('fetchSong', namespace='/group')
def fetchSong(message):
	try:
		urlRes = urlparse(message['msg'])
		if all([urlRes.scheme, urlRes.netloc, urlRes.path]):
			message['msg'] = parse_qs(urlRes.query)['v'][0]
		else:
			message['msg'] = (YoutubeSearch(message['msg'], max_results=1).to_dict())[0]["id"]
		group = getGroupObject(session['group'])
		if group is None:
			return
		group.setCurrentSong(message['msg'])
		emit('video', {'msg': message['msg']}, room=session['group'])
	except:
		pass

@socketio.on('rateGroup', namespace='/group')
def rateGroupRating(message):
	try:
		Group.insertGroupRating(session['email'], session['group'], int(message['msg']), conn)
	except:
		pass

@socketio.on('reportProblem', namespace='/group')
def reportProblem(message):
	try:
		subject = 'WE.J PROBLEM REPORT'
		sender = 'wejreportproblem@gmail.com'
		recipient = 'wejreportproblem@gmail.com'
		password = 'SomethingSuperSecretThatYoullNeverEverGuess'
		email = 'From: ' + sender + '\nTo: ' + recipient + '\nSubject: ' + subject + '\n' + message['msg']
		server = smtplib.SMTP('smtp.gmail.com', 587)
		server.starttls()
		server.login(sender, password)
		server.sendmail(sender, recipient, email)
		server.close()
	except:
		pass

@socketio.on('leaveGroup', namespace='/group')
def leaveGroup(message):
	try:
		if not activeGroups:
			return
		group = getGroupObject(session['group'])
		if group is None:
			return
		group.getMutex().acquire()
		clients = group.getClients()
		clients.remove(request.sid)
		if not clients:
			Group.removeGroup(session['group'], conn)
			activeGroups.remove(group)
	finally:
		try:
			group.getMutex().release()
		except:
			pass
	leave_room(session['group'])
	emit('update',
		 {'msg': datetime.datetime.now().strftime('[%I:%M:%S %p] ')
		 + session['username'] + ' left the group.'}, room=session['group'])
	session['group'] = None

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
	try:
		return render_template('savedSongs.html', songs=User.getSavedSongs(session['email'], conn))
	except:
		return redirect('/login')

@app.route('/logout')
def logout():
	session.clear()
	return redirect('/')

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

if __name__ == '__main__':
	socketio.run(app)