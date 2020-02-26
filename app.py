from flask import Flask, render_template, request, session, redirect
import pymysql.cursors

from modules.user import User

# Initialize Flask
app = Flask(__name__)

app.secret_key = 'secret'

activeUsers = []

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
    if(newUser.loginUser(conn, password)):
      activeUsers.append(newUser)
      session['email'] = email
      print(activeUsers)
      return redirect('/home')
    else:
      return redirect('/login')

@app.route('/logout')
def logout():
  for user in activeUsers:
    if user.email == session['email']:
      activeUsers.remove(user)
  session.pop('email')
  print(activeUsers)
  return redirect('/')

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
  app.run(host='0.0.0.0', port=5000, debug=True)