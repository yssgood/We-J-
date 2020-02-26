from flask import Flask, render_template, request, session
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
  return render_template('index.html')

@app.route('/register')
def register():
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
  return render_template('index.html')
 
@app.route('/login')
def login():
    return render_template('login.html')
 
@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
    email = request.form['email']
    password = request.form['password']
    newUser = User(email)
    newUser.loginUser(conn, password)
    activeUsers.append(newUser)
    session['email'] = email
    print(activeUsers)
    return render_template('index.html')

@app.route('/logout')
def logout():
  for user in activeUsers:
    if user.email == session['email']:
      activeUsers.remove(user)
  session.pop('email')
  print(activeUsers)
  return render_template('index.html')

if __name__ == '__main__':
	#app.run('127.0.0.1', 5000, debug=True)
  app.run(host='0.0.0.0', port=5000)