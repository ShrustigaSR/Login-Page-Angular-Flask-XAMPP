from flask import Flask, render_template, request, redirect, url_for, session,jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
import MySQLdb.cursors
import re

app = Flask(__name__)
CORS(app)
app.secret_key = 'xyzsdfg'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'angdb'

mysql = MySQL(app)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST' and 'email' in request.json and 'password' in request.json:
        email = request.json['email']
        password = request.json['password']
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = %s AND password = %s', (email, password,))
        user = cursor.fetchone()
        if user:
            session['loggedin'] = True
            session['userid'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            message = 'Logged in successfully!'
            return jsonify({'success': True, 'message': message, 'data': {'name': user['name'], 'email': user['email']}})

        else:
            message = 'Please enter correct email / password!'
    return jsonify({'success': False, 'message': message})

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'name' in request.json and 'password' in request.json and 'email' in request.json:
        username = request.json['name']
        email = request.json['email']
        password = request.json['password']
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM user WHERE email = %s', (email,))
        account = cursor.fetchone()
        if account:
            message = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address!'
        elif not username or not password or not email:
            message = 'Please fill out the form!'
        else:
            cursor.execute('INSERT INTO user (name, email, password) VALUES (%s, %s, %s)', (username, email, password,))
            mysql.connection.commit()
            message = 'You have successfully registered!'
            return jsonify({'success': True, 'message': message})
    return jsonify({'success': False, 'message': message})


@app.route('/profile')
def profile():
    if 'loggedin' in session:
        return {
            'name': session['name'],
            'email': session['email']
        }
    else:
        return {'error': 'User not logged in'}


if __name__ == '__main__':
    app.run(debug=True)
