from flask import Flask, render_template, request
import pymysql.cursors

from modules.user import User

# Initialize Flask
app = Flask(__name__)

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
	username = request.form['username']
	password = request.form['password']
	newUser = User(email)
	newUser.insertRegisterDetails(conn, email, username, password)
	activeUsers.append(newUser)
	print(activeUsers)
	return render_template('index.html')

if __name__ == '__main__':
	#app.run('127.0.0.1', 5000, debug=True)
	app.run(host='0.0.0.0', port=80)
