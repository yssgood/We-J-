from flask import Flask, render_template

# Initialize Flask
app = Flask(__name__)

# Configure MySQL
conn = pymysql.connect(host='localhost',
                       port=8001,
                       user='root'
                       password='root',
                       db='WEJ',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def index():
	return render_template('index.html')

if __name__ == '__main__':
	app.run('127.0.0.1', 5000, debug=True)
