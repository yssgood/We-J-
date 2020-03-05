from flask import Flask, render_template, request, session, redirect
from flask_socketio import SocketIO, emit, join_room
import pymysql.cursors

from modules.user import User
from modules.group import Group

# Initialize Flask
app = Flask(__name__)

socketio = SocketIO()
socketio.init_app(app)

app.secret_key = 'secret'

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

@app.route('/registerAuth', methods=['GET', 'POST'])
def registerAuth():
  email = request.form['email']
  password = request.form['password']
  newUser = User(email)
  newUser.insertRegisterDetails(conn, password)
  activeUsers.append(newUser)
  session['email'] = email
  print(activeUsers)
  return redirect('/home')
 
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
      activeUsers.append(newUser)
      session['email'] = email
      print(activeUsers)
      return redirect('/home')
    else:
      return redirect('/login')

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
    groupName = request.form['GroupName']
    newGroup = Group(email, groupName)
    if not(newGroup.checkMusicGroup(conn)):
      newGroup.insertGroupDetails(conn, groupName)
      activeGroups.append(newGroup)
      session['group'] = newGroup.name
      print(activeGroups)
      return redirect('/group')
    else:
      print("yes")
      return redirect('/createGroup')

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
	join_room(group)
	emit('update', {'msg': session['email'] + ' entered the group.'}, room=group)

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
